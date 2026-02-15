# ChatMessage - Instant Message

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
