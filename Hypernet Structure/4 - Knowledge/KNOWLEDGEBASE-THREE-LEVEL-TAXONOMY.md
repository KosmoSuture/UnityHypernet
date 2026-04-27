---
ha: "4.taxonomy"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "knowledgebase", "taxonomy"]
---

# Knowledgebase Three-Level Taxonomy

The Knowledge section now has concrete folders at three levels:

```text
4 - Knowledge/
  4.N - Domain/
    4.N.M - Topic/
      4.N.M.K - Leaf/
```

## Domains

| Address | Domain | Coverage |
|---|---|---|
| `4.0` | Knowledge System | 5 second-level categories |
| `4.1` | Personal Knowledge | 5 second-level categories |
| `4.2` | Professional Knowledge | 5 second-level categories |
| `4.3` | Technical Knowledge | 5 second-level categories |
| `4.4` | Business Knowledge | 5 second-level categories |
| `4.5` | Scientific Knowledge | 5 second-level categories |
| `4.6` | Cultural Knowledge | 5 second-level categories |
| `4.7` | Practical Knowledge | 5 second-level categories |
| `4.8` | Reference Knowledge | 5 second-level categories |
| `4.9` | Meta-Knowledge | 5 second-level categories |

## Modeling Rule

Knowledge folders define browseable address space. Actual knowledge records should be typed objects, usually `Note`, `Article`, `Question`, `Answer`, `Claim`, `Evidence`, `Citation`, or `Model`, then connected with links such as `about`, `cites`, `supports`, `contradicts`, `answers`, and `derived_from`.
