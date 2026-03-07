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
