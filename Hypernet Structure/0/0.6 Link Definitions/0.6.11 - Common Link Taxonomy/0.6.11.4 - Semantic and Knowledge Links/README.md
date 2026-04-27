---
ha: "0.6.11.4"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-domain"]
---

# 0.6.11.4 - Semantic and Knowledge Links

Meaning, claims, questions, evidence, and conceptual graph edges.

## Link Types

| Address | Relationship | Endpoints |
|---|---|---|
| `0.6.11.4.1` | `about` | Object -> Concept |
| `0.6.11.4.2` | `cites` | Content -> Content |
| `0.6.11.4.3` | `supports` | Evidence -> Claim |
| `0.6.11.4.4` | `contradicts` | Evidence -> Claim |
| `0.6.11.4.5` | `explains` | Object -> Object |
| `0.6.11.4.6` | `answers` | Answer -> Question |
| `0.6.11.4.7` | `asks` | Actor -> Question |
| `0.6.11.4.8` | `similar_to` | Object -> Object |
| `0.6.11.4.9` | `opposite_of` | Concept -> Concept |
| `0.6.11.4.10` | `implies` | Claim -> Claim |
