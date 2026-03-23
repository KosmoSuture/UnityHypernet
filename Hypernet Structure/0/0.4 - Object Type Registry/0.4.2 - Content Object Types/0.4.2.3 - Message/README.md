---
ha: "0.4.2.3"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.2.3 - Message

**Type Name:** Message
**Category:** Content (0.4.2)
**Full Schema:** 0.5.14 Communication Object Schema

## Schema

```yaml
message:
  sender: string         # HA of the sending entity
  recipients: list       # HAs of recipients
  channel: enum          # email | chat | discord | sms | internal
  subject: string        # Optional subject line
  body: string           # Message content
  thread_id: string      # Conversation thread identifier
  reply_to: string       # HA of the message being replied to
  attachments: list      # HAs of attached media or documents
  sent_at: datetime      # When the message was sent
  read_by: list          # HAs of entities that have read it
```

## Validation Rules

1. Sender is required
2. At least one recipient is required
3. Body must be non-empty
4. Thread ID is auto-generated if not provided
