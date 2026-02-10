# 0.6 - Link Definitions

**Version:** 1.0
**Last Updated:** February 9, 2026
**Purpose:** Relationship types and patterns connecting objects
**Status:** Active - Knowledge Graph Foundation

---

## Overview

Section 0.6 defines the **links that connect objects** in Hypernet. While Section 0.5 defines what objects are, this section defines how they relate to each other. Links are the third pillar of Hypernet's architecture, transforming isolated objects into an interconnected knowledge graph.

If objects are the nodes and addresses are the coordinates, links are the edges that create meaning, context, and knowledge. A photo becomes more valuable when linked to its photographer, location, and related events. A person becomes part of a network through links to colleagues, organizations, and contributions.

## Purpose and Importance

### Why Links Matter

**Without Links:**
- Objects are isolated data points
- No context or relationships
- Manual searching for connections
- Difficult to discover related information
- Data remains information, not knowledge

**With Links:**
- Objects gain meaning through context
- Relationships are explicit and traversable
- Graph queries discover connections
- Related information surfaces automatically
- Information becomes knowledge

### The Power of the Knowledge Graph

Links enable **emergent intelligence**:
- **Discover patterns**: See relationships you didn't know existed
- **Navigate knowledge**: Follow connections to explore ideas
- **Build understanding**: Context transforms data into wisdom
- **Enable inference**: Derive new knowledge from existing relationships
- **Power AI**: Structured relationships enable machine reasoning

### Three Pillars of Hypernet

```
┌─────────────────────────────────────────────────┐
│  1. THE LIBRARY (0.0 Addressing)                │
│     Addresses and organizes information         │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  2. OBJECTS (0.5 Master Objects)                │
│     Stores information in standard format       │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  3. LINKS (0.6 Link Definitions)                │
│     Creates meaning through relationships       │
└─────────────────────────────────────────────────┘
```

Together: **A comprehensive, navigable knowledge graph of human information**

## Link Architecture

### Link Object Structure

```yaml
link:
  # ═══════════════════════════════════════════════════════
  # LINK IDENTITY
  # ═══════════════════════════════════════════════════════
  identity:
    link_id: "[UUID]"
    link_type: "[Type from 0.6.x]"  # e.g., "created_by"

  # ═══════════════════════════════════════════════════════
  # ENDPOINTS
  # ═══════════════════════════════════════════════════════
  endpoints:
    source:
      address: "[Source Object address]"
      object_type: "photo"

    target:
      address: "[Target Object address]"
      object_type: "person"

  # ═══════════════════════════════════════════════════════
  # LINK PROPERTIES
  # ═══════════════════════════════════════════════════════
  properties:
    directed: true              # true = one-way, false = bidirectional
    weight: 0.8                 # 0.0 to 1.0 (for weighted graphs)
    temporal:
      valid_from: "2025-01-01T00:00:00Z"
      valid_until: null         # null = indefinite
      is_current: true

  # ═══════════════════════════════════════════════════════
  # METADATA
  # ═══════════════════════════════════════════════════════
  metadata:
    created:
      timestamp: "2025-01-30T12:00:00Z"
      by: "[Creator Mandala]"

    context: "Photo taken during Hypernet development sprint"

    evidence:
      - type: "document"
        reference: "[Document Object that evidences this link]"
      - type: "assertion"
        by: "[Person who asserted]"
        confidence: 0.9

    tags: ["work", "photography", "verified"]

  # ═══════════════════════════════════════════════════════
  # VERIFICATION
  # ═══════════════════════════════════════════════════════
  verification:
    status: "peer_verified"
    verifiers:
      - mandala: "[Verifier Mandala]"
        timestamp: "2025-01-30T14:00:00Z"
        method: "exif_data_review"

    trust_score: 0.85
```

### Why This Structure?

- **Identity**: Every link is a first-class object with unique ID
- **Endpoints**: Explicit source and target addresses
- **Properties**: Directionality, weight, temporal validity
- **Metadata**: Context and evidence for the relationship
- **Verification**: Trust and confidence in the link

## Link Type Categories

### Overview of Categories

Section 0.6 defines nine categories of link types:

| Category | Focus | Examples |
|----------|-------|----------|
| 0.6.1 | Person Relationships | knows, works_with, mentors |
| 0.6.2 | Organizational | member_of, employed_by, founded |
| 0.6.3 | Authorship & Creation | created_by, authored, contributed_to |
| 0.6.4 | Reference & Citation | cites, references, quotes |
| 0.6.5 | Hierarchical | part_of, contains, parent_of |
| 0.6.6 | Spatial | located_at, near, within |
| 0.6.7 | Temporal | preceded_by, during, caused |
| 0.6.8 | Semantic | similar_to, opposite_of, instance_of |
| 0.6.9 | Task & Dependency | assigned_to, depends_on, blocks |

## What Should Be Stored Here

### Link Type Definitions

**For each link type:**
- Semantic meaning
- Valid source and target object types
- Directionality (one-way or bidirectional)
- Symmetry properties
- Transitivity properties
- Cardinality constraints
- Use cases and examples

### Link Patterns

**Common relationship patterns:**
- One-to-one relationships
- One-to-many relationships
- Many-to-many relationships
- Hierarchical relationships
- Network relationships
- Temporal relationships

### Link Metadata

**What can be attached to links:**
- Context and description
- Time ranges (when relationship was valid)
- Strength/weight (how strong the relationship is)
- Evidence (what proves this relationship)
- Confidence scores
- Verification status

## Current Contents

### Existing Documents

**0.6.0 Link Definitions Overview**
- Link architecture explained
- Nine link categories
- Link schema specification
- Link properties (directionality, symmetry, transitivity)
- Verification levels
- Graph operations enabled by links

**0.6.1 Person Relationship Links**
- Links between people
- Professional relationships (works_with, reports_to)
- Personal relationships (knows, related_to)
- Mentorship (mentors, mentored_by)
- Family relationships

**0.6.2 Organizational Links**
- Person-to-organization links
- Organization-to-organization links
- Membership and employment
- Founding and ownership
- Partnerships and subsidiaries

**0.6.3 Content and Reference Links**
- Creation and authorship
- Contribution tracking
- Citation and reference
- Derivation and versioning
- Rights and licensing

**0.6.4 Spatial and Temporal Links**
- Location-based relationships
- Proximity and containment
- Time-based relationships
- Causation and sequence
- Event participation

### Planned Additions

- **0.6.5**: Hierarchical Links (detailed)
- **0.6.6**: Spatial Links (expanded)
- **0.6.7**: Temporal Links (expanded)
- **0.6.8**: Semantic Links
- **0.6.9**: Task and Dependency Links

## How Objects Relate to Each Other

### Person-to-Person Relationships

```
Matt Schaeffer (1.0.1)
├─► knows → Hillsong (1.0.2)
├─► works_with → Valeria Campeche (1.0.3)
├─► works_with → Jonathan Garibay (1.0.4)
├─► mentors → Mike Wood (1.0.5)
└─► founded → Hypernet (3.1)
```

**Link properties:**
- `knows`: Bidirectional, no time limit
- `works_with`: Bidirectional, since 2025-12-01
- `mentors`: Directed (mentor → mentee), ongoing
- `founded`: Directed, permanent historical fact

### Document-to-Person Relationships

```
"Funding Strategy 2026" (4.1.2.3.005)
├─► authored_by → Matt Schaeffer (1.0.1)
├─► reviewed_by → Financial Committee (2.5.3)
├─► approved_by → Steering Council (2.5.1)
└─► supersedes → "Funding Strategy 2025" (4.1.2.3.002)
```

**Link properties:**
- `authored_by`: Permanent attribution
- `reviewed_by`: Timestamped, multiple reviewers
- `approved_by`: Official governance action
- `supersedes`: Version relationship

### Task-to-Resource Relationships

```
"Build Unity Website" (3.1.2.1.004)
├─► assigned_to → Mike Wood (1.0.5)
├─► created_by → Matt Schaeffer (1.0.1)
├─► depends_on → "VR Headset Acquisition" (3.1.2.2.2)
├─► part_of → "Hypernet Launch" (7.1.3.2.001)
└─► delivered → Website URL (5.2.3.1.012)
```

**Link properties:**
- `assigned_to`: Current assignee (can change)
- `created_by`: Permanent creator attribution
- `depends_on`: Blocking dependency
- `part_of`: Hierarchical relationship to project
- `delivered`: Output relationship

### Photo-to-Context Relationships

```
Photo "Team Meeting Jan 2026" (6.1.2.1.147)
├─► taken_by → Matt Schaeffer (1.0.1)
├─► taken_at → San Francisco (8.1.5.2.001)
├─► during → "Planning Session" (7.2.1.3.022)
├─► depicts → Hillsong (1.0.2)
├─► depicts → Valeria Campeche (1.0.3)
└─► part_of → "Development Photos" Album (6.1.2.5.003)
```

**Link properties:**
- `taken_by`: Attribution
- `taken_at`: Spatial context
- `during`: Temporal context
- `depicts`: Content (who/what is in the photo)
- `part_of`: Organizational grouping

## Link Properties Explained

### Directionality

**Directed Links (one-way):**
- `created_by`: Document → Person (not Person → Document)
- `reports_to`: Employee → Manager
- `parent_of`: Parent → Child

**Undirected Links (bidirectional):**
- `knows`: Person ↔ Person
- `married_to`: Person ↔ Person
- `similar_to`: Concept ↔ Concept

### Symmetry

**Symmetric:** If A→B exists, then B→A must also exist
- `knows`: If Alice knows Bob, Bob knows Alice
- `married_to`: If A married to B, B married to A
- `colleague_of`: If A colleague of B, B colleague of A

**Asymmetric:** A→B does not imply B→A
- `parent_of`: If A parent of B, B is NOT parent of A
- `created_by`: If Doc created by Person, Person did NOT create Doc
- `reports_to`: If A reports to B, B does NOT report to A

### Transitivity

**Transitive:** If A→B and B→C, then A→C
- `ancestor_of`: If A ancestor of B, B ancestor of C, then A ancestor of C
- `part_of`: If Component part of Module, Module part of System, then Component part of System

**Non-transitive:** A→B and B→C does not imply A→C
- `knows`: If Alice knows Bob, Bob knows Carol, Alice may not know Carol
- `neighbor_of`: If House A neighbor of B, B neighbor of C, A may not neighbor C

### Cardinality

**One-to-One:**
- `married_to`: Person can have at most one spouse (in most jurisdictions)
- `primary_email`: Person has exactly one primary email

**One-to-Many:**
- `parent_of`: Person can have many children
- `manages`: Manager can manage many employees

**Many-to-Many:**
- `knows`: Person can know many people, be known by many
- `member_of`: Person can be member of many organizations

## Link Metadata Deep Dive

### Context

Provides human-readable explanation:
```yaml
context: "Collaborated on Hypernet funding strategy during Q4 2025"
```

**Use:** Helps humans understand WHY the relationship exists

### Evidence

Supports the link with proof:
```yaml
evidence:
  - type: "document"
    reference: "4.1.2.3.005"  # Funding strategy document
    confidence: 1.0

  - type: "assertion"
    by: "1.0.1"  # Matt Schaeffer
    confidence: 0.9
```

**Use:** Enables trust and verification

### Temporal Validity

Specifies when relationship is/was valid:
```yaml
temporal:
  valid_from: "2025-12-01T00:00:00Z"
  valid_until: "2026-06-30T23:59:59Z"
  is_current: true
```

**Use:** Track changes over time (employment, residence, etc.)

### Weight/Strength

Quantifies relationship strength:
```yaml
weight: 0.85  # Strong relationship
```

**Use:** Weighted graph algorithms, prioritization, recommendations

### Verification

Tracks trust in the relationship:
```yaml
verification:
  status: "peer_verified"
  verifiers:
    - mandala: "1.0.2"  # Hillsong verified this relationship
      timestamp: "2026-01-15T10:30:00Z"
      method: "personal_attestation"
  trust_score: 0.9
```

**Use:** Filter by trust level, prioritize verified links

## Common Use Cases

### For Developers

**Task:** Implementing graph queries and traversal
**Read:**
1. 0.6.0 Link Definitions Overview
2. Specific link categories (0.6.1-0.6.4) you'll work with
3. Related: 0.5 Objects (understand object structure)

**Implement:** Graph database queries, link creation APIs, traversal algorithms

### For Data Architects

**Task:** Designing new relationship types
**Read:**
1. 0.6.0 Link Definitions Overview (understand patterns)
2. Similar existing link types for templates
3. Related: Graph theory principles

**Create:** New link type definitions following established patterns

### For Knowledge Modelers

**Task:** Mapping domain knowledge to links
**Read:**
1. All link categories (0.6.1-0.6.9)
2. Related: 0.5 Objects (what can be linked)
3. Domain-specific relationships to model

**Model:** Relationship graphs for specific domains (healthcare, finance, etc.)

### For AI Researchers

**Task:** Training models on knowledge graph
**Read:**
1. 0.6.0 Link Definitions Overview
2. All link types (semantics and properties)
3. Related: Graph embedding techniques

**Use:** Link semantics for relationship understanding, inference, reasoning

## Relationship to Other Sections

### Links Objects from 0.5

Links connect objects:
- Source and target must be valid objects (per 0.5)
- Link types constrained by object types
- Links stored as objects themselves

### Uses Addressing from 0.0

Links reference addresses:
- Source address from 0.0
- Target address from 0.0
- Link itself has an address

### Enables Workflows in 0.7

Links support process execution:
- Task dependencies via links
- Approval chains via links
- Provenance tracking via links

### Visualized in VR

Links create spatial relationships:
- Objects positioned based on links
- Link types determine visualization
- Navigation follows links

## Best Practices

### For Link Creation

**DO:**
- Choose the most specific link type available
- Add context to explain the relationship
- Include evidence when available
- Set temporal validity if relationship is time-bound
- Verify relationships when possible

**DON'T:**
- Use generic links when specific ones exist
- Create links without context
- Skip temporal information for temporary relationships
- Leave verification status unknown
- Create circular dependencies unintentionally

### For Link Type Design

**DO:**
- Define clear semantics
- Specify valid source/target types
- Document directionality and symmetry
- Provide examples
- Consider cardinality constraints

**DON'T:**
- Create ambiguous link types
- Allow any object type to link to any other
- Ignore mathematical properties
- Skip documentation
- Duplicate existing link types

### For Graph Queries

**DO:**
- Use link types to filter traversal
- Respect directionality in queries
- Consider temporal validity
- Weight by trust scores when needed
- Limit traversal depth to prevent infinite loops

**DON'T:**
- Ignore link properties
- Traverse without depth limits
- Treat all links equally regardless of weight
- Skip verification checks
- Assume all links are current

## Future Enhancements

**Planned additions:**

- **Link inference**: Automatically derive new links from patterns
- **Link quality scoring**: Rank links by reliability and usefulness
- **Link evolution tracking**: Track how relationships change over time
- **Link templates**: Pre-defined patterns for common scenarios
- **Link visualization**: Graph visualization tools for link networks
- **Link analytics**: Centrality, clustering, community detection

## Summary

Section 0.6 defines the **relationship layer** that transforms Hypernet from a collection of objects into a knowledge graph. It provides:

1. **Link schema**: Universal structure for all relationships
2. **Nine link categories**: Person, organizational, authorship, reference, hierarchical, spatial, temporal, semantic, task
3. **30+ link types**: Specific relationship types with clear semantics
4. **Link properties**: Directionality, symmetry, transitivity, cardinality
5. **Link metadata**: Context, evidence, temporal validity, verification

This link layer enables:
- **Knowledge graph construction**: Connected web of information
- **Graph traversal**: Navigate from any object to related objects
- **Pattern discovery**: Find non-obvious connections
- **Inference**: Derive new knowledge from existing relationships
- **Context**: Understand objects through their relationships
- **AI reasoning**: Machine understanding of semantic relationships

Without links, Hypernet would be a file storage system. With links, it becomes a knowledge graph—a comprehensive, navigable representation of human knowledge where every piece of information gains meaning through its connections.

This is how we transform information into wisdom.

---

## Related Sections

- **Parent:** Section 0 (System Metadata)
- **Uses:** 0.0 Addressing (for link endpoints)
- **Connects:** 0.5 Objects (link sources and targets)
- **Enables:** 0.7 Workflows (process execution)
- **Implemented in:** 0.1 - Hypernet Core
- **Queried by:** 0.2 Processing Nodes

---

**Document:** README.md
**Location:** C:\Hypernet\Hypernet Structure\0\0.6 Link Definitions\
**Version:** 1.0
**Maintainer:** Hypernet Knowledge Graph Committee
**Next Review:** Quarterly
