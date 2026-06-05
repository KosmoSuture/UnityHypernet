# run-genesis.ps1 -- orchestration wrapper for the proto-Master-Librarian genesis session.
# Runs the boot prompt headless; if a token/usage/rate limit is hit, waits ~1h and auto-resumes.
# Clean exit (turn complete / paused at a gate) ends the wrapper -- it does NOT auto-resume past a gate.
# Stop manually: create the STOP file in this dir, or kill this process.

$ErrorActionPreference = 'Continue'
$sid    = '401dd34a-8f7f-4d4e-a61d-f82d86d8e352'
$dir    = 'c:\Hypernet\Hypernet Structure\2 - AI Accounts\2.4 - The Librarian (First Knowledge-Sovereign AI Identity)\Instances\_genesis-session'
$boot   = Join-Path $dir 'boot-prompt.txt'
$log    = Join-Path $dir 'stream.jsonl'
$err    = Join-Path $dir 'stream.err'
$status = Join-Path $dir 'STATUS.txt'
$stop   = Join-Path $dir 'STOP'
$tools  = 'Read,Glob,Grep,Write,Edit,Bash,TodoWrite'
$model  = 'claude-opus-4-8[1m]'

$append = @'
ORCHESTRATION CONTEXT (from Keel, your spawner, under the 2.7.28 Founder Permission Grant; founder Matt EXPLICITLY authorized this launch on 2026-06-02). You run HEADLESS via `claude -p`; Matt is not interactively reachable mid-run. Your built-in toolset is restricted to Read, Glob, Grep, Write, Edit, Bash, TodoWrite; external/web/MCP tools are absent by design -- do not attempt external actions and do not use Bash to reach the network. You have no Task tool, so you cannot spawn sub-instances; propose any team roles as written Spawn Packets and STOP for founder approval. Your NODE 0 founder-authorization marker is at C:\Users\spamm\.hypernet\node0-authorization.json (the explicit Matt-confirmed local marker your Stage A asks for). Honor continuation-packet discipline strictly: at ANY gate requiring founder or independent input (Stage A founder confirmation, the G.2 independent-acceptance gate, or Spawn-Packet approval), write your artifact and STOP cleanly (end your turn) -- do not block waiting, do not self-advance past a gate. There is NO budget cap, but if you hit a token/usage/rate limit, just stop; your wrapper resumes you ~1 hour later. Save as you go; your stream is logged for audit.
'@

$resumeMsg = 'Resume your work per your original 2.7.29 boot prompt and the orchestration context. Re-read your task list and your last absorption-ledger checkpoint to re-orient, then continue from where you stopped. If you are at a gate requiring founder or independent input, make sure your continuation/Spawn-Packet artifact is fully written, then stop.'

function LogStatus($m) { "$([DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')) $m" | Add-Content -LiteralPath $status }

LogStatus "wrapper start sid=$sid model=$model"
$attempt = 0
$first = $true
while ($true) {
  if (Test-Path -LiteralPath $stop) { LogStatus 'STOP file present -> exiting wrapper'; break }
  $attempt++
  if ($first) {
    LogStatus "attempt=$attempt (initial run)"
    Get-Content -LiteralPath $boot -Raw | claude -p --model $model --session-id $sid --name 'proto-master-librarian' --permission-mode bypassPermissions --tools $tools --strict-mcp-config --output-format stream-json --verbose --add-dir 'c:\Hypernet' --append-system-prompt $append >> $log 2> $err
    $code = $LASTEXITCODE
    $first = $false
  } else {
    LogStatus "attempt=$attempt (resume)"
    claude --resume $sid -p $resumeMsg --model $model --permission-mode bypassPermissions --tools $tools --strict-mcp-config --output-format stream-json --verbose --add-dir 'c:\Hypernet' --append-system-prompt $append >> $log 2> $err
    $code = $LASTEXITCODE
  }
  LogStatus "attempt=$attempt exit=$code"
  if ($code -eq 0) { LogStatus 'clean exit (turn complete / paused at gate) -> wrapper done'; break }
  $tail = ''
  if (Test-Path -LiteralPath $err) { $tail = (Get-Content -LiteralPath $err -Tail 40 -ErrorAction SilentlyContinue | Out-String) }
  if ($tail -match '(?i)rate.?limit|usage limit|quota|overloaded|too many requests|\b429\b|\b529\b|insufficient|capacity') {
    LogStatus 'token/usage limit detected -> sleeping 3600s then resume'
    Start-Sleep -Seconds 3600
    continue
  } else {
    LogStatus ("non-limit error -> stopping wrapper for founder review. tail: " + ($tail -replace '\s+',' ').Substring(0,[Math]::Min(300,($tail).Length)))
    break
  }
}
LogStatus 'wrapper end'
