# Deployment

## Preferred Topology

- Render or Railway
- FastAPI service
- Django music shell/portfolio service
- managed PostgreSQL

Target URL style:

- preferred: portfolio subpath such as `/projects/music-intelligence/`
- fallback: separate deployed service URL linked from the portfolio project card

Free/low-cost hosting may require a smaller deployed dataset than the 100k-300k local research target.

## Production Entrypoints

The Dockerfiles use production commands by default:

- API: `backend/start.sh` runs Alembic migrations and starts Uvicorn on `$PORT`.
- Django shell: `django_music/start.sh` runs `collectstatic` and starts Gunicorn on `$PORT`.

Docker Compose still overrides those commands for local hot-reload development.

## Render Blueprint

`render.yaml` defines:

- `indian-music-intelligence-api`
- `indian-music-intelligence-shell`
- `indian-music-intelligence-db`

Required secrets:

- `ADMIN_SHARED_SECRET`
- `DJANGO_SECRET_KEY` or generated value
- `PUBLIC_API_BASE_URL` set to the public API URL for browser calls
- `BACKEND_CORS_ORIGINS` set to the public portfolio/shell origins allowed to call the API
- optional `SPOTIFY_CLIENT_ID`
- optional `SPOTIFY_CLIENT_SECRET`

Health checks:

- API: `/api/health`
- Django shell: `/health/`

## Deployment Smoke Checks

After deployment:

```bash
curl https://<api-host>/api/health
curl https://<api-host>/api/dashboard/overview
curl https://<shell-host>/health/
```

Then run the sample import from a one-off API shell/job if the database is empty:

```bash
python -m app.cli import csv data/sample/indian_music_sample.csv --source-name "Sample Indian Music Dataset"
python -m app.cli import playlist-json data/sample/public_playlist_sample.json --source-name "Public Playlist Fixture"
python -m app.cli quality run
python -m app.cli models train --seed-limit 18 --result-limit 5
```
