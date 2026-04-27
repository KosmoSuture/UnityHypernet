---
ha: "0.4.0.4.3"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# ChatMessage - Instant Message

> **Superseded by Folder-First Taxonomy (2026-04-26)**
>
> Chat / instant message object definitions now live folder-first under
> `0.4.10 - Common Object Taxonomy/0.4.10.3 - Communication and Social Objects/`.
> This document is preserved as a compatibility reference; new schema
> work should land in the folder taxonomy.
>
> **Runtime:** `GET /schema/object-types`,
> `POST /schema/object-types/validate`,
> `PUT /node/{address}?validation_mode=warn|strict|off`
>
> See `0.4 - Object Type Registry/FOLDER-FIRST-MIGRATION.md` for policy.

**Type ID:** `hypernet.communication.chat`
**Version:** 1.0
**Category:** 0.0.4 - Communication Types
**Parent:** BaseObject
**Status:** Active
**Created:** 2026-02-04

---

## Purpose

Instant messages from Slack, Discord, WhatsApp, Telegram, etc.

---

## Required Fields

```yaml
platform: String(50)
  - "slack", "discord", "whatsapp", "telegram", "signal"

message_content: Text

sent_at: DateTime

direction: Enum
  - "sent", "received"
```

---

## Optional Fields

```yaml
channel_id: String(255)
  - Channel, room, or chat ID

thread_id: String(255)
  - Message thread

sender_name: String(200)
recipient_name: String(200)

has_attachments: Boolean
is_edited: Boolean
edited_at: DateTime

# Reactions
reactions: JSONB
  - {"👍": 5, "❤️": 2}
```

---

## Metadata Schema

```json
{
  "slack": {
    "workspace": "hypernet",
    "channel": "#general",
    "message_ts": "1234567890.123456"
  },
  "discord": {
    "server": "Hypernet Community",
    "channel": "dev-chat",
    "message_id": "123456789"
  },
  "attachments": [],
  "mentions": ["@matt", "@claude"]
}
```

---

**Status:** Active
**Version:** 1.0
