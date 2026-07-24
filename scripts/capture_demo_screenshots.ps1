param(
  [string]$MusicBaseUrl = "http://127.0.0.1:8010",
  [string]$PortfolioUrl = "http://127.0.0.1:8000/#projects",
  [string]$OutputDir = "docs/screenshots",
  [switch]$SkipPortfolio
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

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$pages = @(
  @{ Name = "dashboard"; Url = "$MusicBaseUrl/music/" },
  @{ Name = "songs"; Url = "$MusicBaseUrl/explorer/" },
  @{ Name = "artists"; Url = "$MusicBaseUrl/artists/" },
  @{ Name = "recommender"; Url = "$MusicBaseUrl/recommender/" },
  @{ Name = "model-insights"; Url = "$MusicBaseUrl/model-insights/" },
  @{ Name = "admin-ops"; Url = "$MusicBaseUrl/admin/" }
)

if (-not $SkipPortfolio) {
  $pages += @{ Name = "portfolio-project-card"; Url = $PortfolioUrl }
}

foreach ($page in $pages) {
  $target = Join-Path $OutputDir "$($page.Name).png"
  Write-Host "Capturing $($page.Name): $($page.Url)"
  npx --yes playwright screenshot --wait-for-timeout=2500 --viewport-size=1440,1000 $page.Url $target
  Assert-LastCommand "screenshot $($page.Name)"
}

Write-Host ""
Write-Host "Screenshots written to $OutputDir"
