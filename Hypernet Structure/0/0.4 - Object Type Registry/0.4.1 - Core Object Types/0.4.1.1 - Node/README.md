---
ha: "0.4.1.1"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.1.1 - Node

**Type Name:** Node
**Category:** Core (0.4.1)
**Schema:** See 0.5.0 Master Object Schema

## Schema

```yaml
node:
  address: string       # Required. Dot-notation hierarchical address.
  object_type: string   # Required. Reference to type definition.
  creator: string       # Required. HA of creating entity.
  created: datetime     # Required. ISO 8601.
  modified: datetime    # Updated on any change.
  status: enum          # active | archived | deleted
  flags: list[string]   # References to 0.8.* flag addresses.
  visibility: enum      # public | private | embassy-protected | encrypted
```

## Validation Rules

1. Address must be a valid dot-notation string matching `^[0-9]+(\.[0-9]+)*$` or a named sigil
2. Object type must reference a defined type in 0.4 or 0.5
3. Creator must be a valid existing address
4. Status defaults to "active" on creation
5. A node cannot be permanently deleted by AI (soft-delete only, per 2.0.19)

## Examples

- `1.1` -- Matt Schaeffer (Person node)
- `2.1.librarian` -- The Librarian AI instance
- `0.6.5.1` -- The "parent_of" link type definition
- `3.1` -- Hypernet Inc. (Business node)
