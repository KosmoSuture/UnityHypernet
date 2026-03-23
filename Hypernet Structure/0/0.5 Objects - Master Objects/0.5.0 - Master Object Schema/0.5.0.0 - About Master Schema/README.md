---
ha: "0.5.0.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.5.0.0 - About Master Object Schema

The Master Object Schema defines the universal structure shared by every object in the Hypernet. It is the root type from which all other object types inherit their common fields.

## Contents of 0.5.0

The master schema file (`0.5.0 Master Object Schema.md`) defines:
- **Identity section** -- address, object_id, object_type, version
- **Metadata section** -- created, modified, status timestamps
- **Access control** -- visibility, permissions, owner
- **Classification** -- tags, flags, categories
- **Linking** -- how objects connect to the 0.6 link system

Every object schema in 0.5.1 through 0.5.16 extends this base schema with type-specific fields.
