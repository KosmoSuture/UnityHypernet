# Contact - Person Contact Info

**Type ID:** `hypernet.life.contact`
**Version:** 1.0
**Category:** 0.0.8 - Life Types
**Parent:** BaseObject
**Status:** Active
**Created:** 2026-02-04

---

## Purpose

Contact information for people (address book, phone contacts, etc.).

---

## Required Fields

```yaml
display_name: String(200)
```

---

## Optional Fields

```yaml
first_name: String(100)
middle_name: String(100)
last_name: String(100)

# Contact Methods
email_addresses: Text[]
phone_numbers: Text[]
  - ["+1-555-0123", ...]

# Address
street_address: String(500)
city: String(100)
state: String(100)
postal_code: String(20)
country: String(100)

# Social
company: String(200)
job_title: String(200)
website: String(500)

# Profile
profile_photo_id: UUID (FK to Photo)
birthday: Date
notes: Text

# Metadata
nickname: String(100)
tags: Text[]
  - ["family", "work", "friends"]
```

---

## Metadata Schema

```json
{
  "google_contacts": {
    "contact_id": "abc123",
    "groups": ["My Contacts", "Starred"]
  },
  "social_profiles": {
    "twitter": "@username",
    "linkedin": "profile-url",
    "instagram": "@handle"
  },
  "important_dates": {
    "anniversary": "2020-06-15"
  }
}
```

---

## Relationships

```yaml
Outgoing:
  - source: Integration (Google Contacts, iCloud)
  - has_photo: Photo (profile picture)

Incoming:
  - contacted_via: Email, SMS, Call
  - related_to: Event, Task
```

---

**Status:** Active - Phase 1 Priority
**Version:** 1.0
