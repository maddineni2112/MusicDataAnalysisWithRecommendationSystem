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
