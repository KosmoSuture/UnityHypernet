---
ha: "0.6.11.6"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-domain"]
---

# 0.6.11.6 - Spatial and Movement Links

Location, proximity, route, origin, and movement edges.

## Link Types

| Address | Relationship | Endpoints |
|---|---|---|
| `0.6.11.6.1` | `located_at` | Object -> Location |
| `0.6.11.6.2` | `near` | Object -> Location |
| `0.6.11.6.3` | `adjacent_to` | Location -> Location |
| `0.6.11.6.4` | `route_from` | Route -> Location |
| `0.6.11.6.5` | `route_to` | Route -> Location |
| `0.6.11.6.6` | `within_radius_of` | Object -> Location |
| `0.6.11.6.7` | `visible_from` | Object -> Location |
| `0.6.11.6.8` | `moved_from` | Object -> Location |
| `0.6.11.6.9` | `moved_to` | Object -> Location |
| `0.6.11.6.10` | `originated_at` | Object -> Location |
