# v2.0 Acceptance Checklist

This checklist tracks the final plan toward a complete v2.0 release.

## Completed or Partially Completed

- v1.0 archived under `archive/v1.0/`.
- `v1.0` tag exists from the preserved baseline.
- `v2-platform` branch exists and is pushed.
- PostgreSQL schema and Alembic migration exist.
- FastAPI public APIs exist.
- FastAPI protected admin APIs exist.
- Django music shell exists.
- Existing portfolio project card points to the local music dashboard.
- Docker Compose local demo runs.
- CSV import works.
- playlist-style JSON import works.
- Spotify collection path exists and is credential-gated.
- source-controlled Indian music seed manifest exists.
- manifest validation/export/credential-gated collection commands exist.
- source lineage and raw snapshots are stored.
- automatic labels are inferred with confidence/evidence.
- label overrides persist separately.
- dashboard landing has KPIs and analytics.
- song explorer exists.
- song detail includes source playlists, effective labels, and similar tracks.
- artist explorer exists.
- artist detail exists.
- artist network endpoint/UI exists.
- recommender returns explained results.
- TF-IDF text similarity feature build exists.
- local vector-artifact fallback exists under ignored `artifacts/`.
- model insights show saved evaluation metrics.
- playlist holdout evaluation metrics are stored in model runs.
- admin page supports imports, quality checks, model evaluation, job history, job detail, model runs, and label overrides.
- sample data works without Spotify credentials.
- deployment-ready Docker start scripts exist.
- Render blueprint exists.
- technical report source exists.
- pitch deck source exists.
- exported PDF report exists under `docs/exports/`.
- exported PPT pitch deck exists under `docs/exports/`.
- local demo screenshots exist under `docs/screenshots/`.
- `v2.0-alpha` release notes exist.

## Still Required for Full v2.0

- larger 100k-300k track local/research dataset, or documented smaller deployed subset
- reviewed Spotify playlist IDs or public dataset files collected at scale
- optional sentence-transformer embedding workflow
- pgvector implementation where hosting supports it
- robust playlist holdout evaluation on larger collected data
- popularity prediction demo if official popularity data is sufficient
- production deployment
- deployed URL wired into portfolio card
- `v2.0-alpha` tag
- `v2.0-beta` and `v2.0` tags at appropriate release points
- final merge strategy into `main`

## Current Local Demo URLs

- Portfolio: `http://127.0.0.1:8000/`
- Music dashboard: `http://127.0.0.1:8010/music/`
- Admin Ops: `http://127.0.0.1:8010/admin/`
- API docs: `http://127.0.0.1:8001/docs`
