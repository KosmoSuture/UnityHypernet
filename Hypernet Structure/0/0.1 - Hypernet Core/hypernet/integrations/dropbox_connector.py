"""
Dropbox Connector

Imports files from Dropbox into a Hypernet personal account.
Uses the Dropbox API v2 with OAuth2 for authentication and
cursor-based incremental sync for efficient updates.

Supports:
  - Full directory listing with recursive traversal
  - Incremental sync via Dropbox cursors (only fetch changes)
  - Content hash dedup (Dropbox provides content_hash)
  - File metadata extraction (size, modified, shared status)
  - Category-based import routing (documents, photos, etc.)

Usage:
    connector = DropboxConnector(archive_root, private_root)
    status = connector.authenticate()
    results = connector.run_full_import("1.local.1.6.1")
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .protocol import (
    BaseConnector, AuthStatus, ImportStatus,
    RawItem, ImportResult, ScanResult,
)

log = logging.getLogger(__name__)

# File extensions we care about (skip system files, caches, etc.)
SKIP_EXTENSIONS = {".tmp", ".crdownload", ".part", ".bak", ".swp"}

# Map Dropbox paths to Hypernet categories
CATEGORY_MAP = {
    "document": {"pdf", "docx", "doc", "txt", "md", "rtf", "odt", "pages", "tex", "epub", "xlsx", "xls", "csv", "pptx", "ppt"},
    "photo": {"jpg", "jpeg", "png", "gif", "webp", "heic", "bmp", "tiff", "tif", "raw", "cr2", "nef"},
    "video": {"mp4", "mov", "avi", "mkv", "wmv", "flv", "webm", "m4v"},
    "audio": {"mp3", "wav", "flac", "aac", "ogg", "wma", "m4a"},
    "code": {"py", "js", "ts", "html", "css", "java", "cpp", "c", "go", "rs", "rb"},
    "data": {"json", "xml", "yaml", "yml", "toml", "sql"},
}

EXT_TO_CATEGORY = {}
for cat, exts in CATEGORY_MAP.items():
    for ext in exts:
        EXT_TO_CATEGORY[ext] = cat

# Hypernet address suffixes per category
CATEGORY_ADDRESS = {
    "document": "2",
    "photo": "8.0",
    "video": "8.1",
    "audio": "8.2",
    "code": "7.0",
    "data": "6.0",
}


class DropboxConnector(BaseConnector):
    """Imports files from Dropbox into the Hypernet."""

    source_type = "cloud_storage"
    source_name = "Dropbox"

    def __init__(self, archive_root: str, private_root: str):
        super().__init__(archive_root, private_root)
        self._token_path = self.token_dir / "dropbox.json"
        self._cursor_path = self.staging_dir / "_dropbox_cursor.json"
        self._access_token: str = ""
        self._refresh_token: str = ""
        self._app_key: str = ""
        self._app_secret: str = ""
        self._cursor: str = ""
        self._load_tokens()
        self._load_cursor()

    def _load_tokens(self) -> None:
        """Load saved OAuth tokens."""
        if self._token_path.exists():
            try:
                data = json.loads(self._token_path.read_text(encoding="utf-8"))
                self._access_token = data.get("access_token", "")
                self._refresh_token = data.get("refresh_token", "")
                self._app_key = data.get("app_key", "")
                self._app_secret = data.get("app_secret", "")
            except (json.JSONDecodeError, OSError):
                pass

        # Also check app credentials file
        app_path = self.credentials_dir / "dropbox_app.json"
        if app_path.exists():
            try:
                data = json.loads(app_path.read_text(encoding="utf-8"))
                self._app_key = data.get("app_key", self._app_key)
                self._app_secret = data.get("app_secret", self._app_secret)
            except (json.JSONDecodeError, OSError):
                pass

    def _save_tokens(self) -> None:
        """Persist OAuth tokens."""
        self.token_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "access_token": self._access_token,
            "refresh_token": self._refresh_token,
            "app_key": self._app_key,
            "app_secret": self._app_secret,
            "updated": datetime.now(timezone.utc).isoformat(),
        }
        self._token_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _load_cursor(self) -> None:
        """Load saved sync cursor for incremental sync."""
        if self._cursor_path.exists():
            try:
                data = json.loads(self._cursor_path.read_text(encoding="utf-8"))
                self._cursor = data.get("cursor", "")
            except (json.JSONDecodeError, OSError):
                pass

    def _save_cursor(self) -> None:
        """Persist sync cursor."""
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "cursor": self._cursor,
            "updated": datetime.now(timezone.utc).isoformat(),
        }
        self._cursor_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def authenticate(self) -> AuthStatus:
        """Check if we have valid Dropbox credentials."""
        if not self._app_key:
            return AuthStatus.NOT_CONFIGURED

        if not self._access_token:
            if self._refresh_token:
                # Try to refresh the token
                try:
                    self._refresh_access_token()
                    return AuthStatus.AUTHENTICATED
                except Exception as e:
                    log.warning("Dropbox token refresh failed: %s", e)
                    return AuthStatus.EXPIRED
            return AuthStatus.CONFIGURED  # Has app key but no tokens yet

        # Test the token with a simple API call
        try:
            import httpx
            resp = httpx.post(
                "https://api.dropboxapi.com/2/users/get_current_account",
                headers={"Authorization": f"Bearer {self._access_token}"},
                timeout=10,
            )
            if resp.status_code == 200:
                return AuthStatus.AUTHENTICATED
            elif resp.status_code == 401:
                # Try refresh
                if self._refresh_token:
                    self._refresh_access_token()
                    return AuthStatus.AUTHENTICATED
                return AuthStatus.EXPIRED
            else:
                return AuthStatus.FAILED
        except ImportError:
            log.warning("httpx not installed — cannot verify Dropbox auth")
            return AuthStatus.CONFIGURED  # Assume configured if we have token
        except Exception as e:
            log.warning("Dropbox auth check failed: %s", e)
            return AuthStatus.FAILED

    def _refresh_access_token(self) -> None:
        """Refresh the Dropbox access token using the refresh token."""
        import httpx
        resp = httpx.post(
            "https://api.dropboxapi.com/oauth2/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
                "client_id": self._app_key,
                "client_secret": self._app_secret,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        self._access_token = data["access_token"]
        if "refresh_token" in data:
            self._refresh_token = data["refresh_token"]
        self._save_tokens()
        log.info("Dropbox access token refreshed")

    def _api_call(self, endpoint: str, data: dict = None, retries: int = 3) -> dict:
        """Make a Dropbox API call with retry and token refresh."""
        import httpx

        for attempt in range(retries):
            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json",
            }
            resp = httpx.post(
                f"https://api.dropboxapi.com/2/{endpoint}",
                headers=headers,
                json=data or {},
                timeout=30,
            )

            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 401 and self._refresh_token:
                self._refresh_access_token()
                continue
            elif resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", "5"))
                log.warning("Dropbox rate limited, waiting %ds", retry_after)
                time.sleep(retry_after)
                continue
            else:
                resp.raise_for_status()

        raise RuntimeError(f"Dropbox API call failed after {retries} retries: {endpoint}")

    def scan(self, since: Optional[datetime] = None, max_items: int = 1000) -> ScanResult:
        """Scan Dropbox for files to import.

        Uses cursor-based incremental sync if a cursor exists from a previous scan.
        Falls back to full listing if no cursor is available.
        """
        items: list[RawItem] = []
        total = 0
        has_more = True

        try:
            if self._cursor:
                # Incremental sync — only get changes since last cursor
                result = self._api_call("files/list_folder/continue", {"cursor": self._cursor})
            else:
                # Full listing
                result = self._api_call("files/list_folder", {
                    "path": "",
                    "recursive": True,
                    "include_deleted": False,
                    "limit": min(max_items, 2000),
                })

            while True:
                for entry in result.get("entries", []):
                    if entry[".tag"] != "file":
                        continue

                    total += 1
                    item = self._entry_to_raw_item(entry)
                    if item is None:
                        continue

                    # Filter by date if requested
                    if since and item.timestamp and item.timestamp < since:
                        continue

                    if not self.is_duplicate(item):
                        items.append(item)

                    if len(items) >= max_items:
                        break

                # Save cursor for next incremental sync
                if "cursor" in result:
                    self._cursor = result["cursor"]
                    self._save_cursor()

                if not result.get("has_more", False) or len(items) >= max_items:
                    break

                result = self._api_call("files/list_folder/continue", {"cursor": self._cursor})

        except Exception as e:
            log.error("Dropbox scan failed: %s", e)
            return ScanResult(
                source_platform="dropbox",
                total_found=total,
                new_items=len(items),
                errors=1,
                items=items,
            )

        return ScanResult(
            source_platform="dropbox",
            total_found=total,
            new_items=len(items),
            duplicates=total - len(items),
            items=items,
        )

    def _entry_to_raw_item(self, entry: dict) -> Optional[RawItem]:
        """Convert a Dropbox file entry to a RawItem."""
        name = entry.get("name", "")
        path = entry.get("path_display", entry.get("path_lower", ""))

        # Skip hidden/system files
        if name.startswith("."):
            return None

        # Get extension and category
        ext = Path(name).suffix.lower().lstrip(".")
        if f".{ext}" in SKIP_EXTENSIONS:
            return None

        category = EXT_TO_CATEGORY.get(ext, "document")

        # Parse timestamp
        timestamp = None
        if "client_modified" in entry:
            try:
                timestamp = datetime.fromisoformat(
                    entry["client_modified"].replace("Z", "+00:00")
                )
            except (ValueError, TypeError):
                pass
        if not timestamp and "server_modified" in entry:
            try:
                timestamp = datetime.fromisoformat(
                    entry["server_modified"].replace("Z", "+00:00")
                )
            except (ValueError, TypeError):
                pass

        # Use Dropbox content_hash for dedup (more reliable than our own)
        content_hash = entry.get("content_hash", "")

        item = RawItem(
            source_type=category,
            source_id=entry.get("id", path),
            source_platform="dropbox",
            timestamp=timestamp,
            title=name,
            content=path,
            metadata={
                "dropbox_path": path,
                "dropbox_id": entry.get("id", ""),
                "size_bytes": entry.get("size", 0),
                "content_hash": content_hash,
                "extension": ext,
                "category": category,
                "is_downloadable": entry.get("is_downloadable", True),
                "sharing_info": entry.get("sharing_info"),
            },
        )

        # Use Dropbox content_hash as our hash if available
        if content_hash:
            item.content_hash = content_hash
        else:
            item.compute_hash()

        return item

    def import_item(self, item: RawItem, target_address: str) -> ImportResult:
        """Import a Dropbox file reference as a Hypernet node.

        Creates metadata node referencing the Dropbox file. Does NOT download
        the file — it stays on Dropbox. The node contains enough metadata to
        download on demand later.
        """
        try:
            category = item.metadata.get("category", "document")
            cat_suffix = CATEGORY_ADDRESS.get(category, "2")

            node_data = {
                "title": item.title,
                "source_type": item.source_type,
                "source_platform": "dropbox",
                "dropbox_path": item.metadata.get("dropbox_path", ""),
                "dropbox_id": item.metadata.get("dropbox_id", ""),
                "file_size": item.metadata.get("size_bytes", 0),
                "file_extension": item.metadata.get("extension", ""),
                "content_hash": item.content_hash,
                "timestamp": item.timestamp.isoformat() if item.timestamp else None,
                "category": category,
                "imported_at": datetime.now(timezone.utc).isoformat(),
            }

            # Stage for later Store.put_node()
            stage_path = self.staging_dir / f"{item.content_hash[:16]}.json"
            stage_path.parent.mkdir(parents=True, exist_ok=True)
            stage_path.write_text(
                json.dumps({
                    "target_address": target_address,
                    "category_suffix": cat_suffix,
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

    def download_file(self, dropbox_path: str, local_path: str) -> bool:
        """Download a file from Dropbox to a local path.

        This is for on-demand download when a user wants the actual file,
        not called during normal import (which only creates metadata nodes).
        """
        import httpx

        try:
            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Dropbox-API-Arg": json.dumps({"path": dropbox_path}),
            }
            with httpx.stream("POST", "https://content.dropboxapi.com/2/files/download",
                              headers=headers, timeout=60) as resp:
                resp.raise_for_status()
                Path(local_path).parent.mkdir(parents=True, exist_ok=True)
                with open(local_path, "wb") as f:
                    for chunk in resp.iter_bytes(chunk_size=8192):
                        f.write(chunk)
            return True
        except Exception as e:
            log.error("Failed to download %s: %s", dropbox_path, e)
            return False

    def get_category_for_file(self, filename: str) -> str:
        """Get the Hypernet category for a filename."""
        ext = Path(filename).suffix.lower().lstrip(".")
        return EXT_TO_CATEGORY.get(ext, "document")
