param(
  [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

function Assert-LastCommand {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Step
  )

  if ($LASTEXITCODE -ne 0) {
    throw "$Step failed with exit code $LASTEXITCODE"
  }
}

if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
}

if (-not $SkipBuild) {
  docker compose up --build -d
  Assert-LastCommand "docker compose up --build -d"
} else {
  docker compose up -d
  Assert-LastCommand "docker compose up -d"
}

docker compose exec api alembic upgrade head
Assert-LastCommand "alembic upgrade"
docker compose exec api python -m app.cli import csv data/sample/indian_music_sample.csv --source-name "Sample Indian Music Dataset"
Assert-LastCommand "sample CSV import"
docker compose exec api python -m app.cli import playlist-json data/sample/public_playlist_sample.json --source-name "Public Playlist Fixture"
Assert-LastCommand "sample playlist JSON import"
docker compose exec api python -m app.cli quality run
Assert-LastCommand "quality checks"
docker compose exec api python -m app.cli models train --seed-limit 14 --result-limit 5
Assert-LastCommand "model evaluation"
docker compose exec api python -m app.cli recommender rebuild
Assert-LastCommand "recommender rebuild"

Write-Host ""
Write-Host "Local music platform demo is ready:"
Write-Host "  Django music shell: http://127.0.0.1:8010/music/"
Write-Host "  FastAPI docs:       http://127.0.0.1:8001/docs"
Write-Host ""
Write-Host "Portfolio integration:"
Write-Host "  Run the portfolio seed command in C:\Users\SampathNagaMaddineni\Documents\portfolio\django_portfolio"
Write-Host "  Then open http://127.0.0.1:8000/#projects and click Indian Music Intelligence Platform."
