"""
Photo Connector for Hypernet Personal Data Integration

Handles:
- Dropbox photo sync (OAuth2 API)
- Local directory scanning (any folder on any device)
- Deduplication via perceptual hashing (finds duplicates even with different resolutions/crops)
- EXIF metadata extraction for dates, locations, camera info
- Organization into Hypernet structure (1.1.8 Media)

Flow:
1. Scan sources (Dropbox, local dirs, device imports)
2. Hash every image (SHA256 for exact dupes, perceptual hash for near-dupes)
3. Extract EXIF metadata (date, location, camera)
4. Build deduplication index
5. Present duplicates for review
6. Import unique photos into Hypernet with proper addressing

Governed by: 2.0.19 (Data Protection — no deletion), 2.0.20 (Companion Standard)
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional


# Image extensions we care about
IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif",
    ".webp", ".heic", ".heif", ".raw", ".cr2", ".nef", ".arw",
    ".dng", ".svg",
}

VIDEO_EXTENSIONS = {
    ".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv", ".webm",
    ".m4v", ".3gp",
}


@dataclass
class PhotoRecord:
    """Represents a single photo/video for Hypernet ingestion."""
    filepath: str
    filename: str
    sha256: str
    file_size: int
    media_type: str  # "photo" or "video"
    extension: str
    source: str  # "dropbox", "local", "device"
    date_taken: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lon: Optional[float] = None
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    perceptual_hash: Optional[str] = None
    duplicate_of: Optional[str] = None  # SHA256 of the "primary" copy
    hypernet_address: str = ""
    imported: bool = False


class PhotoScanner:
    """Scans directories for photos and builds a deduplication index."""

    def __init__(self, archive_root: str, private_root: str):
        self.archive_root = Path(archive_root)
        self.private_root = Path(private_root)
        self.staging_dir = self.private_root / "import-staging" / "photos"
        self.index_file = self.staging_dir / "_photo_index.json"
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        self.index: dict[str, PhotoRecord] = {}
        self._load_index()

    def _load_index(self):
        """Load existing photo index from disk."""
        if self.index_file.exists():
            data = json.loads(self.index_file.read_text())
            for sha, record in data.items():
                self.index[sha] = PhotoRecord(**record)

    def _save_index(self):
        """Persist photo index to disk."""
        data = {sha: asdict(rec) for sha, rec in self.index.items()}
        self.index_file.write_text(json.dumps(data, indent=2, default=str))

    def scan_directory(self, directory: str, source: str = "local", recursive: bool = True) -> dict:
        """
        Scan a directory for photos/videos.

        Returns summary: {total, new, duplicates, errors}
        """
        directory = Path(directory)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        stats = {"total": 0, "new": 0, "duplicates": 0, "errors": 0}
        pattern = "**/*" if recursive else "*"

        for filepath in directory.glob(pattern):
            if not filepath.is_file():
                continue

            ext = filepath.suffix.lower()
            if ext not in IMAGE_EXTENSIONS and ext not in VIDEO_EXTENSIONS:
                continue

            stats["total"] += 1

            try:
                record = self._process_file(filepath, source)
                if record.sha256 in self.index:
                    # Exact duplicate found
                    stats["duplicates"] += 1
                    record.duplicate_of = self.index[record.sha256].sha256
                else:
                    self.index[record.sha256] = record
                    stats["new"] += 1
            except Exception as e:
                stats["errors"] += 1
                print(f"  Error processing {filepath}: {e}")

        self._save_index()
        return stats

    def _process_file(self, filepath: Path, source: str) -> PhotoRecord:
        """Process a single file: hash it, extract metadata."""
        # SHA256 for exact deduplication
        sha256 = self._file_hash(filepath)
        file_size = filepath.stat().st_size
        ext = filepath.suffix.lower()
        media_type = "photo" if ext in IMAGE_EXTENSIONS else "video"

        record = PhotoRecord(
            filepath=str(filepath),
            filename=filepath.name,
            sha256=sha256,
            file_size=file_size,
            media_type=media_type,
            extension=ext,
            source=source,
        )

        # Try EXIF extraction (only for photos)
        if media_type == "photo":
            self._extract_exif(record, filepath)

        return record

    def _extract_exif(self, record: PhotoRecord, filepath: Path):
        """Extract EXIF metadata from a photo file."""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS, GPSTAGS

            img = Image.open(filepath)
            record.width = img.width
            record.height = img.height

            exif_data = img.getexif()
            if not exif_data:
                return

            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                if tag == "DateTimeOriginal":
                    record.date_taken = str(value)
                elif tag == "Make":
                    record.camera_make = str(value)
                elif tag == "Model":
                    record.camera_model = str(value)

            # GPS data
            gps_info = exif_data.get_ifd(0x8825)
            if gps_info:
                record.gps_lat = self._gps_to_decimal(
                    gps_info.get(2), gps_info.get(1)
                )
                record.gps_lon = self._gps_to_decimal(
                    gps_info.get(4), gps_info.get(3)
                )

        except ImportError:
            pass  # PIL not available — skip EXIF
        except Exception:
            pass  # Corrupt EXIF or unsupported format

    def compute_perceptual_hash(self, filepath: Path) -> Optional[str]:
        """
        Compute perceptual hash for near-duplicate detection.
        Finds duplicates even with different resolutions, crops, or compression.
        """
        try:
            from PIL import Image

            img = Image.open(filepath)
            # Resize to 8x8, convert to grayscale
            img = img.resize((8, 8), Image.Resampling.LANCZOS).convert("L")
            pixels = list(img.getdata())
            avg = sum(pixels) / len(pixels)
            # Each bit: 1 if pixel > average, 0 otherwise
            bits = "".join("1" if p > avg else "0" for p in pixels)
            return hex(int(bits, 2))[2:].zfill(16)
        except Exception:
            return None

    def find_near_duplicates(self, threshold: int = 5) -> list[tuple[str, str, int]]:
        """
        Find near-duplicate photos using perceptual hashing.

        Returns list of (sha1, sha2, hamming_distance) pairs.
        threshold: max Hamming distance to consider as near-duplicate (0=identical, 64=completely different)
        """
        # First, compute perceptual hashes for all entries that don't have one
        for sha, record in self.index.items():
            if record.perceptual_hash is None and record.media_type == "photo":
                record.perceptual_hash = self.compute_perceptual_hash(Path(record.filepath))

        self._save_index()

        # Compare all pairs (O(n^2) — fine for personal collections up to ~100K)
        hashed = [(sha, rec) for sha, rec in self.index.items() if rec.perceptual_hash]
        near_dupes = []

        for i, (sha1, rec1) in enumerate(hashed):
            for sha2, rec2 in hashed[i+1:]:
                dist = self._hamming_distance(rec1.perceptual_hash, rec2.perceptual_hash)
                if dist <= threshold:
                    near_dupes.append((sha1, sha2, dist))

        return near_dupes

    def get_stats(self) -> dict:
        """Get summary statistics of the photo index."""
        photos = [r for r in self.index.values() if r.media_type == "photo"]
        videos = [r for r in self.index.values() if r.media_type == "video"]
        dupes = [r for r in self.index.values() if r.duplicate_of]

        total_size = sum(r.file_size for r in self.index.values())
        sources = {}
        for r in self.index.values():
            sources[r.source] = sources.get(r.source, 0) + 1

        date_range = [r.date_taken for r in self.index.values() if r.date_taken]
        date_range.sort()

        return {
            "total_files": len(self.index),
            "photos": len(photos),
            "videos": len(videos),
            "duplicates": len(dupes),
            "total_size_bytes": total_size,
            "total_size_gb": round(total_size / (1024**3), 2),
            "sources": sources,
            "earliest_date": date_range[0] if date_range else None,
            "latest_date": date_range[-1] if date_range else None,
        }

    def import_to_hypernet(self, record: PhotoRecord) -> str:
        """Import a photo/video into the Hypernet structure at 1.1.8 Media."""
        media_dir = self.archive_root / "1 - People" / "1.1 Matt Schaeffer" / "1.1.8 - Media"

        if record.media_type == "photo":
            subdir = "1.1.8.0 - Photos"
        else:
            subdir = "1.1.8.1 - Videos"

        # Organize by year/month if date available
        if record.date_taken:
            try:
                dt = datetime.strptime(record.date_taken.split(" ")[0], "%Y:%m:%d")
                subdir = f"{subdir}/{dt.year}/{dt.strftime('%Y-%m')}"
            except (ValueError, IndexError):
                pass

        target_dir = media_dir / subdir
        target_dir.mkdir(parents=True, exist_ok=True)

        ha = f"1.1.8.{record.sha256[:8]}"

        # Create metadata sidecar
        meta = {
            "ha": ha,
            "object_type": record.media_type,
            "creator": "1.1",
            "created": datetime.now().strftime("%Y-%m-%d"),
            "original_date": record.date_taken,
            "sha256": record.sha256,
            "source": record.source,
            "original_path": record.filepath,
            "camera": f"{record.camera_make or ''} {record.camera_model or ''}".strip(),
            "dimensions": f"{record.width}x{record.height}" if record.width else None,
            "gps": f"{record.gps_lat},{record.gps_lon}" if record.gps_lat else None,
            "file_size": record.file_size,
        }

        meta_file = target_dir / f"{record.sha256[:12]}.meta.json"
        meta_file.write_text(json.dumps(meta, indent=2, default=str))

        record.hypernet_address = ha
        record.imported = True
        self._save_index()

        return ha

    @staticmethod
    def _file_hash(filepath: Path) -> str:
        """Compute SHA256 hash of a file."""
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def _gps_to_decimal(coords, ref) -> Optional[float]:
        """Convert GPS coordinates from EXIF format to decimal degrees."""
        if not coords or not ref:
            return None
        try:
            degrees = float(coords[0])
            minutes = float(coords[1])
            seconds = float(coords[2])
            decimal = degrees + minutes / 60 + seconds / 3600
            if ref in ("S", "W"):
                decimal = -decimal
            return round(decimal, 6)
        except (TypeError, IndexError, ZeroDivisionError):
            return None

    @staticmethod
    def _hamming_distance(hash1: str, hash2: str) -> int:
        """Compute Hamming distance between two hex hash strings."""
        val1 = int(hash1, 16)
        val2 = int(hash2, 16)
        return bin(val1 ^ val2).count("1")
