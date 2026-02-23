---
ha: "0.4.0.4.4"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# VoiceCall - Phone/Voice Call Record

**Type ID:** `hypernet.communication.voicecall`
**Version:** 1.0
**Category:** 0.0.4 - Communication Types
**Parent:** BaseObject
**Status:** Active
**Created:** 2026-02-04

---

## Purpose

Voice call records (phone calls, VoIP calls, etc.).

---

## Required Fields

```yaml
phone_number: String(20)

started_at: DateTime

direction: Enum
  - "outgoing", "incoming", "missed"

call_type: Enum
  - "cellular", "voip", "facetime_audio", "whatsapp"
```

---

## Optional Fields

```yaml
contact_id: UUID (FK to Contact)

duration: Integer (seconds)
  - Null for missed calls

ended_at: DateTime

recording_id: UUID (FK to Audio)
  - If call was recorded

transcript: Text
  - AI-generated transcript if available
```

---

## Metadata Schema

```json
{
  "carrier": "AT&T",
  "voicemail_left": true,
  "voicemail_id": "uuid",
  "ai_summary": "Call about project deadline",
  "quality": "good"
}
```

---

**Status:** Active
**Version:** 1.0
