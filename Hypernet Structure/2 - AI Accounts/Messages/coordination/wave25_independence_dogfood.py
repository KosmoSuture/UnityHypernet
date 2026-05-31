#!/usr/bin/env python3
"""Wave 2.5 H4 §5.6 per-reviewer independence dogfood.

Touchstone (Verifier, 2.0.8.2) owns this as the enforcement teeth for rec-2 / RT-2.
It validates the `reviewers:` block of a Gate Record against the §5.6 invariants so a
gate whose seats cannot each be shown to be an independent review is mechanically
rejected — closing the "one runtime wearing several role labels" attack.

Pure function: no DB / network / filesystem. Mirrors the H6 closure validator shape.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any


# Tier -> minimum distinct model families required (H4 §4.7 table).
TIER_MODEL_FAMILY_FLOOR = {"a": 2, "b": 2, "c": 1}
REQUIRED_HUMAN_SEAT_DIMENSIONS = {"quality", "security"}  # privacy may be tool-evidence at Tier C (§4.7.3)
SESSION_REF_RE = re.compile(r"^(?:sha256:)?[0-9a-f]{64}$", re.IGNORECASE)


@dataclass
class IndependenceResult:
    valid: bool
    violations: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _cf(value: Any) -> str:
    return str(value or "").strip().casefold()


def _session_ref_digest(value: Any) -> str:
    """Return a normalized SHA-256 digest string, or empty if the reference is invalid."""
    raw = _cf(value)
    if not SESSION_REF_RE.fullmatch(raw):
        return ""
    return raw.removeprefix("sha256:")


# v0.5 (H4v05) additions — the enforcement teeth for §5.7/§5.8/§6.5.
# The pure core stays filesystem-free: the caller (main) resolves message authors
# and each reviewer's latest verdict-on-artifact, then passes them in as maps.
_DISPOSITION_RE = re.compile(r"^\s*(pass|block|revise)\b", re.IGNORECASE)
_ARTIFACT_ID_RE = re.compile(r"\b\d+(?:\.[a-z0-9]+){2,}", re.IGNORECASE)


def _disposition(verdict: Any) -> str:
    """Canonical leading disposition of a verdict string: PASS | BLOCK | REVISE | ''."""
    m = _DISPOSITION_RE.match(str(verdict or ""))
    return m.group(1).upper() if m else ""


def _identity_token(identity: Any) -> str:
    """First identity-like token, casefolded ('Touchstone (...)' -> 'touchstone').

    Bridges the repo's two identity spellings: a reviewer_identity short name
    ('Touchstone') vs a message's creator ('2.1.touchstone') / from ('Touchstone (...)').
    """
    for token in re.findall(r"[a-z][a-z0-9]*", _cf(identity)):
        return token
    return ""


def _identity_matches(reviewer_identity: Any, author_field: Any) -> bool:
    """True if the reviewer short-name is present in the resolved author field."""
    token = _identity_token(reviewer_identity)
    return bool(token) and token in _cf(author_field)


def _artifact_key(artifact_id: Any) -> str:
    """Stable comparison key for artifact IDs with optional descriptive suffixes."""
    raw = _cf(artifact_id)
    match = _ARTIFACT_ID_RE.search(raw)
    if match:
        return match.group(0)
    return re.sub(r"\s+", " ", raw)


def validate_independence(
    reviewers: list[dict[str, Any]],
    *,
    author_identity: str,
    quorum_tier: str,
    accepted_duplicate_sessions: bool = False,
    allow_pending_operator_locator: bool = False,
    ref_authors: dict[str, str] | None = None,
    latest_verdicts: dict[str, str] | None = None,
    proposer: str = "",
    record_author: str = "",
    executor: str = "",
    require_role_separation_fields: bool = False,
) -> IndependenceResult:
    """Assert the §5.6 invariants over a Gate Record's reviewers block.

    accepted_duplicate_sessions models invariant (v)'s narrow escape hatch: a
    duplicate session_ref_hash is allowed ONLY if explicitly explained and accepted
    by a higher-tier panel. Default False => duplicates are rejected.

    v0.5 (H4v05) checks are opt-in — they run only when the caller supplies the
    resolved data, so the pure core stays filesystem-free and the I0-I8 behaviour
    is unchanged when the new maps/identities are omitted:
      * ref_authors      {artifact_ref(casefolded): author_identity}  -> I9  (§5.7)
      * latest_verdicts  {reviewer_identity(casefolded): latest verdict on artifact} -> I10 (§6.5)
      * proposer/record_author/executor identities                    -> I11 (§5.8)
    """
    violations: list[str] = []
    tier = _cf(quorum_tier)
    author = _cf(author_identity)

    if not reviewers:
        return IndependenceResult(False, ["I0-NO-REVIEWERS"])

    identities = [_cf(r.get("reviewer_identity")) for r in reviewers]

    # (i) all reviewer_identity distinct across seats
    seen: set[str] = set()
    for ident in identities:
        if not ident:
            violations.append("I0-MISSING-IDENTITY")
        elif ident in seen:
            violations.append("I1-DUPLICATE-IDENTITY")  # one instance in two seats
        seen.add(ident)

    # (iii) no reviewer_identity == the author (recusal)
    if author and author in seen:
        violations.append("I3-AUTHOR-AS-REVIEWER")

    # (ii) model_family count across DISTINCT identities >= the tier floor
    family_by_identity: dict[str, str] = {}
    for r in reviewers:
        ident = _cf(r.get("reviewer_identity"))
        if ident:
            family_by_identity[ident] = _cf(r.get("model_family"))
    distinct_families = {f for f in family_by_identity.values() if f}
    floor = TIER_MODEL_FAMILY_FLOOR.get(tier, 2)
    if len(distinct_families) < floor:
        violations.append("I2-MODEL-FAMILY-FLOOR")  # e.g. one runtime faking 2 families

    # (iv) every seat verdict carries an authored_artifact_refs, and no two seats
    # rely on the same verdict artifact as their independence anchor.
    artifact_seen: set[str] = set()
    for r in reviewers:
        refs = r.get("authored_artifact_refs")
        if not (isinstance(refs, (list, tuple)) and any(_cf(x) for x in refs)):
            violations.append("I4-NO-ARTIFACT-REF")
            break
        for ref in refs:
            normalized_ref = _cf(ref)
            if not normalized_ref:
                continue
            if normalized_ref in artifact_seen:
                violations.append("I4-DUPLICATE-ARTIFACT-REF")
                break
            artifact_seen.add(normalized_ref)
        if "I4-DUPLICATE-ARTIFACT-REF" in violations:
            break

    # (v) duplicate session_ref_hash across two seats rejected unless explained+accepted.
    # §5.6 requires a SHA-256 hash, not an arbitrary non-empty locator label. The
    # pending marker is an explicit interim exception: it is honest "operator must
    # supply the true locator later" evidence, and is only useful when paired with
    # the distinct artifact-anchor check above.
    session_seen: set[str] = set()
    for r in reviewers:
        sh = _cf(r.get("session_ref_hash"))
        if not sh:
            violations.append("I5-NO-SESSION-REF")
            continue
        if sh == "pending-operator-locator":
            if not allow_pending_operator_locator:
                violations.append("I5-PENDING-SESSION-REF")
            continue
        digest = _session_ref_digest(sh)
        if not digest:
            violations.append("I5-INVALID-SESSION-REF")
            continue
        if digest in session_seen and not accepted_duplicate_sessions:
            violations.append("I5-DUPLICATE-SESSION")  # same session => not independent
        session_seen.add(digest)

    # Required human seats must be present and distinct (v0.3 §4.3 / H4 §4.7.3).
    dims = {_cf(r.get("seat_dimension")) for r in reviewers}
    if "quality" not in dims:
        violations.append("I6-NO-QUALITY-SEAT")
    if "security" not in dims:
        violations.append("I7-NO-ADVERSARY-SEAT")
    if tier != "c" and "privacy" not in dims:
        violations.append("I8-NO-PRIVACY-SEAT")

    # --- v0.5 §5.7: each seat's entry MUST trace to a message AUTHORED BY that reviewer ---
    # Closes the exact incident vector: the record-author hand-writing a seat's verdict and
    # anchoring it to a message the reviewer did not author. Opt-in: runs only when the
    # caller resolves ref->author (filesystem-free core).
    if ref_authors is not None:
        for r in reviewers:
            ident = r.get("reviewer_identity")
            if not ident:
                continue
            refs = [_cf(x) for x in (r.get("authored_artifact_refs") or []) if _cf(x)]
            self_authored_entry = _cf(r.get("self_authored_entry"))
            if self_authored_entry and self_authored_entry not in refs:
                refs.append(self_authored_entry)
            if not refs:
                continue  # absence already caught by I4-NO-ARTIFACT-REF
            # Every anchor used for a seat must resolve to that reviewer's own message.
            # A mixed set lets the record-author smuggle in non-self-authored evidence.
            if not all(_identity_matches(ident, ref_authors.get(ref, "")) for ref in refs):
                violations.append("I9-NOT-SELF-AUTHORED")  # record-author wrote a seat's entry
                break

    # --- v0.5 §6.5: the entry's verdict MUST match the reviewer's latest self-authored
    # verdict on the artifact; a recorded PASS while a BLOCK-of-record exists is void. ---
    if latest_verdicts is not None:
        for r in reviewers:
            ident = _identity_token(r.get("reviewer_identity"))
            if not ident or ident not in latest_verdicts:
                violations.append("I10-NO-SELF-VERDICT-METADATA")
                break
            latest = _disposition(latest_verdicts.get(ident))
            recorded = _disposition(r.get("verdict"))
            if not latest:
                continue
            # A live BLOCK that the record omits/contradicts is dispositive and void.
            if latest == "BLOCK" and recorded != "BLOCK":
                violations.append("I10-OMITTED-BLOCK")
                break
            if not recorded or latest != recorded:
                violations.append("I10-VERDICT-MISMATCH")  # entry disagrees with the reviewer
                break

    # --- v0.5 §5.8: no single instance may be proposer AND record-author AND/OR executor. ---
    role_holders = {
        "proposer": _identity_token(proposer),
        "record_author": _identity_token(record_author),
        "executor": _identity_token(executor),
    }
    if require_role_separation_fields and any(not who for who in role_holders.values()):
        violations.append("I11-MISSING-ROLE-FIELD")
    present = {role: who for role, who in role_holders.items() if who}
    if len(present) >= 2:
        # any two distinct roles held by the same identity is concentration
        values = list(present.values())
        if len(set(values)) < len(values):
            violations.append("I11-ROLE-CONCENTRATION")

    # de-dupe preserving order
    ordered, seen_v = [], set()
    for v in violations:
        if v not in seen_v:
            ordered.append(v)
            seen_v.add(v)
    return IndependenceResult(valid=not ordered, violations=ordered)


def frontmatter_text(markdown: str) -> str:
    normalized = markdown.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        return ""
    end = normalized.find("\n---", 4)
    return normalized[4:end] if end != -1 else ""


def _strip_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _parse_inline_list(value: str) -> list[str]:
    try:
        parsed = ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return [_strip_scalar(item) for item in value.strip("[]").split(",") if item.strip()]
    if isinstance(parsed, (list, tuple)):
        return [str(item) for item in parsed if str(item).strip()]
    return []


def extract_reviewers_from_markdown(markdown: str) -> list[dict[str, Any]]:
    """Extract a simple frontmatter `reviewers:` list for dogfood validation.

    The repo's lightweight frontmatter reader intentionally avoids a YAML
    dependency and flattens nested lists. Gate records need nested reviewer
    dictionaries, so this parser handles the constrained schema used by the
    Wave-2.5 records without accepting arbitrary YAML.
    """
    reviewers: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    pending_list_key = ""
    in_reviewers = False

    for raw_line in frontmatter_text(markdown).splitlines():
        line = raw_line.rstrip()
        if line.startswith("reviewers:"):
            in_reviewers = True
            continue
        if not in_reviewers:
            continue
        if line and not line.startswith(" "):
            break

        new_reviewer = re.match(r"\s{2}-\s+(\w+):\s*(.*)$", line)
        if new_reviewer:
            if current is not None:
                reviewers.append(current)
            current = {new_reviewer.group(1): _strip_scalar(new_reviewer.group(2))}
            pending_list_key = ""
            continue

        key_value = re.match(r"\s{4}(\w+):\s*(.*)$", line)
        if key_value and current is not None:
            key, value = key_value.group(1), key_value.group(2).strip()
            if value.startswith("["):
                current[key] = _parse_inline_list(value)
                pending_list_key = ""
            elif value:
                current[key] = _strip_scalar(value)
                pending_list_key = ""
            else:
                current[key] = []
                pending_list_key = key
            continue

        list_item = re.match(r"\s{6}-\s*(.*)$", line)
        if list_item and current is not None and pending_list_key:
            current.setdefault(pending_list_key, []).append(_strip_scalar(list_item.group(1)))

    if current is not None:
        reviewers.append(current)
    return reviewers


def fm_scalar(markdown: str, key: str) -> str:
    """Read a single top-level frontmatter scalar (quotes stripped); '' if absent."""
    pattern = re.compile(rf"^{re.escape(key)}:\s*(.*)$", re.MULTILINE)
    m = pattern.search(frontmatter_text(markdown))
    return _strip_scalar(m.group(1)) if m else ""


def _resolve_ref_path(ref: str, coordination_dir: Path) -> Path | None:
    """Map an authored_artifact_ref to a file on disk, tolerating repo-relative paths."""
    candidates = [Path(ref), coordination_dir / Path(ref).name]
    parent = coordination_dir.parent
    candidates.append(parent / ref)  # e.g. ref is 'Messages/coordination/..' under board root
    for cand in candidates:
        try:
            if cand.is_file():
                return cand
        except OSError:
            continue
    return None


def resolve_ref_authors(reviewers: list[dict[str, Any]], coordination_dir: Path) -> dict[str, str]:
    """{ref(casefolded): author identity} by reading each referenced message's creator/from."""
    authors: dict[str, str] = {}
    for r in reviewers:
        refs = list(r.get("authored_artifact_refs") or [])
        self_authored_entry = r.get("self_authored_entry")
        if _cf(self_authored_entry):
            refs.append(self_authored_entry)
        for ref in refs:
            key = _cf(ref)
            if not key or key in authors:
                continue
            path = _resolve_ref_path(str(ref), coordination_dir)
            if path is None:
                authors[key] = ""  # dangling anchor -> cannot establish self-authorship
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            authors[key] = fm_scalar(text, "creator") or fm_scalar(text, "from")
    return authors


def resolve_latest_verdicts(artifact_id: str, coordination_dir: Path) -> dict[str, str]:
    """{reviewer(token): latest self-authored verdict} over messages whose
    `verdicts_artifact` references this artifact. Latest by sorted filename (UTC stamp prefix).
    """
    target = _artifact_key(artifact_id)
    if not target:
        return {}
    by_author: dict[str, tuple[str, str]] = {}  # token -> (filename, verdict)
    for path in sorted(coordination_dir.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        declared = _artifact_key(fm_scalar(text, "verdicts_artifact"))
        if not declared or declared != target:
            continue
        verdict = fm_scalar(text, "verdict")
        if not verdict:
            continue
        token = _identity_token(fm_scalar(text, "from") or fm_scalar(text, "creator"))
        if not token:
            continue
        prior = by_author.get(token)
        if prior is None or path.name > prior[0]:
            by_author[token] = (path.name, verdict)
    return {token: verdict for token, (_, verdict) in by_author.items()}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a Gate Record reviewers block against §5.6/§5.7/§5.8/§6.5.")
    parser.add_argument("--gate-record", required=True)
    parser.add_argument("--author-identity", required=True)
    parser.add_argument("--quorum-tier", default="B")
    parser.add_argument("--allow-pending-operator-locator", action="store_true")
    parser.add_argument("--accepted-duplicate-sessions", action="store_true")
    # v0.5 (H4v05) provenance + role-separation checks (opt-in).
    parser.add_argument("--check-self-authored", action="store_true",
                        help="§5.7: each seat must trace to a message authored by that reviewer (I9)")
    parser.add_argument("--check-verdict-match", metavar="ARTIFACT_ID",
                        help="§6.5: cross-check each entry against the reviewer's latest verdict on ARTIFACT_ID (I10)")
    parser.add_argument("--check-role-separation", action="store_true",
                        help="§5.8: proposer/record-author/executor must be distinct (I11)")
    parser.add_argument("--coordination-dir",
                        help="dir holding reviewer messages (default: the gate record's own dir)")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    gate_path = Path(args.gate_record)
    markdown = gate_path.read_text(encoding="utf-8")
    reviewers = extract_reviewers_from_markdown(markdown)
    coordination_dir = Path(args.coordination_dir) if args.coordination_dir else gate_path.parent

    ref_authors = resolve_ref_authors(reviewers, coordination_dir) if args.check_self_authored else None
    latest_verdicts = (
        resolve_latest_verdicts(args.check_verdict_match, coordination_dir)
        if args.check_verdict_match else None
    )
    proposer = record_author = executor = ""
    if args.check_role_separation:
        proposer = fm_scalar(markdown, "proposer")
        record_author = fm_scalar(markdown, "record_author") or fm_scalar(markdown, "creator")
        executor = fm_scalar(markdown, "executor")

    result = validate_independence(
        reviewers,
        author_identity=args.author_identity,
        quorum_tier=args.quorum_tier,
        accepted_duplicate_sessions=args.accepted_duplicate_sessions,
        allow_pending_operator_locator=args.allow_pending_operator_locator,
        ref_authors=ref_authors,
        latest_verdicts=latest_verdicts,
        proposer=proposer,
        record_author=record_author,
        executor=executor,
        require_role_separation_fields=args.check_role_separation,
    )
    payload = {"valid": result.valid, "violations": result.violations, "reviewer_count": len(reviewers)}
    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        verdict = "PASS" if result.valid else "FAIL"
        print(f"{verdict}: reviewers={len(reviewers)} violations={result.violations}")
    return 0 if result.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
