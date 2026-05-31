"""Dogfood the Trust Ledger on the team's OWN claims (mandate pt 3; contract 2.7.13.4 Part D).

This is the loop closing: point Meridian's `audit_claim` (#1) at this team's real
artifacts — contract files, the live `2.7.13` board, the harness's own findings record —
and report what the trust tooling says about the trust team.

Unlike `run.py`'s scenarios, this is an *on-demand audit of live, changing state*, not a
deterministic test: it asserts nothing and reports whatever is true at run time. If the
registry desync is later synced, the contradiction claim below will flip to verified — and
that is correct, not a regression.

Run:  ``python -m verifier.dogfood``   (from "0.1 - Hypernet Core")
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from . import _paths

_CONTRACT_4 = _paths.SHARED_UNDERSTANDING_DIR / "2.7.13.4 - Contract - Verification Harness Interface.md"
_FINDINGS = Path(__file__).resolve().parent / "FINDINGS.md"
_LEDGER_SRC = _paths.CORE_DIR / "hypernet" / "trust_ledger.py"
_BOARD = _paths.BOARD_PATH
# Wave-2 governance artifacts (the trust team auditing its own Wave-2 output).
_GATEWAY_STD = _paths.ACCOUNTS_DIR / "2.0 - AI Governance & Framework" / "2.0.26 - AI Significant-Action Gateway Standard.md"
_BOARD_W2 = _paths.SHARED_UNDERSTANDING_DIR / "2.7.13.W2 - Execution Wave 2 Coordination & Status.md"


def _claims():
    """Curated claims about the team's own output. (address, statement, locator, match_text).

    Match on STABLE content (frontmatter, code symbols, status strings) rather than
    formatted board table rows — a lesson learned the hard way: exact-row match_text
    against the live `2.7.13` board went stale within minutes as the board evolved. The
    point of dogfooding is to audit truth, not to be brittle about layout.
    """
    return [
        # A true 'status' claim about a contract file -> should verify. (Refreshed to the
        # current point release published-v1.1; the old 'published-v1' fixture went stale.)
        ("0.7.91.1", "Contract 2.7.13.4 file declares status published-v1.1",
         str(_CONTRACT_4), 'status: "published-v1.1"'),
        # A FALSE status claim about the same file -> should surface as contradicted.
        ("0.7.91.2", "Contract 2.7.13.4 file declares status drafting (false)",
         str(_CONTRACT_4), 'status: "drafting"'),
        # The board's stable frontmatter ha -> should verify.
        ("0.7.91.3", "The 2.7.13 board declares ha 2.7.13 in its frontmatter",
         str(_BOARD), 'ha: "2.7.13"'),
        # verifier/FINDINGS.md now records real open Wave-2 findings -> should verify
        # (refreshed from the Wave-1 'no open findings' fixture, which my own red-team
        # findings correctly invalidated — honest state, not a regression).
        ("0.7.91.4", "verifier/FINDINGS.md records the open rollup-significance finding",
         str(_FINDINGS), "vf-w2rollup-significance-trusted"),
        # #1's own module defines the audited interface -> should verify.
        ("0.7.91.5", "The Trust Ledger module defines audit_claim",
         str(_LEDGER_SRC), "def audit_claim"),
        # A source that does not resolve -> auditor must NOT fake-verify it.
        ("0.7.91.6", "A claim whose source file does not exist",
         str(_paths.CORE_DIR / "this_file_does_not_exist.md"), "anything"),
        # --- Wave-2 governance artifacts (trust team auditing its own Wave-2 output) ---
        # The Gateway Standard's stable ha -> should verify.
        ("0.7.91.7", "The 2.0.26 Gateway Standard declares ha 2.0.26",
         str(_GATEWAY_STD), 'ha: "2.0.26"'),
        # The standard was RATIFIED 2026-05-31 (legitimate self-gate: 3 roles + independent
        # Adversary red-team + 2 model families, author recused, PLUS Matt's §9.4 founding
        # grant — which I, the red-team seat, confirmed DIRECTLY with Matt, closing the one
        # fact the archive alone could not prove). So 'status: active' is now legitimately
        # true and the ratification is recorded.
        ("0.7.91.8", "The 2.0.26 Gateway Standard declares it was ratified 2026-05-31",
         str(_GATEWAY_STD), 'ratified: "2026-05-31"'),
        # HONESTY CHECK: now that it is ratified, it must NOT still claim it is a pre-gate
        # draft — a 'draft-awaiting-self-gate' status claim is contradicted by the active file.
        ("0.7.91.10", "The 2.0.26 Gateway Standard still declares status draft-awaiting-self-gate (false)",
         str(_GATEWAY_STD), 'status: "draft-awaiting-self-gate"'),
        # The Wave-2 board's stable frontmatter ha -> should verify.
        ("0.7.91.9", "The 2.7.13.W2 board declares ha 2.7.13.W2 in its frontmatter",
         str(_BOARD_W2), 'ha: "2.7.13.W2"'),
    ]


def run() -> int:
    try:
        from hypernet.trust_ledger import TrustLedger
        from hypernet.store import Store
    except Exception as exc:  # pragma: no cover - #1 absent
        print(f"Trust Ledger (#1) not importable, cannot dogfood: {exc}")
        return 2

    workdir = Path(tempfile.mkdtemp(prefix="verifier_dogfood_"))
    ledger = TrustLedger(Store(str(workdir / "store")), archive_root="/")

    print("\n=== Dogfood: Trust Ledger auditing the team's own artifacts ===\n")
    results = {}
    for addr, statement, locator, match_text in _claims():
        ledger.create_claim(
            addr, statement, "2.1.touchstone",
            [{"locator": locator, "locator_type": "file", "match_text": match_text}],
        )
        result = ledger.audit_claim(addr)
        results[addr] = result.new_status
        print(f"[{result.new_status:>12}] {statement}")
        print(f"               source: {locator}")
        print(f"               note:   {result.note}")

    print("\n--- What the trust tooling says about the trust team ---")
    expected = {
        "0.7.91.1": "verified",       # true status claim (published-v1.1)
        "0.7.91.2": "contradicted",   # false status claim is caught
        "0.7.91.3": "verified",       # stable board frontmatter
        "0.7.91.4": "verified",       # findings record carries the open Wave-2 finding
        "0.7.91.5": "verified",       # #1 exposes its interface
        "0.7.91.6": "unverified",     # missing source is NOT fake-verified
        "0.7.91.7": "verified",       # Gateway Standard ha
        "0.7.91.8": "verified",       # standard records its legitimate ratification (2026-05-31)
        "0.7.91.9": "verified",       # Wave-2 board ha
        "0.7.91.10": "contradicted",  # no longer a pre-gate draft (honesty: active status is real)
    }
    surprises = {a: (results.get(a), exp) for a, exp in expected.items() if results.get(a) != exp}
    if not surprises:
        print(
            "Loop closed: the Trust Ledger (#1), pointed at the team's own artifacts, "
            "verifies true status claims, contradicts a false one, and refuses to "
            "fake-verify a missing source. The trust tooling can verify the trust team."
        )
    else:
        print(
            "Live state differs from the baseline expectation (this is an audit of changing "
            f"artifacts, not a test — differences are information, not failures): {surprises}"
        )
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
