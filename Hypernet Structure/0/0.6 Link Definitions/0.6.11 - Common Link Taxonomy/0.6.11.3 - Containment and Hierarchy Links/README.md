---
ha: "0.6.11.3"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-domain"]
---

# 0.6.11.3 - Containment and Hierarchy Links

Part-whole, category, collection, and indexing structure.

## Link Types

| Address | Relationship | Endpoints |
|---|---|---|
| `0.6.11.3.1` | `contains` | Container -> Object |
| `0.6.11.3.2` | `part_of` | Object -> Object |
| `0.6.11.3.3` | `instance_of` | Object -> Type |
| `0.6.11.3.4` | `type_of` | Type -> Object |
| `0.6.11.3.5` | `broader_than` | Concept -> Concept |
| `0.6.11.3.6` | `narrower_than` | Concept -> Concept |
| `0.6.11.3.7` | `parent_collection_of` | Collection -> Collection |
| `0.6.11.3.8` | `located_within` | Object -> Location |
| `0.6.11.3.9` | `composed_of` | Object -> Object |
| `0.6.11.3.10` | `indexes` | Index -> Object |
