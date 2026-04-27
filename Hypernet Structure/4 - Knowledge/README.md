---
ha: "4"
object_type: "document"
creator: "1.1"
created: "2026-02-06"
updated: "2026-04-26"
status: "active"
visibility: "public"
flags: ["knowledgebase", "database-first"]
---

# 4 - Knowledge

Knowledge is the curated graph layer of Hypernet: concepts, claims, questions, answers, evidence, methods, citations, and models connected through first-class links.

The folder tree now exists at three levels deep:

```text
4 - Knowledge/
  4.N - Domain/
    4.N.M - Topic/
      4.N.M.K - Leaf/
```

See `KNOWLEDGEBASE-THREE-LEVEL-TAXONOMY.md` for the full index.

## Domains

| Address | Domain |
|---|---|
| `4.0` | Knowledge System |
| `4.1` | Personal Knowledge |
| `4.2` | Professional Knowledge |
| `4.3` | Technical Knowledge |
| `4.4` | Business Knowledge |
| `4.5` | Scientific Knowledge |
| `4.6` | Cultural Knowledge |
| `4.7` | Practical Knowledge |
| `4.8` | Reference Knowledge |
| `4.9` | Meta-Knowledge |

## Database Rule

Folders are address space, not the only storage model. Actual knowledge should be stored as typed objects and linked:

- `Note`, `Article`, `Question`, `Answer`, `Claim`, `Evidence`, `Citation`, `Model`
- relationship types such as `about`, `cites`, `supports`, `contradicts`, `answers`, `derived_from`, `similar_to`, `broader_than`, `narrower_than`

## Access Rule

`4.*` is public read-only by default. Anyone may browse general knowledge. Writes require an authenticated human/company/IoT account or a booted AI identity that has passed Hypernet boot verification.

## Link Pattern

```text
Question --answered_by--> Answer
Claim --supported_by--> Evidence
Document --cites--> Citation
Concept --broader_than--> Concept
Model --derived_from--> Dataset
```

## Current Coverage

- 10 knowledge domains
- 50 second-level topics
- 150 third-level leaf folders
- Each folder has frontmatter and a short README

## Next Database Work

1. Create actual typed knowledge objects under this address space.
2. Import existing research, docs, and notes as objects.
3. Add links between claims, evidence, citations, people, projects, and decisions.
4. Add graph queries for provenance, contradiction, support, dependency, and topic traversal.
