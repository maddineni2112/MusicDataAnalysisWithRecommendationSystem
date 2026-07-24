from pathlib import Path

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.services.evaluation import evaluate_recommender
from app.services.imports import import_csv, import_json
from app.services.jobs import list_jobs, run_logged_job
from app.services.quality import run_quality_checks

router = APIRouter(prefix="/admin")


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    if x_admin_token != get_settings().admin_shared_secret:
        raise HTTPException(status_code=403, detail="Admin access required")


@router.post("/import/csv")
def admin_import_csv(path: str, source_name: str, _: None = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    return run_logged_job(
        db,
        job_type="import_csv",
        parameters={"path": path, "source_name": source_name},
        handler=lambda: import_csv(db, Path(path), source_name),
    )


@router.post("/import/json")
def admin_import_json(path: str, source_name: str, _: None = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    return run_logged_job(
        db,
        job_type="import_json",
        parameters={"path": path, "source_name": source_name},
        handler=lambda: import_json(db, Path(path), source_name),
    )


@router.post("/spotify/collect")
def collect_spotify(_: None = Depends(require_admin)) -> dict:
    settings = get_settings()
    if not settings.spotify_client_id or not settings.spotify_client_secret:
        return {"status": "credential_required", "message": "Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET to enable playlist-first collection."}
    return {"status": "ready", "message": "Spotify credentials detected; playlist crawler implementation is the next data-collection slice."}


@router.post("/features/build")
def build_features(_: None = Depends(require_admin)) -> dict:
    return {"status": "completed", "message": "Current milestone builds recommendation features online from normalized labels and metadata."}


@router.post("/models/train")
def train_models(_: None = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    return run_logged_job(
        db,
        job_type="model_evaluation",
        parameters={"seed_limit": 25, "result_limit": 10},
        handler=lambda: evaluate_recommender(db, seed_limit=25, result_limit=10),
    )


@router.post("/recommendations/rebuild")
def rebuild_recommendations(_: None = Depends(require_admin)) -> dict:
    return {"status": "completed", "message": "Hybrid recommender computes online from normalized metadata in this milestone."}


@router.get("/jobs")
def jobs(_: None = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    return {"items": list_jobs(db)}


@router.post("/labels/override")
def override_label(_: None = Depends(require_admin)) -> dict:
    return {"status": "accepted", "message": "Label override persistence is planned after the owner review UI is connected."}


@router.post("/quality/run")
def quality_run(_: None = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    return run_logged_job(
        db,
        job_type="quality_run",
        parameters={},
        handler=lambda: {
            "rows_read": 0,
            "rows_written": len(run_quality_checks(db)),
            "rows_skipped": 0,
            "failure_count": 0,
        },
    )
