from __future__ import annotations

from statistics import mean

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import ModelRun, Playlist, PlaylistTrack, RecommendationRun, RecommendationResult, Track
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
    metrics.update(playlist_holdout_metrics(db, result_limit=result_limit))
    model_run.metrics = metrics
    db.commit()
    return {
        "rows_read": len(seeds),
        "rows_written": stored_results,
        "failure_count": 0,
        "metrics": metrics,
        "model_run_id": model_run.id,
    }


def playlist_holdout_metrics(db: Session, *, result_limit: int = 10, playlist_limit: int = 100) -> dict:
    playlist_ids = db.scalars(
        select(Playlist.id)
        .join(PlaylistTrack, PlaylistTrack.playlist_id == Playlist.id)
        .group_by(Playlist.id)
        .having(func.count(PlaylistTrack.track_id) >= 2)
        .order_by(Playlist.id)
        .limit(playlist_limit)
    ).all()
    evaluated = 0
    hits = 0
    ranks: list[int] = []
    candidate_counts: list[int] = []
    for playlist_id in playlist_ids:
        track_ids = db.scalars(
            select(PlaylistTrack.track_id)
            .where(PlaylistTrack.playlist_id == playlist_id)
            .order_by(PlaylistTrack.position.nullslast(), PlaylistTrack.track_id)
        ).all()
        if len(track_ids) < 2:
            continue
        seed_id = track_ids[0]
        heldout_ids = set(track_ids[1:])
        results = recommend_tracks(db, seed_id, limit=result_limit)
        recommended_ids = [item["track"].id for item in results]
        summary = holdout_result_summary(recommended_ids, heldout_ids)
        evaluated += 1
        candidate_counts.append(len(heldout_ids))
        if summary["hit"]:
            hits += 1
            ranks.append(summary["rank"])
    return {
        "playlist_holdout_evaluated": evaluated,
        "playlist_holdout_hit_rate": round(hits / evaluated, 4) if evaluated else 0,
        "playlist_holdout_hits": hits,
        "playlist_holdout_avg_rank": round(mean(ranks), 2) if ranks else 0,
        "playlist_holdout_avg_candidates": round(mean(candidate_counts), 2) if candidate_counts else 0,
    }


def holdout_result_summary(recommended_ids: list[int], heldout_ids: set[int]) -> dict:
    for rank, track_id in enumerate(recommended_ids, start=1):
        if track_id in heldout_ids:
            return {"hit": True, "rank": rank}
    return {"hit": False, "rank": 0}
