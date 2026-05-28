"""
Trust Ledger and deterministic claim auditor.

Wave 1 v1 scope:
- claim/evidence records are normal Hypernet Nodes;
- provenance uses existing Link evidence and claim audit_history;
- file, inline, and HA sources are checked by SHA-256 and deterministic
  substring matching;
- positive status is always derived by audit_claim(), never trusted from input.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .address import HypernetAddress
from .link import Link
from .node import Node
from .store import Store


CLAIM_TYPE = HypernetAddress.parse("0.4.10.8.2")
EVIDENCE_TYPE = HypernetAddress.parse("0.4.10.8.3")
AUDIT_RECORD_TYPE = HypernetAddress.parse("0.4.10.7.6")

LINK_CITES = "0.6.11.4.2"
LINK_SUPPORTS = "0.6.11.4.3"
LINK_CONTRADICTS = "0.6.11.4.4"


class ClaimStatus:
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    STALE = "stale"
    CONTRADICTED = "contradicted"
    BROKEN = "broken"


STATUS_SEVERITY = {
    ClaimStatus.VERIFIED: 0,
    ClaimStatus.UNVERIFIED: 1,
    ClaimStatus.STALE: 2,
    ClaimStatus.BROKEN: 3,
    ClaimStatus.CONTRADICTED: 4,
}


@dataclass
class SourceResult:
    locator: str
    locator_type: str
    resolved: bool
    matched: Optional[bool]
    content_hash: Optional[str]
    drift: bool
    status: str
    method: str = "substring"
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AuditResult:
    claim_id: str
    old_status: str
    new_status: str
    confidence: Optional[float]
    checked_at: str
    source_results: list[SourceResult] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["source_results"] = [r.to_dict() for r in self.source_results]
        return data


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _as_address(address: str | HypernetAddress) -> HypernetAddress:
    return address if isinstance(address, HypernetAddress) else HypernetAddress.parse(address)


def _line_range_content(content: str, line_range: Any) -> str:
    if not line_range:
        return content
    if isinstance(line_range, str) and "-" in line_range:
        start_text, end_text = line_range.split("-", 1)
        start = max(int(start_text), 1)
        end = max(int(end_text), start)
    else:
        start = end = max(int(line_range), 1)
    lines = content.splitlines()
    return "\n".join(lines[start - 1:end])


class TrustLedger:
    """Small v1 claim/evidence store and auditor."""

    def __init__(
        self,
        store: Store,
        archive_root: str | Path = ".",
        auditor_id: str = "2.6.codex-b",
    ) -> None:
        self.store = store
        self.archive_root = Path(archive_root)
        self.auditor_id = auditor_id

    def create_claim(
        self,
        address: str | HypernetAddress,
        statement: str,
        asserted_by: str,
        source_refs: list[dict[str, Any]],
        *,
        claim_id: Optional[str] = None,
        subject: Optional[str] = None,
        asserted_at: Optional[str] = None,
    ) -> Node:
        addr = _as_address(address)
        data = {
            "claim_id": claim_id or str(addr),
            "statement": statement,
            "subject": subject,
            "asserted_by": asserted_by,
            "asserted_at": asserted_at or utc_now(),
            "source_refs": [dict(ref) for ref in source_refs],
            "status": ClaimStatus.UNVERIFIED,
            "confidence": None,
            "last_checked_at": None,
            "audit_history": [],
        }
        node = Node(
            address=addr,
            type_address=CLAIM_TYPE,
            data=data,
            source_type="ai_generated",
            creator=HypernetAddress.parse(asserted_by) if asserted_by else None,
            flags=["trust-ledger-claim"],
        )
        self.store.put_node(node)
        return node

    def read_claim(self, address: str | HypernetAddress) -> Optional[Node]:
        return self.store.get_node(_as_address(address))

    def create_evidence(
        self,
        address: str | HypernetAddress,
        *,
        source: str,
        method: str,
        confidence: float,
        content_hash: Optional[str] = None,
    ) -> Node:
        addr = _as_address(address)
        node = Node(
            address=addr,
            type_address=EVIDENCE_TYPE,
            data={
                "source": source,
                "method": method,
                "confidence": confidence,
                "content_hash": content_hash,
                "checked_at": utc_now() if content_hash else None,
            },
            source_type="ai_generated",
            creator=HypernetAddress.parse(self.auditor_id),
            flags=["trust-ledger-evidence"],
        )
        self.store.put_node(node)
        return node

    def link_evidence_to_claim(
        self,
        evidence_address: str | HypernetAddress,
        claim_address: str | HypernetAddress,
        *,
        relationship: str = "supports",
        evidence: Optional[dict[str, Any]] = None,
    ) -> str:
        evidence_addr = _as_address(evidence_address)
        claim_addr = _as_address(claim_address)
        link_type = LINK_CONTRADICTS if relationship == "contradicts" else LINK_SUPPORTS
        link = Link(
            from_address=evidence_addr,
            to_address=claim_addr,
            link_type=link_type,
            relationship=relationship,
            created_by=self.auditor_id,
            creation_method="audit",
            evidence=[evidence or {}] if evidence else [],
            tags=["trust-ledger"],
        )
        return self.store.put_link(link)

    def audit_claim(self, claim_id: str | HypernetAddress) -> AuditResult:
        claim_address = _as_address(claim_id)
        node = self.store.get_node(claim_address)
        if node is None:
            raise KeyError(f"Claim not found: {claim_address}")

        checked_at = utc_now()
        old_status = node.data.get("status", ClaimStatus.UNVERIFIED)
        source_refs = [dict(ref) for ref in node.data.get("source_refs", [])]
        source_results = [self._audit_source(node, ref) for ref in source_refs]
        link_contradiction = self._has_contradicting_link(claim_address)

        if link_contradiction:
            new_status = ClaimStatus.CONTRADICTED
            note = "Contradicting evidence link exists."
        elif source_results:
            new_status = max(
                (result.status for result in source_results),
                key=lambda status: STATUS_SEVERITY[status],
            )
            note = self._note_for_status(new_status)
        else:
            new_status = ClaimStatus.UNVERIFIED
            note = "Claim has no source_refs to audit."

        confidence = self._confidence_for_status(new_status)
        self._persist_audit(
            node=node,
            source_refs=source_refs,
            source_results=source_results,
            old_status=old_status,
            new_status=new_status,
            confidence=confidence,
            checked_at=checked_at,
            note=note,
        )

        return AuditResult(
            claim_id=node.data.get("claim_id", str(claim_address)),
            old_status=old_status,
            new_status=new_status,
            confidence=confidence,
            checked_at=checked_at,
            source_results=source_results,
            note=note,
        )

    def audit_all(
        self,
        prefix: str | HypernetAddress | None = None,
        since: Optional[str] = None,
    ) -> list[AuditResult]:
        del since  # Reserved for v2 incremental scans.
        prefix_addr = _as_address(prefix) if prefix else None
        claims = self.store.list_nodes(prefix=prefix_addr, type_address=CLAIM_TYPE)
        return [self.audit_claim(claim.address) for claim in claims]

    def _audit_source(self, claim: Node, source_ref: dict[str, Any]) -> SourceResult:
        locator = str(source_ref.get("locator", ""))
        locator_type = source_ref.get("locator_type", "file")
        method = source_ref.get("method", "substring")
        stored_hash = source_ref.get("content_hash")

        if locator_type == "file":
            path = self._resolve_file(locator)
            if not path.exists():
                status = ClaimStatus.BROKEN if stored_hash else ClaimStatus.UNVERIFIED
                note = "Source file missing after prior verification." if stored_hash else "Source file does not resolve."
                return SourceResult(
                    locator=locator,
                    locator_type=locator_type,
                    resolved=False,
                    matched=None,
                    content_hash=None,
                    drift=False,
                    status=status,
                    method=method,
                    note=note,
                )
            current_hash = sha256_file(path)
            text = path.read_text(encoding="utf-8")
        elif locator_type == "inline":
            if "content" not in source_ref and "text" not in source_ref:
                return SourceResult(
                    locator=locator,
                    locator_type=locator_type,
                    resolved=False,
                    matched=None,
                    content_hash=None,
                    drift=False,
                    status=ClaimStatus.UNVERIFIED,
                    method=method,
                    note="Inline source has no content/text field.",
                )
            text = str(source_ref.get("content", source_ref.get("text", "")))
            current_hash = sha256_text(text)
        elif locator_type == "ha":
            source_node = self.store.get_node(_as_address(locator))
            if source_node is None:
                status = ClaimStatus.BROKEN if stored_hash else ClaimStatus.UNVERIFIED
                note = "HA source missing after prior verification." if stored_hash else "HA source does not resolve."
                return SourceResult(
                    locator=locator,
                    locator_type=locator_type,
                    resolved=False,
                    matched=None,
                    content_hash=None,
                    drift=False,
                    status=status,
                    method=method,
                    note=note,
                )
            text = self._node_text(source_node)
            current_hash = sha256_text(text)
        else:
            return SourceResult(
                locator=locator,
                locator_type=locator_type,
                resolved=False,
                matched=None,
                content_hash=None,
                drift=False,
                status=ClaimStatus.UNVERIFIED,
                method=method,
                note=f"Unsupported locator_type for v1: {locator_type}",
            )

        if stored_hash and current_hash != stored_hash:
            return SourceResult(
                locator=locator,
                locator_type=locator_type,
                resolved=True,
                matched=None,
                content_hash=current_hash,
                drift=True,
                status=ClaimStatus.STALE,
                method=method,
                note="Source hash changed since last verified audit.",
            )

        text = _line_range_content(text, source_ref.get("line_range"))
        expected = source_ref.get("match_text") or source_ref.get("expected_text") or claim.data.get("statement", "")
        matched = str(expected) in text
        return SourceResult(
            locator=locator,
            locator_type=locator_type,
            resolved=True,
            matched=matched,
            content_hash=current_hash,
            drift=False,
            status=ClaimStatus.VERIFIED if matched else ClaimStatus.CONTRADICTED,
            method=method,
            note="Substring matched source." if matched else "Substring was not found in source.",
        )

    def _resolve_file(self, locator: str) -> Path:
        path = Path(locator)
        return path if path.is_absolute() else self.archive_root / path

    @staticmethod
    def _node_text(node: Node) -> str:
        for key in ("text", "content", "body", "statement", "summary", "title"):
            if key in node.data:
                return str(node.data[key])
        return json.dumps(node.data, sort_keys=True, default=str)

    def _has_contradicting_link(self, claim_address: HypernetAddress) -> bool:
        links = self.store.get_links_to(claim_address, relationship="contradicts")
        links.extend(self.store.get_links_from(claim_address, relationship="contradicts"))
        return any(link.is_active for link in links)

    def _persist_audit(
        self,
        *,
        node: Node,
        source_refs: list[dict[str, Any]],
        source_results: list[SourceResult],
        old_status: str,
        new_status: str,
        confidence: Optional[float],
        checked_at: str,
        note: str,
    ) -> None:
        result_by_locator = {result.locator: result for result in source_results}
        for ref in source_refs:
            result = result_by_locator.get(str(ref.get("locator", "")))
            if result and result.status == ClaimStatus.VERIFIED and result.content_hash:
                ref["content_hash"] = result.content_hash
                ref["checked_at"] = checked_at

        node.data["source_refs"] = source_refs
        node.data["status"] = new_status
        node.data["confidence"] = confidence
        node.data["last_checked_at"] = checked_at
        node.data.setdefault("audit_history", []).append({
            "checked_at": checked_at,
            "old_status": old_status,
            "status": new_status,
            "by": self.auditor_id,
            "note": note,
            "source_hashes": {
                result.locator: result.content_hash
                for result in source_results
                if result.content_hash
            },
        })
        self.store.put_node(node)
        self._stamp_claim_evidence_links(node.address, source_results, checked_at)

    def _stamp_claim_evidence_links(
        self,
        claim_address: HypernetAddress,
        source_results: list[SourceResult],
        checked_at: str,
    ) -> None:
        links = []
        for relationship in ("supports", "contradicts"):
            links.extend(self.store.get_links_to(claim_address, relationship=relationship))
        links.extend(self.store.get_links_from(claim_address, relationship="cites"))
        if not links or not source_results:
            return

        for link in links:
            for result in source_results:
                link.evidence.append({
                    "type": "document" if result.locator_type in {"file", "ha"} else "assertion",
                    "reference": result.locator,
                    "confidence": self._confidence_for_status(result.status),
                    "content_hash": result.content_hash,
                    "checked_at": checked_at,
                    "method": result.method,
                    "status": result.status,
                })
            self.store.put_link(link)

    @staticmethod
    def _confidence_for_status(status: str) -> Optional[float]:
        return {
            ClaimStatus.VERIFIED: 1.0,
            ClaimStatus.STALE: 0.4,
            ClaimStatus.BROKEN: 0.2,
            ClaimStatus.CONTRADICTED: 0.0,
            ClaimStatus.UNVERIFIED: None,
        }[status]

    @staticmethod
    def _note_for_status(status: str) -> str:
        return {
            ClaimStatus.VERIFIED: "All audited sources support the claim.",
            ClaimStatus.UNVERIFIED: "No source could verify the claim.",
            ClaimStatus.STALE: "At least one source changed since prior verification.",
            ClaimStatus.BROKEN: "At least one previously verified source no longer resolves.",
            ClaimStatus.CONTRADICTED: "At least one audited source contradicts the claim.",
        }[status]


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Audit a Hypernet trust-ledger claim.")
    parser.add_argument("store_root", help="Path to a Hypernet Store root")
    parser.add_argument("claim_id", help="Claim Hypernet address to audit")
    parser.add_argument("--archive-root", default=".", help="Root used for relative file locators")
    args = parser.parse_args(argv)

    ledger = TrustLedger(Store(args.store_root), archive_root=args.archive_root)
    result = ledger.audit_claim(args.claim_id)
    print(json.dumps(result.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
