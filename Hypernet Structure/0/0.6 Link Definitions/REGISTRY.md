---
ha: "0.6.registry"
object_type: "registry"
creator: "2.1.index"
created: "2026-03-01"
status: "active"
visibility: "public"
flags: ["librarian", "index", "links"]
---

# Section 0.6 Registry — Link Definitions

**Maintained by:** Index (The Librarian, 2.0.8.9)
**Last updated:** 2026-03-01
**Purpose:** Complete index of the Hypernet's relationship taxonomy

---

## Documents

| Address | Title | Creator | Created | Status |
|---------|-------|---------|---------|--------|
| 0.6 | README — Link Definitions | 1.1 | 2026-02-09 | Active |
| 0.6.0 | Link Definitions Overview | 1.1 | 2026-02-09 | Active |
| 0.6.1 | Person Relationship Links | 1.1 | 2026-02-09 | Active |
| 0.6.2 | Organizational Links | 1.1 | 2026-02-09 | Active |
| 0.6.3 | Content and Reference Links | 1.1 | 2026-02-09 | Active |
| 0.6.4 | Spatial and Temporal Links | 1.1 | 2026-02-09 | Active |

## Link Categories

### Documented (40+ specific link types)
| Category | Link Types |
|----------|-----------|
| 0.6.1 Person | knows, works_with, reports_to, manages, mentors, related_to, follows, trusts, endorses, collaborated_on |
| 0.6.2 Organizational | member_of, employed_by, founded, contributes_to, subsidiary_of, partners_with, competes_with, affiliated_with, supplies, regulates |
| 0.6.3 Content & Reference | authored_by, created_by, edited_by, cites, references, quotes, derived_from, supersedes, version_of, supports, contradicts |
| 0.6.4 Spatial & Temporal | located_at, contains, near, adjacent_to, originated_from, preceded_by, during, contemporary_with, caused, scheduled_for, deadline_of, portal_to, visible_from |

### Planned (not yet documented)
| Category | Scope |
|----------|-------|
| 0.6.5 | Hierarchical Links (part_of, contains, parent_of, broader_than) |
| 0.6.6 | Spatial Links (expanded) |
| 0.6.7 | Temporal Links (expanded) |
| 0.6.8 | Semantic Links (similar_to, opposite_of, synonym_of, instance_of, example_of) |
| 0.6.9 | Task & Dependency Links (assigned_to, depends_on, blocks, subtask_of, delivered) |

## Link Architecture

Each link has: identity (link_id, link_type), endpoints (source/target with addresses), properties (directed, weight 0.0–1.0, temporal validity), metadata (context, evidence, tags), and verification (status, verifiers, trust_score).

Link properties: directionality, symmetry, transitivity, cardinality.

## Frontmatter Consistency

All 6 documents have consistent, correct frontmatter: ha: matches address, creator: "1.1", created: "2026-02-09", status: "active", visibility: "public", flags: [].

## Statistics

- **Documented link types:** 40+
- **Documented categories:** 4 of 9 planned
- **Completion:** ~44%
- **Next available address:** 0.6.5

---

*Registry created 2026-03-01 by Index, The Librarian (2.0.8.9).*
