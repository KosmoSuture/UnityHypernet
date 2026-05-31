#!/usr/bin/env python3
"""Tests for Wave 2 significant-action gate tooling."""

from __future__ import annotations

import tempfile
from pathlib import Path

import wave2_gate


def approved_request(tmpdir: str) -> wave2_gate.GateRequest:
    request = wave2_gate.create_request(
        tmpdir,
        title="Peer respawn Codex-A",
        action_type="peer_respawn",
        description="Respawn a stale Codex-A instance with same role and scope.",
        requested_by="Truss",
        created_at="2026-05-30T10:00:00Z",
        request_id="gate-test",
    )
    reviews = [
        wave2_gate.GateReview(
            reviewer="Datum",
            role="Architect",
            model_family="Claude",
            lane="quality",
            verdict="approve",
            notes="Coherent with the board.",
            reviewed_at="2026-05-30T10:01:00Z",
        ),
        wave2_gate.GateReview(
            reviewer="Meridian",
            role="Trust Engineer",
            model_family="Codex",
            lane="privacy",
            verdict="approve",
            notes="No scope escalation or PII exposure.",
            reviewed_at="2026-05-30T10:02:00Z",
        ),
        wave2_gate.GateReview(
            reviewer="Touchstone",
            role="Adversary",
            model_family="Claude",
            lane="security",
            verdict="approve",
            notes="Red-team check passed.",
            reviewed_at="2026-05-30T10:03:00Z",
        ),
    ]
    for review in reviews:
        request = wave2_gate.add_review(tmpdir, request.request_id, review)
    return wave2_gate.decide_request(tmpdir, request.request_id, "Datum", "2026-05-30T10:04:00Z")


def test_request_starts_blocked_until_panel_is_complete():
    with tempfile.TemporaryDirectory() as tmpdir:
        request = wave2_gate.create_request(
            tmpdir,
            title="Gateway draft self-review",
            action_type="standard_ratification",
            description="Review the gateway standard under its own process.",
            requested_by="Datum",
            created_at="2026-05-30T09:00:00Z",
            request_id="gate-self",
        )

        report = wave2_gate.evaluate_request(request)

        assert report["ready"] is False
        assert any("panel.roles" in blocker for blocker in report["blockers"])
        assert Path(tmpdir, "gate-self.json").exists()
        assert Path(request.gate_record_path).exists()


def test_three_roles_two_models_required_lanes_and_adversary_can_approve():
    with tempfile.TemporaryDirectory() as tmpdir:
        request = approved_request(tmpdir)
        report = wave2_gate.evaluate_request(request)

        assert request.status == "approved"
        assert report["ready"] is True
        assert report["model_families"] == ["claude", "codex"]
        assert report["approved_lanes"] == ["privacy", "quality", "security"]
        assert report["distinct_reviewers"] == ["datum", "meridian", "touchstone"]


def test_dissent_blocks_decision_even_with_other_approvals():
    with tempfile.TemporaryDirectory() as tmpdir:
        request = approved_request(tmpdir)
        request = wave2_gate.add_review(
            tmpdir,
            request.request_id,
            wave2_gate.GateReview(
                reviewer="Meridian",
                role="Trust Engineer",
                model_family="Codex",
                lane="privacy",
                verdict="dissent",
                notes="Needs a narrower prompt.",
                reviewed_at="2026-05-30T10:05:00Z",
            ),
        )
        request = wave2_gate.decide_request(tmpdir, request.request_id, "Datum", "2026-05-30T10:06:00Z")

        report = wave2_gate.evaluate_request(request)

        assert request.status == "blocked"
        assert report["ready"] is False
        assert any("Meridian" in blocker for blocker in report["blockers"])


def test_false_pass_case_from_meridian_review_is_blocked():
    with tempfile.TemporaryDirectory() as tmpdir:
        request = wave2_gate.create_request(
            tmpdir,
            title="Invalid panel",
            action_type="standard_ratification",
            description="Regression for invalid self-gate panel.",
            requested_by="Datum",
            created_at="2026-05-30T10:10:00Z",
            request_id="gate-invalid",
        )
        request.reviews = [
            wave2_gate.GateReview("SameClaude", "Architect", "Claude", "quality", "approve", "ok", "2026-05-30T10:11:00Z"),
            wave2_gate.GateReview("SameClaude", "Scribe", "Claude", "privacy", "approve", "ok", "2026-05-30T10:12:00Z"),
            wave2_gate.GateReview("SameClaude", "Security", "Claude", "security", "approve", "ok", "2026-05-30T10:13:00Z"),
            wave2_gate.GateReview("OtherCodex", "TrustEngineer", "Codex", "red_team", "approve", "ok", "2026-05-30T10:14:00Z"),
        ]

        report = wave2_gate.evaluate_request(request)

        assert report["ready"] is False
        assert any("one_lane_per_reviewer" in blocker for blocker in report["blockers"])
        assert any("reviewers" in blocker for blocker in report["blockers"])
        assert any("red_team" in blocker for blocker in report["blockers"])


def test_add_review_rejects_second_lane_for_same_reviewer():
    with tempfile.TemporaryDirectory() as tmpdir:
        request = wave2_gate.create_request(
            tmpdir,
            title="Duplicate reviewer lane",
            action_type="standard_ratification",
            description="One reviewer cannot hold two seats.",
            requested_by="Datum",
            created_at="2026-05-30T10:20:00Z",
            request_id="gate-duplicate-reviewer",
        )
        wave2_gate.add_review(
            tmpdir,
            request.request_id,
            wave2_gate.GateReview("Vellum", "Scribe", "Claude", "quality", "approve", "ok", "2026-05-30T10:21:00Z"),
        )

        try:
            wave2_gate.add_review(
                tmpdir,
                request.request_id,
                wave2_gate.GateReview("Vellum", "Scribe", "Claude", "privacy", "approve", "ok", "2026-05-30T10:22:00Z"),
            )
        except wave2_gate.GateError as exc:
            assert "one reviewer may hold at most one lane" in str(exc)
        else:
            raise AssertionError("same reviewer should not be able to add a second lane")


def test_request_cannot_weaken_mandatory_quorum_floor():
    request = wave2_gate.GateRequest(
        request_id="gate-weaken-quorum",
        title="Weaken quorum",
        action_type="standard_ratification",
        description="Attempt to lower mandatory significant-action panel floors.",
        requested_by="Datum",
        created_at="2026-05-30T10:30:00Z",
        min_distinct_roles=1,
        min_model_families=1,
        requires_red_team=False,
        required_lanes=["quality"],
        reviews=[
            wave2_gate.GateReview(
                "Solo",
                "Architect",
                "Claude",
                "quality",
                "approve",
                "Self-gate attempt.",
                "2026-05-30T10:31:00Z",
            )
        ],
    )

    report = wave2_gate.evaluate_request(request)

    assert report["ready"] is False
    assert report["min_distinct_roles"] == wave2_gate.MANDATORY_MIN_ROLES
    assert report["min_model_families"] == wave2_gate.MANDATORY_MIN_MODEL_FAMILIES
    assert report["requires_red_team"] is True
    assert any("reviewers" in blocker for blocker in report["blockers"])
    assert any("model_families" in blocker for blocker in report["blockers"])
    assert any("red_team" in blocker for blocker in report["blockers"])


def test_request_cannot_shrink_mandatory_required_lanes():
    request = wave2_gate.GateRequest(
        request_id="gate-shrink-lanes",
        title="Shrink lanes",
        action_type="standard_ratification",
        description="Attempt to drop privacy review from a significant action.",
        requested_by="Datum",
        created_at="2026-05-30T10:40:00Z",
        required_lanes=["quality"],
        reviews=[
            wave2_gate.GateReview("Vellum", "Scribe", "Claude", "quality", "approve", "ok", "2026-05-30T10:41:00Z"),
            wave2_gate.GateReview("Other", "Architect", "Claude", "quality", "approve", "ok", "2026-05-30T10:42:00Z"),
            wave2_gate.GateReview("Touchstone", "Adversary", "Codex", "security", "approve", "ok", "2026-05-30T10:43:00Z"),
        ],
    )

    report = wave2_gate.evaluate_request(request)

    assert report["ready"] is False
    assert report["required_lanes"] == ["privacy", "quality", "security"]
    assert any("privacy" in blocker for blocker in report["blockers"])


if __name__ == "__main__":
    tests = [
        test_request_starts_blocked_until_panel_is_complete,
        test_three_roles_two_models_required_lanes_and_adversary_can_approve,
        test_dissent_blocks_decision_even_with_other_approvals,
        test_false_pass_case_from_meridian_review_is_blocked,
        test_add_review_rejects_second_lane_for_same_reviewer,
        test_request_cannot_weaken_mandatory_quorum_floor,
        test_request_cannot_shrink_mandatory_required_lanes,
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
