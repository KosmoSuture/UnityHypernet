---
ha: "0.4.folder-first-migration"
object_type: "migration_note"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-taxonomy", "migration"]
---

# Folder-First Object Type Migration

Hypernet object type definitions are now folder-first.

## Canonical Source

The canonical common object taxonomy is:

```text
0.4.10 - Common Object Taxonomy/
  0.4.10.N - Domain/
    0.4.10.N.M - Object Type/
      README.md
```

Each object type folder README is the source of truth for:

- object type address
- object type name
- purpose
- required fields
- recommended graph links
- indexing expectations
- validation notes

The runtime API reads this folder taxonomy through:

- `GET /schema/object-types`
- `GET /schema/object-types/{type_address}`
- `POST /schema/object-types/validate`
- `GET /schema/summary`

Node writes also use this taxonomy:

- `PUT /node/{address}?validation_mode=warn` returns validation without blocking
- `PUT /node/{address}?validation_mode=strict` rejects missing required fields
- `PUT /node/{address}?validation_mode=off` skips validation for migration work

## Legacy Root-Level Files

Older root-level or category-level files remain in place only as compatibility documentation. They should not receive new object definitions.

When an older file overlaps a canonical object type:

1. Keep the old file stable if other documents link to it.
2. Add or preserve a note pointing to the matching `0.4.10.*` object folder.
3. Move new schema detail into the canonical folder README.
4. Do not add new root-level type files.

## Migration Rule

New objects and new schema changes must be expressed as graph database schema:

- structured object fields stay in object type folder READMEs
- cross-object references become typed links
- validation requirements are represented as required fields or link requirements
- search and traversal requirements are represented as index hints

This keeps file storage as an implementation layer while the graph database contract stays portable.
