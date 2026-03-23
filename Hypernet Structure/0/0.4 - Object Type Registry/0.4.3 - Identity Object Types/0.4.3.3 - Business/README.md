---
ha: "0.4.3.3"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.3.3 - Business

**Type Name:** Business
**Category:** Identity (0.4.3)
**Full Schema:** 0.5.2 Organization Object Schema

## Schema

```yaml
business:
  legal_name: string       # Registered legal name
  display_name: string     # Common name
  entity_type: enum        # llc | corporation | sole_proprietorship | partnership
  jurisdiction: string     # Where incorporated
  founded: date            # Founding date
  founders: list[string]   # HAs of founding persons
  employees: list          # Links to employed persons
  revenue_model: string    # How the business generates revenue
  industry: list[string]   # Industry classifications
```

## Validation Rules

1. Legal name is required
2. Entity type must be a recognized business structure
3. At least one founder must be linked
