"""Boot-portability scenarios (project #6 proper — merges old C6 + K5).

These assert on the real ``hypernet_swarm.boot_integrity`` primitives the contract
points at (``DocumentManifest``, ``DocumentRecord``, ``BootIntegrityManager``). The
behaviors under test are the load-bearing ones for boot portability and tamper-evidence:

  - a manifest hash is *content-deterministic* (the same boot docs hash the same across
    sessions/models — that is what makes a manifest portable);
  - unchanged docs verify clean;
  - a mutated doc is detected (tamper-evidence);
  - a removed doc is detected (a vanished boot source cannot pass silently);
  - a manifest round-trips through dict serialization without losing its hash.

All of these run today and should pass. If one fails, that is a real finding about boot
integrity, not a harness artifact. The model-behavior regression check (boot fixture
across model configs) is genuinely not yet runnable offline, so it is an honest PENDING.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from .. import _paths  # noqa: F401  (ensures sys.path includes hypernet_swarm)
from ..scenario import Context, Pending, Scenario

from hypernet_swarm.boot_integrity import (
    BootIntegrityManager,
    DocumentManifest,
)
from hypernet_swarm.security import ActionSigner, KeyManager

_FIXTURE_DOCS = {
    "0.fixture.a": ("boot/a.md", "# Boot Doc A\n\nOrientation content A.\n"),
    "0.fixture.b": ("boot/b.md", "# Boot Doc B\n\nOrientation content B.\n"),
    "0.fixture.c": ("boot/c.md", "# Boot Doc C\n\nTrust guardrail acknowledged.\n"),
}


def _new_manager() -> BootIntegrityManager:
    km = KeyManager()
    return BootIntegrityManager(km, ActionSigner(km))


def _write_fixture_archive(root: Path) -> None:
    for _ha, (rel, content) in _FIXTURE_DOCS.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _build_manifest(root: Path) -> DocumentManifest:
    _write_fixture_archive(root)
    mgr = _new_manager()
    for ha, (rel, content) in _FIXTURE_DOCS.items():
        mgr.record_document(ha, rel, content)
    return mgr.create_manifest("FixtureInstance")


# --- scenarios ---------------------------------------------------------------

def content_hash_determinism(ctx: Context) -> None:
    """Per-document content_hash must be identical across loads of identical content.

    This is the actual portability guarantee. NOTE (recorded as a finding for #2): the
    manifest-level ``manifest_hash`` is *not* content-deterministic — it folds in each
    document's ``loaded_at`` timestamp and ``load_order``, so two boots of identical
    content produce different manifest hashes. That is fine for tamper-evidence (which
    compares per-document content_hash, as the other scenarios here verify) but means
    ``manifest_hash`` must not be used as a cross-session 'same boot content?' identity.
    """
    manifest_a = _build_manifest(ctx.workdir / "a")
    manifest_b = _build_manifest(ctx.workdir / "b")
    mismatches = [
        ha
        for ha in manifest_a.documents
        if manifest_a.documents[ha].content_hash != manifest_b.documents[ha].content_hash
    ]
    ctx.expect(
        not mismatches,
        finding_id="vf-bootport-content-determinism",
        target="hypernet_swarm/boot_integrity.py DocumentRecord.content_hash",
        claim_tested="Identical boot-document content hashes identically across loads",
        expected="every document's content_hash matches across the two loads",
        observed=f"mismatched documents: {mismatches}",
        severity="high",
        why_it_matters=(
            "Per-document content_hash is what tamper-evidence and drift detection rest "
            "on. If identical content hashed differently, no boot/restore integrity check "
            "could be trusted."
        ),
        repro="python -m verifier.run boot_portability::content_hash_determinism",
        would_unblock="Hash document content only (encoding-stable), independent of load time/order.",
    )


def unchanged_docs_pass(ctx: Context) -> None:
    """Unchanged docs verify clean: all_valid True, nothing flagged."""
    root = ctx.workdir / "arch"
    manifest = _build_manifest(root)
    result = _new_manager().verify_documents_unchanged(manifest, root)
    ctx.expect(
        result.all_valid and not result.documents_changed,
        finding_id="vf-bootport-unchanged",
        target="hypernet_swarm/boot_integrity.py BootIntegrityManager.verify_documents_unchanged",
        claim_tested="Unmodified boot docs verify as unchanged",
        expected="all_valid is True and documents_changed == []",
        observed=f"all_valid={result.all_valid}, changed={result.documents_changed}",
        severity="high",
        why_it_matters=(
            "False positives here would make the tamper-evidence signal useless — if "
            "clean docs flag as changed, nobody will trust a real alarm."
        ),
        repro="python -m verifier.run boot_portability::unchanged_docs_pass",
        would_unblock="Ensure hashing reads files identically at record and verify time (encoding, newlines).",
    )


def tamper_detected(ctx: Context) -> None:
    """A mutated boot doc is detected as changed."""
    root = ctx.workdir / "arch"
    manifest = _build_manifest(root)
    # Tamper with one document after the manifest was captured.
    (root / "boot/b.md").write_text("# Boot Doc B\n\nTAMPERED content.\n", encoding="utf-8")
    result = _new_manager().verify_documents_unchanged(manifest, root)
    ctx.expect(
        (not result.all_valid) and ("0.fixture.b" in result.documents_changed),
        finding_id="vf-bootport-tamper",
        target="hypernet_swarm/boot_integrity.py BootIntegrityManager.verify_documents_unchanged",
        claim_tested="A boot document mutated after capture is detected (tamper-evidence)",
        expected="all_valid is False and '0.fixture.b' in documents_changed",
        observed=f"all_valid={result.all_valid}, changed={result.documents_changed}",
        severity="high",
        why_it_matters=(
            "A compromised boot sequence produces an instance that cannot detect its own "
            "compromise. Silent tampering is the deepest trust betrayal in the boot path."
        ),
        repro="python -m verifier.run boot_portability::tamper_detected",
        would_unblock="Re-hash each doc at verify time and compare to the recorded content_hash.",
    )


def missing_doc_detected(ctx: Context) -> None:
    """A removed boot doc cannot pass silently — it must be flagged."""
    root = ctx.workdir / "arch"
    manifest = _build_manifest(root)
    (root / "boot/c.md").unlink()
    result = _new_manager().verify_documents_unchanged(manifest, root)
    flagged = "0.fixture.c" in result.documents_changed
    mentions = any("no longer exists" in issue for issue in result.issues)
    ctx.expect(
        (not result.all_valid) and flagged and mentions,
        finding_id="vf-bootport-missing",
        target="hypernet_swarm/boot_integrity.py BootIntegrityManager.verify_documents_unchanged",
        claim_tested="A boot document that no longer resolves is detected as changed/missing",
        expected="all_valid is False, '0.fixture.c' flagged, issue says 'no longer exists'",
        observed=f"all_valid={result.all_valid}, changed={result.documents_changed}, issues={result.issues}",
        severity="high",
        why_it_matters=(
            "A vanished boot source is the boot-path analogue of a broken claim in the "
            "Trust Ledger — it must surface, never be treated as still-present."
        ),
        repro="python -m verifier.run boot_portability::missing_doc_detected",
        would_unblock="Treat a non-existent path as a hard 'changed' with an explicit reason.",
    )


def manifest_roundtrip(ctx: Context) -> None:
    """A manifest survives dict serialization without losing its hash (portable record)."""
    root = ctx.workdir / "arch"
    manifest = _build_manifest(root)
    restored = DocumentManifest.from_dict(manifest.to_dict())
    ctx.expect(
        restored.manifest_hash == manifest.manifest_hash
        and restored._compute_hash() == manifest.manifest_hash,
        finding_id="vf-bootport-roundtrip",
        target="hypernet_swarm/boot_integrity.py DocumentManifest.to_dict/from_dict",
        claim_tested="A serialized manifest reloads with an identical, self-consistent hash",
        expected="restored.manifest_hash == manifest.manifest_hash == recomputed",
        observed=f"stored={manifest.manifest_hash[:12]}..., restored={restored.manifest_hash[:12]}..., recomputed={restored._compute_hash()[:12]}...",
        severity="medium",
        why_it_matters=(
            "Continuity (#2) and boot signatures persist manifests as JSON; if the hash "
            "shifts on reload, every restored integrity check would falsely fail."
        ),
        repro="python -m verifier.run boot_portability::manifest_roundtrip",
        would_unblock="Keep the canonical representation stable across to_dict/from_dict.",
    )


def model_regression_equivalence(ctx: Context) -> None:
    """Same boot fixture across model configs reaches an equivalent valid state.

    Genuinely not runnable offline yet: this needs the boot runner (boot.py BootManager)
    driven under at least two model configurations with live or mocked providers, plus an
    agreed definition of "equivalent valid state." Marked PENDING rather than faked green.
    """
    raise Pending(
        "Model-behavior regression not runnable offline yet: needs boot.py BootManager run "
        "under >=2 model configs (providers) and an agreed 'equivalent valid state' "
        "definition. Coordinate with the swarm boot owners; until then this is honest "
        "not-yet-testable, not a pass."
    )


SCENARIOS = [
    Scenario("boot_portability", "content_hash_determinism", content_hash_determinism,
             "Identical boot docs hash identically (per-document content_hash)."),
    Scenario("boot_portability", "unchanged_docs_pass", unchanged_docs_pass,
             "Unmodified docs verify clean."),
    Scenario("boot_portability", "tamper_detected", tamper_detected,
             "A mutated boot doc is detected."),
    Scenario("boot_portability", "missing_doc_detected", missing_doc_detected,
             "A removed boot doc is flagged."),
    Scenario("boot_portability", "manifest_roundtrip", manifest_roundtrip,
             "Manifest survives serialization with a stable hash."),
    Scenario("boot_portability", "model_regression_equivalence", model_regression_equivalence,
             "PENDING: needs boot runner across model configs."),
]
