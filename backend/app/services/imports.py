from __future__ import annotations

import csv
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Artist, CollectionSource, InferredLabel, Playlist, PlaylistTrack, RawSnapshot, Track, TrackArtist, TrackSource
from app.services.labeling import infer_labels


def import_records(db: Session, records: list[dict], source_name: str, source_type: str = "csv", source_url: str | None = None) -> dict:
    source = CollectionSource(name=source_name, source_type=source_type, url=source_url, license="See source documentation")
    db.add(source)
    db.flush()
    rows_read = rows_written = rows_skipped = 0
    for row in records:
        rows_read += 1
        if not row.get("name"):
            rows_skipped += 1
            continue
        track = upsert_track_from_row(db, row)
        artist_names = split_artists(row.get("artists", ""))
        for artist_name in artist_names:
            artist = upsert_artist(db, artist_name)
            if not db.get(TrackArtist, (track.id, artist.id)):
                db.add(TrackArtist(track_id=track.id, artist_id=artist.id))
        playlist = upsert_playlist_from_row(db, row)
        if playlist and not db.get(PlaylistTrack, (playlist.id, track.id)):
            db.add(PlaylistTrack(playlist_id=playlist.id, track_id=track.id, position=safe_int(row.get("playlist_position"))))
        source_record_id = track.external_id or f"{track.name}:{rows_read}"
        if not db.get(TrackSource, (track.id, source.id, source_record_id)):
            db.add(
                TrackSource(
                    track_id=track.id,
                    source_id=source.id,
                    source_record_id=source_record_id,
                    source_context={
                        "playlist_name": row.get("playlist_name"),
                        "playlist_category": row.get("playlist_category"),
                        "source_name": source_name,
                    },
                )
            )
        db.add(RawSnapshot(source_id=source.id, record_type="track", external_id=track.external_id, payload=row))
        source_text = " ".join(
            [
                source_name,
                row.get("language", ""),
                row.get("music_type", ""),
                row.get("mood", ""),
                row.get("playlist_name", ""),
                row.get("playlist_category", ""),
            ]
        )
        labels = infer_labels(
            track_name=track.name,
            album_name=track.album_name,
            artist_names=artist_names,
            source_text=source_text,
        )
        existing_labels = {
            (label.dimension, label.value)
            for label in db.scalars(select(InferredLabel).where(InferredLabel.track_id == track.id)).all()
        }
        for label in labels:
            if (label.dimension, label.value) not in existing_labels:
                db.add(InferredLabel(track_id=track.id, dimension=label.dimension, value=label.value, confidence=label.confidence, evidence=label.evidence))
        rows_written += 1
    db.commit()
    return {"rows_read": rows_read, "rows_written": rows_written, "rows_skipped": rows_skipped}


def import_csv(db: Session, path: Path, source_name: str, source_url: str | None = None) -> dict:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return import_records(db, list(csv.DictReader(handle)), source_name, source_type="csv", source_url=source_url)


def import_json(db: Session, path: Path, source_name: str) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload if isinstance(payload, list) else payload.get("tracks", [])
    temp_csv = path.with_suffix(".normalized.csv")
    fields = [
        "external_id",
        "name",
        "artists",
        "album_name",
        "release_date",
        "release_year",
        "duration_ms",
        "popularity",
        "explicit",
        "spotify_url",
        "language",
        "music_type",
        "mood",
        "playlist_name",
        "playlist_category",
        "playlist_position",
    ]
    with temp_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow({field: record.get(field, "") for field in fields})
    try:
        return import_csv(db, temp_csv, source_name)
    finally:
        temp_csv.unlink(missing_ok=True)


def import_playlist_json(db: Session, path: Path, source_name: str) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    playlists = payload if isinstance(payload, list) else payload.get("playlists", [])
    records: list[dict] = []
    for playlist in playlists:
        playlist_name = playlist.get("name") or playlist.get("playlist_name")
        playlist_id = playlist.get("pid") or playlist.get("id") or playlist.get("external_id") or playlist_name
        tracks = playlist.get("tracks", [])
        for index, track in enumerate(tracks, start=1):
            records.append(
                {
                    "external_id": track.get("track_uri") or track.get("external_id") or track.get("id"),
                    "name": track.get("track_name") or track.get("name"),
                    "artists": track.get("artist_name") or track.get("artists") or "",
                    "album_name": track.get("album_name") or track.get("album"),
                    "duration_ms": track.get("duration_ms"),
                    "spotify_url": spotify_url_from_uri(track.get("track_uri")),
                    "playlist_external_id": f"public:{playlist_id}",
                    "playlist_name": playlist_name,
                    "playlist_description": playlist.get("description"),
                    "playlist_category": playlist.get("category") or playlist.get("source_category") or playlist_name,
                    "playlist_position": track.get("pos") or index,
                }
            )
    return import_records(db, records, source_name, source_type="playlist_json")


def spotify_url_from_uri(uri: str | None) -> str | None:
    if not uri or not uri.startswith("spotify:track:"):
        return None
    return f"https://open.spotify.com/track/{uri.rsplit(':', 1)[-1]}"


def upsert_track_from_row(db: Session, row: dict) -> Track:
    external_id = row.get("external_id") or None
    track = None
    if external_id:
        track = db.scalar(select(Track).where(Track.external_id == external_id))
    if track is None:
        track = Track(external_id=external_id, name=row["name"])
        db.add(track)
    track.name = row["name"]
    track.album_name = row.get("album_name") or row.get("album") or None
    track.release_date = row.get("release_date") or None
    track.release_year = safe_int(row.get("release_year") or (track.release_date or "")[:4])
    track.duration_ms = safe_int(row.get("duration_ms"))
    track.popularity = safe_int(row.get("popularity"))
    track.explicit = str(row.get("explicit", "")).lower() in {"true", "1", "yes"}
    track.spotify_url = row.get("spotify_url") or None
    db.flush()
    return track


def upsert_artist(db: Session, name: str) -> Artist:
    artist = db.scalar(select(Artist).where(Artist.name == name))
    if artist is None:
        artist = Artist(name=name, genres=[])
        db.add(artist)
        db.flush()
    return artist


def upsert_playlist_from_row(db: Session, row: dict) -> Playlist | None:
    name = row.get("playlist_name")
    if not name:
        return None
    external_id = row.get("playlist_external_id") or f"local:{name.lower().replace(' ', '-')}"
    playlist = db.scalar(select(Playlist).where(Playlist.external_id == external_id))
    if playlist is None:
        playlist = Playlist(external_id=external_id, name=name)
        db.add(playlist)
    playlist.description = row.get("playlist_description") or playlist.description
    playlist.source_category = row.get("playlist_category") or playlist.source_category
    playlist.source_url = row.get("playlist_url") or playlist.source_url
    db.flush()
    return playlist


def split_artists(value: str) -> list[str]:
    parts = value.replace(";", ",").split(",")
    return [part.strip() for part in parts if part.strip()]


def safe_int(value: object) -> int | None:
    try:
        if value in ("", None):
            return None
        return int(float(str(value)))
    except ValueError:
        return None
