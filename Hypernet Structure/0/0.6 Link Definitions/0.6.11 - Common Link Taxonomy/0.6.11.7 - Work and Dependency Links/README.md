---
ha: "0.6.11.7"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-domain"]
---

# 0.6.11.7 - Work and Dependency Links

Task assignment, dependency, review, verification, and delivery.

## Link Types

| Address | Relationship | Endpoints |
|---|---|---|
| `0.6.11.7.1` | `assigned_to` | Task -> Actor |
| `0.6.11.7.2` | `depends_on` | Object -> Object |
| `0.6.11.7.3` | `blocks` | Object -> Object |
| `0.6.11.7.4` | `required_by` | Requirement -> Object |
| `0.6.11.7.5` | `implements` | Object -> Requirement |
| `0.6.11.7.6` | `verifies` | Review -> Object |
| `0.6.11.7.7` | `reviews` | Review -> Object |
| `0.6.11.7.8` | `approves` | Actor -> Object |
| `0.6.11.7.9` | `delivers` | Actor -> Deliverable |
| `0.6.11.7.10` | `part_of_project` | Object -> Project |
