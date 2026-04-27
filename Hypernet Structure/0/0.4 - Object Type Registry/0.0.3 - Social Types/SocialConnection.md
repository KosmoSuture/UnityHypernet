---
ha: "0.4.0.3.3"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# SocialConnection - Social Relationship

> **Superseded by Folder-First Taxonomy (2026-04-26)**
>
> Social connection / relationship records are first-class typed links,
> not stand-alone objects. The canonical relationship catalog now lives
> at `0.6 Link Definitions/0.6.11 - Common Link Taxonomy/` (typed link
> definitions for `friends_with`, `follows`, `member_of`, etc.). For the
> Person object that participates in connections, see
> `0.4.10 - Common Object Taxonomy/0.4.10.1 - Identity and Agent Objects/`.
> This document is preserved as a compatibility reference.
>
> **Runtime:** `GET /schema/link-types`, `GET /schema/object-types`,
> `POST /link?validation_mode=warn|strict|off`
>
> See `0.4 - Object Type Registry/FOLDER-FIRST-MIGRATION.md` and
> `0.6 Link Definitions/FOLDER-FIRST-MIGRATION.md` for policies.

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
