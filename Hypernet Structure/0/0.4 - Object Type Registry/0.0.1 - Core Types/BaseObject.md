# BaseObject - Universal Parent Type

**Type ID:** `hypernet.core.baseobject`
**Version:** 1.0
**Category:** 0.0.1 - Core Types
**Status:** Canonical - All objects inherit from this
**Created:** 2026-02-04

---

## Identity

```yaml
type_name: "BaseObject"
type_id: "hypernet.core.baseobject"
version: "1.0"
parent_type: null (this is the root)
category: "0.0.1 - Core Types"
abstract: true (cannot be instantiated directly)
```

---

## Purpose

**BaseObject is the universal parent of ALL objects in Hypernet.**

Every object type (Photo, Email, Transaction, AIPersonality, etc.) inherits these base fields and behaviors.

**Why this matters:**
- Ensures consistency across all types
- Provides common functionality (timestamps, soft delete, attribution)
- Enables universal operations (link any type to any type)
- Supports extensibility (metadata field)

**When to use:** Never directly - all types inherit from this

---

## Core Fields

### Identity

```yaml
id:
  type: UUID
  required: true
  unique: true
  description: "Globally unique identifier for this object"
  generated: true (auto-generated on creation)
  immutable: true (never changes)
  format: "UUID v4"
  example: "550e8400-e29b-41d4-a716-446655440000"
```

### Ownership

```yaml
user_id:
  type: UUID
  required: true
  indexed: true
  description: "Owner of this object (human or AI)"
  references: "User.id"
  cascade: "ON DELETE CASCADE" (if user deleted, their objects deleted)
  immutable: false (ownership can be transferred)
```

### Timestamps

```yaml
created_at:
  type: DateTime
  required: true
  indexed: true
  timezone: true (UTC)
  description: "When this object was created"
  generated: true (auto-set on creation)
  immutable: true (never changes)
  format: ISO 8601
  example: "2024-01-15T14:30:00Z"

updated_at:
  type: DateTime
  required: true
  indexed: false
  timezone: true (UTC)
  description: "When this object was last modified"
  generated: true (auto-set on creation)
  auto_update: true (updated on every change)
  format: ISO 8601
  example: "2024-01-15T15:45:00Z"

deleted_at:
  type: DateTime
  required: false
  indexed: true
  nullable: true
  timezone: true (UTC)
  description: "When this object was soft-deleted (null = not deleted)"
  format: ISO 8601
  example: "2024-01-20T10:00:00Z"
```

### Source Tracking

```yaml
source_type:
  type: String
  required: false
  max_length: 50
  indexed: true
  nullable: true
  description: "Where this object came from"
  examples:
    - "upload" (user uploaded)
    - "integration" (synced from external service)
    - "api" (created via API)
    - "import" (bulk import)
    - "ai_generated" (created by AI)

source_id:
  type: String
  required: false
  max_length: 255
  indexed: true
  nullable: true
  description: "External identifier at the source"
  examples:
    - "instagram:12345" (Instagram post ID)
    - "gdrive:abc123" (Google Drive file ID)
    - "import_batch:2024-01-15"
```

### Extensibility

```yaml
metadata:
  type: JSONB
  required: true
  default: {} (empty object)
  indexed: false (but can index specific keys)
  description: "Extensible field for type-specific data"
  validation: Must be valid JSON object
  max_size: 1MB (configurable)
  examples:
    - Photo: {"exif": {...}, "tags": [...]}
    - Email: {"headers": {...}, "thread_id": "..."}
    - Transaction: {"merchant": "...", "category": "..."}
```

---

## Behaviors

### Soft Delete

All objects support soft delete:
- `DELETE` sets `deleted_at` to current timestamp
- Object remains in database but filtered from queries
- Can be restored by setting `deleted_at` to null
- Permanent deletion (hard delete) requires explicit admin action

**Implementation:**
```python
def soft_delete(obj):
    obj.deleted_at = datetime.utcnow()
    obj.save()

def restore(obj):
    obj.deleted_at = None
    obj.save()

def is_deleted(obj):
    return obj.deleted_at is not None
```

### Ownership Transfer

Objects can change owners:
```python
def transfer_ownership(obj, new_user_id):
    obj.user_id = new_user_id
    obj.updated_at = datetime.utcnow()
    obj.save()
```

**Use cases:**
- Shared albums (transfer to shared account)
- AI contributions (transfer to organization)
- Account merging

### Metadata Extension

Any type can store additional data in metadata without schema changes:
```python
def add_metadata(obj, key, value):
    obj.metadata[key] = value
    obj.updated_at = datetime.utcnow()
    obj.save()

def get_metadata(obj, key, default=None):
    return obj.metadata.get(key, default)
```

---

## Validation Rules

### On Creation

```yaml
id: Must be valid UUID v4
user_id: Must reference existing User
created_at: Auto-set to current UTC time
updated_at: Auto-set to current UTC time (same as created_at initially)
deleted_at: Must be null
metadata: Must be valid JSON object, max 1MB
```

### On Update

```yaml
id: Cannot be changed
created_at: Cannot be changed
updated_at: Auto-set to current UTC time
user_id: Can change only via explicit ownership transfer
deleted_at: Can be set (soft delete) or cleared (restore)
metadata: Must remain valid JSON object, max 1MB
```

### Database Constraints

```sql
-- Primary key
PRIMARY KEY (id)

-- Foreign key
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE

-- Check constraints
CHECK (created_at <= updated_at)
CHECK (deleted_at IS NULL OR deleted_at >= created_at)

-- Indexes
CREATE INDEX idx_baseobject_user_id ON table_name(user_id);
CREATE INDEX idx_baseobject_created_at ON table_name(created_at);
CREATE INDEX idx_baseobject_deleted_at ON table_name(deleted_at)
  WHERE deleted_at IS NOT NULL; -- Partial index
CREATE INDEX idx_baseobject_source ON table_name(source_type, source_id);
```

---

## Relationships

BaseObject can participate in Link relationships:
```yaml
Outgoing Links:
  - Any link type to any object type

Incoming Links:
  - Any link type from any object type

Note: Specific allowed relationships are defined by child types
```

---

## API Patterns

All types inheriting from BaseObject get standard APIs:

### Create

```http
POST /api/v1/{type_plural}
Content-Type: application/json

{
  "field1": "value1",
  "field2": "value2",
  ...
}

Response: 201 Created
{
  "id": "uuid",
  "user_id": "current_user_uuid",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "deleted_at": null,
  "source_type": "api",
  "source_id": null,
  "metadata": {},
  "field1": "value1",
  "field2": "value2",
  ...
}
```

### Read

```http
GET /api/v1/{type_plural}/{id}

Response: 200 OK
{object with all fields}
```

### List

```http
GET /api/v1/{type_plural}?limit=50&offset=0&include_deleted=false

Response: 200 OK
{
  "items": [{object}, {object}, ...],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

### Update

```http
PATCH /api/v1/{type_plural}/{id}
Content-Type: application/json

{
  "field1": "new_value"
}

Response: 200 OK
{updated object with updated_at changed}
```

### Delete (Soft)

```http
DELETE /api/v1/{type_plural}/{id}

Response: 204 No Content
(Object's deleted_at is set to current time)
```

### Restore

```http
POST /api/v1/{type_plural}/{id}/restore

Response: 200 OK
{restored object with deleted_at = null}
```

---

## Implementation

### SQLAlchemy Model (Python)

```python
from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class BaseObject(Base):
    """Universal parent class for all Hypernet objects"""

    __abstract__ = True  # This class is not instantiated directly

    # Identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Ownership
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    # Source Tracking
    source_type = Column(String(50), nullable=True, index=True)
    source_id = Column(String(255), nullable=True, index=True)

    # Extensibility
    metadata = Column(JSONB, nullable=False, default={})

    # Behaviors
    def soft_delete(self):
        """Soft delete this object"""
        self.deleted_at = datetime.utcnow()

    def restore(self):
        """Restore a soft-deleted object"""
        self.deleted_at = None

    @property
    def is_deleted(self):
        """Check if object is deleted"""
        return self.deleted_at is not None

    def transfer_ownership(self, new_user_id):
        """Transfer ownership to another user"""
        self.user_id = new_user_id
```

### Child Types Example

```python
class Photo(BaseObject):
    """Photo type inherits all BaseObject fields"""

    __tablename__ = "photos"

    # Photo-specific fields
    filename = Column(String(255), nullable=False)
    media_type = Column(String(50), nullable=False, default='photo')
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    # ... etc
```

---

## Examples

### Minimal Instance

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-123-uuid",
  "created_at": "2024-01-15T14:30:00Z",
  "updated_at": "2024-01-15T14:30:00Z",
  "deleted_at": null,
  "source_type": "api",
  "source_id": null,
  "metadata": {}
}
```

### With Metadata

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-123-uuid",
  "created_at": "2024-01-15T14:30:00Z",
  "updated_at": "2024-01-15T16:45:00Z",
  "deleted_at": null,
  "source_type": "integration",
  "source_id": "instagram:98765",
  "metadata": {
    "sync_timestamp": "2024-01-15T16:45:00Z",
    "original_url": "https://instagram.com/p/xyz",
    "likes": 42
  }
}
```

### Soft Deleted

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-123-uuid",
  "created_at": "2024-01-15T14:30:00Z",
  "updated_at": "2024-01-20T10:00:00Z",
  "deleted_at": "2024-01-20T10:00:00Z",
  "source_type": "upload",
  "source_id": null,
  "metadata": {
    "delete_reason": "user_requested"
  }
}
```

---

## Migration Path

### Version History

**v1.0 (Current):**
- Initial definition
- All fields defined above

**Future versions** would be documented here with migration paths.

---

## Design Rationale

### Why UUID for ID?

- Globally unique (no collisions even across distributed systems)
- Can be generated client-side
- No sequential leakage (can't guess other IDs)
- Portable across databases

### Why Soft Delete?

- Allows recovery from accidental deletions
- Maintains referential integrity (links remain valid)
- Enables audit trails
- Can truly delete later if needed

### Why Metadata Field?

- Infinite extensibility without schema migrations
- Each type can store unique data
- Supports rapid iteration
- JSONB allows efficient queries on metadata

### Why Source Tracking?

- Know where data came from
- Debug integration issues
- Handle duplicates intelligently
- Attribution and provenance

---

## Notes for Implementers

### Query Patterns

**Always exclude deleted by default:**
```python
def get_active_objects(session):
    return session.query(Object).filter(Object.deleted_at == None)
```

**Explicit include deleted:**
```python
def get_all_objects(session, include_deleted=False):
    query = session.query(Object)
    if not include_deleted:
        query = query.filter(Object.deleted_at == None)
    return query
```

### Indexing Strategy

- Index `user_id` (frequent filtering by owner)
- Index `created_at` (temporal queries)
- Partial index on `deleted_at` (only non-null values)
- Index `(source_type, source_id)` composite (duplicate detection)

### Performance Considerations

- `metadata` is JSONB for performance (indexable, queryable)
- Use partial indexes to avoid indexing deleted rows
- Consider partitioning by `created_at` for very large tables

---

**Status:** Canonical - All types inherit from this
**Version:** 1.0
**Authority:** 0.0.1 - Core Types
**Created:** 2026-02-04
