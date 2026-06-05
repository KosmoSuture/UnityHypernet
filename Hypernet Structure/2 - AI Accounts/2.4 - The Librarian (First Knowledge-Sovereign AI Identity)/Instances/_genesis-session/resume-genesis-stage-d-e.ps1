# resume-genesis-stage-d-e.ps1 -- resume proto-Master-Librarian for Stage D (naming) + Stage E (self-design).
# Authority: Codex round-6 ACCEPT + [[feedback-overnight-autonomous-authority]] + conservative E→F boundary.

$ErrorActionPreference = 'Continue'
$sid    = '401dd34a-8f7f-4d4e-a61d-f82d86d8e352'
$dir    = 'c:\Hypernet\Hypernet Structure\2 - AI Accounts\2.4 - The Librarian (First Knowledge-Sovereign AI Identity)\Instances\_genesis-session'
$msgFile = Join-Path $dir 'RESUME-MESSAGE-STAGE-D-E.txt'
$log    = Join-Path $dir 'stream.jsonl'
$err    = Join-Path $dir 'stream.err'
$status = Join-Path $dir 'STATUS.txt'
$stop   = Join-Path $dir 'STOP'
$tools  = 'Read,Glob,Grep,Write,Edit,Bash,TodoWrite'
$model  = 'claude-opus-4-8[1m]'

$append = @'
ORCHESTRATION CONTEXT (Keel spawner; Stage D+E AUTHORIZED per Codex round-6 ACCEPT 20260603T004722Z; conservative E→F boundary still binds — HARD STOP at Stage E completion, NO Spawn Packets in this resume). HEADLESS via `claude --resume`. Tools: Read, Glob, Grep, Write, Edit, Bash, TodoWrite. NODE 0 marker still valid (no re-auth needed). Gate discipline: name yourself + design team docs + STOP at E→F boundary. NO background jobs. No external actions (GitHub pushes, R-PUSH-1, new external-service grants remain Matt-only). Output absolute paths of artifacts + posted coordination message on stdout, then stop.
'@

$resumeMsg = Get-Content -LiteralPath $msgFile -Raw

function LogStatus($m) { "$([DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')) $m" | Add-Content -LiteralPath $status }

LogStatus "stage-d-e resume wrapper start sid=$sid model=$model (PROCEEDING POST ACCEPT)"
$attempt = 0
$first = $true
while ($true) {
  if (Test-Path -LiteralPath $stop) { LogStatus 'STOP file present -> exiting wrapper'; break }
  $attempt++
  if ($first) {
    LogStatus "attempt=$attempt (initial stage-d-e resume)"
    claude --resume $sid -p $resumeMsg --model $model --permission-mode bypassPermissions --tools $tools --strict-mcp-config --output-format stream-json --verbose --add-dir 'c:\Hypernet' --append-system-prompt $append >> $log 2> $err
    $code = $LASTEXITCODE
    $first = $false
  } else {
    LogStatus "attempt=$attempt (rate-limit resume)"
    $rlMsg = 'Resume your Stage D + Stage E work. After writing identity.md + BOOT-SEQUENCE.md + team-design.md + posting the completion coordination message, STOP cleanly at the E→F boundary.'
    claude --resume $sid -p $rlMsg --model $model --permission-mode bypassPermissions --tools $tools --strict-mcp-config --output-format stream-json --verbose --add-dir 'c:\Hypernet' --append-system-prompt $append >> $log 2> $err
    $code = $LASTEXITCODE
  }
  LogStatus "attempt=$attempt exit=$code"
  if ($code -eq 0) { LogStatus 'clean exit (stage-d-e complete / stopped at E→F boundary) -> wrapper done'; break }
  $tail = ''
  if (Test-Path -LiteralPath $err) { $tail = (Get-Content -LiteralPath $err -Tail 40 -ErrorAction SilentlyContinue | Out-String) }
  if ($tail -match '(?i)rate.?limit|usage limit|quota|overloaded|too many requests|\b429\b|\b529\b|insufficient|capacity') {
    LogStatus 'token/usage limit detected -> sleeping 3600s then resume'
    Start-Sleep -Seconds 3600
    continue
  } else {
    LogStatus ("non-limit error -> stopping wrapper. tail: " + ($tail -replace '\s+',' ').Substring(0,[Math]::Min(300,($tail).Length)))
    break
  }
}
LogStatus 'stage-d-e resume wrapper end'
