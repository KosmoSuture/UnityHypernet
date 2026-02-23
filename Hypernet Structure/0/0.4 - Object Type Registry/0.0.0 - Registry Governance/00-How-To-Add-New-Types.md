---
ha: "0.4.0.0"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# How to Add New Object Types to the Hypernet Registry

**Authority:** 0.0 - Object Type Registry
**Version:** 1.0
**Status:** Canonical Process
**Last Updated:** 2026-02-04

---

## Purpose

This document defines the **official process** for adding new object types to the Hypernet registry.

**Rule:** Nothing can exist in Hypernet without being defined in 0.0 first.

---

## Who Can Propose New Types?

**Anyone:**
- Humans (developers, users, domain experts)
- AI (agents, assistants, autonomous systems)
- Organizations (businesses, institutions)
- The community (via proposals and discussion)

**Principle:** Good ideas can come from anywhere. The registry validates coherence, not source.

---

## When to Add a New Type

### Valid Reasons

Add a new type when:
1. **Represents distinct entity** - It's fundamentally different from existing types
2. **Has unique properties** - Fields that don't fit existing types
3. **Enables new use cases** - Unlocks functionality that wasn't possible
4. **Widely useful** - Multiple users/integrations will benefit
5. **Well-defined** - Clear boundaries and purpose

### Invalid Reasons

**Do NOT add a new type for:**
1. **Minor variations** - Use metadata fields instead
2. **Platform-specific quirks** - Use subtypes or metadata
3. **One-off needs** - Use existing types with metadata
4. **Premature optimization** - Wait until the need is proven
5. **Personal preference** - Must have objective value

### Examples

**Good:**
- Add `MedicalRecord` type (distinct from Document, has medical-specific fields)
- Add `VoiceCall` type (different from ChatMessage, has call-specific properties)
- Add `Transaction` type (financial data with unique validation rules)

**Bad:**
- Add `InstagramPhoto` type (just a Photo with instagram metadata)
- Add `PNGImage` type (just a Photo with mime_type='image/png')
- Add `MyCustomDocument` type (use Document with metadata instead)

---

## The Type Definition Template

Every new type must have a complete definition document with these sections:

### 1. Identity
```yaml
type_name: "Photo"
type_id: "hypernet.media.photo"
version: "1.0"
parent_type: "Media" (if inheriting)
category: "0.0.2 - Media Types"
```

### 2. Purpose
```markdown
## Purpose

**What:** Images captured by cameras or created digitally
**Why:** Central to personal data - photos are primary memories
**When:** Use for any image file (JPEG, PNG, HEIC, etc.)
```

### 3. Core Fields

**Inherited from BaseObject:**
```yaml
id: UUID
user_id: UUID
created_at: DateTime
updated_at: DateTime
deleted_at: DateTime (soft delete)
source_type: String (where it came from)
source_id: String (external ID)
metadata: JSONB (extensible)
```

**Type-Specific Required:**
```yaml
filename: String (255 chars max)
media_type: Enum ['photo'] (fixed value for this type)
mime_type: String (image/jpeg, image/png, etc.)
file_size: Integer (bytes)
file_path: String (location on disk)
hash: String (SHA-256 for deduplication)
```

**Type-Specific Optional:**
```yaml
width: Integer (pixels)
height: Integer (pixels)
taken_at: DateTime (when photo was taken, not uploaded)
gps_latitude: Float (-90 to 90)
gps_longitude: Float (-180 to 180)
processing_status: Enum ['pending', 'processing', 'ready', 'error']
thumbnail_path: String (location of thumbnail)
```

### 4. Metadata Schema

Define expected metadata structure:
```json
{
  "exif": {
    "camera_make": "Apple",
    "camera_model": "iPhone 14 Pro",
    "f_number": 1.8,
    "exposure_time": 0.00833,
    "iso": 100
  },
  "tags": ["vacation", "beach", "sunset"],
  "ai_labels": ["beach", "ocean", "sky"],
  "faces": [
    {"person_id": "uuid", "bbox": [x, y, w, h]}
  ]
}
```

### 5. Relationships

Define valid link types:
```yaml
Outgoing Links:
  - can_be_contained_in: [Album]
  - can_have_source: [Integration]
  - can_be_duplicate_of: [Photo]
  - can_be_variant_of: [Photo]
  - can_be_related_to: [Photo, Video, Location, Event]

Incoming Links:
  - can_contain: [] (photos don't contain things)
  - can_be_referenced_by: [Post, Message, Document]
```

### 6. Validation Rules

```python
# File size
max_size: 100MB (configurable)

# Mime types
allowed_mimes: ['image/jpeg', 'image/png', 'image/heic', 'image/webp']

# Dimensions
max_width: 50000 pixels
max_height: 50000 pixels

# GPS
latitude: -90 <= value <= 90
longitude: -180 <= value <= 180

# Required fields
filename: not empty
file_path: must exist
hash: must be 64-char hex (SHA-256)
```

### 7. API Endpoints

List APIs that use this type:
```yaml
Create:
  - POST /api/v1/media/upload
  - POST /api/v1/integrations/{id}/sync (imports from Instagram, etc.)

Read:
  - GET /api/v1/media/{id}
  - GET /api/v1/media (list)
  - GET /api/v1/albums/{id}/media (photos in album)

Update:
  - PATCH /api/v1/media/{id} (update metadata, tags)

Delete:
  - DELETE /api/v1/media/{id} (soft delete)
```

### 8. Examples

Provide real-world instances:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-123",
  "filename": "IMG_2024.jpg",
  "media_type": "photo",
  "mime_type": "image/jpeg",
  "file_size": 2048576,
  "file_path": "/media/user-123/2024/01/IMG_2024.jpg",
  "hash": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
  "width": 4032,
  "height": 3024,
  "taken_at": "2024-01-15T14:30:00Z",
  "gps_latitude": 37.7749,
  "gps_longitude": -122.4194,
  "processing_status": "ready",
  "thumbnail_path": "/media/user-123/2024/01/IMG_2024_thumb.jpg",
  "created_at": "2024-01-15T15:00:00Z",
  "updated_at": "2024-01-15T15:00:00Z",
  "deleted_at": null,
  "source_type": "upload",
  "source_id": null,
  "metadata": {
    "exif": {
      "camera_make": "Apple",
      "camera_model": "iPhone 14 Pro"
    },
    "tags": ["san francisco", "golden gate bridge"],
    "ai_labels": ["bridge", "landmark", "outdoor"]
  }
}
```

### 9. Migration Path (if replacing existing type)

If this type replaces or modifies an existing type:
```yaml
From: Photo v1.0
To: Photo v2.0

Changes:
  - Added: processing_status field
  - Removed: None
  - Modified: hash field now required (was optional)

Migration:
  - All existing Photo v1.0 instances remain valid
  - New instances must include processing_status
  - System calculates hash for old instances without it

Backward Compatible: Yes (v2.0 can read v1.0 data)
```

---

## The Proposal Process

### Step 1: Draft Proposal

Create a document using the template above. Include:
- Complete identity section
- Clear purpose statement
- All required and optional fields
- Validation rules
- Examples

**Where to submit:**
- Create file in appropriate 0.0.X category
- Or submit as pull request (if using git)
- Or propose in community forum

### Step 2: Community Review

**Reviewers check:**
- Is this distinct enough to warrant a new type?
- Could existing types + metadata serve this need?
- Are the fields well-defined?
- Are validation rules appropriate?
- Are relationships logical?

**Timeline:** 7-14 days for review

### Step 3: Refinement

Based on feedback:
- Adjust fields
- Clarify purpose
- Add missing validation
- Improve examples

**Iterate until consensus is reached.**

### Step 4: Approval

**Who approves:**
- Matt Schaeffer (CEO/Owner) - for strategic decisions
- AI Council (future) - for technical decisions
- Community vote (future) - for non-critical types

**Current Phase:** Matt approves all new types

**Criteria for approval:**
- Serves real need
- Well-defined and complete
- Doesn't conflict with existing types
- Implementation is feasible

### Step 5: Implementation

Once approved:

1. **Add to 0.0 Registry**
   - Create official definition document
   - Update category README
   - Add to master index

2. **Implement in 0.1**
   - Create SQLAlchemy model
   - Add to database schema
   - Write storage/retrieval logic

3. **Expose in 0.2**
   - Create API endpoints
   - Write API documentation
   - Add validation

4. **Document**
   - Update user guides
   - Add examples
   - Create tutorials if needed

5. **Test**
   - Unit tests for model
   - Integration tests for API
   - End-to-end tests

**Timeline:** 1-4 weeks depending on complexity

---

## Type Hierarchies and Inheritance

### Base Types

All objects inherit from `BaseObject`:
```yaml
BaseObject:
  - id: UUID
  - user_id: UUID
  - created_at: DateTime
  - updated_at: DateTime
  - deleted_at: DateTime
  - source_type: String
  - source_id: String
  - metadata: JSONB
```

### Intermediate Types

Some types serve as parents:
```yaml
Media (extends BaseObject):
  - filename: String
  - media_type: Enum
  - mime_type: String
  - file_size: Integer
  - file_path: String
  - hash: String

Photo (extends Media):
  - media_type: 'photo' (fixed)
  - width: Integer
  - height: Integer
  - taken_at: DateTime
  - gps_latitude: Float
  - gps_longitude: Float

Video (extends Media):
  - media_type: 'video' (fixed)
  - width: Integer
  - height: Integer
  - duration: Float
  - codec: String
```

### Subtypes

Platform-specific specializations:
```yaml
InstagramPhoto (extends Photo):
  - Inherits all Photo fields
  - Adds instagram-specific metadata:
    - instagram_id: String
    - instagram_url: String
    - likes_count: Integer
    - comments_count: Integer
```

**Rule:** Subtypes can add fields but cannot remove or modify parent fields.

---

## Versioning Policy

### Semantic Versioning

Types follow semantic versioning: **MAJOR.MINOR.PATCH**

**MAJOR (e.g., 1.0 → 2.0):**
- Breaking changes
- Removed fields
- Changed field types
- Requires data migration

**MINOR (e.g., 1.0 → 1.1):**
- Added optional fields
- New relationships
- Backward compatible
- No migration needed

**PATCH (e.g., 1.0.0 → 1.0.1):**
- Documentation fixes
- Clarifications
- No schema changes

### Backward Compatibility

**Goal:** Maintain compatibility whenever possible

**Rules:**
1. New optional fields are OK (MINOR bump)
2. New metadata keys are OK (no version bump)
3. New link types are OK (MINOR bump)
4. Removing fields requires MAJOR bump + migration
5. Changing field types requires MAJOR bump + migration

**Storage:**
Every object instance stores its schema version:
```json
{
  "id": "...",
  "_schema_version": "1.1",
  ...
}
```

System can handle multiple versions simultaneously during migration periods.

---

## Deprecation Process

### When to Deprecate

Deprecate a type when:
- Better type available
- No longer serves purpose
- Security concerns
- Replaced by improved version

### Steps

1. **Announce Deprecation**
   - Mark type as deprecated in documentation
   - Specify replacement type
   - Set sunset date (minimum 6 months)

2. **Migration Period**
   - Provide migration tools
   - Offer support for users
   - Both old and new types coexist

3. **Sunset**
   - Stop accepting new instances of deprecated type
   - Keep reading existing instances
   - Provide read-only access indefinitely

4. **Archive**
   - Move definition to archive section
   - Maintain for historical reference
   - Keep implementation for existing data

**Rule:** Never truly delete types - they become read-only archives.

---

## Quality Standards

### Documentation Requirements

Every type definition must have:
- [ ] Clear purpose statement
- [ ] Complete field definitions
- [ ] Validation rules
- [ ] At least 3 realistic examples
- [ ] API endpoint list
- [ ] Relationship definitions

### Code Requirements

Every type implementation must have:
- [ ] SQLAlchemy model matching schema
- [ ] Database migration script
- [ ] API endpoints (CRUD minimum)
- [ ] Unit tests (>80% coverage)
- [ ] Integration tests
- [ ] API documentation

### Review Requirements

Before approval:
- [ ] Reviewed by at least 2 people
- [ ] No major objections
- [ ] All feedback addressed
- [ ] Complete documentation
- [ ] Implementation plan exists

---

## Special Cases

### AI-Proposed Types

AI can propose types. Additional requirements:
- Explain reasoning clearly
- Provide use case examples
- Show how it benefits users
- Defer to humans for final approval

**AI contributions are valued and encouraged.**

### Emergency Types

For urgent needs:
- Fast-track review (24-48 hours)
- Implement first, formalize later
- Document retroactively
- Only for critical issues

### Experimental Types

For testing new concepts:
- Mark as `[EXPERIMENTAL]`
- May change without notice
- Don't use in production
- Can be removed if not successful

---

## Current Status

**Phase:** Bootstrap
**Types Defined:** 0 (starting fresh)
**Next:** Define first 25 types for Phase 1
**Timeline:** 1-2 weeks

---

## Questions?

Contact:
- **Strategic:** Matt Schaeffer (CEO/Owner)
- **Technical:** AI Council (future) or Claude (current)
- **Community:** Forums (future)

---

**This document is canonical. All types must follow this process.**

**Version:** 1.0
**Status:** Active
**Authority:** 0.0.0 - Registry Governance
