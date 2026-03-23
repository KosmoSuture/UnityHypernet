---
ha: "0.4.1.2.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.1.2.0 - About Links

A Link is a typed, directional relationship between two nodes. Links are the edges of the Hypernet knowledge graph, transforming isolated data points into interconnected knowledge.

## Key Properties

- **Directionality**: Links can be directed (A -> B) or undirected (A <-> B)
- **Symmetry**: Some links are inherently symmetric (A knows B implies B knows A)
- **Transitivity**: Some links chain (A parent_of B, B parent_of C implies A ancestor of C)
- **Cardinality**: one-to-one, one-to-many, many-to-one, many-to-many

## Links Are First-Class Objects

Unlike many graph systems where edges are second-class, Hypernet links are full objects with their own addresses, metadata, lifecycle, and flags. A link can itself be linked to.

## Full Taxonomy

All link types are defined in section 0.6, organized into 10 categories (0.6.1 through 0.6.10).
