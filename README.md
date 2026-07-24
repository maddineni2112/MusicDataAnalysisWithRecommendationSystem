# Indian Music Intelligence Platform

Version 2.0 transforms the original Spotify music-analysis notebook into a full-stack ML platform for Indian music discovery, analytics, and recommendations. The project is designed as a portfolio-ready capstone for ML/data and Python backend roles.

## What This Platform Does

- Collects and imports Indian music metadata from Spotify-style playlist sources and public datasets.
- Stores normalized tracks, artists, albums, playlists, source lineage, labels, model runs, job logs, and recommendation outputs in PostgreSQL.
- Infers language, region, music type, mood, and genre/style labels with confidence scores.
- Provides public read-only dashboards, song/artist explorers, model insights, and hybrid recommendations.
- Provides owner-only data-ops workflows for imports, quality checks, feature building, training, and recommender rebuilds.

## Architecture

```text
Portfolio/Django shell + React islands
            |
            v
FastAPI ML/API service ---- PostgreSQL
            |
            v
Typer CLI jobs, imports, labeling, quality checks, recommender artifacts
```

## Repository Layout

```text
.
|-- archive/v1.0/          # Preserved original notebook/report/PPT
|-- backend/               # FastAPI, SQLAlchemy, ML services, Typer CLI
|-- django_music/          # Django page shell/templates for portfolio integration
|-- frontend/              # Vite React island source
|-- data/sample/           # Small committed demo data
|-- docs/                  # Architecture, setup, API, schema, modeling docs
|-- docker-compose.yml
`-- .env.example
```

## Quick Start

1. Copy environment files:

```bash
copy .env.example .env
copy backend\.env.example backend\.env
copy django_music\.env.example django_music\.env
```

2. Start local services:

```bash
docker compose up --build
```

3. Run migrations and import sample data:

```bash
docker compose exec api alembic upgrade head
docker compose exec api python -m app.cli import csv data/sample/indian_music_sample.csv --source-name "Sample Indian Music Dataset"
docker compose exec api python -m app.cli import playlist-json data/sample/public_playlist_sample.json --source-name "Public Playlist Fixture"
docker compose exec api python -m app.cli quality run
docker compose exec api python -m app.cli recommender rebuild
docker compose exec api python -m app.cli models train --seed-limit 14 --result-limit 5
```

4. Open:

- FastAPI: `http://localhost:8001/docs`
- Django music shell: `http://localhost:8010/music/`
- Admin ops page: `http://localhost:8010/admin/`

On Windows, the helper script runs the full local demo setup:

```powershell
.\scripts\local_demo.ps1
```

The existing portfolio repo can seed a project card that opens the local dashboard at `http://127.0.0.1:8010/music/` while the portfolio itself runs at `http://127.0.0.1:8000/`.

## Data Acquisition Seeds

The scalable Indian music acquisition plan is tracked in `data/seeds/indian_music_seed_manifest.json`. It covers 8 Indian language groups and 40 Spotify discovery queries while keeping reviewed playlist IDs and raw exports out of Git.

```bash
docker compose exec api python -m app.cli seeds validate
docker compose exec api python -m app.cli seeds export
docker compose exec api python -m app.cli seeds collect-spotify
```

`collect-spotify` requires reviewed playlist IDs in the manifest plus Spotify API credentials. Without IDs, it exits safely with `needs_playlist_ids`.

## v1.0 Archive

The original academic project is preserved under `archive/v1.0/`. It includes the PySpark notebook, report, presentation, and original recommender helper.

## Documentation Deliverables

- [Technical report source](docs/technical-report-v2.md)
- [Pitch deck source](docs/pitch-deck-v2.md)
- [Exported PDF report](docs/exports/Indian_Music_Intelligence_Platform_v2_Report.pdf)
- [Exported PPT pitch deck](docs/exports/Indian_Music_Intelligence_Platform_v2_Pitch_Deck.pptx)
- [Demo screenshots](docs/screenshots/README.md)
- [Acceptance checklist](docs/acceptance-checklist.md)
- [Architecture](docs/architecture.md)
- [Setup](docs/setup.md)
- [API](docs/api.md)
- [Database schema](docs/database-schema.md)
- [Data sources](docs/data-sources.md)
- [Modeling](docs/modeling.md)
- [Deployment](docs/deployment.md)
- [v1-to-v2 evolution](docs/v1-to-v2-evolution.md)

## Development Status

This branch implements a working v2 local demo: schema, APIs, CLI imports, public playlist fallback, credential-gated Spotify collection, automatic labeling rules, quality checks, explained recommendations, model insights, admin operations, Docker/Render deployment configuration, documentation sources, and a portfolio-linked Django shell. Spotify live collection remains credential-dependent and is designed not to block public-dataset development.
