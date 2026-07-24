from pathlib import Path

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.services.imports import import_csv, import_json
from app.services.quality import run_quality_checks

router = APIRouter(prefix="/admin")


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    if x_admin_token != get_settings().admin_shared_secret:
        raise HTTPException(status_code=403, detail="Admin access required")


@router.post("/import/csv")
def admin_import_csv(path: str, source_name: str, _: None = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    return import_csv(db, Path(path), source_name)


@router.post("/import/json")
def admin_import_json(path: str, source_name: str, _: None = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    return import_json(db, Path(path), source_name)


@router.post("/spotify/collect")
def collect_spotify(_: None = Depends(require_admin)) -> dict:
    return {"status": "credential-dependent", "message": "Spotify playlist-first crawler scaffold is planned behind env credentials."}


@router.post("/features/build")
def build_features(_: None = Depends(require_admin)) -> dict:
    return {"status": "queued_scaffold", "message": "Feature-building job scaffold is ready for implementation."}


@router.post("/models/train")
def train_models(_: None = Depends(require_admin)) -> dict:
    return {"status": "queued_scaffold", "message": "Model training scaffold is ready for implementation."}


@router.post("/recommendations/rebuild")
def rebuild_recommendations(_: None = Depends(require_admin)) -> dict:
    return {"status": "completed_scaffold", "message": "Hybrid recommender computes online from normalized metadata in this milestone."}


@router.get("/jobs")
def jobs(_: None = Depends(require_admin)) -> dict:
    return {"items": []}


@router.post("/labels/override")
def override_label(_: None = Depends(require_admin)) -> dict:
    return {"status": "scaffolded"}


@router.post("/quality/run")
def quality_run(_: None = Depends(require_admin), db: Session = Depends(get_db)) -> dict:
    results = run_quality_checks(db)
    return {"results": [{"id": result.id, "status": result.status, "count": result.count} for result in results]}
