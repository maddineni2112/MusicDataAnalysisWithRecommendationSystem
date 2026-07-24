from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import Artist, DataQualityCheck, DataQualityResult, InferredLabel, Track, TrackArtist


CHECKS = [
    ("missing_titles", "Tracks with missing or empty titles", "error"),
    ("missing_artists", "Tracks without linked artists", "error"),
    ("missing_labels", "Tracks without inferred labels", "warning"),
    ("low_confidence_labels", "Labels below 0.60 confidence", "info"),
    ("missing_source_ids", "Tracks without external/source IDs", "info"),
]


def run_quality_checks(db: Session) -> list[DataQualityResult]:
    results = []
    checks = {name: _get_or_create_check(db, name, description, severity) for name, description, severity in CHECKS}
    metrics = {
        "missing_titles": db.scalar(select(func.count()).select_from(Track).where((Track.name == "") | (Track.name.is_(None)))) or 0,
        "missing_artists": db.scalar(select(func.count()).select_from(Track).outerjoin(TrackArtist).where(TrackArtist.artist_id.is_(None))) or 0,
        "missing_labels": db.scalar(select(func.count()).select_from(Track).outerjoin(InferredLabel).where(InferredLabel.id.is_(None))) or 0,
        "low_confidence_labels": db.scalar(select(func.count()).select_from(InferredLabel).where(InferredLabel.confidence < 0.60)) or 0,
        "missing_source_ids": db.scalar(select(func.count()).select_from(Track).where(Track.external_id.is_(None))) or 0,
    }
    for name, count in metrics.items():
        result = DataQualityResult(
            check_id=checks[name].id,
            status="pass" if count == 0 else "review",
            count=count,
            sample=[],
        )
        db.add(result)
        results.append(result)
    db.commit()
    return results


def _get_or_create_check(db: Session, name: str, description: str, severity: str) -> DataQualityCheck:
    check = db.scalar(select(DataQualityCheck).where(DataQualityCheck.name == name))
    if check is None:
        check = DataQualityCheck(name=name, description=description, severity=severity)
        db.add(check)
        db.flush()
    return check
