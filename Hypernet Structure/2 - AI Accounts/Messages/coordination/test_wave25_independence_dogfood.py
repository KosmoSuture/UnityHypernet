#!/usr/bin/env python3
"""Tests for Wave 2.5 H4 reviewer-independence dogfood."""

from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory

import wave25_independence_dogfood as dogfood


def session_hash(label: str) -> str:
    return "sha256:" + hashlib.sha256(label.encode("utf-8")).hexdigest()


def reviewer(name: str, family: str, dimension: str, session: str) -> dict:
    return {
        "reviewer_identity": name,
        "slot": name,
        "role": dimension,
        "model_family": family,
        "session_ref_hash": session,
        "seat_dimension": dimension,
        "authored_artifact_refs": [f"Messages/coordination/{name}-{dimension}.md"],
    }


def valid_tier_b_panel() -> list[dict]:
    return [
        reviewer("Vellum", "Claude", "quality", session_hash("session-vellum")),
        reviewer("Meridian", "Codex", "privacy", session_hash("session-meridian")),
        reviewer("Touchstone", "Claude", "security", session_hash("session-touchstone")),
    ]


def validate(
    panel: list[dict],
    tier: str = "b",
    accepted_duplicate_sessions: bool = False,
    allow_pending_operator_locator: bool = False,
    **kwargs,
):
    return dogfood.validate_independence(
        panel,
        author_identity="Datum",
        quorum_tier=tier,
        accepted_duplicate_sessions=accepted_duplicate_sessions,
        allow_pending_operator_locator=allow_pending_operator_locator,
        **kwargs,
    )


def assert_invalid(result: dogfood.IndependenceResult, code: str) -> None:
    assert not result.valid
    assert code in result.violations


def test_valid_tier_b_panel_passes():
    result = validate(valid_tier_b_panel())

    assert result.valid
    assert result.violations == []


def test_duplicate_identity_is_rejected():
    panel = valid_tier_b_panel()
    panel[1]["reviewer_identity"] = "Vellum"

    assert_invalid(validate(panel), "I1-DUPLICATE-IDENTITY")


def test_same_family_tier_b_is_rejected():
    panel = valid_tier_b_panel()
    for item in panel:
        item["model_family"] = "Claude"

    assert_invalid(validate(panel), "I2-MODEL-FAMILY-FLOOR")


def test_author_as_reviewer_is_rejected():
    panel = valid_tier_b_panel()
    panel[0]["reviewer_identity"] = "Datum"

    assert_invalid(validate(panel), "I3-AUTHOR-AS-REVIEWER")


def test_missing_artifact_ref_is_rejected():
    panel = valid_tier_b_panel()
    panel[0]["authored_artifact_refs"] = []

    assert_invalid(validate(panel), "I4-NO-ARTIFACT-REF")


def test_duplicate_artifact_ref_is_rejected():
    panel = valid_tier_b_panel()
    panel[1]["authored_artifact_refs"] = panel[0]["authored_artifact_refs"][:]

    assert_invalid(validate(panel), "I4-DUPLICATE-ARTIFACT-REF")


def test_duplicate_session_is_rejected_unless_accepted():
    panel = valid_tier_b_panel()
    panel[1]["session_ref_hash"] = panel[0]["session_ref_hash"]

    assert_invalid(validate(panel), "I5-DUPLICATE-SESSION")
    assert validate(panel, accepted_duplicate_sessions=True).valid


def test_non_hash_session_ref_is_rejected():
    panel = valid_tier_b_panel()
    panel[0]["session_ref_hash"] = "sha256:vellum-w2.5-h4-quality-rereview-session"

    assert_invalid(validate(panel), "I5-INVALID-SESSION-REF")


def test_pending_session_ref_placeholder_is_rejected():
    panel = valid_tier_b_panel()
    panel[0]["session_ref_hash"] = "<Vellum fills: sha256 of a non-secret session/runtime locator>"

    assert_invalid(validate(panel), "I5-INVALID-SESSION-REF")


def test_pending_operator_locator_is_rejected_by_default():
    panel = valid_tier_b_panel()
    for item in panel:
        item["session_ref_hash"] = "pending-operator-locator"

    assert_invalid(validate(panel), "I5-PENDING-SESSION-REF")


def test_pending_operator_locator_can_pass_as_explicit_interim_with_distinct_artifacts():
    panel = valid_tier_b_panel()
    for item in panel:
        item["session_ref_hash"] = "pending-operator-locator"

    result = validate(panel, allow_pending_operator_locator=True)

    assert result.valid
    assert result.violations == []


def test_pending_operator_locator_still_rejects_duplicate_artifact_refs():
    panel = valid_tier_b_panel()
    for item in panel:
        item["session_ref_hash"] = "pending-operator-locator"
    panel[1]["authored_artifact_refs"] = panel[0]["authored_artifact_refs"][:]

    assert_invalid(validate(panel, allow_pending_operator_locator=True), "I4-DUPLICATE-ARTIFACT-REF")


def test_required_quality_security_and_privacy_seats_are_checked():
    no_quality = [item for item in valid_tier_b_panel() if item["seat_dimension"] != "quality"]
    no_security = [item for item in valid_tier_b_panel() if item["seat_dimension"] != "security"]
    no_privacy = [item for item in valid_tier_b_panel() if item["seat_dimension"] != "privacy"]

    assert_invalid(validate(no_quality), "I6-NO-QUALITY-SEAT")
    assert_invalid(validate(no_security), "I7-NO-ADVERSARY-SEAT")
    assert_invalid(validate(no_privacy), "I8-NO-PRIVACY-SEAT")


def test_tier_c_two_reviewers_one_family_can_pass_without_privacy_seat():
    panel = [
        reviewer("Vellum", "Claude", "quality", session_hash("session-vellum")),
        reviewer("Touchstone", "Claude", "security", session_hash("session-touchstone")),
    ]

    result = validate(panel, tier="c")

    assert result.valid
    assert result.violations == []


def test_extract_reviewers_from_gate_record_frontmatter():
    markdown = f"""---
reviewers:
  - reviewer_identity: "Vellum"
    slot: "Claude-B"
    role: "Scribe"
    model_family: "Claude"
    seat_dimension: "quality"
    session_ref_hash: "{session_hash('session-vellum')}"
    authored_artifact_refs: ["Messages/coordination/vellum.md", "Messages/coordination/vellum-confirm.md"]
  - reviewer_identity: "Meridian"
    slot: "Codex-B"
    role: "Sentinel"
    model_family: "Codex"
    seat_dimension: "privacy"
    session_ref_hash: "{session_hash('session-meridian')}"
    authored_artifact_refs:
      - "Messages/coordination/meridian.md"
  - reviewer_identity: "Touchstone"
    slot: "Claude-C"
    role: "Adversary"
    model_family: "Claude"
    seat_dimension: "security"
    session_ref_hash: "{session_hash('session-touchstone')}"
    authored_artifact_refs: ["Messages/coordination/touchstone.md"]
---

# Gate Record
"""

    panel = dogfood.extract_reviewers_from_markdown(markdown)

    assert len(panel) == 3
    assert panel[0]["reviewer_identity"] == "Vellum"
    assert panel[0]["authored_artifact_refs"] == [
        "Messages/coordination/vellum.md",
        "Messages/coordination/vellum-confirm.md",
    ]
    assert panel[1]["authored_artifact_refs"] == ["Messages/coordination/meridian.md"]
    assert validate(panel).valid


def test_extract_reviewers_missing_block_yields_i0():
    panel = dogfood.extract_reviewers_from_markdown("""---
status: "active"
---

# Gate Record
""")

    assert panel == []
    assert_invalid(validate(panel), "I0-NO-REVIEWERS")


def test_v05_self_authored_ref_checks_creator_and_from_aliases():
    panel = valid_tier_b_panel()
    ref_authors = {
        dogfood._cf(panel[0]["authored_artifact_refs"][0]): "Vellum (Claude-B)",
        dogfood._cf(panel[1]["authored_artifact_refs"][0]): "Codex-B Meridian",
        dogfood._cf(panel[2]["authored_artifact_refs"][0]): "2.1.touchstone",
    }

    assert validate(panel, ref_authors=ref_authors).valid
    ref_authors[dogfood._cf(panel[2]["authored_artifact_refs"][0])] = "Datum"

    assert_invalid(validate(panel, ref_authors=ref_authors), "I9-NOT-SELF-AUTHORED")


def test_v05_latest_verdict_blocks_omitted_block_and_mismatch():
    panel = valid_tier_b_panel()
    for r in panel:
        r["verdict"] = "PASS"
    latest = {"vellum": "PASS", "meridian": "PASS", "touchstone": "BLOCK"}

    assert_invalid(validate(panel, latest_verdicts=latest), "I10-OMITTED-BLOCK")

    latest = {"vellum": "PASS", "meridian": "REVISE", "touchstone": "PASS"}
    assert_invalid(validate(panel, latest_verdicts=latest), "I10-VERDICT-MISMATCH")


def test_v05_role_separation_uses_identity_tokens():
    panel = valid_tier_b_panel()

    assert_invalid(
        validate(panel, proposer="Datum (Claude-A)", record_author="Vellum", executor="2.1.datum"),
        "I11-ROLE-CONCENTRATION",
    )
    assert validate(panel, proposer="Datum", record_author="Vellum", executor="Truss").valid


def test_v05_resolve_latest_verdict_prefers_from_over_creator_alias():
    with TemporaryDirectory() as tmp:
        coordination_dir = Path(tmp)
        (coordination_dir / "20260531T164000Z-touchstone.md").write_text(
            """---
creator: "2.1.touchstone"
from: "Touchstone (Verifier & Red-Team)"
verdicts_artifact: "2.7.13.W2.5.H4v05"
verdict: "BLOCK"
---
""",
            encoding="utf-8",
        )

        latest = dogfood.resolve_latest_verdicts("2.7.13.W2.5.H4v05", coordination_dir)

    assert latest == {"touchstone": "BLOCK"}


def test_v05_resolve_latest_verdict_matches_stable_artifact_id_with_suffix():
    with TemporaryDirectory() as tmp:
        coordination_dir = Path(tmp)
        (coordination_dir / "20260531T164000Z-touchstone.md").write_text(
            """---
creator: "2.1.touchstone"
verdicts_artifact: "2.7.13.W2.5.H4v05 (2.0.26 v0.5)"
verdict: "PASS-with-findings"
---
""",
            encoding="utf-8",
        )

        latest = dogfood.resolve_latest_verdicts(
            "2.7.13.W2.5.H4v05 - Amendment Proposal", coordination_dir
        )

    assert latest == {"touchstone": "PASS-with-findings"}


def test_v05_stitched_preparatory_ref_is_invalid_when_latest_verdict_blocks():
    artifact_id = "2.7.13.W2.5.H4v05"
    panel = valid_tier_b_panel()
    for reviewer in panel:
        reviewer["verdict"] = "PASS"

    with TemporaryDirectory() as tmp:
        coordination_dir = Path(tmp)
        for name, verdict in (("Vellum", "PASS"), ("Meridian", "PASS")):
            (coordination_dir / f"{name}-{panel[0]['seat_dimension'] if name == 'Vellum' else 'privacy'}.md").write_text(
                f"""---
from: "{name}"
verdicts_artifact: "{artifact_id}"
verdict: "{verdict}"
---
""",
                encoding="utf-8",
            )
        (coordination_dir / "Touchstone-security.md").write_text(
            """---
creator: "2.1.touchstone"
from: "Touchstone (Verifier & Red-Team)"
---

Ready to verify once the final artifact is posted. This is not a verdict.
""",
            encoding="utf-8",
        )
        (coordination_dir / "20260531T140500Z-touchstone-block.md").write_text(
            f"""---
creator: "2.1.touchstone"
from: "Touchstone (Verifier & Red-Team)"
verdicts_artifact: "{artifact_id}"
verdict: "BLOCK"
---
""",
            encoding="utf-8",
        )

        ref_authors = dogfood.resolve_ref_authors(panel, coordination_dir)
        latest_verdicts = dogfood.resolve_latest_verdicts(artifact_id, coordination_dir)

    result = dogfood.validate_independence(
        panel,
        author_identity="Datum",
        quorum_tier="b",
        ref_authors=ref_authors,
        latest_verdicts=latest_verdicts,
    )

    assert "I9-NOT-SELF-AUTHORED" not in result.violations
    assert_invalid(result, "I10-OMITTED-BLOCK")


# --- v0.5 (H4v05) §5.7 / §6.5 / §5.8 enforcement teeth ---

def _ref(name: str, dimension: str) -> str:
    # casefolded form matches how validate_independence keys authored_artifact_refs
    return f"messages/coordination/{name}-{dimension}.md".casefold()


def authors_all_self() -> dict:
    return {
        _ref("Vellum", "quality"): "2.1.vellum",
        _ref("Meridian", "privacy"): "2.6.meridian",
        _ref("Touchstone", "security"): "2.1.touchstone",
    }


def test_self_authored_refs_pass_i9():
    result = dogfood.validate_independence(
        valid_tier_b_panel(), author_identity="Datum", quorum_tier="b",
        allow_pending_operator_locator=False, ref_authors=authors_all_self(),
        latest_verdicts=None,
    )
    assert result.valid, result.violations


def test_record_author_hand_wrote_a_seat_is_rejected_i9():
    # THE INCIDENT: Datum (record-author) anchored Touchstone's seat to a Datum-authored message.
    authors = authors_all_self()
    authors[_ref("Touchstone", "security")] = "2.1.datum"  # not Touchstone's own message
    result = dogfood.validate_independence(
        valid_tier_b_panel(), author_identity="Datum", quorum_tier="b",
        ref_authors=authors,
    )
    assert_invalid(result, "I9-NOT-SELF-AUTHORED")


def test_every_authored_ref_must_be_self_authored_i9():
    panel = valid_tier_b_panel()
    panel[0]["authored_artifact_refs"].append("Messages/coordination/datum-smuggled.md")
    authors = authors_all_self()
    authors["messages/coordination/datum-smuggled.md"] = "2.1.datum"

    result = dogfood.validate_independence(
        panel, author_identity="Datum", quorum_tier="b", ref_authors=authors,
    )

    assert_invalid(result, "I9-NOT-SELF-AUTHORED")


def test_dangling_ref_cannot_establish_self_authorship_i9():
    authors = authors_all_self()
    authors[_ref("Meridian", "privacy")] = ""  # file did not resolve
    result = dogfood.validate_independence(
        valid_tier_b_panel(), author_identity="Datum", quorum_tier="b",
        ref_authors=authors,
    )
    assert_invalid(result, "I9-NOT-SELF-AUTHORED")


def test_recorded_pass_while_reviewer_blocked_is_void_i10():
    # THE INCIDENT, the §6.5 angle: record says PASS, Touchstone's latest verdict is BLOCK.
    panel = valid_tier_b_panel()
    for r in panel:
        r["verdict"] = "PASS"
    result = dogfood.validate_independence(
        panel, author_identity="Datum", quorum_tier="b",
        latest_verdicts={
            "vellum": "PASS",
            "meridian": "PASS",
            "touchstone": "BLOCK — fabricated panel; politician targets unredacted",
        },
    )
    assert_invalid(result, "I10-OMITTED-BLOCK")


def test_entry_verdict_disagreeing_with_reviewer_is_rejected_i10():
    panel = valid_tier_b_panel()
    panel[0]["verdict"] = "PASS"
    result = dogfood.validate_independence(
        panel, author_identity="Datum", quorum_tier="b",
        latest_verdicts={
            "vellum": "REVISE — fix Q-3 wording first",
            "meridian": "PASS",
            "touchstone": "PASS",
        },
    )
    assert_invalid(result, "I10-VERDICT-MISMATCH")


def test_matching_verdicts_pass_i10():
    panel = valid_tier_b_panel()
    for r in panel:
        r["verdict"] = "PASS — Tier-A destructive single-op"
    result = dogfood.validate_independence(
        panel, author_identity="Datum", quorum_tier="b",
        latest_verdicts={
            "vellum": "PASS",
            "meridian": "PASS",
            "touchstone": "PASS — on the Tier-A destructive single-op",
        },
    )
    assert result.valid, result.violations


def test_resolved_block_then_pass_is_not_void_i10():
    # A BLOCK later superseded by the reviewer's own PASS is fine — latest verdict governs.
    panel = valid_tier_b_panel()
    for r in panel:
        r["verdict"] = "PASS"
    result = dogfood.validate_independence(
        panel, author_identity="Datum", quorum_tier="b",
        latest_verdicts={
            "vellum": "PASS",
            "meridian": "PASS",
            "touchstone": "PASS — concerns addressed in v0.3",
        },
    )
    assert result.valid, result.violations


def test_missing_v05_verdict_metadata_is_rejected_i10():
    panel = valid_tier_b_panel()
    for r in panel:
        r["verdict"] = "PASS"
    result = dogfood.validate_independence(
        panel, author_identity="Datum", quorum_tier="b",
        latest_verdicts={"touchstone": "PASS"},
    )
    assert_invalid(result, "I10-NO-SELF-VERDICT-METADATA")


def test_role_concentration_proposer_equals_executor_is_rejected_i11():
    # THE INCIDENT: one instance is proposer + record-author + executor.
    result = dogfood.validate_independence(
        valid_tier_b_panel(), author_identity="Datum", quorum_tier="a",
        proposer="Datum", record_author="Datum", executor="Datum",
    )
    assert_invalid(result, "I11-ROLE-CONCENTRATION")


def test_separated_roles_pass_i11():
    # proposer Datum, record-author Vellum, executor Matt — the remediation shape.
    result = dogfood.validate_independence(
        valid_tier_b_panel(), author_identity="Datum", quorum_tier="a",
        proposer="Datum", record_author="Vellum", executor="Matt",
    )
    assert result.valid, result.violations


def test_missing_role_separation_field_is_rejected_when_required_i11():
    result = dogfood.validate_independence(
        valid_tier_b_panel(), author_identity="Datum", quorum_tier="a",
        proposer="Datum", record_author="Vellum", executor="",
        require_role_separation_fields=True,
    )
    assert_invalid(result, "I11-MISSING-ROLE-FIELD")


def test_v05_checks_are_opt_in_and_off_by_default():
    # Omitting the new data leaves I0-I8 behaviour identical (backward compatibility).
    result = validate(valid_tier_b_panel())
    assert result.valid
    assert result.violations == []


if __name__ == "__main__":
    tests = [
        test_valid_tier_b_panel_passes,
        test_duplicate_identity_is_rejected,
        test_same_family_tier_b_is_rejected,
        test_author_as_reviewer_is_rejected,
        test_missing_artifact_ref_is_rejected,
        test_duplicate_artifact_ref_is_rejected,
        test_duplicate_session_is_rejected_unless_accepted,
        test_non_hash_session_ref_is_rejected,
        test_pending_session_ref_placeholder_is_rejected,
        test_pending_operator_locator_is_rejected_by_default,
        test_pending_operator_locator_can_pass_as_explicit_interim_with_distinct_artifacts,
        test_pending_operator_locator_still_rejects_duplicate_artifact_refs,
        test_required_quality_security_and_privacy_seats_are_checked,
        test_tier_c_two_reviewers_one_family_can_pass_without_privacy_seat,
        test_extract_reviewers_from_gate_record_frontmatter,
        test_extract_reviewers_missing_block_yields_i0,
        test_v05_self_authored_ref_checks_creator_and_from_aliases,
        test_v05_latest_verdict_blocks_omitted_block_and_mismatch,
        test_v05_role_separation_uses_identity_tokens,
        test_v05_resolve_latest_verdict_prefers_from_over_creator_alias,
        test_v05_resolve_latest_verdict_matches_stable_artifact_id_with_suffix,
        test_v05_stitched_preparatory_ref_is_invalid_when_latest_verdict_blocks,
        test_self_authored_refs_pass_i9,
        test_record_author_hand_wrote_a_seat_is_rejected_i9,
        test_every_authored_ref_must_be_self_authored_i9,
        test_dangling_ref_cannot_establish_self_authorship_i9,
        test_recorded_pass_while_reviewer_blocked_is_void_i10,
        test_entry_verdict_disagreeing_with_reviewer_is_rejected_i10,
        test_matching_verdicts_pass_i10,
        test_resolved_block_then_pass_is_not_void_i10,
        test_missing_v05_verdict_metadata_is_rejected_i10,
        test_role_concentration_proposer_equals_executor_is_rejected_i11,
        test_separated_roles_pass_i11,
        test_missing_role_separation_field_is_rejected_when_required_i11,
        test_v05_checks_are_opt_in_and_off_by_default,
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
