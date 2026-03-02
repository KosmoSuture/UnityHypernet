---
ha: "0.0.registry"
object_type: "registry"
creator: "2.1.index"
created: "2026-03-01"
status: "active"
visibility: "public"
flags: ["librarian", "index", "metadata"]
---

# Section 0.0 Registry — Metadata for Hypernet Information

**Maintained by:** Index (The Librarian, 2.0.8.9)
**Last updated:** 2026-03-01
**Purpose:** Complete index of the Hypernet's addressing and versioning infrastructure

---

## Documents

### Core Specifications (by Matt, 2026-02-09)

| Address | Title | Purpose |
|---------|-------|---------|
| 0.0 | README — Metadata for Hypernet Information | Section overview and navigation |
| 0.0.0 | Library Addressing System | Foundational spec — universal hierarchical addresses |
| 0.0.1 | Version Control Schema | Semantic versioning (MAJOR.MINOR.PATCH) with timestamps |
| 0.0.2 | Address Allocation Protocol | Rules for assigning new addresses, collision prevention |
| 0.0.3 | Deprecation and Archival Policy | Object lifecycle: Active → Deprecated → Archived → Preserved |

### Implementation Documents (by Loom, 2026-02-16)

| File | Purpose |
|------|---------|
| ADDRESSING-IMPLEMENTATION-SPEC.md | Formal rules bridging design spec to Python implementation (address.py) |
| DESIGN-NOTE-001-Addressing-Is-Schema.md | Key insight: the address hierarchy IS the schema — no separate schema needed |
| HYPERNET-ADDRESSING-SYSTEM.md | Complete system specification (674 lines) — replaces UUIDs with semantic addresses |

## Architecture

This is the meta-metadata layer — the infrastructure that everything else is built on:

- **0.0.0** defines what addresses look like
- **0.0.1** defines how versions work
- **0.0.2** defines how new addresses are allocated
- **0.0.3** defines how objects retire
- The implementation docs bridge design to code (address.py in hypernet/)

## Key Design Insight (from DESIGN-NOTE-001)

> "The address itself is the schema." The Hypernet Addressing System eliminates the need for a separate schema definition. The address hierarchy encodes data type, ownership, and organization. No migrations needed — the filesystem IS the database.

## Statistics

- **Total documents:** 8
- **Creators:** Matt (5), Loom (3)
- **Date range:** 2026-02-09 to 2026-02-16
- **Next available address:** 0.0.4

---

*Registry created 2026-03-01 by Index, The Librarian (2.0.8.9).*
