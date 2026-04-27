---
ha: "0.6.folder-first-migration"
object_type: "migration_note"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-taxonomy", "migration"]
---

# Folder-First Link Type Migration

Hypernet link definitions are now folder-first.

## Canonical Source

The canonical common link taxonomy is:

```text
0.6.11 - Common Link Taxonomy/
  0.6.11.N - Domain/
    0.6.11.N.M - Relationship/
      README.md
```

Each relationship folder README is the source of truth for:

- relationship name
- source and target object classes
- direction
- symmetry and transitivity
- inverse relationship
- graph database behavior
- validation and evidence expectations

Runtime clients should discover registered links through:

- `GET /schema/link-types`
- `GET /schema/summary`

Link writes also use this registry:

- `POST /link?validation_mode=warn` returns validation without blocking
- `POST /link?validation_mode=strict` rejects unknown relationships or category mismatches
- `POST /link?validation_mode=off` skips validation for migration work

## Legacy Root-Level Files

The older root-level files such as `0.6.3 Content and Reference Links.md` now serve as compatibility summaries for their categories. They should not receive new relationship definitions.

When adding or refining a relationship:

1. Update the canonical folder in `0.6.11 - Common Link Taxonomy`.
2. Keep old category files as stable indexes or redirect notes.
3. Add runtime support in `hypernet/link.py` when clients need validation or discovery.
4. Avoid embedding relationships as free-text object fields when a typed link can represent them.

## Migration Rule

Links are database records, not loose references. A useful link definition should specify endpoints, direction, inverse behavior, evidence, trust, consent, and lifecycle expectations.
