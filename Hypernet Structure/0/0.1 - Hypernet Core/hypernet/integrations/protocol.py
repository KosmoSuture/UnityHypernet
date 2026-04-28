"""
Universal Connector Protocol

Defines the interface that all data connectors must implement.
Each connector handles authentication, scanning, importing, and
deduplication for a specific data source.

This protocol enables:
- Uniform import pipeline across all data sources
- Swarm task generation (each scan/import becomes a task)
- Progress tracking through the dashboard
- Consistent error handling and retry logic

Usage:
    class GmailConnector(BaseConnector):
        source_type = "email"
        source_name = "Gmail"
        ...
"""

from __future__ import annotations

import hashlib
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger(__name__)


class AuthStatus(Enum):
    """Authentication state for a connector."""
    NOT_CONFIGURED = "not_configured"
    CONFIGURED = "configured"
    AUTHENTICATED = "authenticated"
    EXPIRED = "expired"
    FAILED = "failed"


class ImportStatus(Enum):
    """Status of an individual item import."""
    PENDING = "pending"
    IMPORTED = "imported"
    SKIPPED = "skipped"
    DUPLICATE = "duplicate"
    FAILED = "failed"


@dataclass
class RawItem:
    """A raw item from an external source, before Hypernet import.

    This is the universal intermediate format. Connectors convert their
    source-specific data into RawItems, which the import pipeline then
    converts into Hypernet Nodes.
    """
    source_type: str          # e.g., "email", "photo", "social_post"
    source_id: str            # Unique ID from the source platform
    source_platform: str      # e.g., "gmail", "instagram", "local"
    timestamp: Optional[datetime] = None
    title: str = ""
    content: str = ""
    metadata: dict = field(default_factory=dict)
    attachments: list[str] = field(default_factory=list)
    raw_data: Optional[dict] = None
    content_hash: str = ""    # SHA-256 of content for dedup

    def compute_hash(self) -> str:
        """Compute content hash for deduplication."""
        hasher = hashlib.sha256()
        hasher.update(self.source_type.encode())
        hasher.update(self.source_id.encode())
        hasher.update(self.content.encode())
        self.content_hash = hasher.hexdigest()
        return self.content_hash


@dataclass
class ImportResult:
    """Result of importing a single item."""
    source_id: str
    status: ImportStatus
    hypernet_address: str = ""
    error: str = ""
    duration_seconds: float = 0.0


@dataclass
class ScanResult:
    """Result of scanning a data source."""
    source_platform: str
    total_found: int = 0
    new_items: int = 0
    duplicates: int = 0
    errors: int = 0
    items: list[RawItem] = field(default_factory=list)
    duration_seconds: float = 0.0

    def summary(self) -> dict:
        """Return a summary without the full item list."""
        return {
            "source": self.source_platform,
            "total": self.total_found,
            "new": self.new_items,
            "duplicates": self.duplicates,
            "errors": self.errors,
            "duration_s": round(self.duration_seconds, 2),
        }


@dataclass
class TypedNodeSpec:
    """A typed Hypernet node to materialize during import."""

    address: str
    type_address: str
    data: dict[str, Any] = field(default_factory=dict)
    source_type: str = ""
    source_id: str = ""
    creator: str = ""


@dataclass
class TypedLinkSpec:
    """A typed Hypernet link to materialize during import."""

    from_address: str
    to_address: str
    relationship: str
    link_type: str
    data: dict[str, Any] = field(default_factory=dict)
    strength: float = 1.0
    bidirectional: bool = False


@dataclass
class GraphImportBatch:
    """A batch of typed nodes and links imported from one source."""

    source_platform: str
    import_id: str = ""
    nodes: list[TypedNodeSpec] = field(default_factory=list)
    links: list[TypedLinkSpec] = field(default_factory=list)


@dataclass
class GraphImportResult:
    """Outcome of applying a typed graph import batch."""

    source_platform: str
    status: ImportStatus
    import_id: str = ""
    node_addresses: list[str] = field(default_factory=list)
    link_hashes: list[str] = field(default_factory=list)
    nodes_imported: int = 0
    links_imported: int = 0
    nodes_skipped: int = 0
    links_skipped: int = 0
    errors: list[str] = field(default_factory=list)
    validations: list[dict[str, Any]] = field(default_factory=list)
    duration_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


class GraphImportPipeline:
    """Materialize typed import batches into a Store.

    Connectors can keep source-specific scanning/authentication while
    sharing this final graph write step. The pipeline validates the whole
    batch first, then writes nodes before links through normal Store APIs.
    """

    VALIDATION_MODES = {"off", "warn", "strict"}

    def __init__(self, store):
        self.store = store

    def import_batch(
        self,
        batch: GraphImportBatch,
        *,
        validation_mode: str = "warn",
        upsert: bool = True,
        dry_run: bool = False,
    ) -> GraphImportResult:
        import time

        mode = validation_mode if validation_mode in self.VALIDATION_MODES else "warn"
        start = time.time()
        result = GraphImportResult(
            source_platform=batch.source_platform,
            import_id=batch.import_id,
            status=ImportStatus.PENDING,
        )

        node_records = []
        link_records = []
        try:
            node_records = self._prepare_nodes(batch, result, mode, upsert=upsert)
            link_records = self._prepare_links(batch, result, mode, upsert=upsert)
        except Exception as exc:
            result.errors.append(str(exc))

        if result.errors:
            result.status = ImportStatus.FAILED
            result.duration_seconds = time.time() - start
            return result

        if dry_run:
            result.status = ImportStatus.SKIPPED
            result.duration_seconds = time.time() - start
            return result

        for node in node_records:
            self.store.put_node(node)
            result.node_addresses.append(str(node.address))
            result.nodes_imported += 1

        for link in link_records:
            link_hash = self.store.put_link(link)
            result.link_hashes.append(link_hash)
            result.links_imported += 1

        if result.nodes_imported or result.links_imported:
            result.status = ImportStatus.IMPORTED
        elif result.nodes_skipped or result.links_skipped:
            result.status = ImportStatus.SKIPPED
        else:
            result.status = ImportStatus.PENDING
        result.duration_seconds = time.time() - start
        return result

    def _prepare_nodes(
        self,
        batch: GraphImportBatch,
        result: GraphImportResult,
        mode: str,
        *,
        upsert: bool,
    ) -> list:
        from ..address import HypernetAddress
        from ..node import Node
        from ..object_schema import validate_object_payload

        nodes = []
        for spec in batch.nodes:
            address = HypernetAddress.parse(spec.address)
            existing = self.store.get_node(address)
            if existing is not None and not upsert:
                result.nodes_skipped += 1
                continue

            type_address = HypernetAddress.parse(spec.type_address) if spec.type_address else None
            data = dict(spec.data or {})
            if batch.source_platform:
                data.setdefault("source_platform", batch.source_platform)
            if batch.import_id:
                data.setdefault("import_id", batch.import_id)

            source_type = spec.source_type or batch.source_platform or "import"
            source_id = spec.source_id or spec.address
            if mode != "off" and type_address is not None:
                validation = validate_object_payload(str(type_address), data)
                validation.update({
                    "address": str(address),
                    "mode": mode,
                    "kind": "node",
                })
                result.validations.append(validation)
                if mode == "strict" and not validation["valid"]:
                    result.errors.append(
                        f"Node {address} failed object validation: {validation['issues']}"
                    )

            nodes.append(Node(
                address=address,
                type_address=type_address,
                data=data,
                source_type=source_type,
                source_id=source_id,
                creator=HypernetAddress.parse(spec.creator) if spec.creator else None,
            ))
        return nodes

    def _prepare_links(
        self,
        batch: GraphImportBatch,
        result: GraphImportResult,
        mode: str,
        *,
        upsert: bool,
    ) -> list:
        from ..address import HypernetAddress
        from ..link import Link, LinkRegistry

        registry = LinkRegistry(self.store)
        links = []
        for spec in batch.links:
            from_address = HypernetAddress.parse(spec.from_address)
            to_address = HypernetAddress.parse(spec.to_address)
            if not upsert:
                existing = self.store.get_links_from(from_address, relationship=spec.relationship)
                if any(str(link.to_address) == str(to_address) and link.link_type == spec.link_type for link in existing):
                    result.links_skipped += 1
                    continue

            data = dict(spec.data or {})
            if batch.source_platform:
                data.setdefault("source_platform", batch.source_platform)
            if batch.import_id:
                data.setdefault("import_id", batch.import_id)
            link = Link(
                from_address=from_address,
                to_address=to_address,
                relationship=spec.relationship,
                link_type=spec.link_type,
                data=data,
                strength=float(spec.strength),
                bidirectional=bool(spec.bidirectional),
                creation_method="import",
            )
            if mode != "off":
                issues = registry.validate_link(link) + registry.validate_link_endpoints(link)
                validation = {
                    "kind": "link",
                    "from_address": spec.from_address,
                    "to_address": spec.to_address,
                    "relationship": spec.relationship,
                    "link_type": spec.link_type,
                    "mode": mode,
                    "valid": not issues,
                    "issues": issues,
                }
                result.validations.append(validation)
                if mode == "strict" and issues:
                    result.errors.append(
                        f"Link {spec.from_address}->{spec.to_address} failed validation: {issues}"
                    )
            links.append(link)
        return links


@dataclass
class ConnectorStatus:
    """Current status of a connector."""
    source_platform: str
    auth_status: AuthStatus
    last_scan: Optional[datetime] = None
    items_imported: int = 0
    items_pending: int = 0
    error: str = ""

    def to_dict(self) -> dict:
        return {
            "platform": self.source_platform,
            "auth": self.auth_status.value,
            "last_scan": self.last_scan.isoformat() if self.last_scan else None,
            "imported": self.items_imported,
            "pending": self.items_pending,
            "error": self.error,
        }


class BaseConnector(ABC):
    """Base class for all data connectors.

    Subclasses must implement:
        - source_type: str (e.g., "email", "photo")
        - source_name: str (e.g., "Gmail", "Google Photos")
        - authenticate() -> AuthStatus
        - scan() -> ScanResult
        - import_item(item: RawItem) -> ImportResult

    Optional overrides:
        - deduplicate(items) -> list[RawItem]
        - get_status() -> ConnectorStatus
        - export_item(address: str) -> bool
    """

    source_type: str = ""
    source_name: str = ""

    def __init__(self, archive_root: str, private_root: str):
        self.archive_root = Path(archive_root)
        self.private_root = Path(private_root)
        self.credentials_dir = self.private_root / "credentials"
        self.token_dir = self.private_root / "oauth-tokens"
        self.staging_dir = self.private_root / "import-staging" / self.source_type
        self._imported_hashes: set[str] = set()
        self._load_dedup_index()

    def _dedup_index_path(self) -> Path:
        return self.staging_dir / "_dedup_index.json"

    def _load_dedup_index(self) -> None:
        """Load the set of already-imported content hashes."""
        idx_path = self._dedup_index_path()
        if idx_path.exists():
            try:
                data = json.loads(idx_path.read_text(encoding="utf-8"))
                self._imported_hashes = set(data.get("hashes", []))
            except (json.JSONDecodeError, OSError):
                self._imported_hashes = set()

    def _save_dedup_index(self) -> None:
        """Persist the dedup index."""
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        data = {"hashes": sorted(self._imported_hashes), "updated": datetime.now(timezone.utc).isoformat()}
        self._dedup_index_path().write_text(json.dumps(data), encoding="utf-8")

    def is_duplicate(self, item: RawItem) -> bool:
        """Check if an item has already been imported."""
        if not item.content_hash:
            item.compute_hash()
        return item.content_hash in self._imported_hashes

    def mark_imported(self, item: RawItem) -> None:
        """Mark an item as imported in the dedup index."""
        if not item.content_hash:
            item.compute_hash()
        self._imported_hashes.add(item.content_hash)

    @abstractmethod
    def authenticate(self) -> AuthStatus:
        """Authenticate with the data source. Returns auth status."""
        ...

    @abstractmethod
    def scan(self, since: Optional[datetime] = None, max_items: int = 1000) -> ScanResult:
        """Scan the data source for items to import.

        Args:
            since: Only return items newer than this timestamp
            max_items: Maximum items to return in one scan
        """
        ...

    @abstractmethod
    def import_item(self, item: RawItem, target_address: str) -> ImportResult:
        """Import a single item into the Hypernet at the given address.

        Args:
            item: The raw item to import
            target_address: Hypernet address to store the item at
        """
        ...

    def deduplicate(self, items: list[RawItem]) -> list[RawItem]:
        """Filter out items that have already been imported.

        Default implementation uses content hashing. Override for
        platform-specific dedup (e.g., perceptual hashing for photos).
        """
        unique = []
        for item in items:
            if not self.is_duplicate(item):
                unique.append(item)
        return unique

    def get_status(self) -> ConnectorStatus:
        """Return current connector status."""
        return ConnectorStatus(
            source_platform=self.source_name,
            auth_status=self.authenticate(),
            items_imported=len(self._imported_hashes),
        )

    def run_full_import(self, target_prefix: str, since: Optional[datetime] = None,
                        max_items: int = 1000) -> list[ImportResult]:
        """Convenience: scan → deduplicate → import all new items.

        Args:
            target_prefix: Base Hypernet address (e.g., "1.local.1.3.0")
            since: Only import items newer than this
            max_items: Max items per run
        """
        import time

        log.info("[%s] Starting full import to %s", self.source_name, target_prefix)

        # Authenticate
        auth = self.authenticate()
        if auth not in (AuthStatus.AUTHENTICATED, AuthStatus.CONFIGURED):
            log.error("[%s] Authentication failed: %s", self.source_name, auth.value)
            return []

        # Scan
        scan_result = self.scan(since=since, max_items=max_items)
        log.info("[%s] Scan found %d items (%d new)",
                 self.source_name, scan_result.total_found, scan_result.new_items)

        # Deduplicate
        unique_items = self.deduplicate(scan_result.items)
        log.info("[%s] After dedup: %d items to import", self.source_name, len(unique_items))

        # Import
        results = []
        for i, item in enumerate(unique_items):
            start = time.time()
            address = f"{target_prefix}.{item.source_id}"
            try:
                result = self.import_item(item, address)
                result.duration_seconds = time.time() - start
                if result.status == ImportStatus.IMPORTED:
                    self.mark_imported(item)
                results.append(result)
            except Exception as e:
                results.append(ImportResult(
                    source_id=item.source_id,
                    status=ImportStatus.FAILED,
                    error=str(e),
                    duration_seconds=time.time() - start,
                ))

            # Save dedup index periodically
            if (i + 1) % 50 == 0:
                self._save_dedup_index()

        # Final save
        self._save_dedup_index()

        imported = sum(1 for r in results if r.status == ImportStatus.IMPORTED)
        failed = sum(1 for r in results if r.status == ImportStatus.FAILED)
        log.info("[%s] Import complete: %d imported, %d failed",
                 self.source_name, imported, failed)

        return results
