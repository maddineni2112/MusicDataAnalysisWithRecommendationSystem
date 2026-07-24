from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import JobEvent, JobRun, ModelRun


def run_logged_job(
    db: Session,
    *,
    job_type: str,
    parameters: dict | None = None,
    handler: Callable[[], dict],
) -> dict:
    job = JobRun(job_type=job_type, status="running", parameters=parameters or {})
    db.add(job)
    db.flush()
    try:
        result = handler()
        job.status = "completed"
        job.rows_read = int(result.get("rows_read", 0) or 0)
        job.rows_written = int(result.get("rows_written", 0) or 0)
        job.rows_skipped = int(result.get("rows_skipped", 0) or 0)
        job.failure_count = int(result.get("failure_count", 0) or 0)
        job.finished_at = datetime.now(UTC)
        db.add(JobEvent(job_id=job.id, level="info", message=f"{job_type} completed", payload=result))
        db.commit()
        return serialize_job(job, events=[{"level": "info", "message": f"{job_type} completed", "payload": result}])
    except Exception as exc:
        job.status = "failed"
        job.failure_count = 1
        job.finished_at = datetime.now(UTC)
        db.add(JobEvent(job_id=job.id, level="error", message=str(exc), payload={}))
        db.commit()
        raise


def list_jobs(db: Session, limit: int = 25) -> list[dict[str, Any]]:
    jobs = db.scalars(select(JobRun).order_by(JobRun.started_at.desc()).limit(limit)).all()
    return [serialize_job(job) for job in jobs]


def get_job(db: Session, job_id: int) -> dict[str, Any] | None:
    job = db.get(JobRun, job_id)
    if job is None:
        return None
    events = db.scalars(select(JobEvent).where(JobEvent.job_id == job_id).order_by(JobEvent.created_at)).all()
    return serialize_job(job, events=[serialize_event(event) for event in events])


def list_model_runs(db: Session, limit: int = 25) -> list[dict[str, Any]]:
    runs = db.scalars(select(ModelRun).order_by(ModelRun.created_at.desc()).limit(limit)).all()
    return [serialize_model_run(run) for run in runs]


def serialize_job(job: JobRun, events: list[dict] | None = None) -> dict:
    return {
        "id": job.id,
        "job_type": job.job_type,
        "status": job.status,
        "parameters": job.parameters,
        "rows_read": job.rows_read,
        "rows_written": job.rows_written,
        "rows_skipped": job.rows_skipped,
        "failure_count": job.failure_count,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "finished_at": job.finished_at.isoformat() if job.finished_at else None,
        "events": events or [],
    }


def serialize_event(event: JobEvent) -> dict:
    return {
        "id": event.id,
        "job_id": event.job_id,
        "level": event.level,
        "message": event.message,
        "payload": event.payload,
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }


def serialize_model_run(run: ModelRun) -> dict:
    return {
        "id": run.id,
        "model_type": run.model_type,
        "version": run.version,
        "metrics": run.metrics,
        "artifact_path": run.artifact_path,
        "created_at": run.created_at.isoformat() if run.created_at else None,
    }
