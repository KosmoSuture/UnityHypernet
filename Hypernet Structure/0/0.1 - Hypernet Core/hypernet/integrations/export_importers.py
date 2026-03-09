"""
Export File Importers — Facebook, LinkedIn, Google Photos (Takeout)

These importers process manual data exports from platforms that don't
offer viable APIs for personal data access. Each importer:
  1. Reads a ZIP/directory from a GDPR or platform-specific data export
  2. Parses the platform's export format (JSON, CSV, HTML)
  3. Converts items to RawItem format for the standard import pipeline
  4. Routes to appropriate Hypernet categories

Usage:
    # Facebook
    importer = FacebookImporter(archive_root, private_root)
    results = importer.import_export("/path/to/facebook-export.zip")

    # LinkedIn
    importer = LinkedInImporter(archive_root, private_root)
    results = importer.import_export("/path/to/linkedin-export.zip")

    # Google Photos (Takeout)
    importer = GooglePhotosTakeoutImporter(archive_root, private_root)
    results = importer.import_export("/path/to/takeout-photos.zip")
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import logging
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .protocol import (
    BaseConnector, AuthStatus, ImportStatus,
    RawItem, ImportResult, ScanResult,
)

log = logging.getLogger(__name__)


# ── Facebook Importer ────────────────────────────────────────────────


class FacebookImporter(BaseConnector):
    """Imports data from Facebook's 'Download Your Information' export.

    Facebook export format (JSON):
        facebook-export/
        ├── posts/
        │   └── your_posts_1.json
        ├── messages/
        │   └── inbox/
        │       └── person_name/
        │           └── message_1.json
        ├── photos_and_videos/
        │   └── album/
        │       ├── photo.jpg
        │       └── ...
        ├── friends/
        │   └── friends.json
        ├── profile_information/
        │   └── profile_information.json
        └── ...
    """

    source_type = "social"
    source_name = "Facebook"

    def __init__(self, archive_root: str, private_root: str):
        super().__init__(archive_root, private_root)
        self._export_path: Optional[Path] = None

    def authenticate(self) -> AuthStatus:
        """No auth needed — just check if export exists."""
        if self._export_path and self._export_path.exists():
            return AuthStatus.AUTHENTICATED
        return AuthStatus.NOT_CONFIGURED

    def configure(self, export_path: str) -> None:
        """Set the path to the Facebook export ZIP or directory."""
        self._export_path = Path(export_path)

    def scan(self, since: Optional[datetime] = None, max_items: int = 1000) -> ScanResult:
        """Scan Facebook export for importable items."""
        if not self._export_path or not self._export_path.exists():
            return ScanResult(source_platform="facebook", errors=1)

        items: list[RawItem] = []
        total = 0

        try:
            root = self._get_export_root()
            if root is None:
                return ScanResult(source_platform="facebook", errors=1)

            # Scan posts
            for item in self._scan_posts(root, since):
                total += 1
                if not self.is_duplicate(item):
                    items.append(item)
                    if len(items) >= max_items:
                        break

            # Scan messages
            if len(items) < max_items:
                for item in self._scan_messages(root, since):
                    total += 1
                    if not self.is_duplicate(item):
                        items.append(item)
                        if len(items) >= max_items:
                            break

            # Scan friends list
            if len(items) < max_items:
                for item in self._scan_friends(root):
                    total += 1
                    if not self.is_duplicate(item):
                        items.append(item)

            # Scan profile info
            if len(items) < max_items:
                for item in self._scan_profile(root):
                    total += 1
                    if not self.is_duplicate(item):
                        items.append(item)

        except Exception as e:
            log.error("Facebook scan failed: %s", e)
            return ScanResult(
                source_platform="facebook",
                total_found=total,
                errors=1,
                items=items,
            )

        return ScanResult(
            source_platform="facebook",
            total_found=total,
            new_items=len(items),
            duplicates=total - len(items),
            items=items,
        )

    def _get_export_root(self) -> Optional[Path]:
        """Get the root directory of the export (handles ZIP and directory)."""
        if self._export_path.is_dir():
            return self._export_path

        if self._export_path.suffix.lower() == ".zip":
            # Extract to staging
            extract_dir = self.staging_dir / "facebook_export"
            if not extract_dir.exists():
                log.info("Extracting Facebook export to %s", extract_dir)
                extract_dir.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(self._export_path, "r") as zf:
                    zf.extractall(extract_dir)
            return extract_dir

        return None

    def _read_json_file(self, path: Path) -> dict | list:
        """Read a JSON file, handling Facebook's encoding quirks."""
        if not path.exists():
            return {}
        try:
            text = path.read_text(encoding="utf-8")
            return json.loads(text)
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Facebook exports sometimes use latin-1 encoding
            try:
                text = path.read_text(encoding="latin-1")
                return json.loads(text)
            except Exception:
                return {}

    def _fb_timestamp(self, ts: int | float | None) -> Optional[datetime]:
        """Convert Facebook timestamp (Unix seconds) to datetime."""
        if ts is None:
            return None
        try:
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        except (ValueError, TypeError, OSError):
            return None

    def _scan_posts(self, root: Path, since: Optional[datetime]) -> list[RawItem]:
        """Extract posts from the export."""
        items = []
        posts_dir = root / "posts"
        if not posts_dir.exists():
            # Try alternate locations
            for alt in ["your_posts", "posts"]:
                candidate = root / alt
                if candidate.exists():
                    posts_dir = candidate
                    break

        for json_file in sorted(posts_dir.glob("*.json")) if posts_dir.exists() else []:
            data = self._read_json_file(json_file)
            posts = data if isinstance(data, list) else data.get("data", data.get("posts", []))

            for post in posts if isinstance(posts, list) else []:
                ts = self._fb_timestamp(post.get("timestamp"))
                if since and ts and ts < since:
                    continue

                # Extract post text
                text_parts = []
                for attachment_group in post.get("data", []):
                    if isinstance(attachment_group, dict):
                        if "post" in attachment_group:
                            text_parts.append(attachment_group["post"])

                text = post.get("title", "") or " ".join(text_parts)

                item = RawItem(
                    source_type="social_post",
                    source_id=f"fb_post_{post.get('timestamp', '')}",
                    source_platform="facebook",
                    timestamp=ts,
                    title=text[:100] if text else "Facebook Post",
                    content=text,
                    metadata={
                        "type": "post",
                        "has_media": bool(post.get("attachments")),
                    },
                )
                item.compute_hash()
                items.append(item)

        return items

    def _scan_messages(self, root: Path, since: Optional[datetime]) -> list[RawItem]:
        """Extract message threads from the export."""
        items = []
        msg_dirs = [root / "messages" / "inbox", root / "messages" / "archived_threads"]

        for msg_dir in msg_dirs:
            if not msg_dir.exists():
                continue

            for thread_dir in sorted(msg_dir.iterdir()):
                if not thread_dir.is_dir():
                    continue

                for json_file in sorted(thread_dir.glob("message_*.json")):
                    data = self._read_json_file(json_file)
                    thread_title = data.get("title", thread_dir.name)
                    participants = [p.get("name", "") for p in data.get("participants", [])]

                    for msg in data.get("messages", []):
                        ts = self._fb_timestamp(msg.get("timestamp_ms", 0) / 1000 if msg.get("timestamp_ms") else None)
                        if since and ts and ts < since:
                            continue

                        content = msg.get("content", "")
                        sender = msg.get("sender_name", "")

                        item = RawItem(
                            source_type="message",
                            source_id=f"fb_msg_{msg.get('timestamp_ms', '')}_{sender}",
                            source_platform="facebook",
                            timestamp=ts,
                            title=f"{sender}: {content[:60]}" if content else f"Message from {sender}",
                            content=content,
                            metadata={
                                "type": "message",
                                "sender": sender,
                                "thread": thread_title,
                                "participants": participants,
                                "has_media": bool(msg.get("photos") or msg.get("videos")),
                            },
                        )
                        item.compute_hash()
                        items.append(item)

        return items

    def _scan_friends(self, root: Path) -> list[RawItem]:
        """Extract friends list from the export."""
        items = []
        friends_path = root / "friends_and_followers" / "friends.json"
        if not friends_path.exists():
            friends_path = root / "friends" / "friends.json"
        if not friends_path.exists():
            return items

        data = self._read_json_file(friends_path)
        friends = data if isinstance(data, list) else data.get("friends_v2", data.get("friends", []))

        for friend in friends if isinstance(friends, list) else []:
            name = friend.get("name", "")
            ts = self._fb_timestamp(friend.get("timestamp"))

            item = RawItem(
                source_type="contact",
                source_id=f"fb_friend_{name}",
                source_platform="facebook",
                timestamp=ts,
                title=name,
                content=f"Facebook friend: {name}",
                metadata={
                    "type": "friend",
                    "name": name,
                    "added_timestamp": friend.get("timestamp"),
                },
            )
            item.compute_hash()
            items.append(item)

        return items

    def _scan_profile(self, root: Path) -> list[RawItem]:
        """Extract profile info from the export."""
        items = []
        profile_path = root / "profile_information" / "profile_information.json"
        if not profile_path.exists():
            return items

        data = self._read_json_file(profile_path)
        profile = data.get("profile_v2", data) if isinstance(data, dict) else {}

        if profile:
            item = RawItem(
                source_type="profile",
                source_id="fb_profile",
                source_platform="facebook",
                title="Facebook Profile",
                content=json.dumps(profile, indent=2),
                metadata={"type": "profile"},
            )
            item.compute_hash()
            items.append(item)

        return items

    def import_item(self, item: RawItem, target_address: str) -> ImportResult:
        """Import a Facebook item as a Hypernet node."""
        try:
            node_data = {
                "title": item.title,
                "source_type": item.source_type,
                "source_platform": "facebook",
                "content": item.content,
                "timestamp": item.timestamp.isoformat() if item.timestamp else None,
                "content_hash": item.content_hash,
                "imported_at": datetime.now(timezone.utc).isoformat(),
                **item.metadata,
            }

            stage_path = self.staging_dir / f"{item.content_hash[:16]}.json"
            stage_path.parent.mkdir(parents=True, exist_ok=True)
            stage_path.write_text(
                json.dumps({"target_address": target_address, "data": node_data}, indent=2),
                encoding="utf-8",
            )

            return ImportResult(
                source_id=item.source_id,
                status=ImportStatus.IMPORTED,
                hypernet_address=target_address,
            )
        except Exception as e:
            return ImportResult(source_id=item.source_id, status=ImportStatus.FAILED, error=str(e))

    def import_export(self, export_path: str, target_prefix: str = "1.1",
                      max_items: int = 10000) -> list[ImportResult]:
        """Convenience: configure → scan → import all."""
        self.configure(export_path)
        return self.run_full_import(target_prefix, max_items=max_items)


# ── LinkedIn Importer ─────────────────────────────────────────────────


class LinkedInImporter(BaseConnector):
    """Imports data from LinkedIn's 'Download Your Data' export.

    LinkedIn export format:
        linkedin-export/
        ├── Connections.csv
        ├── Messages.csv
        ├── Profile.csv
        ├── Skills.csv
        ├── Endorsement_Received_Info.csv
        ├── Positions.csv
        ├── Education.csv
        └── ...
    """

    source_type = "social"
    source_name = "LinkedIn"

    def __init__(self, archive_root: str, private_root: str):
        super().__init__(archive_root, private_root)
        self._export_path: Optional[Path] = None

    def authenticate(self) -> AuthStatus:
        if self._export_path and self._export_path.exists():
            return AuthStatus.AUTHENTICATED
        return AuthStatus.NOT_CONFIGURED

    def configure(self, export_path: str) -> None:
        self._export_path = Path(export_path)

    def scan(self, since: Optional[datetime] = None, max_items: int = 1000) -> ScanResult:
        """Scan LinkedIn export for importable items."""
        if not self._export_path or not self._export_path.exists():
            return ScanResult(source_platform="linkedin", errors=1)

        items: list[RawItem] = []
        total = 0

        try:
            root = self._get_export_root()
            if root is None:
                return ScanResult(source_platform="linkedin", errors=1)

            # Connections
            for item in self._scan_connections(root):
                total += 1
                if not self.is_duplicate(item):
                    items.append(item)
                    if len(items) >= max_items:
                        break

            # Messages
            if len(items) < max_items:
                for item in self._scan_messages(root, since):
                    total += 1
                    if not self.is_duplicate(item):
                        items.append(item)
                        if len(items) >= max_items:
                            break

            # Skills
            if len(items) < max_items:
                for item in self._scan_skills(root):
                    total += 1
                    if not self.is_duplicate(item):
                        items.append(item)

            # Positions
            if len(items) < max_items:
                for item in self._scan_positions(root):
                    total += 1
                    if not self.is_duplicate(item):
                        items.append(item)

        except Exception as e:
            log.error("LinkedIn scan failed: %s", e)

        return ScanResult(
            source_platform="linkedin",
            total_found=total,
            new_items=len(items),
            duplicates=total - len(items),
            items=items,
        )

    def _get_export_root(self) -> Optional[Path]:
        if self._export_path.is_dir():
            return self._export_path

        if self._export_path.suffix.lower() == ".zip":
            extract_dir = self.staging_dir / "linkedin_export"
            if not extract_dir.exists():
                log.info("Extracting LinkedIn export to %s", extract_dir)
                extract_dir.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(self._export_path, "r") as zf:
                    zf.extractall(extract_dir)
            return extract_dir

        return None

    def _read_csv(self, path: Path) -> list[dict]:
        """Read a CSV file, handling LinkedIn's encoding."""
        if not path.exists():
            return []
        try:
            text = path.read_text(encoding="utf-8-sig")  # LinkedIn uses BOM
            reader = csv.DictReader(io.StringIO(text))
            return list(reader)
        except Exception as e:
            log.warning("Failed to read %s: %s", path, e)
            return []

    def _scan_connections(self, root: Path) -> list[RawItem]:
        """Extract professional connections."""
        items = []
        rows = self._read_csv(root / "Connections.csv")

        for row in rows:
            name = f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip()
            company = row.get("Company", "")
            position = row.get("Position", "")
            connected = row.get("Connected On", "")

            ts = None
            if connected:
                for fmt in ["%d %b %Y", "%m/%d/%Y", "%Y-%m-%d"]:
                    try:
                        ts = datetime.strptime(connected, fmt).replace(tzinfo=timezone.utc)
                        break
                    except ValueError:
                        continue

            item = RawItem(
                source_type="contact",
                source_id=f"li_conn_{name}_{company}",
                source_platform="linkedin",
                timestamp=ts,
                title=name,
                content=f"{name} — {position} at {company}" if position and company else name,
                metadata={
                    "type": "connection",
                    "name": name,
                    "first_name": row.get("First Name", ""),
                    "last_name": row.get("Last Name", ""),
                    "company": company,
                    "position": position,
                    "email": row.get("Email Address", ""),
                    "connected_on": connected,
                },
            )
            item.compute_hash()
            items.append(item)

        return items

    def _scan_messages(self, root: Path, since: Optional[datetime]) -> list[RawItem]:
        """Extract LinkedIn messages."""
        items = []
        rows = self._read_csv(root / "messages.csv")

        for row in rows:
            sender = row.get("FROM", row.get("Sender", ""))
            content = row.get("CONTENT", row.get("Content", ""))
            date_str = row.get("DATE", row.get("Date", ""))

            ts = None
            if date_str:
                for fmt in ["%Y-%m-%d %H:%M:%S UTC", "%m/%d/%Y %I:%M %p", "%Y-%m-%d"]:
                    try:
                        ts = datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
                        break
                    except ValueError:
                        continue

            if since and ts and ts < since:
                continue

            item = RawItem(
                source_type="message",
                source_id=f"li_msg_{date_str}_{sender}",
                source_platform="linkedin",
                timestamp=ts,
                title=f"{sender}: {content[:60]}" if content else f"Message from {sender}",
                content=content or "",
                metadata={
                    "type": "message",
                    "sender": sender,
                    "conversation_id": row.get("CONVERSATION ID", ""),
                    "folder": row.get("FOLDER", ""),
                },
            )
            item.compute_hash()
            items.append(item)

        return items

    def _scan_skills(self, root: Path) -> list[RawItem]:
        """Extract skills from the export."""
        items = []
        rows = self._read_csv(root / "Skills.csv")

        for row in rows:
            skill = row.get("Name", row.get("Skill", ""))
            if skill:
                item = RawItem(
                    source_type="skill",
                    source_id=f"li_skill_{skill}",
                    source_platform="linkedin",
                    title=skill,
                    content=skill,
                    metadata={"type": "skill", "name": skill},
                )
                item.compute_hash()
                items.append(item)

        return items

    def _scan_positions(self, root: Path) -> list[RawItem]:
        """Extract work positions from the export."""
        items = []
        rows = self._read_csv(root / "Positions.csv")

        for row in rows:
            company = row.get("Company Name", "")
            title = row.get("Title", "")
            start = row.get("Started On", "")
            end = row.get("Finished On", "")

            ts = None
            if start:
                for fmt in ["%b %Y", "%Y-%m", "%m/%Y"]:
                    try:
                        ts = datetime.strptime(start, fmt).replace(tzinfo=timezone.utc)
                        break
                    except ValueError:
                        continue

            item = RawItem(
                source_type="work_history",
                source_id=f"li_pos_{company}_{title}",
                source_platform="linkedin",
                timestamp=ts,
                title=f"{title} at {company}",
                content=row.get("Description", ""),
                metadata={
                    "type": "position",
                    "company": company,
                    "title": title,
                    "location": row.get("Location", ""),
                    "started": start,
                    "finished": end,
                },
            )
            item.compute_hash()
            items.append(item)

        return items

    def import_item(self, item: RawItem, target_address: str) -> ImportResult:
        try:
            node_data = {
                "title": item.title,
                "source_type": item.source_type,
                "source_platform": "linkedin",
                "content": item.content,
                "timestamp": item.timestamp.isoformat() if item.timestamp else None,
                "content_hash": item.content_hash,
                "imported_at": datetime.now(timezone.utc).isoformat(),
                **item.metadata,
            }

            stage_path = self.staging_dir / f"{item.content_hash[:16]}.json"
            stage_path.parent.mkdir(parents=True, exist_ok=True)
            stage_path.write_text(
                json.dumps({"target_address": target_address, "data": node_data}, indent=2),
                encoding="utf-8",
            )

            return ImportResult(
                source_id=item.source_id,
                status=ImportStatus.IMPORTED,
                hypernet_address=target_address,
            )
        except Exception as e:
            return ImportResult(source_id=item.source_id, status=ImportStatus.FAILED, error=str(e))

    def import_export(self, export_path: str, target_prefix: str = "1.1",
                      max_items: int = 10000) -> list[ImportResult]:
        self.configure(export_path)
        return self.run_full_import(target_prefix, max_items=max_items)


# ── Google Photos Takeout Importer ────────────────────────────────────


class GooglePhotosTakeoutImporter(BaseConnector):
    """Imports photos from Google Takeout export.

    Google Takeout format:
        Takeout/
        └── Google Photos/
            ├── Album Name/
            │   ├── photo.jpg
            │   ├── photo.jpg.json     ← companion metadata
            │   └── ...
            └── Photos from YYYY/
                ├── IMG_1234.jpg
                ├── IMG_1234.jpg.json
                └── ...

    The companion JSON files contain GPS coordinates, timestamps, and
    other metadata that the photos themselves may not have in EXIF.
    """

    source_type = "photo"
    source_name = "Google Photos (Takeout)"

    def __init__(self, archive_root: str, private_root: str):
        super().__init__(archive_root, private_root)
        self._export_path: Optional[Path] = None

    def authenticate(self) -> AuthStatus:
        if self._export_path and self._export_path.exists():
            return AuthStatus.AUTHENTICATED
        return AuthStatus.NOT_CONFIGURED

    def configure(self, export_path: str) -> None:
        self._export_path = Path(export_path)

    PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic",
                        ".bmp", ".tiff", ".tif", ".raw", ".cr2", ".nef"}
    VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".m4v", ".3gp", ".webm"}

    def scan(self, since: Optional[datetime] = None, max_items: int = 1000) -> ScanResult:
        """Scan Google Photos takeout for media files."""
        if not self._export_path or not self._export_path.exists():
            return ScanResult(source_platform="google_photos", errors=1)

        items: list[RawItem] = []
        total = 0

        try:
            root = self._get_export_root()
            if root is None:
                return ScanResult(source_platform="google_photos", errors=1)

            # Find the Google Photos directory
            photos_root = root / "Google Photos"
            if not photos_root.exists():
                # Might be extracted directly
                photos_root = root

            # Walk all subdirectories
            for media_file in self._walk_media(photos_root):
                total += 1

                # Look for companion JSON metadata
                metadata = self._read_companion_json(media_file)

                # Extract timestamp
                ts = self._extract_timestamp(media_file, metadata)
                if since and ts and ts < since:
                    continue

                # Determine media type
                ext = media_file.suffix.lower()
                is_video = ext in self.VIDEO_EXTENSIONS
                category = "video" if is_video else "photo"

                # Compute file hash for dedup
                file_hash = self._file_sha256(media_file)

                # Album name from parent directory
                album = media_file.parent.name

                item_metadata = {
                    "original_path": str(media_file),
                    "album": album,
                    "extension": ext,
                    "file_size": media_file.stat().st_size,
                    "category": category,
                }

                # Add GPS if available from companion JSON
                if metadata:
                    geo = metadata.get("geoData", metadata.get("geoDataExif", {}))
                    if geo and (geo.get("latitude", 0) != 0 or geo.get("longitude", 0) != 0):
                        item_metadata["latitude"] = geo.get("latitude")
                        item_metadata["longitude"] = geo.get("longitude")
                        item_metadata["altitude"] = geo.get("altitude")

                    # Camera info
                    if "googlePhotosOrigin" in metadata:
                        item_metadata["source_device"] = metadata["googlePhotosOrigin"]

                    # Description
                    desc = metadata.get("description", "")
                    if desc:
                        item_metadata["description"] = desc

                    # People
                    people = metadata.get("people", [])
                    if people:
                        item_metadata["people"] = [p.get("name", "") for p in people]

                item = RawItem(
                    source_type=category,
                    source_id=f"gp_{file_hash[:16]}",
                    source_platform="google_photos",
                    timestamp=ts,
                    title=media_file.name,
                    content=str(media_file),
                    metadata=item_metadata,
                    content_hash=file_hash,
                )

                if not self.is_duplicate(item):
                    items.append(item)

                if len(items) >= max_items:
                    break

        except Exception as e:
            log.error("Google Photos scan failed: %s", e)

        return ScanResult(
            source_platform="google_photos",
            total_found=total,
            new_items=len(items),
            duplicates=total - len(items),
            items=items,
        )

    def _get_export_root(self) -> Optional[Path]:
        if self._export_path.is_dir():
            return self._export_path

        if self._export_path.suffix.lower() == ".zip":
            extract_dir = self.staging_dir / "google_photos_export"
            if not extract_dir.exists():
                log.info("Extracting Google Photos takeout to %s", extract_dir)
                extract_dir.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(self._export_path, "r") as zf:
                    zf.extractall(extract_dir)
            return extract_dir

        return None

    def _walk_media(self, root: Path):
        """Walk directory tree yielding media files."""
        all_media_exts = self.PHOTO_EXTENSIONS | self.VIDEO_EXTENSIONS
        try:
            for entry in sorted(root.iterdir()):
                if entry.is_file() and entry.suffix.lower() in all_media_exts:
                    yield entry
                elif entry.is_dir():
                    yield from self._walk_media(entry)
        except PermissionError:
            pass

    def _read_companion_json(self, media_path: Path) -> dict:
        """Read the companion JSON metadata file for a media file."""
        # Google Takeout puts metadata in filename.ext.json
        json_path = media_path.parent / f"{media_path.name}.json"
        if json_path.exists():
            try:
                return json.loads(json_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    def _extract_timestamp(self, media_path: Path, metadata: dict) -> Optional[datetime]:
        """Extract timestamp from metadata or file."""
        # Priority 1: Companion JSON photoTakenTime
        taken = metadata.get("photoTakenTime", {})
        if taken and "timestamp" in taken:
            try:
                return datetime.fromtimestamp(int(taken["timestamp"]), tz=timezone.utc)
            except (ValueError, TypeError, OSError):
                pass

        # Priority 2: Companion JSON creationTime
        created = metadata.get("creationTime", {})
        if created and "timestamp" in created:
            try:
                return datetime.fromtimestamp(int(created["timestamp"]), tz=timezone.utc)
            except (ValueError, TypeError, OSError):
                pass

        # Priority 3: File modification time
        try:
            return datetime.fromtimestamp(media_path.stat().st_mtime, tz=timezone.utc)
        except OSError:
            return None

    def _file_sha256(self, filepath: Path) -> str:
        """Compute SHA-256 of a file."""
        hasher = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except OSError:
            return hashlib.sha256(str(filepath).encode()).hexdigest()

    def import_item(self, item: RawItem, target_address: str) -> ImportResult:
        """Import a Google Photos item as a Hypernet node."""
        try:
            node_data = {
                "title": item.title,
                "source_type": item.source_type,
                "source_platform": "google_photos",
                "original_path": item.metadata.get("original_path", ""),
                "album": item.metadata.get("album", ""),
                "file_size": item.metadata.get("file_size", 0),
                "file_extension": item.metadata.get("extension", ""),
                "content_hash": item.content_hash,
                "timestamp": item.timestamp.isoformat() if item.timestamp else None,
                "imported_at": datetime.now(timezone.utc).isoformat(),
            }

            # Include GPS if available
            if "latitude" in item.metadata:
                node_data["gps"] = {
                    "latitude": item.metadata["latitude"],
                    "longitude": item.metadata["longitude"],
                    "altitude": item.metadata.get("altitude"),
                }

            if "people" in item.metadata:
                node_data["people"] = item.metadata["people"]

            if "description" in item.metadata:
                node_data["description"] = item.metadata["description"]

            stage_path = self.staging_dir / f"{item.content_hash[:16]}.json"
            stage_path.parent.mkdir(parents=True, exist_ok=True)
            stage_path.write_text(
                json.dumps({"target_address": target_address, "data": node_data}, indent=2),
                encoding="utf-8",
            )

            return ImportResult(
                source_id=item.source_id,
                status=ImportStatus.IMPORTED,
                hypernet_address=target_address,
            )
        except Exception as e:
            return ImportResult(source_id=item.source_id, status=ImportStatus.FAILED, error=str(e))

    def import_export(self, export_path: str, target_prefix: str = "1.1.8.0",
                      max_items: int = 50000) -> list[ImportResult]:
        self.configure(export_path)
        return self.run_full_import(target_prefix, max_items=max_items)
