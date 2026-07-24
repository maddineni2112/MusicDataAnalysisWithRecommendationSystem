param(
  [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

& $Python scripts/export_deliverables.py

if ($LASTEXITCODE -ne 0) {
  throw "deliverable export failed with exit code $LASTEXITCODE"
}
