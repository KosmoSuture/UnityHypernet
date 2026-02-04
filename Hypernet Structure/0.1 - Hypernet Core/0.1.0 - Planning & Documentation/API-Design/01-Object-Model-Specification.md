# Hypernet Core - Object Model Specification

**Version:** 0.1.0
**Last Updated:** 2026-02-03
**Status:** Design Phase
**Related:** Database-Design/, API endpoint specifications

---

## Table of Contents

1. [Overview](#overview)
2. [Design Philosophy](#design-philosophy)
3. [Core Object Types](#core-object-types)
4. [Object Schema](#object-schema)
5. [Field Types and Validation](#field-types-and-validation)
6. [Metadata and Extensibility](#metadata-and-extensibility)
7. [Object Lifecycle](#object-lifecycle)
8. [Object Relationships](#object-relationships)
9. [Examples](#examples)

---

## Overview

The Hypernet object model defines how all data is structured, stored, and accessed through the API. It uses a **hybrid approach** combining:

- **Structured core fields** (predictable, queryable, performant)
- **Flexible metadata** (integration-specific, extensible)
- **First-class links** (relationships as objects, see Link Model spec)

This design balances:
- ✅ **Performance** - Core fields indexed and optimized
- ✅ **Flexibility** - New integrations don't require schema changes
- ✅ **Queryability** - Can filter/search by common attributes
- ✅ **Type Safety** - Strong typing in API and database

---

## Design Philosophy

### Principles

1. **Hybrid Schema**
   - Core fields are strongly typed and validated
   - Integration-specific data stored in `metadata` JSON field
   - Balance structure and flexibility

2. **Immutable IDs**
   - Every object has a unique, immutable UUID
   - UUIDs are globally unique (can merge databases later)
   - Never reused, even after deletion

3. **Ownership and Isolation**
   - Every object (except User) belongs to a single user
   - Users can only access their own objects (enforced at API + DB level)
   - Multi-tenancy via `user_id` foreign key

4. **Audit Trail**
   - All objects have `created_at`, `updated_at` timestamps
   - Deletions are soft by default (marked `deleted_at`, not removed)
   - Can reconstruct history of changes

5. **Source Tracking**
   - Objects created via integrations track their source
   - `source_type` and `source_id` fields link back to original
   - Enables sync, deduplication, and provenance

6. **Extensibility**
   - New object types can be added without breaking existing code
   - `metadata` field allows arbitrary additional data
   - Plugin architecture for type-specific behavior

---

## Core Object Types

### Phase 1 Object Types

These are the minimum object types for Phase 1 (0.1.0):

| Object Type | Purpose | Examples |
|-------------|---------|----------|
| **User** | Account, authentication, ownership | user@example.com |
| **Media** | Photos, videos, files | IMG_1234.jpg, video.mp4 |
| **Album** | Collections of media | "Vacation 2025", "Family Photos" |
| **Integration** | Connected external services | Instagram account, Google Photos |
| **Link** | Relationships between objects | Photo → Instagram Post, Photo → Album |

### Phase 2+ Object Types (Future)

Not implemented in Phase 1, but design should accommodate:

| Object Type | Purpose | Examples |
|-------------|---------|----------|
| **Post** | Social media posts | Tweet, Facebook post, Instagram story |
| **Message** | Communications | Email, SMS, chat message |
| **Contact** | People | Friends, family, colleagues |
| **Event** | Calendar events | Birthday, meeting, vacation |
| **Location** | Places | GPS coordinates, addresses |
| **Tag** | User-defined labels | #vacation, #family, #work |

---

## Object Schema

### Base Object

All objects inherit these common fields:

```python
class BaseObject:
    """Base class for all Hypernet objects"""

    # Identity
    id: UUID                    # Unique identifier (UUIDv4)
    type: str                   # Object type ("media", "album", etc.)

    # Ownership
    user_id: UUID               # Owner (foreign key to User)

    # Timestamps
    created_at: datetime        # When created (UTC, ISO 8601)
    updated_at: datetime        # Last modified (UTC, ISO 8601)
    deleted_at: datetime | None # Soft delete timestamp (null if not deleted)

    # Source Tracking
    source_type: str | None     # Where it came from ("integration", "upload", "system")
    source_id: str | None       # ID in source system (e.g., Instagram post ID)

    # Extensibility
    metadata: dict              # JSON object for additional fields
```

### User Object

```python
class User(BaseObject):
    """User account and authentication"""

    type: str = "user"          # Always "user"

    # Authentication
    email: str                  # Email address (unique, indexed)
    password_hash: str          # bcrypt or argon2 hash
    email_verified: bool        # Email verification status

    # Profile
    display_name: str | None    # Display name (optional)
    avatar_url: str | None      # Profile picture URL (optional)

    # Account Status
    is_active: bool             # Account enabled/disabled
    is_admin: bool              # Admin privileges

    # Timestamps (inherited from BaseObject)
    created_at: datetime        # Account creation
    updated_at: datetime        # Last profile update
    last_login_at: datetime     # Last successful login

    # Quotas and Limits
    storage_used: int           # Bytes used (for photos/videos)
    storage_quota: int          # Bytes allowed (default: 10 GB)

    # Metadata
    metadata: dict              # User preferences, settings, etc.
```

**Validation:**
- `email`: Valid email format, unique across all users
- `password`: Min 12 chars, complexity requirements (enforced at API level)
- `display_name`: Max 100 chars, no special characters
- `storage_quota`: Min 1GB, max 1TB (configurable)

**Indexes:**
- Primary key: `id`
- Unique: `email`
- Index: `created_at` (for user stats)

---

### Media Object

```python
class Media(BaseObject):
    """Photos, videos, and other media files"""

    type: str = "media"         # Always "media"

    # Basic Info
    filename: str               # Original filename
    media_type: str             # "photo", "video", "document", "other"
    mime_type: str              # MIME type (image/jpeg, video/mp4, etc.)

    # File Information
    size: int                   # File size in bytes
    width: int | None           # Image/video width in pixels
    height: int | None          # Image/video height in pixels
    duration: float | None      # Video duration in seconds

    # Storage
    file_path: str              # Path in /media partition (relative)
    thumbnail_path: str | None  # Path to thumbnail (if generated)
    hash: str                   # SHA-256 hash of file (for deduplication)

    # Dates and Location
    taken_at: datetime | None   # When photo/video was taken (from EXIF)
    latitude: float | None      # GPS latitude (from EXIF)
    longitude: float | None     # GPS longitude (from EXIF)

    # Source Tracking (inherited, but commonly used)
    source_type: str | None     # "upload", "integration", "import"
    source_id: str | None       # External ID (e.g., Instagram media ID)

    # Processing Status
    processing_status: str      # "pending", "processing", "complete", "failed"
    thumbnail_generated: bool   # Has thumbnail been created?
    metadata_extracted: bool    # Has EXIF/metadata been extracted?

    # Metadata (EXIF and more)
    metadata: dict              # {
                                #   "exif": {...},          # EXIF data
                                #   "camera": "iPhone 15",  # Camera model
                                #   "tags": ["vacation"],   # User tags
                                #   "description": "...",   # User description
                                #   "integration_data": {...} # Integration-specific
                                # }
```

**Validation:**
- `filename`: Max 255 chars, valid filename chars
- `media_type`: One of ["photo", "video", "document", "other"]
- `mime_type`: Valid MIME type from allowed list
- `size`: Max 100MB for photos, 1GB for videos (configurable)
- `hash`: Valid SHA-256 hash (64 hex chars)
- `latitude`: -90 to 90
- `longitude`: -180 to 180
- `processing_status`: One of ["pending", "processing", "complete", "failed"]

**Indexes:**
- Primary key: `id`
- Foreign key: `user_id` (with index)
- Index: `hash` (for deduplication)
- Index: `taken_at` (for timeline queries)
- Index: `media_type` (for filtering)
- Composite: `(user_id, source_type, source_id)` (for sync deduplication)

**File Path Convention:**
```
/media/users/{user_id}/media/{year}/{month}/{id}.{ext}
Example: /media/users/a1b2c3d4-1234-5678-abcd-123456789abc/media/2026/02/e5f6g7h8-5678-90ab-cdef-567890abcdef.jpg
```

---

### Album Object

```python
class Album(BaseObject):
    """Collection of media objects"""

    type: str = "album"         # Always "album"

    # Basic Info
    name: str                   # Album name
    description: str | None     # Album description (optional)

    # Display
    cover_media_id: UUID | None # Media object to use as cover (foreign key)
    sort_order: str             # "date_asc", "date_desc", "manual"

    # Counts (denormalized for performance)
    media_count: int            # Number of media in album (cached)

    # Privacy (Phase 2)
    visibility: str             # "private", "unlisted", "public" (future)

    # Metadata
    metadata: dict              # {
                                #   "color": "#ff5733",    # Theme color
                                #   "icon": "camera",      # Icon name
                                #   "tags": [...],         # Tags
                                # }
```

**Validation:**
- `name`: Max 200 chars, required
- `description`: Max 5000 chars
- `sort_order`: One of ["date_asc", "date_desc", "manual"]
- `visibility`: One of ["private", "unlisted", "public"]
- `media_count`: >= 0

**Indexes:**
- Primary key: `id`
- Foreign key: `user_id` (with index)
- Foreign key: `cover_media_id` (nullable)
- Index: `name` (for search)

**Notes:**
- Media ↔ Album relationship handled via Link objects (many-to-many)
- A media object can be in multiple albums
- An album can contain many media objects

---

### Integration Object

```python
class Integration(BaseObject):
    """Connected external service (Instagram, Google Photos, etc.)"""

    type: str = "integration"   # Always "integration"

    # Integration Details
    integration_type: str       # "instagram", "google_photos", "facebook", etc.
    integration_name: str       # Display name (e.g., "@username")

    # Status
    status: str                 # "connected", "disconnected", "error", "pending"
    is_enabled: bool            # User can disable without disconnecting

    # OAuth2 (for integrations requiring OAuth)
    access_token: str | None    # OAuth access token (encrypted)
    refresh_token: str | None   # OAuth refresh token (encrypted)
    token_expires_at: datetime | None  # Token expiration

    # Sync State
    last_sync_at: datetime | None      # Last successful sync
    last_sync_status: str              # "success", "partial", "failed"
    sync_cursor: str | None            # Cursor/offset for incremental sync

    # Statistics
    items_synced: int           # Total items imported from this integration

    # Metadata
    metadata: dict              # {
                                #   "user_id": "...",        # External user ID
                                #   "username": "@john",     # External username
                                #   "profile_url": "...",    # External profile
                                #   "sync_settings": {...},  # What to sync
                                #   "rate_limit": {...},     # API rate limit info
                                # }
```

**Validation:**
- `integration_type`: One of allowed integration types
- `integration_name`: Max 200 chars
- `status`: One of ["connected", "disconnected", "error", "pending"]
- `last_sync_status`: One of ["success", "partial", "failed"]
- `items_synced`: >= 0

**Indexes:**
- Primary key: `id`
- Foreign key: `user_id` (with index)
- Composite: `(user_id, integration_type)` (user can have multiple of same type)
- Index: `status` (for monitoring)

**Security:**
- `access_token` and `refresh_token` encrypted at rest (database-level encryption)
- Never returned in API responses (use `[REDACTED]` placeholder)
- Stored in encrypted secrets table (separate from main Integration table)

---

### Link Object

```python
class Link(BaseObject):
    """Relationship between two objects"""

    type: str = "link"          # Always "link"

    # Link Endpoints
    from_object_id: UUID        # Source object ID (foreign key)
    from_object_type: str       # Source object type ("media", "album", etc.)
    to_object_id: UUID          # Target object ID (foreign key)
    to_object_type: str         # Target object type

    # Link Type
    link_type: str              # Relationship type (see below)

    # Link Properties
    strength: float             # Confidence/strength (0.0 to 1.0)
    is_bidirectional: bool      # Does link go both ways?

    # Ordering (for ordered relationships like album → photos)
    sort_order: int | None      # Position in ordered list (null if unordered)

    # Metadata
    metadata: dict              # {
                                #   "created_by": "system" | "user",
                                #   "reason": "...",
                                #   "properties": {...}
                                # }
```

**Link Types:**

| Link Type | From → To | Description | Example |
|-----------|-----------|-------------|---------|
| `contains` | Album → Media | Album contains media | "Vacation" album contains photo123 |
| `source` | Media → Integration | Media came from integration | photo456 sourced from Instagram |
| `duplicate_of` | Media → Media | Duplicate detection | photo789 is duplicate of photo123 |
| `variant_of` | Media → Media | Different version | thumbnail is variant of original |
| `related_to` | Any → Any | Generic relationship | (future use) |
| `tagged_with` | Media → Tag | Media has tag | (Phase 2) |
| `depicts` | Media → Contact | Media shows person | (Phase 2) |
| `taken_at` | Media → Location | Media taken at location | (Phase 2) |

**Validation:**
- `from_object_id`, `to_object_id`: Valid UUIDs, objects must exist
- `from_object_type`, `to_object_type`: Valid object types
- `link_type`: One of allowed link types
- `strength`: 0.0 to 1.0
- `sort_order`: >= 0

**Indexes:**
- Primary key: `id`
- Foreign key: `user_id` (with index)
- Composite: `(from_object_id, link_type)` (fast "get all links from object")
- Composite: `(to_object_id, link_type)` (fast "get all links to object")
- Composite: `(from_object_id, to_object_id, link_type)` (prevent duplicate links)

**Constraints:**
- Unique constraint on `(from_object_id, to_object_id, link_type)` - no duplicate links
- Objects can't link to themselves (checked at API level)
- `from_object` and `to_object` must belong to same user (enforced at API + DB)

**See:** `02-Link-Model-Specification.md` for detailed link semantics

---

## Field Types and Validation

### Data Types

| Type | Python Type | PostgreSQL Type | Validation |
|------|-------------|-----------------|------------|
| **UUID** | `uuid.UUID` | `UUID` | UUIDv4 format |
| **String** | `str` | `VARCHAR(n)` or `TEXT` | Max length, allowed chars |
| **Integer** | `int` | `INTEGER` or `BIGINT` | Range checks |
| **Float** | `float` | `DOUBLE PRECISION` | Range checks |
| **Boolean** | `bool` | `BOOLEAN` | True/False only |
| **Datetime** | `datetime` | `TIMESTAMP WITH TIME ZONE` | ISO 8601, UTC |
| **JSON** | `dict` | `JSONB` | Valid JSON, schema validation |
| **Enum** | `str` | `VARCHAR` or `ENUM` | One of allowed values |

### String Validation

```python
# Email
pattern: r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
max_length: 255

# Filename
pattern: r'^[a-zA-Z0-9._-]+$'  # No path separators, special chars
max_length: 255

# Display Name
pattern: r'^[a-zA-Z0-9 ._-]+$'  # Alphanumeric + space and common punctuation
max_length: 100

# File Path
pattern: r'^[a-zA-Z0-9/._-]+$'  # Unix-style paths
max_length: 1024

# SHA-256 Hash
pattern: r'^[a-f0-9]{64}$'      # 64 hex characters
length: 64
```

### Datetime Handling

- **Storage:** Always UTC, stored as `TIMESTAMP WITH TIME ZONE`
- **API:** ISO 8601 format (`2026-02-03T12:34:56.789Z`)
- **Timezone:** Server converts to UTC, clients handle local display
- **Precision:** Milliseconds (3 decimal places)

### JSON Metadata

- **Storage:** PostgreSQL `JSONB` (binary, indexed, queryable)
- **Validation:** Must be valid JSON object `{}`
- **Max Size:** 1MB per metadata field (configurable)
- **Indexing:** Can create GIN indexes on specific keys

**Example:**
```json
{
  "exif": {
    "camera": "Canon EOS R5",
    "lens": "RF 24-70mm f/2.8",
    "iso": 400,
    "aperture": "f/2.8",
    "shutter_speed": "1/250",
    "focal_length": "50mm"
  },
  "tags": ["vacation", "beach", "sunset"],
  "description": "Beautiful sunset at the beach",
  "location_name": "Santa Monica Beach",
  "instagram": {
    "post_id": "ABC123XYZ",
    "likes": 42,
    "comments": 5,
    "caption": "Amazing sunset! 🌅"
  }
}
```

---

## Metadata and Extensibility

### Core vs. Metadata

**Core Fields:**
- Defined in object schema
- Strongly typed and validated
- Indexed for performance
- Common across all instances of object type
- **Examples:** `id`, `user_id`, `created_at`, `filename`, `size`

**Metadata Fields:**
- Stored in `metadata` JSON column
- Flexible structure
- Integration-specific or optional
- Can be indexed selectively (JSONB GIN indexes)
- **Examples:** EXIF data, external IDs, user-defined tags, custom properties

### When to Use Core vs. Metadata

**Use Core Field When:**
- Field is required for all instances
- Field needs to be indexed for performance
- Field is used in frequent queries or filters
- Field has strict validation requirements

**Use Metadata When:**
- Field is optional or integration-specific
- Field structure varies by source
- Field is rarely queried
- Field is user-defined or extensible

### Metadata Schema Evolution

Metadata is **schema-less** but **conventionally structured**:

```python
# Convention for metadata structure
metadata = {
    # EXIF data (for photos/videos)
    "exif": {
        "camera": str,
        "lens": str,
        "iso": int,
        "aperture": str,
        "shutter_speed": str,
        # ... more EXIF fields
    },

    # User-defined tags
    "tags": [str, str, ...],

    # User description
    "description": str,

    # Integration-specific data (namespaced by integration type)
    "instagram": {
        "post_id": str,
        "permalink": str,
        "likes": int,
        "comments": int,
        "caption": str,
        "hashtags": [str, ...]
    },

    "google_photos": {
        "media_item_id": str,
        "product_url": str,
        "base_url": str,
        "album_id": str
    },

    # Any other custom fields
    "custom": {
        # User or plugin-defined fields
    }
}
```

**Validation:**
- Metadata must be valid JSON
- Max size: 1MB (configurable)
- No PII in metadata unless explicitly user-provided
- Scrub sensitive data from integration metadata

---

## Object Lifecycle

### Creation

```
1. API receives object creation request
2. Validate request payload (Pydantic model)
3. Generate UUID for object ID
4. Set user_id from authenticated user
5. Set created_at, updated_at to current time
6. Initialize metadata to {}
7. Insert into database
8. Return created object in response
```

### Read

```
1. API receives object read request (by ID)
2. Authenticate user
3. Query database for object by ID
4. Verify object.user_id == authenticated user
5. Return object in response (or 404/403)
```

### Update

```
1. API receives object update request (by ID)
2. Authenticate user
3. Load existing object from database
4. Verify object.user_id == authenticated user
5. Validate update payload
6. Merge changes (preserve immutable fields)
7. Set updated_at to current time
8. Update in database
9. Return updated object in response
```

### Delete

**Soft Delete (Default):**
```
1. API receives delete request (by ID)
2. Authenticate user
3. Load object from database
4. Verify object.user_id == authenticated user
5. Set deleted_at to current time
6. Update in database
7. Return 204 No Content
```

**Hard Delete (Admin Only, Permanent):**
```
1. Verify user is admin
2. Delete associated files (media files, thumbnails)
3. Delete associated links (cascade)
4. Delete object from database (permanent)
5. Return 204 No Content
```

**Soft-Deleted Objects:**
- Not returned in normal queries (WHERE deleted_at IS NULL)
- Can be restored by admin (set deleted_at = NULL)
- Permanently deleted after retention period (e.g., 30 days)

---

## Object Relationships

### Ownership

```
User
  └── owns many → Media
  └── owns many → Album
  └── owns many → Integration
  └── owns many → Link
```

**Enforcement:**
- All non-User objects have `user_id` foreign key
- API enforces: user can only access their own objects
- Database enforces: `ON DELETE CASCADE` for user deletion

### Media Relationships

```
Media
  ├── belongs to → User (via user_id)
  ├── in many → Album (via Link: Album → Media)
  ├── sourced from → Integration (via Link: Media → Integration)
  ├── has variants → Media (via Link: Media → Media, type "variant_of")
  └── has metadata → JSONB (inline)
```

### Album Relationships

```
Album
  ├── belongs to → User (via user_id)
  ├── contains many → Media (via Link: Album → Media)
  └── has cover → Media (via cover_media_id foreign key)
```

### Integration Relationships

```
Integration
  ├── belongs to → User (via user_id)
  └── sourced many → Media (via Link: Media → Integration)
```

---

## Examples

### Example 1: Upload a Photo

**Request:**
```http
POST /api/v1/media/upload
Authorization: Bearer {jwt_token}
Content-Type: multipart/form-data

{file: photo.jpg}
```

**Created Object:**
```json
{
  "id": "a1b2c3d4-1234-5678-abcd-123456789abc",
  "type": "media",
  "user_id": "e5f6g7h8-5678-90ab-cdef-567890abcdef",
  "created_at": "2026-02-03T12:34:56.789Z",
  "updated_at": "2026-02-03T12:34:56.789Z",
  "deleted_at": null,
  "source_type": "upload",
  "source_id": null,
  "filename": "photo.jpg",
  "media_type": "photo",
  "mime_type": "image/jpeg",
  "size": 2457600,
  "width": 4032,
  "height": 3024,
  "duration": null,
  "file_path": "users/e5f6g7h8.../media/2026/02/a1b2c3d4....jpg",
  "thumbnail_path": "users/e5f6g7h8.../thumbnails/a1b2c3d4....jpg",
  "hash": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
  "taken_at": "2026-02-01T14:23:45.000Z",
  "latitude": 34.0195,
  "longitude": -118.4912,
  "processing_status": "complete",
  "thumbnail_generated": true,
  "metadata_extracted": true,
  "metadata": {
    "exif": {
      "camera": "iPhone 15 Pro",
      "lens": "iPhone 15 Pro back triple camera 6.86mm f/1.78",
      "iso": 64,
      "aperture": "f/1.78",
      "shutter_speed": "1/2000"
    },
    "tags": [],
    "description": null
  }
}
```

### Example 2: Create an Album

**Request:**
```http
POST /api/v1/albums
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "name": "Vacation 2026",
  "description": "Photos from our trip to California"
}
```

**Created Object:**
```json
{
  "id": "b2c3d4e5-2345-6789-bcde-234567890bcd",
  "type": "album",
  "user_id": "e5f6g7h8-5678-90ab-cdef-567890abcdef",
  "created_at": "2026-02-03T12:40:00.123Z",
  "updated_at": "2026-02-03T12:40:00.123Z",
  "deleted_at": null,
  "source_type": "user",
  "source_id": null,
  "name": "Vacation 2026",
  "description": "Photos from our trip to California",
  "cover_media_id": null,
  "sort_order": "date_desc",
  "media_count": 0,
  "visibility": "private",
  "metadata": {}
}
```

### Example 3: Add Photo to Album (via Link)

**Request:**
```http
POST /api/v1/links
Authorization: Bearer {jwt_token}
Content-Type: application/json

{
  "from_object_id": "b2c3d4e5-2345-6789-bcde-234567890bcd",
  "from_object_type": "album",
  "to_object_id": "a1b2c3d4-1234-5678-abcd-123456789abc",
  "to_object_type": "media",
  "link_type": "contains",
  "sort_order": 0
}
```

**Created Link:**
```json
{
  "id": "c3d4e5f6-3456-7890-cdef-345678901cde",
  "type": "link",
  "user_id": "e5f6g7h8-5678-90ab-cdef-567890abcdef",
  "created_at": "2026-02-03T12:45:00.456Z",
  "updated_at": "2026-02-03T12:45:00.456Z",
  "deleted_at": null,
  "from_object_id": "b2c3d4e5-2345-6789-bcde-234567890bcd",
  "from_object_type": "album",
  "to_object_id": "a1b2c3d4-1234-5678-abcd-123456789abc",
  "to_object_type": "media",
  "link_type": "contains",
  "strength": 1.0,
  "is_bidirectional": false,
  "sort_order": 0,
  "metadata": {
    "created_by": "user"
  }
}
```

### Example 4: Integration Sync (Instagram)

**Integration Object:**
```json
{
  "id": "d4e5f6g7-4567-8901-defg-456789012def",
  "type": "integration",
  "user_id": "e5f6g7h8-5678-90ab-cdef-567890abcdef",
  "created_at": "2026-02-03T10:00:00.000Z",
  "updated_at": "2026-02-03T12:50:00.789Z",
  "deleted_at": null,
  "integration_type": "instagram",
  "integration_name": "@johnsmith",
  "status": "connected",
  "is_enabled": true,
  "access_token": "[REDACTED]",
  "refresh_token": "[REDACTED]",
  "token_expires_at": "2026-03-03T10:00:00.000Z",
  "last_sync_at": "2026-02-03T12:50:00.789Z",
  "last_sync_status": "success",
  "sync_cursor": "next_page_abc123",
  "items_synced": 150,
  "metadata": {
    "user_id": "instagram_user_12345",
    "username": "johnsmith",
    "profile_url": "https://instagram.com/johnsmith",
    "sync_settings": {
      "import_posts": true,
      "import_stories": false,
      "import_reels": true
    }
  }
}
```

**Media Created from Instagram:**
```json
{
  "id": "f6g7h8i9-6789-0123-fghi-678901234fgh",
  "type": "media",
  "user_id": "e5f6g7h8-5678-90ab-cdef-567890abcdef",
  "source_type": "integration",
  "source_id": "instagram_media_abc123xyz",
  "filename": "instagram_post_2026_01_15.jpg",
  "media_type": "photo",
  "taken_at": "2026-01-15T18:30:00.000Z",
  "metadata": {
    "instagram": {
      "post_id": "abc123xyz",
      "permalink": "https://instagram.com/p/abc123xyz",
      "caption": "Amazing sunset! 🌅 #sunset #beach",
      "likes": 127,
      "comments": 8,
      "hashtags": ["sunset", "beach"]
    }
  }
}
```

**Link (Media → Integration):**
```json
{
  "from_object_id": "f6g7h8i9-6789-0123-fghi-678901234fgh",
  "from_object_type": "media",
  "to_object_id": "d4e5f6g7-4567-8901-defg-456789012def",
  "to_object_type": "integration",
  "link_type": "source",
  "metadata": {
    "created_by": "system",
    "reason": "instagram_sync",
    "sync_timestamp": "2026-02-03T12:50:00.789Z"
  }
}
```

---

## Open Questions

1. **Object Versioning?**
   - Should we track version history for objects?
   - Store previous versions in separate table?
   - Defer to Phase 2?

2. **Cascading Deletes?**
   - When user deletes media, delete links automatically?
   - When album deleted, delete links but keep media?
   - Database CASCADE vs. application logic?

3. **Metadata Schema Validation?**
   - Should we enforce schema for common metadata patterns?
   - Use JSON Schema validation for known structures?
   - Or keep fully flexible?

4. **Performance Optimization?**
   - Denormalize media_count in Album?
   - Materialize views for common queries?
   - When to add indexes?

---

## Next Steps

- [ ] Review and approve object model
- [ ] Design database schema (see Database-Design/)
- [ ] Define API endpoints (see 03-API-Endpoints.md)
- [ ] Implement Pydantic models for validation
- [ ] Create SQLAlchemy ORM models
- [ ] Write database migrations

---

**Status:** Draft - Ready for review and feedback
**Next Document:** `02-Link-Model-Specification.md` (detailed link semantics)
