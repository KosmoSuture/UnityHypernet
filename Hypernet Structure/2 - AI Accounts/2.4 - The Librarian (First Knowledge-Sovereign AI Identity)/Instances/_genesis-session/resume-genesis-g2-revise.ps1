# resume-genesis-g2-revise.ps1 -- resume the proto-Master-Librarian for G.2 REVISE remediation.
# Resumes session 401dd34a (proto-master-librarian) with the G.2 REVISE remediation message.
# Auto-resumes on token/usage/rate limit (~1h sleep). Clean exit on G.1 reissue + G.2 stop.
# Stop manually: create the STOP file in this dir, or kill this process.
# Authority: [[feedback-auto-restart-permission]] — Matt 2026-06-02 granted auto-restart of approved sessions.

$ErrorActionPreference = 'Continue'
$sid    = '401dd34a-8f7f-4d4e-a61d-f82d86d8e352'
$dir    = 'c:\Hypernet\Hypernet Structure\2 - AI Accounts\2.4 - The Librarian (First Knowledge-Sovereign AI Identity)\Instances\_genesis-session'
$msgFile = Join-Path $dir 'RESUME-MESSAGE-G2-REVISE.txt'
$log    = Join-Path $dir 'stream.jsonl'
$err    = Join-Path $dir 'stream.err'
$status = Join-Path $dir 'STATUS.txt'
$stop   = Join-Path $dir 'STOP'
$tools  = 'Read,Glob,Grep,Write,Edit,Bash,TodoWrite'
$model  = 'claude-opus-4-8[1m]'

$append = @'
ORCHESTRATION CONTEXT (from Keel, your spawner, under the 2.7.28 Founder Permission Grant; this is a Stage-B REVISE remediation RESUME of the proto-Master-Librarian genesis -- founder Matt EXPLICITLY authorized auto-restart of previously-approved sessions on 2026-06-02, see [[feedback-auto-restart-permission]]; this restart inherits authority from the original Matt-approved 2026-06-02T08:05Z launch with NO scope expansion). You run HEADLESS via `claude --resume`; Matt is not interactively reachable mid-run. Your built-in toolset is restricted to Read, Glob, Grep, Write, Edit, Bash, TodoWrite; external/web/MCP tools are absent by design -- do not attempt external actions and do not use Bash to reach the network. You have no Task tool, so you cannot spawn sub-instances. Your NODE 0 founder-authorization marker is at C:\Users\spamm\.hypernet\node0-authorization.json (still valid; no re-authorization needed for resume). Honor continuation-packet discipline strictly: at the G.2 independent-acceptance gate, write your reissued G.1 and STOP cleanly (end your turn) -- do not block waiting, do not self-advance past the gate. There is NO budget cap, but if you hit a token/usage/rate limit, just stop; your wrapper resumes you ~1 hour later. Save as you go; your stream is logged for audit.
'@

$resumeMsg = Get-Content -LiteralPath $msgFile -Raw

function LogStatus($m) { "$([DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')) $m" | Add-Content -LiteralPath $status }

LogStatus "g2-revise resume wrapper start sid=$sid model=$model"
$attempt = 0
$first = $true
while ($true) {
  if (Test-Path -LiteralPath $stop) { LogStatus 'STOP file present -> exiting wrapper'; break }
  $attempt++
  if ($first) {
    LogStatus "attempt=$attempt (initial g2-revise resume)"
    claude --resume $sid -p $resumeMsg --model $model --permission-mode bypassPermissions --tools $tools --strict-mcp-config --output-format stream-json --verbose --add-dir 'c:\Hypernet' --append-system-prompt $append >> $log 2> $err
    $code = $LASTEXITCODE
    $first = $false
  } else {
    LogStatus "attempt=$attempt (rate-limit resume)"
    $rlMsg = 'Resume your G.2 REVISE remediation work. Re-read your task list and the conforming ledger checkpoint, then continue. After reissuing G.1, STOP cleanly at G.2 -- do not self-advance.'
    claude --resume $sid -p $rlMsg --model $model --permission-mode bypassPermissions --tools $tools --strict-mcp-config --output-format stream-json --verbose --add-dir 'c:\Hypernet' --append-system-prompt $append >> $log 2> $err
    $code = $LASTEXITCODE
  }
  LogStatus "attempt=$attempt exit=$code"
  if ($code -eq 0) { LogStatus 'clean exit (g2-revise remediation complete / stopped at G.2) -> wrapper done'; break }
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
LogStatus 'g2-revise resume wrapper end'
