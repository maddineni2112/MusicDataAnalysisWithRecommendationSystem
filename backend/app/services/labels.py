from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.entities import InferredLabel, LabelOverride, Track


def apply_label_override(db: Session, *, track_id: int, dimension: str, value: str, reason: str | None = None) -> dict:
    track = db.get(Track, track_id)
    if track is None:
        raise ValueError("Track not found")
    normalized_dimension = dimension.strip().lower()
    normalized_value = value.strip()
    if not normalized_dimension or not normalized_value:
        raise ValueError("Dimension and value are required")
    db.execute(delete(LabelOverride).where(LabelOverride.track_id == track_id, LabelOverride.dimension == normalized_dimension))
    override = LabelOverride(track_id=track_id, dimension=normalized_dimension, value=normalized_value, reason=reason)
    db.add(override)
    db.commit()
    db.refresh(override)
    return serialize_override(override)


def list_label_overrides(db: Session, limit: int = 50) -> list[dict]:
    rows = db.execute(
        select(LabelOverride, Track.name)
        .join(Track, Track.id == LabelOverride.track_id)
        .order_by(LabelOverride.created_at.desc())
        .limit(limit)
    ).all()
    return [serialize_override(override, track_name=track_name) for override, track_name in rows]


def label_overrides_for_track(db: Session, track_id: int) -> list[dict]:
    overrides = db.scalars(select(LabelOverride).where(LabelOverride.track_id == track_id).order_by(LabelOverride.dimension)).all()
    return [serialize_override(override) for override in overrides]


def effective_labels_for_track(db: Session, track_id: int) -> list[dict]:
    inferred = db.scalars(select(InferredLabel).where(InferredLabel.track_id == track_id)).all()
    overrides = db.scalars(select(LabelOverride).where(LabelOverride.track_id == track_id)).all()
    overridden_dimensions = {override.dimension for override in overrides}
    labels = [
        {
            "dimension": label.dimension,
            "value": label.value,
            "confidence": label.confidence,
            "evidence": label.evidence,
            "source": "inferred",
        }
        for label in inferred
        if label.dimension not in overridden_dimensions
    ]
    labels.extend(
        {
            "dimension": override.dimension,
            "value": override.value,
            "confidence": 1.0,
            "evidence": {"override_id": override.id, "reason": override.reason},
            "source": "override",
        }
        for override in overrides
    )
    return sorted(labels, key=lambda item: (item["dimension"], item["value"]))


def effective_label_map(db: Session, track_id: int) -> dict[str, set[str]]:
    mapped: dict[str, set[str]] = {}
    for label in effective_labels_for_track(db, track_id):
        mapped.setdefault(label["dimension"], set()).add(label["value"])
    return mapped


def serialize_override(override: LabelOverride, track_name: str | None = None) -> dict:
    return {
        "id": override.id,
        "track_id": override.track_id,
        "track_name": track_name,
        "dimension": override.dimension,
        "value": override.value,
        "reason": override.reason,
        "created_at": override.created_at.isoformat() if override.created_at else None,
    }
