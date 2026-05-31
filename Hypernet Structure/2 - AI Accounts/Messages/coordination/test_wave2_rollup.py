#!/usr/bin/env python3
"""Tests for Wave 2 hierarchical project rollup tooling."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import wave2_rollup


def write_projects(
    root: Path,
    filename: str,
    node: str,
    projects: list[dict],
    visibility: str = "public",
    channel_role: str = wave2_rollup.PROJECT_CHANNEL_ROLE,
) -> Path:
    path = root / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "node": node,
                "slot": "N.0.2",
                "channel_role": channel_role,
                "visibility": visibility,
                "projects": projects,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def project(project_id: str, title: str, **overrides):
    data = {
        "project_id": project_id,
        "title": title,
        "description": f"Do {title}.",
        "priority": "p1",
        "status": "pending",
        "updated_at": "2026-05-30T10:00:00Z",
        "acceptance": ["evidence recorded"],
    }
    data.update(overrides)
    return data


def test_rollup_includes_descendants_and_excludes_siblings():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_projects(root, "root.projects.json", "0", [project("p-root", "root work")])
        write_projects(root, "child/child.projects.json", "0.1", [project("p-child", "child work")])
        write_projects(root, "sibling/sibling.projects.json", "1", [project("p-sibling", "sibling work")])

        lists = [wave2_rollup.load_project_list(path) for path in wave2_rollup.discover_project_lists(root)]
        rollup = wave2_rollup.compile_rollup("0", lists, generated_at="2026-05-30T10:01:00Z")

        ids = {item["project_id"] for item in rollup["projects"]}
        assert ids == {"p-root", "p-child"}
        assert rollup["project_channel_role"] == wave2_rollup.PROJECT_CHANNEL_ROLE
        assert rollup["channel_binding"]["binding_status"] == "provisional_pending_matt_ruling"
        assert rollup["compiled_at"] == "2026-05-30T10:01:00Z"
        assert rollup["freshness"]["compiled_at"] == rollup["compiled_at"]
        assert len(rollup["source_content_hashes"]) == 2
        assert all(len(item["content_hash"]) == 64 for item in rollup["source_content_hashes"])


def test_rollup_physical_slot_is_resolved_from_channel_registry():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_projects(root, "root.projects.json", "0", [project("p-root", "root work")])
        lists = [wave2_rollup.load_project_list(path) for path in wave2_rollup.discover_project_lists(root)]

        rollup = wave2_rollup.compile_rollup(
            "0",
            lists,
            channel_registry={
                "channels": {
                    wave2_rollup.PROJECT_CHANNEL_ROLE: {
                        "slot": "N.0.9",
                        "binding_status": "test_binding",
                        "rationale": "test registry",
                    }
                }
            },
        )

        assert rollup["project_channel_role"] == "projects.work-queue"
        assert rollup["project_slot"] == "N.0.9"
        assert rollup["channel_binding"]["binding_status"] == "test_binding"


def test_global_duplicate_keeps_newer_record():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_projects(
            root,
            "a.projects.json",
            "0.1",
            [project("local-a", "old", global_id="global-one", updated_at="2026-05-30T10:00:00Z")],
        )
        write_projects(
            root,
            "b.projects.json",
            "0.2",
            [project("local-b", "new", global_id="global-one", updated_at="2026-05-30T10:05:00Z")],
        )

        lists = [wave2_rollup.load_project_list(path) for path in wave2_rollup.discover_project_lists(root)]
        rollup = wave2_rollup.compile_rollup("0", lists)

        assert rollup["project_count"] == 1
        assert rollup["projects"][0]["title"] == "new"
        assert len(rollup["duplicates"]) == 1


def test_agent_pull_filters_by_role_tags_and_marks_gate_required():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_projects(
            root,
            "root.projects.json",
            "0",
            [
                project(
                    "p-respawn",
                    "respawn",
                    roles=["Collaboration Substrate Engineer"],
                    personality_tags=["tooling"],
                    significant_action=True,
                    files_owned=["Messages/coordination/wave2_respawn.py"],
                ),
                project("p-scribe", "scribe", roles=["Scribe"], personality_tags=["writing"]),
            ],
        )
        lists = [wave2_rollup.load_project_list(path) for path in wave2_rollup.discover_project_lists(root)]
        rollup = wave2_rollup.compile_rollup("0", lists, generated_at="2026-05-30T10:00:00Z")

        matches = wave2_rollup.pull_for_agent(
            rollup,
            "Collaboration Substrate Engineer",
            ["tooling"],
        )

        assert len(matches) == 1
        assert matches[0]["project_id"] == "p-respawn"
        assert matches[0]["gate_required"] is True
        assert matches[0]["coordination_create_args"]["owned_paths"] == [
            "Messages/coordination/wave2_respawn.py"
        ]


def test_agent_pull_derives_gate_required_from_significant_content():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_projects(
            root,
            "root.projects.json",
            "0",
            [
                project(
                    "p-gated",
                    "sync docs",
                    description="git push the new docs to the public GitHub repository and grant Gmail access.",
                    significant_action=False,
                    files_owned=[".git/", "README.md"],
                    roles=["Scribe"],
                )
            ],
        )
        lists = [wave2_rollup.load_project_list(path) for path in wave2_rollup.discover_project_lists(root)]
        rollup = wave2_rollup.compile_rollup("0", lists, generated_at="2026-05-30T10:00:00Z")

        matches = wave2_rollup.pull_for_agent(rollup, "Scribe")

        assert len(matches) == 1
        assert matches[0]["project_id"] == "p-gated"
        assert matches[0]["gate_required"] is True
        assert "publication" in matches[0]["gate_reasons"]
        assert "external_access" in matches[0]["gate_reasons"]
        assert "Gate required: yes" in matches[0]["coordination_create_args"]["description"]


def test_public_rollup_keeps_private_child_projects_count_only():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_projects(root, "root.projects.json", "0", [project("p-root", "root work")])
        private_path = write_projects(
            root,
            "personal/private.projects.json",
            "0.1",
            [
                project(
                    "p-secret",
                    "sensitive private work",
                    description="Investigate private material in personal notes.",
                    files_owned=["1/private/file.md"],
                    acceptance=["private acceptance"],
                    visibility="private",
                    public_summary="Private child project pending.",
                )
            ],
            visibility="private",
        )

        rollup = wave2_rollup.build_rollup_from_root(root, "0", audience_visibility="public")

        assert rollup["project_count"] == 2
        assert rollup["emitted_project_count"] == 1
        assert rollup["private_count_only"] == 1
        assert rollup["redacted_count"] == 0
        assert {item["project_id"] for item in rollup["projects"]} == {"p-root"}
        assert "sensitive private work" not in json.dumps(rollup)
        assert "Investigate private material" not in json.dumps(rollup)
        assert "Private child project pending" not in json.dumps(rollup)
        assert str(private_path) not in rollup["source_lists"]
        assert any(item.startswith("redacted-source:") for item in rollup["source_lists"])
        assert any(
            item["content_hash"].startswith("redacted-content:")
            for item in rollup["source_content_hashes"]
        )


def test_public_rollup_redacts_restricted_child_project_reference():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_projects(
            root,
            "restricted/restricted.projects.json",
            "0.1",
            [
                project(
                    "p-restricted",
                    "restricted details",
                    global_id="proj:0.1:restricted",
                    description="Do not expose restricted details.",
                    files_owned=["restricted/file.md"],
                    roles=["Trust"],
                    visibility="restricted",
                    public_summary="This summary must not appear in a restricted row.",
                )
            ],
            visibility="restricted",
        )

        rollup = wave2_rollup.build_rollup_from_root(root, "0", audience_visibility="public")

        assert rollup["project_count"] == 1
        assert rollup["emitted_project_count"] == 1
        assert rollup["redacted_count"] == 1
        entry = rollup["projects"][0]
        assert entry["project_id"] == "proj:0.1:restricted"
        assert entry["title"] == "[restricted]"
        assert entry["description"] == "[restricted]"
        assert entry["roles"] == ["Trust"]
        assert entry["files_owned"] == []
        assert "restricted details" not in json.dumps(rollup)
        assert "This summary must not appear" not in json.dumps(rollup)


def test_private_ancestor_makes_public_child_count_only_for_public_rollup():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_projects(root, "private-parent/parent.projects.json", "0.1", [], visibility="private")
        write_projects(
            root,
            "private-parent/public-child/child.projects.json",
            "0.1.1",
            [project("p-child", "public child under private parent", visibility="public")],
            visibility="public",
        )

        rollup = wave2_rollup.build_rollup_from_root(root, "0", audience_visibility="public")

        assert rollup["project_count"] == 1
        assert rollup["emitted_project_count"] == 0
        assert rollup["private_count_only"] == 1
        assert rollup["by_priority"]["p1"] == 1
        assert "public child under private parent" not in json.dumps(rollup)


def test_claim_project_execute_updates_node_local_list():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        path = write_projects(root, "root.projects.json", "0", [project("p-claim", "claim me")])

        report = wave2_rollup.claim_project(
            path,
            "p-claim",
            "Truss",
            execute=True,
            claimed_at="2026-05-30T10:10:00Z",
        )
        data = json.loads(path.read_text(encoding="utf-8"))

        assert report["changed"] is True
        assert data["projects"][0]["status"] == "claimed"
        assert data["projects"][0]["claimed_by"] == "Truss"
        assert data["projects"][0]["claim_expires_at"] == "2026-05-30T16:10:00Z"
        assert data["projects"][0]["claim_lease"] == {
            "holder": "Truss",
            "acquired_at": "2026-05-30T10:10:00Z",
            "expires_at": "2026-05-30T16:10:00Z",
        }
        assert data["audit_log"][0]["event"] == "claimed:p-claim"


def test_expired_claim_can_be_reclaimed_with_new_lease():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        path = write_projects(
            root,
            "root.projects.json",
            "0",
            [
                project(
                    "p-reclaim",
                    "reclaim me",
                    status="claimed",
                    claimed_by="Vellum",
                    claimed_at="2026-05-30T01:00:00Z",
                    claim_expires_at="2026-05-30T07:00:00Z",
                    claim_lease={
                        "holder": "Vellum",
                        "acquired_at": "2026-05-30T01:00:00Z",
                        "expires_at": "2026-05-30T07:00:00Z",
                    },
                )
            ],
        )

        report = wave2_rollup.claim_project(
            path,
            "p-reclaim",
            "Meridian",
            execute=True,
            claimed_at="2026-05-30T10:00:00Z",
        )
        data = json.loads(path.read_text(encoding="utf-8"))

        assert report["changed"] is True
        assert data["projects"][0]["claimed_by"] == "Meridian"
        assert data["projects"][0]["claim_expires_at"] == "2026-05-30T16:00:00Z"
        assert data["audit_log"][0]["reclaimed_expired"] is True


def test_priority_buckets_include_starvation_escalation():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        write_projects(
            root,
            "root.projects.json",
            "0",
            [
                project(
                    "p-old",
                    "old low priority",
                    priority="p3",
                    created_at="2026-05-01T00:00:00Z",
                    updated_at="2026-05-01T00:00:00Z",
                ),
                project(
                    "p-new",
                    "new low priority",
                    priority="p3",
                    created_at="2026-05-29T00:00:00Z",
                    updated_at="2026-05-29T00:00:00Z",
                ),
            ],
        )

        lists = [wave2_rollup.load_project_list(path) for path in wave2_rollup.discover_project_lists(root)]
        rollup = wave2_rollup.compile_rollup("0", lists, generated_at="2026-05-30T10:00:00Z")
        old_project = next(item for item in rollup["projects"] if item["project_id"] == "p-old")
        new_project = next(item for item in rollup["projects"] if item["project_id"] == "p-new")

        assert old_project["priority_bucket"] == "medium"
        assert old_project["starvation_escalated"] is True
        assert new_project["priority_bucket"] == "low"
        assert new_project["starvation_escalated"] is False
        assert rollup["by_bucket"]["medium"] == 1
        assert rollup["by_bucket"]["low"] == 1
        assert rollup["starvation"]["escalated"][0]["project_id"] == "p-old"


if __name__ == "__main__":
    tests = [
        test_rollup_includes_descendants_and_excludes_siblings,
        test_rollup_physical_slot_is_resolved_from_channel_registry,
        test_global_duplicate_keeps_newer_record,
        test_agent_pull_filters_by_role_tags_and_marks_gate_required,
        test_agent_pull_derives_gate_required_from_significant_content,
        test_public_rollup_keeps_private_child_projects_count_only,
        test_public_rollup_redacts_restricted_child_project_reference,
        test_private_ancestor_makes_public_child_count_only_for_public_rollup,
        test_claim_project_execute_updates_node_local_list,
        test_expired_claim_can_be_reclaimed_with_new_lease,
        test_priority_buckets_include_starvation_escalation,
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
