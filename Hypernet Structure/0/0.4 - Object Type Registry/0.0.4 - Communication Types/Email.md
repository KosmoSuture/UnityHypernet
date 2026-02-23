---
ha: "0.4.0.4.1"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# Email - Email Message

**Type ID:** `hypernet.communication.email`
**Version:** 1.0
**Category:** 0.0.4 - Communication Types
**Parent:** BaseObject
**Status:** Active
**Created:** 2026-02-04

---

## Purpose

Email messages from Gmail, Outlook, iCloud Mail, etc.

---

## Required Fields

```yaml
subject: String(500)

from_address: String(255)
  - Sender email

to_addresses: Text[]
  - Array of recipient emails

sent_at: DateTime

direction: Enum
  - "sent", "received", "draft"
```

---

## Optional Fields

```yaml
cc_addresses: Text[]
bcc_addresses: Text[]

body_text: Text (plain text)
body_html: Text (HTML version)

thread_id: String(255)
  - Email thread/conversation ID

message_id: String(255)
  - RFC 822 Message-ID

has_attachments: Boolean
attachment_count: Integer

is_read: Boolean
is_starred: Boolean
is_important: Boolean

labels: Text[]
  - Gmail labels or folder names
```

---

## Metadata Schema

```json
{
  "headers": {
    "message-id": "<abc@mail.gmail.com>",
    "in-reply-to": "<xyz@mail.gmail.com>",
    "references": ["<...>"]
  },
  "gmail": {
    "thread_id": "thread_123",
    "labels": ["INBOX", "IMPORTANT"]
  },
  "attachments": [
    {
      "filename": "document.pdf",
      "media_id": "uuid",
      "size": 1024000
    }
  ]
}
```

---

## Relationships

```yaml
Outgoing:
  - references: Document, Photo (attachments)
  - part_of: EmailThread
  - source: Integration (Gmail, Outlook)

Incoming:
  - related_to: Task, Event (emails about tasks/events)
```

---

**Status:** Active - Phase 1 Priority
**Version:** 1.0
