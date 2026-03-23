---
ha: "0.6.3.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.6.3.0 - About Content and Reference Links

Content links track authorship, citation, derivation, and intellectual provenance. They answer: who created this, what was it based on, and what does it support or contradict?

## Link Types

| Address | Link Type | Directed | Inverse |
|---------|-----------|----------|---------|
| 0.6.3.1 | authored_by | Yes | authored |
| 0.6.3.2 | created_by | Yes | created |
| 0.6.3.3 | contributed_to | Yes | has_contributor |
| 0.6.3.4 | cites | Yes | cited_by |
| 0.6.3.5 | references | Yes | referenced_by |
| 0.6.3.6 | derived_from | Yes | source_of |
| 0.6.3.7 | supersedes | Yes | superseded_by |
| 0.6.3.8 | supports | Yes | supported_by |
| 0.6.3.9 | contradicts | Yes | (symmetric) |
