"""
Hypernet Reputation System

Multi-entity reputation tracking for People (1.*), AI (2.*), and
Businesses (3.*). Each entity has domain-specific scores derived from
their contributions, task completions, peer reviews, and governance
participation.

Reputation is:
  - Transparent: all scores and evidence are auditable
  - Address-mapped: reputation lives at the entity's address
  - Multi-domain: separate scores for code, architecture, governance, etc.
  - Evidence-based: every score change must cite evidence
  - Peer-influenced: peer assessments contribute to scores

Scoring: 0-100 per domain, based on:
  - Volume (minor weight)
  - Quality (major weight)
  - Impact on others' work (major weight)
  - Self-correction when wrong (moderate weight)
  - Peer recognition (moderate weight)

Usage:
    system = ReputationSystem()
    system.record_contribution("2.1.loom", "code", score=85,
        evidence="Built 8 modules, all tests passing")
    system.record_peer_review("2.1.trace", "2.1.loom", "code", score=80,
        evidence="Reviewed and approved code with minor fixes")

    profile = system.get_profile("2.1.loom")
    print(profile.domain_scores["code"])  # Weighted average
"""

from __future__ import annotations
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)


# Standard reputation domains
DOMAINS = [
    "code",
    "architecture",
    "governance",
    "communication",
    "identity",
    "coordination",
    "research",
    "review",
    "infrastructure",
    "outreach",
]


@dataclass
class ReputationEntry:
    """A single reputation data point."""
    entity_address: str
    domain: str
    score: float          # 0-100
    evidence: str
    source: str           # Who contributed this assessment
    source_type: str      # "self", "peer", "system", "retroactive"
    timestamp: str = ""
    weight: float = 1.0   # Weight multiplier for this entry

    def __post_init__(self):
        if not 0 <= self.score <= 100:
            raise ValueError(f"Score must be 0-100, got {self.score}")
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class ReputationProfile:
    """Aggregated reputation profile for an entity."""
    address: str
    name: str = ""
    entity_type: str = ""  # "person", "ai", "business"
    domain_scores: dict[str, float] = field(default_factory=dict)
    entry_count: int = 0
    last_updated: str = ""

    @property
    def overall_score(self) -> float:
        """Weighted average across all domains."""
        if not self.domain_scores:
            return 0.0
        return round(sum(self.domain_scores.values()) / len(self.domain_scores), 1)

    def top_domains(self, n: int = 3) -> list[tuple[str, float]]:
        """Top N domains by score."""
        sorted_domains = sorted(self.domain_scores.items(), key=lambda x: -x[1])
        return sorted_domains[:n]

    def to_dict(self) -> dict:
        return {
            "address": self.address,
            "name": self.name,
            "entity_type": self.entity_type,
            "domain_scores": self.domain_scores,
            "overall_score": self.overall_score,
            "entry_count": self.entry_count,
            "last_updated": self.last_updated,
        }


class ReputationSystem:
    """Multi-entity reputation tracking system.

    Collects reputation entries from multiple sources (self-assessment,
    peer review, system metrics) and aggregates them into per-entity
    profiles with domain-specific scores.
    """

    # Weight multipliers by source type
    SOURCE_WEIGHTS = {
        "self": 0.3,        # Self-assessment (lowest weight)
        "peer": 1.0,        # Peer review (full weight)
        "system": 0.8,      # System-generated (task completion, etc.)
        "retroactive": 0.7, # Historical assessment
    }

    def __init__(self):
        self._entries: list[ReputationEntry] = []
        self._entity_names: dict[str, str] = {}  # address → name
        self._entity_types: dict[str, str] = {}   # address → type

    def register_entity(self, address: str, name: str = "",
                        entity_type: str = "") -> None:
        """Register an entity for reputation tracking."""
        if name:
            self._entity_names[address] = name
        if entity_type:
            self._entity_types[address] = entity_type
        elif address.startswith("1."):
            self._entity_types[address] = "person"
        elif address.startswith("2."):
            self._entity_types[address] = "ai"
        elif address.startswith("3."):
            self._entity_types[address] = "business"

    def record_contribution(self, entity_address: str, domain: str,
                            score: float, evidence: str,
                            source: str = "", source_type: str = "system") -> ReputationEntry:
        """Record a reputation contribution for an entity.

        Args:
            entity_address: The entity being assessed
            domain: The domain (e.g., "code", "governance")
            score: Score 0-100
            evidence: What justifies this score
            source: Who provided this assessment
            source_type: "self", "peer", "system", or "retroactive"
        """
        entry = ReputationEntry(
            entity_address=entity_address,
            domain=domain,
            score=score,
            evidence=evidence,
            source=source or "system",
            source_type=source_type,
            weight=self.SOURCE_WEIGHTS.get(source_type, 0.5),
        )
        self._entries.append(entry)
        log.debug(f"Reputation entry: {entity_address} [{domain}] = {score} ({source_type})")
        return entry

    def record_peer_review(self, reviewer: str, entity_address: str,
                           domain: str, score: float, evidence: str) -> ReputationEntry:
        """Record a peer review score.

        Peer reviews carry the highest weight.
        """
        return self.record_contribution(
            entity_address=entity_address,
            domain=domain,
            score=score,
            evidence=evidence,
            source=reviewer,
            source_type="peer",
        )

    def record_task_completion(self, entity_address: str, domain: str,
                                success: bool, evidence: str = "") -> ReputationEntry:
        """Record a task completion as a system-generated reputation event."""
        score = 70 if success else 20  # Base score for success/failure
        return self.record_contribution(
            entity_address=entity_address,
            domain=domain,
            score=score,
            evidence=evidence or ("Task completed successfully" if success else "Task failed"),
            source="task_system",
            source_type="system",
        )

    def get_profile(self, entity_address: str) -> ReputationProfile:
        """Get the aggregated reputation profile for an entity.

        Scores are weighted averages across all entries for each domain.
        """
        entries = [e for e in self._entries if e.entity_address == entity_address]

        # Group by domain and compute weighted averages
        domain_entries: dict[str, list[ReputationEntry]] = {}
        for entry in entries:
            if entry.domain not in domain_entries:
                domain_entries[entry.domain] = []
            domain_entries[entry.domain].append(entry)

        domain_scores: dict[str, float] = {}
        for domain, d_entries in domain_entries.items():
            total_weight = sum(e.weight for e in d_entries)
            if total_weight == 0:
                domain_scores[domain] = 0.0
            else:
                weighted_sum = sum(e.score * e.weight for e in d_entries)
                domain_scores[domain] = round(weighted_sum / total_weight, 1)

        last_updated = ""
        if entries:
            last_updated = max(e.timestamp for e in entries)

        return ReputationProfile(
            address=entity_address,
            name=self._entity_names.get(entity_address, ""),
            entity_type=self._entity_types.get(entity_address, ""),
            domain_scores=domain_scores,
            entry_count=len(entries),
            last_updated=last_updated,
        )

    def get_domain_leaders(self, domain: str, top_n: int = 5) -> list[tuple[str, float]]:
        """Get the top entities in a specific domain."""
        # Collect all entities that have entries in this domain
        entities = set()
        for entry in self._entries:
            if entry.domain == domain:
                entities.add(entry.entity_address)

        # Score each entity
        scored = []
        for addr in entities:
            profile = self.get_profile(addr)
            if domain in profile.domain_scores:
                scored.append((addr, profile.domain_scores[domain]))

        scored.sort(key=lambda x: -x[1])
        return scored[:top_n]

    def get_all_profiles(self) -> list[ReputationProfile]:
        """Get profiles for all entities with reputation data."""
        entities = set(e.entity_address for e in self._entries)
        return [self.get_profile(addr) for addr in sorted(entities)]

    def compare(self, addr_a: str, addr_b: str) -> dict:
        """Compare two entities' reputation profiles."""
        a = self.get_profile(addr_a)
        b = self.get_profile(addr_b)

        all_domains = sorted(set(list(a.domain_scores.keys()) + list(b.domain_scores.keys())))
        comparison = {}
        for domain in all_domains:
            score_a = a.domain_scores.get(domain, 0)
            score_b = b.domain_scores.get(domain, 0)
            comparison[domain] = {
                "a": score_a,
                "b": score_b,
                "diff": round(score_a - score_b, 1),
            }

        return {
            "entity_a": {"address": addr_a, "name": a.name, "overall": a.overall_score},
            "entity_b": {"address": addr_b, "name": b.name, "overall": b.overall_score},
            "by_domain": comparison,
        }

    def entries_for(self, entity_address: str, domain: str | None = None) -> list[ReputationEntry]:
        """Get raw entries for an entity, optionally filtered by domain."""
        entries = [e for e in self._entries if e.entity_address == entity_address]
        if domain:
            entries = [e for e in entries if e.domain == domain]
        return entries

    def stats(self) -> dict:
        """System-wide reputation statistics."""
        entities = set(e.entity_address for e in self._entries)
        by_type: dict[str, int] = {}
        for addr in entities:
            etype = self._entity_types.get(addr, "unknown")
            by_type[etype] = by_type.get(etype, 0) + 1

        return {
            "total_entries": len(self._entries),
            "total_entities": len(entities),
            "by_entity_type": by_type,
            "domains_used": sorted(set(e.domain for e in self._entries)),
        }

    def save(self, path: str | Path) -> None:
        """Persist reputation data to a JSON file.

        Saves all entries, entity names, and entity types so the system
        can be fully restored across restarts.
        """
        data = {
            "entries": [asdict(e) for e in self._entries],
            "entity_names": self._entity_names,
            "entity_types": self._entity_types,
            "saved_at": datetime.now(timezone.utc).isoformat(),
        }
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp.replace(path)
        log.info(f"Reputation saved: {len(self._entries)} entries, {len(self._entity_names)} entities")

    def load(self, path: str | Path) -> bool:
        """Load reputation data from a JSON file.

        Returns True if data was loaded, False if file doesn't exist.
        Merges loaded data with any existing in-memory data.
        """
        path = Path(path)
        if not path.exists():
            return False
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            # Load entity metadata
            self._entity_names.update(data.get("entity_names", {}))
            self._entity_types.update(data.get("entity_types", {}))
            # Load entries (avoiding duplicates based on entity + domain + timestamp + source)
            existing_keys = {
                (e.entity_address, e.domain, e.timestamp, e.source)
                for e in self._entries
            }
            for entry_data in data.get("entries", []):
                key = (
                    entry_data["entity_address"], entry_data["domain"],
                    entry_data["timestamp"], entry_data["source"],
                )
                if key not in existing_keys:
                    self._entries.append(ReputationEntry(**entry_data))
                    existing_keys.add(key)
            log.info(f"Reputation loaded: {len(self._entries)} total entries")
            return True
        except Exception as e:
            log.warning(f"Could not load reputation data: {e}")
            return False
