"""
OneDrive / Microsoft Graph Connector

Imports files from OneDrive into a Hypernet personal account.
Uses Microsoft Graph API with MSAL OAuth2 authentication and
delta queries for efficient incremental sync.

Supports:
  - Full directory listing with recursive traversal
  - Delta queries (only fetch changes since last sync)
  - Content hash dedup (OneDrive provides SHA-256 and QuickXor hashes)
  - Rich metadata (photo EXIF, GPS, sharing info)
  - Category-based import routing

Usage:
    connector = OneDriveConnector(archive_root, private_root)
    status = connector.authenticate()
    results = connector.run_full_import("1.local.1.6.1")
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .protocol import (
    BaseConnector, AuthStatus, ImportStatus,
    RawItem, ImportResult, ScanResult,
)

log = logging.getLogger(__name__)

# Microsoft Graph API base
GRAPH_BASE = "https://graph.microsoft.com/v1.0"

# OAuth2 scopes needed
SCOPES = ["Files.Read", "Files.Read.All", "User.Read", "offline_access"]

# File extension categories (same as dropbox_connector)
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

CATEGORY_ADDRESS = {
    "document": "2",
    "photo": "8.0",
    "video": "8.1",
    "audio": "8.2",
    "code": "7.0",
    "data": "6.0",
}


class OneDriveConnector(BaseConnector):
    """Imports files from OneDrive/Microsoft 365 into the Hypernet."""

    source_type = "cloud_storage"
    source_name = "OneDrive"

    def __init__(self, archive_root: str, private_root: str):
        super().__init__(archive_root, private_root)
        self._token_path = self.token_dir / "onedrive.json"
        self._delta_path = self.staging_dir / "_onedrive_delta.json"
        self._config_path = self.credentials_dir / "microsoft_app.json"
        self._access_token: str = ""
        self._refresh_token: str = ""
        self._client_id: str = ""
        self._client_secret: str = ""
        self._tenant_id: str = "common"  # Multi-tenant by default
        self._delta_link: str = ""
        self._load_config()
        self._load_tokens()
        self._load_delta()

    def _load_config(self) -> None:
        """Load app registration config."""
        if self._config_path.exists():
            try:
                data = json.loads(self._config_path.read_text(encoding="utf-8"))
                self._client_id = data.get("client_id", "")
                self._client_secret = data.get("client_secret", "")
                self._tenant_id = data.get("tenant_id", "common")
            except (json.JSONDecodeError, OSError):
                pass

    def _load_tokens(self) -> None:
        """Load saved OAuth tokens."""
        if self._token_path.exists():
            try:
                data = json.loads(self._token_path.read_text(encoding="utf-8"))
                self._access_token = data.get("access_token", "")
                self._refresh_token = data.get("refresh_token", "")
            except (json.JSONDecodeError, OSError):
                pass

    def _save_tokens(self) -> None:
        """Persist OAuth tokens."""
        self.token_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "access_token": self._access_token,
            "refresh_token": self._refresh_token,
            "updated": datetime.now(timezone.utc).isoformat(),
        }
        self._token_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _load_delta(self) -> None:
        """Load saved delta link for incremental sync."""
        if self._delta_path.exists():
            try:
                data = json.loads(self._delta_path.read_text(encoding="utf-8"))
                self._delta_link = data.get("delta_link", "")
            except (json.JSONDecodeError, OSError):
                pass

    def _save_delta(self) -> None:
        """Persist delta link."""
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "delta_link": self._delta_link,
            "updated": datetime.now(timezone.utc).isoformat(),
        }
        self._delta_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def authenticate(self) -> AuthStatus:
        """Check if we have valid Microsoft Graph credentials."""
        if not self._client_id:
            return AuthStatus.NOT_CONFIGURED

        if not self._access_token:
            if self._refresh_token:
                try:
                    self._refresh_access_token()
                    return AuthStatus.AUTHENTICATED
                except Exception as e:
                    log.warning("OneDrive token refresh failed: %s", e)
                    return AuthStatus.EXPIRED
            return AuthStatus.CONFIGURED

        # Test the token
        try:
            import httpx
            resp = httpx.get(
                f"{GRAPH_BASE}/me",
                headers={"Authorization": f"Bearer {self._access_token}"},
                timeout=10,
            )
            if resp.status_code == 200:
                return AuthStatus.AUTHENTICATED
            elif resp.status_code == 401 and self._refresh_token:
                self._refresh_access_token()
                return AuthStatus.AUTHENTICATED
            else:
                return AuthStatus.EXPIRED
        except ImportError:
            return AuthStatus.CONFIGURED
        except Exception as e:
            log.warning("OneDrive auth check failed: %s", e)
            return AuthStatus.FAILED

    def _refresh_access_token(self) -> None:
        """Refresh the access token using MSAL or direct endpoint."""
        import httpx

        token_url = f"https://login.microsoftonline.com/{self._tenant_id}/oauth2/v2.0/token"
        resp = httpx.post(
            token_url,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "scope": " ".join(SCOPES),
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        self._access_token = data["access_token"]
        if "refresh_token" in data:
            self._refresh_token = data["refresh_token"]
        self._save_tokens()
        log.info("OneDrive access token refreshed")

    def _graph_get(self, url: str, retries: int = 3) -> dict:
        """Make a Microsoft Graph GET request with retry logic."""
        import httpx

        # Handle both full URLs and relative paths
        if not url.startswith("http"):
            url = f"{GRAPH_BASE}{url}"

        for attempt in range(retries):
            resp = httpx.get(
                url,
                headers={"Authorization": f"Bearer {self._access_token}"},
                timeout=30,
            )

            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 401 and self._refresh_token:
                self._refresh_access_token()
                continue
            elif resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", "5"))
                log.warning("OneDrive rate limited, waiting %ds", retry_after)
                time.sleep(retry_after)
                continue
            elif resp.status_code == 404:
                return {}
            else:
                resp.raise_for_status()

        raise RuntimeError(f"Graph API call failed after {retries} retries: {url}")

    def scan(self, since: Optional[datetime] = None, max_items: int = 1000) -> ScanResult:
        """Scan OneDrive for files to import.

        Uses delta queries for incremental sync if a delta link exists.
        Falls back to full listing if no delta link is available.
        """
        items: list[RawItem] = []
        total = 0

        try:
            if self._delta_link:
                # Incremental sync — only changes since last delta
                url = self._delta_link
            else:
                # Full listing via delta (which gives us all items + a delta link)
                url = "/me/drive/root/delta"

            while url:
                result = self._graph_get(url)

                for entry in result.get("value", []):
                    # Skip folders and deleted items
                    if "folder" in entry or entry.get("deleted"):
                        continue

                    total += 1
                    item = self._entry_to_raw_item(entry)
                    if item is None:
                        continue

                    if since and item.timestamp and item.timestamp < since:
                        continue

                    if not self.is_duplicate(item):
                        items.append(item)

                    if len(items) >= max_items:
                        break

                # Save delta link for next sync
                if "@odata.deltaLink" in result:
                    self._delta_link = result["@odata.deltaLink"]
                    self._save_delta()

                # Pagination
                url = result.get("@odata.nextLink", "")
                if len(items) >= max_items:
                    break

        except Exception as e:
            log.error("OneDrive scan failed: %s", e)
            return ScanResult(
                source_platform="onedrive",
                total_found=total,
                new_items=len(items),
                errors=1,
                items=items,
            )

        return ScanResult(
            source_platform="onedrive",
            total_found=total,
            new_items=len(items),
            duplicates=total - len(items),
            items=items,
        )

    def _entry_to_raw_item(self, entry: dict) -> Optional[RawItem]:
        """Convert a OneDrive drive item to a RawItem."""
        name = entry.get("name", "")
        if not name or name.startswith("."):
            return None

        # Get extension and category
        ext = Path(name).suffix.lower().lstrip(".")
        category = EXT_TO_CATEGORY.get(ext, "document")

        # Parse timestamps
        timestamp = None
        for time_field in ["lastModifiedDateTime", "createdDateTime"]:
            if time_field in entry:
                try:
                    timestamp = datetime.fromisoformat(
                        entry[time_field].replace("Z", "+00:00")
                    )
                    break
                except (ValueError, TypeError):
                    pass

        # Get content hash (OneDrive provides file hashes)
        file_info = entry.get("file", {})
        hashes = file_info.get("hashes", {})
        content_hash = hashes.get("sha256Hash", hashes.get("sha1Hash", hashes.get("quickXorHash", "")))

        # Build path from parentReference
        parent = entry.get("parentReference", {})
        parent_path = parent.get("path", "").replace("/drive/root:", "")
        full_path = f"{parent_path}/{name}" if parent_path else f"/{name}"

        # Extract photo/location metadata if available
        photo_meta = entry.get("photo", {})
        location_meta = entry.get("location", {})

        metadata = {
            "onedrive_id": entry.get("id", ""),
            "onedrive_path": full_path,
            "size_bytes": entry.get("size", 0),
            "extension": ext,
            "category": category,
            "mime_type": file_info.get("mimeType", ""),
            "web_url": entry.get("webUrl", ""),
        }

        # Add photo metadata if present
        if photo_meta:
            metadata["photo"] = {
                "camera_make": photo_meta.get("cameraMake", ""),
                "camera_model": photo_meta.get("cameraModel", ""),
                "taken_datetime": photo_meta.get("takenDateTime", ""),
                "iso": photo_meta.get("iso"),
                "focal_length": photo_meta.get("focalLength"),
                "exposure_numerator": photo_meta.get("exposureNumerator"),
                "exposure_denominator": photo_meta.get("exposureDenominator"),
            }
            # Use photo taken date as timestamp if available
            if photo_meta.get("takenDateTime"):
                try:
                    timestamp = datetime.fromisoformat(
                        photo_meta["takenDateTime"].replace("Z", "+00:00")
                    )
                except (ValueError, TypeError):
                    pass

        # Add location metadata if present
        if location_meta:
            metadata["location"] = {
                "latitude": location_meta.get("latitude"),
                "longitude": location_meta.get("longitude"),
                "altitude": location_meta.get("altitude"),
            }

        item = RawItem(
            source_type=category,
            source_id=entry.get("id", full_path),
            source_platform="onedrive",
            timestamp=timestamp,
            title=name,
            content=full_path,
            metadata=metadata,
        )

        if content_hash:
            item.content_hash = content_hash
        else:
            item.compute_hash()

        return item

    def import_item(self, item: RawItem, target_address: str) -> ImportResult:
        """Import a OneDrive file reference as a Hypernet node.

        Creates metadata node referencing the OneDrive file. Does NOT download
        the file — it stays on OneDrive. The node contains enough metadata to
        download on demand later.
        """
        try:
            category = item.metadata.get("category", "document")
            cat_suffix = CATEGORY_ADDRESS.get(category, "2")

            node_data = {
                "title": item.title,
                "source_type": item.source_type,
                "source_platform": "onedrive",
                "onedrive_path": item.metadata.get("onedrive_path", ""),
                "onedrive_id": item.metadata.get("onedrive_id", ""),
                "web_url": item.metadata.get("web_url", ""),
                "file_size": item.metadata.get("size_bytes", 0),
                "file_extension": item.metadata.get("extension", ""),
                "mime_type": item.metadata.get("mime_type", ""),
                "content_hash": item.content_hash,
                "timestamp": item.timestamp.isoformat() if item.timestamp else None,
                "category": category,
                "imported_at": datetime.now(timezone.utc).isoformat(),
            }

            # Include photo/location metadata if present
            if "photo" in item.metadata:
                node_data["photo_metadata"] = item.metadata["photo"]
            if "location" in item.metadata:
                node_data["location"] = item.metadata["location"]

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

    def download_file(self, item_id: str, local_path: str) -> bool:
        """Download a file from OneDrive to a local path."""
        import httpx

        try:
            # Get download URL
            result = self._graph_get(f"/me/drive/items/{item_id}")
            download_url = result.get("@microsoft.graph.downloadUrl", "")
            if not download_url:
                log.error("No download URL for item %s", item_id)
                return False

            with httpx.stream("GET", download_url, timeout=60) as resp:
                resp.raise_for_status()
                Path(local_path).parent.mkdir(parents=True, exist_ok=True)
                with open(local_path, "wb") as f:
                    for chunk in resp.iter_bytes(chunk_size=8192):
                        f.write(chunk)
            return True
        except Exception as e:
            log.error("Failed to download item %s: %s", item_id, e)
            return False
