---
ha: "0.4.legacy.0.3.2.social-account"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# SocialAccount - Social Media Account/Profile

> **Superseded by Folder-First Taxonomy (2026-04-26)**
>
> Social media account / profile object definitions now live folder-first
> under `0.4.10 - Common Object Taxonomy/0.4.10.3 - Communication and Social Objects/`.
> This document is preserved as a compatibility reference; new schema
> work should land in the folder taxonomy.
>
> **Runtime:** `GET /schema/object-types`,
> `POST /schema/object-types/validate`,
> `PUT /node/{address}?validation_mode=warn|strict|off`
>
> See `0.4 - Object Type Registry/FOLDER-FIRST-MIGRATION.md` for policy.

**Type ID:** `hypernet.social.account`
**Version:** 1.0
**Category:** 0.0.3 - Social Types
**Parent:** BaseObject
**Status:** Active
**Created:** 2026-02-04

---

## Purpose

External social media accounts belonging to the user or others.

---

## Required Fields

```yaml
platform: String(50)
  - "instagram", "twitter", "facebook", etc.

username: String(100)
  - @username or handle

account_type: Enum
  - "own" (user's account)
  - "following" (account user follows)
  - "other" (mentioned/tagged)
```

---

## Optional Fields

```yaml
display_name: String(200)
profile_url: String(500)
profile_picture_id: UUID (FK to Photo)

# Stats
followers_count: Integer
following_count: Integer
posts_count: Integer

bio: Text
is_verified: Boolean
is_private: Boolean
```

---

## Metadata Schema

```json
{
  "instagram": {
    "user_id": "17841405793187218",
    "is_business": false,
    "category": "Personal Blog"
  },
  "sync": {
    "connected": true,
    "integration_id": "uuid"
  }
}
```

---

## Relationships

```yaml
Outgoing:
  - authored: SocialPost (posts by this account)
  - source: Integration (if own account)

Incoming:
  - follows: SocialConnection (who follows who)
```

---

**Status:** Active
**Version:** 1.0
