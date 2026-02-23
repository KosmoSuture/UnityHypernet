---
ha: "0.4.0.3.2"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# SocialAccount - Social Media Account/Profile

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
