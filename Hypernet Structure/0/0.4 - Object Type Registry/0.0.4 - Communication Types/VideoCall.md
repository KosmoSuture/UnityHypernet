# VideoCall - Video Call Record

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
