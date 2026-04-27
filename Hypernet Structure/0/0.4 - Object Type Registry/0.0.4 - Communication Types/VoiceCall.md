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

> **Superseded by Folder-First Taxonomy (2026-04-26)**
>
> Voice / phone-call record object definitions now live folder-first under
> `0.4.10 - Common Object Taxonomy/0.4.10.3 - Communication and Social Objects/`.
> This document is preserved as a compatibility reference; new schema
> work should land in the folder taxonomy.
>
> **Runtime:** `GET /schema/object-types`,
> `POST /schema/object-types/validate`,
> `PUT /node/{address}?validation_mode=warn|strict|off`
>
> See `0.4 - Object Type Registry/FOLDER-FIRST-MIGRATION.md` for policy.

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
