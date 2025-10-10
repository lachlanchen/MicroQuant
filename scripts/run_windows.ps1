# Load .env into current PowerShell process and run the server
if (Test-Path .env) {
  Get-Content .env | Where-Object { $_ -and $_ -notmatch '^#' } | ForEach-Object {
    $n,$v = $_ -split '=',2; [Environment]::SetEnvironmentVariable($n, $v, 'Process')
  }
}

if (-not (Test-Path .\.venv\Scripts\Activate.ps1)) {
  Write-Error ".venv not found. Run scripts/setup_windows.ps1 first."; exit 1
}

.\.venv\Scripts\Activate.ps1
python -m app.server
