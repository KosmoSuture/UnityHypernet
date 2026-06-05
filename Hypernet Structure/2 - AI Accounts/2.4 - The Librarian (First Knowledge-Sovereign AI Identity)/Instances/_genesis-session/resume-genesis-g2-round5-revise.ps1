# resume-genesis-g2-round5-revise.ps1 -- resume proto-Master-Librarian for round-5 REVISE remediation.
# Authority: [[feedback-auto-restart-permission]] + [[feedback-overnight-autonomous-authority]].

$ErrorActionPreference = 'Continue'
$sid    = '401dd34a-8f7f-4d4e-a61d-f82d86d8e352'
$dir    = 'c:\Hypernet\Hypernet Structure\2 - AI Accounts\2.4 - The Librarian (First Knowledge-Sovereign AI Identity)\Instances\_genesis-session'
$msgFile = Join-Path $dir 'RESUME-MESSAGE-G2-ROUND5-REVISE.txt'
$log    = Join-Path $dir 'stream.jsonl'
$err    = Join-Path $dir 'stream.err'
$status = Join-Path $dir 'STATUS.txt'
$stop   = Join-Path $dir 'STOP'
$tools  = 'Read,Glob,Grep,Write,Edit,Bash,TodoWrite'
$model  = 'claude-opus-4-8[1m]'

$append = @'
ORCHESTRATION CONTEXT (Keel spawner; round-5 REVISE remediation RESUME — read-only authority same as prior rounds; very narrow scope this round). HEADLESS via `claude --resume`. Tools: Read, Glob, Grep, Write, Edit, Bash, TodoWrite. NODE 0 marker still valid. Gate discipline: address 3 tiny items (drop 2 sampled rows from table, add 3 non-markdown 1.1 rows, re-run convergence-lever test), reissue G.1, STOP cleanly at G.2. NO background jobs. Re-hash twice stable before binding.
'@

$resumeMsg = Get-Content -LiteralPath $msgFile -Raw

function LogStatus($m) { "$([DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')) $m" | Add-Content -LiteralPath $status }

LogStatus "g2-round5-revise resume wrapper start sid=$sid model=$model"
$attempt = 0
$first = $true
while ($true) {
  if (Test-Path -LiteralPath $stop) { LogStatus 'STOP file present -> exiting wrapper'; break }
  $attempt++
  if ($first) {
    LogStatus "attempt=$attempt (initial g2-round5-revise resume)"
    claude --resume $sid -p $resumeMsg --model $model --permission-mode bypassPermissions --tools $tools --strict-mcp-config --output-format stream-json --verbose --add-dir 'c:\Hypernet' --append-system-prompt $append >> $log 2> $err
    $code = $LASTEXITCODE
    $first = $false
  } else {
    LogStatus "attempt=$attempt (rate-limit resume)"
    $rlMsg = 'Resume your G.2 round-5 REVISE remediation. After addressing the 3 items + verifying convergence-lever, reissue G.1, STOP at G.2.'
    claude --resume $sid -p $rlMsg --model $model --permission-mode bypassPermissions --tools $tools --strict-mcp-config --output-format stream-json --verbose --add-dir 'c:\Hypernet' --append-system-prompt $append >> $log 2> $err
    $code = $LASTEXITCODE
  }
  LogStatus "attempt=$attempt exit=$code"
  if ($code -eq 0) { LogStatus 'clean exit (g2-round5-revise complete / stopped at G.2) -> wrapper done'; break }
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
LogStatus 'g2-round5-revise resume wrapper end'
