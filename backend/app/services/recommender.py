from __future__ import annotations

from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.entities import InferredLabel, Track
from app.services.features import load_tfidf_artifact, tfidf_similarity_scores
from app.services.labels import effective_label_map


DEFAULT_WEIGHTS = {
    "language": 2.0,
    "mood": 1.4,
    "music_type": 1.2,
    "region": 0.7,
    "era": 0.6,
    "popularity": 0.4,
    "text_similarity": 1.1,
}


def recommend_tracks(db: Session, seed_track_id: int, limit: int = 10, filters: dict | None = None) -> list[dict]:
    filters = filters or {}
    seed = db.get(Track, seed_track_id)
    if seed is None:
        return []
    seed_labels = effective_label_map(db, seed.id)
    candidates = db.scalars(
        select(Track)
        .options(selectinload(Track.labels))
        .where(Track.id != seed_track_id)
        .limit(1000)
    ).all()
    text_scores = tfidf_similarity_scores(seed_track_id, [candidate.id for candidate in candidates], load_tfidf_artifact())
    scored = []
    artist_counter: Counter[str] = Counter()
    for candidate in candidates:
        candidate_labels = effective_label_map(db, candidate.id)
        if not passes_filters(candidate, filters, candidate_labels):
            continue
        score, reasons, breakdown = score_candidate(seed, seed_labels, candidate, candidate_labels, text_scores.get(candidate.id, 0.0))
        if score <= 0:
            continue
        artist_key = candidate.album_name or "unknown"
        diversity_penalty = min(0.5, artist_counter[artist_key] * 0.1)
        score -= diversity_penalty
        breakdown["diversity_penalty"] = diversity_penalty
        scored.append({"track": candidate, "score": round(score, 4), "reasons": reasons, "score_breakdown": breakdown})
        artist_counter[artist_key] += 1
    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:limit]


def score_candidate(
    seed: Track,
    seed_labels: dict[str, set[str]],
    candidate: Track,
    candidate_labels: dict[str, set[str]] | None = None,
    text_similarity: float = 0.0,
) -> tuple[float, list[str], dict]:
    candidate_labels = candidate_labels or label_map(candidate.labels)
    score = 0.0
    reasons = []
    breakdown = {}
    for dimension, weight in DEFAULT_WEIGHTS.items():
        if dimension in {"era", "popularity"}:
            continue
        overlap = seed_labels.get(dimension, set()) & candidate_labels.get(dimension, set())
        if overlap:
            value = weight * len(overlap)
            score += value
            breakdown[dimension] = value
            reasons.append(f"similar {dimension}: {', '.join(sorted(overlap))}")
    if seed.release_year and candidate.release_year:
        gap = abs(seed.release_year - candidate.release_year)
        era_score = max(0.0, DEFAULT_WEIGHTS["era"] - (gap * 0.05))
        score += era_score
        breakdown["era"] = era_score
        if era_score > 0.3:
            reasons.append("close release era")
    if seed.popularity is not None and candidate.popularity is not None:
        gap = abs(seed.popularity - candidate.popularity)
        popularity_score = max(0.0, DEFAULT_WEIGHTS["popularity"] - (gap * 0.01))
        score += popularity_score
        breakdown["popularity"] = popularity_score
    if text_similarity > 0:
        text_score = DEFAULT_WEIGHTS["text_similarity"] * text_similarity
        score += text_score
        breakdown["text_similarity"] = round(text_score, 4)
        if text_similarity >= 0.12:
            reasons.append("strong text similarity")
    return score, reasons[:3] or ["metadata similarity match"], breakdown


def label_map(labels: list[InferredLabel]) -> dict[str, set[str]]:
    mapped: dict[str, set[str]] = {}
    for label in labels:
        mapped.setdefault(label.dimension, set()).add(label.value)
    return mapped


def passes_filters(track: Track, filters: dict, labels: dict[str, set[str]] | None = None) -> bool:
    labels = labels or label_map(track.labels)
    for key in ["language", "mood", "music_type", "region"]:
        requested = filters.get(key)
        if requested and requested not in labels.get(key, set()):
            return False
    min_year = filters.get("min_year")
    max_year = filters.get("max_year")
    if min_year and (track.release_year is None or track.release_year < int(min_year)):
        return False
    if max_year and (track.release_year is None or track.release_year > int(max_year)):
        return False
    return True
