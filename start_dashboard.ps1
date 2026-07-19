<#
.SYNOPSIS
    Starts the local Finance Dashboard on demand.

.DESCRIPTION
    1. Starts Docker Desktop / the daemon if it isn't already running.
    2. Starts only the MySQL container (data is refreshed separately by
       sync_local.ps1 on its own schedule — this script never runs ETL).
    3. Launches Streamlit locally against MySQL on localhost:3307, which
       opens your default browser automatically.
    4. When you close the browser and press Ctrl+C (or close this window),
       you'll be asked whether to also stop the MySQL container.
#>

$ProjectDir = $PSScriptRoot
$StreamlitDir = Join-Path $ProjectDir "visualization\streamlit_app"
$StreamlitExe = "C:\Users\Thoness\source\BudgetManagement\.venv\Scripts\streamlit.exe"
$DockerDesktop = "C:\Program Files\Docker\Docker\Docker Desktop.exe"

function Log($msg) {
    Write-Host "$(Get-Date -Format 'HH:mm:ss')  $msg"
}

Set-Location $ProjectDir

# ── 1. Make sure the Docker daemon is running ─────────────────────────────
docker info 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Log "Docker not running -- starting Docker Desktop..."
    if (Test-Path $DockerDesktop) {
        Start-Process $DockerDesktop
    }
    else {
        Log "ERROR: Docker Desktop not found at '$DockerDesktop'. Start it manually and re-run this script."
        Read-Host "Press Enter to close"
        exit 1
    }

    $daemonReady = $false
    for ($i = 1; $i -le 12; $i++) {
        Start-Sleep -Seconds 10
        docker info 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { $daemonReady = $true; break }
        Log "Waiting for Docker daemon ($($i * 10)s / 120s)..."
    }
    if (-not $daemonReady) {
        Log "ERROR: Docker daemon did not start in time."
        Read-Host "Press Enter to close"
        exit 1
    }
    Log "Docker daemon is ready."
}
else {
    Log "Docker daemon already running."
}

# ── 2. Start the MySQL container only ─────────────────────────────────────
Log "Starting MySQL container..."
docker compose up -d mysql 2>&1 | ForEach-Object { Log $_ }

Log "Waiting for MySQL to accept connections..."
$ready = $false
for ($i = 1; $i -le 20; $i++) {
    docker compose exec -T mysql mysqladmin ping --silent 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { $ready = $true; break }
    Start-Sleep -Seconds 3
}
if (-not $ready) {
    Log "ERROR: MySQL did not become ready in time."
    Read-Host "Press Enter to close"
    exit 1
}
Log "MySQL is ready."

# ── 3. Launch Streamlit locally (opens your browser automatically) ───────
$env:MYSQL_HOST = "localhost"
$env:MYSQL_PORT = "3307"

Log "Starting Streamlit dashboard -- press Ctrl+C in this window to stop."
Push-Location $StreamlitDir
try {
    & $StreamlitExe run app.py
}
finally {
    Pop-Location
}

# ── 4. Streamlit stopped (Ctrl+C or window closed) ────────────────────────
Log "Streamlit stopped."
$answer = Read-Host "Stop the MySQL container too? (y/N)"
if ($answer -match '^[Yy]') {
    docker compose stop mysql
    Log "MySQL container stopped."
}
else {
    Log "Leaving MySQL container running."
}
Read-Host "Press Enter to close this window"
