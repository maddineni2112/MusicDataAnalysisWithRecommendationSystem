param(
  [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
}

if (-not $SkipBuild) {
  docker compose up --build -d
} else {
  docker compose up -d
}

docker compose exec api alembic upgrade head
docker compose exec api python -m app.cli import csv data/sample/indian_music_sample.csv --source-name "Sample Indian Music Dataset"
docker compose exec api python -m app.cli quality run
docker compose exec api python -m app.cli recommender rebuild

Write-Host ""
Write-Host "Local music platform demo is ready:"
Write-Host "  Django music shell: http://127.0.0.1:8000/music/"
Write-Host "  FastAPI docs:       http://127.0.0.1:8001/docs"
Write-Host ""
Write-Host "Portfolio integration:"
Write-Host "  Run the portfolio seed command in C:\Users\SampathNagaMaddineni\Documents\portfolio\django_portfolio"
Write-Host "  Then open http://127.0.0.1:8000/#projects and click Indian Music Intelligence Platform."
