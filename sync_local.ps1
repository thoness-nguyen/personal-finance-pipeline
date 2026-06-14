param([switch]$Register, [switch]$Unregister)

$ProjectDir         = $PSScriptRoot
$PythonExe          = "C:\Users\Thoness\source\BudgetManagement\.venv\Scripts\python.exe"
$OrchestratorScript = Join-Path $ProjectDir "orchestrator\run_pipeline.py"
$LogFile            = Join-Path $ProjectDir "logs\sync_local.log"

if ($Unregister) {
    Unregister-ScheduledTask -TaskName "FinancePipeline-LocalSync" -Confirm:$false
    Write-Host "Scheduled task 'FinancePipeline-LocalSync' removed."
    exit 0
}

if ($Register) {
    $taskName   = "FinancePipeline-LocalSync"
    $scriptPath = $MyInvocation.MyCommand.Path
    $arg        = '-NonInteractive -ExecutionPolicy Bypass -File "' + $scriptPath + '"'

    $action   = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arg
    $trigger  = New-ScheduledTaskTrigger -Daily -At "22:30"
    $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 10) -StartWhenAvailable -RunOnlyIfNetworkAvailable

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
    } catch {}
    Start-Sleep -Seconds 3
}
if (-not $apiReady) { Log "ERROR: python-api not ready."; exit 1 }

Log "Running orchestrator..."
$env:PYTHONUNBUFFERED = "1"
& $PythonExe $OrchestratorScript --service python 2>&1 | ForEach-Object { Log $_ }

if ($LASTEXITCODE -eq 0) {
    Log "=== sync_local completed successfully ==="
} else {
    Log "=== sync_local FAILED (exit $LASTEXITCODE) ==="
    exit $LASTEXITCODE
}
