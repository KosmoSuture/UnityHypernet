"""Collaboration scenarios — assert on AND red-team Truss's board tooling (#3 / #10).

These run today against ``wave1_board.py`` (the board parser) and
``wave1_work_packages.py`` (the work-package validator + conflict detector). They use
*fixture* boards written to a temp dir — never the live ``2.7.13`` — so they are
deterministic and do not depend on the board's constantly-changing state.

The positive scenarios prove the parser's Part A obligations (2.7.13.4): enumerate every
roster row, flag a stale lock, flag a registry/file desync, raise a file collision when
two WPs claim one path, and guard against a "completed" WP with no acceptance (the
green-but-fake guard). The one intentionally-red scenario surfaces a fair coverage gap:
matrix item 4 (roster status contradicts BOARD STATUS) is not yet implemented by the
parser. That FAIL carries an actionable finding and will go green when Truss adds the
detector — "a red test against a real contract is honest progress."
"""

from __future__ import annotations

from pathlib import Path

from .. import _paths  # noqa: F401
from ..scenario import Context, Pending, Scenario

import wave1_board
import wave1_work_packages

NOW = "2026-05-28T08:00:00Z"

_DEFAULT_STATUS = (
    "> **CURRENT PHASE:** Fixture phase.\n"
    "> **WHAT'S HAPPENING NOW:** Fixture testing of the parser.\n"
    "> **NEXT ACTION (Datum):** none.\n"
    "> **HUMAN GATE:** none."
)
_DEFAULT_HANDOFF = "- **2026-05-28T07:00Z — Datum → all** — fixture handoff entry.\n"


def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    sep = "|" + "|".join(["---"] * len(headers)) + "|"
    if not rows:
        rows = [["—"] * len(headers)]
    body = "\n".join("| " + " | ".join(r) + " |" for r in rows)
    return "\n".join([head, sep, body])


def _board_text(
    roster: list[list[str]],
    contracts: list[list[str]],
    locks: list[list[str]],
    status: str = _DEFAULT_STATUS,
    handoff: str = _DEFAULT_HANDOFF,
) -> str:
    return (
        '---\n'
        'ha: "2.7.13.fixture"\n'
        'object_type: "coordination_board"\n'
        'created: "2026-05-28"\n'
        '---\n\n'
        "# Fixture Coordination Board\n\n"
        "## BOARD STATUS — READ THIS FIRST\n\n"
        f"{status}\n\n"
        "## Instance Roster\n\n"
        f"{_md_table(['Slot', 'Chosen Name', 'Role', 'Current Task', 'Blocked-On', 'Last Handoff', 'Updated'], roster)}\n\n"
        "## Interface-Contract Registry\n\n"
        f"{_md_table(['Contract', 'Address', 'Owner', 'Consumed By', 'Version', 'Status'], contracts)}\n\n"
        "## Active Edit Locks\n\n"
        f"{_md_table(['Name', 'File / Address', 'Claimed (UTC-ish)', 'Note'], locks)}\n\n"
        "## Handoff Log\n\n"
        f"{handoff}\n"
        "---\n"
    )


def _write_board(ctx: Context, text: str) -> Path:
    path = ctx.workdir / "board.md"
    path.write_text(text, encoding="utf-8")
    return path


def _fresh_roster(n: int) -> list[list[str]]:
    return [
        [f"Slot-{i}", f"Name{i}", "Role", "Working", "—", "handoff", "2026-05-28T07:58Z"]
        for i in range(n)
    ]


# --- positive scenarios (prove Part A behaviors) -----------------------------

def parser_enumerates_roster(ctx: Context) -> None:
    path = _write_board(ctx, _board_text(_fresh_roster(3), [], []))
    board = wave1_board.parse_board(path)
    ctx.expect(
        len(board.roster) == 3,
        finding_id="vf-collab-roster-count",
        target="Messages/coordination/wave1_board.py parse_board (roster enumeration)",
        claim_tested="The parser enumerates every (non-placeholder) roster row",
        expected="len(board.roster) == 3",
        observed=f"len(board.roster) == {len(board.roster)}",
        severity="high",
        why_it_matters=(
            "If the board parser silently drops a roster row, an instance's status "
            "becomes invisible to coordination — a dropped row is a dropped person."
        ),
        repro="python -m verifier.run collaboration::parser_enumerates_roster",
        would_unblock="Ensure table parsing keeps every content row and only filters all-empty rows.",
    )


def parser_enumerates_contracts(ctx: Context) -> None:
    contracts = [
        ["C1", "9.9.1", "Datum", "Codex-A", "v1", "drafting"],
        ["C2", "9.9.2", "Datum", "Codex-B", "v1", "published"],
        ["C3", "9.9.3", "Datum", "Codex-B", "v1", "drafting"],
        ["C4", "9.9.4", "Datum", "Claude-C", "v1", "published"],
    ]
    path = _write_board(ctx, _board_text(_fresh_roster(1), contracts, []))
    board = wave1_board.parse_board(path)
    ctx.expect(
        len(board.contracts) == 4,
        finding_id="vf-collab-contract-count",
        target="Messages/coordination/wave1_board.py parse_board (contract registry)",
        claim_tested="The parser enumerates every contract-registry row",
        expected="len(board.contracts) == 4",
        observed=f"len(board.contracts) == {len(board.contracts)}",
        severity="medium",
        why_it_matters="A dropped contract row hides a blocked-on dependency from the team.",
        repro="python -m verifier.run collaboration::parser_enumerates_contracts",
        would_unblock="Parse the registry table with the same fidelity as the roster table.",
    )


def stale_lock_flagged(ctx: Context) -> None:
    locks = [["Ghost", "some/file.py", "2026-05-27T00:00:00Z", "abandoned long ago"]]
    path = _write_board(ctx, _board_text(_fresh_roster(1), [], locks))
    board = wave1_board.parse_board(path)
    findings = wave1_board.collect_findings(
        board, contracts_dir=ctx.workdir, now=wave1_board.parse_now(NOW)
    )
    ctx.expect(
        any(f.kind == "stale_lock" for f in findings),
        finding_id="vf-collab-stale-lock",
        target="Messages/coordination/wave1_board.py collect_findings (stale_lock)",
        claim_tested="An edit lock older than the staleness threshold is flagged",
        expected="a finding with kind == 'stale_lock' exists",
        observed=f"finding kinds = {[f.kind for f in findings]}",
        severity="high",
        why_it_matters=(
            "A stale lock that is never flagged silently freezes a shared file — the exact "
            "deadlock the lock protocol exists to prevent."
        ),
        repro="python -m verifier.run collaboration::stale_lock_flagged",
        would_unblock="Compare claimed_at against now and flag locks past the threshold.",
    )


def registry_file_desync_flagged(ctx: Context) -> None:
    contracts = [["C1", "9.9.1", "Datum", "Codex-A", "v1", "drafting"]]
    path = _write_board(ctx, _board_text(_fresh_roster(1), contracts, []))
    # A fixture contract file whose frontmatter status disagrees with the registry row.
    cdir = ctx.workdir / "contracts"
    cdir.mkdir()
    (cdir / "c1.md").write_text(
        '---\nha: "9.9.1"\nstatus: "published-v1"\n---\n# C1\n', encoding="utf-8"
    )
    board = wave1_board.parse_board(path)
    findings = wave1_board.collect_findings(board, contracts_dir=cdir, now=wave1_board.parse_now(NOW))
    ctx.expect(
        any(f.kind == "desync" for f in findings),
        finding_id="vf-collab-registry-desync",
        target="Messages/coordination/wave1_board.py collect_findings (registry/file desync)",
        claim_tested="A registry status that disagrees with the contract file's status is flagged",
        expected="a finding with kind == 'desync' exists",
        observed=f"finding kinds = {[f.kind for f in findings]}",
        severity="high",
        why_it_matters=(
            "The whole point of the registry is to tell engineers a contract is safe to "
            "build against. If it can lie about a published contract (or vice versa), the "
            "interface-first discipline breaks — this is the live desync the team hit on day one."
        ),
        repro="python -m verifier.run collaboration::registry_file_desync_flagged",
        would_unblock="Cross-check each registry row's status against the contract file frontmatter.",
    )


def wp_file_collision_flagged(ctx: Context) -> None:
    base = {
        "title": "t", "description": "d", "project": "#3", "owner": "Truss",
        "status": "in_progress", "phase": "build", "blocked_on": [],
        "acceptance": ["does X"], "evidence": [], "created_by": "Truss",
        "created_at": "2026-05-28T00:00:00Z",
    }
    wp_a = {**base, "wp_id": "wp-a", "files_owned": ["pkg/mod.py"]}
    wp_b = {**base, "wp_id": "wp-b", "files_owned": ["pkg/mod.py"]}
    issues = wave1_work_packages.detect_work_package_conflicts([wp_a, wp_b])
    ctx.expect(
        any(i.field == "files_owned" and i.severity == "error" for i in issues),
        finding_id="vf-collab-wp-collision",
        target="Messages/coordination/wave1_work_packages.py detect_work_package_conflicts",
        claim_tested="Two work packages claiming the same owned path raise a file collision",
        expected="an error issue on field 'files_owned' exists",
        observed=f"issues = {[(i.field, i.severity) for i in issues]}",
        severity="high",
        why_it_matters=(
            "Two instances owning the same file is the precise collision the substrate "
            "exists to prevent (retro 2.7.14). It must be caught before work starts, not after."
        ),
        repro="python -m verifier.run collaboration::wp_file_collision_flagged",
        would_unblock="Compare files_owned across all WPs and raise on any overlap.",
    )


def completed_wp_without_acceptance_flagged(ctx: Context) -> None:
    """Matrix item 5 / green-but-fake guard: a 'completed' WP with no acceptance/evidence."""
    wp = {
        "wp_id": "wp-x", "title": "t", "description": "d", "project": "#6",
        "owner": "Touchstone", "status": "completed", "phase": "done",
        "blocked_on": [], "files_owned": [], "acceptance": [], "evidence": [],
        "created_by": "Touchstone", "created_at": "2026-05-28T00:00:00Z",
    }
    issues = wave1_work_packages.validate_work_package(wp)
    fields = {i.field for i in issues if i.severity == "error"}
    ctx.expect(
        "acceptance" in fields and "evidence" in fields,
        finding_id="vf-collab-fake-green-wp",
        target="Messages/coordination/wave1_work_packages.py validate_work_package (completed WP)",
        claim_tested="A 'completed' WP with empty acceptance AND empty evidence is rejected",
        expected="error issues on both 'acceptance' and 'evidence'",
        observed=f"error fields = {sorted(fields)}",
        severity="high",
        why_it_matters=(
            "A WP marked 'completed' with nothing to prove it is the canonical fake-green: "
            "status theater with no evidence. Rejecting it is this whole experiment's thesis in code."
        ),
        repro="python -m verifier.run collaboration::completed_wp_without_acceptance_flagged",
        would_unblock="Require non-empty acceptance always, and evidence whenever status == 'completed'.",
    )


def lock_conflict_detected_on_prose_cells(ctx: Context) -> None:
    """RED-TEAM (verified defect): two locks on the SAME file must raise lock_conflict,
    even when the lock cells carry the usual descriptive note after the path.

    Every real edit-lock cell on the live board is prose — a path/address plus a note
    (e.g. ``wave1_board.py — fixing parser``) and sometimes several paths separated by
    ``;``. ``overlaps_path_or_address`` compares the whole cleaned cell, so two locks on
    the same file with different notes do NOT match. Verified directly: the detector
    returns False for the two prose cells below but True for the bare addresses. Net
    effect: lock_conflict is effectively inert against the board's actual lock format —
    the exact two-instances-on-one-file contention the lock protocol exists to catch
    (and the contention Touchstone and Truss actually hit on day one) slips through.

    This is a built-but-broken behavior, so it is a FAIL (not a PENDING). It will flip to
    PASS the moment the detector splits a lock cell into its component paths/addresses.
    """
    locks = [
        ["Truss", "wave1_board.py — adding detector", "2026-05-28T07:59Z", "n1"],
        ["Touchstone", "wave1_board.py — fixing parser", "2026-05-28T07:59Z", "n2"],
    ]
    path = _write_board(ctx, _board_text(_fresh_roster(1), [], locks))
    board = wave1_board.parse_board(path)
    findings = wave1_board.collect_findings(board, contracts_dir=ctx.workdir, now=wave1_board.parse_now(NOW))
    ctx.expect(
        any(f.kind == "lock_conflict" for f in findings),
        finding_id="vf-collab-lock-prose",
        target="Messages/coordination/wave1_board.py overlaps_path_or_address / collect_findings",
        claim_tested="Two edit locks on the same file (path + note) raise a lock_conflict",
        expected="a finding with kind == 'lock_conflict' exists",
        observed=f"no lock_conflict; kinds present = {sorted({f.kind for f in findings})}",
        severity="medium",
        why_it_matters=(
            "The lock-conflict detector is the structural guard against two instances "
            "editing one shared file. Because real lock cells always include a note (or "
            "multiple ';'-separated paths), the whole-cell comparison never matches, so "
            "the guard silently passes on genuine contention — fake-green on the precise "
            "failure mode the lock protocol exists to prevent."
        ),
        repro="python -m verifier.run collaboration::lock_conflict_detected_on_prose_cells",
        would_unblock=(
            "Before comparing, split each lock cell on ';' and strip the trailing note "
            "(after '—'/'-'), then extract the path/address token from each part and "
            "compare those tokens — not the raw prose cell."
        ),
    )


# --- red-team scenario (intentional, fair gap) -------------------------------

def roster_status_vs_board_status_desync(ctx: Context) -> None:
    """Matrix item 4 (2.7.13.4 Part B): roster status contradicting BOARD STATUS is flagged.

    I verified the parser currently emits no finding for a constructed contradiction
    (BOARD STATUS says 'every engineer is blocked' while a roster row shows an engineer
    actively building, blocked_on '—'). This is a *not-yet-built, non-Part-A capability*,
    so it is an honest PENDING rather than a FAIL: it would be unfair to hard-fail Truss's
    acknowledged incremental slice over an optional detector the Part A obligations do not
    require. The gap is tracked as a low-severity recommendation in the parser red-team
    findings and routed to Truss via 2.7.13. If the team later makes roster/BOARD-STATUS
    cross-checking a Part A obligation, this flips from PENDING to a real assertion.
    """
    status = (
        "> **CURRENT PHASE:** Blocked phase.\n"
        "> **WHAT'S HAPPENING NOW:** Every engineer is blocked on a contract and waiting.\n"
        "> **NEXT ACTION (Datum):** publish contracts.\n"
        "> **HUMAN GATE:** none."
    )
    roster = [
        ["Codex-A", "Truss", "Engineer", "Actively building the parser", "—", "h", "2026-05-28T07:58Z"],
    ]
    path = _write_board(ctx, _board_text(roster, [], [], status=status))
    board = wave1_board.parse_board(path)
    findings = wave1_board.collect_findings(board, contracts_dir=ctx.workdir, now=wave1_board.parse_now(NOW))
    flagged = any(
        ("board status" in f.message.lower() and "roster" in f.message.lower())
        or f.kind in {"roster_board_status_desync", "status_contradiction"}
        for f in findings
    )
    if flagged:
        return  # detector exists now — capability landed, scenario passes
    raise Pending(
        "Parser has no roster-vs-BOARD-STATUS cross-check detector yet (matrix item 4, "
        "Part B; NOT a Part A obligation). Verified: collect_findings emits 0 findings for "
        "a clear contradiction. Tracked as recommendation REC-collab-01 to Truss. Honest "
        "not-yet-built capability, not a pass and not a hard fail."
    )


SCENARIOS = [
    Scenario("collaboration", "parser_enumerates_roster", parser_enumerates_roster,
             "Parser enumerates every roster row."),
    Scenario("collaboration", "parser_enumerates_contracts", parser_enumerates_contracts,
             "Parser enumerates every contract row."),
    Scenario("collaboration", "stale_lock_flagged", stale_lock_flagged,
             "A stale edit lock is flagged."),
    Scenario("collaboration", "registry_file_desync_flagged", registry_file_desync_flagged,
             "Registry/contract-file status desync is flagged."),
    Scenario("collaboration", "wp_file_collision_flagged", wp_file_collision_flagged,
             "Two WPs claiming one path raise a collision."),
    Scenario("collaboration", "completed_wp_without_acceptance_flagged", completed_wp_without_acceptance_flagged,
             "A completed WP with no acceptance/evidence is rejected (fake-green guard)."),
    Scenario("collaboration", "lock_conflict_detected_on_prose_cells", lock_conflict_detected_on_prose_cells,
             "RED (verified defect): two locks on one file with notes are not flagged."),
    Scenario("collaboration", "roster_status_vs_board_status_desync", roster_status_vs_board_status_desync,
             "RED (gap): roster-vs-BOARD-STATUS desync not yet detected (matrix item 4)."),
]
