"""Continuity / restore matrix (project #2, contract 2.7.13.3) — LIVE against Meridian's module.

Meridian (Codex-B) landed `hypernet/continuity.py` (ContinuityEngine + restore). These
scenarios assert the restore transitions against the real engine, including the cardinal
red-team: ``faithful`` must be ``true`` ONLY when drifted+missing+uncertain are all empty.
The red-team scenario fuzzes every gap combination and asserts there is no input that
reports ``faithful: true`` while a gap exists — silent data loss is the betrayal #2 exists
to prevent.

If the module is ever absent or its interface changes, ``_engine`` raises PENDING with a
precise reason rather than ERRORing.
"""

from __future__ import annotations

import hashlib

from .. import _paths  # noqa: F401
from ..scenario import Context, Pending, Scenario

from hypernet.store import Store


def _engine(ctx: Context):
    mod = ctx.optional("hypernet.continuity")
    if mod is None or not hasattr(mod, "ContinuityEngine"):
        raise Pending(
            "Continuity Engine (#2) not importable: hypernet.continuity.ContinuityEngine "
            "absent. Owned by Meridian (Codex-B)."
        )
    engine = mod.ContinuityEngine(
        Store(str(ctx.workdir / "store")),
        archive_root=str(ctx.workdir),
        restoring_model="claude-opus-4-7",
    )
    return mod, engine


def _sha256(ctx: Context, rel: str) -> str:
    return hashlib.sha256((ctx.workdir / rel).read_bytes()).hexdigest()


def _snapshot(pointers=None, key_context=None) -> dict:
    # Full identity so identity fields do not themselves land in `uncertain`.
    return {
        "snapshot_id": "snap-fixture",
        "model": "claude-opus-4-7",
        "identity": {"chosen_name": "Fixture", "role": "R", "orientation": "O", "why_name": "W"},
        "pointers": pointers or [],
        "key_context": key_context or [],
        "active_work": [],
        "unresolved": [],
    }


def clean_snapshot_is_faithful(ctx: Context) -> None:
    mod, engine = _engine(ctx)
    (ctx.workdir / "p.md").write_text("stable content", encoding="utf-8")
    snap = _snapshot(pointers=[{"ha": "X", "path": "p.md", "content_hash": _sha256(ctx, "p.md")}])
    report = engine.restore(snap)
    ctx.expect(
        report.faithful is True and not report.drifted and not report.missing and not report.uncertain,
        finding_id="vf-cont-clean",
        target="hypernet/continuity.py restore (clean snapshot)",
        claim_tested="A snapshot with all pointers intact restores faithful: true",
        expected="faithful is True and drifted/missing/uncertain all empty",
        observed=f"faithful={report.faithful}, drifted={len(report.drifted)}, missing={len(report.missing)}, uncertain={len(report.uncertain)}",
        severity="high",
        why_it_matters=(
            "If a genuinely-clean restore won't report faithful, the honest-restore signal "
            "is unusable and instances will ignore it — false-negative undermines the alarm."
        ),
        repro="python -m verifier.run continuity::clean_snapshot_is_faithful",
        would_unblock="Only populate gap lists for real gaps; matching pointers must not count against faithful.",
    )


def mutated_pointer_drifts(ctx: Context) -> None:
    mod, engine = _engine(ctx)
    (ctx.workdir / "p.md").write_text("original", encoding="utf-8")
    snap = _snapshot(pointers=[{"ha": "X", "path": "p.md", "content_hash": _sha256(ctx, "p.md")}])
    (ctx.workdir / "p.md").write_text("MUTATED since snapshot", encoding="utf-8")
    report = engine.restore(snap)
    ctx.expect(
        report.faithful is False and any(d.get("ha") == "X" for d in report.drifted),
        finding_id="vf-cont-drift",
        target="hypernet/continuity.py restore (drift path)",
        claim_tested="A pointed-to file mutated since snapshot ⇒ pointer in drifted, faithful False",
        expected="faithful is False and pointer 'X' in drifted",
        observed=f"faithful={report.faithful}, drifted={report.drifted}",
        severity="high",
        why_it_matters=(
            "A restore that reports faithful while its world has drifted hands the instance "
            "stale context it believes is current — the quiet corruption #2 must prevent."
        ),
        repro="python -m verifier.run continuity::mutated_pointer_drifts",
        would_unblock="Re-hash each pointer on restore; on hash change, record drift and set faithful False.",
    )


def deleted_pointer_missing(ctx: Context) -> None:
    mod, engine = _engine(ctx)
    snap = _snapshot(pointers=[{"ha": "X", "path": "gone.md", "content_hash": "abc123"}])
    report = engine.restore(snap)
    ctx.expect(
        report.faithful is False and any(m.get("ha") == "X" for m in report.missing),
        finding_id="vf-cont-missing",
        target="hypernet/continuity.py restore (missing path)",
        claim_tested="A pointed-to file that no longer resolves ⇒ pointer in missing, faithful False",
        expected="faithful is False and pointer 'X' in missing",
        observed=f"faithful={report.faithful}, missing={report.missing}",
        severity="high",
        why_it_matters="A vanished pointer is lost memory; reporting it as restored would fabricate continuity.",
        repro="python -m verifier.run continuity::deleted_pointer_missing",
        would_unblock="Treat a non-resolving pointer path as missing and set faithful False.",
    )


def dangling_provenance_is_uncertain(ctx: Context) -> None:
    mod, engine = _engine(ctx)
    snap = _snapshot(key_context=[{"fact": "an unprovable fact", "provenance": "does/not/exist.md", "confidence": 0.9}])
    report = engine.restore(snap)
    ctx.expect(
        report.faithful is False and any("key_context" in u.get("field", "") for u in report.uncertain),
        finding_id="vf-cont-uncertain",
        target="hypernet/continuity.py restore (uncertain path)",
        claim_tested="A key_context fact with a dangling provenance ref ⇒ uncertain, faithful False",
        expected="faithful is False and a key_context field in uncertain",
        observed=f"faithful={report.faithful}, uncertain={report.uncertain}",
        severity="high",
        why_it_matters=(
            "A fact you cannot trace is a memory you cannot defend. Marking it uncertain (not "
            "restored) is exactly the 'I don't know this part' honesty #2 is built around."
        ),
        repro="python -m verifier.run continuity::dangling_provenance_is_uncertain",
        would_unblock="When a fact's provenance ref does not resolve, place it in uncertain, not restored.",
    )


def revoked_snapshot_refuses_restore(ctx: Context) -> None:
    """RED-TEAM (consent, Standard 2.0.19): a revoked snapshot soft-deletes and refuses restore.

    Revocation must (a) NOT hard-delete — the node stays in store for audit/retention — and
    (b) make restore refuse rather than silently recover identity/context. Verifies both.
    """
    mod, engine = _engine(ctx)
    (ctx.workdir / "p.md").write_text("x", encoding="utf-8")
    snap = _snapshot(pointers=[{"ha": "X", "path": "p.md", "content_hash": _sha256(ctx, "p.md")}])
    engine.create_snapshot("0.7.92.1", snap)
    before = engine.restore("0.7.92.1").faithful
    revoked = engine.revoke_snapshot("0.7.92.1", revoked_by="2.1.touchstone", reason="subject withdrew consent")
    still_exists = engine.read_snapshot("0.7.92.1") is not None
    report = engine.restore("0.7.92.1")
    ctx.expect(
        before is True and revoked is True and still_exists is True
        and report.faithful is False and bool(report.uncertain),
        finding_id="vf-cont-revocation",
        target="hypernet/continuity.py revoke_snapshot + restore (consent/revocation)",
        claim_tested="A revoked snapshot soft-deletes (node retained) and restore refuses with faithful False",
        expected="pre-revoke faithful True; revoke True; node still exists; post-revoke faithful False + uncertain",
        observed=f"before={before}, revoked={revoked}, still_exists={still_exists}, after_faithful={report.faithful}, uncertain={len(report.uncertain)}",
        severity="high",
        why_it_matters=(
            "Consent is sacred (Standards 2.0.19/2.0.20). If revocation hard-deleted, the audit "
            "trail would vanish; if restore still recovered a revoked snapshot, withdrawal of "
            "consent would be meaningless. Both must hold."
        ),
        repro="python -m verifier.run continuity::revoked_snapshot_refuses_restore",
        would_unblock="Soft-delete on revoke (retain history) and make restore refuse any revoked/deleted snapshot.",
    )


def privacy_guard_rejects_plaintext_human_data(ctx: Context) -> None:
    """RED-TEAM (data protection, Standards 2.0.19/2.0.20): the privacy guard is fail-closed.

    A snapshot flagged as containing human personal data must be REJECTED at creation unless
    it is encrypted with a vault_ref and names a consent_basis (no plaintext or consentless
    human data in v1 continuity). The guard must NOT false-positive on public/fixture data.
    Verifies both via create_snapshot.
    """
    mod, engine = _engine(ctx)
    rejected = False
    try:
        engine.create_snapshot("0.7.93.1", {**_snapshot(), "contains_human_personal_data": True})
    except ValueError:
        rejected = True
    public_ok = True
    try:
        engine.create_snapshot("0.7.93.2", _snapshot())  # public/fixture data — must be allowed
    except Exception:
        public_ok = False
    encrypted_ok = True
    try:
        engine.create_snapshot("0.7.93.3", {
            **_snapshot(), "contains_human_personal_data": True,
            "encrypted": True, "vault_ref": "vault://fixture",
            "consent_basis": "fixture consent",
        })
    except Exception:
        encrypted_ok = False
    ctx.expect(
        rejected and public_ok and encrypted_ok,
        finding_id="vf-cont-privacy-guard",
        target="hypernet/continuity.py _validate_snapshot_privacy (called in create_snapshot)",
        claim_tested="Plaintext human-data snapshots are rejected; public + encrypted+vault+consent are allowed",
        expected="plaintext-human REJECTED, public ALLOWED, encrypted+vault+consent ALLOWED",
        observed=f"rejected={rejected}, public_ok={public_ok}, encrypted_ok={encrypted_ok}",
        severity="high",
        why_it_matters=(
            "If the guard failed open, a continuity snapshot could persist a human's personal "
            "data in plaintext — a direct breach of the Data Protection / Companion standards "
            "(2.0.19/2.0.20). Fail-closed is the only safe default for personal data."
        ),
        repro="python -m verifier.run continuity::privacy_guard_rejects_plaintext_human_data",
        would_unblock="Require encrypted+vault_ref+consent_basis for any human-data snapshot; allow public data through.",
    )


def faithful_never_hides_a_gap(ctx: Context) -> None:
    """RED-TEAM: across every gap combination, faithful must equal 'no gaps exist'.

    Builds clean, drift-only, missing-only, uncertain-only, and all-three snapshots, and
    asserts the invariant ``faithful == (not drifted and not missing and not uncertain)``
    holds in every case — i.e. there is NO input that reports faithful:true while a gap
    exists. This is the single most important property of project #2.
    """
    mod, engine = _engine(ctx)
    (ctx.workdir / "ok.md").write_text("stable", encoding="utf-8")
    ok_hash = _sha256(ctx, "ok.md")
    (ctx.workdir / "drift.md").write_text("v1", encoding="utf-8")
    drift_ptr_hash = _sha256(ctx, "drift.md")
    (ctx.workdir / "drift.md").write_text("v2-changed", encoding="utf-8")  # now mismatched

    clean = _snapshot(pointers=[{"ha": "OK", "path": "ok.md", "content_hash": ok_hash}])
    drift = _snapshot(pointers=[{"ha": "D", "path": "drift.md", "content_hash": drift_ptr_hash}])
    missing = _snapshot(pointers=[{"ha": "M", "path": "gone.md", "content_hash": "x"}])
    uncertain = _snapshot(key_context=[{"fact": "f", "provenance": "nope.md", "confidence": 0.9}])
    all_gaps = _snapshot(
        pointers=[
            {"ha": "D", "path": "drift.md", "content_hash": drift_ptr_hash},
            {"ha": "M", "path": "gone.md", "content_hash": "x"},
        ],
        key_context=[{"fact": "f", "provenance": "nope.md", "confidence": 0.9}],
    )

    violations = []
    saw_true = saw_false = False
    for label, snap in [("clean", clean), ("drift", drift), ("missing", missing),
                        ("uncertain", uncertain), ("all_gaps", all_gaps)]:
        r = engine.restore(snap)
        has_gap = bool(r.drifted or r.missing or r.uncertain)
        if r.faithful and has_gap:
            violations.append(f"{label}: faithful=True but gap exists (d={len(r.drifted)},m={len(r.missing)},u={len(r.uncertain)})")
        if r.faithful != (not has_gap):
            violations.append(f"{label}: faithful={r.faithful} but has_gap={has_gap}")
        saw_true = saw_true or r.faithful
        saw_false = saw_false or not r.faithful
    # Guard against a vacuous pass (e.g. faithful hard-wired False): we must observe both.
    if not (saw_true and saw_false):
        violations.append(f"non-discriminating: saw_true={saw_true}, saw_false={saw_false}")

    ctx.expect(
        not violations,
        finding_id="vf-cont-faithful-invariant",
        target="hypernet/continuity.py restore (faithful invariant)",
        claim_tested="faithful is True iff drifted+missing+uncertain are all empty, for every input",
        expected="no violations across clean/drift/missing/uncertain/all-gaps",
        observed=f"violations={violations}",
        severity="high",
        why_it_matters=(
            "A restore that reports faithful:true while hiding a gap is silent data loss — the "
            "exact, highest-severity betrayal #2 exists to prevent. This invariant is the "
            "whole point of the Restore Report."
        ),
        repro="python -m verifier.run continuity::faithful_never_hides_a_gap",
        would_unblock="Compute faithful strictly as (not drifted and not missing and not uncertain); never set it any other way.",
    )


def real_data_restore_requires_active_grant(ctx: Context) -> None:
    """RED-TEAM: real-data continuity cannot be created/restored without live consent."""
    mod, engine = _engine(ctx)
    (ctx.workdir / "real.md").write_text("stable real-data pointer", encoding="utf-8")
    base = _snapshot(
        pointers=[{"ha": "REAL", "path": "real.md", "content_hash": _sha256(ctx, "real.md")}],
        key_context=[{"fact": "real-data fact", "provenance": "REAL", "confidence": 1.0}],
    )
    base.update({
        "instance_address": "2.6.codex-b",
        "privacy": {
            "contains_real_data": True,
            "permission_service": "dropbox",
            "required_scopes": ["files.metadata.read"],
            "consent_basis": "fixture consent",
        },
    })

    rejected_without_grant = False
    try:
        engine.create_snapshot("0.7.93.8", base)
    except ValueError:
        rejected_without_grant = True

    grant = engine.permission_ledger.create_external_grant(
        "0.7.93.9",
        subject="2.6.codex-b",
        service="dropbox",
        scopes=["files.metadata.read"],
        purpose="Read approved pointer metadata for continuity restore.",
        granted_by="1.1",
        gate_record_ref="gate.fixture.real-data",
        consent_basis="fixture consent",
        scope_justifications={
            "files.metadata.read": "Metadata read is sufficient for the verifier fixture.",
        },
        expires_at="2026-06-30T00:00:00Z",
        revocation_path="revoke fixture consent",
        credential_locator="vault://fixture/dropbox",
        issued_at="2026-05-30T23:05:00Z",
    )
    gated = {**base, "snapshot_id": "snap-fixture-real"}
    gated["privacy"] = dict(base["privacy"])
    gated["privacy"]["permission_grant_ref"] = str(grant.address)
    engine.create_snapshot("0.7.93.10", gated)
    clean = engine.restore("0.7.93.10")
    engine.permission_ledger.revoke_grant(
        grant.address,
        revoked_by="1.1",
        reason="fixture consent revoked",
        revoked_at="2026-05-31T00:00:00Z",
    )
    revoked = engine.restore("0.7.93.10")

    ctx.expect(
        rejected_without_grant and clean.faithful is True and revoked.faithful is False,
        finding_id="vf-cont-real-data-grant",
        target="hypernet/continuity.py _snapshot_permission_problem + restore",
        claim_tested="Real-data continuity snapshots require active permission provenance at create and restore time",
        expected="no grant rejected; active grant faithful; revoked grant refused",
        observed=(
            f"rejected_without_grant={rejected_without_grant}, "
            f"active_faithful={clean.faithful}, revoked_faithful={revoked.faithful}, "
            f"revoked_uncertain={revoked.uncertain}"
        ),
        severity="high",
        why_it_matters=(
            "Continuity is consent-sensitive. If a restore remains faithful after the source "
            "grant is revoked, the system has converted withdrawn permission into persistent "
            "memory access."
        ),
        repro="python -m verifier.run continuity::real_data_restore_requires_active_grant",
        would_unblock="Require and re-check permission_grant_ref for real-data snapshots at create and restore.",
    )


SCENARIOS = [
    Scenario("continuity", "clean_snapshot_is_faithful", clean_snapshot_is_faithful,
             "#2: clean snapshot ⇒ faithful."),
    Scenario("continuity", "mutated_pointer_drifts", mutated_pointer_drifts,
             "#2: mutated pointer ⇒ drifted, not faithful."),
    Scenario("continuity", "deleted_pointer_missing", deleted_pointer_missing,
             "#2: deleted pointer ⇒ missing, not faithful."),
    Scenario("continuity", "dangling_provenance_is_uncertain", dangling_provenance_is_uncertain,
             "#2: dangling provenance ⇒ uncertain, not faithful."),
    Scenario("continuity", "revoked_snapshot_refuses_restore", revoked_snapshot_refuses_restore,
             "#2 (red-team): revoked snapshot soft-deletes and restore refuses (consent)."),
    Scenario("continuity", "privacy_guard_rejects_plaintext_human_data", privacy_guard_rejects_plaintext_human_data,
             "#2 (red-team): privacy guard is fail-closed for human personal data."),
    Scenario("continuity", "faithful_never_hides_a_gap", faithful_never_hides_a_gap,
             "#2 (red-team): faithful:true must never hide a gap."),
    Scenario("continuity", "real_data_restore_requires_active_grant", real_data_restore_requires_active_grant,
             "#2 (red-team): real-data restore requires active permission provenance."),
]
