Param(
  [string]$EnvName = "mtrader",
  [string]$PyVersion = "3.11"
)

Write-Host "Ensuring Python $PyVersion venv and installing requirements..." -ForegroundColor Cyan

# Prefer py launcher
$py = "py -$PyVersion"
try { $null = & py -$PyVersion -V 2>$null } catch { $py = $null }
if (-not $py) {
  Write-Error "Python $PyVersion not found via 'py'. Install Python $PyVersion or adjust PyVersion."; exit 1
}

# Create venv if missing
if (-not (Test-Path .\.venv)) {
  & py -$PyVersion -m venv .venv
}
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Done. Activate with .\\.venv\\Scripts\\Activate.ps1 and run: python -m app.server" -ForegroundColor Green
