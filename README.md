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
├── archive/v1.0/          # Preserved original notebook/report/PPT
├── backend/               # FastAPI, SQLAlchemy, ML services, Typer CLI
├── django_music/          # Django page shell/templates for portfolio integration
├── frontend/              # Vite React island source
├── data/sample/           # Small committed demo data
├── docs/                  # Architecture, setup, API, schema, modeling docs
├── docker-compose.yml
└── .env.example
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
docker compose exec api python -m app.cli quality run
docker compose exec api python -m app.cli recommender rebuild
```

4. Open:

- FastAPI: `http://localhost:8001/docs`
- Django music shell: `http://localhost:8000/music/`

On Windows, the helper script runs the full local demo setup:

```powershell
.\scripts\local_demo.ps1
```

The existing portfolio repo can seed a project card that opens the local dashboard at `http://127.0.0.1:8000/music/`.

## v1.0 Archive

The original academic project is preserved under `archive/v1.0/`. It includes the PySpark notebook, report, presentation, and original recommender helper.

## Development Status

This branch implements the v2 foundation: schema, APIs, CLI, sample imports, automatic labeling rules, quality checks, hybrid recommender scaffolding, documentation, and portfolio integration shell. Spotify live collection remains credential-dependent and is designed not to block public-dataset development.
