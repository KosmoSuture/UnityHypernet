"""
Hypernet Cross-Link Generator

Analyzes imported personal data and automatically creates Hypernet
links between related items. This is what turns a flat collection
of data into an interconnected, navigable Life Story.

Cross-link types:
  - Person mentions: email from X → contact node for X
  - Location co-occurrence: photo at Y → location history at Y
  - Temporal proximity: events on same day → linked
  - Same-thread: email replies → linked in conversation thread
  - Receipt → purchase: receipt email → financial record
  - Content similarity: documents with shared keywords

Uses the existing Link and LinkRegistry systems from link.py.

Architecture: docs/architecture/personal-accounts-and-life-story.md §Cross-linking
"""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from typing import Optional

from ..address import HypernetAddress
from ..node import Node
from ..link import Link, LinkRegistry
from ..store import Store

log = logging.getLogger(__name__)


# Standard cross-link relationship types
LINK_TYPES = {
    "mentions_person": {
        "link_type": "semantic",
        "relationship": "mentions",
        "description": "Source mentions or involves this person",
    },
    "at_location": {
        "link_type": "spatial",
        "relationship": "located_at",
        "description": "Event occurred at this location",
    },
    "same_day": {
        "link_type": "temporal",
        "relationship": "same_day",
        "description": "Events that occurred on the same day",
    },
    "reply_to": {
        "link_type": "content",
        "relationship": "reply_to",
        "description": "Reply or response to another item",
    },
    "receipt_for": {
        "link_type": "economic",
        "relationship": "receipt_for",
        "description": "Receipt or confirmation for a purchase",
    },
    "related_topic": {
        "link_type": "semantic",
        "relationship": "related_topic",
        "description": "Shares keywords or topic with another item",
    },
    "part_of_chapter": {
        "link_type": "hierarchical",
        "relationship": "part_of",
        "description": "Belongs to a Life Story chapter",
    },
}


class CrossLinkGenerator:
    """Generates cross-links between nodes in a personal account.

    Usage:
        gen = CrossLinkGenerator(store, link_registry, "1.local.1")
        stats = gen.generate_all()
        print(f"Created {stats['total']} links")
    """

    def __init__(
        self,
        store: Store,
        link_registry: LinkRegistry,
        account_address: str,
    ):
        self.store = store
        self.links = link_registry
        self.account_address = account_address
        self._existing_links: set[tuple[str, str, str]] = set()

    def _link_exists(self, from_addr: str, to_addr: str, relationship: str) -> bool:
        """Check if a link already exists (avoid duplicates)."""
        key = (from_addr, to_addr, relationship)
        if key in self._existing_links:
            return True
        # Check registry using from_address()
        existing = self.links.from_address(HypernetAddress.parse(from_addr))
        for link in existing:
            if (str(link.to_address) == to_addr
                    and link.relationship == relationship):
                self._existing_links.add(key)
                return True
        return False

    def _create_link(
        self,
        from_addr: str,
        to_addr: str,
        link_type: str,
        relationship: str,
        strength: float = 1.0,
        data: Optional[dict] = None,
    ) -> Optional[Link]:
        """Create a cross-link if it doesn't already exist."""
        if self._link_exists(from_addr, to_addr, relationship):
            return None

        link = self.links.link(
            from_addr=from_addr,
            to_addr=to_addr,
            link_type=link_type,
            relationship=relationship,
            strength=strength,
            data=data or {},
            created_by="1.1.10.1",
            creation_method="auto_crosslink",
        )
        self._existing_links.add((from_addr, to_addr, relationship))
        return link

    # ── Link Generators ─────────────────────────────────────────────

    def link_person_mentions(self, nodes: list[Node]) -> int:
        """Link nodes that mention people to contact/person nodes.

        If node A mentions "John Smith" and there's a contact node
        for John Smith, create a "mentions" link between them.
        """
        # Build person index: name → contact node address
        contact_prefix = f"{self.account_address}.4"  # Relationships & Social
        contact_nodes = [n for n in nodes if str(n.address).startswith(contact_prefix)]
        person_index: dict[str, str] = {}
        for node in contact_nodes:
            name = node.data.get("display_name") or node.data.get("name", "")
            if name:
                person_index[name.lower()] = str(node.address)

        if not person_index:
            return 0

        created = 0
        for node in nodes:
            # Extract people mentioned
            people = []
            for field in ["from", "sender", "to", "recipients", "people",
                         "tagged_people", "author", "participants"]:
                val = node.data.get(field)
                if isinstance(val, str) and val:
                    people.append(val)
                elif isinstance(val, list):
                    people.extend(str(v) for v in val if v)

            for person_name in people:
                contact_addr = person_index.get(person_name.lower())
                if contact_addr and contact_addr != str(node.address):
                    link = self._create_link(
                        str(node.address), contact_addr,
                        "semantic", "mentions",
                        data={"person_name": person_name},
                    )
                    if link:
                        created += 1

        return created

    def link_same_day_events(self, nodes: list[Node], max_links_per_day: int = 10) -> int:
        """Link events that occurred on the same day.

        Only links events of different types (email + photo = interesting,
        email + email = not interesting).
        """
        # Group nodes by date
        by_date: dict[str, list[Node]] = defaultdict(list)
        for node in nodes:
            ts = self._extract_timestamp(node)
            if ts:
                date_key = ts.strftime("%Y-%m-%d")
                by_date[date_key].append(node)

        created = 0
        for date_key, day_nodes in by_date.items():
            if len(day_nodes) < 2:
                continue

            # Only link different source types
            typed_nodes: dict[str, list[Node]] = defaultdict(list)
            for node in day_nodes:
                stype = node.data.get("source_type", "unknown")
                typed_nodes[stype].append(node)

            if len(typed_nodes) < 2:
                continue

            # Cross-link between types (limit to avoid explosion)
            types = list(typed_nodes.keys())
            links_this_day = 0
            for i in range(len(types)):
                for j in range(i + 1, len(types)):
                    for n1 in typed_nodes[types[i]][:3]:
                        for n2 in typed_nodes[types[j]][:3]:
                            if links_this_day >= max_links_per_day:
                                break
                            link = self._create_link(
                                str(n1.address), str(n2.address),
                                "temporal", "same_day",
                                strength=0.5,
                                data={"date": date_key},
                            )
                            if link:
                                created += 1
                                links_this_day += 1

        return created

    def link_email_threads(self, nodes: list[Node]) -> int:
        """Link emails that are part of the same conversation thread.

        Uses subject line matching (Re:/Fwd: stripping) and
        message-id/in-reply-to headers when available.
        """
        # Group by normalized subject
        subject_groups: dict[str, list[Node]] = defaultdict(list)
        for node in nodes:
            if node.data.get("source_type") != "email":
                continue
            subject = node.data.get("subject", node.data.get("title", ""))
            normalized = re.sub(r'^(Re|Fwd|FW|RE):\s*', '', subject, flags=re.IGNORECASE).strip().lower()
            if normalized:
                subject_groups[normalized].append(node)

        created = 0
        for subject, thread_nodes in subject_groups.items():
            if len(thread_nodes) < 2:
                continue

            # Sort by timestamp
            thread_nodes.sort(key=lambda n: self._extract_timestamp(n) or datetime.min.replace(tzinfo=timezone.utc))

            # Link each to the previous (conversation chain)
            for i in range(1, len(thread_nodes)):
                link = self._create_link(
                    str(thread_nodes[i].address),
                    str(thread_nodes[i-1].address),
                    "content", "reply_to",
                    data={"thread_subject": subject},
                )
                if link:
                    created += 1

        return created

    def link_location_cooccurrence(self, nodes: list[Node]) -> int:
        """Link items that share a location.

        Groups items by location name and links them together.
        """
        by_location: dict[str, list[Node]] = defaultdict(list)
        for node in nodes:
            for field in ["location", "place", "city", "venue"]:
                val = node.data.get(field)
                if isinstance(val, str) and val:
                    by_location[val.lower()].append(node)
                elif isinstance(val, dict):
                    name = val.get("name") or val.get("city", "")
                    if name:
                        by_location[name.lower()].append(node)

        created = 0
        for location, loc_nodes in by_location.items():
            if len(loc_nodes) < 2:
                continue

            # Link first N pairs (avoid quadratic explosion)
            for i in range(min(len(loc_nodes), 5)):
                for j in range(i + 1, min(len(loc_nodes), 5)):
                    link = self._create_link(
                        str(loc_nodes[i].address),
                        str(loc_nodes[j].address),
                        "spatial", "same_location",
                        strength=0.6,
                        data={"location": location},
                    )
                    if link:
                        created += 1

        return created

    # ── Orchestration ───────────────────────────────────────────────

    def generate_all(self) -> dict:
        """Run all cross-link generators and return statistics.

        Returns a dict with counts of links created per type.
        """
        prefix = HypernetAddress.parse(self.account_address)
        all_nodes = self.store.list_nodes(prefix=prefix)

        log.info(
            "Generating cross-links for %s (%d nodes)",
            self.account_address, len(all_nodes),
        )

        stats = {
            "person_mentions": self.link_person_mentions(all_nodes),
            "same_day": self.link_same_day_events(all_nodes),
            "email_threads": self.link_email_threads(all_nodes),
            "location": self.link_location_cooccurrence(all_nodes),
        }
        stats["total"] = sum(stats.values())

        log.info(
            "Cross-links generated for %s: %d total (%s)",
            self.account_address, stats["total"],
            ", ".join(f"{k}={v}" for k, v in stats.items() if k != "total"),
        )
        return stats

    # ── Helpers ──────────────────────────────────────────────────────

    def _extract_timestamp(self, node: Node) -> Optional[datetime]:
        """Extract timestamp from a node."""
        data = node.data
        for field_name in ["timestamp", "date", "sent_at", "taken_at", "created_at",
                          "published_at", "received_at", "created"]:
            val = data.get(field_name)
            if val:
                try:
                    if isinstance(val, str):
                        return datetime.fromisoformat(val.replace("Z", "+00:00"))
                    elif isinstance(val, datetime):
                        return val
                    elif isinstance(val, (int, float)):
                        return datetime.fromtimestamp(val, tz=timezone.utc)
                except (ValueError, OSError):
                    continue

        if node.created_at:
            if isinstance(node.created_at, datetime):
                return node.created_at
        return None
