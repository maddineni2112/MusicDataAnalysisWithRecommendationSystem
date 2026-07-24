from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import JobEvent, JobRun


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
