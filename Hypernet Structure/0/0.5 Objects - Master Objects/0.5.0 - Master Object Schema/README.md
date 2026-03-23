---
ha: "0.5.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.5.0 - Master Object Schema

The universal base schema for all Hypernet objects. See `0.5.0 Master Object Schema.md` in the parent directory for the complete specification.

## Core Sections

Every object has these sections:
1. **Identity** -- address, type, version
2. **Metadata** -- timestamps, creator, modifier
3. **Access** -- visibility, encryption, permissions
4. **Classification** -- flags from 0.8, tags, categories
5. **Links** -- connections to other objects via 0.6
6. **Content** -- type-specific payload (defined in 0.5.1-0.5.16)
