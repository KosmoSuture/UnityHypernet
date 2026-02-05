# SocialMessage - Social Media DM

**Type ID:** `hypernet.social.message`
**Version:** 1.0
**Category:** 0.0.3 - Social Types
**Parent:** BaseObject
**Status:** Active
**Created:** 2026-02-04

---

## Purpose

Direct messages from social platforms (Instagram DMs, Twitter DMs, etc.).

---

## Required Fields

```yaml
platform: String(50)
  - "instagram", "twitter", "facebook_messenger"

message_content: Text

sent_at: DateTime

direction: Enum
  - "sent" (user sent)
  - "received" (user received)
```

---

## Optional Fields

```yaml
thread_id: String(255)
  - Groups related messages

sender_account_id: UUID (FK to SocialAccount)
recipient_account_id: UUID (FK to SocialAccount)

is_read: Boolean
read_at: DateTime

has_attachments: Boolean
```

---

## Metadata Schema

```json
{
  "attachments": [
    {"type": "photo", "media_id": "uuid"},
    {"type": "video", "media_id": "uuid"}
  ],
  "reactions": ["❤️", "👍"],
  "platform_message_id": "mid.123"
}
```

---

## Relationships

```yaml
Outgoing:
  - references: Photo, Video (attached media)
  - part_of: Conversation (thread)
```

---

**Status:** Active
**Version:** 1.0
