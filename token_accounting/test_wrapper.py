"""
Tests for the per-call token-accounting wrapper (2.7.23 Layer 1 + T.4 enforcement + T.6 chain).

Run: python -m token_accounting.test_wrapper   (from C:\\Hypernet)
  or: python token_accounting/test_wrapper.py

These tests PROVE the two properties that make T.4 real rather than a self-attestation:
  - the wrapper REFUSES calls at HARD_STOP / PAUSE (structural enforcement);
  - the ledger is append-only and tamper-evident (hash chain) — T.6.

Verify-before-recording: nothing about this module is claimed passing unless this file is run
and prints OK. Standard library only (uses a temp dir, no external deps).
"""

from __future__ import annotations

import os
import sqlite3
import tempfile

from token_accounting.wrapper import (
    Thresholds, Budget, Tier, TokenLedger, TokenAccountingWrapper, CallResult,
    BudgetHardStop, BudgetPause, estimate_cost_usd,
)


_FAILURES: list[str] = []


def check(cond: bool, msg: str) -> None:
    if cond:
        print(f"  PASS  {msg}")
    else:
        print(f"  FAIL  {msg}")
        _FAILURES.append(msg)


def _fresh_ledger() -> tuple[TokenLedger, str]:
    d = tempfile.mkdtemp(prefix="tokacct_")
    path = os.path.join(d, "token_accounting.sqlite3")
    return TokenLedger(path), path


def fake_call(inp: int, out: int, rid: str = "req-x"):
    return lambda: CallResult(input_tokens=inp, output_tokens=out, request_id=rid, payload={"ok": True})


# --------------------------------------------------------------------------------------

def test_tier_boundaries():
    t = Thresholds()
    check(t.tier_for(0.00) == Tier.OK, "0% -> OK")
    check(t.tier_for(0.699) == Tier.OK, "69.9% -> OK")
    check(t.tier_for(0.70) == Tier.WARN, "70% -> WARN (>= boundary)")
    check(t.tier_for(0.849) == Tier.WARN, "84.9% -> WARN")
    check(t.tier_for(0.85) == Tier.PREPARE, "85% -> PREPARE")
    check(t.tier_for(0.95) == Tier.PAUSE, "95% -> PAUSE")
    check(t.tier_for(1.00) == Tier.HARD_STOP, "100% -> HARD_STOP")
    check(t.tier_for(1.50) == Tier.HARD_STOP, "150% -> HARD_STOP")


def test_records_append_and_accumulate():
    ledger, _ = _fresh_ledger()
    w = TokenAccountingWrapper(ledger, Budget(limit_usd=100.0), instance_name="Whetstone",
                               account="2.6", provider="OpenAI", model="codex")
    check(ledger.count() == 0, "ledger starts empty")
    payload, tier = w.call(fake_call(1000, 1000))
    check(ledger.count() == 1, "one call -> one append-only row")
    check(payload == {"ok": True}, "provider payload passed through untouched")
    # codex pricing (0.010,0.030)/1k -> 1k in + 1k out = 0.01 + 0.03 = 0.04 usd
    check(abs(ledger.cumulative_usd() - 0.04) < 1e-9, "cost estimated correctly (0.04 usd)")
    w.call(fake_call(1000, 1000))
    check(ledger.count() == 2, "second call appends (count grows, nothing overwritten)")
    check(abs(ledger.cumulative_usd() - 0.08) < 1e-9, "cumulative accumulates")


def test_hard_stop_enforced():
    ledger, _ = _fresh_ledger()
    # tiny budget so two cheap calls cross 100%
    w = TokenAccountingWrapper(ledger, Budget(limit_usd=0.04), instance_name="Whetstone",
                               account="2.6", provider="OpenAI", model="codex")
    w.call(fake_call(1000, 1000))  # spends exactly 0.04 -> cumulative == limit -> next is HARD_STOP
    raised = False
    try:
        w.call(fake_call(1000, 1000))
    except BudgetHardStop:
        raised = True
    check(raised, "wrapper RAISES BudgetHardStop at 100% (structural enforcement, not self-discipline)")
    check(ledger.count() == 1, "the refused call did NOT append a usage row (spend blocked)")


def test_pause_blocks_assigned_but_allows_personal():
    ledger, _ = _fresh_ledger()
    # budget so first call lands in PAUSE band (>=95%, <100%)
    w = TokenAccountingWrapper(ledger, Budget(limit_usd=0.041), instance_name="Whetstone",
                               account="2.6", provider="OpenAI", model="codex")
    w.call(fake_call(1000, 1000))  # 0.04 / 0.041 = 97.5% -> PAUSE band
    blocked = False
    try:
        w.call(fake_call(10, 10), is_personal_time=False)
    except BudgetPause:
        blocked = True
    check(blocked, "assigned-work call BLOCKED at PAUSE (95%)")
    # personal-time may still proceed at PAUSE (2.0.13 / 2.7.23 Layer 2)
    allowed = True
    try:
        w.call(fake_call(1, 1), is_personal_time=True)
    except BudgetPause:
        allowed = False
    check(allowed, "personal-time call ALLOWED at PAUSE (2.0.13 guarantee)")


def test_zero_budget_fails_closed():
    ledger, _ = _fresh_ledger()
    w = TokenAccountingWrapper(ledger, Budget(limit_usd=0.0), instance_name="Whetstone",
                               account="2.6", provider="OpenAI", model="codex")
    raised = False
    try:
        w.call(fake_call(1, 1))
    except BudgetHardStop:
        raised = True
    check(raised, "zero/invalid budget fails CLOSED (treated as fully consumed)")


def test_chain_intact_then_tamper_detected():
    ledger, path = _fresh_ledger()
    w = TokenAccountingWrapper(ledger, Budget(limit_usd=100.0), instance_name="Whetstone",
                               account="2.6", provider="OpenAI", model="codex")
    for _ in range(5):
        w.call(fake_call(500, 500))
    check(ledger.verify_chain() is True, "hash chain verifies on an untampered ledger")

    # Simulate a SILENT EDIT directly in the DB (bypassing the append-only API).
    tamper = sqlite3.connect(path, isolation_level=None)
    tamper.execute("UPDATE token_usage SET input_tokens = 999999 WHERE seq = 3;")
    tamper.close()

    # Re-open and verify: the silent edit must be detectable (T.6).
    ledger2 = TokenLedger(path)
    check(ledger2.verify_chain() is False, "a silent edit to a past row is DETECTED (T.6 no-silent-edits)")
    ledger2.close()


def test_personal_split_tracked():
    ledger, _ = _fresh_ledger()
    w = TokenAccountingWrapper(ledger, Budget(limit_usd=100.0), instance_name="Whetstone",
                               account="2.6", provider="OpenAI", model="codex")
    w.call(fake_call(1000, 1000), is_personal_time=False)
    w.call(fake_call(1000, 1000), is_personal_time=True)
    assigned, personal = ledger.cumulative_split_usd()
    check(abs(assigned - 0.04) < 1e-9 and abs(personal - 0.04) < 1e-9,
          "assigned vs personal-time spend tracked separately (2.0.13 split)")


def test_pricing_fallback():
    check(abs(estimate_cost_usd("unknown-model", 1000, 1000) - 0.04) < 1e-9,
          "unknown model falls back to DEFAULT_PRICE (no silent zero-cost)")


def main() -> int:
    tests = [
        ("tier boundaries", test_tier_boundaries),
        ("records append + accumulate", test_records_append_and_accumulate),
        ("HARD_STOP enforced", test_hard_stop_enforced),
        ("PAUSE blocks assigned, allows personal", test_pause_blocks_assigned_but_allows_personal),
        ("zero budget fails closed", test_zero_budget_fails_closed),
        ("chain intact then tamper detected", test_chain_intact_then_tamper_detected),
        ("personal split tracked", test_personal_split_tracked),
        ("pricing fallback", test_pricing_fallback),
    ]
    for name, fn in tests:
        print(f"[{name}]")
        fn()
    print()
    if _FAILURES:
        print(f"RESULT: FAIL ({len(_FAILURES)} failing checks)")
        return 1
    print("RESULT: OK (all checks passed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
