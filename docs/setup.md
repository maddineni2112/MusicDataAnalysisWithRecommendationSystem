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
docker compose exec api python -m app.cli quality run
```

Spotify collection requires `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`; public/sample imports do not.

## One-Command Local Demo

On Windows PowerShell, after Docker Desktop is running:

```powershell
.\scripts\local_demo.ps1
```

This starts the services, runs migrations, imports sample data, runs quality checks, stores a small recommender evaluation run, and prepares the recommender path.

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
