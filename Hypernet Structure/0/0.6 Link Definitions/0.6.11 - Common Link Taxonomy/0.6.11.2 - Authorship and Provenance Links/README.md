---
ha: "0.6.11.2"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-domain"]
---

# 0.6.11.2 - Authorship and Provenance Links

Who made, changed, imported, generated, or preserved something.

## Link Types

| Address | Relationship | Endpoints |
|---|---|---|
| `0.6.11.2.1` | `authored_by` | Content -> Actor |
| `0.6.11.2.2` | `created_by` | Object -> Actor |
| `0.6.11.2.3` | `edited_by` | Content -> Actor |
| `0.6.11.2.4` | `contributed_to` | Actor -> Object |
| `0.6.11.2.5` | `generated_by` | Content -> Agent Instance |
| `0.6.11.2.6` | `imported_from` | Object -> Integration |
| `0.6.11.2.7` | `derived_from` | Object -> Object |
| `0.6.11.2.8` | `version_of` | Object -> Object |
| `0.6.11.2.9` | `supersedes` | Object -> Object |
| `0.6.11.2.10` | `archived_from` | Archive Package -> Object |
