---
ha: "0.4.0.8.1"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# CalendarEvent - Calendar Event/Appointment

**Type ID:** `hypernet.life.calendarevent`
**Version:** 1.0
**Category:** 0.0.8 - Life Types
**Parent:** BaseObject
**Status:** Active
**Created:** 2026-02-04

---

## Purpose

Calendar events from Google Calendar, Outlook, Apple Calendar, etc.

---

## Required Fields

```yaml
title: String(500)

starts_at: DateTime

event_type: Enum
  - "event", "reminder", "task", "birthday"
```

---

## Optional Fields

```yaml
ends_at: DateTime

location: String(500)
  - Physical or virtual location

description: Text

# Recurrence
is_recurring: Boolean
recurrence_rule: String(255)
  - iCal RRULE format

# Participants
organizer_email: String(255)
attendees: Text[]

# Virtual
meeting_url: String(500)
  - Zoom, Teams link

# Status
status: Enum
  - "confirmed", "tentative", "cancelled"

reminder_minutes: Integer[]
  - [15, 60] (15 min and 1 hour before)
```

---

## Metadata Schema

```json
{
  "google_calendar": {
    "event_id": "abc123",
    "calendar_name": "Work",
    "color": "#ff0000"
  },
  "zoom": {
    "meeting_id": "123-456-789",
    "password": "..."
  },
  "rsvp": {
    "response": "accepted",
    "responded_at": "2024-01-10T12:00:00Z"
  }
}
```

---

## Relationships

```yaml
Outgoing:
  - source: Integration (Google Calendar)
  - at_location: Location
  - related_to: Photo, Video, Email

Incoming:
  - invited_to: User, Contact
```

---

**Status:** Active - Phase 1 Priority
**Version:** 1.0
