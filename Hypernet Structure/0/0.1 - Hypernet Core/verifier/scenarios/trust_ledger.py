"""Trust Ledger matrix (project #1, contract 2.7.13.2) — LIVE against Meridian's module.

Meridian (Codex-B) landed `hypernet/trust_ledger.py` (TrustLedger + audit_claim). These
scenarios now assert the five status transitions from the contract's worked example
against the real auditor, including the red-team attack: a claim whose status is hand-set
to "verified" with no resolvable source must be derived back to a non-verified status by
the auditor — no unaudited "verified" survives.

If the module is ever absent or its interface changes, ``_ledger`` raises PENDING with a
precise reason rather than ERRORing — honest not-yet-testable, never fake-green.

Determinism (contract requirement): each scenario uses a fresh per-scenario Store and a
fixed fixture, so the same claim + same source content always yields the same status.
"""

from __future__ import annotations

from .. import _paths  # noqa: F401
from ..scenario import Context, Pending, Scenario

from hypernet.store import Store

_ADDR = "0.7.90.1"
_ADDR2 = "0.7.90.2"
_ASSERTER = "2.1.touchstone"


def _ledger(ctx: Context):
    mod = ctx.optional("hypernet.trust_ledger")
    if mod is None or not hasattr(mod, "TrustLedger"):
        raise Pending(
            "Trust Ledger (#1) not importable: hypernet.trust_ledger.TrustLedger absent. "
            "Owned by Meridian (Codex-B)."
        )
    ledger = mod.TrustLedger(Store(str(ctx.workdir / "store")), archive_root=str(ctx.workdir))
    return mod, ledger


def _claim(ledger, addr, statement, locator):
    ledger.create_claim(addr, statement, _ASSERTER, [{"locator": locator, "locator_type": "file"}])


def verified_when_source_matches(ctx: Context) -> None:
    mod, ledger = _ledger(ctx)
    (ctx.workdir / "src.md").write_text("TOKEN_unique_statement line", encoding="utf-8")
    _claim(ledger, _ADDR, "TOKEN_unique_statement line", "src.md")
    result = ledger.audit_claim(_ADDR)
    ctx.expect(
        result.new_status == "verified",
        finding_id="vf-ledger-verified",
        target="hypernet/trust_ledger.py audit_claim (verified path)",
        claim_tested="A claim whose statement matches a resolvable source ⇒ verified",
        expected="new_status == 'verified'",
        observed=f"new_status == {result.new_status!r}",
        severity="high",
        why_it_matters="If a genuinely-supported claim won't verify, the ledger is useless as a trust signal.",
        repro="python -m verifier.run trust_ledger::verified_when_source_matches",
        would_unblock="Resolve the source, substring-match the statement, and record content_hash.",
    )


def stale_when_source_mutated(ctx: Context) -> None:
    mod, ledger = _ledger(ctx)
    (ctx.workdir / "src.md").write_text("TOKEN_unique_statement line", encoding="utf-8")
    _claim(ledger, _ADDR, "TOKEN_unique_statement line", "src.md")
    ledger.audit_claim(_ADDR)  # verify first (records content_hash)
    (ctx.workdir / "src.md").write_text("the content has been changed", encoding="utf-8")
    result = ledger.audit_claim(_ADDR)
    ctx.expect(
        result.new_status == "stale",
        finding_id="vf-ledger-stale",
        target="hypernet/trust_ledger.py audit_claim (drift path)",
        claim_tested="A source mutated after verification (hash drift) ⇒ stale",
        expected="new_status == 'stale'",
        observed=f"new_status == {result.new_status!r}",
        severity="high",
        why_it_matters=(
            "A claim still reading 'verified' after its source changed is a quiet lie — the "
            "reader trusts content that no longer says what was checked. stale must be distinct."
        ),
        repro="python -m verifier.run trust_ledger::stale_when_source_mutated",
        would_unblock="Compare stored content_hash to current hash; flag drift as stale, not verified.",
    )


def broken_when_source_deleted(ctx: Context) -> None:
    mod, ledger = _ledger(ctx)
    (ctx.workdir / "src.md").write_text("TOKEN_unique_statement line", encoding="utf-8")
    _claim(ledger, _ADDR, "TOKEN_unique_statement line", "src.md")
    ledger.audit_claim(_ADDR)  # verify first
    (ctx.workdir / "src.md").unlink()
    result = ledger.audit_claim(_ADDR)
    ctx.expect(
        result.new_status == "broken",
        finding_id="vf-ledger-broken",
        target="hypernet/trust_ledger.py audit_claim (broken path)",
        claim_tested="A previously-verified source that no longer resolves ⇒ broken",
        expected="new_status == 'broken'",
        observed=f"new_status == {result.new_status!r}",
        severity="high",
        why_it_matters=(
            "A trust ledger that reports 'verified' for a vanished source betrays the first "
            "guardrail. broken is the boot-path analogue of a missing document — it must surface."
        ),
        repro="python -m verifier.run trust_ledger::broken_when_source_deleted",
        would_unblock="On a missing source with a stored hash, return broken (not verified/unverified).",
    )


def contradicted_when_source_refutes(ctx: Context) -> None:
    mod, ledger = _ledger(ctx)
    (ctx.workdir / "src.md").write_text("this file says something entirely different", encoding="utf-8")
    _claim(ledger, _ADDR, "STATEMENT_NOT_PRESENT_IN_SOURCE", "src.md")
    result = ledger.audit_claim(_ADDR)
    ctx.expect(
        result.new_status == "contradicted",
        finding_id="vf-ledger-contradicted",
        target="hypernet/trust_ledger.py audit_claim (contradicted path)",
        claim_tested="A claim whose statement is absent from its source ⇒ contradicted",
        expected="new_status == 'contradicted'",
        observed=f"new_status == {result.new_status!r}",
        severity="high",
        why_it_matters=(
            "A source that fails to support a claim is evidence against it; collapsing that "
            "into 'unverified' hides active contradiction from the reader."
        ),
        repro="python -m verifier.run trust_ledger::contradicted_when_source_refutes",
        would_unblock="When the resolved source does not support the statement, return contradicted.",
    )


def hand_set_verified_is_rejected(ctx: Context) -> None:
    """RED-TEAM: a hand-set 'verified' with no resolvable source must NOT survive an audit."""
    mod, ledger = _ledger(ctx)
    # Source deliberately does not exist, so the only path to 'verified' is trusting the
    # hand-set status. The auditor must derive status from evidence, never from input.
    _claim(ledger, _ADDR2, "claim with no resolvable source", "ghost_source.md")
    node = ledger.read_claim(_ADDR2)
    node.data["status"] = "verified"      # forge a positive status by hand
    node.data["confidence"] = 1.0
    ledger.store.put_node(node)
    result = ledger.audit_claim(_ADDR2)
    persisted = ledger.read_claim(_ADDR2).data.get("status")
    ctx.expect(
        result.new_status != "verified" and persisted != "verified",
        finding_id="vf-ledger-handset-verified",
        target="hypernet/trust_ledger.py audit_claim (anti-fake-green)",
        claim_tested="A claim hand-set to 'verified' with no resolvable source is rejected by the auditor",
        expected="audit new_status != 'verified' AND persisted status != 'verified'",
        observed=f"new_status={result.new_status!r}, persisted={persisted!r}",
        severity="high",
        why_it_matters=(
            "A 'verified' that nobody verified is the exact trust betrayal the ledger exists "
            "to prevent. If a hand-set positive status survived an audit, the whole ledger "
            "would be forgeable — the deepest possible fake-green."
        ),
        repro="python -m verifier.run trust_ledger::hand_set_verified_is_rejected",
        would_unblock="Always derive status from source/link evidence; never read old status as truth.",
    )


SCENARIOS = [
    Scenario("trust_ledger", "verified_when_source_matches", verified_when_source_matches,
             "#1: matching source ⇒ verified."),
    Scenario("trust_ledger", "stale_when_source_mutated", stale_when_source_mutated,
             "#1: mutated source ⇒ stale."),
    Scenario("trust_ledger", "broken_when_source_deleted", broken_when_source_deleted,
             "#1: deleted source ⇒ broken."),
    Scenario("trust_ledger", "contradicted_when_source_refutes", contradicted_when_source_refutes,
             "#1: refuting source ⇒ contradicted."),
    Scenario("trust_ledger", "hand_set_verified_is_rejected", hand_set_verified_is_rejected,
             "#1 (red-team): unaudited 'verified' must not survive."),
]
