---
ha: "0.4.0.1.3"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# Link - Relationship Between Objects

**Type ID:** `hypernet.core.link`
**Version:** 1.0
**Category:** 0.0.1 - Core Types
**Parent:** BaseObject
**Status:** Active
**Created:** 2026-02-04

---

## Identity

```yaml
type_name: "Link"
type_id: "hypernet.core.link"
version: "1.0"
parent_type: "BaseObject"
category: "0.0.1 - Core Types"
```

---

## Purpose

### What
First-class relationships between any two objects in Hypernet.

### Why
- NOT just foreign keys - links are objects themselves
- Enable graph queries and traversal
- Support many-to-many relationships
- Capture relationship metadata (strength, confidence)
- Foundation for knowledge graph

### When to Use
- Connect objects: Album contains Photos
- Track provenance: Photo sourced from Instagram
- Deduplicate: Photo is duplicate_of another Photo
- Relate: Event related_to Location

---

## Inherited Fields
```yaml
id, user_id, created_at, updated_at, deleted_at, source_type, source_id, metadata
```

---

## Required Fields

```yaml
from_object_id: UUID
  - Source of relationship
  - Can be any object type

from_object_type: String(50)
  - Type name: "Photo", "Album", "User", etc.

to_object_id: UUID
  - Target of relationship
  - Can be any object type

to_object_type: String(50)
  - Type name

link_type: Enum(50)
  - "contains" (Album contains Photos)
  - "source" (Photo sourced from Integration)
  - "duplicate_of" (exact duplicate)
  - "variant_of" (different version)
  - "related_to" (general relationship)
```

---

## Optional Fields

```yaml
strength: Float (0.0 to 1.0)
  - Confidence or weight of relationship
  - Default: 1.0
  - Example: 0.85 for "probably related"

is_bidirectional: Boolean
  - Default: false
  - If true, relationship works both ways
  - Example: "related_to" is bidirectional

sort_order: Integer
  - For ordered relationships (photos in album)
  - Nullable for unordered links
```

---

## Metadata Schema

```json
{
  "relationship_details": {
    "added_by": "user|ai|system",
    "confidence": 0.89,
    "reasoning": "Same location and timestamp"
  },
  "contains": {
    "position": 5,
    "featured": true
  },
  "source": {
    "sync_timestamp": "2024-01-15T10:00:00Z",
    "original_id": "instagram:12345"
  }
}
```

---

## Relationships

Links themselves can have metadata but typically don't link to other objects.

---

## Validation

```sql
CHECK (link_type IN ('contains', 'source', 'duplicate_of', 'variant_of', 'related_to'))
CHECK (strength >= 0.0 AND strength <= 1.0)
CHECK (from_object_id != to_object_id OR from_object_type != to_object_type) -- No self-links

-- No duplicate links
UNIQUE (from_object_id, to_object_id, link_type) WHERE deleted_at IS NULL

-- Indexes for traversal
INDEX ON (from_object_id, link_type) WHERE deleted_at IS NULL
INDEX ON (to_object_id, link_type) WHERE deleted_at IS NULL
INDEX ON (from_object_id, sort_order) WHERE deleted_at IS NULL AND sort_order IS NOT NULL
```

---

## API Endpoints

```http
POST /api/v1/links (create relationship)
GET /api/v1/links?from_id={id}&link_type=contains (outgoing links)
GET /api/v1/links?to_id={id}&link_type=source (incoming links)
DELETE /api/v1/links/{id} (remove relationship)

# Convenience endpoints
POST /api/v1/albums/{id}/add-media (creates contains link)
GET /api/v1/albums/{id}/media (traverses contains links)
```

---

## Graph Queries

```python
# Find all photos in album
photos = session.query(Photo).join(Link,
    Link.to_object_id == Photo.id
).filter(
    Link.from_object_id == album_id,
    Link.link_type == 'contains',
    Link.deleted_at == None
).order_by(Link.sort_order).all()

# Find source integration for photo
integration = session.query(Integration).join(Link,
    Link.to_object_id == Integration.id
).filter(
    Link.from_object_id == photo_id,
    Link.link_type == 'source',
    Link.deleted_at == None
).first()

# Find related photos (bidirectional)
related = session.query(Photo).join(Link,
    or_(
        Link.to_object_id == Photo.id,
        Link.from_object_id == Photo.id
    )
).filter(
    Link.link_type == 'related_to',
    or_(
        Link.from_object_id == photo_id,
        Link.to_object_id == photo_id
    )
).all()
```

---

## Link Types Reference

```yaml
contains:
  - Parent contains child
  - Examples: Album → Photo, Playlist → Audio
  - Usually ordered (sort_order)
  - One-directional

source:
  - Object came from external source
  - Examples: Photo → Integration, Email → EmailAccount
  - One-directional
  - Tracks provenance

duplicate_of:
  - Exact duplicate content
  - Example: Photo → Photo (same hash)
  - One-directional (points to original)
  - Used for deduplication

variant_of:
  - Different version of same content
  - Examples: Photo (edited) → Photo (original)
  - One-directional
  - Preserves edit history

related_to:
  - General relationship
  - Examples: Photo ↔ Photo (same event), Photo ↔ Location
  - Can be bidirectional
  - Flexible metadata
```

---

**Status:** Active - Critical Core Type
**Version:** 1.0
