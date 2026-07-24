# Setup

## Local Docker

```bash
copy .env.example .env
docker compose up --build
```

## Database

```bash
docker compose exec api alembic upgrade head
```

## Sample Import

```bash
docker compose exec api python -m app.cli import csv data/sample/indian_music_sample.csv --source-name "Sample Indian Music Dataset"
docker compose exec api python -m app.cli import playlist-json data/sample/public_playlist_sample.json --source-name "Public Playlist Fixture"
docker compose exec api python -m app.cli quality run
docker compose exec api python -m app.cli recommender features
docker compose exec api python -m app.cli models train --seed-limit 14 --result-limit 5
```

Spotify collection requires `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`; public/sample imports do not.

## One-Command Local Demo

On Windows PowerShell, after Docker Desktop is running:

```powershell
.\scripts\local_demo.ps1
```

This starts the services, runs migrations, imports sample data, runs quality checks, builds the TF-IDF recommender artifact, and stores a small recommender evaluation run.

Open:

- Music dashboard: `http://127.0.0.1:8010/music/`
- FastAPI docs: `http://127.0.0.1:8001/docs`
- Admin ops: `http://127.0.0.1:8010/admin/`

## Existing Portfolio Integration

The existing portfolio project at `C:\Users\SampathNagaMaddineni\Documents\portfolio\django_portfolio` has a seed entry for **Indian Music Intelligence Platform**. Run its seed command after pulling the portfolio changes:

```powershell
cd C:\Users\SampathNagaMaddineni\Documents\portfolio\django_portfolio
python manage.py seed_portfolio
python manage.py runserver 127.0.0.1:8000
```

The project card opens `http://127.0.0.1:8010/music/` for the local demo while the portfolio stays on `http://127.0.0.1:8000/`.

## Portfolio Deliverables

Export the report PDF and pitch deck PPTX:

```powershell
.\scripts\export_deliverables.ps1 -Python "C:\Users\SampathNagaMaddineni\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
```

Capture local demo screenshots after both the music shell and portfolio are running:

```powershell
.\scripts\capture_demo_screenshots.ps1
```
