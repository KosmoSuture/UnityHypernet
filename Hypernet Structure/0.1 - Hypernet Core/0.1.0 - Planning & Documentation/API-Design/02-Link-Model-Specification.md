# Hypernet Core - Link Model Specification

**Version:** 0.1.0
**Last Updated:** 2026-02-03
**Status:** Design Phase
**Related:** 01-Object-Model-Specification.md, Database-Design/

---

## Table of Contents

1. [Overview](#overview)
2. [Design Philosophy](#design-philosophy)
3. [Link Types](#link-types)
4. [Link Semantics](#link-semantics)
5. [Link Operations](#link-operations)
6. [Querying Links](#querying-links)
7. [Link Constraints](#link-constraints)
8. [Examples](#examples)

---

## Overview

Links represent **relationships between objects** in Hypernet. Unlike traditional foreign keys, links are **first-class objects** with their own properties, metadata, and lifecycle.

### Why First-Class Links?

**Traditional Approach (Foreign Keys):**
```python
class Media:
    album_id: UUID  # Can only be in one album
```

**Problems:**
- Media can only belong to one album
- Can't represent many-to-many relationships
- Can't add metadata to relationships (when added, why, confidence)
- Hard to query "all relationships for object X"

**Hypernet Approach (Link Objects):**
```python
class Link:
    from_object_id: UUID  # Album
    to_object_id: UUID    # Media
    link_type: "contains"
    strength: 1.0
    metadata: {"added_by": "user", "date": "..."}
```

**Benefits:**
- ✅ Media can be in multiple albums
- ✅ Rich metadata on relationships (who, when, why, confidence)
- ✅ Flexible relationship types without schema changes
- ✅ Easy to query all relationships for an object
- ✅ Can represent complex graphs (not just trees)

---

## Design Philosophy

### Principles

1. **Links are Objects**
   - Have unique IDs, timestamps, metadata
   - Can be created, read, updated, deleted
   - Belong to a user (same as from/to objects)

2. **Directionality**
   - Links have direction: `from_object → to_object`
   - Can be marked bidirectional if semantics are symmetric
   - Examples:
     - `Album → Media` (unidirectional: album contains media)
     - `Media ↔ Media` (bidirectional: duplicate_of is symmetric)

3. **Type Safety**
   - Link types define allowed from/to object types
   - Validation enforced at API level
   - Examples:
     - `contains`: Only `Album → Media` or `Album → Album`
     - `source`: Only `Media → Integration`

4. **Cardinality**
   - Link types define allowed cardinality (one-to-one, one-to-many, many-to-many)
   - Enforced by database constraints or application logic
   - Examples:
     - `Album → Media`: One-to-many (album can have many media)
     - `Media → Integration`: Many-to-one (media has one source)

5. **Ordering**
   - Links can be ordered via `sort_order` field
   - Used for sequences (photos in album, slides in presentation)
   - Null `sort_order` means unordered

6. **Strength/Confidence**
   - Links have `strength` field (0.0 to 1.0)
   - Used for:
     - Confidence in automated links (AI-detected duplicates: 0.85)
     - User-confirmed links (user says "this is a duplicate": 1.0)
     - Weak suggestions (might be related: 0.3)

---

## Link Types

### Phase 1 Link Types

| Link Type | From → To | Bidirectional | Cardinality | Description |
|-----------|-----------|---------------|-------------|-------------|
| **contains** | Album → Media | No | 1:N | Album contains media items |
| **contains** | Album → Album | No | 1:N | Album contains sub-albums (nested) |
| **source** | Media → Integration | No | N:1 | Media sourced from integration |
| **duplicate_of** | Media → Media | Yes | N:N | Media is duplicate of another |
| **variant_of** | Media → Media | No | N:1 | Media is variant (thumbnail, edited) |

### Phase 2+ Link Types (Future)

| Link Type | From → To | Bidirectional | Cardinality | Description |
|-----------|-----------|---------------|-------------|-------------|
| **tagged_with** | Media → Tag | No | N:N | Media has tag |
| **depicts** | Media → Contact | No | N:N | Media shows person (face detection) |
| **taken_at** | Media → Location | No | N:1 | Media taken at location |
| **posted_to** | Media → Post | No | 1:N | Media shared in social post |
| **sent_in** | Media → Message | No | N:N | Media attached to message |
| **related_to** | Any → Any | Yes | N:N | Generic relationship (user-defined) |

---

## Link Semantics

### `contains` (Album → Media)

**Meaning:** Album contains media item

**Properties:**
- **Directionality:** Unidirectional (Album owns the relationship)
- **Cardinality:** One-to-many (album can have many media, media can be in many albums)
- **Ordered:** Yes (via `sort_order` field)
- **Strength:** Always 1.0 (user explicitly added to album)

**Use Cases:**
- User creates album "Vacation 2026" and adds photos
- Photos displayed in album order (sorted by `sort_order`)
- Deleting link removes photo from album (but doesn't delete photo)

**Validation:**
- `from_object_type` must be "album"
- `to_object_type` must be "media"
- Both objects must belong to same user
- `sort_order` must be unique within album (no two photos at same position)

**Database Constraints:**
- Unique: `(from_object_id, to_object_id)` - can't add same photo twice
- Check: `from_object_type = 'album' AND to_object_type = 'media'`

**Example:**
```json
{
  "from_object_id": "album-uuid",
  "from_object_type": "album",
  "to_object_id": "photo-uuid",
  "to_object_type": "media",
  "link_type": "contains",
  "strength": 1.0,
  "is_bidirectional": false,
  "sort_order": 5,
  "metadata": {
    "created_by": "user",
    "added_at": "2026-02-03T12:00:00Z"
  }
}
```

---

### `contains` (Album → Album)

**Meaning:** Album contains sub-album (nested albums)

**Properties:**
- **Directionality:** Unidirectional (parent album owns relationship)
- **Cardinality:** One-to-many (album can have many sub-albums)
- **Ordered:** Yes (via `sort_order`)
- **Strength:** Always 1.0

**Use Cases:**
- User organizes albums hierarchically:
  - "Vacations" (parent album)
    - "Europe 2025" (sub-album)
    - "Asia 2026" (sub-album)

**Validation:**
- `from_object_type` must be "album"
- `to_object_type` must be "album"
- Both albums must belong to same user
- **Circular Reference Prevention:** Album can't contain itself (directly or indirectly)

**Circular Reference Check:**
```python
def can_add_subalbum(parent_id, child_id):
    """Prevent circular references in album hierarchy"""
    # Check if child is ancestor of parent
    ancestors = get_ancestor_albums(parent_id)
    if child_id in ancestors:
        raise ValueError("Would create circular reference")
    return True
```

---

### `source` (Media → Integration)

**Meaning:** Media was imported from external integration

**Properties:**
- **Directionality:** Unidirectional (media points to source)
- **Cardinality:** Many-to-one (many media from one integration)
- **Ordered:** No
- **Strength:** Always 1.0 (definitive source tracking)

**Use Cases:**
- Track which integration a photo came from (Instagram, Google Photos, etc.)
- Enable re-sync or update from source
- Prevent duplicate imports (check if media with same source_id exists)

**Validation:**
- `from_object_type` must be "media"
- `to_object_type` must be "integration"
- Both objects must belong to same user
- Media can only have **one source** (enforced by unique constraint)

**Database Constraints:**
- Unique: `(from_object_id)` - media can only have one source
- Check: `from_object_type = 'media' AND to_object_type = 'integration'`

**Example:**
```json
{
  "from_object_id": "photo-uuid",
  "from_object_type": "media",
  "to_object_id": "instagram-integration-uuid",
  "to_object_type": "integration",
  "link_type": "source",
  "strength": 1.0,
  "is_bidirectional": false,
  "sort_order": null,
  "metadata": {
    "created_by": "system",
    "sync_timestamp": "2026-02-03T10:30:00Z",
    "external_id": "instagram_post_abc123"
  }
}
```

---

### `duplicate_of` (Media → Media)

**Meaning:** Media is a duplicate of another media

**Properties:**
- **Directionality:** Bidirectional (if A is duplicate of B, then B is duplicate of A)
- **Cardinality:** Many-to-many (complex duplicate graphs possible)
- **Ordered:** No
- **Strength:** 0.0 to 1.0 (confidence in duplicate detection)

**Use Cases:**
- Automatic duplicate detection (same hash or perceptual hash)
- User confirms/rejects duplicates
- Display deduplicated media views
- Bulk operations (delete all duplicates)

**Validation:**
- `from_object_type` and `to_object_type` must both be "media"
- Both objects must belong to same user
- Objects must be different (`from_object_id != to_object_id`)
- When creating A → B, automatically create B → A (bidirectional)

**Strength Values:**
- `1.0`: User confirmed duplicate
- `0.9-0.99`: Identical hash (definite duplicate)
- `0.7-0.89`: High perceptual similarity (very likely duplicate)
- `0.5-0.69`: Moderate similarity (possible duplicate, needs review)
- `< 0.5`: Low confidence (suggestion only)

**Example:**
```json
// Link 1: Photo A → Photo B
{
  "from_object_id": "photo-a-uuid",
  "from_object_type": "media",
  "to_object_id": "photo-b-uuid",
  "to_object_type": "media",
  "link_type": "duplicate_of",
  "strength": 0.95,
  "is_bidirectional": true,
  "metadata": {
    "created_by": "system",
    "detection_method": "hash_match",
    "hash_match": true,
    "perceptual_similarity": 0.98
  }
}

// Link 2: Photo B → Photo A (auto-created)
{
  "from_object_id": "photo-b-uuid",
  "from_object_type": "media",
  "to_object_id": "photo-a-uuid",
  "to_object_type": "media",
  "link_type": "duplicate_of",
  "strength": 0.95,
  "is_bidirectional": true,
  "metadata": {
    "created_by": "system",
    "detection_method": "hash_match",
    "hash_match": true,
    "perceptual_similarity": 0.98,
    "reverse_of": "link-1-uuid"
  }
}
```

---

### `variant_of` (Media → Media)

**Meaning:** Media is a variant/derivative of another media

**Properties:**
- **Directionality:** Unidirectional (variant points to original)
- **Cardinality:** Many-to-one (many variants of one original)
- **Ordered:** No
- **Strength:** Always 1.0 (definitive relationship)

**Use Cases:**
- Thumbnails of original photos
- Edited versions of photos
- Transcoded videos (different formats/resolutions)
- Cropped or rotated versions

**Validation:**
- `from_object_type` and `to_object_type` must both be "media"
- Both objects must belong to same user
- Objects must be different
- **No Circular Variants:** Variant can't be variant of itself (directly or indirectly)

**Variant Types (in metadata):**
```json
{
  "variant_type": "thumbnail",  // or "edited", "transcoded", "cropped"
  "variant_properties": {
    "size": "large",           // For thumbnails: "small", "medium", "large"
    "operation": "crop",       // For edited: "crop", "rotate", "filter"
    "format": "mp4"            // For transcoded: target format
  }
}
```

**Example:**
```json
{
  "from_object_id": "thumbnail-uuid",
  "from_object_type": "media",
  "to_object_id": "original-photo-uuid",
  "to_object_type": "media",
  "link_type": "variant_of",
  "strength": 1.0,
  "is_bidirectional": false,
  "metadata": {
    "created_by": "system",
    "variant_type": "thumbnail",
    "variant_properties": {
      "size": "large",
      "dimensions": "800x600",
      "generated_at": "2026-02-03T10:00:00Z"
    }
  }
}
```

---

## Link Operations

### Creating Links

**API Endpoint:** `POST /api/v1/links`

**Request:**
```json
{
  "from_object_id": "album-uuid",
  "from_object_type": "album",
  "to_object_id": "photo-uuid",
  "to_object_type": "media",
  "link_type": "contains",
  "sort_order": 0,
  "metadata": {}
}
```

**Validation Steps:**
1. Verify user is authenticated
2. Verify `from_object` and `to_object` exist
3. Verify both objects belong to authenticated user
4. Verify link type is valid
5. Verify link type allows this from/to combination
6. Check for duplicate link (same from, to, type)
7. Check cardinality constraints
8. If bidirectional link, create reverse link automatically
9. Insert link into database
10. Update denormalized counts (e.g., `album.media_count`)
11. Return created link(s)

**Response:**
```json
{
  "id": "link-uuid",
  "from_object_id": "album-uuid",
  "to_object_id": "photo-uuid",
  "link_type": "contains",
  "created_at": "2026-02-03T12:00:00Z",
  ...
}
```

---

### Reading Links

**Get Links From Object:**
```http
GET /api/v1/objects/{object_id}/links/outgoing?type=contains
```

**Get Links To Object:**
```http
GET /api/v1/objects/{object_id}/links/incoming?type=source
```

**Get All Links for Object:**
```http
GET /api/v1/objects/{object_id}/links
```

**Response:**
```json
{
  "links": [
    {
      "id": "link-1-uuid",
      "link_type": "contains",
      "from_object_id": "album-uuid",
      "to_object_id": "photo-1-uuid",
      "to_object": {
        "id": "photo-1-uuid",
        "type": "media",
        "filename": "photo1.jpg",
        ...
      }
    },
    {
      "id": "link-2-uuid",
      "link_type": "contains",
      "from_object_id": "album-uuid",
      "to_object_id": "photo-2-uuid",
      "to_object": {
        "id": "photo-2-uuid",
        "type": "media",
        "filename": "photo2.jpg",
        ...
      }
    }
  ],
  "total": 2
}
```

**Common Queries:**

1. **Get all photos in album (ordered):**
```http
GET /api/v1/albums/{album_id}/media
# → Returns media objects linked via "contains", sorted by sort_order
```

2. **Get source integration for photo:**
```http
GET /api/v1/media/{photo_id}/source
# → Returns integration object linked via "source"
```

3. **Get all duplicates of photo:**
```http
GET /api/v1/media/{photo_id}/duplicates
# → Returns media objects linked via "duplicate_of"
```

---

### Updating Links

Links can be updated to change properties like `sort_order`, `strength`, or `metadata`.

**API Endpoint:** `PATCH /api/v1/links/{link_id}`

**Request:**
```json
{
  "sort_order": 10,
  "strength": 1.0,
  "metadata": {
    "user_confirmed": true
  }
}
```

**Immutable Fields:**
- `from_object_id`, `to_object_id`, `link_type` cannot be changed
- To change endpoints or type, delete and recreate link

---

### Deleting Links

**API Endpoint:** `DELETE /api/v1/links/{link_id}`

**Behavior:**
- Soft delete by default (set `deleted_at`)
- If bidirectional, delete reverse link too
- Update denormalized counts
- Do NOT delete linked objects (only remove relationship)

**Example: Remove photo from album**
```http
DELETE /api/v1/links/{link_id}
# → Photo removed from album, but photo still exists
```

**Cascade Deletes:**

When an object is deleted, what happens to its links?

| Scenario | Behavior |
|----------|----------|
| **User deleted** | All user's objects and links deleted (CASCADE) |
| **Album deleted** | Links where album is `from_object` deleted (contains links) |
| **Media deleted** | All links to/from media deleted |
| **Integration deleted** | Links where integration is `to_object` deleted (source links preserved but orphaned) |

---

## Querying Links

### Graph Traversal

Links enable graph-like queries:

**1. Get all media in album and sub-albums (recursive):**
```sql
WITH RECURSIVE album_tree AS (
  -- Start with root album
  SELECT id FROM albums WHERE id = '{album_id}'

  UNION ALL

  -- Recursively find sub-albums
  SELECT l.to_object_id
  FROM links l
  JOIN album_tree at ON l.from_object_id = at.id
  WHERE l.link_type = 'contains'
    AND l.from_object_type = 'album'
    AND l.to_object_type = 'album'
    AND l.deleted_at IS NULL
)
-- Get all media in any of these albums
SELECT DISTINCT m.*
FROM media m
JOIN links l ON l.to_object_id = m.id
JOIN album_tree at ON l.from_object_id = at.id
WHERE l.link_type = 'contains'
  AND l.from_object_type = 'album'
  AND l.to_object_type = 'media'
  AND l.deleted_at IS NULL
ORDER BY l.sort_order;
```

**2. Get all media from a specific integration:**
```sql
SELECT m.*
FROM media m
JOIN links l ON l.from_object_id = m.id
WHERE l.link_type = 'source'
  AND l.to_object_id = '{integration_id}'
  AND l.deleted_at IS NULL;
```

**3. Find duplicate clusters (all duplicates of duplicates):**
```sql
WITH RECURSIVE duplicate_cluster AS (
  -- Start with specific photo
  SELECT to_object_id AS media_id
  FROM links
  WHERE from_object_id = '{photo_id}'
    AND link_type = 'duplicate_of'
    AND deleted_at IS NULL

  UNION

  -- Find duplicates of duplicates
  SELECT l.to_object_id
  FROM links l
  JOIN duplicate_cluster dc ON l.from_object_id = dc.media_id
  WHERE l.link_type = 'duplicate_of'
    AND l.deleted_at IS NULL
)
SELECT DISTINCT m.*
FROM media m
JOIN duplicate_cluster dc ON m.id = dc.media_id;
```

### Performance Considerations

**Indexes for Link Queries:**
```sql
-- Fast lookup: "Get all links from object X"
CREATE INDEX idx_links_from ON links(from_object_id, link_type)
  WHERE deleted_at IS NULL;

-- Fast lookup: "Get all links to object X"
CREATE INDEX idx_links_to ON links(to_object_id, link_type)
  WHERE deleted_at IS NULL;

-- Prevent duplicate links
CREATE UNIQUE INDEX idx_links_unique ON links(from_object_id, to_object_id, link_type)
  WHERE deleted_at IS NULL;

-- Ordered links (albums)
CREATE INDEX idx_links_ordered ON links(from_object_id, sort_order)
  WHERE deleted_at IS NULL AND sort_order IS NOT NULL;
```

**Query Optimization:**
- Use indexes on `from_object_id`, `to_object_id`, `link_type`
- Filter by `deleted_at IS NULL` in all queries
- Consider materializing common queries (e.g., album media counts)
- Limit recursive queries with depth limits

---

## Link Constraints

### Validation Rules

```python
LINK_TYPE_RULES = {
    "contains": {
        "allowed_combinations": [
            ("album", "media"),
            ("album", "album"),
        ],
        "bidirectional": False,
        "ordered": True,
        "unique_from": False,  # Album can contain many items
        "unique_to": False,    # Media can be in many albums
    },
    "source": {
        "allowed_combinations": [
            ("media", "integration"),
        ],
        "bidirectional": False,
        "ordered": False,
        "unique_from": True,   # Media can only have one source
        "unique_to": False,    # Integration can source many media
    },
    "duplicate_of": {
        "allowed_combinations": [
            ("media", "media"),
        ],
        "bidirectional": True,  # Auto-create reverse link
        "ordered": False,
        "unique_from": False,   # Media can have many duplicates
        "unique_to": False,     # Media can be duplicate of many
        "prevent_self_loop": True,  # Can't be duplicate of itself
    },
    "variant_of": {
        "allowed_combinations": [
            ("media", "media"),
        ],
        "bidirectional": False,
        "ordered": False,
        "unique_from": True,   # Variant can only have one original
        "unique_to": False,    # Original can have many variants
        "prevent_self_loop": True,
        "prevent_cycles": True,  # No circular variants
    },
}
```

### Cardinality Enforcement

**One-to-One:**
- `unique_from: True` and `unique_to: True`
- Example: (none in Phase 1)

**One-to-Many:**
- `unique_from: True` and `unique_to: False`
- Example: `variant_of` (variant has one original, original has many variants)

**Many-to-One:**
- `unique_from: False` and `unique_to: True`
- Example: (conceptually reverse of one-to-many)

**Many-to-Many:**
- `unique_from: False` and `unique_to: False`
- Example: `contains` (album → media), `duplicate_of`

### Circular Reference Prevention

For link types with `prevent_cycles: True`, check before creating:

```python
def would_create_cycle(from_id, to_id, link_type):
    """Check if creating link would create a cycle"""
    if from_id == to_id:
        return True  # Self-loop

    # Check if to_id is ancestor of from_id
    # (BFS or DFS traversal)
    visited = set()
    queue = [from_id]

    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)

        if current == to_id:
            return True  # Cycle detected

        # Get all objects that current points to via same link type
        parents = get_linked_objects(current, link_type, direction="outgoing")
        queue.extend(parents)

    return False
```

---

## Examples

### Example 1: Album with Photos

**Setup:**
```
User creates album "Vacation 2026"
User uploads 3 photos
User adds photos to album
```

**Objects:**
```json
// Album
{
  "id": "album-1",
  "type": "album",
  "name": "Vacation 2026",
  "media_count": 3
}

// Photos
{
  "id": "photo-1",
  "type": "media",
  "filename": "beach.jpg"
}
{
  "id": "photo-2",
  "type": "media",
  "filename": "sunset.jpg"
}
{
  "id": "photo-3",
  "type": "media",
  "filename": "dinner.jpg"
}
```

**Links:**
```json
// Link 1: Album contains photo-1
{
  "from_object_id": "album-1",
  "to_object_id": "photo-1",
  "link_type": "contains",
  "sort_order": 0
}

// Link 2: Album contains photo-2
{
  "from_object_id": "album-1",
  "to_object_id": "photo-2",
  "link_type": "contains",
  "sort_order": 1
}

// Link 3: Album contains photo-3
{
  "from_object_id": "album-1",
  "to_object_id": "photo-3",
  "link_type": "contains",
  "sort_order": 2
}
```

**Query: Get photos in album**
```http
GET /api/v1/albums/album-1/media

Response:
{
  "items": [
    {"id": "photo-1", "filename": "beach.jpg"},
    {"id": "photo-2", "filename": "sunset.jpg"},
    {"id": "photo-3", "filename": "dinner.jpg"}
  ],
  "total": 3
}
```

---

### Example 2: Instagram Sync

**Setup:**
```
User connects Instagram integration
System syncs 100 photos from Instagram
Each photo linked to integration via "source"
```

**Objects:**
```json
// Integration
{
  "id": "instagram-1",
  "type": "integration",
  "integration_type": "instagram",
  "integration_name": "@johnsmith",
  "items_synced": 100
}

// Media (one of 100)
{
  "id": "photo-ig-1",
  "type": "media",
  "filename": "instagram_post_2026_01_15.jpg",
  "source_type": "integration",
  "source_id": "instagram_media_abc123"
}
```

**Link:**
```json
{
  "from_object_id": "photo-ig-1",
  "to_object_id": "instagram-1",
  "link_type": "source",
  "metadata": {
    "external_id": "instagram_media_abc123",
    "sync_timestamp": "2026-02-03T10:00:00Z"
  }
}
```

**Query: Get all Instagram photos**
```http
GET /api/v1/integrations/instagram-1/media

Response:
{
  "items": [
    {"id": "photo-ig-1", ...},
    {"id": "photo-ig-2", ...},
    ...
  ],
  "total": 100
}
```

**Deduplication on Re-Sync:**
```python
# Before importing from Instagram
existing_link = find_link(
    from_object_type="media",
    to_object_id=integration_id,
    metadata__external_id=instagram_media_id
)

if existing_link:
    # Already imported, skip or update
    pass
else:
    # New photo, import and create link
    create_media_and_link(instagram_data, integration_id)
```

---

### Example 3: Duplicate Detection

**Setup:**
```
User uploads same photo twice (different filenames)
System detects duplicates via hash match
System creates bidirectional "duplicate_of" links
```

**Objects:**
```json
{
  "id": "photo-original",
  "filename": "IMG_1234.jpg",
  "hash": "abc123..."
}
{
  "id": "photo-duplicate",
  "filename": "IMG_1234_copy.jpg",
  "hash": "abc123..."  // Same hash!
}
```

**Links (bidirectional):**
```json
// Link 1: photo-original → photo-duplicate
{
  "id": "link-1",
  "from_object_id": "photo-original",
  "to_object_id": "photo-duplicate",
  "link_type": "duplicate_of",
  "strength": 1.0,
  "is_bidirectional": true,
  "metadata": {
    "detection_method": "hash_match",
    "hash_match": true
  }
}

// Link 2: photo-duplicate → photo-original (auto-created)
{
  "id": "link-2",
  "from_object_id": "photo-duplicate",
  "to_object_id": "photo-original",
  "link_type": "duplicate_of",
  "strength": 1.0,
  "is_bidirectional": true,
  "metadata": {
    "detection_method": "hash_match",
    "hash_match": true,
    "reverse_of": "link-1"
  }
}
```

**Query: Get duplicates**
```http
GET /api/v1/media/photo-original/duplicates

Response:
{
  "items": [
    {"id": "photo-duplicate", "filename": "IMG_1234_copy.jpg"}
  ],
  "total": 1
}
```

**User Action: Confirm or Reject**
```http
PATCH /api/v1/links/link-1
{
  "strength": 1.0,  // User confirmed
  "metadata": {
    "user_confirmed": true,
    "confirmed_at": "2026-02-03T14:00:00Z"
  }
}
```

---

## Open Questions

1. **Link Versioning?**
   - Track history of link changes?
   - Useful for undo/redo?

2. **Link Properties vs. Metadata?**
   - Should some common metadata be promoted to core fields?
   - E.g., `confidence` instead of `strength`?

3. **Performance at Scale?**
   - How well do link queries perform with millions of links?
   - Need caching or materialized views?

4. **Graph Database?**
   - Would a dedicated graph DB (Neo4j, ArangoDB) be better?
   - Or is PostgreSQL + indexes sufficient?

---

## Next Steps

- [ ] Review link model design
- [ ] Implement link validation logic
- [ ] Create database schema for links
- [ ] Write API endpoints for link CRUD
- [ ] Implement graph traversal queries
- [ ] Add link-based features (album media listing, duplicate detection)

---

**Status:** Draft - Ready for review
**Next Document:** `03-API-Endpoints.md` (RESTful API specification)
