---
ha: "0.4.3.1"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.3.1 - Person

**Type Name:** Person
**Category:** Identity (0.4.3)
**Full Schema:** 0.5.1 Person Object Schema

## Schema

```yaml
person:
  name: string           # Full legal name
  display_name: string   # Preferred display name
  date_of_birth: date    # Encrypted, access-controlled
  location: string       # Current location (HA reference)
  contact: object        # Email, phone, social -- encrypted
  family: list           # Links to related persons
  accounts: list         # External service accounts
  preferences: object    # UI, notification, privacy preferences
```

## Validation Rules

1. Name is required
2. Date of birth, contact, and financial data are always encrypted
3. A person can have exactly one primary account in category 1
4. Deletion requires human authorization -- AI cannot delete person accounts
