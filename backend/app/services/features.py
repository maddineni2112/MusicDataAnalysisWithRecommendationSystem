from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.entities import Playlist, PlaylistTrack, Track, TrackArtist, TrackFeature
from app.services.labels import effective_label_map

TFIDF_ARTIFACT_NAME = "tfidf_index.pkl"


def build_track_feature_text(db: Session, track: Track) -> str:
    parts: list[str] = [track.name]
    if track.album_name:
        parts.append(track.album_name)
    if track.release_year:
        parts.append(str(track.release_year))

    artist_names = db.scalars(select(TrackArtist).where(TrackArtist.track_id == track.id)).all()
    for link in artist_names:
        if link.artist:
            parts.append(link.artist.name)
            parts.extend(link.artist.genres or [])

    playlist_rows = db.execute(
        select(Playlist)
        .join(PlaylistTrack, PlaylistTrack.playlist_id == Playlist.id)
        .where(PlaylistTrack.track_id == track.id)
    ).scalars()
    for playlist in playlist_rows:
        parts.append(playlist.name)
        if playlist.description:
            parts.append(playlist.description)
        if playlist.source_category:
            parts.append(playlist.source_category)

    labels = effective_label_map(db, track.id)
    for dimension, values in labels.items():
        parts.append(dimension)
        parts.extend(sorted(values))

    return " ".join(part for part in parts if part).lower()


def build_tfidf_features(db: Session, artifact_dir: str | Path | None = None) -> dict[str, Any]:
    tracks = db.scalars(select(Track).order_by(Track.id)).all()
    if not tracks:
        return {"rows_read": 0, "rows_written": 0, "failure_count": 0, "artifact_path": None}

    feature_rows: list[TrackFeature] = []
    corpus: list[str] = []
    track_ids: list[int] = []
    for track in tracks:
        feature_text = build_track_feature_text(db, track)
        corpus.append(feature_text)
        track_ids.append(track.id)
        feature = db.get(TrackFeature, track.id)
        if feature is None:
            feature = TrackFeature(track_id=track.id)
            db.add(feature)
        feature.feature_text = feature_text
        feature.feature_payload = {
            "builder": "tfidf_v1",
            "source": "track_artist_playlist_label_text",
        }
        feature_rows.append(feature)

    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=1)
    matrix = vectorizer.fit_transform(corpus)

    root = Path(artifact_dir or get_settings().artifact_dir)
    recommender_dir = root / "recommender"
    recommender_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = recommender_dir / TFIDF_ARTIFACT_NAME
    with artifact_path.open("wb") as handle:
        pickle.dump(
            {
                "kind": "tfidf_track_index",
                "version": "v2-alpha-tfidf",
                "track_ids": track_ids,
                "vectorizer": vectorizer,
                "matrix": matrix,
            },
            handle,
        )

    db.commit()
    return {
        "rows_read": len(tracks),
        "rows_written": len(feature_rows),
        "failure_count": 0,
        "artifact_path": str(artifact_path),
        "vocabulary_size": len(vectorizer.vocabulary_),
    }


def load_tfidf_artifact(artifact_dir: str | Path | None = None) -> dict[str, Any] | None:
    root = Path(artifact_dir or get_settings().artifact_dir)
    artifact_path = root / "recommender" / TFIDF_ARTIFACT_NAME
    if not artifact_path.exists():
        return None
    with artifact_path.open("rb") as handle:
        artifact = pickle.load(handle)
    if artifact.get("kind") != "tfidf_track_index":
        return None
    return artifact


def tfidf_similarity_scores(seed_track_id: int, candidate_track_ids: list[int], artifact: dict[str, Any] | None = None) -> dict[int, float]:
    artifact = artifact or load_tfidf_artifact()
    if not artifact:
        return {}
    track_ids = artifact["track_ids"]
    if seed_track_id not in track_ids:
        return {}
    index_by_id = {track_id: index for index, track_id in enumerate(track_ids)}
    seed_index = index_by_id[seed_track_id]
    matrix = artifact["matrix"]
    seed_vector = matrix[seed_index]
    scores: dict[int, float] = {}
    for candidate_id in candidate_track_ids:
        candidate_index = index_by_id.get(candidate_id)
        if candidate_index is None:
            continue
        score = seed_vector.multiply(matrix[candidate_index]).sum()
        scores[candidate_id] = float(score)
    return scores
