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


SCENARIOS = [
    Scenario("continuity", "clean_snapshot_is_faithful", clean_snapshot_is_faithful,
             "#2: clean snapshot ⇒ faithful."),
    Scenario("continuity", "mutated_pointer_drifts", mutated_pointer_drifts,
             "#2: mutated pointer ⇒ drifted, not faithful."),
    Scenario("continuity", "deleted_pointer_missing", deleted_pointer_missing,
             "#2: deleted pointer ⇒ missing, not faithful."),
    Scenario("continuity", "dangling_provenance_is_uncertain", dangling_provenance_is_uncertain,
             "#2: dangling provenance ⇒ uncertain, not faithful."),
    Scenario("continuity", "faithful_never_hides_a_gap", faithful_never_hides_a_gap,
             "#2 (red-team): faithful:true must never hide a gap."),
]
