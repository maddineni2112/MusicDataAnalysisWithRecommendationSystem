from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import Artist, InferredLabel, ModelRun, Playlist, PlaylistTrack, RecommendationResult, Track


def overview(db: Session) -> dict:
    language_count = db.scalar(select(func.count(func.distinct(InferredLabel.value))).where(InferredLabel.dimension == "language")) or 0
    avg_confidence = db.scalar(select(func.avg(InferredLabel.confidence)))
    return {
        "tracks": db.scalar(select(func.count()).select_from(Track)) or 0,
        "artists": db.scalar(select(func.count()).select_from(Artist)) or 0,
        "playlists": db.scalar(select(func.count()).select_from(Playlist)) or 0,
        "languages": language_count,
        "label_confidence_avg": float(avg_confidence) if avg_confidence is not None else None,
        "official_popularity_available": db.scalar(select(func.count()).select_from(Track).where(Track.popularity.is_not(None))) or 0,
    }


def language_trends(db: Session) -> list[dict]:
    rows = db.execute(
        select(Track.release_year, InferredLabel.value, func.count())
        .join(InferredLabel, InferredLabel.track_id == Track.id)
        .where(InferredLabel.dimension == "language", Track.release_year.is_not(None))
        .group_by(Track.release_year, InferredLabel.value)
        .order_by(Track.release_year, InferredLabel.value)
    ).all()
    return [{"year": year, "language": language, "count": count} for year, language, count in rows]


def label_distribution(db: Session, dimension: str, limit: int = 12) -> list[dict]:
    rows = db.execute(
        select(InferredLabel.value, func.count(), func.avg(InferredLabel.confidence))
        .where(InferredLabel.dimension == dimension)
        .group_by(InferredLabel.value)
        .order_by(func.count().desc(), InferredLabel.value)
        .limit(limit)
    ).all()
    return [
        {"value": value, "count": count, "avg_confidence": round(float(avg_confidence or 0), 3)}
        for value, count, avg_confidence in rows
    ]


def top_playlists(db: Session, limit: int = 10) -> list[dict]:
    rows = db.execute(
        select(Playlist.id, Playlist.name, Playlist.source_category, func.count(PlaylistTrack.track_id))
        .join(PlaylistTrack, PlaylistTrack.playlist_id == Playlist.id)
        .group_by(Playlist.id, Playlist.name, Playlist.source_category)
        .order_by(func.count(PlaylistTrack.track_id).desc(), Playlist.name)
        .limit(limit)
    ).all()
    return [{"id": row[0], "name": row[1], "source_category": row[2], "tracks": row[3]} for row in rows]


def popularity_summary(db: Session) -> dict:
    values = [row[0] for row in db.execute(select(Track.popularity).where(Track.popularity.is_not(None))).all()]
    if not values:
        return {"available": 0, "average": None, "min": None, "max": None, "buckets": []}
    buckets = [
        {"label": "0-25", "count": sum(1 for value in values if 0 <= value <= 25)},
        {"label": "26-50", "count": sum(1 for value in values if 26 <= value <= 50)},
        {"label": "51-75", "count": sum(1 for value in values if 51 <= value <= 75)},
        {"label": "76-100", "count": sum(1 for value in values if 76 <= value <= 100)},
    ]
    return {
        "available": len(values),
        "average": round(sum(values) / len(values), 2),
        "min": min(values),
        "max": max(values),
        "buckets": buckets,
    }


def recommender_coverage(db: Session) -> dict:
    total_tracks = db.scalar(select(func.count()).select_from(Track)) or 0
    recommended_tracks = db.scalar(select(func.count(func.distinct(RecommendationResult.track_id)))) or 0
    latest_model = db.scalars(select(ModelRun).order_by(ModelRun.created_at.desc()).limit(1)).first()
    return {
        "total_tracks": total_tracks,
        "recommended_tracks": recommended_tracks,
        "coverage": round(recommended_tracks / total_tracks, 4) if total_tracks else 0,
        "latest_model_metrics": latest_model.metrics if latest_model else {},
    }


def analytics_summary(db: Session) -> dict:
    return {
        "languages": label_distribution(db, "language"),
        "moods": label_distribution(db, "mood"),
        "music_types": label_distribution(db, "music_type"),
        "top_playlists": top_playlists(db),
        "popularity": popularity_summary(db),
        "recommender": recommender_coverage(db),
    }
