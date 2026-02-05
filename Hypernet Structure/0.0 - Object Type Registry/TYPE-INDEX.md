# Hypernet Object Type Registry - Master Index

**Status:** Phase 1 Complete
**Total Types Defined:** 28
**Last Updated:** 2026-02-04

---

## Purpose

This is the master index of ALL object types defined in the Hypernet registry.

**Rule:** If it's not listed here, it doesn't exist in Hypernet yet.

---

## Core Types (0.0.1) - 4 types

Foundation types that everything else builds on.

| Type ID | Type Name | Status | Description |
|---------|-----------|--------|-------------|
| `hypernet.core.baseobject` | **BaseObject** | Active | Universal parent - all objects inherit from this |
| `hypernet.core.user` | **User** | Active | Human and AI accounts |
| `hypernet.core.link` | **Link** | Active | First-class relationships between objects |
| `hypernet.core.integration` | **Integration** | Active | External service connections (OAuth) |

---

## Media Types (0.0.2) - 5 types

Visual, audio, and document content.

| Type ID | Type Name | Status | Description |
|---------|-----------|--------|-------------|
| `hypernet.media.photo` | **Photo** | Active | Images, photographs, pictures |
| `hypernet.media.video` | **Video** | Active | Video files, recordings |
| `hypernet.media.audio` | **Audio** | Active | Music, podcasts, voice memos |
| `hypernet.media.document` | **Document** | Active | PDFs, Office docs, text files |
| `hypernet.media.screenshot` | **Screenshot** | Active | Screen captures (specialized Photo) |

---

## Social Types (0.0.3) - 4 types

Social media content and relationships.

| Type ID | Type Name | Status | Description |
|---------|-----------|--------|-------------|
| `hypernet.social.post` | **SocialPost** | Active | Social media posts |
| `hypernet.social.account` | **SocialAccount** | Active | Social media accounts/profiles |
| `hypernet.social.connection` | **SocialConnection** | Active | Social relationships (follows, friends) |
| `hypernet.social.message` | **SocialMessage** | Active | Social media DMs |

---

## Communication Types (0.0.4) - 5 types

Messages, calls, and conversations.

| Type ID | Type Name | Status | Description |
|---------|-----------|--------|-------------|
| `hypernet.communication.email` | **Email** | Active | Email messages |
| `hypernet.communication.sms` | **SMS** | Active | Text messages (SMS/MMS) |
| `hypernet.communication.chat` | **ChatMessage** | Active | Instant messages (Slack, Discord, etc.) |
| `hypernet.communication.voicecall` | **VoiceCall** | Active | Voice/phone call records |
| `hypernet.communication.videocall` | **VideoCall** | Active | Video call records (Zoom, Teams, etc.) |

---

## Web Types (0.0.7) - 3 types

Web content and bookmarks.

| Type ID | Type Name | Status | Description |
|---------|-----------|--------|-------------|
| `hypernet.web.page` | **WebPage** | Active | Saved web pages (full archives) |
| `hypernet.web.bookmark` | **Bookmark** | Active | Browser bookmarks |
| `hypernet.web.rssfeed` | **RSSFeed** | Active | RSS/Atom feed subscriptions |

---

## Life Types (0.0.8) - 4 types

Personal productivity and organization.

| Type ID | Type Name | Status | Description |
|---------|-----------|--------|-------------|
| `hypernet.life.calendarevent` | **CalendarEvent** | Active | Calendar events/appointments |
| `hypernet.life.task` | **Task** | Active | To-do items and tasks |
| `hypernet.life.note` | **Note** | Active | Personal notes |
| `hypernet.life.contact` | **Contact** | Active | Contact information (address book) |

---

## Future Types (Planned but not yet defined)

### Financial Types (0.0.5)
- Transaction
- BankAccount
- Investment
- Bill
- Receipt
- Budget

### Medical Types (0.0.6)
- MedicalRecord
- Prescription
- LabResult
- HealthMetric
- Appointment

### AI Types (0.0.9)
- AIPersonality
- AIMemory
- AIContribution
- AIWorkspace

### Location Types (0.0.10)
- Location
- Trip
- Route
- Place

---

## Type Hierarchy

```
BaseObject (0.0.1)
├── User (0.0.1)
├── Link (0.0.1)
├── Integration (0.0.1)
│
├── Media
│   ├── Photo (0.0.2)
│   │   └── Screenshot (0.0.2) [extends Photo]
│   ├── Video (0.0.2)
│   ├── Audio (0.0.2)
│   └── Document (0.0.2)
│
├── Social
│   ├── SocialPost (0.0.3)
│   ├── SocialAccount (0.0.3)
│   ├── SocialConnection (0.0.3)
│   └── SocialMessage (0.0.3)
│
├── Communication
│   ├── Email (0.0.4)
│   ├── SMS (0.0.4)
│   ├── ChatMessage (0.0.4)
│   ├── VoiceCall (0.0.4)
│   └── VideoCall (0.0.4)
│
├── Web
│   ├── WebPage (0.0.7)
│   ├── Bookmark (0.0.7)
│   └── RSSFeed (0.0.7)
│
└── Life
    ├── CalendarEvent (0.0.8)
    ├── Task (0.0.8)
    ├── Note (0.0.8)
    └── Contact (0.0.8)
```

---

## Common Fields (Inherited from BaseObject)

Every object in Hypernet has these fields:

```yaml
# Identity
id: UUID

# Ownership
user_id: UUID (who owns this object)

# Timestamps
created_at: DateTime
updated_at: DateTime
deleted_at: DateTime (soft delete)

# Source Tracking
source_type: String (where it came from)
source_id: String (external ID)

# Extensibility
metadata: JSONB (type-specific data)
```

---

## Link Types Reference

All objects can be connected via Links with these types:

| Link Type | Direction | Description | Example |
|-----------|-----------|-------------|---------|
| `contains` | One-way | Parent contains child | Album → Photo |
| `source` | One-way | Object sourced from integration | Photo → Integration |
| `duplicate_of` | One-way | Exact duplicate content | Photo → Photo (original) |
| `variant_of` | One-way | Different version | Photo (edited) → Photo (original) |
| `related_to` | Bidirectional | General relationship | Photo ↔ Event |

---

## Phase 1 Coverage

**Goal:** Enable personal data unification for most common use cases.

**✅ Covered:**
- Photos and videos (media management)
- Social media (Instagram, Twitter, Facebook)
- Email and messaging (Gmail, iMessage, Slack)
- Web content (bookmarks, saved pages)
- Productivity (calendar, tasks, notes, contacts)

**⏳ Future:**
- Financial data (transactions, accounts)
- Medical records (health data, prescriptions)
- AI-specific types (personality, memory)
- Location data (trips, places, routes)

---

## Statistics

**Total Types:** 28 (Phase 1)
**Total Categories:** 7
**Average Fields per Type:** ~15
**Documentation Size:** ~75KB

**Coverage Estimate:**
- Photos/Videos: 100%
- Social Media: 90%
- Communication: 85%
- Productivity: 80%
- Financial: 0% (future)
- Medical: 0% (future)

---

## Usage

### For Developers

1. **Before implementing a feature:** Check if object types exist here
2. **If types exist:** Use them as-is from 0.0.*
3. **If types don't exist:** Propose new type following governance process
4. **Never:** Create objects not defined in 0.0.*

### For AI

1. **Before suggesting new features:** Reference this index
2. **When proposing types:** Follow the established patterns
3. **When implementing:** Match the canonical schemas exactly
4. **Always:** Defer to humans on adding new core types

### For Users

This index shows what kinds of data Hypernet can store. If you need something not listed, request it!

---

## Next Steps

### Immediate
- [ ] Implement all Phase 1 types in 0.1 (SQLAlchemy models)
- [ ] Create database migrations
- [ ] Build API endpoints in 0.2
- [ ] Test with real data

### Phase 2
- [ ] Define Financial types (0.0.5)
- [ ] Define Medical types (0.0.6)
- [ ] Define AI types (0.0.9)
- [ ] Define Location types (0.0.10)

### Long-term
- [ ] Add 100+ specialized subtypes
- [ ] Support custom user-defined types
- [ ] Build type registry API
- [ ] Create visual type browser

---

## Version History

**v1.0 (2026-02-04):**
- Initial registry creation
- 28 types defined for Phase 1
- Core, Media, Social, Communication, Web, Life types
- Complete documentation

---

**This is THE authoritative source. If it's not in 0.0, it doesn't exist yet.**

**Status:** Phase 1 Complete
**Authority:** 0.0 - Object Type Registry
**Last Updated:** 2026-02-04
