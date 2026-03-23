---
ha: "0.4.3.4"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.3.4 - Organization

**Type Name:** Organization
**Category:** Identity (0.4.3)
**Full Schema:** 0.5.2 Organization Object Schema

## Schema

```yaml
organization:
  name: string             # Official name
  org_type: enum           # nonprofit | government | educational | community | foundation
  mission: string          # Mission statement
  founded: date            # Founding date
  jurisdiction: string     # Operating jurisdiction
  members: list[string]    # HAs of member persons or organizations
  governance: object       # How decisions are made
```

## Validation Rules

1. Name is required
2. Org type must be a recognized category
3. At least one member or founder must be linked
