"""
Hypernet Life Story Narrative Generator

Transforms timeline chapters and events into human-readable narratives.
This is what turns organized data into an actual "Life Story" — prose
summaries of chapters, relationship arcs, and milestone detection.

Works in two modes:
  1. Local (no LLM): Template-based summaries from timeline metadata
  2. AI-enhanced: Uses an LLM to generate richer, more natural narratives

The local mode always works; AI mode enhances when available.

Architecture: docs/architecture/personal-accounts-and-life-story.md §Life Story
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .timeline import TimelineEngine, Chapter, TimelineEvent, ZoomLevel

log = logging.getLogger(__name__)


@dataclass
class ChapterNarrative:
    """A narrative summary of a single chapter."""
    chapter_id: str
    title: str
    summary: str           # 1-3 sentence summary
    duration_text: str     # e.g., "3 days", "2 weeks"
    event_count: int
    highlights: list[str]  # Key moments/events
    people_involved: list[str]
    places_mentioned: list[str]
    mood: str = ""         # Detected mood/tone (optional, AI-enhanced)
    ai_generated: bool = False

    def to_dict(self) -> dict:
        return {
            "chapter_id": self.chapter_id,
            "title": self.title,
            "summary": self.summary,
            "duration_text": self.duration_text,
            "event_count": self.event_count,
            "highlights": self.highlights,
            "people_involved": self.people_involved,
            "places_mentioned": self.places_mentioned,
            "mood": self.mood,
            "ai_generated": self.ai_generated,
        }


@dataclass
class LifeStoryOverview:
    """High-level overview of someone's Life Story."""
    account_address: str
    total_events: int
    total_chapters: int
    date_range: str               # e.g., "June 2024 — March 2026"
    chapter_narratives: list[ChapterNarrative]
    milestones: list[dict]        # Key life events detected
    top_people: list[tuple[str, int]]  # (name, mention_count)
    top_places: list[tuple[str, int]]
    source_breakdown: dict[str, int]   # source_type → count

    def to_dict(self) -> dict:
        return {
            "account_address": self.account_address,
            "total_events": self.total_events,
            "total_chapters": self.total_chapters,
            "date_range": self.date_range,
            "chapters": [c.to_dict() for c in self.chapter_narratives],
            "milestones": self.milestones,
            "top_people": [{"name": n, "count": c} for n, c in self.top_people],
            "top_places": [{"name": n, "count": c} for n, c in self.top_places],
            "source_breakdown": self.source_breakdown,
        }


class NarrativeGenerator:
    """Generates Life Story narratives from timeline data.

    Usage:
        gen = NarrativeGenerator(timeline_engine)
        overview = gen.generate_overview()
        chapter = gen.narrate_chapter("ch-001")
    """

    def __init__(self, timeline: TimelineEngine):
        self.timeline = timeline

    def generate_overview(self) -> LifeStoryOverview:
        """Generate a complete Life Story overview."""
        chapters = self.timeline.get_chapter_objects()
        events = list(self.timeline._events)

        # Compute people/place frequency
        people_counter: Counter = Counter()
        place_counter: Counter = Counter()
        source_counter: Counter = Counter()
        for ev in events:
            for p in ev.people:
                people_counter[p] += 1
            for pl in ev.places:
                place_counter[pl] += 1
            if ev.source_type:
                source_counter[ev.source_type] += 1

        # Generate chapter narratives
        narratives = []
        for chapter in chapters:
            narrative = self._narrate_chapter_local(chapter, events)
            narratives.append(narrative)

        # Detect milestones
        milestones = self._detect_milestones(events, chapters)

        # Date range
        date_range = ""
        if events:
            sorted_events = sorted(events, key=lambda e: e.timestamp)
            start = sorted_events[0].timestamp
            end = sorted_events[-1].timestamp
            date_range = f"{start.strftime('%B %Y')} — {end.strftime('%B %Y')}"

        return LifeStoryOverview(
            account_address=self.timeline.account_address,
            total_events=len(events),
            total_chapters=len(chapters),
            date_range=date_range,
            chapter_narratives=narratives,
            milestones=milestones,
            top_people=people_counter.most_common(10),
            top_places=place_counter.most_common(10),
            source_breakdown=dict(source_counter),
        )

    def narrate_chapter(self, chapter_id: str) -> Optional[ChapterNarrative]:
        """Generate a narrative for a specific chapter."""
        chapters = self.timeline.get_chapter_objects()
        chapter = next((c for c in chapters if c.chapter_id == chapter_id), None)
        if not chapter:
            return None

        events = [
            e for e in self.timeline._events
            if e.chapter_id == chapter_id
            or (chapter.start <= e.timestamp <= chapter.end)
        ]

        return self._narrate_chapter_local(chapter, events)

    def _narrate_chapter_local(
        self, chapter: Chapter, all_events: list[TimelineEvent]
    ) -> ChapterNarrative:
        """Generate a template-based narrative for a chapter (no LLM needed)."""
        # Filter events to this chapter
        chapter_events = [
            e for e in all_events
            if e.chapter_id == chapter.chapter_id
            or (chapter.start <= e.timestamp <= chapter.end)
        ]
        chapter_events.sort(key=lambda e: e.timestamp)

        # Duration text
        duration = chapter.duration_days()
        duration_text = self._format_duration(duration)

        # Build summary
        summary = self._build_summary(chapter, chapter_events, duration_text)

        # Pick highlights (most "interesting" events)
        highlights = self._pick_highlights(chapter_events)

        return ChapterNarrative(
            chapter_id=chapter.chapter_id,
            title=chapter.title,
            summary=summary,
            duration_text=duration_text,
            event_count=len(chapter_events),
            highlights=highlights,
            people_involved=chapter.key_people[:5],
            places_mentioned=chapter.key_places[:5],
        )

    def _build_summary(
        self, chapter: Chapter, events: list[TimelineEvent], duration_text: str
    ) -> str:
        """Build a template-based summary sentence."""
        parts = []

        # Opening: what type of chapter
        type_counts: Counter = Counter()
        for ev in events:
            if ev.source_type:
                type_counts[ev.source_type] += 1

        dominant = type_counts.most_common(1)
        dominant_type = dominant[0][0] if dominant else "activity"
        count = len(events)

        # Time frame
        if events:
            start_str = events[0].timestamp.strftime("%B %d")
            end_str = events[-1].timestamp.strftime("%B %d, %Y")
            if events[0].timestamp.year != events[-1].timestamp.year:
                start_str = events[0].timestamp.strftime("%B %d, %Y")
            time_frame = f"{start_str} to {end_str}"
        else:
            time_frame = duration_text

        # Build the summary
        if chapter.key_people and chapter.key_places:
            parts.append(
                f"A {duration_text} period of {dominant_type} activity "
                f"from {time_frame}, involving {', '.join(chapter.key_people[:3])} "
                f"in {', '.join(chapter.key_places[:2])}."
            )
        elif chapter.key_people:
            parts.append(
                f"A {duration_text} period from {time_frame} "
                f"with {', '.join(chapter.key_people[:3])}."
            )
        elif chapter.key_places:
            parts.append(
                f"A {duration_text} in {', '.join(chapter.key_places[:2])}, "
                f"from {time_frame}."
            )
        else:
            parts.append(
                f"A {duration_text} period from {time_frame} "
                f"with {count} {dominant_type} events."
            )

        # Add detail about variety
        if len(type_counts) > 1:
            types_str = ", ".join(
                f"{c} {t}{'s' if c > 1 else ''}"
                for t, c in type_counts.most_common(3)
            )
            parts.append(f"Includes {types_str}.")

        return " ".join(parts)

    def _pick_highlights(self, events: list[TimelineEvent], max_highlights: int = 5) -> list[str]:
        """Pick the most notable events as highlights."""
        highlights = []
        seen_types = set()

        for ev in events:
            if len(highlights) >= max_highlights:
                break

            # Prefer events with titles, people, or places
            score = 0
            if ev.title:
                score += 1
            if ev.people:
                score += 1
            if ev.places:
                score += 1
            if ev.source_type not in seen_types:
                score += 1  # Prefer variety

            if score >= 1 and ev.title:
                date_str = ev.timestamp.strftime("%b %d")
                highlights.append(f"{date_str}: {ev.title}")
                seen_types.add(ev.source_type)

        return highlights

    def _detect_milestones(
        self, events: list[TimelineEvent], chapters: list[Chapter]
    ) -> list[dict]:
        """Detect milestone events (first of a type, large chapters, etc.)."""
        milestones = []
        first_of_type: dict[str, TimelineEvent] = {}

        sorted_events = sorted(events, key=lambda e: e.timestamp)
        for ev in sorted_events:
            if ev.source_type and ev.source_type not in first_of_type:
                first_of_type[ev.source_type] = ev
                milestones.append({
                    "type": "first_import",
                    "label": f"First {ev.source_type} imported",
                    "date": ev.timestamp.isoformat(),
                    "address": ev.address,
                })

        # Largest chapter
        if chapters:
            largest = max(chapters, key=lambda c: c.event_count)
            milestones.append({
                "type": "largest_chapter",
                "label": f"Biggest chapter: {largest.title} ({largest.event_count} events)",
                "date": largest.start.isoformat(),
                "chapter_id": largest.chapter_id,
            })

        # Longest chapter
        if chapters:
            longest = max(chapters, key=lambda c: c.duration_days())
            if longest.chapter_id != (chapters and max(chapters, key=lambda c: c.event_count).chapter_id):
                milestones.append({
                    "type": "longest_chapter",
                    "label": f"Longest chapter: {longest.title} ({self._format_duration(longest.duration_days())})",
                    "date": longest.start.isoformat(),
                    "chapter_id": longest.chapter_id,
                })

        return milestones

    def _format_duration(self, days: float) -> str:
        """Format a duration in days to human-readable text."""
        if days < 1:
            return "less than a day"
        elif days < 2:
            return "1 day"
        elif days < 7:
            return f"{int(days)} days"
        elif days < 14:
            return "1 week"
        elif days < 30:
            return f"{int(days / 7)} weeks"
        elif days < 60:
            return "1 month"
        elif days < 365:
            return f"{int(days / 30)} months"
        elif days < 730:
            return "1 year"
        else:
            return f"{int(days / 365)} years"
