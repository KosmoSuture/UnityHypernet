# SocialConnection - Social Relationship

**Type ID:** `hypernet.social.connection`
**Version:** 1.0
**Category:** 0.0.3 - Social Types
**Parent:** Link (specialized link type)
**Status:** Active
**Created:** 2026-02-04

---

## Purpose

Relationships between social accounts (follows, friends, connections).

---

## Required Fields

```yaml
from_account_id: UUID (FK to SocialAccount)
to_account_id: UUID (FK to SocialAccount)

connection_type: Enum
  - "follows" (one-way: Twitter, Instagram)
  - "friends" (two-way: Facebook)
  - "connection" (LinkedIn)
  - "blocks"

platform: String(50)
```

---

## Optional Fields

```yaml
established_at: DateTime
is_mutual: Boolean (for follows)
interaction_count: Integer
```

---

**Status:** Active
**Version:** 1.0
