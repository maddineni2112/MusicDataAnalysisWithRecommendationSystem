from pathlib import Path

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.services.evaluation import evaluate_recommender
from app.services.imports import import_csv, import_json, import_playlist_json
from app.services.jobs import get_job, list_jobs, list_model_runs, run_logged_job
from app.services.labels import apply_label_override, list_label_overrides
from app.services.quality import run_quality_checks
from app.services.spotify import collect_spotify_playlists, read_playlist_ids

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


@router.post("/import/playlist-json")
def admin_import_playlist_json(path: str, source_name: str, _: None = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    return run_logged_job(
        db,
        job_type="import_playlist_json",
        parameters={"path": path, "source_name": source_name},
        handler=lambda: import_playlist_json(db, Path(path), source_name),
    )


@router.post("/spotify/collect")
def collect_spotify(
    playlist_id: list[str] | None = None,
    playlist_file: str | None = None,
    market: str = "IN",
    limit_per_playlist: int = 100,
    _: None = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    playlist_ids = read_playlist_ids(Path(playlist_file) if playlist_file else None, playlist_id)
    if not playlist_ids:
        return {"status": "needs_playlist_ids", "message": "Provide one or more playlist_id values or a playlist_file path."}
    return run_logged_job(
        db,
        job_type="spotify_collect",
        parameters={"playlist_ids": playlist_ids, "market": market, "limit_per_playlist": limit_per_playlist},
        handler=lambda: collect_spotify_playlists(db, playlist_ids=playlist_ids, market=market, limit_per_playlist=limit_per_playlist),
    )


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


@router.get("/jobs/{job_id}")
def job_detail(job_id: int, _: None = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    job = get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/models/runs")
def model_runs(_: None = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    return {"items": list_model_runs(db)}


@router.post("/labels/override")
def override_label(track_id: int, dimension: str, value: str, reason: str | None = None, _: None = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    try:
        return {"status": "completed", "override": apply_label_override(db, track_id=track_id, dimension=dimension, value=value, reason=reason)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/labels/overrides")
def label_overrides(_: None = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    return {"items": list_label_overrides(db)}


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
