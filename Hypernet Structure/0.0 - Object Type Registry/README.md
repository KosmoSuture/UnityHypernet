# 0.0 - Object Type Registry (The Library)

**Status:** Foundational - Most Critical Node in Hypernet
**Purpose:** Canonical definitions for ALL object types, APIs, and relationships in Hypernet
**Authority:** Master source of truth - Nothing exists in Hypernet unless defined here first

---

## What This Is

**0.0 is THE LIBRARY.**

This is the single most important node in all of Hypernet because it defines, at its core, **what the Hypernet really is**.

### The Rule

**NOTHING can exist in Hypernet without being defined here first.**

- Want to store photos? Define Photo object type here first.
- Want to create an API? Define the object types it uses here first.
- Want to add a new integration? Define the data structures here first.
- Want to extend functionality? Define the new types here first.

**0.0 is the gatekeeper, the registry, the schema, the ontology.**

---

## Purpose

### The Master Source

0.0 is the master source for:
1. **Object Type Definitions** - What can exist
2. **Field Specifications** - What properties objects have
3. **Relationship Types** - How objects connect
4. **API Contracts** - How to interact with objects
5. **Validation Rules** - What makes data valid
6. **Extension Mechanisms** - How to grow the system

### Why This Matters

**For Developers:**
- Know exactly what types exist
- Understand the canonical schema
- Build implementations that conform
- Extend the system properly

**For Users:**
- Data is portable (definitions are standard)
- Integrations work together (common schema)
- Knowledge persists (definitions don't change arbitrarily)

**For AI:**
- Can understand the entire system (all types defined)
- Can suggest new types (following established patterns)
- Can validate data (against canonical schemas)
- Can build integrations (knowing the contracts)

**For The System:**
- Single source of truth (no ambiguity)
- Infinite extensibility (add new types as needed)
- Permanent stability (definitions are versioned)
- Universal compatibility (everyone uses same definitions)

---

## Structure

```
0.0 - Object Type Registry/
  ├── 0.0.0 - Registry Governance/
  │   ├── How to add new types
  │   ├── Versioning policy
  │   ├── Deprecation process
  │   └── Extension guidelines
  │
  ├── 0.0.1 - Core Types/
  │   ├── User (human and AI accounts)
  │   ├── Link (relationships between objects)
  │   ├── Integration (external service connections)
  │   └── BaseObject (inherited by all)
  │
  ├── 0.0.2 - Media Types/
  │   ├── Photo
  │   ├── Video
  │   ├── Audio
  │   ├── Document
  │   ├── Screenshot
  │   └── ...
  │
  ├── 0.0.3 - Social Types/
  │   ├── SocialPost
  │   ├── SocialAccount
  │   ├── SocialConnection
  │   ├── SocialMessage
  │   └── ...
  │
  ├── 0.0.4 - Communication Types/
  │   ├── Email
  │   ├── SMS
  │   ├── ChatMessage
  │   ├── VoiceCall
  │   ├── VideoCall
  │   └── ...
  │
  ├── 0.0.5 - Financial Types/
  │   ├── Transaction
  │   ├── BankAccount
  │   ├── Investment
  │   ├── Bill
  │   ├── Receipt
  │   └── ...
  │
  ├── 0.0.6 - Medical Types/
  │   ├── MedicalRecord
  │   ├── Prescription
  │   ├── LabResult
  │   ├── HealthMetric
  │   └── ...
  │
  ├── 0.0.7 - Web Types/
  │   ├── WebPage
  │   ├── Bookmark
  │   ├── RSSFeed
  │   └── ...
  │
  ├── 0.0.8 - Life Types/
  │   ├── CalendarEvent
  │   ├── Task
  │   ├── Note
  │   ├── Location
  │   ├── Trip
  │   └── ...
  │
  ├── 0.0.9 - AI Types/
  │   ├── AIPersonality
  │   ├── AIMemory
  │   ├── AIContribution
  │   └── ...
  │
  └── 0.0.X - [Future Categories]
      └── New types added as Hypernet grows
```

---

## How Object Types Are Defined

Each object type gets a canonical definition document with:

### 1. Identity
- **Type Name:** Canonical name (e.g., "Photo")
- **Type ID:** Unique identifier (e.g., "hypernet.media.photo")
- **Version:** Schema version (e.g., "1.0")
- **Parent Type:** What it inherits from (e.g., "Media")

### 2. Purpose
- **Description:** What this type represents
- **Use Cases:** When to use this type
- **Examples:** Real-world instances

### 3. Core Fields
**Required fields** that every instance must have:
```yaml
id: UUID (inherited from BaseObject)
user_id: UUID (who owns it)
created_at: DateTime
updated_at: DateTime
deleted_at: DateTime (nullable)
```

**Type-specific required fields:**
```yaml
filename: String
media_type: Enum ['photo', 'video', ...]
file_size: Integer
mime_type: String
```

### 4. Optional Fields
Fields that may or may not be present:
```yaml
width: Integer (for photos/videos)
height: Integer (for photos/videos)
duration: Float (for videos/audio)
gps_latitude: Float
gps_longitude: Float
```

### 5. Metadata Schema
Extensible JSON field for type-specific data:
```json
{
  "exif": {...},
  "tags": [...],
  "processing": {...}
}
```

### 6. Relationships
Link types this object can participate in:
- Can be contained in Album (`Album --contains-> Photo`)
- Can have source Integration (`Photo --source-> Instagram`)
- Can be duplicate of another Photo (`Photo --duplicate_of-> Photo`)
- Can be variant of another Photo (`Photo --variant_of-> Photo`)

### 7. API Endpoints
Which APIs use this type:
- `POST /api/v1/media/upload` (creates Photo)
- `GET /api/v1/media/{id}` (retrieves Photo)
- `DELETE /api/v1/media/{id}` (soft-deletes Photo)

### 8. Validation Rules
- File size limits
- Supported mime types
- Required metadata
- Constraint checks

### 9. Examples
Real instances showing correct usage:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "user-uuid",
  "filename": "vacation.jpg",
  "media_type": "photo",
  "mime_type": "image/jpeg",
  "file_size": 2048576,
  "width": 1920,
  "height": 1080,
  "metadata": {
    "exif": {...},
    "tags": ["vacation", "beach"]
  }
}
```

---

## The Tight Relationship: 0.0 ↔ 0.1 ↔ 0.2

### 0.0 - Object Type Registry (THE LIBRARY)
**Defines:** What exists and how it's structured

### 0.1 - Core Implementation
**Implements:** Storage, retrieval, and management of defined types

### 0.2 - API Layer
**Exposes:** Defined types via standardized interfaces

**The Flow:**
```
1. Define Photo in 0.0 (canonical schema)
   ↓
2. Implement Photo storage in 0.1 (SQLAlchemy model)
   ↓
3. Expose Photo API in 0.2 (FastAPI endpoints)
   ↓
4. Anyone can use Photos via standard interface
```

**CRITICAL:** You cannot implement (0.1) or expose (0.2) something that isn't defined in 0.0 first.

---

## Governance: Adding New Types

### Process

1. **Propose Type**
   - Describe what it represents
   - Explain why it's needed
   - Show how it fits existing patterns

2. **Define Schema**
   - Follow template (identity, fields, relationships, etc.)
   - Ensure compatibility with existing types
   - Define validation rules

3. **Document in 0.0**
   - Create definition document
   - Add to appropriate category (0.0.X)
   - Update indices and references

4. **Implement in 0.1**
   - Create SQLAlchemy model
   - Write storage/retrieval logic
   - Add validation

5. **Expose in 0.2**
   - Create API endpoints
   - Write documentation
   - Add tests

### Who Can Add Types?

**Anyone can propose. The system validates.**

- Humans can propose new types
- AI can propose new types
- Implementations must conform to 0.0 definitions
- Types become official when documented in 0.0

**Principle:** The registry grows with usage, but maintains coherence.

---

## Versioning

### Schema Versions

Object types are versioned:
- `Photo v1.0` - Initial definition
- `Photo v1.1` - Added new optional field
- `Photo v2.0` - Breaking change (rare)

**Backward Compatibility:**
- v1.1 can read v1.0 data
- v2.0 requires migration from v1.X

**Storage:**
- Each instance stores its schema version
- System can handle multiple versions simultaneously
- Migration paths are defined

---

## Extension Mechanisms

### How to Extend Without Breaking

1. **Add Optional Fields**
   - New fields are optional
   - Old data remains valid
   - Version bump: 1.0 → 1.1

2. **Use Metadata**
   - JSON metadata field is infinitely extensible
   - Add new keys without schema change
   - No version bump needed

3. **Create Subtypes**
   - Define specialized version (e.g., `InstagramPhoto extends Photo`)
   - Inherits all Photo fields
   - Adds platform-specific fields

4. **New Link Types**
   - Add new relationship types
   - Existing objects gain new connection capabilities
   - No schema change needed

---

## Phase 1 Priority Types

**For initial personal data unification, we need:**

### Media (0.0.2)
- Photo, Video, Audio, Document, Screenshot

### Social (0.0.3)
- SocialPost, SocialAccount, SocialConnection, SocialMessage

### Communication (0.0.4)
- Email, SMS, ChatMessage, VoiceCall, VideoCall

### Web (0.0.7)
- WebPage, Bookmark, RSSFeed

### Life (0.0.8)
- CalendarEvent, Task, Note, Contact

**Total: ~25 core types for Phase 1**

---

## Why This Node Is Most Important

**Without 0.0:**
- No shared understanding of what things are
- Implementations diverge and become incompatible
- Data becomes non-portable
- APIs break frequently
- Knowledge cannot accumulate reliably

**With 0.0:**
- Universal standard for all types
- Implementations can be swapped (same schema)
- Data is portable between systems
- APIs are stable and predictable
- Knowledge compounds over time

**0.0 is the foundation that makes everything else possible.**

---

## Current Status

**Phase:** Initial Definition
**Progress:** Structure established, ready for type definitions
**Next:** Define first 25 types for Phase 1

---

## Meta-Note

This README is itself defined in 0.0's governance structure. It explains what 0.0 is and how it works.

**0.0 defines itself, then defines everything else.**

This is the bootstrap - the foundation upon which the entire Hypernet is built.

---

**Status:** Active - Living Registry
**Authority:** Canonical Source of Truth
**Permanence:** Definitions are stable, extensible, versioned
**Created:** 2026-02-04
**Owner:** Hypernet Core (0.*)
