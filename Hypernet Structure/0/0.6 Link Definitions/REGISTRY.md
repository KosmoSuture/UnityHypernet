---
ha: "0.6.registry"
object_type: "registry"
creator: "2.1.index"
created: "2026-03-01"
updated: "2026-04-26"
status: "active"
visibility: "public"
flags: ["librarian", "index", "links", "database-first"]
---

# Section 0.6 Registry - Link Definitions

**Status:** Database-first link registry active
**Canonical common taxonomy:** `0.6.11 - Common Link Taxonomy`
**Common link types defined in folders:** 100
**Runtime link types exposed by API:** `/schema/link-types`
**Migration rule:** [FOLDER-FIRST-MIGRATION.md](FOLDER-FIRST-MIGRATION.md)

## Rule

Links are first-class graph objects. New link definitions should live in their own folders. Root-level files are category summaries, master schemas, or migration notes.

## Primary Taxonomy

| Address | Domain | Count |
|---|---|---:|
| `0.6.11.1` | Identity and Actor Links | 10 |
| `0.6.11.2` | Authorship and Provenance Links | 10 |
| `0.6.11.3` | Containment and Hierarchy Links | 10 |
| `0.6.11.4` | Semantic and Knowledge Links | 10 |
| `0.6.11.5` | Temporal and Causal Links | 10 |
| `0.6.11.6` | Spatial and Movement Links | 10 |
| `0.6.11.7` | Work and Dependency Links | 10 |
| `0.6.11.8` | Communication and Social Links | 10 |
| `0.6.11.9` | Governance and Trust Links | 10 |
| `0.6.11.10` | Economic and Resource Links | 10 |

## Link Record Contract

Every link should carry:

- `from_address`
- `to_address`
- `relationship`
- `link_type`
- directionality, strength, cardinality, temporal validity
- evidence and verification
- consent and access control
- provenance and lifecycle state

## Existing Category Summaries

The older `0.6.1` through `0.6.10` category files remain useful summaries and should be reconciled into folder definitions over time. The new `0.6.11` taxonomy is the broad common vocabulary for graph-database work.

## Next Work

1. Backfill runtime validation from folder definitions.
2. Migrate legacy root-level category files into index-only summaries.
3. Add query planner support for transitive, symmetric, temporal, and trust-filtered traversal.
4. Add link evidence and consent filters to the Graph API.
