---
ha: "0.4.0.4.5"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# VideoCall - Video Call Record

> **Superseded by Folder-First Taxonomy (2026-04-26)**
>
> Video-call record object definitions now live folder-first under
> `0.4.10 - Common Object Taxonomy/0.4.10.3 - Communication and Social Objects/`.
> This document is preserved as a compatibility reference; new schema
> work should land in the folder taxonomy.
>
> **Runtime:** `GET /schema/object-types`,
> `POST /schema/object-types/validate`,
> `PUT /node/{address}?validation_mode=warn|strict|off`
>
> See `0.4 - Object Type Registry/FOLDER-FIRST-MIGRATION.md` for policy.

**Type ID:** `hypernet.communication.videocall`
**Version:** 1.0
**Category:** 0.0.4 - Communication Types
**Parent:** BaseObject
**Status:** Active
**Created:** 2026-02-04

---

## Purpose

Video call records (Zoom, Teams, FaceTime, Google Meet, etc.).

---

## Required Fields

```yaml
platform: String(50)
  - "zoom", "teams", "facetime", "google_meet", "whatsapp"

started_at: DateTime

call_type: Enum
  - "one_to_one", "group"
```

---

## Optional Fields

```yaml
duration: Integer (seconds)
ended_at: DateTime

participants: Text[]
  - List of participant names/emails

meeting_title: String(255)
meeting_url: String(500)

recording_id: UUID (FK to Video)
  - If call was recorded

transcript: Text
  - AI-generated transcript
```

---

## Metadata Schema

```json
{
  "zoom": {
    "meeting_id": "123-456-789",
    "host": "matt@hypernet.com",
    "participant_count": 5
  },
  "ai_summary": "Discussed Q1 roadmap and milestones",
  "action_items": [
    "Complete Phase 1 by Feb 15",
    "Review AI proposals"
  ]
}
```

---

**Status:** Active
**Version:** 1.0
