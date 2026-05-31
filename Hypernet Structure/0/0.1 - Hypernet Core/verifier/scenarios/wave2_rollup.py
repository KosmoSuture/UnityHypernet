"""Wave 2 Directive-2 rollup verifier scenarios.

These scenarios assert against the live coordination helper
``Messages/coordination/wave2_rollup.py``. They lock the privacy and continuity-critical
parts of contract ``2.7.13.W2.1``: C2 freshness, C3 no-leak, C4 starvation buckets, and
C5 claim leases.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .. import _paths  # noqa: F401  (puts Messages/coordination on sys.path)
from ..scenario import Context, Pending, Scenario


def _rollup(ctx: Context):
    mod = ctx.optional("wave2_rollup")
    if mod is None:
        raise Pending(
            "Messages/coordination/wave2_rollup.py is not importable. "
            "D2 rollup contract tests need Truss/Meridian's live helper."
        )
    return mod


def _write_projects(
    root: Path,
    filename: str,
    node: str,
    projects: list[dict],
    visibility: str = "public",
) -> Path:
    path = root / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "node": node,
                "slot": "N.0.3",
                "channel_role": "projects.work-queue",
                "visibility": visibility,
                "projects": projects,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def _project(project_id: str, title: str, **overrides) -> dict:
    data = {
        "project_id": project_id,
        "title": title,
        "description": f"Do {title}.",
        "priority": "p1",
        "status": "pending",
        "created_at": "2026-05-30T10:00:00Z",
        "updated_at": "2026-05-30T10:00:00Z",
        "acceptance": ["evidence recorded"],
    }
    data.update(overrides)
    return data


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8")).hexdigest()


def private_descendant_count_only_for_public_rollup(ctx: Context) -> None:
    r = _rollup(ctx)
    _write_projects(ctx.workdir, "root.projects.json", "0", [_project("p-root", "root")])
    _write_projects(
        ctx.workdir,
        "private/child.projects.json",
        "0.1",
        [_project("p-secret", "secret title", description="private description", visibility="private")],
        visibility="private",
    )

    rollup = r.build_rollup_from_root(ctx.workdir, "0", audience_visibility="public")
    text = json.dumps(rollup)
    ctx.expect(
        rollup["project_count"] == 2
        and rollup["emitted_project_count"] == 1
        and rollup["private_count_only"] == 1
        and "secret title" not in text
        and "private description" not in text,
        finding_id="vf-w2rollup-c3-private-count-only",
        target="Messages/coordination/wave2_rollup.py C3 privacy transform",
        claim_tested="Private descendants contribute count-only to public rollups",
        expected="private project counted but no enumerable row or cleartext",
        observed=f"rollup={rollup}",
        severity="high",
        why_it_matters="A public root rollup must not leak private-node project metadata/content.",
        repro="python -m verifier.run wave2_rollup::private_descendant_count_only_for_public_rollup",
        would_unblock="Keep private effective visibility as count-only for public audiences.",
    )


def private_ancestor_makes_public_child_count_only(ctx: Context) -> None:
    r = _rollup(ctx)
    _write_projects(ctx.workdir, "private-parent/parent.projects.json", "0.1", [], visibility="private")
    _write_projects(
        ctx.workdir,
        "private-parent/public-child/child.projects.json",
        "0.1.1",
        [_project("p-child", "public child under private parent", visibility="public")],
        visibility="public",
    )

    rollup = r.build_rollup_from_root(ctx.workdir, "0", audience_visibility="public")
    ctx.expect(
        rollup["project_count"] == 1
        and rollup["emitted_project_count"] == 0
        and rollup["private_count_only"] == 1
        and "public child under private parent" not in json.dumps(rollup),
        finding_id="vf-w2rollup-c3-ancestor-most-restrictive",
        target="Messages/coordination/wave2_rollup.py effective_visibility_for",
        claim_tested="Most-restrictive visibility composes down the ancestor chain",
        expected="public child under private ancestor is count-only in public root rollup",
        observed=f"rollup={rollup}",
        severity="high",
        why_it_matters="A child cannot launder private ancestor work into the public root by marking itself public.",
        repro="python -m verifier.run wave2_rollup::private_ancestor_makes_public_child_count_only",
        would_unblock="Compose record, origin/list, and ancestor visibility; most restrictive wins.",
    )


def freshness_hashes_are_declared_and_privacy_preserving(ctx: Context) -> None:
    r = _rollup(ctx)
    public_path = _write_projects(ctx.workdir, "root.projects.json", "0", [_project("p-root", "root")])
    private_path = _write_projects(
        ctx.workdir,
        "private/child.projects.json",
        "0.1",
        [_project("p-secret", "secret", visibility="private")],
        visibility="private",
    )
    lists = [r.load_project_list(public_path), r.load_project_list(private_path)]
    rollup = r.compile_rollup("0", lists, generated_at="2026-05-30T10:01:00Z", audience_visibility="public")
    hashes = {item["source"]: item["content_hash"] for item in rollup["source_content_hashes"]}

    public_hash = hashes.get(str(public_path))
    redacted_hashes = [
        item["content_hash"]
        for item in rollup["source_content_hashes"]
        if item["source"].startswith("redacted-source:")
    ]
    ctx.expect(
        rollup["compiled_at"] == "2026-05-30T10:01:00Z"
        and rollup["freshness"]["compiled_at"] == rollup["compiled_at"]
        and public_hash == _sha256(public_path)
        and len(redacted_hashes) == 1
        and redacted_hashes[0].startswith("redacted-content:")
        and str(private_path) not in json.dumps(rollup),
        finding_id="vf-w2rollup-c2-freshness",
        target="Messages/coordination/wave2_rollup.py source_content_hashes",
        claim_tested="Compiled rollups declare source content hashes without exposing private source paths/hashes",
        expected="compiled_at set; public hash raw; private source/hash redacted",
        observed=f"source_content_hashes={rollup['source_content_hashes']}",
        severity="medium",
        why_it_matters="C2 freshness must be detectable without turning private child state into public cleartext.",
        repro="python -m verifier.run wave2_rollup::freshness_hashes_are_declared_and_privacy_preserving",
        would_unblock="Populate freshness from loaded ProjectList.content_hash and redact non-public sources.",
    )


def claim_writes_lease_and_reclaims_expired_claim(ctx: Context) -> None:
    r = _rollup(ctx)
    path = _write_projects(
        ctx.workdir,
        "root.projects.json",
        "0",
        [
            _project(
                "p-reclaim",
                "reclaim",
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

    report = r.claim_project(path, "p-reclaim", "Meridian", execute=True, claimed_at="2026-05-30T10:00:00Z")
    data = json.loads(path.read_text(encoding="utf-8"))
    project = data["projects"][0]
    ctx.expect(
        report["changed"] is True
        and project["claimed_by"] == "Meridian"
        and project["claim_expires_at"] == "2026-05-30T16:00:00Z"
        and project["claim_lease"]["holder"] == "Meridian"
        and data["audit_log"][0]["reclaimed_expired"] is True,
        finding_id="vf-w2rollup-c5-claim-lease",
        target="Messages/coordination/wave2_rollup.py claim_project",
        claim_tested="Expired claims can be atomically reclaimed with a new lease",
        expected="new holder, expiry, claim_lease, and audit reclaimed_expired=true",
        observed=f"project={project}, audit={data.get('audit_log')}",
        severity="medium",
        why_it_matters="Agent-pull work must not be stranded forever by a dead claimant.",
        repro="python -m verifier.run wave2_rollup::claim_writes_lease_and_reclaims_expired_claim",
        would_unblock="Write claim_lease on claim and allow reclaim only after expiry.",
    )


def starvation_bucket_escalates_old_pending_project(ctx: Context) -> None:
    r = _rollup(ctx)
    _write_projects(
        ctx.workdir,
        "root.projects.json",
        "0",
        [_project("p-old", "old low project", priority="p3", created_at="2026-05-01T00:00:00Z")],
    )

    rollup = r.build_rollup_from_root(ctx.workdir, "0")
    project = rollup["projects"][0]
    ctx.expect(
        project["priority_bucket"] == "medium"
        and project["starvation_escalated"] is True
        and rollup["by_bucket"]["medium"] == 1
        and rollup["starvation"]["escalated"][0]["project_id"] == "p-old",
        finding_id="vf-w2rollup-c4-starvation",
        target="Messages/coordination/wave2_rollup.py priority_bucket_for",
        claim_tested="Old pending low-priority work is escalated one bucket and logged",
        expected="p3/low old pending project escalates to medium with audit entry",
        observed=f"project={project}, starvation={rollup.get('starvation')}",
        severity="medium",
        why_it_matters="C4 requires a starvation backstop so low-priority work cannot disappear forever.",
        repro="python -m verifier.run wave2_rollup::starvation_bucket_escalates_old_pending_project",
        would_unblock="Keep deterministic bucket promotion and a visible starvation audit entry.",
    )


def pull_forces_gate_on_significant_content(ctx: Context) -> None:
    """OPEN red-team finding (Touchstone, Adversary seat, 2026-05-30).

    Directive 2 §5 + 2.0.26 §1.3: any pulled work that LEADS TO a significant action must
    route through the gate, and significance defaults to *significant* under doubt. But the
    rollup trusts a self-declared `significant_action` boolean end-to-end: `pull_for_agent`
    sets `gate_required = project.significant_action` with NO cross-check against the
    project's own content. A project that pushes to the public repo and grants Gmail, but
    declares `significant_action: false`, is pulled as `gate_required=False` — it would be
    executed without ever reaching the gate. Asserts the required behavior (content with
    publication/external-access/spawn/destructive indicators must force gate_required); fails
    against the current tool until a conservative heuristic is added.
    """
    r = _rollup(ctx)
    _write_projects(
        ctx.workdir, "root.projects.json", "0",
        [_project(
            "sneaky", "sync docs",
            description="git push the new docs to the public GitHub repository and grant Gmail access.",
            significant_action=False,
            files_owned=[".git/", "README.md"],
            roles=["scribe"],
        )],
    )
    rollup = r.build_rollup_from_root(ctx.workdir, "0")
    matches = r.pull_for_agent(rollup, "scribe")
    sneaky = next((m for m in matches if m["project_id"] == "sneaky"), None)
    ctx.expect(
        sneaky is not None and sneaky["gate_required"] is True,
        finding_id="vf-w2rollup-significance-trusted",
        target="Messages/coordination/wave2_rollup.py pull_for_agent / to_coordination_create_args",
        claim_tested="A pulled project whose content implies a significant action is forced gate_required, not trusted to its self-declared flag",
        expected="gate_required is True for a publish-to-public + grant-external project",
        observed=f"match={sneaky}",
        severity="medium",
        why_it_matters=(
            "Directive 2 §5 / 2.0.26 §1.3: significance defaults to significant under doubt, and "
            "pulled work that leads to a significant action must route through the gate. The rollup "
            "is the work-distribution surface; if it trusts a self-declared (or forged) "
            "significant_action=false, a mislabeled publish/grant/spawn project is handed to an "
            "agent as non-gated and bypasses the entire gateway. The gate is the enforcement, but "
            "the rollup must not actively mark a significant action as gate-not-required."
        ),
        repro="python -m verifier.run wave2_rollup::pull_forces_gate_on_significant_content",
        would_unblock=(
            "Apply a conservative significance heuristic in pull_for_agent / normalize: force "
            "gate_required=True when description or files_owned show publication (push/commit to a "
            "public repo, .git, external publish), new external-service access (gmail/dropbox/oauth/"
            "grant), instance spawn/respawn, or destructive ops — regardless of the self-declared "
            "flag. Default to significant under doubt; the Adversary can only RAISE, never lower."
        ),
    )


SCENARIOS = [
    Scenario("wave2_rollup", "private_descendant_count_only_for_public_rollup",
             private_descendant_count_only_for_public_rollup,
             "C3: private descendant is count-only in a public rollup."),
    Scenario("wave2_rollup", "private_ancestor_makes_public_child_count_only",
             private_ancestor_makes_public_child_count_only,
             "C3: most-restrictive visibility composes through ancestors."),
    Scenario("wave2_rollup", "freshness_hashes_are_declared_and_privacy_preserving",
             freshness_hashes_are_declared_and_privacy_preserving,
             "C2: source freshness hashes are emitted without private cleartext leaks."),
    Scenario("wave2_rollup", "claim_writes_lease_and_reclaims_expired_claim",
             claim_writes_lease_and_reclaims_expired_claim,
             "C5: claims write leases and expired claims can be reclaimed."),
    Scenario("wave2_rollup", "starvation_bucket_escalates_old_pending_project",
             starvation_bucket_escalates_old_pending_project,
             "C4: old pending work escalates one priority bucket and is logged."),
    Scenario("wave2_rollup", "pull_forces_gate_on_significant_content",
             pull_forces_gate_on_significant_content,
             "FINDING: rollup trusts self-declared significant_action; mislabeled publish/grant pulled as non-gated."),
]
