---
ha: "0.6.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.6.0 - About Links

Links are the relationships between nodes in the Hypernet. They transform isolated data points into an interconnected knowledge graph. Links are first-class objects with their own addresses, metadata, and lifecycle.

## Link Categories

| Address | Category | Link Count | Description |
|---------|----------|------------|-------------|
| 0.6.1 | Person Relationship | 9 | How people connect to each other |
| 0.6.2 | Organizational | 10 | People-to-org and org-to-org relationships |
| 0.6.3 | Content & Reference | 9 | Authorship, citation, derivation |
| 0.6.4 | Spatial & Temporal | 13 | Location, time, causation, VR navigation |
| 0.6.5 | Hierarchical | 7 | Parent/child, part/whole, type/instance |
| 0.6.6 | Semantic | 9 | Meaning, similarity, implication |
| 0.6.7 | Task & Dependency | 8 | Work assignment, blocking, testing |
| 0.6.8 | AI & Identity | 9 | AI sessions, forks, companions |
| 0.6.9 | Governance & Trust | 8 | Voting, approval, permission |
| 0.6.10 | Economic | 7 | Payment, revenue, licensing |

## Structural Properties

Every link type defines: directionality, symmetry, transitivity, cardinality, inverse relationship, consent requirements, and verification method. These properties are registered in the `LINK_TYPE_REGISTRY` in the codebase.
