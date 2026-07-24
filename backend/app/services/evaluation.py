from __future__ import annotations

from statistics import mean

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import ModelRun, RecommendationRun, RecommendationResult, Track
from app.services.recommender import recommend_tracks


def evaluate_recommender(db: Session, *, seed_limit: int = 25, result_limit: int = 10) -> dict:
    seeds = db.scalars(select(Track).order_by(Track.id).limit(seed_limit)).all()
    total_tracks = db.scalar(select(func.count()).select_from(Track)) or 0
    if not seeds or total_tracks <= 1:
        metrics = {
            "seed_count": len(seeds),
            "result_limit": result_limit,
            "coverage": 0,
            "avg_results_per_seed": 0,
            "seed_exclusion_pass_rate": 1,
            "avg_score": 0,
        }
        run = ModelRun(model_type="hybrid_recommender_evaluation", version="v2-alpha-local", metrics=metrics, artifact_path=None)
        db.add(run)
        db.commit()
        return {"rows_read": len(seeds), "rows_written": 1, "failure_count": 0, "metrics": metrics, "model_run_id": run.id}

    recommended_ids: set[int] = set()
    result_counts: list[int] = []
    scores: list[float] = []
    seed_exclusion_checks: list[bool] = []

    model_run = ModelRun(model_type="hybrid_recommender_evaluation", version="v2-alpha-local", metrics={}, artifact_path=None)
    db.add(model_run)
    db.flush()

    stored_results = 0
    for seed in seeds:
        results = recommend_tracks(db, seed.id, limit=result_limit)
        result_counts.append(len(results))
        seed_exclusion_checks.append(all(item["track"].id != seed.id for item in results))
        recommendation_run = RecommendationRun(seed_track_id=seed.id, model_run_id=model_run.id, parameters={"result_limit": result_limit})
        db.add(recommendation_run)
        db.flush()
        for rank, item in enumerate(results, start=1):
            recommended_ids.add(item["track"].id)
            scores.append(float(item["score"]))
            db.add(
                RecommendationResult(
                    run_id=recommendation_run.id,
                    track_id=item["track"].id,
                    rank=rank,
                    score=float(item["score"]),
                    reasons=item["reasons"],
                    score_breakdown=item["score_breakdown"],
                )
            )
            stored_results += 1

    metrics = {
        "seed_count": len(seeds),
        "result_limit": result_limit,
        "coverage": round(len(recommended_ids) / total_tracks, 4),
        "unique_recommended_tracks": len(recommended_ids),
        "avg_results_per_seed": round(mean(result_counts), 2) if result_counts else 0,
        "seed_exclusion_pass_rate": round(sum(seed_exclusion_checks) / len(seed_exclusion_checks), 4) if seed_exclusion_checks else 1,
        "avg_score": round(mean(scores), 4) if scores else 0,
    }
    model_run.metrics = metrics
    db.commit()
    return {
        "rows_read": len(seeds),
        "rows_written": stored_results,
        "failure_count": 0,
        "metrics": metrics,
        "model_run_id": model_run.id,
    }
