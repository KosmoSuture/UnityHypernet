"""
Google Maps Location History Importer

Imports location data from Google Takeout's Location History export,
turning years of GPS breadcrumbs into a rich personal timeline.

Google provides location history in two formats:
  1. **Semantic Location History** (Records.json) — Place visits and activity
     segments with names, addresses, durations, and travel modes.
  2. **Raw Location History** (Records.json legacy) — Raw GPS coordinates
     with timestamps and accuracy.

The semantic format is far more useful for life stories — it contains
named places ("Starbucks on Main St"), visit durations, and how you
traveled between them.

This importer creates:
  - Timeline entries (visited X for Y minutes)
  - Frequently visited places (home, work, favorites)
  - Travel patterns (commute routes, trips)
  - Life chapters (moved cities, vacations, road trips)
  - Heatmap data for visualization

Usage:
    # From Google Takeout ZIP
    importer = GoogleLocationImporter(archive_root, private_root)
    results = importer.import_export("/path/to/takeout-location-history.zip")

    # From extracted Semantic Location History folder
    results = importer.import_directory("/path/to/Semantic Location History/")

How to export:
    1. Go to https://takeout.google.com
    2. Deselect all, then select only "Location History (Timeline)"
    3. Choose format: JSON
    4. Export and download the ZIP
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import os
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional

from .protocol import (
    BaseConnector, AuthStatus, ImportStatus,
    RawItem, ImportResult, ScanResult,
)

log = logging.getLogger(__name__)


@dataclass
class PlaceVisit:
    """A visit to a named place."""
    name: str
    address: str
    latitude: float
    longitude: float
    start_time: datetime
    end_time: datetime
    duration_minutes: float
    place_id: str = ""
    category: str = ""  # restaurant, home, work, store, etc.
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_minutes": self.duration_minutes,
            "place_id": self.place_id,
            "category": self.category,
            "confidence": self.confidence,
        }


@dataclass
class ActivitySegment:
    """Travel between two places."""
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    start_time: datetime
    end_time: datetime
    distance_meters: int = 0
    activity_type: str = ""  # WALKING, DRIVING, IN_BUS, CYCLING, FLYING
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "start": {"lat": self.start_lat, "lng": self.start_lng},
            "end": {"lat": self.end_lat, "lng": self.end_lng},
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "distance_meters": self.distance_meters,
            "activity_type": self.activity_type,
            "confidence": self.confidence,
        }


@dataclass
class LocationStats:
    """Aggregate statistics from location history."""
    total_visits: int = 0
    total_segments: int = 0
    unique_places: int = 0
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None
    top_places: list[dict] = field(default_factory=list)
    activity_breakdown: dict[str, int] = field(default_factory=dict)
    cities_visited: list[str] = field(default_factory=list)
    total_distance_km: float = 0.0
    total_days_tracked: int = 0


class GoogleLocationImporter(BaseConnector):
    """Imports location history from Google Takeout export.

    Processes both the new Semantic Location History format and the
    legacy Records.json format. Converts GPS data into meaningful
    life story events: places visited, trips taken, routines formed.
    """

    source_type = "location_history"
    source_name = "Google Maps Timeline"

    def __init__(self, archive_root: str, private_root: str = ""):
        self.archive_root = Path(archive_root)
        self.private_root = Path(private_root) if private_root else self.archive_root
        self._visits: list[PlaceVisit] = []
        self._segments: list[ActivitySegment] = []
        self._stats = LocationStats()

    def auth_status(self) -> AuthStatus:
        """Location history uses file import — no auth needed."""
        return AuthStatus.CONFIGURED

    def scan(self, **kwargs) -> ScanResult:
        """Scan a location history export for available data."""
        path = kwargs.get("path", "")
        if not path:
            return ScanResult(source=self.source_name, total=0, new=0)

        path = Path(path)
        visits, segments = self._parse_location_data(path)

        return ScanResult(
            source=self.source_name,
            total=len(visits) + len(segments),
            new=len(visits) + len(segments),
            details={
                "visits": len(visits),
                "segments": len(segments),
                "unique_places": len(set(v.name for v in visits if v.name)),
            },
        )

    def import_export(self, export_path: str) -> ImportResult:
        """Import from a Google Takeout ZIP or extracted directory.

        Args:
            export_path: Path to the Takeout ZIP or extracted directory.
        """
        path = Path(export_path)
        result = ImportResult(source=self.source_name)

        if path.is_file() and path.suffix == ".zip":
            visits, segments = self._parse_zip(path)
        elif path.is_dir():
            visits, segments = self._parse_directory(path)
        else:
            result.errors.append(f"Not a ZIP file or directory: {path}")
            return result

        self._visits = visits
        self._segments = segments

        # Build stats
        self._build_stats()

        # Convert to Hypernet nodes
        imported = 0
        skipped = 0

        # Import place visits as timeline entries
        for visit in visits:
            try:
                item = self._visit_to_raw_item(visit)
                node = self._import_raw_item(item)
                if node:
                    imported += 1
                else:
                    skipped += 1
            except Exception as e:
                result.errors.append(f"Failed to import visit '{visit.name}': {e}")
                skipped += 1

        # Save aggregate data
        self._save_location_summary()
        self._save_frequent_places()
        self._save_travel_patterns()

        result.imported = imported
        result.skipped = skipped
        result.total = len(visits) + len(segments)
        result.details = {
            "visits_imported": imported,
            "segments": len(segments),
            "unique_places": self._stats.unique_places,
            "date_range": f"{self._stats.date_range_start} to {self._stats.date_range_end}",
            "total_distance_km": round(self._stats.total_distance_km, 1),
            "top_places": self._stats.top_places[:5],
        }

        log.info(
            "Google Location History: imported %d visits, %d segments, %d unique places",
            imported, len(segments), self._stats.unique_places,
        )
        return result

    def import_directory(self, dir_path: str) -> ImportResult:
        """Import from an extracted Semantic Location History directory."""
        return self.import_export(dir_path)

    # ── Parsing ──

    def _parse_location_data(self, path: Path) -> tuple[list[PlaceVisit], list[ActivitySegment]]:
        """Parse location data from either ZIP or directory."""
        if path.is_file() and path.suffix == ".zip":
            return self._parse_zip(path)
        elif path.is_dir():
            return self._parse_directory(path)
        return [], []

    def _parse_zip(self, zip_path: Path) -> tuple[list[PlaceVisit], list[ActivitySegment]]:
        """Parse a Google Takeout ZIP file for location data."""
        visits = []
        segments = []

        try:
            with zipfile.ZipFile(zip_path) as zf:
                for info in zf.infolist():
                    name = info.filename.lower()
                    # Semantic Location History (monthly JSON files)
                    if "semantic location history" in name and name.endswith(".json"):
                        try:
                            data = json.loads(zf.read(info))
                            v, s = self._parse_semantic_json(data)
                            visits.extend(v)
                            segments.extend(s)
                        except (json.JSONDecodeError, KeyError) as e:
                            log.debug("Failed to parse %s: %s", info.filename, e)

                    # Legacy Records.json
                    elif name.endswith("records.json") and "location" in name:
                        try:
                            data = json.loads(zf.read(info))
                            v = self._parse_records_json(data)
                            visits.extend(v)
                        except (json.JSONDecodeError, KeyError) as e:
                            log.debug("Failed to parse Records.json: %s", e)

                    # Settings.json (for metadata)
                    elif name.endswith("settings.json") and "location" in name:
                        pass  # Could extract account info

        except zipfile.BadZipFile:
            log.error("Invalid ZIP file: %s", zip_path)

        return visits, segments

    def _parse_directory(self, dir_path: Path) -> tuple[list[PlaceVisit], list[ActivitySegment]]:
        """Parse an extracted Semantic Location History directory."""
        visits = []
        segments = []

        # Look for semantic location history JSON files
        for json_file in sorted(dir_path.rglob("*.json")):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))

                if "timelineObjects" in data:
                    v, s = self._parse_semantic_json(data)
                    visits.extend(v)
                    segments.extend(s)
                elif "locations" in data:
                    v = self._parse_records_json(data)
                    visits.extend(v)
            except (json.JSONDecodeError, KeyError) as e:
                log.debug("Failed to parse %s: %s", json_file, e)

        return visits, segments

    def _parse_semantic_json(self, data: dict) -> tuple[list[PlaceVisit], list[ActivitySegment]]:
        """Parse a Semantic Location History JSON file.

        Google's semantic format contains 'timelineObjects' with either
        'placeVisit' or 'activitySegment' entries.
        """
        visits = []
        segments = []

        for obj in data.get("timelineObjects", []):
            if "placeVisit" in obj:
                visit = self._parse_place_visit(obj["placeVisit"])
                if visit:
                    visits.append(visit)
            elif "activitySegment" in obj:
                segment = self._parse_activity_segment(obj["activitySegment"])
                if segment:
                    segments.append(segment)

        return visits, segments

    def _parse_place_visit(self, pv: dict) -> Optional[PlaceVisit]:
        """Parse a single placeVisit object."""
        try:
            location = pv.get("location", {})
            duration = pv.get("duration", {})

            name = location.get("name", "")
            address = location.get("address", "")
            lat = location.get("latitudeE7", 0) / 1e7
            lng = location.get("longitudeE7", 0) / 1e7
            place_id = location.get("placeId", "")

            # Parse timestamps
            start_str = duration.get("startTimestamp", "") or duration.get("startTimestampMs", "")
            end_str = duration.get("endTimestamp", "") or duration.get("endTimestampMs", "")

            start_time = self._parse_timestamp(start_str)
            end_time = self._parse_timestamp(end_str)

            if not start_time or not end_time:
                return None

            duration_min = (end_time - start_time).total_seconds() / 60

            # Semantic type / category
            semantic_type = location.get("semanticType", "")
            category = self._classify_place(semantic_type, name)

            confidence_pct = pv.get("placeConfidence", "LOW")
            confidence = {"HIGH": 0.9, "MEDIUM": 0.6, "LOW": 0.3}.get(confidence_pct, 0.5)

            return PlaceVisit(
                name=name or f"Location ({lat:.4f}, {lng:.4f})",
                address=address,
                latitude=lat,
                longitude=lng,
                start_time=start_time,
                end_time=end_time,
                duration_minutes=duration_min,
                place_id=place_id,
                category=category,
                confidence=confidence,
            )
        except Exception as e:
            log.debug("Failed to parse place visit: %s", e)
            return None

    def _parse_activity_segment(self, seg: dict) -> Optional[ActivitySegment]:
        """Parse a single activitySegment object."""
        try:
            start_loc = seg.get("startLocation", {})
            end_loc = seg.get("endLocation", {})
            duration = seg.get("duration", {})

            start_time = self._parse_timestamp(
                duration.get("startTimestamp", "") or duration.get("startTimestampMs", "")
            )
            end_time = self._parse_timestamp(
                duration.get("endTimestamp", "") or duration.get("endTimestampMs", "")
            )

            if not start_time or not end_time:
                return None

            activity_type = seg.get("activityType", "UNKNOWN")
            distance = seg.get("distance", 0)
            confidence = seg.get("confidence", "LOW")
            conf_val = {"HIGH": 0.9, "MEDIUM": 0.6, "LOW": 0.3}.get(confidence, 0.5)

            return ActivitySegment(
                start_lat=start_loc.get("latitudeE7", 0) / 1e7,
                start_lng=start_loc.get("longitudeE7", 0) / 1e7,
                end_lat=end_loc.get("latitudeE7", 0) / 1e7,
                end_lng=end_loc.get("longitudeE7", 0) / 1e7,
                start_time=start_time,
                end_time=end_time,
                distance_meters=distance,
                activity_type=activity_type,
                confidence=conf_val,
            )
        except Exception as e:
            log.debug("Failed to parse activity segment: %s", e)
            return None

    def _parse_records_json(self, data: dict) -> list[PlaceVisit]:
        """Parse legacy Records.json format (raw GPS points).

        Converts clusters of nearby GPS points into synthetic place visits.
        """
        visits = []
        locations = data.get("locations", [])

        # Group by day and cluster by proximity
        # This is a simplified version — production would use proper clustering
        for loc in locations[:10000]:  # Limit for performance
            try:
                lat = loc.get("latitudeE7", 0) / 1e7
                lng = loc.get("longitudeE7", 0) / 1e7
                ts = self._parse_timestamp(
                    loc.get("timestamp", "") or loc.get("timestampMs", "")
                )
                if ts and abs(lat) > 0.1:
                    visits.append(PlaceVisit(
                        name=f"Location ({lat:.4f}, {lng:.4f})",
                        address="",
                        latitude=lat,
                        longitude=lng,
                        start_time=ts,
                        end_time=ts + timedelta(minutes=5),
                        duration_minutes=5,
                        category="raw_gps",
                    ))
            except Exception:
                continue

        return visits

    # ── Helpers ──

    @staticmethod
    def _parse_timestamp(ts: str) -> Optional[datetime]:
        """Parse a Google timestamp (ISO 8601 or milliseconds)."""
        if not ts:
            return None
        try:
            # Try ISO 8601 first
            if "T" in ts:
                return datetime.fromisoformat(ts.replace("Z", "+00:00"))
            # Try milliseconds
            ms = int(ts)
            return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
        except (ValueError, TypeError, OSError):
            return None

    @staticmethod
    def _classify_place(semantic_type: str, name: str) -> str:
        """Classify a place into a category."""
        st = (semantic_type or "").upper()
        nm = (name or "").lower()

        if "HOME" in st:
            return "home"
        if "WORK" in st:
            return "work"

        # Name-based classification
        food_words = ["restaurant", "cafe", "coffee", "pizza", "burger", "sushi",
                      "starbucks", "mcdonald", "subway", "chipotle", "taco"]
        if any(w in nm for w in food_words):
            return "food"

        store_words = ["walmart", "target", "costco", "store", "market", "shop",
                       "mall", "amazon", "home depot", "lowes"]
        if any(w in nm for w in store_words):
            return "shopping"

        if any(w in nm for w in ["gym", "fitness", "yoga", "sport"]):
            return "fitness"
        if any(w in nm for w in ["hospital", "doctor", "clinic", "pharmacy", "medical"]):
            return "health"
        if any(w in nm for w in ["school", "university", "college", "library"]):
            return "education"
        if any(w in nm for w in ["church", "mosque", "temple", "synagogue"]):
            return "worship"
        if any(w in nm for w in ["park", "beach", "trail", "garden", "zoo"]):
            return "recreation"
        if any(w in nm for w in ["airport", "station", "terminal"]):
            return "transit"
        if any(w in nm for w in ["hotel", "motel", "airbnb", "inn"]):
            return "lodging"

        return "other"

    def _visit_to_raw_item(self, visit: PlaceVisit) -> RawItem:
        """Convert a PlaceVisit into a RawItem for the import pipeline."""
        # Create a unique hash for deduplication
        content_hash = hashlib.sha256(
            f"{visit.latitude:.6f}:{visit.longitude:.6f}:{visit.start_time.isoformat()}".encode()
        ).hexdigest()[:16]

        title = f"Visited {visit.name}" if visit.name else f"Location visit"
        if visit.duration_minutes > 60:
            hours = visit.duration_minutes / 60
            title += f" ({hours:.1f} hours)"
        elif visit.duration_minutes > 1:
            title += f" ({int(visit.duration_minutes)} min)"

        return RawItem(
            source=self.source_name,
            source_id=f"gmaps-{content_hash}",
            title=title,
            content=json.dumps(visit.to_dict()),
            timestamp=visit.start_time,
            category="timeline",
            tags=["location", visit.category, "google-maps"],
            metadata={
                "latitude": visit.latitude,
                "longitude": visit.longitude,
                "address": visit.address,
                "place_id": visit.place_id,
                "duration_minutes": visit.duration_minutes,
                "category": visit.category,
                "confidence": visit.confidence,
            },
            content_hash=content_hash,
        )

    def _import_raw_item(self, item: RawItem) -> Optional[Any]:
        """Import a RawItem into the Hypernet timeline.

        Creates a node in the user's personal timeline (1.local.timeline).
        """
        # For now, save to a local timeline directory
        timeline_dir = self.private_root / "data" / "timeline" / "location"
        timeline_dir.mkdir(parents=True, exist_ok=True)

        # Create a file for each visit
        date_str = item.timestamp.strftime("%Y-%m-%d")
        filename = f"{date_str}-{item.source_id}.json"
        filepath = timeline_dir / filename

        if filepath.exists():
            return None  # Duplicate

        entry = {
            "ha": f"1.local.timeline.location.{item.source_id}",
            "object_type": "timeline-entry",
            "source": item.source,
            "source_id": item.source_id,
            "title": item.title,
            "timestamp": item.timestamp.isoformat(),
            "category": item.category,
            "tags": item.tags,
            **item.metadata,
        }
        filepath.write_text(json.dumps(entry, indent=2), encoding="utf-8")
        return entry

    # ── Aggregate Analysis ──

    def _build_stats(self):
        """Build aggregate statistics from parsed data."""
        if not self._visits:
            return

        place_counts = Counter(v.name for v in self._visits if v.name)
        dates = [v.start_time for v in self._visits]

        self._stats = LocationStats(
            total_visits=len(self._visits),
            total_segments=len(self._segments),
            unique_places=len(place_counts),
            date_range_start=min(dates).strftime("%Y-%m-%d") if dates else None,
            date_range_end=max(dates).strftime("%Y-%m-%d") if dates else None,
            top_places=[
                {"name": name, "visits": count}
                for name, count in place_counts.most_common(20)
            ],
            activity_breakdown=dict(Counter(s.activity_type for s in self._segments)),
            total_distance_km=sum(s.distance_meters for s in self._segments) / 1000,
            total_days_tracked=len(set(d.date() for d in dates)),
        )

    def _save_location_summary(self):
        """Save aggregate location summary for the Life Story."""
        summary_dir = self.private_root / "data" / "timeline"
        summary_dir.mkdir(parents=True, exist_ok=True)

        summary = {
            "ha": "1.local.timeline.location-summary",
            "object_type": "location-summary",
            "source": self.source_name,
            "generated": datetime.now(timezone.utc).isoformat(),
            "stats": {
                "total_visits": self._stats.total_visits,
                "total_segments": self._stats.total_segments,
                "unique_places": self._stats.unique_places,
                "date_range": {
                    "start": self._stats.date_range_start,
                    "end": self._stats.date_range_end,
                },
                "total_distance_km": round(self._stats.total_distance_km, 1),
                "total_days_tracked": self._stats.total_days_tracked,
                "activity_breakdown": self._stats.activity_breakdown,
            },
            "top_places": self._stats.top_places[:20],
        }

        (summary_dir / "location-summary.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
        log.info("Location summary saved: %d visits, %d places", self._stats.total_visits, self._stats.unique_places)

    def _save_frequent_places(self):
        """Identify and save frequently visited places (home, work, favorites)."""
        places_dir = self.private_root / "data" / "places"
        places_dir.mkdir(parents=True, exist_ok=True)

        # Group visits by place
        by_place: dict[str, list[PlaceVisit]] = defaultdict(list)
        for v in self._visits:
            if v.name:
                by_place[v.name].append(v)

        frequent = []
        for name, place_visits in sorted(by_place.items(), key=lambda x: -len(x[1])):
            total_time = sum(v.duration_minutes for v in place_visits)
            avg_visit = total_time / len(place_visits) if place_visits else 0
            first_visit = min(v.start_time for v in place_visits)
            last_visit = max(v.start_time for v in place_visits)

            # Use the most common category
            categories = [v.category for v in place_visits if v.category != "other"]
            category = Counter(categories).most_common(1)[0][0] if categories else "other"

            frequent.append({
                "name": name,
                "category": category,
                "visit_count": len(place_visits),
                "total_hours": round(total_time / 60, 1),
                "avg_visit_minutes": round(avg_visit, 1),
                "first_visit": first_visit.isoformat(),
                "last_visit": last_visit.isoformat(),
                "latitude": place_visits[0].latitude,
                "longitude": place_visits[0].longitude,
                "address": place_visits[0].address,
            })

        output = {
            "ha": "1.local.places",
            "object_type": "frequent-places",
            "source": self.source_name,
            "generated": datetime.now(timezone.utc).isoformat(),
            "places": frequent[:100],  # Top 100
        }

        (places_dir / "frequent-places.json").write_text(
            json.dumps(output, indent=2), encoding="utf-8"
        )
        log.info("Saved %d frequent places", len(frequent))

    def _save_travel_patterns(self):
        """Analyze and save travel patterns for life story enrichment."""
        patterns_dir = self.private_root / "data" / "timeline"
        patterns_dir.mkdir(parents=True, exist_ok=True)

        # Group segments by activity type
        by_type = defaultdict(list)
        for seg in self._segments:
            by_type[seg.activity_type].append(seg)

        # Monthly distance tracking
        monthly_distance: dict[str, float] = defaultdict(float)
        for seg in self._segments:
            month = seg.start_time.strftime("%Y-%m")
            monthly_distance[month] += seg.distance_meters / 1000

        patterns = {
            "ha": "1.local.timeline.travel-patterns",
            "object_type": "travel-patterns",
            "source": self.source_name,
            "generated": datetime.now(timezone.utc).isoformat(),
            "activity_summary": {
                activity: {
                    "count": len(segs),
                    "total_km": round(sum(s.distance_meters for s in segs) / 1000, 1),
                    "avg_km": round(sum(s.distance_meters for s in segs) / 1000 / max(len(segs), 1), 1),
                }
                for activity, segs in by_type.items()
            },
            "monthly_distance_km": dict(sorted(monthly_distance.items())),
            "total_trips": len(self._segments),
            "total_km": round(sum(s.distance_meters for s in self._segments) / 1000, 1),
        }

        (patterns_dir / "travel-patterns.json").write_text(
            json.dumps(patterns, indent=2), encoding="utf-8"
        )
        log.info("Saved travel patterns: %d trips, %.0f km total", len(self._segments), patterns["total_km"])
