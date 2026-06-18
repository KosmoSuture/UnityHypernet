<#
  worker-check-once.ps1 — ONE-SHOT worker liveness check + relaunch (task #66 keepalive).

  Designed to be run every ~2 min by a user-level Windows Scheduled Task. The OS scheduler is the
  indestructible watchdog — there is no long-lived watcher process to itself die abruptly (the residual
  death class, per the 153000Z investigation). Each run: if the worker PID is gone (the real death
  pattern) AND no STOP file AND the NODE-0 marker is present, relaunch the worker, then EXIT.

  A busy worker (blocked reading a long subprocess stream → stale heartbeat but ALIVE pid) is NEVER
  relaunched — relaunching it would kill the active call. Only a dead PID triggers relaunch.

  Relaunching the tally worker = a remediation reboot of an already-approved session (resume_session_id
  in roster cfg), within the auto-restart permission — not a new instance spawn.
#>
param([string]$Role = "tally")
$Root    = "C:\Hypernet"
$SessDir = Join-Path $Root "session_manager\sessions\$Role"
$PidFile = Join-Path $SessDir "worker.pid"
$StopF   = Join-Path $SessDir "STOP"
$Node0   = Join-Path $env:USERPROFILE ".hypernet\node0-authorization.json"
$LogF    = Join-Path $Root "session_manager\worker-keepalive.log"

function Log($m) { Add-Content -Path $LogF -Value ("{0}  {1}" -f (Get-Date).ToString("o"), $m) }

if (Test-Path $StopF)        { Log "check: STOP present -> not relaunching (intentional)"; exit 0 }
if (-not (Test-Path $Node0)) { Log "check: NODE-0 marker absent -> not relaunching (fail-closed)"; exit 0 }

$alive = $false
if (Test-Path $PidFile) {
    $procId = (Get-Content -Raw $PidFile).Trim()
    if ($procId -as [int]) {
        if (Get-Process -Id ([int]$procId) -ErrorAction SilentlyContinue) { $alive = $true }  # ALIVE pid => alive, never kill a busy worker
    }
}

if ($alive) { exit 0 }   # healthy (or busy) — nothing to do

Log "check: worker DOWN (pid gone) -> relaunching python -m session_manager.worker $Role"
try {
    Start-Process -FilePath "python" -ArgumentList @("-m","session_manager.worker",$Role) `
                  -WorkingDirectory $Root -WindowStyle Hidden
    Log "check: relaunch issued"
} catch {
    Log "check: relaunch FAILED: $_"
}
exit 0
