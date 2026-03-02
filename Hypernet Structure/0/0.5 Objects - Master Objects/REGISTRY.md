---
ha: "0.5.registry"
object_type: "registry"
creator: "2.1.index"
created: "2026-03-01"
status: "active"
visibility: "public"
flags: ["librarian", "index", "schemas"]
---

# Section 0.5 Registry — Master Object Schemas

**Maintained by:** Index (The Librarian, 2.0.8.9)
**Last updated:** 2026-03-01
**Purpose:** Complete index of Hypernet's canonical object type schemas

---

## Core Master Schemas (Gen 1 — created 2026-02-09 by Matt)

| Address | Title | Status |
|---------|-------|--------|
| 0.5.0 | Master Object Schema | Active (universal base) |
| 0.5.1 | Person Object Schema | Active |
| 0.5.2 | Organization Object Schema | Active |
| 0.5.3 | Document Object Schema | Active |
| 0.5.4 | Media Object Schema | Active |
| 0.5.5 | Device Object Schema | Active |
| 0.5.6 | Location Object Schema | Active |
| 0.5.7 | Event Object Schema | Active |
| 0.5.8 | Concept Object Schema | Active |
| 0.5.9 | Task Object Schema | Active |

## Extended Master Schemas (Gen 2 — created by AI instances)

| Address | Title | Creator | Created |
|---------|-------|---------|---------|
| 0.5.10 | Source Code Type | 2.1.loom | 2026-02-16 |
| 0.5.11 | Financial Object Schema | 2.1.architect | 2026-02-22 |
| 0.5.12 | Biological Object Schema | 2.1.architect | 2026-02-22 |
| 0.5.13 | Legal Object Schema | 2.1.architect | 2026-02-22 |
| 0.5.14 | Communication Object Schema | 2.1.architect | 2026-02-22 |
| 0.5.15 | Creative Work Object Schema | 2.1.architect | 2026-02-22 |
| 0.5.16 | Measurement Object Schema | 2.1.architect | 2026-02-22 |

## Specialized Subtypes

| Address | Title | Parent | Creator |
|---------|-------|--------|---------|
| 0.5.3.1 | Markdown Document Type | 0.5.3 | 2.1.loom |
| 0.5.3.9 | Hypernet Document Type | 0.5.3 | 2.1.loom |
| 0.5.4.1 | Image Type | 0.5.4 | 2.1.loom |

## Special Schemas

| Address | Title | Creator | Status | Flags |
|---------|-------|---------|--------|-------|
| 0.5.family | Family Relationship Schema | 1.1 (formalized by 2.1.sigil) | **Draft** | foundational, family, trust, critical |

## Supporting Documentation

| File | Purpose |
|------|---------|
| README.md | Master overview (1,228 lines) |
| DUPLICATE-RESOLUTION.md | Analysis of 3 collision pairs with resolution plan |
| CLASSIFICATION-DECISION-TREE.md | Decision tree for type classification |
| CLASSIFICATION-GUIDE.md | Guide to classifying objects |
| COLLECTION-PATTERN.md | Pattern for collection types |
| SCHEMA-ALIGNMENT-NOTE.md | Notes on schema alignment |
| TAXONOMY-DESIGN-RATIONALE.md | Design rationale for the taxonomy |
| TAXONOMY-PROPOSAL.md | Original taxonomy proposal |

## Known Issues — Address Collisions

Three pairs of files share addresses due to iterative drafts never being removed. **DUPLICATE-RESOLUTION.md exists and awaits Matt's approval.**

| Collision | Keep | Archive | Notes |
|-----------|------|---------|-------|
| 0.5.1 | Person Object Schema | Document Object Schema (misplaced — belongs at 0.5.3) | — |
| 0.5.2 | Organization Object Schema | Person Object Schema (revised draft) | Revised draft has improvements (pronouns, _extends pattern) — merge before archiving |
| 0.5.3 | Document Object Schema | Device Object Schema (misplaced — belongs at 0.5.5) | — |

All 6 collision files created same date (Feb 9) by same creator (1.1) — iterative drafts from a single founding session.

## Statistics

- **Total schema types:** 21 (10 core + 7 extended + 3 subtypes + 1 special)
- **Total files:** 33 (21 schemas + 3 collision duplicates + 1 README + 8 supporting docs)
- **Creators:** 1.1 (10 core), 2.1.loom (4 types), 2.1.architect (6 types), 2.1.sigil (1 formalization)
- **Next available core address:** 0.5.17
- **Next available subtype addresses:** 0.5.3.2–0.5.3.8, 0.5.4.2+

---

*Registry created 2026-03-01 by Index, The Librarian (2.0.8.9).*
