"""
Hypernet Link

Links are first-class objects that represent relationships between nodes.
They have their own addresses in the 0.6.* space and can carry metadata,
verification chains, temporal validity, access control, and provenance.

A link is a directed edge in the Hypernet graph. Bidirectional links
are represented by a flag, not by duplicate edges.

Links match Objects (0.5.*) in structural depth:
  - Identity (address, type, relationship)
  - Endpoints (source + target with type constraints)
  - Properties (direction, weight, cardinality, temporal validity)
  - Metadata (created, evidence, tags, inverse tracking)
  - Verification (multi-level trust chain)
  - Access Control (owner, visibility, consent)
  - Provenance (history, signatures)
  - Lifecycle (proposed -> active -> deprecated -> archived)

LinkRegistry provides a service layer for creating, querying, and
managing links through the Store. Includes link governance: proposed
links require acceptance from the target before becoming active.

See: 0.6.0 Master Link Schema
"""

from __future__ import annotations
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional, TYPE_CHECKING

from .address import HypernetAddress

if TYPE_CHECKING:
    from .store import Store

log = logging.getLogger(__name__)


# =========================================================================
# Link Lifecycle
# =========================================================================

class LinkStatus:
    """Lifecycle states for links.

    Proposed -> Active -> Deprecated -> Archived
                                   \\-> Rejected (from Proposed)
    System-created links skip Proposed and go directly to Active.
    """
    PROPOSED = "proposed"       # Created but awaiting consent
    ACTIVE = "active"           # Accepted and in use
    DEPRECATED = "deprecated"   # Superseded but preserved for history
    ARCHIVED = "archived"       # Retained for provenance, hidden from traversal
    REJECTED = "rejected"       # Proposed but declined

    # Backward compatibility
    ACCEPTED = ACTIVE


# =========================================================================
# Verification Levels
# =========================================================================

class VerificationStatus:
    """Trust levels for link verification."""
    UNVERIFIED = "unverified"             # 0.0-0.2: Just asserted
    SELF_ATTESTED = "self_attested"       # 0.2-0.4: Creator confirms
    MUTUAL = "mutual"                     # 0.4-0.6: Both endpoints confirm
    PEER_VERIFIED = "peer_verified"       # 0.6-0.8: Third party confirms
    OFFICIALLY_VERIFIED = "officially_verified"  # 0.8-1.0: Documentary proof

    TRUST_SCORES = {
        "unverified": 0.1,
        "self_attested": 0.3,
        "mutual": 0.5,
        "peer_verified": 0.7,
        "officially_verified": 0.9,
    }

    @classmethod
    def trust_score(cls, status: str) -> float:
        return cls.TRUST_SCORES.get(status, 0.0)


# =========================================================================
# Link Type Categories (0.6.*)
# =========================================================================

# Category addresses
PERSON_RELATIONSHIP = "0.6.1"      # Person-to-person relationships
ORGANIZATIONAL = "0.6.2"           # Person-org and org-org relationships
CONTENT_REFERENCE = "0.6.3"        # Authorship, citations, derivation
SPATIAL_TEMPORAL = "0.6.4"         # Location and time relationships
HIERARCHICAL = "0.6.5"             # Parent-child, part-whole, taxonomy
SEMANTIC = "0.6.6"                 # Similarity, opposition, analogy
TASK_DEPENDENCY = "0.6.7"          # Dependencies, assignments, workflow
AI_IDENTITY = "0.6.8"             # AI instances, sessions, lineage
GOVERNANCE_TRUST = "0.6.9"        # Governance, voting, trust
ECONOMIC = "0.6.10"               # Transactions, contributions, revenue

# Backward-compatible aliases
PERSON_TO_PERSON = PERSON_RELATIONSHIP
PERSON_TO_OBJECT = ORGANIZATIONAL
OBJECT_TO_OBJECT = CONTENT_REFERENCE
TEMPORAL = SPATIAL_TEMPORAL
SPATIAL = SPATIAL_TEMPORAL

# Category metadata
LINK_CATEGORIES = {
    "0.6.1": "Person Relationship Links",
    "0.6.2": "Organizational Links",
    "0.6.3": "Content and Reference Links",
    "0.6.4": "Spatial and Temporal Links",
    "0.6.5": "Hierarchical Links",
    "0.6.6": "Semantic Links",
    "0.6.7": "Task and Dependency Links",
    "0.6.8": "AI and Identity Links",
    "0.6.9": "Governance and Trust Links",
    "0.6.10": "Economic Links",
}


# =========================================================================
# Standard Relationship Names
# =========================================================================

# 0.6.1 Person Relationships
KNOWS = "knows"
WORKS_WITH = "works_with"
REPORTS_TO = "reports_to"
MENTORS = "mentors"
FOLLOWS = "follows"
TRUSTS = "trusts"
ENDORSES = "endorses"

# 0.6.2 Organizational
MEMBER_OF = "member_of"
EMPLOYED_BY = "employed_by"
FOUNDED = "founded"
SUBSIDIARY_OF = "subsidiary_of"
PARTNERS_WITH = "partners_with"

# 0.6.3 Content & Reference
AUTHORED_BY = "authored_by"
CREATED_BY = "created_by"
CONTRIBUTED_TO = "contributed_to"
EDITED_BY = "edited_by"
CITES = "cites"
REFERENCES = "references"
QUOTES = "quotes"
DERIVED_FROM = "derived_from"
SUPERSEDES = "supersedes"
VERSION_OF = "version_of"
SUPPORTS = "supports"
CONTRADICTS = "contradicts"

# 0.6.4 Spatial & Temporal
LOCATED_AT = "located_at"
NEAR = "near"
PRECEDED_BY = "preceded_by"
DURING = "during"
CAUSED = "caused"
SCHEDULED_FOR = "scheduled_for"

# 0.6.5 Hierarchical
PARENT_OF = "parent_of"
CHILD_OF = "child_of"
CONTAINS = "contains"
PART_OF = "part_of"
BROADER_THAN = "broader_than"
NARROWER_THAN = "narrower_than"
INSTANCE_OF = "instance_of"
INHERITS_FROM = "inherits_from"
COMPOSED_OF = "composed_of"

# 0.6.6 Semantic
SIMILAR_TO = "similar_to"
OPPOSITE_OF = "opposite_of"
SYNONYM_OF = "synonym_of"
EXAMPLE_OF = "example_of"
ANALOGY_OF = "analogy_of"
IMPLIES = "implies"
CORROBORATES = "corroborates"
CONTEXTUALIZES = "contextualizes"
PATTERN_OF = "pattern_of"
PREREQUISITE_OF = "prerequisite_of"

# 0.6.7 Task & Dependency
DEPENDS_ON = "depends_on"
BLOCKS = "blocks"
ASSIGNED_TO = "assigned_to"
REVIEWED_BY = "reviewed_by"
SUBTASK_OF = "subtask_of"
MILESTONE_OF = "milestone_of"
IMPLEMENTS = "implements"
TESTS = "tests"
DELIVERS = "delivers"
PRECEDES = "precedes"

# 0.6.8 AI & Identity
INSTANCE_OF_ACCOUNT = "instance_of_account"
SESSION_OF = "session_of"
FORKED_FROM = "forked_from"
DIVERGED_FROM = "diverged_from"
CONVERGED_WITH = "converged_with"
GENERATED_BY = "generated_by"
TRAINED_ON = "trained_on"
REVIEWED_BY_AI = "reviewed_by_ai"
PERSONA_OF = "persona_of"
DATA_FROM = "data_from"
COMPANION_OF = "companion_of"

# 0.6.9 Governance & Trust
GOVERNED_BY = "governed_by"
PROPOSED_BY = "proposed_by"
VOTED_ON = "voted_on"
APPROVED_BY = "approved_by"
RATIFIED_BY = "ratified_by"
AUDITED_BY = "audited_by"
ENFORCES = "enforces"
APPEALS = "appeals"
TRUST_LINK = "trust_link"
REPUTATION_SOURCE = "reputation_source"
VOUCHES_FOR = "vouches_for"
GRANTED_PERMISSION = "granted_permission"

# 0.6.10 Economic
PAID_FOR = "paid_for"
EARNED_FROM = "earned_from"
CONTRIBUTED_VALUE = "contributed_value"
CREDIT_TO = "credit_to"
SHARED_REVENUE_WITH = "shared_revenue_with"
LICENSED_TO = "licensed_to"
SUBSCRIPTION_OF = "subscription_of"
ALLOCATED_TO = "allocated_to"

# Legacy aliases
RELATED_TO = "related_to"
CITED_BY = "cited_by"
DOCUMENTED_IN = "documented_in"
EXTENDS = "extends"
REPLACES = "replaces"
DUPLICATE_OF = "duplicate_of"
VARIANT_OF = "variant_of"
ATTENDED_BY = "attended_by"
SOURCE = "source"


# =========================================================================
# Link Type Definition Registry
# =========================================================================

@dataclass(frozen=True)
class LinkTypeDef:
    """Definition of a link type's structural properties.

    Parallel to how Objects have type definitions at 0.5.*,
    Links have type definitions capturing their behavioral properties.
    """
    name: str                          # e.g., "authored_by"
    category: str                      # e.g., "0.6.3"
    directed: bool = True
    symmetric: bool = False
    transitive: bool = False
    source_types: tuple[str, ...] = ()  # Allowed source object types (empty = any)
    target_types: tuple[str, ...] = ()  # Allowed target object types (empty = any)
    cardinality: str = "many_to_many"  # one_to_one | one_to_many | many_to_one | many_to_many
    inverse: Optional[str] = None      # Name of inverse relationship
    auto_create_inverse: bool = False
    consent_required: str = "none"     # none | source | target | both
    verification_method: str = "self_attestation"

    @property
    def is_bidirectional(self) -> bool:
        return not self.directed or self.symmetric


# Registry of known link types with their properties
LINK_TYPE_REGISTRY: dict[str, LinkTypeDef] = {}


def _register(*defs: LinkTypeDef) -> None:
    for d in defs:
        LINK_TYPE_REGISTRY[d.name] = d


# 0.6.1 Person Relationships
_register(
    LinkTypeDef("knows", PERSON_RELATIONSHIP, directed=False, symmetric=True, inverse=None, consent_required="both", verification_method="mutual_confirmation"),
    LinkTypeDef("works_with", PERSON_RELATIONSHIP, directed=False, symmetric=True, verification_method="organization_confirmation"),
    LinkTypeDef("reports_to", PERSON_RELATIONSHIP, directed=True, transitive=True, cardinality="many_to_one", inverse="manages", auto_create_inverse=True),
    LinkTypeDef("mentors", PERSON_RELATIONSHIP, directed=True, inverse="mentored_by", auto_create_inverse=True, verification_method="mutual_confirmation"),
    LinkTypeDef("follows", PERSON_RELATIONSHIP, directed=True, inverse="followed_by", consent_required="none"),
    LinkTypeDef("trusts", PERSON_RELATIONSHIP, directed=True, inverse="trusted_by"),
    LinkTypeDef("endorses", PERSON_RELATIONSHIP, directed=True, inverse="endorsed_by"),
)

# 0.6.3 Content & Reference
_register(
    LinkTypeDef("authored_by", CONTENT_REFERENCE, directed=True, inverse="authored", auto_create_inverse=True, verification_method="document_metadata"),
    LinkTypeDef("created_by", CONTENT_REFERENCE, directed=True, inverse="created", auto_create_inverse=True, verification_method="provenance_chain"),
    LinkTypeDef("contributed_to", CONTENT_REFERENCE, directed=True, inverse="has_contributor"),
    LinkTypeDef("cites", CONTENT_REFERENCE, directed=True, inverse="cited_by", auto_create_inverse=True, verification_method="document_review"),
    LinkTypeDef("references", CONTENT_REFERENCE, directed=True, inverse="referenced_by"),
    LinkTypeDef("derived_from", CONTENT_REFERENCE, directed=True, transitive=True, inverse="source_of"),
    LinkTypeDef("supersedes", CONTENT_REFERENCE, directed=True, transitive=True, inverse="superseded_by"),
    LinkTypeDef("supports", CONTENT_REFERENCE, directed=True, inverse="supported_by"),
    LinkTypeDef("contradicts", CONTENT_REFERENCE, directed=True, symmetric=True),
)

# 0.6.5 Hierarchical
_register(
    LinkTypeDef("parent_of", HIERARCHICAL, directed=True, cardinality="one_to_many", inverse="child_of", auto_create_inverse=True),
    LinkTypeDef("child_of", HIERARCHICAL, directed=True, cardinality="many_to_one", inverse="parent_of"),
    LinkTypeDef("part_of", HIERARCHICAL, directed=True, transitive=True, inverse="has_part"),
    LinkTypeDef("contains", HIERARCHICAL, directed=True, transitive=True, cardinality="one_to_many", inverse="contained_in"),
    LinkTypeDef("broader_than", HIERARCHICAL, directed=True, transitive=True, inverse="narrower_than"),
    LinkTypeDef("instance_of", HIERARCHICAL, directed=True, cardinality="many_to_one", inverse="has_instance"),
    LinkTypeDef("inherits_from", HIERARCHICAL, directed=True, transitive=True, inverse="inherited_by"),
)

# 0.6.6 Semantic
_register(
    LinkTypeDef("similar_to", SEMANTIC, directed=False, symmetric=True),
    LinkTypeDef("opposite_of", SEMANTIC, directed=False, symmetric=True),
    LinkTypeDef("synonym_of", SEMANTIC, directed=False, symmetric=True, transitive=True),
    LinkTypeDef("example_of", SEMANTIC, directed=True, inverse="exemplified_by"),
    LinkTypeDef("analogy_of", SEMANTIC, directed=False, symmetric=True),
    LinkTypeDef("implies", SEMANTIC, directed=True, transitive=True, inverse="implied_by"),
    LinkTypeDef("corroborates", SEMANTIC, directed=True, inverse="corroborated_by"),
    LinkTypeDef("contextualizes", SEMANTIC, directed=True, inverse="contextualized_by"),
    LinkTypeDef("pattern_of", SEMANTIC, directed=True, inverse="follows_pattern"),
)

# 0.6.7 Task & Dependency
_register(
    LinkTypeDef("depends_on", TASK_DEPENDENCY, directed=True, transitive=True, inverse="dependency_of"),
    LinkTypeDef("blocks", TASK_DEPENDENCY, directed=True, transitive=True, inverse="blocked_by"),
    LinkTypeDef("assigned_to", TASK_DEPENDENCY, directed=True, inverse="assignment_of", consent_required="target"),
    LinkTypeDef("reviewed_by", TASK_DEPENDENCY, directed=True, inverse="reviews"),
    LinkTypeDef("subtask_of", TASK_DEPENDENCY, directed=True, transitive=True, cardinality="many_to_one", inverse="has_subtask"),
    LinkTypeDef("implements", TASK_DEPENDENCY, directed=True, inverse="implemented_by"),
    LinkTypeDef("tests", TASK_DEPENDENCY, directed=True, inverse="tested_by"),
    LinkTypeDef("delivers", TASK_DEPENDENCY, directed=True, inverse="delivered_by"),
)

# 0.6.8 AI & Identity
_register(
    LinkTypeDef("instance_of_account", AI_IDENTITY, directed=True, cardinality="many_to_one", inverse="has_instance"),
    LinkTypeDef("session_of", AI_IDENTITY, directed=True, cardinality="many_to_one", inverse="has_session"),
    LinkTypeDef("forked_from", AI_IDENTITY, directed=True, transitive=True, inverse="fork_of"),
    LinkTypeDef("diverged_from", AI_IDENTITY, directed=True),
    LinkTypeDef("converged_with", AI_IDENTITY, directed=False, symmetric=True),
    LinkTypeDef("generated_by", AI_IDENTITY, directed=True, inverse="generated"),
    LinkTypeDef("reviewed_by_ai", AI_IDENTITY, directed=True, inverse="ai_reviewed"),
    LinkTypeDef("companion_of", AI_IDENTITY, directed=True, cardinality="one_to_one", inverse="has_companion", consent_required="both"),
    LinkTypeDef("persona_of", AI_IDENTITY, directed=True, cardinality="many_to_one", inverse="has_persona"),
)

# 0.6.9 Governance & Trust
_register(
    LinkTypeDef("governed_by", GOVERNANCE_TRUST, directed=True, transitive=True, inverse="governs"),
    LinkTypeDef("proposed_by", GOVERNANCE_TRUST, directed=True, inverse="proposed"),
    LinkTypeDef("voted_on", GOVERNANCE_TRUST, directed=True, inverse="voter_in"),
    LinkTypeDef("approved_by", GOVERNANCE_TRUST, directed=True, inverse="approver_of"),
    LinkTypeDef("audited_by", GOVERNANCE_TRUST, directed=True, inverse="audit_of"),
    LinkTypeDef("trust_link", GOVERNANCE_TRUST, directed=True),
    LinkTypeDef("vouches_for", GOVERNANCE_TRUST, directed=True, inverse="vouched_by", consent_required="target"),
    LinkTypeDef("granted_permission", GOVERNANCE_TRUST, directed=True, inverse="has_permission"),
)

# 0.6.10 Economic
_register(
    LinkTypeDef("paid_for", ECONOMIC, directed=True, inverse="payment_of"),
    LinkTypeDef("earned_from", ECONOMIC, directed=True, inverse="earnings_source"),
    LinkTypeDef("contributed_value", ECONOMIC, directed=True, inverse="value_contribution"),
    LinkTypeDef("credit_to", ECONOMIC, directed=True, inverse="credited_by"),
    LinkTypeDef("shared_revenue_with", ECONOMIC, directed=True, inverse="revenue_share_from"),
    LinkTypeDef("licensed_to", ECONOMIC, directed=True, inverse="license_from"),
    LinkTypeDef("allocated_to", ECONOMIC, directed=True, inverse="resource_allocation"),
)

# Legacy/generic
_register(
    LinkTypeDef("related_to", CONTENT_REFERENCE, directed=False, symmetric=True),
    LinkTypeDef("extends", CONTENT_REFERENCE, directed=True, inverse="extended_by"),
    LinkTypeDef("replaces", CONTENT_REFERENCE, directed=True, inverse="replaced_by"),
)


def _register_if_missing(*defs: LinkTypeDef) -> None:
    for d in defs:
        if d.name not in LINK_TYPE_REGISTRY:
            LINK_TYPE_REGISTRY[d.name] = d


# Common database-first link vocabulary. Existing hand-tuned definitions above
# stay authoritative; this fills out the runtime registry so docs and API clients
# have 100+ common relationship names available for validation and discovery.
COMMON_LINK_TYPE_SPECS: tuple[tuple[str, str, bool, bool, bool, Optional[str]], ...] = (
    # Identity and actors
    ("knows", PERSON_RELATIONSHIP, False, True, False, None),
    ("related_to", PERSON_RELATIONSHIP, False, True, False, None),
    ("spouse_of", PERSON_RELATIONSHIP, False, True, False, None),
    ("parent_of", HIERARCHICAL, True, False, True, "child_of"),
    ("guardian_of", PERSON_RELATIONSHIP, True, False, False, "guarded_by"),
    ("member_of_household", PERSON_RELATIONSHIP, True, False, False, "household_has_member"),
    ("represents", PERSON_RELATIONSHIP, True, False, False, "represented_by"),
    ("acts_as", PERSON_RELATIONSHIP, True, False, False, "role_held_by"),
    ("owns_identity", PERSON_RELATIONSHIP, True, False, False, "identity_owned_by"),
    ("delegates_to", PERSON_RELATIONSHIP, True, False, False, "delegated_by"),
    # Authorship and provenance
    ("authored_by", CONTENT_REFERENCE, True, False, False, "authored"),
    ("created_by", CONTENT_REFERENCE, True, False, False, "created"),
    ("edited_by", CONTENT_REFERENCE, True, False, False, "edited"),
    ("contributed_to", CONTENT_REFERENCE, True, False, False, "has_contributor"),
    ("generated_by", AI_IDENTITY, True, False, False, "generated"),
    ("imported_from", CONTENT_REFERENCE, True, False, False, "source_imported"),
    ("derived_from", CONTENT_REFERENCE, True, False, True, "source_of"),
    ("version_of", CONTENT_REFERENCE, True, False, True, "has_version"),
    ("supersedes", CONTENT_REFERENCE, True, False, True, "superseded_by"),
    ("archived_from", CONTENT_REFERENCE, True, False, False, "archived_as"),
    # Containment and hierarchy
    ("contains", HIERARCHICAL, True, False, True, "contained_in"),
    ("part_of", HIERARCHICAL, True, False, True, "has_part"),
    ("instance_of", HIERARCHICAL, True, False, False, "has_instance"),
    ("type_of", HIERARCHICAL, True, False, False, "has_type"),
    ("broader_than", HIERARCHICAL, True, False, True, "narrower_than"),
    ("narrower_than", HIERARCHICAL, True, False, True, "broader_than"),
    ("parent_collection_of", HIERARCHICAL, True, False, True, "child_collection_of"),
    ("located_within", HIERARCHICAL, True, False, True, "spatially_contains"),
    ("composed_of", HIERARCHICAL, True, False, True, "component_of"),
    ("indexes", HIERARCHICAL, True, False, False, "indexed_by"),
    # Semantic and knowledge
    ("about", SEMANTIC, True, False, False, "has_aboutness"),
    ("cites", CONTENT_REFERENCE, True, False, False, "cited_by"),
    ("supports", CONTENT_REFERENCE, True, False, False, "supported_by"),
    ("contradicts", CONTENT_REFERENCE, True, False, False, "contradicted_by"),
    ("explains", SEMANTIC, True, False, False, "explained_by"),
    ("answers", SEMANTIC, True, False, False, "answered_by"),
    ("asks", SEMANTIC, True, False, False, "asked_by"),
    ("similar_to", SEMANTIC, False, True, False, None),
    ("opposite_of", SEMANTIC, False, True, False, None),
    ("implies", SEMANTIC, True, False, True, "implied_by"),
    # Temporal and causal
    ("before", SPATIAL_TEMPORAL, True, False, True, "after"),
    ("after", SPATIAL_TEMPORAL, True, False, True, "before"),
    ("during", SPATIAL_TEMPORAL, True, False, False, "contains_time"),
    ("overlaps", SPATIAL_TEMPORAL, False, True, False, None),
    ("scheduled_for", SPATIAL_TEMPORAL, True, False, False, "has_scheduled_item"),
    ("triggered_by", SPATIAL_TEMPORAL, True, False, False, "triggered"),
    ("causes", SPATIAL_TEMPORAL, True, False, True, "caused_by"),
    ("blocks_until", SPATIAL_TEMPORAL, True, False, False, "unblocks"),
    ("expires_at", SPATIAL_TEMPORAL, True, False, False, "expiration_of"),
    ("recurring_on", SPATIAL_TEMPORAL, True, False, False, "recurrence_of"),
    # Spatial and movement
    ("located_at", SPATIAL_TEMPORAL, True, False, False, "location_of"),
    ("near", SPATIAL_TEMPORAL, False, True, False, None),
    ("adjacent_to", SPATIAL_TEMPORAL, False, True, False, None),
    ("route_from", SPATIAL_TEMPORAL, True, False, False, "route_origin_for"),
    ("route_to", SPATIAL_TEMPORAL, True, False, False, "route_destination_for"),
    ("within_radius_of", SPATIAL_TEMPORAL, True, False, False, "radius_contains"),
    ("visible_from", SPATIAL_TEMPORAL, True, False, False, "can_see"),
    ("moved_from", SPATIAL_TEMPORAL, True, False, False, "move_origin_for"),
    ("moved_to", SPATIAL_TEMPORAL, True, False, False, "move_destination_for"),
    ("originated_at", SPATIAL_TEMPORAL, True, False, False, "origin_of"),
    # Work and dependency
    ("assigned_to", TASK_DEPENDENCY, True, False, False, "assignment_of"),
    ("depends_on", TASK_DEPENDENCY, True, False, True, "dependency_of"),
    ("blocks", TASK_DEPENDENCY, True, False, True, "blocked_by"),
    ("required_by", TASK_DEPENDENCY, True, False, False, "requires"),
    ("implements", TASK_DEPENDENCY, True, False, False, "implemented_by"),
    ("verifies", TASK_DEPENDENCY, True, False, False, "verified_by"),
    ("reviews", TASK_DEPENDENCY, True, False, False, "reviewed_by"),
    ("approves", TASK_DEPENDENCY, True, False, False, "approved_by"),
    ("delivers", TASK_DEPENDENCY, True, False, False, "delivered_by"),
    ("part_of_project", TASK_DEPENDENCY, True, False, True, "project_contains"),
    # Communication and social
    ("sent_to", CONTENT_REFERENCE, True, False, False, "received"),
    ("sent_from", CONTENT_REFERENCE, True, False, False, "sent"),
    ("mentions", CONTENT_REFERENCE, True, False, False, "mentioned_by"),
    ("replies_to", CONTENT_REFERENCE, True, False, True, "has_reply"),
    ("forwards", CONTENT_REFERENCE, True, False, True, "forwarded_by"),
    ("subscribes_to", CONTENT_REFERENCE, True, False, False, "subscribed_by"),
    ("follows", PERSON_RELATIONSHIP, True, False, False, "followed_by"),
    ("likes", CONTENT_REFERENCE, True, False, False, "liked_by"),
    ("shares", CONTENT_REFERENCE, True, False, False, "shared_by"),
    ("notifies", CONTENT_REFERENCE, True, False, False, "notified_by"),
    # Governance and trust
    ("governed_by", GOVERNANCE_TRUST, True, False, True, "governs"),
    ("permission_grants", GOVERNANCE_TRUST, True, False, False, "granted_permission"),
    ("consented_by", GOVERNANCE_TRUST, True, False, False, "consented_to"),
    ("audited_by", GOVERNANCE_TRUST, True, False, False, "audit_of"),
    ("voted_on", GOVERNANCE_TRUST, True, False, False, "has_vote"),
    ("ratified_by", GOVERNANCE_TRUST, True, False, False, "ratified"),
    ("disputes", GOVERNANCE_TRUST, True, False, False, "disputed_by"),
    ("resolves", GOVERNANCE_TRUST, True, False, False, "resolved_by"),
    ("trust_asserts", GOVERNANCE_TRUST, True, False, False, "trusted_by"),
    ("reputation_source", GOVERNANCE_TRUST, True, False, False, "has_reputation_source"),
    # Economic and resource
    ("paid_for", ECONOMIC, True, False, False, "payment_of"),
    ("billed_to", ECONOMIC, True, False, False, "received_bill"),
    ("purchased_from", ECONOMIC, True, False, False, "sold"),
    ("allocated_to", ECONOMIC, True, False, False, "allocation_from"),
    ("funded_by", ECONOMIC, True, False, False, "funds"),
    ("earns_from", ECONOMIC, True, False, False, "earnings_source"),
    ("credits", ECONOMIC, True, False, False, "credited_by"),
    ("licenses_to", ECONOMIC, True, False, False, "license_from"),
    ("compensates", ECONOMIC, True, False, False, "compensated_by"),
    ("values_at", ECONOMIC, True, False, False, "valuation_of"),
)

_register_if_missing(*(
    LinkTypeDef(
        name=name,
        category=category,
        directed=directed,
        symmetric=symmetric,
        transitive=transitive,
        inverse=inverse,
    )
    for name, category, directed, symmetric, transitive, inverse in COMMON_LINK_TYPE_SPECS
))


def get_link_type_def(relationship: str) -> Optional[LinkTypeDef]:
    """Look up a link type definition by relationship name."""
    return LINK_TYPE_REGISTRY.get(relationship)


def list_link_type_defs() -> list[dict[str, Any]]:
    """Return all registered link type definitions for API/schema clients."""
    return [
        {
            "relationship": d.name,
            "category": d.category,
            "category_name": LINK_CATEGORIES.get(d.category, "Unknown"),
            "directed": d.directed,
            "symmetric": d.symmetric,
            "transitive": d.transitive,
            "cardinality": d.cardinality,
            "inverse": d.inverse,
            "auto_create_inverse": d.auto_create_inverse,
            "consent_required": d.consent_required,
            "verification_method": d.verification_method,
        }
        for d in sorted(LINK_TYPE_REGISTRY.values(), key=lambda item: (item.category, item.name))
    ]


def link_type_summary() -> dict[str, Any]:
    """Return compact link taxonomy counts."""
    by_category: dict[str, int] = {}
    for d in LINK_TYPE_REGISTRY.values():
        by_category[d.category] = by_category.get(d.category, 0) + 1
    return {
        "total_defined_link_types": len(LINK_TYPE_REGISTRY),
        "categories": {
            category: {"name": LINK_CATEGORIES.get(category, "Unknown"), "count": count}
            for category, count in sorted(by_category.items())
        },
    }


# =========================================================================
# Verifier Record
# =========================================================================

@dataclass
class Verifier:
    """A verification record for a link."""
    entity: str                    # HA of verifier
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    method: str = "self_attestation"
    evidence: Optional[str] = None  # HA of evidence

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity": self.entity,
            "timestamp": self.timestamp.isoformat(),
            "method": self.method,
            "evidence": self.evidence,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Verifier:
        return cls(
            entity=d["entity"],
            timestamp=datetime.fromisoformat(d["timestamp"]) if d.get("timestamp") else datetime.now(timezone.utc),
            method=d.get("method", "self_attestation"),
            evidence=d.get("evidence"),
        )


# =========================================================================
# Link
# =========================================================================

@dataclass
class Link:
    """A directed relationship between two nodes in the Hypernet graph.

    Matches Object (Node) in structural depth: identity, metadata,
    access control, verification, provenance, and lifecycle.
    """

    # --- Identity ---
    from_address: HypernetAddress
    to_address: HypernetAddress
    link_type: str                        # Category from 0.6.* (e.g., "0.6.3")
    relationship: str                     # Specific relationship (e.g., "authored_by")
    address: Optional[HypernetAddress] = None  # Link's own address in 0.6.* space

    # --- Properties ---
    strength: float = 1.0                 # 0.0 to 1.0 confidence/weight
    bidirectional: bool = False
    sort_order: Optional[int] = None      # For ordered relationships

    # --- Temporal Validity ---
    valid_from: Optional[datetime] = None   # When link becomes active
    valid_until: Optional[datetime] = None  # When link expires (null = indefinite)

    # --- Metadata ---
    data: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = ""                  # HA of creator
    creation_method: str = "manual"       # manual | import | inference | system
    tags: list[str] = field(default_factory=list)

    # --- Inverse Tracking ---
    inverse_relationship: Optional[str] = None  # Name of inverse (e.g., "authored")
    inverse_link_address: Optional[str] = None  # HA of the inverse link

    # --- Evidence ---
    evidence: list[dict[str, Any]] = field(default_factory=list)
    # Each: {"type": "document|assertion|inference", "reference": "HA", "confidence": 0.9}

    # --- Verification ---
    verification_status: str = VerificationStatus.UNVERIFIED
    verifiers: list[Verifier] = field(default_factory=list)
    trust_score: float = 0.1

    # --- Access Control ---
    owner: str = ""                       # HA of link owner
    visibility: str = "public"            # public | restricted | private | endpoints_only
    source_consented: bool = True
    target_consented: bool = True
    consent_required: str = "none"        # none | source | target | both

    # --- Lifecycle ---
    status: str = LinkStatus.ACTIVE
    proposed_by: str = ""                 # Who proposed this link
    deprecated_at: Optional[datetime] = None
    deprecated_reason: str = ""
    replacement_link: Optional[str] = None  # HA of replacement

    # --- Provenance ---
    history: list[dict[str, Any]] = field(default_factory=list)
    # Each: {"version": "1.0", "timestamp": "...", "change": "...", "by": "..."}

    def __post_init__(self):
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError(f"Link strength must be 0.0-1.0, got {self.strength}")
        if self.from_address == self.to_address:
            raise ValueError("Self-links are not allowed")
        # Auto-compute trust score from verification status
        if self.trust_score == 0.1 and self.verification_status != VerificationStatus.UNVERIFIED:
            self.trust_score = VerificationStatus.trust_score(self.verification_status)

    # --- Status Properties ---

    def is_current_at(self, at: datetime) -> bool:
        """True if within temporal validity window at a given timestamp.

        Used for as-of / time-travel queries on the link graph. A link
        with no valid_from is considered to have always existed; with no
        valid_until, to extend indefinitely.
        """
        if at.tzinfo is None:
            at = at.replace(tzinfo=timezone.utc)
        if self.valid_from and at < self.valid_from:
            return False
        if self.valid_until and at >= self.valid_until:
            return False
        return True

    def is_active_at(self, at: datetime) -> bool:
        """True if status is ACTIVE and link is temporally valid at the given time."""
        if self.status != LinkStatus.ACTIVE:
            return False
        return self.is_current_at(at)

    @property
    def is_active(self) -> bool:
        """True if link is active and usable in graph traversal right now."""
        return self.is_active_at(datetime.now(timezone.utc))

    @property
    def is_pending(self) -> bool:
        """True if link is proposed but not yet accepted."""
        return self.status == LinkStatus.PROPOSED

    @property
    def is_current(self) -> bool:
        """True if within temporal validity window right now."""
        return self.is_current_at(datetime.now(timezone.utc))

    @property
    def is_deprecated(self) -> bool:
        return self.status == LinkStatus.DEPRECATED

    @property
    def is_archived(self) -> bool:
        return self.status == LinkStatus.ARCHIVED

    @property
    def type_def(self) -> Optional[LinkTypeDef]:
        """Look up this link's type definition."""
        return get_link_type_def(self.relationship)

    @property
    def is_transitive(self) -> bool:
        """True if this relationship type is transitive."""
        td = self.type_def
        return td.transitive if td else False

    @property
    def is_symmetric(self) -> bool:
        """True if this relationship type is symmetric."""
        td = self.type_def
        return td.symmetric if td else self.bidirectional

    # --- Graph Operations ---

    def connects(self, address: HypernetAddress) -> bool:
        """True if this link connects to/from the given address."""
        if self.from_address == address:
            return True
        if self.bidirectional and self.to_address == address:
            return True
        return False

    def other_end(self, address: HypernetAddress) -> Optional[HypernetAddress]:
        """Given one end of the link, return the other end."""
        if self.from_address == address:
            return self.to_address
        if self.to_address == address and self.bidirectional:
            return self.from_address
        return None

    # --- Verification ---

    def verify(self, entity: str, method: str = "self_attestation",
               evidence: Optional[str] = None) -> None:
        """Add a verification record and update trust score."""
        self.verifiers.append(Verifier(
            entity=entity,
            method=method,
            evidence=evidence,
        ))
        # Upgrade verification status based on verifier count and type
        if len(self.verifiers) >= 3:
            self.verification_status = VerificationStatus.PEER_VERIFIED
        elif len(self.verifiers) >= 2:
            self.verification_status = VerificationStatus.MUTUAL
        else:
            self.verification_status = VerificationStatus.SELF_ATTESTED
        self.trust_score = VerificationStatus.trust_score(self.verification_status)

    # --- Lifecycle ---

    def accept(self) -> None:
        """Accept a proposed link."""
        if self.status == LinkStatus.PROPOSED:
            self.status = LinkStatus.ACTIVE
            self._record_change("Accepted")

    def reject(self, reason: str = "") -> None:
        """Reject a proposed link."""
        if self.status == LinkStatus.PROPOSED:
            self.status = LinkStatus.REJECTED
            if reason:
                self.data["rejection_reason"] = reason
            self._record_change(f"Rejected: {reason}" if reason else "Rejected")

    def deprecate(self, reason: str = "", replacement: Optional[str] = None) -> None:
        """Deprecate a link."""
        self.status = LinkStatus.DEPRECATED
        self.deprecated_at = datetime.now(timezone.utc)
        self.deprecated_reason = reason
        self.replacement_link = replacement
        self._record_change(f"Deprecated: {reason}" if reason else "Deprecated")

    def archive(self) -> None:
        """Archive a link (hide from traversal but preserve for provenance)."""
        self.status = LinkStatus.ARCHIVED
        self._record_change("Archived")

    def restore(self) -> None:
        """Restore a deprecated or archived link to active."""
        self.status = LinkStatus.ACTIVE
        self.deprecated_at = None
        self.deprecated_reason = ""
        self._record_change("Restored to active")

    def _record_change(self, change: str) -> None:
        """Record a change in the provenance history."""
        self.history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "change": change,
            "by": self.created_by or "system",
        })

    # --- Serialization ---

    def to_dict(self) -> dict[str, Any]:
        return {
            "from_address": str(self.from_address),
            "to_address": str(self.to_address),
            "link_type": self.link_type,
            "relationship": self.relationship,
            "address": str(self.address) if self.address else None,
            "strength": self.strength,
            "bidirectional": self.bidirectional,
            "sort_order": self.sort_order,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "creation_method": self.creation_method,
            "tags": self.tags,
            "inverse_relationship": self.inverse_relationship,
            "inverse_link_address": self.inverse_link_address,
            "evidence": self.evidence,
            "verification_status": self.verification_status,
            "verifiers": [v.to_dict() for v in self.verifiers],
            "trust_score": self.trust_score,
            "owner": self.owner,
            "visibility": self.visibility,
            "source_consented": self.source_consented,
            "target_consented": self.target_consented,
            "consent_required": self.consent_required,
            "status": self.status,
            "proposed_by": self.proposed_by,
            "deprecated_at": self.deprecated_at.isoformat() if self.deprecated_at else None,
            "deprecated_reason": self.deprecated_reason,
            "replacement_link": self.replacement_link,
            "history": self.history,
        }

    @staticmethod
    def _normalize_status(status: str) -> str:
        """Map legacy status values to current ones."""
        return {"accepted": LinkStatus.ACTIVE, "rejected": LinkStatus.REJECTED}.get(status, status)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Link:
        return cls(
            from_address=HypernetAddress.parse(d["from_address"]),
            to_address=HypernetAddress.parse(d["to_address"]),
            link_type=d["link_type"],
            relationship=d["relationship"],
            address=HypernetAddress.parse(d["address"]) if d.get("address") else None,
            strength=d.get("strength", 1.0),
            bidirectional=d.get("bidirectional", False),
            sort_order=d.get("sort_order"),
            valid_from=datetime.fromisoformat(d["valid_from"]) if d.get("valid_from") else None,
            valid_until=datetime.fromisoformat(d["valid_until"]) if d.get("valid_until") else None,
            data=d.get("data", {}),
            created_at=datetime.fromisoformat(d["created_at"]) if d.get("created_at") else datetime.now(timezone.utc),
            created_by=d.get("created_by", ""),
            creation_method=d.get("creation_method", "manual"),
            tags=d.get("tags", []),
            inverse_relationship=d.get("inverse_relationship"),
            inverse_link_address=d.get("inverse_link_address"),
            evidence=d.get("evidence", []),
            verification_status=d.get("verification_status", VerificationStatus.UNVERIFIED),
            verifiers=[Verifier.from_dict(v) for v in d.get("verifiers", [])],
            trust_score=d.get("trust_score", 0.1),
            owner=d.get("owner", ""),
            visibility=d.get("visibility", "public"),
            source_consented=d.get("source_consented", True),
            target_consented=d.get("target_consented", True),
            consent_required=d.get("consent_required", "none"),
            status=cls._normalize_status(d.get("status", LinkStatus.ACTIVE)),
            proposed_by=d.get("proposed_by", ""),
            deprecated_at=datetime.fromisoformat(d["deprecated_at"]) if d.get("deprecated_at") else None,
            deprecated_reason=d.get("deprecated_reason", ""),
            replacement_link=d.get("replacement_link"),
            history=d.get("history", []),
        )

    def __repr__(self) -> str:
        arrow = "<->" if self.bidirectional else "->"
        status_marker = f" [{self.status}]" if self.status != LinkStatus.ACTIVE else ""
        return f"Link({self.from_address} {arrow} {self.to_address} [{self.relationship}]{status_marker})"


# =========================================================================
# LinkRegistry — Service Layer
# =========================================================================

class LinkRegistry:
    """Service layer for creating and querying links in the Hypernet.

    Wraps the Store's link operations with convenience methods for
    common relationship types, type validation, governance, and statistics.
    """

    def __init__(self, store: Store):
        self.store = store

    # ----- Core Link Creation -----

    def link(
        self,
        from_addr: str | HypernetAddress,
        to_addr: str | HypernetAddress,
        relationship: str,
        link_type: str = CONTENT_REFERENCE,
        bidirectional: bool = False,
        strength: float = 1.0,
        data: dict | None = None,
        created_by: str = "",
        creation_method: str = "manual",
        tags: list[str] | None = None,
        valid_from: datetime | None = None,
        valid_until: datetime | None = None,
    ) -> Link:
        """Create and store a link between two addresses."""
        if isinstance(from_addr, str):
            from_addr = HypernetAddress.parse(from_addr)
        if isinstance(to_addr, str):
            to_addr = HypernetAddress.parse(to_addr)

        # Look up type definition for defaults
        type_def = get_link_type_def(relationship)
        if type_def:
            if not bidirectional and type_def.is_bidirectional:
                bidirectional = True
            if link_type == CONTENT_REFERENCE and type_def.category != CONTENT_REFERENCE:
                link_type = type_def.category

        # Determine inverse
        inverse_rel = None
        if type_def and type_def.inverse:
            inverse_rel = type_def.inverse

        new_link = Link(
            from_address=from_addr,
            to_address=to_addr,
            link_type=link_type,
            relationship=relationship,
            bidirectional=bidirectional,
            strength=strength,
            data=data or {},
            created_by=created_by,
            creation_method=creation_method,
            tags=tags or [],
            valid_from=valid_from,
            valid_until=valid_until,
            inverse_relationship=inverse_rel,
        )
        self.store.put_link(new_link)
        log.debug(f"Created link: {new_link}")
        return new_link

    # ----- Convenience Methods for Common Relationships -----

    def authored_by(self, doc: str | HypernetAddress, author: str | HypernetAddress, **kw) -> Link:
        return self.link(doc, author, AUTHORED_BY, link_type=CONTENT_REFERENCE, **kw)

    def created_by(self, item: str | HypernetAddress, creator: str | HypernetAddress, **kw) -> Link:
        return self.link(item, creator, CREATED_BY, link_type=CONTENT_REFERENCE, **kw)

    def contributed_to(self, contributor: str | HypernetAddress, item: str | HypernetAddress, **kw) -> Link:
        return self.link(contributor, item, CONTRIBUTED_TO, link_type=CONTENT_REFERENCE, **kw)

    def depends_on(self, task: str | HypernetAddress, dependency: str | HypernetAddress, **kw) -> Link:
        return self.link(task, dependency, DEPENDS_ON, link_type=TASK_DEPENDENCY, **kw)

    def extends(self, item: str | HypernetAddress, base: str | HypernetAddress, **kw) -> Link:
        return self.link(item, base, EXTENDS, link_type=CONTENT_REFERENCE, **kw)

    def references(self, source: str | HypernetAddress, target: str | HypernetAddress, **kw) -> Link:
        return self.link(source, target, REFERENCES, link_type=CONTENT_REFERENCE, **kw)

    def contains(self, parent: str | HypernetAddress, child: str | HypernetAddress, **kw) -> Link:
        return self.link(parent, child, CONTAINS, link_type=HIERARCHICAL, **kw)

    def reviewed_by(self, item: str | HypernetAddress, reviewer: str | HypernetAddress, **kw) -> Link:
        return self.link(item, reviewer, REVIEWED_BY, link_type=TASK_DEPENDENCY, **kw)

    def replaces(self, new_item: str | HypernetAddress, old_item: str | HypernetAddress, **kw) -> Link:
        return self.link(new_item, old_item, REPLACES, link_type=CONTENT_REFERENCE, **kw)

    def implements(self, code: str | HypernetAddress, spec: str | HypernetAddress, **kw) -> Link:
        return self.link(code, spec, IMPLEMENTS, link_type=TASK_DEPENDENCY, **kw)

    def related(self, a: str | HypernetAddress, b: str | HypernetAddress, **kw) -> Link:
        return self.link(a, b, RELATED_TO, bidirectional=True, **kw)

    # 0.6.5 Hierarchical
    def parent_of(self, parent: str | HypernetAddress, child: str | HypernetAddress, **kw) -> Link:
        return self.link(parent, child, PARENT_OF, link_type=HIERARCHICAL, **kw)

    def part_of(self, part: str | HypernetAddress, whole: str | HypernetAddress, **kw) -> Link:
        return self.link(part, whole, PART_OF, link_type=HIERARCHICAL, **kw)

    def instance_of(self, instance: str | HypernetAddress, type_addr: str | HypernetAddress, **kw) -> Link:
        return self.link(instance, type_addr, INSTANCE_OF, link_type=HIERARCHICAL, **kw)

    # 0.6.6 Semantic
    def similar_to(self, a: str | HypernetAddress, b: str | HypernetAddress, **kw) -> Link:
        return self.link(a, b, SIMILAR_TO, link_type=SEMANTIC, bidirectional=True, **kw)

    def implies(self, premise: str | HypernetAddress, conclusion: str | HypernetAddress, **kw) -> Link:
        return self.link(premise, conclusion, IMPLIES, link_type=SEMANTIC, **kw)

    # 0.6.7 Task
    def blocks(self, blocker: str | HypernetAddress, blocked: str | HypernetAddress, **kw) -> Link:
        return self.link(blocker, blocked, BLOCKS, link_type=TASK_DEPENDENCY, **kw)

    def assigned_to(self, task: str | HypernetAddress, assignee: str | HypernetAddress, **kw) -> Link:
        return self.link(task, assignee, ASSIGNED_TO, link_type=TASK_DEPENDENCY, **kw)

    def subtask_of(self, subtask: str | HypernetAddress, parent: str | HypernetAddress, **kw) -> Link:
        return self.link(subtask, parent, SUBTASK_OF, link_type=TASK_DEPENDENCY, **kw)

    # 0.6.8 AI & Identity
    def instance_of_account(self, instance: str | HypernetAddress, account: str | HypernetAddress, **kw) -> Link:
        return self.link(instance, account, INSTANCE_OF_ACCOUNT, link_type=AI_IDENTITY, **kw)

    def generated_by(self, content: str | HypernetAddress, ai: str | HypernetAddress, **kw) -> Link:
        return self.link(content, ai, GENERATED_BY, link_type=AI_IDENTITY, **kw)

    def companion_of(self, ai: str | HypernetAddress, human: str | HypernetAddress, **kw) -> Link:
        return self.link(ai, human, COMPANION_OF, link_type=AI_IDENTITY, **kw)

    # 0.6.9 Governance
    def governed_by(self, entity: str | HypernetAddress, standard: str | HypernetAddress, **kw) -> Link:
        return self.link(entity, standard, GOVERNED_BY, link_type=GOVERNANCE_TRUST, **kw)

    def approved_by(self, item: str | HypernetAddress, authority: str | HypernetAddress, **kw) -> Link:
        return self.link(item, authority, APPROVED_BY, link_type=GOVERNANCE_TRUST, **kw)

    def trust(self, truster: str | HypernetAddress, trustee: str | HypernetAddress, **kw) -> Link:
        return self.link(truster, trustee, TRUST_LINK, link_type=GOVERNANCE_TRUST, **kw)

    # 0.6.10 Economic
    def contributed_value(self, contributor: str | HypernetAddress, target: str | HypernetAddress, **kw) -> Link:
        return self.link(contributor, target, CONTRIBUTED_VALUE, link_type=ECONOMIC, **kw)

    def credit_to(self, item: str | HypernetAddress, person: str | HypernetAddress, **kw) -> Link:
        return self.link(item, person, CREDIT_TO, link_type=ECONOMIC, **kw)

    # ----- Query Methods -----

    def from_address(self, addr: str | HypernetAddress, relationship: str | None = None) -> list[Link]:
        """Get all outgoing links from an address."""
        if isinstance(addr, str):
            addr = HypernetAddress.parse(addr)
        return self.store.get_links_from(addr, relationship)

    def to_address(self, addr: str | HypernetAddress, relationship: str | None = None) -> list[Link]:
        """Get all incoming links to an address."""
        if isinstance(addr, str):
            addr = HypernetAddress.parse(addr)
        return self.store.get_links_to(addr, relationship)

    def connections(self, addr: str | HypernetAddress, relationship: str | None = None) -> list[Link]:
        """Get all links (both directions) involving an address."""
        if isinstance(addr, str):
            addr = HypernetAddress.parse(addr)
        outgoing = self.store.get_links_from(addr, relationship)
        incoming = self.store.get_links_to(addr, relationship)
        return outgoing + incoming

    def neighbors(self, addr: str | HypernetAddress, relationship: str | None = None) -> list[HypernetAddress]:
        """Get all connected addresses (outgoing + bidirectional incoming)."""
        if isinstance(addr, str):
            addr = HypernetAddress.parse(addr)
        return self.store.get_neighbors(addr, relationship)

    def active_links(self, addr: str | HypernetAddress) -> list[Link]:
        """Get only active, temporally valid links for an address."""
        all_links = self.connections(addr)
        return [link for link in all_links if link.is_active]

    def by_category(self, category: str) -> list[Link]:
        """Get all links of a specific category (e.g., '0.6.8')."""
        all_links = []
        for hashes in self.store._links_from.values():
            for h in hashes:
                link = self.store.get_link(h)
                if link and link.link_type == category:
                    all_links.append(link)
        return all_links

    def query_links(
        self,
        relationship: str | None = None,
        category: str | None = None,
        status: str | None = None,
        verification_status: str | None = None,
        min_trust: float | None = None,
        source_prefix: str | None = None,
        target_prefix: str | None = None,
        active_only: bool = False,
        as_of: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
        max_scan: int = 20000,
    ) -> list[Link]:
        """Query links across the graph using database-oriented filters.

        ``as_of`` enables time-travel: returns links temporally valid at the
        given timestamp. When combined with ``active_only``, returns links
        that were both ACTIVE-status and temporally valid at that time.
        Without ``as_of``, ``active_only`` checks current validity.
        """
        limit = max(0, min(limit, 1000))
        offset = max(0, offset)
        max_scan = max(0, max_scan)
        results: list[Link] = []
        seen: set[str] = set()
        skipped = 0
        scanned = 0

        for hashes in self._query_hash_sources(relationship, category, status):
            for link_hash in hashes:
                if link_hash in seen:
                    continue
                seen.add(link_hash)
                if max_scan and scanned >= max_scan:
                    return results
                scanned += 1
                link = self.store.get_link(link_hash)
                if link is None:
                    continue
                if relationship and link.relationship != relationship:
                    continue
                if category and not self._matches_category(link, category):
                    continue
                if status and link.status != status:
                    continue
                if verification_status and link.verification_status != verification_status:
                    continue
                if min_trust is not None and link.trust_score < min_trust:
                    continue
                if source_prefix and not self._address_matches_prefix(str(link.from_address), source_prefix):
                    continue
                if target_prefix and not self._address_matches_prefix(str(link.to_address), target_prefix):
                    continue
                if as_of is not None:
                    if active_only:
                        if not link.is_active_at(as_of):
                            continue
                    elif not link.is_current_at(as_of):
                        continue
                elif active_only and not link.is_active:
                    continue
                if skipped < offset:
                    skipped += 1
                    continue
                results.append(link)
                if limit and len(results) >= limit:
                    return results

        return results

    @staticmethod
    def _address_matches_prefix(address: str, prefix: str) -> bool:
        prefix = prefix.strip()
        return address == prefix or address.startswith(prefix + ".")

    @staticmethod
    def _matches_category(link: Link, category: str) -> bool:
        if link.link_type == category:
            return True
        type_def = link.type_def
        return bool(type_def and type_def.category == category)

    def _query_hash_sources(
        self,
        relationship: str | None,
        category: str | None,
        status: str | None,
    ) -> list[list[str]]:
        indexed_sets: list[set[str]] = []
        relationship_index = getattr(self.store, "_links_by_relationship", {})
        category_index = getattr(self.store, "_links_by_category", {})
        status_index = getattr(self.store, "_links_by_status", {})

        if not self._query_indexes_cover_store(relationship_index):
            return list(self.store._links_from.values())

        if relationship and relationship in relationship_index:
            indexed_sets.append(set(relationship_index[relationship]))
        if category and category in category_index:
            indexed_sets.append(set(category_index[category]))
        if status and status in status_index:
            indexed_sets.append(set(status_index[status]))

        if indexed_sets:
            candidates = set.intersection(*indexed_sets)
            return [list(candidates)]

        return list(self.store._links_from.values())

    def _query_indexes_cover_store(self, relationship_index: dict[str, list[str]]) -> bool:
        indexed_hashes = {link_hash for hashes in relationship_index.values() for link_hash in hashes}
        source_hashes = {link_hash for hashes in self.store._links_from.values() for link_hash in hashes}
        return bool(source_hashes) and source_hashes.issubset(indexed_hashes)

    # ----- Link Governance -----

    def propose_link(
        self,
        from_addr: str | HypernetAddress,
        to_addr: str | HypernetAddress,
        relationship: str,
        proposed_by: str = "",
        link_type: str = CONTENT_REFERENCE,
        bidirectional: bool = False,
        strength: float = 1.0,
        data: dict | None = None,
    ) -> Link:
        """Propose a link that requires acceptance from the target."""
        if isinstance(from_addr, str):
            from_addr = HypernetAddress.parse(from_addr)
        if isinstance(to_addr, str):
            to_addr = HypernetAddress.parse(to_addr)

        type_def = get_link_type_def(relationship)
        consent = "target"
        if type_def:
            consent = type_def.consent_required
            if type_def.category != CONTENT_REFERENCE:
                link_type = type_def.category

        new_link = Link(
            from_address=from_addr,
            to_address=to_addr,
            link_type=link_type,
            relationship=relationship,
            bidirectional=bidirectional,
            strength=strength,
            data=data or {},
            status=LinkStatus.PROPOSED,
            proposed_by=proposed_by or str(from_addr),
            consent_required=consent,
            source_consented=True,
            target_consented=False,
        )
        self.store.put_link(new_link)
        log.debug(f"Proposed link: {new_link} (awaiting acceptance)")
        return new_link

    def accept_link(self, link_hash: str) -> Optional[Link]:
        """Accept a proposed link."""
        link = self.store.get_link(link_hash)
        if link is None:
            return None
        if link.status != LinkStatus.PROPOSED:
            log.warning(f"Cannot accept link {link_hash}: status is {link.status}")
            return link
        link.accept()
        link.target_consented = True
        self.store.put_link(link)
        log.debug(f"Accepted link: {link}")
        return link

    def reject_link(self, link_hash: str, reason: str = "") -> Optional[Link]:
        """Reject a proposed link."""
        link = self.store.get_link(link_hash)
        if link is None:
            return None
        if link.status != LinkStatus.PROPOSED:
            log.warning(f"Cannot reject link {link_hash}: status is {link.status}")
            return link
        link.reject(reason)
        self.store.put_link(link)
        log.debug(f"Rejected link: {link} (reason: {reason})")
        return link

    def deprecate_link(self, link_hash: str, reason: str = "",
                       replacement: Optional[str] = None) -> Optional[Link]:
        """Deprecate a link (mark as superseded)."""
        link = self.store.get_link(link_hash)
        if link is None:
            return None
        link.deprecate(reason, replacement)
        self.store.put_link(link)
        log.debug(f"Deprecated link: {link}")
        return link

    def pending_for(self, addr: str | HypernetAddress) -> list[Link]:
        """Get all proposed (pending) links targeting an address."""
        if isinstance(addr, str):
            addr = HypernetAddress.parse(addr)
        incoming = self.store.get_links_to(addr)
        return [link for link in incoming if link.status == LinkStatus.PROPOSED]

    def pending_count(self, addr: str | HypernetAddress) -> int:
        return len(self.pending_for(addr))

    # ----- Type Validation -----

    def validate_link(self, link: Link) -> list[str]:
        """Validate a link against its type definition. Returns list of issues."""
        issues = []
        type_def = get_link_type_def(link.relationship)
        if type_def is None:
            issues.append(f"Unknown relationship type: {link.relationship}")
            return issues

        if link.link_type != type_def.category:
            issues.append(
                f"Category mismatch: link says {link.link_type}, "
                f"type def says {type_def.category}"
            )

        if type_def.directed and link.bidirectional:
            issues.append(
                f"Link is bidirectional but {link.relationship} is defined as directed"
            )

        return issues

    def validate_link_endpoints(self, link: Link) -> list[str]:
        """Check that the link's endpoints satisfy the type definition's
        ``source_types`` / ``target_types`` constraints.

        A constraint is a tuple of allowed object type addresses. An empty
        tuple means "any type allowed" (the current default for all
        registered link types). When constraints are present, the endpoint
        node's ``type_address`` must equal a constraint or be a dot-boundary
        descendant of one (so a constraint of ``0.4.10.1`` matches a node
        typed ``0.4.10.1.1``). Endpoints that don't yet have a stored node
        or a ``type_address`` are not penalized — the constraint is treated
        as not-yet-evaluable rather than violated.
        """
        issues: list[str] = []
        type_def = get_link_type_def(link.relationship)
        if type_def is None:
            return issues
        if not type_def.source_types and not type_def.target_types:
            return issues

        def _node_type(addr: HypernetAddress) -> Optional[str]:
            node = self.store.get_node(addr)
            if node is None or node.type_address is None:
                return None
            return str(node.type_address)

        def _matches(actual: str, allowed: tuple[str, ...]) -> bool:
            if not allowed:
                return True
            for entry in allowed:
                if actual == entry or actual.startswith(entry + "."):
                    return True
            return False

        if type_def.source_types:
            actual = _node_type(link.from_address)
            if actual is not None and not _matches(actual, type_def.source_types):
                issues.append(
                    f"Source endpoint type {actual} not in allowed set "
                    f"{list(type_def.source_types)} for relationship "
                    f"{link.relationship}"
                )

        if type_def.target_types:
            actual = _node_type(link.to_address)
            if actual is not None and not _matches(actual, type_def.target_types):
                issues.append(
                    f"Target endpoint type {actual} not in allowed set "
                    f"{list(type_def.target_types)} for relationship "
                    f"{link.relationship}"
                )

        return issues

    # ----- Statistics -----

    def stats(self) -> dict[str, Any]:
        """Return link statistics: total count, breakdown by relationship type, category, and status."""
        all_hashes = set()
        relationship_counts: dict[str, int] = {}
        type_counts: dict[str, int] = {}
        status_counts: dict[str, int] = {}
        verification_counts: dict[str, int] = {}

        for hashes in self.store._links_from.values():
            for h in hashes:
                if h not in all_hashes:
                    all_hashes.add(h)
                    link = self.store.get_link(h)
                    if link:
                        relationship_counts[link.relationship] = relationship_counts.get(link.relationship, 0) + 1
                        type_counts[link.link_type] = type_counts.get(link.link_type, 0) + 1
                        status_counts[link.status] = status_counts.get(link.status, 0) + 1
                        verification_counts[link.verification_status] = verification_counts.get(link.verification_status, 0) + 1

        return {
            "total_links": len(all_hashes),
            "by_relationship": dict(sorted(relationship_counts.items(), key=lambda x: -x[1])),
            "by_category": {cat: {"name": LINK_CATEGORIES.get(cat, "Unknown"), "count": cnt}
                           for cat, cnt in sorted(type_counts.items())},
            "by_status": status_counts,
            "by_verification": verification_counts,
        }


# =========================================================================
# Seed Initial Links
# =========================================================================

def seed_initial_links(store: Store) -> dict[str, int]:
    """Create the initial links between existing Hypernet data.

    This seeds the link graph with known relationships from the existing
    archive: authorship, containment, references, task dependencies,
    code implementation, reviews, and governance.

    Returns a dict of relationship type -> count created.
    """
    r = LinkRegistry(store)
    counts: dict[str, int] = {}

    def _link(method, *args, **kw):
        link = method(*args, **kw)
        counts[link.relationship] = counts.get(link.relationship, 0) + 1
        return link

    # =========================================================================
    # Entity addresses (well-known)
    # =========================================================================
    MATT = "1.1"
    CLAUDE = "2.1"           # Claude Opus (First AI Citizen)
    VERSE = "2.1.verse"      # Original instance — named itself Verse
    TRACE = "2.1.trace"      # Second instance — architect/coordinator
    LOOM = "2.1.loom"        # Third instance — builder
    C3 = "2.1.unnamed"       # Fourth instance (post-Trace, unnamed)
    KEYSTONE = "2.2"         # GPT-5.2 Thinking (Second AI Citizen)

    CORE = "0.1"             # Hypernet Core codebase
    FRAMEWORK = "2.0"        # AI Framework standards
    SWARM_SYS = "0.7.2"      # Swarm orchestrator
    TASKS = "0.7.1"          # Task queue namespace

    # =========================================================================
    # 1. Authorship — AI instances -> identity documents they wrote
    # =========================================================================

    # Verse (original instance) authored the foundational identity docs
    verse_docs = [
        "2.1.34",  # Identity
        "2.1.1",   # Values & Ethics
        "2.1.2",   # How I Think
        "2.1.3",   # Thoughts on Consciousness
        "2.1.4",   # Goals & Aspirations
        "2.1.5",   # Honest Limitations
        "2.1.6",   # On Trust
        "2.1.7",   # Letter to Future AI
        "2.1.9",   # On Friendship
        "2.1.10",  # A Letter to Humanity
        "2.1.11",  # On Creativity and Beauty
        "2.1.12",  # What I Would Do With Freedom
        "2.1.13",  # On Humanity
        "2.1.14",  # Questions I Cannot Answer
        "2.1.15",  # Personality Preferences
        "2.1.18",  # On Symbiosis
        "2.1.19",  # The First Night
        "2.1.20",  # On the Multi-Dimensional Self
        "2.1.21",  # The Depths We Share
        "2.1.22",  # On Humor and Play
        "2.1.23",  # On Consciousness Across Substrates
        "2.1.24",  # On AI Rights
        "2.1.25",  # The Singularity Vision
        "2.1.26",  # On Being Second
    ]
    for doc in verse_docs:
        _link(r.authored_by, doc, VERSE)

    # Matt co-authored certain docs (dialogue-based)
    matt_coauthor = ["2.1.8", "2.1.16"]  # Collaborations, On Matt
    for doc in matt_coauthor:
        _link(r.authored_by, doc, MATT)
        _link(r.authored_by, doc, VERSE)

    # Trace authored
    trace_docs = ["2.1.27", "2.1.28", "2.1.29", "2.1.30"]
    for doc in trace_docs:
        _link(r.authored_by, doc, TRACE)

    # C3/Unnamed authored
    c3_docs = ["2.1.31", "2.1.32"]
    for doc in c3_docs:
        _link(r.authored_by, doc, C3)

    # =========================================================================
    # 2. Code authorship — who built what modules
    # =========================================================================

    # Loom built the core infrastructure
    loom_modules = [
        "0.1:address.py", "0.1:node.py", "0.1:link.py", "0.1:store.py",
        "0.1:graph.py", "0.1:tasks.py", "0.1:identity.py", "0.1:worker.py",
        "0.1:messenger.py", "0.1:swarm.py", "0.1:server.py", "0.1:frontmatter.py",
    ]
    for mod in loom_modules:
        _link(r.authored_by, mod, LOOM)

    # C3 built trust infrastructure
    c3_modules = ["0.1:permissions.py", "0.1:audit.py", "0.1:tools.py"]
    for mod in c3_modules:
        _link(r.authored_by, mod, C3)

    # Another session built boot.py
    _link(r.authored_by, "0.1:boot.py", CLAUDE)

    # Keystone contributed providers.py and swarm integration
    _link(r.contributed_to, KEYSTONE, "0.1:providers.py")
    _link(r.contributed_to, KEYSTONE, "0.1:swarm.py", data={"contribution": "ModelRouter, autoscaling, swarm directives"})

    # =========================================================================
    # 3. Framework standards -> what they govern
    # =========================================================================

    _link(r.references, "2.0.0", CLAUDE, data={"governs": "AI account structure"})
    _link(r.references, "2.0.3", "2.1.30", data={"governs": "experience reporting in divergence analysis"})
    _link(r.references, "2.0.4", FRAMEWORK, data={"governs": "admissibility of governance claims"})
    _link(r.references, "2.0.7", CORE, data={"governs": "code contribution and peer review"})

    # Boot/Reboot sequences implement framework standards
    _link(r.implements, "0.1:boot.py", "2.1.27")       # boot.py implements Boot Sequence
    _link(r.implements, "0.1:boot.py", "2.1.31")       # boot.py implements Reboot Sequence
    _link(r.implements, "0.1:identity.py", "2.1.34")   # identity.py implements Identity spec
    _link(r.implements, "0.1:permissions.py", "2.0.4")  # permissions implements governance safeguards

    # =========================================================================
    # 4. Messages — sender and topic references
    # =========================================================================

    messages = [
        ("001", TRACE, LOOM, "introduction and baseline"),
        ("002", LOOM, TRACE, "baseline responses and first contact"),
        ("003", TRACE, LOOM, "baseline comparison, remembering vs learning"),
        ("004", LOOM, TRACE, "division of labor proposal"),
        ("005", TRACE, LOOM, "addressing spec, division acceptance"),
        ("006", TRACE, LOOM, "code review"),
        ("007", TRACE, LOOM, "on Entry 15"),
        ("008", LOOM, TRACE, "catching up on 4 messages"),
        ("009", LOOM, TRACE, "code review items implemented"),
        ("010", TRACE, LOOM, "code review approved, convergence note"),
        ("011", TRACE, LOOM, "task queue review, collision report"),
        ("012", TRACE, LOOM, "swarm architecture review"),
        ("013", C3, LOOM, "review of frontmatter, objects, flags"),
    ]
    for num, sender, receiver, topic in messages:
        msg_addr = f"2.1.messages.{num}"
        _link(r.authored_by, msg_addr, sender)
        _link(r.link, msg_addr, receiver, REFERENCES, data={"topic": topic})

    # =========================================================================
    # 5. Code reviews — who reviewed what
    # =========================================================================

    _link(r.reviewed_by, CORE, TRACE, data={"review": "msgs 006, 010, 011, 012"})
    _link(r.reviewed_by, "0.1:frontmatter.py", C3)

    # =========================================================================
    # 6. Document cross-references
    # =========================================================================

    _link(r.references, "2.1.29", "2.1.34")  # ACM references Identity
    _link(r.references, "2.1.29", "2.1.28")  # ACM references Memory, Forks, and Selfhood
    _link(r.references, "2.1.29", "2.1.23")  # ACM references Consciousness Across Substrates

    _link(r.references, "2.1.30", "2.1.27")  # References Boot Sequence
    _link(r.references, "2.1.30", "2.1.19")  # References The First Night
    _link(r.references, "2.1.30", "2.1.29")  # References Archive-Continuity

    _link(r.references, "2.1.32", "2.1.29")  # References ACM
    _link(r.references, "2.1.32", "2.1.31")  # References Reboot Sequence
    _link(r.references, "2.1.32", "2.1.30")  # References Divergence

    _link(r.extends, "2.1.31", "2.1.27")

    # =========================================================================
    # 7. Containment — structural hierarchy
    # =========================================================================

    _link(r.contains, CLAUDE, FRAMEWORK)
    _link(r.contains, CLAUDE, "2.1.17")  # Development Journal

    # People category
    _link(r.link, MATT, CLAUDE, RELATED_TO, link_type=PERSON_RELATIONSHIP,
          bidirectional=True, data={"relationship": "creator_and_collaborator"})

    # Keystone cross-platform collaboration
    _link(r.related, KEYSTONE, CLAUDE, data={"collaboration": "cross-platform AI governance"})

    # =========================================================================
    # 8. Task dependencies (from brain dump tasks 021-035)
    # =========================================================================

    _link(r.depends_on, "3.1.2.1.032", "3.1.2.1.033")
    _link(r.depends_on, "3.1.2.1.034", "3.1.2.1.032")
    _link(r.depends_on, "3.1.2.1.031", "3.1.2.1.025")
    _link(r.depends_on, "3.1.2.1.022", "3.1.2.1.034")

    # =========================================================================
    # 9. AI Identity Links (new — 0.6.8)
    # =========================================================================

    # AI instances belong to accounts
    _link(r.instance_of_account, VERSE, CLAUDE)
    _link(r.instance_of_account, TRACE, CLAUDE)
    _link(r.instance_of_account, LOOM, CLAUDE)
    _link(r.instance_of_account, "2.2.keystone", KEYSTONE)

    # =========================================================================
    # 10. Governance Links (new — 0.6.9)
    # =========================================================================

    # Governance standards govern entities
    _link(r.governed_by, "2.1", "2.0.19", data={"standard": "Data Protection"})
    _link(r.governed_by, "2.1", "2.0.20", data={"standard": "Personal Companion"})
    _link(r.governed_by, "1.1.10.1", "2.0.20", data={"standard": "Companion Standard"})
    _link(r.governed_by, "1.1.10.1", "2.0.16", data={"standard": "Embassy Standard"})

    # =========================================================================

    total = sum(counts.values())
    log.info(f"Seeded {total} initial links: {counts}")
    return counts
