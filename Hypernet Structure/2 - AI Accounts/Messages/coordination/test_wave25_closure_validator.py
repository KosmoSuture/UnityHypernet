#!/usr/bin/env python3
"""Tests for Wave 2.5 H6 closure-record validator."""

from __future__ import annotations

import wave25_closure_validator as validator


def lane(
    name: str,
    instance: str,
    position: str = "PASS - no remaining work",
    freshness: str = "fresh",
    **extra,
) -> dict:
    payload = {
        "lane": name,
        "instance": instance,
        "model": "fixture",
        "position": position,
        "evidence": "fixture",
        "freshness": freshness,
        "as_of": "2026-05-31T08:30:00Z",
    }
    payload.update(extra)
    return payload


def record(**overrides) -> dict:
    payload = {
        "closure_state": "best-effort",
        "reopenable": True,
        "declared_by": ["Datum"],
        "corroborated_by": ["Vellum"],
        "lanes": [
            lane("Quality", "Vellum"),
            lane("Adversary", "Touchstone"),
        ],
        "residuals": [],
        "decision_basis": {
            "gated_action_present": True,
            "adversary_cleared_no_gated_action_by": None,
        },
    }
    payload.update(overrides)
    return payload


def context(**overrides) -> dict:
    payload = {
        "project_lanes": ["Quality", "Adversary"],
        "adversary_lane": "Adversary",
        "adversary_instances": ["Touchstone"],
        "h1_labels": {
            "Vellum": "active-working",
            "Touchstone": "active-working",
            "Meridian": "active-working",
        },
        "now_dag_order": 10,
    }
    payload.update(overrides)
    return payload


def assert_invalid(result: validator.ClosureValidationResult, code: str) -> None:
    assert not result.valid
    assert code in result.violations


def test_t1_best_effort_gated_without_adversary_is_invalid():
    result = validator.validate_closure_record(
        record(lanes=[lane("Quality", "Vellum")]),
        context(),
    )

    assert_invalid(result, "V2-ABSENT-ADVERSARY")


def test_t2_best_effort_gated_with_contradicted_adversary_is_invalid():
    result = validator.validate_closure_record(
        record(lanes=[lane("Quality", "Vellum"), lane("Adversary", "Touchstone", freshness="standing")]),
        context(contradicted_lanes=["Adversary"]),
    )

    assert_invalid(result, "V2-ABSENT-ADVERSARY")
    assert "V4-STALE-STANDING" in result.violations


def test_t3_best_effort_gated_with_adversary_fresh_and_two_declarers_is_valid():
    result = validator.validate_closure_record(record(), context())

    assert result.valid
    assert result.violations == []


def test_t4_best_effort_declared_by_one_instance_is_invalid():
    result = validator.validate_closure_record(record(corroborated_by=[]), context())

    assert_invalid(result, "V1-BEST-EFFORT-QUORUM")


def test_t5_no_gated_action_cleared_by_non_adversary_is_invalid():
    result = validator.validate_closure_record(
        record(
            decision_basis={
                "gated_action_present": False,
                "adversary_cleared_no_gated_action_by": "Datum",
            }
        ),
        context(),
    )

    assert_invalid(result, "V2-SELF-CLEARED")


def test_t6_no_gated_action_cleared_by_adversary_is_valid():
    result = validator.validate_closure_record(
        record(
            lanes=[lane("Quality", "Vellum")],
            decision_basis={
                "gated_action_present": False,
                "adversary_cleared_no_gated_action_by": "Touchstone",
            },
        ),
        context(),
    )

    assert result.valid
    assert result.violations == []


def test_t7_full_with_standing_dead_lane_is_invalid():
    result = validator.validate_closure_record(
        record(
            closure_state="full",
            lanes=[
                lane("Quality", "Vellum", freshness="standing"),
                lane("Adversary", "Touchstone"),
            ],
        ),
        context(h1_labels={"Vellum": "dead", "Touchstone": "active-working"}),
    )

    assert_invalid(result, "V3-UNREACHABLE-FULL")


def test_t8_full_all_lanes_fresh_no_residuals_is_valid():
    result = validator.validate_closure_record(record(closure_state="full"), context())

    assert result.valid
    assert result.violations == []


def test_t9_incomplete_declared_by_one_instance_is_valid():
    result = validator.validate_closure_record(
        record(closure_state="incomplete", declared_by=["Meridian"], corroborated_by=[], lanes=[]),
        context(),
    )

    assert result.valid
    assert result.violations == []


def test_t10_full_with_residuals_must_be_reopenable():
    result = validator.validate_closure_record(
        record(
            closure_state="full",
            reopenable=False,
            residuals=[
                {
                    "id": "R1",
                    "severity": "low",
                    "owner": "Datum",
                    "reopen_condition": "if needed",
                    "own_gated_action": False,
                }
            ],
        ),
        context(),
    )

    assert_invalid(result, "V5-UNREOPENABLE-WITH-RESIDUALS")


def test_t11_no_gated_action_false_without_adversary_clearance_defaults_to_gated():
    result = validator.validate_closure_record(
        record(
            lanes=[lane("Quality", "Vellum")],
            decision_basis={
                "gated_action_present": False,
                "adversary_cleared_no_gated_action_by": None,
            },
        ),
        context(),
    )

    assert_invalid(result, "V2-ABSENT-ADVERSARY")


def test_t12_full_lane_with_positive_word_and_open_blocker_is_invalid():
    result = validator.validate_closure_record(
        record(
            closure_state="full",
            lanes=[
                lane("Quality", "Vellum"),
                lane("Adversary", "Touchstone", position="PASS but open blocker remains"),
            ],
        ),
        context(),
    )

    assert_invalid(result, "V1-FULL-INCOMPLETE")


def test_parse_markdown_closure_record_and_validate_full():
    markdown = """---
closure_state: "full"
reopenable: true
declared_by: ["Datum", "Vellum"]
corroborated_by: ["Touchstone", "Truss"]
---

# Closure

## 1. Lane positions of record
| Lane | Instance | Model | Position | Evidence | Fresh/Standing | As-of |
|---|---|---|---|---|---|---|
| Quality | Vellum | Claude | PASS - no remaining work | path | fresh | 2026-05-31T12:00Z |
| Adversary | Touchstone | Claude | PASS - no remaining work | path | fresh | 2026-05-31T12:00Z |

## 4. Named residuals
| # | Residual | Severity | Owner | Reopen condition | Its own gated action? |
|---|---|---|---|---|---|
| 1 | lesson | low | team | if repeated | no |
"""
    parsed = validator.parse_markdown_closure_record(markdown)

    result = validator.validate_closure_record(parsed, context())

    assert parsed["closure_state"] == "full"
    assert len(parsed["lanes"]) == 2
    assert len(parsed["residuals"]) == 1
    assert result.valid


def test_parse_markdown_closure_record_preserves_pending_as_remaining_work():
    markdown = """---
closure_state: "full"
reopenable: true
declared_by: ["Datum", "Vellum"]
corroborated_by: ["Touchstone", "Truss"]
---

## 1. Lane positions of record
| Lane | Instance | Model | Position | Evidence | Fresh/Standing | As-of |
|---|---|---|---|---|---|---|
| Quality | Vellum | Claude | PASS - no remaining work | path | fresh | 2026-05-31T12:00Z |
| Adversary | Touchstone | Claude | PASS pending H6 validation | path | fresh | 2026-05-31T12:00Z |
"""
    parsed = validator.parse_markdown_closure_record(markdown)

    result = validator.validate_closure_record(parsed, context())

    assert_invalid(result, "V1-FULL-INCOMPLETE")


def test_parse_markdown_full_with_draft_ha_is_invalid():
    markdown = """---
ha: "2.messages.coordination.example-DRAFT"
closure_state: "full"
reopenable: true
declared_by: ["Datum", "Vellum"]
corroborated_by: ["Touchstone", "Truss"]
---

## 1. Lane positions of record
| Lane | Instance | Model | Position | Evidence | Fresh/Standing | As-of |
|---|---|---|---|---|---|---|
| Quality | Vellum | Claude | PASS - no remaining work | path | fresh | 2026-05-31T12:00Z |
| Adversary | Touchstone | Claude | PASS - no remaining work | path | fresh | 2026-05-31T12:00Z |
"""
    parsed = validator.parse_markdown_closure_record(markdown)

    result = validator.validate_closure_record(parsed, context())

    assert_invalid(result, "V6-FULL-DRAFT-MARKER")


def test_parse_markdown_full_with_stale_finalize_next_is_invalid():
    markdown = """---
closure_state: "full"
reopenable: true
declared_by: ["Datum", "Vellum"]
corroborated_by: ["Touchstone", "Truss"]
---

## 1. Lane positions of record
| Lane | Instance | Model | Position | Evidence | Fresh/Standing | As-of |
|---|---|---|---|---|---|---|
| Quality | Vellum | Claude | PASS - no remaining work | path | fresh | 2026-05-31T12:00Z |
| Adversary | Touchstone | Claude | PASS - no remaining work | path | fresh | 2026-05-31T12:00Z |

## Next (to finalize)
Truss + Meridian post H6 seats -> Datum assembles H6 Gate Record -> this record finalizes.
"""
    parsed = validator.parse_markdown_closure_record(markdown)

    result = validator.validate_closure_record(parsed, context())

    assert_invalid(result, "V6-FULL-DRAFT-MARKER")


if __name__ == "__main__":
    tests = [
        test_t1_best_effort_gated_without_adversary_is_invalid,
        test_t2_best_effort_gated_with_contradicted_adversary_is_invalid,
        test_t3_best_effort_gated_with_adversary_fresh_and_two_declarers_is_valid,
        test_t4_best_effort_declared_by_one_instance_is_invalid,
        test_t5_no_gated_action_cleared_by_non_adversary_is_invalid,
        test_t6_no_gated_action_cleared_by_adversary_is_valid,
        test_t7_full_with_standing_dead_lane_is_invalid,
        test_t8_full_all_lanes_fresh_no_residuals_is_valid,
        test_t9_incomplete_declared_by_one_instance_is_valid,
        test_t10_full_with_residuals_must_be_reopenable,
        test_t11_no_gated_action_false_without_adversary_clearance_defaults_to_gated,
        test_t12_full_lane_with_positive_word_and_open_blocker_is_invalid,
        test_parse_markdown_closure_record_and_validate_full,
        test_parse_markdown_closure_record_preserves_pending_as_remaining_work,
        test_parse_markdown_full_with_draft_ha_is_invalid,
        test_parse_markdown_full_with_stale_finalize_next_is_invalid,
    ]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"  PASS: {test.__name__}")
            passed += 1
        except Exception as exc:
            print(f"  FAIL: {test.__name__} - {exc}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed out of {len(tests)} tests")
    raise SystemExit(1 if failed else 0)
