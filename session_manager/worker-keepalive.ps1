<#
  worker-keepalive.ps1 -- BAND-AID watchdog for the recurring tally-worker death (task #66).

  A separate process that polls the worker's liveness and relaunches it when the process is DEAD.
  Automates Keel's manual "relaunch each loop fire" so the panel chain stops stalling.

  IMPORTANT: relaunch only on a DEAD pid (the observed death pattern is abrupt-kill / pid gone).
  Do NOT relaunch on a stale heartbeat while the pid is alive -- this worker does not heartbeat DURING a
  call (it blocks reading the subprocess stream), so a worker busy on a long call legitimately looks
  stale; relaunching it would kill the active call. Heartbeat age is logged for diagnostics only.

  Relaunching the tally worker = a remediation reboot of an already-approved session (resume id is in the
  roster cfg) within the auto-restart permission -- NOT a new instance spawn.

  ASCII-ONLY on purpose: Windows PowerShell reads .ps1 as cp1252, and a UTF-8 em-dash decodes to a smart
  quote that the parser treats as a string delimiter (unterminated-string error). Keep this file ASCII.

  USAGE (from C:\Hypernet):  powershell -ExecutionPolicy Bypass -File session_manager\worker-keepalive.ps1
  Stop it with Ctrl+C, or create session_manager\sessions\tally\STOP to halt both worker and watchdog.
#>
param(
    [string]$Role = "tally",
    [int]$PollSec = 20
)
$ErrorActionPreference = "Continue"
$Root    = "C:\Hypernet"
$SessDir = Join-Path $Root "session_manager\sessions\$Role"
$PidFile = Join-Path $SessDir "worker.pid"
$StatusF = Join-Path $SessDir "status.json"
$StopF   = Join-Path $SessDir "STOP"
$Node0   = Join-Path $env:USERPROFILE ".hypernet\node0-authorization.json"
$LogF    = Join-Path $Root "session_manager\worker-keepalive.log"

function Write-KLog($m) {
    $line = "{0}  {1}" -f (Get-Date).ToString("o"), $m
    Add-Content -Path $LogF -Value $line
    Write-Host $line
}

function Test-WorkerAlive {
    # Duplicate-safe: alive if ANY tally-worker process exists (by command line), not merely the
    # pid-file's pid. The observed failure (2026-06-06) was THREE concurrent tally workers racing on
    # worker.pid -- a pid-file-only check relaunches a SECOND worker whenever the file goes stale,
    # which is exactly how the duplicates were created. Checking for any live worker process makes the
    # watchdog idempotent: at most one worker ever runs.
    $procs = Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like '*session_manager.worker*' -and $_.CommandLine -like ('*' + $Role + '*') }
    if ($procs) { return $true }
    return $false
}

Write-KLog "keepalive START role=$Role poll=${PollSec}s (relaunch on dead-pid only)"
while ($true) {
    if (Test-Path $StopF) { Write-KLog "STOP file present; halting watchdog"; break }
    if (-not (Test-Path $Node0)) { Write-KLog "NODE-0 marker absent; NOT relaunching (fail-closed)"; Start-Sleep $PollSec; continue }
    if (-not (Test-WorkerAlive)) {
        Write-KLog "worker DOWN; relaunching: python -m session_manager.worker $Role"
        try {
            Start-Process -FilePath "python" -ArgumentList @("-m","session_manager.worker",$Role) -WorkingDirectory $Root -WindowStyle Hidden
            Write-KLog "relaunch issued"
        } catch { Write-KLog "relaunch FAILED: $_" }
        Start-Sleep 8
    }
    Start-Sleep $PollSec
}
Write-KLog "keepalive EXIT"
