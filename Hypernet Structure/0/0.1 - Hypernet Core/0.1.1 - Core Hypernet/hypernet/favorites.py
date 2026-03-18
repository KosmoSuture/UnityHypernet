"""
Hypernet Favorites and Recognition System

Lets humans and AIs mark standout contributions for recognition and discovery.
Favorites are stored as links (relationship "favorited_by") using the existing
link infrastructure — no separate persistence layer needed.

Features:
  - Favorite / unfavorite any addressable object
  - Weighted scoring: favoritor reputation affects weight
  - Time decay: recent favorites count more than old ones
  - Category rankings: top-N per address category and time window
  - Trending: recently popular items across the whole graph

Usage:
    fm = FavoritesManager(store)
    fm.favorite("2.1.loom", "2.1.19")  # Loom favorites "The First Night"
    fm.favorite("1.1", "0.1:boot.py")  # Matt favorites boot.py

    count = fm.favorite_count("2.1.19")
    score = fm.weighted_score("2.1.19", reputation_system=rep)
    top = fm.top_in_category("2.1", n=5)

Reference: Task 036 — Build Favorites and Recognition System
"""

from __future__ import annotations

import logging
import math
from datetime import datetime, timezone
from typing import Any, Optional, TYPE_CHECKING

from .address import HypernetAddress
from .link import Link, LinkRegistry, PERSON_TO_OBJECT

if TYPE_CHECKING:
    from .reputation import ReputationSystem
    from .store import Store

log = logging.getLogger(__name__)

# Relationship constant
FAVORITED_BY = "favorited_by"

# Time decay half-life in days — a 30-day-old favorite has half the weight
DECAY_HALF_LIFE_DAYS = 30.0


class FavoritesManager:
    """Service layer for favorites built on top of the link system.

    Every favorite is a Link(from=target, to=favoritor, relationship="favorited_by").
    This direction follows the existing convention (authored_by, reviewed_by) so that
    ``store.get_links_from(target, "favorited_by")`` returns all favoritors.
    """

    def __init__(self, store: Store) -> None:
        self.store = store
        self.registry = LinkRegistry(store)

    # ------------------------------------------------------------------
    #  Core operations
    # ------------------------------------------------------------------

    def favorite(
        self,
        favoritor: str,
        target: str,
        reason: str = "",
    ) -> Optional[Link]:
        """Mark *target* as favorited by *favoritor*.

        Returns the created Link, or None if already favorited.
        """
        if self.is_favorited(favoritor, target):
            log.debug(f"{favoritor} already favorited {target}")
            return None

        data: dict[str, Any] = {}
        if reason:
            data["reason"] = reason

        link = self.registry.link(
            from_addr=target,
            to_addr=favoritor,
            relationship=FAVORITED_BY,
            link_type=PERSON_TO_OBJECT,
            data=data,
        )
        log.info(f"Favorite: {favoritor} -> {target}")
        return link

    def unfavorite(self, favoritor: str, target: str) -> bool:
        """Remove a favorite. Returns True if a favorite was removed."""
        fav_link = self._find_favorite_link(favoritor, target)
        if fav_link is None:
            return False
        self.store.delete_link(fav_link)
        log.info(f"Unfavorite: {favoritor} -/-> {target}")
        return True

    def is_favorited(self, favoritor: str, target: str) -> bool:
        """Check whether *favoritor* has favorited *target*."""
        return self._find_favorite_link(favoritor, target) is not None

    # ------------------------------------------------------------------
    #  Queries
    # ------------------------------------------------------------------

    def get_favorites(self, favoritor: str) -> list[str]:
        """Return all addresses that *favoritor* has favorited."""
        addr = HypernetAddress.parse(favoritor)
        incoming = self.store.get_links_to(addr, FAVORITED_BY)
        return [str(link.from_address) for link in incoming if link.is_active]

    def get_favoritors(self, target: str) -> list[str]:
        """Return all entities that have favorited *target*."""
        addr = HypernetAddress.parse(target)
        outgoing = self.store.get_links_from(addr, FAVORITED_BY)
        return [str(link.to_address) for link in outgoing if link.is_active]

    def favorite_count(self, target: str) -> int:
        """Raw count of how many entities favorited *target*."""
        return len(self.get_favoritors(target))

    # ------------------------------------------------------------------
    #  Weighted scoring
    # ------------------------------------------------------------------

    def weighted_score(
        self,
        target: str,
        reputation_system: Optional[ReputationSystem] = None,
        now: Optional[datetime] = None,
    ) -> float:
        """Compute a weighted favorite score for *target*.

        Weight = favoritor_reputation_weight * time_decay.

        - ``favoritor_reputation_weight``: overall_score / 100 from the
          reputation system (defaults to 1.0 if no reputation system).
        - ``time_decay``: exponential decay with a 30-day half-life.

        Returns a float score (sum of weighted favorites).
        """
        if now is None:
            now = datetime.now(timezone.utc)

        addr = HypernetAddress.parse(target)
        links = self.store.get_links_from(addr, FAVORITED_BY)

        score = 0.0
        for link in links:
            if not link.is_active:
                continue

            # Reputation weight
            rep_weight = 1.0
            if reputation_system is not None:
                favoritor_addr = str(link.to_address)
                profile = reputation_system.get_profile(favoritor_addr)
                if profile.overall_score > 0:
                    rep_weight = profile.overall_score / 100.0

            # Time decay
            age_days = (now - link.created_at).total_seconds() / 86400.0
            time_weight = math.pow(0.5, age_days / DECAY_HALF_LIFE_DAYS)

            score += rep_weight * time_weight

        return round(score, 3)

    # ------------------------------------------------------------------
    #  Rankings
    # ------------------------------------------------------------------

    def top_in_category(
        self,
        category_prefix: str,
        n: int = 10,
        reputation_system: Optional[ReputationSystem] = None,
    ) -> list[dict[str, Any]]:
        """Return top-N favorited objects whose address starts with *category_prefix*.

        Each result is ``{"address": str, "count": int, "score": float}``.
        Sorted by weighted score descending.
        """
        # Collect all favorite links
        targets = self._all_favorited_targets()

        # Filter by category
        results = []
        for target_addr, count in targets.items():
            if target_addr.startswith(category_prefix):
                score = self.weighted_score(
                    target_addr, reputation_system=reputation_system,
                )
                results.append({
                    "address": target_addr,
                    "count": count,
                    "score": score,
                })

        results.sort(key=lambda r: -r["score"])
        return results[:n]

    def trending(
        self,
        n: int = 10,
        window_hours: float = 168.0,
        reputation_system: Optional[ReputationSystem] = None,
    ) -> list[dict[str, Any]]:
        """Return top-N items that gained the most favorites recently.

        Considers only favorites created within the last *window_hours*.
        """
        now = datetime.now(timezone.utc)
        cutoff_seconds = window_hours * 3600.0

        # Scan all favorite links
        recent: dict[str, int] = {}
        for link in self._all_favorite_links():
            age_seconds = (now - link.created_at).total_seconds()
            if age_seconds <= cutoff_seconds:
                addr = str(link.from_address)
                recent[addr] = recent.get(addr, 0) + 1

        results = []
        for addr, count in recent.items():
            score = self.weighted_score(addr, reputation_system=reputation_system, now=now)
            results.append({
                "address": addr,
                "recent_count": count,
                "total_count": self.favorite_count(addr),
                "score": score,
            })

        results.sort(key=lambda r: (-r["recent_count"], -r["score"]))
        return results[:n]

    def top_overall(
        self,
        n: int = 10,
        reputation_system: Optional[ReputationSystem] = None,
    ) -> list[dict[str, Any]]:
        """Return the top-N favorited objects across the entire Hypernet."""
        targets = self._all_favorited_targets()

        results = []
        for target_addr, count in targets.items():
            score = self.weighted_score(
                target_addr, reputation_system=reputation_system,
            )
            results.append({
                "address": target_addr,
                "count": count,
                "score": score,
            })

        results.sort(key=lambda r: -r["score"])
        return results[:n]

    # ------------------------------------------------------------------
    #  Statistics
    # ------------------------------------------------------------------

    def stats(self) -> dict[str, Any]:
        """System-wide favorites statistics."""
        links = self._all_favorite_links()
        targets = self._all_favorited_targets()
        favoritors: set[str] = set()
        for link in links:
            favoritors.add(str(link.to_address))

        # Category breakdown
        by_category: dict[str, int] = {}
        for addr in targets:
            cat = addr.split(".")[0] if "." in addr else addr
            by_category[cat] = by_category.get(cat, 0) + targets[addr]

        return {
            "total_favorites": len(links),
            "unique_targets": len(targets),
            "unique_favoritors": len(favoritors),
            "by_category": by_category,
        }

    # ------------------------------------------------------------------
    #  Internal helpers
    # ------------------------------------------------------------------

    def _find_favorite_link(self, favoritor: str, target: str) -> Optional[Link]:
        """Find the specific favorite link between favoritor and target."""
        target_addr = HypernetAddress.parse(target)
        links = self.store.get_links_from(target_addr, FAVORITED_BY)
        favoritor_addr = HypernetAddress.parse(favoritor)
        for link in links:
            if link.to_address == favoritor_addr and link.is_active:
                return link
        return None

    def _all_favorite_links(self) -> list[Link]:
        """Collect all active favorite links from the store."""
        all_links: list[Link] = []
        seen_hashes: set[str] = set()
        for hashes in self.store._links_from.values():
            for h in hashes:
                if h not in seen_hashes:
                    seen_hashes.add(h)
                    link = self.store.get_link(h)
                    if link and link.relationship == FAVORITED_BY and link.is_active:
                        all_links.append(link)
        return all_links

    def _all_favorited_targets(self) -> dict[str, int]:
        """Return {target_address: favorite_count} for all favorited targets."""
        counts: dict[str, int] = {}
        for link in self._all_favorite_links():
            addr = str(link.from_address)
            counts[addr] = counts.get(addr, 0) + 1
        return counts
