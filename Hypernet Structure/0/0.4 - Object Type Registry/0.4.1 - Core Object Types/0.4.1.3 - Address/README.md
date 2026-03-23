---
ha: "0.4.1.3"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.1.3 - Address

**Type Name:** Address (Hypernet Address, HA)
**Category:** Core (0.4.1)

## Schema

```yaml
address:
  value: string          # The dot-notation address (e.g., "1.1.6.3")
  sigil: string          # Optional named alias (e.g., "librarian")
  parent: string         # Parent address (e.g., "1.1.6" for "1.1.6.3")
  depth: integer         # Number of segments (e.g., 4 for "1.1.6.3")
  category: integer      # Top-level category number
  assigned: datetime     # When this address was first assigned
  permanent: boolean     # Always true -- addresses never change
```

## Validation Rules

1. Must match pattern `^[0-9]+(\.[0-9a-z_]+)*$`
2. Parent address must exist before child can be created
3. No gaps allowed in numeric sequences within a parent
4. Sigils must be unique within their parent scope
5. Reserved: `.0` suffix always denotes metadata for the parent node

## Top-Level Categories

| Number | Category | Contents |
|--------|----------|----------|
| 0 | System | Definitions, infrastructure, meta |
| 1 | People | Human accounts and data |
| 2 | AI | AI accounts and data |
| 3 | Businesses | Organization accounts |
| 4+ | Knowledge | Subject-matter data (future) |
