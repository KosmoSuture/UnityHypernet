#!/usr/bin/env python3
"""Secret / credential content scanner.

Companion to privacy_wall_check.py. Scans a list of file paths for
high-confidence secret/credential signatures (API tokens, webhook URLs,
private keys, access keys) — the failure mode a pre-push gate must catch
(cf. the R-PUSH-1 webhook-token near-miss that the path/PII pre-commit
check did not cover).

Design goals:
- HIGH PRECISION over recall: only well-known token shapes, to avoid
  false positives that train people to bypass the gate.
- Placeholder-aware: synthetic samples (your_token_here, xxxx, <...>,
  REDACTED, ${ENV}, .env.example / *.template.* files) are NOT flagged.
- Self-exempt: this file and privacy_wall_check.py contain patterns by
  necessity and are skipped.

Usage (same calling convention as privacy_wall_check.py):
    <file-list> | xargs -0 python secret_scan.py
Returns 0 if clean, 1 if any candidate secret is found (report to stderr).
A finding is "candidate, not proof" — human review decides.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# High-confidence secret signatures. value-group (1) used for placeholder test
# where relevant.
SECRET_PATTERNS = {
    "github_pat":            re.compile(r"\bgh[posru]_[A-Za-z0-9]{36}\b"),
    "github_fine_grained":   re.compile(r"\bgithub_pat_[A-Za-z0-9_]{60,}\b"),
    "slack_token":           re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),
    "slack_webhook":         re.compile(r"https://hooks\.slack\.com/services/[A-Za-z0-9/_-]{20,}"),
    "discord_webhook":       re.compile(r"https://(?:canary\.|ptb\.)?discord(?:app)?\.com/api/webhooks/\d+/[\w-]{20,}"),
    "aws_access_key_id":     re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    "google_api_key":        re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b"),
    "stripe_live_key":       re.compile(r"\b(?:sk|rk)_live_[0-9A-Za-z]{20,}\b"),
    "private_key_block":     re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"),
    "jwt":                   re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{6,}\b"),
    "generic_assignment":    re.compile(
        r"""(?ix)\b(?:api[_-]?key|secret|access[_-]?token|auth[_-]?token|
            client[_-]?secret|passwd|password)\b\s*[:=]\s*["']([^"'\s]{16,})["']"""
    ),
}

# Substrings marking a matched value as a non-secret placeholder/example.
# Deliberately CONSERVATIVE: only strong template signals. Weak common
# substrings ("test", "sample", "fake", "abcdef", "foo") are intentionally
# EXCLUDED — they appear by chance in real high-entropy tokens and would cause
# false NEGATIVES (a missed real secret is far worse than a reviewed false
# positive, since findings are "candidate, not proof" and human-reviewed).
PLACEHOLDER_MARKERS = (
    "your_", "your-", "example", "placeholder", "change_me", "changeme",
    "redacted", "xxxx", "<", ">", "${", "{{", "...", "replace_me",
    "replaceme", "0000000000", "1234567890", "deadbeef",
)

# File paths that are intentionally templates/examples — skip entirely.
SKIP_PATH_PATTERNS = [
    re.compile(r"\.example(\.|$)", re.IGNORECASE),
    re.compile(r"\.sample(\.|$)", re.IGNORECASE),
    re.compile(r"\.template(\.|$)", re.IGNORECASE),
    re.compile(r"template\.[A-Za-z0-9]+$", re.IGNORECASE),
    re.compile(r"(^|/)secret_scan\.py$"),
    re.compile(r"(^|/)privacy_wall_check\.py$"),
    re.compile(r"\.(png|jpe?g|gif|webp|bmp|ico|svg|mp[34]|wav|pdf|zip|gz|7z|exe|dll|bin|woff2?|ttf|otf|db|sqlite3?)$", re.IGNORECASE),
    re.compile(r"node_modules/", re.IGNORECASE),
]
MAX_FILE_BYTES = 2_000_000


def _skip_path(p: str) -> bool:
    return any(rx.search(p) for rx in SKIP_PATH_PATTERNS)


def _is_placeholder(value: str) -> bool:
    low = value.lower()
    if any(m in low for m in PLACEHOLDER_MARKERS):
        return True
    # all-same-char or trivially low entropy
    if len(set(value)) <= 4:
        return True
    return False


def scan_file(path: Path, path_str: str) -> list[str]:
    if _skip_path(path_str) or not path.is_file():
        return []
    try:
        if path.stat().st_size == 0 or path.stat().st_size > MAX_FILE_BYTES:
            return []
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    hits: list[str] = []
    for name, rx in SECRET_PATTERNS.items():
        for m in rx.finditer(text):
            # the value to placeholder-test: capture group 1 if present else whole match
            value = m.group(1) if (m.groups() and m.group(1)) else m.group(0)
            if _is_placeholder(value):
                continue
            line_no = text.count("\n", 0, m.start()) + 1
            hits.append(f"{name} (line {line_no})")
    # de-dup
    return sorted(set(hits))


def main(argv: list[str]) -> int:
    paths = [a for a in argv[1:] if a.strip()]
    findings: list[tuple[str, list[str]]] = []
    for raw in paths:
        h = scan_file(Path(raw), raw.replace("\\", "/"))
        if h:
            findings.append((raw, h))

    if not findings:
        return 0

    print("SECRET SCAN: candidate secrets found (candidate, not proof — review before pushing):", file=sys.stderr)
    for raw, h in findings:
        print(f"  • {raw}", file=sys.stderr)
        for item in h:
            print(f"      - {item}", file=sys.stderr)
    print("\nIf real: remove + rotate the secret, move it to *.private/ or a gitignored secrets store.", file=sys.stderr)
    print("If a false positive: tune SECRET_PATTERNS / PLACEHOLDER_MARKERS in secret_scan.py.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
