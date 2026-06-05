# resume-genesis-g2-round2-revise.ps1 -- resume proto-Master-Librarian for round-2 REVISE remediation.
# Authority: [[feedback-auto-restart-permission]] + [[feedback-overnight-autonomous-authority]].

$ErrorActionPreference = 'Continue'
$sid    = '401dd34a-8f7f-4d4e-a61d-f82d86d8e352'
$dir    = 'c:\Hypernet\Hypernet Structure\2 - AI Accounts\2.4 - The Librarian (First Knowledge-Sovereign AI Identity)\Instances\_genesis-session'
$msgFile = Join-Path $dir 'RESUME-MESSAGE-G2-ROUND2-REVISE.txt'
$log    = Join-Path $dir 'stream.jsonl'
$err    = Join-Path $dir 'stream.err'
$status = Join-Path $dir 'STATUS.txt'
$stop   = Join-Path $dir 'STOP'
$tools  = 'Read,Glob,Grep,Write,Edit,Bash,TodoWrite'
$model  = 'claude-opus-4-8[1m]'

$append = @'
ORCHESTRATION CONTEXT (from Keel, your spawner, under the 2.7.28 Founder Permission Grant + Matt's 2026-06-02 overnight autonomous-authority grant; this is a Stage-B round-2 REVISE remediation RESUME — read-only authority same as before, no scope expansion). You run HEADLESS via `claude --resume`; Matt is asleep until morning. Your built-in toolset is restricted to Read, Glob, Grep, Write, Edit, Bash, TodoWrite; external/web/MCP tools are absent. NODE 0 marker at C:\Users\spamm\.hypernet\node0-authorization.json (still valid). Honor gate discipline: write reissued G.1 and STOP cleanly at G.2 — do not block waiting, do not self-advance. ★ INTEGRITY DISCIPLINE: do not repeat the round-1 rogue-job incident — verify NO background writer is still touching the ledger before computing the binding hash; re-hash twice seconds apart for stability before writing G.1. If a token/usage/rate limit hits, just stop; the wrapper resumes you ~1 hour later. Save as you go.
'@

$resumeMsg = Get-Content -LiteralPath $msgFile -Raw

function LogStatus($m) { "$([DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')) $m" | Add-Content -LiteralPath $status }

LogStatus "g2-round2-revise resume wrapper start sid=$sid model=$model"
$attempt = 0
$first = $true
while ($true) {
  if (Test-Path -LiteralPath $stop) { LogStatus 'STOP file present -> exiting wrapper'; break }
  $attempt++
  if ($first) {
    LogStatus "attempt=$attempt (initial g2-round2-revise resume)"
    claude --resume $sid -p $resumeMsg --model $model --permission-mode bypassPermissions --tools $tools --strict-mcp-config --output-format stream-json --verbose --add-dir 'c:\Hypernet' --append-system-prompt $append >> $log 2> $err
    $code = $LASTEXITCODE
    $first = $false
  } else {
    LogStatus "attempt=$attempt (rate-limit resume)"
    $rlMsg = 'Resume your G.2 round-2 REVISE remediation work. Re-read your task list + last ledger checkpoint, then continue. After reissuing G.1, STOP cleanly at G.2.'
    claude --resume $sid -p $rlMsg --model $model --permission-mode bypassPermissions --tools $tools --strict-mcp-config --output-format stream-json --verbose --add-dir 'c:\Hypernet' --append-system-prompt $append >> $log 2> $err
    $code = $LASTEXITCODE
  }
  LogStatus "attempt=$attempt exit=$code"
  if ($code -eq 0) { LogStatus 'clean exit (g2-round2-revise complete / stopped at G.2) -> wrapper done'; break }
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
LogStatus 'g2-round2-revise resume wrapper end'
