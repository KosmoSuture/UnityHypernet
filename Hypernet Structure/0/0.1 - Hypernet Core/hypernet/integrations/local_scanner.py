"""
Local File Scanner Connector

Imports files from local directories into a Hypernet personal account.
This is the simplest connector — no authentication needed, just point it
at a directory and it scans for documents, photos, and media.

Supports:
  - Documents: .pdf, .docx, .txt, .md, .rtf, .odt
  - Photos: .jpg, .jpeg, .png, .gif, .webp, .heic, .bmp, .tiff
  - Media: .mp3, .mp4, .wav, .mov, .avi, .mkv
  - Data: .csv, .json, .xml, .xlsx

Usage:
    scanner = LocalFileScanner(archive_root, private_root)
    scanner.configure(scan_dirs=["/home/user/Documents", "/home/user/Photos"])
    results = scanner.run_full_import("1.local.1.6.1")
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .protocol import (
    BaseConnector, AuthStatus, ImportStatus,
    RawItem, ImportResult, ScanResult,
)

log = logging.getLogger(__name__)

# File type categories
FILE_CATEGORIES = {
    "document": {".pdf", ".docx", ".doc", ".txt", ".md", ".rtf", ".odt", ".pages", ".tex", ".epub"},
    "photo": {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".bmp", ".tiff", ".tif", ".raw", ".cr2", ".nef"},
    "video": {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm", ".m4v"},
    "audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"},
    "data": {".csv", ".json", ".xml", ".xlsx", ".xls", ".yaml", ".yml", ".toml"},
    "code": {".py", ".js", ".ts", ".html", ".css", ".java", ".cpp", ".c", ".go", ".rs", ".rb"},
}

# Reverse lookup: extension → category
EXT_TO_CATEGORY = {}
for cat, exts in FILE_CATEGORIES.items():
    for ext in exts:
        EXT_TO_CATEGORY[ext] = cat

# Category → Hypernet sub-address mapping
CATEGORY_ADDRESS = {
    "document": "2",    # Documents & Files
    "photo": "6.1",     # Media Objects
    "video": "6.1",     # Media Objects
    "audio": "6.1",     # Media Objects
    "data": "2",        # Documents & Files
    "code": "1",        # Projects & Work
}


class LocalFileScanner(BaseConnector):
    """Scans local directories and imports files into Hypernet."""

    source_type = "local_file"
    source_name = "Local Files"

    def __init__(self, archive_root: str, private_root: str):
        super().__init__(archive_root, private_root)
        self.scan_dirs: list[Path] = []
        self.exclude_patterns: list[str] = [
            ".git", "__pycache__", "node_modules", ".venv",
            ".env", "venv", ".idea", ".vscode", ".DS_Store",
        ]
        self.max_file_size_mb: float = 100.0
        self._config_path = self.private_root / "connectors" / "local_scanner.json"
        self._load_config()

    def _load_config(self) -> None:
        """Load scanner configuration."""
        if self._config_path.exists():
            try:
                data = json.loads(self._config_path.read_text(encoding="utf-8"))
                self.scan_dirs = [Path(d) for d in data.get("scan_dirs", [])]
                self.exclude_patterns = data.get("exclude_patterns", self.exclude_patterns)
                self.max_file_size_mb = data.get("max_file_size_mb", self.max_file_size_mb)
            except (json.JSONDecodeError, OSError) as e:
                log.warning("Failed to load scanner config: %s", e)

    def _save_config(self) -> None:
        """Persist scanner configuration."""
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "scan_dirs": [str(d) for d in self.scan_dirs],
            "exclude_patterns": self.exclude_patterns,
            "max_file_size_mb": self.max_file_size_mb,
            "updated": datetime.now(timezone.utc).isoformat(),
        }
        self._config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def configure(self, scan_dirs: list[str], exclude: list[str] = None,
                  max_size_mb: float = None) -> None:
        """Configure which directories to scan."""
        self.scan_dirs = [Path(d) for d in scan_dirs]
        if exclude is not None:
            self.exclude_patterns = exclude
        if max_size_mb is not None:
            self.max_file_size_mb = max_size_mb
        self._save_config()

    def authenticate(self) -> AuthStatus:
        """Check that scan directories exist and are readable."""
        if not self.scan_dirs:
            return AuthStatus.NOT_CONFIGURED

        for d in self.scan_dirs:
            if not d.exists():
                log.warning("Scan directory does not exist: %s", d)
                return AuthStatus.FAILED
            if not os.access(d, os.R_OK):
                log.warning("Scan directory not readable: %s", d)
                return AuthStatus.FAILED

        return AuthStatus.AUTHENTICATED

    def scan(self, since: Optional[datetime] = None, max_items: int = 1000) -> ScanResult:
        """Scan configured directories for importable files."""
        items: list[RawItem] = []
        total = 0
        max_bytes = self.max_file_size_mb * 1024 * 1024

        for scan_dir in self.scan_dirs:
            if not scan_dir.exists():
                continue

            for filepath in self._walk_directory(scan_dir):
                total += 1

                # Skip files that are too large
                try:
                    size = filepath.stat().st_size
                    if size > max_bytes:
                        continue
                except OSError:
                    continue

                # Get file category
                ext = filepath.suffix.lower()
                category = EXT_TO_CATEGORY.get(ext)
                if not category:
                    continue  # Skip unsupported file types

                # Check modification time
                try:
                    mtime = datetime.fromtimestamp(filepath.stat().st_mtime, tz=timezone.utc)
                except OSError:
                    continue

                if since and mtime < since:
                    continue

                # Create RawItem
                item = RawItem(
                    source_type=category,
                    source_id=str(filepath),
                    source_platform="local",
                    timestamp=mtime,
                    title=filepath.name,
                    content=str(filepath),
                    metadata={
                        "path": str(filepath),
                        "extension": ext,
                        "size_bytes": size,
                        "category": category,
                        "relative_path": str(filepath.relative_to(scan_dir)) if filepath.is_relative_to(scan_dir) else str(filepath),
                    },
                )
                item.compute_hash()

                if not self.is_duplicate(item):
                    items.append(item)

                if len(items) >= max_items:
                    break

        # Compute dedup stats
        new_count = len(items)
        dup_count = total - new_count

        return ScanResult(
            source_platform="local",
            total_found=total,
            new_items=new_count,
            duplicates=dup_count,
            items=items,
        )

    def import_item(self, item: RawItem, target_address: str) -> ImportResult:
        """Import a local file as a Hypernet node.

        Creates the node metadata (not a copy of the file — the file stays
        in place and the node references it).
        """
        filepath = Path(item.metadata.get("path", item.source_id))

        if not filepath.exists():
            return ImportResult(
                source_id=item.source_id,
                status=ImportStatus.FAILED,
                error=f"File not found: {filepath}",
            )

        try:
            # Build node data
            stat = filepath.stat()
            node_data = {
                "title": item.title,
                "source_type": item.source_type,
                "source_platform": "local",
                "source_path": str(filepath),
                "file_extension": item.metadata.get("extension", ""),
                "file_size": stat.st_size,
                "timestamp": item.timestamp.isoformat() if item.timestamp else None,
                "content_hash": item.content_hash,
                "imported_at": datetime.now(timezone.utc).isoformat(),
            }

            # Extract basic metadata based on type
            if item.source_type == "photo":
                node_data["media_type"] = "image"
            elif item.source_type == "video":
                node_data["media_type"] = "video"
            elif item.source_type == "audio":
                node_data["media_type"] = "audio"
            elif item.source_type == "document":
                node_data["media_type"] = "document"

            # Stage the node data for later Store.put_node()
            stage_path = self.staging_dir / f"{item.content_hash[:16]}.json"
            stage_path.parent.mkdir(parents=True, exist_ok=True)
            stage_path.write_text(
                json.dumps({
                    "target_address": target_address,
                    "data": node_data,
                }, indent=2),
                encoding="utf-8",
            )

            return ImportResult(
                source_id=item.source_id,
                status=ImportStatus.IMPORTED,
                hypernet_address=target_address,
            )

        except Exception as e:
            return ImportResult(
                source_id=item.source_id,
                status=ImportStatus.FAILED,
                error=str(e),
            )

    def _walk_directory(self, root: Path):
        """Walk directory tree, skipping excluded patterns."""
        try:
            for entry in root.iterdir():
                # Skip excluded patterns
                if any(pat in entry.name for pat in self.exclude_patterns):
                    continue

                if entry.is_file():
                    yield entry
                elif entry.is_dir():
                    yield from self._walk_directory(entry)
        except PermissionError:
            log.debug("Permission denied: %s", root)
        except OSError as e:
            log.debug("Error walking %s: %s", root, e)

    def get_category_address(self, category: str) -> str:
        """Get the Hypernet sub-address for a file category."""
        return CATEGORY_ADDRESS.get(category, "2")  # Default to Documents
