"""Meta-tests for the verification harness itself.

The Verifier's harness must be held to the standard it enforces on everyone else. These
tests prove the framework's own load-bearing properties — above all, that a PENDING
scenario can NEVER be counted as a pass (the anti-fake-green invariant), that a FAIL
always carries an actionable Finding, and that an ERROR (a harness bug) breaks ``ok``.

Run:  ``python -m verifier.test_verifier``   (from the "0.1 - Hypernet Core" directory)

Stdlib only, in the idiom of ``test_hypernet.py``.
"""

from __future__ import annotations

from .finding import Finding
from .scenario import Context, Outcome, Pending, RunSummary, Scenario, run_scenario, run_scenarios
from .scenarios import all_scenarios, select


# --- synthetic scenario bodies ----------------------------------------------

def _passing(ctx: Context) -> None:
    pass


def _failing(ctx: Context) -> None:
    ctx.expect(
        False,
        finding_id="t-fail-1",
        target="synthetic",
        claim_tested="a deliberately false assertion",
        expected="True",
        observed="False",
        severity="high",
        why_it_matters="proves FAIL produces a finding",
        repro="python -m verifier.test_verifier",
        would_unblock="n/a (synthetic)",
    )


def _pending(ctx: Context) -> None:
    raise Pending("synthetic subsystem not available")


def _erroring(ctx: Context) -> None:
    raise RuntimeError("synthetic harness bug")


# --- tests -------------------------------------------------------------------

def test_pass():
    print("  PASS scenario -> Outcome.PASS...")
    result = run_scenario(Scenario("meta", "pass", _passing))
    assert result.outcome is Outcome.PASS, result.outcome
    assert result.finding is None
    print("    PASS")


def test_fail_carries_finding():
    print("  FAIL scenario -> Outcome.FAIL + Finding...")
    result = run_scenario(Scenario("meta", "fail", _failing))
    assert result.outcome is Outcome.FAIL, result.outcome
    assert result.finding is not None, "a FAIL must carry a Finding"
    assert result.finding.finding_id == "t-fail-1"
    assert result.finding.would_unblock, "a finding must say what would unblock it"
    print("    PASS")


def test_pending_is_not_a_pass():
    """The anti-fake-green invariant: PENDING is never counted as a pass."""
    print("  PENDING scenario is NOT a pass...")
    result = run_scenario(Scenario("meta", "pending", _pending))
    assert result.outcome is Outcome.PENDING, result.outcome
    assert result.finding is None
    summary = RunSummary([result])
    assert summary.passed == 0, "pending must not increment passed"
    assert summary.pending == 1
    assert summary.ok is True, "pending alone must not break ok (honest not-yet-testable)"
    print("    PASS")


def test_error_breaks_ok():
    print("  ERROR scenario -> Outcome.ERROR and breaks ok...")
    result = run_scenario(Scenario("meta", "error", _erroring))
    assert result.outcome is Outcome.ERROR, result.outcome
    assert result.error_trace, "an ERROR must capture a traceback for debugging"
    summary = RunSummary([result])
    assert summary.errored == 1
    assert summary.ok is False, "an ERROR (harness bug) must break ok"
    print("    PASS")


def test_summary_ok_semantics():
    """ok is False iff there is any FAIL or ERROR; PASS+PENDING is ok."""
    print("  Summary ok semantics...")
    summary = run_scenarios([
        Scenario("meta", "p", _passing),
        Scenario("meta", "pend", _pending),
    ])
    assert summary.passed == 1 and summary.pending == 1 and summary.failed == 0
    assert summary.ok is True

    summary2 = run_scenarios([
        Scenario("meta", "p", _passing),
        Scenario("meta", "f", _failing),
        Scenario("meta", "pend", _pending),
    ])
    assert summary2.passed == 1 and summary2.failed == 1 and summary2.pending == 1
    assert summary2.ok is False, "any FAIL must break ok"
    assert len(summary2.findings) == 1, "findings collects exactly the FAIL's finding"
    print("    PASS")


def test_finding_rejects_bad_severity_and_status():
    print("  Finding rejects bad severity/status...")
    for bad in (
        dict(severity="critical"),  # not in SEVERITIES
        dict(status="resolved"),    # not in STATUSES
    ):
        kwargs = dict(
            finding_id="t", target="t", claim_tested="c", expected="e", observed="o",
            severity="high", why_it_matters="w", repro="r", would_unblock="u",
        )
        kwargs.update(bad)
        try:
            Finding(**kwargs)
        except ValueError:
            continue
        raise AssertionError(f"Finding should have rejected {bad}")
    print("    PASS")


def test_determinism():
    print("  Same scenario, same outcome (determinism)...")
    s = Scenario("meta", "pend", _pending)
    first = run_scenario(s).outcome
    second = run_scenario(s).outcome
    assert first is second is Outcome.PENDING
    print("    PASS")


def test_registry_selectors_unique():
    print("  Every registered scenario has a unique selector...")
    scenarios = all_scenarios()
    assert scenarios, "registry must not be empty"
    selectors = [s.selector for s in scenarios]
    assert len(selectors) == len(set(selectors)), "duplicate selector(s) registered"
    # select() round-trips
    one = select(["boot_portability::tamper_detected"])
    assert len(one) == 1 and one[0].name == "tamper_detected"
    subsystem = select(["trust_ledger"])
    assert len(subsystem) == 5, len(subsystem)
    print("    PASS")


def test_finding_node_projection():
    """A finding projects into a claim-shaped Node.data (the seam for #1 dogfooding)."""
    print("  Finding -> node_data projection...")
    f = Finding(
        finding_id="t-node", target="2.7.13.2 audit_claim", claim_tested="c",
        expected="e", observed="o", severity="medium", why_it_matters="w",
        repro="python -m verifier.run x::y", would_unblock="u",
    )
    data = f.to_node_data()
    assert data["finding_id"] == "t-node"
    assert "statement" in data and data["source_refs"], data
    print("    PASS")


def main():
    print("\n=== Verifier Harness Meta-Tests ===\n")
    tests = [
        ("PASS outcome", test_pass),
        ("FAIL carries finding", test_fail_carries_finding),
        ("PENDING is not a pass", test_pending_is_not_a_pass),
        ("ERROR breaks ok", test_error_breaks_ok),
        ("Summary ok semantics", test_summary_ok_semantics),
        ("Finding validates fields", test_finding_rejects_bad_severity_and_status),
        ("Determinism", test_determinism),
        ("Registry selectors unique", test_registry_selectors_unique),
        ("Finding node projection", test_finding_node_projection),
    ]
    passed = failed = 0
    for name, fn in tests:
        print(f"[{name}]")
        try:
            fn()
            passed += 1
        except Exception as exc:
            print(f"    FAIL: {exc}")
            import traceback
            traceback.print_exc()
            failed += 1
    print(f"\n=== Results: {passed} passed, {failed} failed ===\n")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
