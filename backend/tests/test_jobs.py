from datetime import UTC, datetime
from types import SimpleNamespace

from app.services.jobs import serialize_event, serialize_job, serialize_model_run


def test_serialize_job_includes_events_and_counts() -> None:
    job = SimpleNamespace(
        id=7,
        job_type="model_evaluation",
        status="completed",
        parameters={"seed_limit": 10},
        rows_read=10,
        rows_written=50,
        rows_skipped=0,
        failure_count=0,
        started_at=datetime(2026, 1, 1, tzinfo=UTC),
        finished_at=datetime(2026, 1, 1, 0, 1, tzinfo=UTC),
    )

    payload = serialize_job(job, events=[{"level": "info", "message": "done", "payload": {"ok": True}}])

    assert payload["id"] == 7
    assert payload["events"][0]["payload"] == {"ok": True}
    assert payload["rows_written"] == 50


def test_serialize_event_and_model_run_are_api_ready() -> None:
    event = SimpleNamespace(id=1, job_id=7, level="info", message="stored", payload={"rows": 2}, created_at=datetime(2026, 1, 1, tzinfo=UTC))
    model_run = SimpleNamespace(id=2, model_type="hybrid", version="v2", metrics={"coverage": 0.8}, artifact_path=None, created_at=datetime(2026, 1, 1, tzinfo=UTC))

    assert serialize_event(event)["created_at"].startswith("2026-01-01")
    assert serialize_model_run(model_run)["metrics"]["coverage"] == 0.8
