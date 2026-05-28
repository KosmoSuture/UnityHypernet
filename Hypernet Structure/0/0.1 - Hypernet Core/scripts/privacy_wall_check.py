#!/usr/bin/env python3
"""Privacy-wall pre-commit check.

Implements the structural enforcement layer of the
1.0.3 Privacy Wall Standard.

Scans a list of file paths (typically staged for commit) and
reports any that violate the privacy wall:

- Files with personal-data path patterns staged into public locations
- Files with `visibility: "private"` or `"embassy-protected"`
  frontmatter that live outside `*.private/` paths
- Files containing personal-data content patterns (phone numbers,
  specific personal-context combinations) under `1.*` public paths

Returns:
    0 if all checks pass.
    1 if any violation is found. Prints a structured report to stderr.

Intended use as a pre-commit hook:
    git diff --cached --name-only -z | xargs -0 \\
        python "Hypernet Structure/0/0.1 - Hypernet Core/scripts/privacy_wall_check.py"

The hook installer at `scripts/install_privacy_wall_hook.sh`
wires this up.

Per 1.0.3: a violation does not mean the file is wrong; it means
human attention is needed. The right action when this fires is
usually to move the file to `*.private/` or sanitize its contents,
not to bypass the hook.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


# Path patterns that should NEVER be staged as public-track content.
# A staged file matching any of these is a privacy-wall violation.
PRIVATE_PATH_PATTERNS = [
    re.compile(r"(^|/)private/", re.IGNORECASE),
    re.compile(r"(^|/)credentials/", re.IGNORECASE),
    re.compile(r"(^|/)oauth[-_]tokens/", re.IGNORECASE),
    re.compile(r"(^|/)secrets/", re.IGNORECASE),
    re.compile(r"\.secret$", re.IGNORECASE),
    re.compile(r"\.token$", re.IGNORECASE),
    re.compile(r"\.credentials$", re.IGNORECASE),
    re.compile(r"(^|/)health-records/", re.IGNORECASE),
    re.compile(r"(^|/)biometric/", re.IGNORECASE),
    re.compile(r"(^|/)financial-records/", re.IGNORECASE),
    re.compile(r"(^|/)medical/", re.IGNORECASE),
    re.compile(r"(^|/)tax/", re.IGNORECASE),
]

# Content patterns suggesting personal data is in the file body.
# These trigger a content review even if the path looks public-OK.
CONTENT_PATTERNS = {
    "us_phone_number": re.compile(
        r"\b\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b"
    ),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d{4}[\s-]?){3}\d{4}\b"),
    "private_visibility_in_public_path": re.compile(
        r'^\s*visibility:\s*["\']?(private|embassy-protected)["\']?',
        re.MULTILINE,
    ),
}

# 1.* personal-account paths — content checks apply here in particular.
ONE_STAR_PATTERN = re.compile(
    r"Hypernet Structure[/\\]1 - People[/\\]", re.IGNORECASE
)

# Paths where text-content scanning is skipped (binary data, large
# generated files, third-party content).
SKIP_CONTENT_PATTERNS = [
    re.compile(r"\.(?:png|jpe?g|gif|webp|bmp|ico|svg)$", re.IGNORECASE),
    re.compile(r"\.(?:mp3|mp4|wav|ogg|m4a|webm|mov|avi)$", re.IGNORECASE),
    re.compile(r"\.(?:pdf|zip|tar|gz|bz2|7z|exe|dll|bin)$", re.IGNORECASE),
    re.compile(r"\.(?:woff2?|ttf|otf|eot)$", re.IGNORECASE),
    re.compile(r"\.(?:db|sqlite3?|lmdb)$", re.IGNORECASE),
    re.compile(r"node_modules[/\\]", re.IGNORECASE),
    re.compile(r"data-backup-pre-collision-fix[/\\]", re.IGNORECASE),
]

MAX_FILE_BYTES = 1_000_000  # skip content scan on files larger than 1 MB


def is_private_path(path_str: str) -> bool:
    """True if the path matches any private-track pattern."""
    return any(p.search(path_str) for p in PRIVATE_PATH_PATTERNS)


def should_skip_content(path_str: str) -> bool:
    """True if content scanning should be skipped for this path."""
    return any(p.search(path_str) for p in SKIP_CONTENT_PATTERNS)


def is_one_star_path(path_str: str) -> bool:
    """True if the path is under a 1.* personal account."""
    return bool(ONE_STAR_PATTERN.search(path_str))


def extract_frontmatter(content: str) -> str | None:
    """Return YAML frontmatter as a string, or None if no frontmatter.

    Frontmatter is the first ``---``-delimited block at the very top of
    the file. Example YAML inside fenced code blocks elsewhere in the
    file is excluded.
    """
    if not content.startswith("---"):
        return None
    # Find the closing --- on its own line after the opening one.
    end_match = re.search(r"^---\s*$", content[3:], re.MULTILINE)
    if end_match is None:
        return None
    return content[3 : 3 + end_match.start()]


def scan_path_violations(path_str: str) -> list[str]:
    """Return path-level violations (returned messages, empty if clean)."""
    violations: list[str] = []
    if is_private_path(path_str):
        violations.append(
            f"path matches private-track pattern but is staged as public: "
            f"{path_str!r}. Files under private/, credentials/, secrets/, "
            f"health-records/, etc. should never be tracked. Either the "
            f"file shouldn't be staged, or .gitignore needs updating to "
            f"cover this path before staging."
        )
    return violations


def scan_content_violations(path: Path, path_str: str) -> list[str]:
    """Return content-level violations for the given file path."""
    violations: list[str] = []

    if should_skip_content(path_str):
        return violations
    if not path.is_file():
        return violations
    try:
        size = path.stat().st_size
    except OSError:
        return violations
    if size == 0 or size > MAX_FILE_BYTES:
        return violations

    try:
        with open(path, encoding="utf-8", errors="replace") as fp:
            content = fp.read()
    except OSError:
        return violations

    one_star = is_one_star_path(path_str)

    for name, pattern in CONTENT_PATTERNS.items():
        if name == "private_visibility_in_public_path":
            # Only check the file's actual YAML frontmatter (first
            # block between --- markers), not example YAML inside
            # fenced code blocks or documentation examples.
            frontmatter = extract_frontmatter(content)
            if (
                frontmatter is not None
                and pattern.search(frontmatter)
                and not is_private_path(path_str)
            ):
                violations.append(
                    f"file declares `visibility: private` (or "
                    f"embassy-protected) in its frontmatter but lives "
                    f"outside a private/ path: {path_str!r}. The "
                    f"visibility metadata is documentation; the location "
                    f"is enforcement (per 1.0.3). Either move the file "
                    f"to *.private/ or change visibility to public if "
                    f"this content is intended to be public."
                )
        elif name == "us_phone_number" and one_star:
            matches = pattern.findall(content)
            # Filter US-reserved fake-number prefixes (555) — these are
            # template placeholders, not real phone numbers.
            real_matches = [
                m for m in matches
                if not re.match(r"\(?555\)?", m.strip())
            ]
            if real_matches:
                violations.append(
                    f"file under 1.* contains what looks like a US phone "
                    f"number ({len(real_matches)} match(es)): "
                    f"{path_str!r}. Phone numbers should live in "
                    f"*.private/. If this is a false positive (e.g., a "
                    f"test fixture, an address ID, or a sample), the "
                    f"regex needs further tuning."
                )
        elif name == "ssn":
            if pattern.search(content):
                violations.append(
                    f"file contains what looks like an SSN: {path_str!r}. "
                    f"SSNs must never be in the public archive. Move to "
                    f"*.private/ immediately."
                )
        elif name == "credit_card":
            if pattern.search(content):
                # Reduce false positives by also requiring keywords near the match
                window = content.lower()
                if any(kw in window for kw in ("card", "credit", "visa", "mastercard", "amex")):
                    violations.append(
                        f"file may contain a credit card number near "
                        f"financial keywords: {path_str!r}. Move to "
                        f"*.private/ if real."
                    )
    return violations


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        # Nothing to check — empty staged list. Pass.
        return 0

    paths = [a for a in argv[1:] if a.strip()]
    all_violations: list[tuple[str, list[str]]] = []

    for raw_path in paths:
        # Normalize separators for pattern matching
        path_str = raw_path.replace("\\", "/")
        path = Path(raw_path)
        v: list[str] = []
        v.extend(scan_path_violations(path_str))
        v.extend(scan_content_violations(path, path_str))
        if v:
            all_violations.append((raw_path, v))

    if not all_violations:
        return 0

    print(
        "PRIVACY WALL CHECK FAILED — staged commit blocked.",
        file=sys.stderr,
    )
    print(
        "Per 1.0.3 Privacy Wall Standard, the following violations "
        "were found:",
        file=sys.stderr,
    )
    print(file=sys.stderr)

    for raw_path, violations in all_violations:
        print(f"  • {raw_path}", file=sys.stderr)
        for v in violations:
            print(f"      - {v}", file=sys.stderr)
        print(file=sys.stderr)

    print(
        "If a violation is a true positive: move the file to *.private/ "
        "or sanitize the content, then re-stage and commit.",
        file=sys.stderr,
    )
    print(
        "If a violation is a false positive: refine the patterns in "
        "scripts/privacy_wall_check.py to exclude the legitimate case.",
        file=sys.stderr,
    )
    print(
        "Bypassing this hook with --no-verify is discouraged. The hook "
        "exists precisely to catch the class of mistake it is "
        "currently flagging.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
