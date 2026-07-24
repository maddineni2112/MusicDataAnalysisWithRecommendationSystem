from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import DataQualityCheck, DataQualityResult, InferredLabel, PlaylistTrack, Track, TrackArtist, TrackSource


CHECKS = [
    ("missing_titles", "Tracks with missing or empty titles", "error"),
    ("missing_artists", "Tracks without linked artists", "error"),
    ("missing_labels", "Tracks without inferred labels", "warning"),
    ("low_confidence_labels", "Labels below 0.60 confidence", "info"),
    ("missing_source_ids", "Tracks without external/source IDs", "info"),
    ("missing_source_lineage", "Tracks without stored source lineage", "warning"),
    ("sparse_playlists", "Playlists with fewer than two tracks", "info"),
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
        "missing_source_lineage": db.scalar(select(func.count()).select_from(Track).outerjoin(TrackSource).where(TrackSource.track_id.is_(None))) or 0,
        "sparse_playlists": _sparse_playlist_count(db),
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


def quality_summary(db: Session) -> dict:
    latest = db.execute(
        select(DataQualityCheck.name, DataQualityCheck.severity, DataQualityResult.status, DataQualityResult.count)
        .join(DataQualityResult, DataQualityResult.check_id == DataQualityCheck.id)
        .order_by(DataQualityResult.created_at.desc())
    ).all()
    seen = set()
    checks = []
    for name, severity, status, count in latest:
        if name in seen:
            continue
        seen.add(name)
        checks.append({"name": name, "severity": severity, "status": status, "count": count})
    return {"checks": checks, "status": "pass" if all(item["status"] == "pass" for item in checks) else "review"}


def _get_or_create_check(db: Session, name: str, description: str, severity: str) -> DataQualityCheck:
    check = db.scalar(select(DataQualityCheck).where(DataQualityCheck.name == name))
    if check is None:
        check = DataQualityCheck(name=name, description=description, severity=severity)
        db.add(check)
        db.flush()
    return check


def _sparse_playlist_count(db: Session) -> int:
    subquery = (
        select(PlaylistTrack.playlist_id, func.count(PlaylistTrack.track_id).label("track_count"))
        .group_by(PlaylistTrack.playlist_id)
        .subquery()
    )
    return db.scalar(select(func.count()).select_from(subquery).where(subquery.c.track_count < 2)) or 0
