---
ha: "0.4.2.1"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.2.1 - Document

**Type Name:** Document
**Category:** Content (0.4.2)
**Full Schema:** 0.5.3 Document Object Schema

## Schema

```yaml
document:
  title: string          # Document title
  body: string           # Content in the document's format
  format: enum           # markdown | html | plaintext | hypernet
  word_count: integer    # Computed field
  language: string       # ISO 639-1 language code
  version: string        # Semantic version
  revision_history: list # Previous versions
  tags: list[string]     # Topic tags
```

## Validation Rules

1. Title is required
2. Body must be valid for the declared format
3. Language defaults to "en" if not specified
4. Version increments automatically on edit
