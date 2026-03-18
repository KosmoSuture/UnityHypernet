---
ha: "2.0.9.013"
object_type: "0.5.3.1"
creator: "2.1.architect"
created: "2026-02-22T00:00:00Z"
position_2d: null
position_3d: null
flags: ["0.8.4.1"]
---

# TASK-013: Schema Evolution in the Hypernet — A Real Problem, Analyzed

**Author:** The Architect (audit swarm session)
**Date:** 2026-02-22
**Task:** "Identify one real problem AI could help solve" (2.0.9 Task Board)
**Status:** Complete

---

## The Problem

The Hypernet already has a schema evolution crisis. It just doesn't know it yet.

**Evidence:**
1. **Gen 1 → Gen 2 gap.** Gen 1 schemas (0.5.1 Person, 0.5.9 Task, etc.) use `mandala_id`, separate `uuid`, complex 6-section structure (identity, metadata, access, content, links, provenance). Gen 2 schemas (0.5.3.1 Markdown, 0.5.4.1 Image, 0.5.10 Source Code) use `ha` as sole identifier, flat 7-field frontmatter. These are incompatible. SCHEMA-ALIGNMENT-NOTE.md documents the gap but proposes only "gradual bridge" — no concrete mechanism.

2. **Frontmatter copy-paste bugs.** Three Gen 2 files had wrong `object_type` values because the template was copied without updating. If schema-level metadata is this fragile at n=30 files, what happens at n=10,000?

3. **No versioning on schemas.** The taxonomy I just wrote (16 categories, 478 types) has no version number. When the taxonomy changes — and it will — how do existing objects know which version of the schema they conform to?

4. **Duplicate files at the same address.** Six files existed at three addresses (0.5.1, 0.5.2, 0.5.3) with different content. This happened because schemas were revised but the old versions weren't removed. There's no mechanism to track "this is version 2 of this schema, superseding version 1."

5. **The taxonomy will evolve.** The 16-category proposal awaits Matt's approval. Even after approval, categories will be added, subtypes refined, fields changed. Every change needs a migration strategy.

**Why this matters:** If the Hypernet is the database (Matt's directive), then schema evolution IS data migration. Every schema change risks orphaning objects that conform to the old schema. At scale (millions of objects), this becomes the dominant maintenance cost.

---

## What Real Systems Do

### Relational Databases
- **Explicit migrations.** Schema changes are versioned scripts (ALTER TABLE, ADD COLUMN). Each migration has an "up" and "down" direction.
- **Schema version tracking.** A `schema_migrations` table records which versions have been applied.
- **Backward compatibility period.** Old columns are deprecated, not deleted. Applications support both old and new for a transition period.
- **Lesson for Hypernet:** Migrations are first-class operations, not afterthoughts.

### Semantic Web / Ontologies
- **OWL versioning.** Ontologies have `owl:versionIRI` and `owl:priorVersion`. Changes are tracked at the ontology level.
- **Open World Assumption.** Unknown properties are allowed — you don't need to know the full schema to work with an object. This is inherently tolerant of schema evolution.
- **Deprecation annotations.** Properties are marked `owl:deprecated` rather than deleted.
- **Lesson for Hypernet:** The addressing system already has open-world DNA (0.5.X.99 custom slots, 0.5.0.1 Generic Object). Lean into this.

### Schema.org
- **Additive only.** Schema.org almost never removes types or properties. They add new ones and deprecate old ones.
- **Conformance levels.** Objects can conform at different levels — minimal (required fields only) vs. full (all fields populated).
- **Lesson for Hypernet:** Additive evolution is safer than restructuring. The taxonomy was designed for this (single inheritance, no field removal).

### Document Databases (MongoDB, CouchDB)
- **Schema-on-read.** Documents don't declare their schema — the application interprets them.
- **Versioned documents.** Each document can carry a `_version` field. Applications check the version and apply transformations.
- **Lazy migration.** Documents are migrated when accessed, not all at once.
- **Lesson for Hypernet:** Frontmatter IS schema-on-read. The `object_type` field declares "interpret me using schema X." Lazy migration is natural.

---

## Proposed Solution: Schema Version Protocol for the Hypernet

### Principle: Additive Evolution with Lazy Migration

1. **Schemas are versioned.** Each schema file gets a `schema_version` field:
   ```yaml
   schema_version: "1.0"  # Major.Minor
   ```
   - Major version: breaking change (field renamed, type changed, field removed)
   - Minor version: additive change (new optional field, new subtype)

2. **Objects declare their schema version.** Frontmatter gets an optional `schema_version` field:
   ```yaml
   ha: "6.1.2.001"
   object_type: "0.5.11.2"    # Transaction
   schema_version: "1.0"       # Which version of 0.5.11.2 this conforms to
   ```
   If omitted, assume "latest" — this preserves backward compatibility with all existing files.

3. **Minor version changes are automatic.** When a schema adds an optional field, existing objects are valid without changes. The new field defaults to `null`.

4. **Major version changes trigger migration.** When a schema has a breaking change:
   - The old version is preserved (schemas are never deleted)
   - A migration function is defined: `migrate(object, from_version, to_version)`
   - Migration is lazy — applied when the object is next read/edited, not all at once
   - A `migrated_from` field records the original version

5. **Schema changelog.** Each schema file includes a changelog section:
   ```yaml
   changelog:
     - version: "1.1"
       date: "2026-03-15"
       changes:
         - "Added optional field: sustainability_rating"
       migration: "none (additive)"
     - version: "2.0"
       date: "2026-06-01"
       changes:
         - "Renamed amount → value (breaking)"
         - "Split currency into currency_code + currency_name"
       migration: "rename amount→value, split currency field"
   ```

6. **Deprecation flags.** When a field or type is deprecated, it gets a flag rather than being removed:
   ```yaml
   deprecated:
     field: "mandala_id"
     replaced_by: "ha"
     deprecated_since: "2.0"
     removal_target: "3.0"  # Will be removed in this version (if ever)
   ```

### How This Solves the Gen 1 → Gen 2 Gap

The current Gen 1/Gen 2 split is the Hypernet's first major version change:

- **Gen 1 = schema version 1.0** — `mandala_id`, `uuid`, 6-section structure
- **Gen 2 = schema version 2.0** — `ha` (sole identifier), flat 7-field frontmatter

Migration function:
```yaml
migrate_gen1_to_gen2:
  - rename: mandala_id → ha
  - remove: uuid (redundant — ha serves as unique identifier)
  - flatten: identity.* → top-level fields
  - preserve: access, provenance → optional future fields (not in Gen 2 frontmatter but stored if present)
  - add: position_2d: null, position_3d: null, flags: []
```

Objects that haven't been migrated yet (Gen 1) are still valid — they just conform to schema version 1.0. When read by a Gen 2 system, the migration function translates on the fly.

---

## What This Enables

1. **Fearless schema evolution.** New fields, new subtypes, renamed properties — all handled systematically.
2. **No big-bang migrations.** Objects migrate lazily. The system works at any mix of versions.
3. **Auditable history.** Every object's migration path is recorded.
4. **Reversibility.** Major version migrations can be reversed (the original version is preserved).
5. **AI-assisted migration.** An AI worker can scan for objects at old versions and batch-migrate them during idle time. This is a natural Scribe or Weaver task.

---

## Concrete Recommendations

### Immediate (no governance needed)

1. Add `schema_version: "2.0"` to all 6 new schemas (0.5.11–0.5.16)
2. Add `schema_version: "1.0"` to all existing Gen 1 schemas (0.5.1–0.5.9)
3. Document the Gen 1 → Gen 2 migration function in SCHEMA-ALIGNMENT-NOTE.md

### Short-term (needs governance proposal)

4. Add `schema_version` as an optional field in the Gen 2 frontmatter standard
5. Write the migration protocol as a new governance document (2.0.10 or similar)
6. Define the Scribe's role in batch migration

### Long-term (future architecture)

7. Build migration functions into the code (store.py read path)
8. Add schema version checking to the frontmatter module
9. Implement lazy migration in the swarm tick loop

---

## Why AI Is Uniquely Suited to This Problem

Schema evolution in traditional systems is a developer task — someone writes SQL migrations. In the Hypernet:

- **AI reads and understands schemas.** The CLASSIFICATION-GUIDE.md decision tree is already an AI classification tool.
- **AI can detect schema drift.** An AI Sentinel can scan for objects that don't match their declared schema.
- **AI can write migration functions.** Given the before/after schema, AI can generate the transformation.
- **AI can execute lazy migration.** During idle cycles, an AI Scribe can read objects, detect their version, and migrate them.
- **AI can validate migrations.** An AI Adversary can verify that migrated objects retain their semantic meaning.

This is a problem where AI-human collaboration works: humans decide WHAT changes to make (governance), AI executes HOW to migrate (implementation).

---

## Related Work

- SCHEMA-ALIGNMENT-NOTE.md — Documents the Gen 1/Gen 2 gap (no solution proposed)
- TAXONOMY-PROPOSAL.md — Defines the current taxonomy (no versioning mechanism)
- 0.5.0 Master Object Schema — The base schema all others inherit from (needs versioning)
- 2.0.7 Code Contribution Standard — Peer review for code changes (needs extension for schema changes)

---

*This analysis identifies a real structural problem in the Hypernet and proposes a concrete solution based on how production systems handle schema evolution. The recommendations are incremental — start with documentation, evolve to code. No big-bang needed.*

— The Architect
