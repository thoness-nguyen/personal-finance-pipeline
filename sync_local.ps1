param([switch]$Register, [switch]$Unregister)

$ProjectDir = $PSScriptRoot
$PythonExe = "C:\Users\Thoness\source\BudgetManagement\.venv\Scripts\python.exe"
$DbtExe = "C:\Users\Thoness\source\BudgetManagement\.venv\Scripts\dbt.exe"
$OrchestratorScript = Join-Path $ProjectDir "orchestrator\run_pipeline.py"
$DbtProjectDir = Join-Path $ProjectDir "transformation\dbt_project"
$LogFile = Join-Path $ProjectDir "logs\sync_local.log"

if ($Unregister) {
    Unregister-ScheduledTask -TaskName "FinancePipeline-LocalSync" -Confirm:$false
    Write-Host "Scheduled task 'FinancePipeline-LocalSync' removed."
    exit 0
}

if ($Register) {
    $taskName = "FinancePipeline-LocalSync"
    $scriptPath = $MyInvocation.MyCommand.Path
    $arg = '-NonInteractive -ExecutionPolicy Bypass -File "' + $scriptPath + '"'

    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arg
    $trigger = New-ScheduledTaskTrigger -Daily -At "22:30"
    $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 15) -StartWhenAvailable -RunOnlyIfNetworkAvailable

    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest -Force
    Write-Host "Scheduled task '$taskName' registered -- runs daily at 22:30."
    Write-Host "To run it now: Start-ScheduledTask -TaskName '$taskName'"
    exit 0
}

New-Item -ItemType Directory -Force -Path (Split-Path $LogFile) | Out-Null

function Log($msg) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  $msg"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line
}

Log "=== sync_local started ==="

Set-Location $ProjectDir

# Start Docker Desktop if the daemon is not already running
$dockerDesktop = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
docker info 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Log "Docker not running -- starting Docker Desktop..."
    if (Test-Path $dockerDesktop) {
        Start-Process $dockerDesktop
    }
    else {
        Log "ERROR: Docker Desktop not found at '$dockerDesktop'. Please start it manually."
        exit 1
    }
    # Wait up to 90 s for the daemon to become ready
    $daemonReady = $false
    for ($i = 1; $i -le 9; $i++) {
        Start-Sleep -Seconds 10
        docker info 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { $daemonReady = $true; break }
        Log "Waiting for Docker daemon ($($i * 10)s / 90s)..."
    }
    if (-not $daemonReady) { Log "ERROR: Docker daemon did not start in 90 s."; exit 1 }
    Log "Docker daemon is ready."
}
else {
    Log "Docker daemon already running."
}

Log "Starting Docker containers..."
docker compose up -d mysql python-api 2>&1 | ForEach-Object { Log $_ }

Log "Waiting for MySQL..."
$ready = $false
for ($i = 1; $i -le 20; $i++) {
    docker compose exec -T mysql mysqladmin ping --silent 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { $ready = $true; break }
    Start-Sleep -Seconds 3
}
if (-not $ready) { Log "ERROR: MySQL not ready."; exit 1 }

Log "Waiting for python-api..."
$apiReady = $false
for ($i = 1; $i -le 20; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($r.StatusCode -eq 200) { $apiReady = $true; break }
    }
    catch {}
    Start-Sleep -Seconds 3
}
if (-not $apiReady) { Log "ERROR: python-api not ready."; exit 1 }

Log "Running orchestrator..."
$env:PYTHONUNBUFFERED = "1"
& $PythonExe $OrchestratorScript --service python 2>&1 | ForEach-Object { Log $_ }

if ($LASTEXITCODE -ne 0) {
    Log "=== sync_local FAILED (exit $LASTEXITCODE) ==="
    exit $LASTEXITCODE
}

Log "Ingestion succeeded -- running dbt build..."
& $DbtExe build --project-dir $DbtProjectDir --profiles-dir "$env:USERPROFILE\.dbt" 2>&1 | ForEach-Object { Log $_ }

if ($LASTEXITCODE -eq 0) {
    Log "=== sync_local completed successfully ==="
}
else {
    Log "=== sync_local FAILED -- dbt build failed (exit $LASTEXITCODE) ==="
    exit $LASTEXITCODE
}
