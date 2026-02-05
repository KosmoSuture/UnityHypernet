# SMS - Text Message

**Type ID:** `hypernet.communication.sms`
**Version:** 1.0
**Category:** 0.0.4 - Communication Types
**Parent:** BaseObject
**Status:** Active
**Created:** 2026-02-04

---

## Purpose

SMS/MMS text messages (iMessage, Android Messages, etc.).

---

## Required Fields

```yaml
message_content: Text

phone_number: String(20)
  - Contact's phone number

sent_at: DateTime

direction: Enum
  - "sent", "received"

message_type: Enum
  - "sms" (text only)
  - "mms" (with media)
```

---

## Optional Fields

```yaml
contact_id: UUID (FK to Contact)
thread_id: String(255)

is_read: Boolean
has_attachments: Boolean

# iMessage specific
is_imessage: Boolean
  - True if sent via iMessage, false if SMS

# Group messaging
is_group: Boolean
group_participants: Text[]
```

---

## Metadata Schema

```json
{
  "imessage": {
    "message_guid": "abc-123",
    "chat_id": "chat456"
  },
  "attachments": [
    {"type": "photo", "media_id": "uuid"}
  ],
  "reactions": {
    "user_123": "❤️"
  }
}
```

---

## Relationships

```yaml
Outgoing:
  - references: Photo, Video (MMS attachments)
  - part_of: Conversation
  - with: Contact
```

---

**Status:** Active
**Version:** 1.0
