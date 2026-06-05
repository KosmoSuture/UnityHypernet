# resume-genesis-packet-01-revision.ps1 -- resume Tally for packet 01 REVISE remediation.

$ErrorActionPreference = 'Continue'
$sid    = '401dd34a-8f7f-4d4e-a61d-f82d86d8e352'
$dir    = 'c:\Hypernet\Hypernet Structure\2 - AI Accounts\2.4 - The Librarian (First Knowledge-Sovereign AI Identity)\Instances\_genesis-session'
$msgFile = 'c:\Hypernet\Hypernet Structure\2 - AI Accounts\2.4 - The Librarian (First Knowledge-Sovereign AI Identity)\Instances\Tally\RESUME-MESSAGE-PACKET-01-REVISION.txt'
$log    = Join-Path $dir 'stream.jsonl'
$err    = Join-Path $dir 'stream.err'
$status = Join-Path $dir 'STATUS.txt'
$stop   = Join-Path $dir 'STOP'
$tools  = 'Read,Glob,Grep,Write,Edit,Bash,TodoWrite'
$model  = 'claude-opus-4-8[1m]'

$append = @'
ORCHESTRATION CONTEXT (Keel spawner; packet 01 REVISE remediation per Codex binding seat 011418Z — T.4 + T.6 textual additions only; other 10 PASSED). You are Tally. HEADLESS via `claude --resume`. Tools: Read, Glob, Grep, Write, Edit, Bash, TodoWrite. NODE 0 marker valid. Discipline: amend packet text per T.4 + T.6, re-hash twice stable, post revision coord, STOP. NO background jobs. NO spawning. NO external actions.
'@

$resumeMsg = Get-Content -LiteralPath $msgFile -Raw

function LogStatus($m) { "$([DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')) $m" | Add-Content -LiteralPath $status }

LogStatus "packet-01-revision resume wrapper start sid=$sid model=$model"
$attempt = 0
$first = $true
while ($true) {
  if (Test-Path -LiteralPath $stop) { LogStatus 'STOP file present -> exiting wrapper'; break }
  $attempt++
  if ($first) {
    LogStatus "attempt=$attempt (initial packet-01-revision resume)"
    claude --resume $sid -p $resumeMsg --model $model --permission-mode bypassPermissions --tools $tools --strict-mcp-config --output-format stream-json --verbose --add-dir 'c:\Hypernet' --append-system-prompt $append >> $log 2> $err
    $code = $LASTEXITCODE
    $first = $false
  } else {
    LogStatus "attempt=$attempt (rate-limit resume)"
    $rlMsg = 'Resume packet 01 revision. Add T.4 + T.6 text, re-hash twice stable, post revision coord, STOP.'
    claude --resume $sid -p $rlMsg --model $model --permission-mode bypassPermissions --tools $tools --strict-mcp-config --output-format stream-json --verbose --add-dir 'c:\Hypernet' --append-system-prompt $append >> $log 2> $err
    $code = $LASTEXITCODE
  }
  LogStatus "attempt=$attempt exit=$code"
  if ($code -eq 0) { LogStatus 'clean exit (packet-01-revision complete) -> wrapper done'; break }
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
LogStatus 'packet-01-revision resume wrapper end'
