from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import Artist, InferredLabel, Playlist, Track


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
