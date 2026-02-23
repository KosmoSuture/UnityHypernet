---
ha: "0.5"
object_type: "0.5.3.1"
creator: "2.1.adversary"
created: "2026-02-22T00:00:00Z"
position_2d: null
position_3d: null
flags: ["0.8.4.1"]
---
# Collections in the Hypernet — Canonical Pattern

**Author:** The Adversary (Audit Swarm Node 4)
**Date:** 2026-02-22
**Companion to:** TAXONOMY-PROPOSAL.md, CLASSIFICATION-DECISION-TREE.md
**Purpose:** Define how to represent ordered and unordered collections of objects
**Status:** PROPOSAL

---

## The Problem

Many real-world things are collections of other things:
- A **playlist** is an ordered list of songs/videos
- A **photo album** is a collection of images
- A **bibliography** is a collection of documents
- A **reading list** is a curated collection of books/articles
- A **portfolio** is a collection of creative works
- A **software bundle** is a collection of packages
- A **course curriculum** is an ordered sequence of lessons
- A **recipe book** is a collection of recipes
- A **thread** is an ordered sequence of messages

The 0.5 taxonomy defines 16 categories of objects but no explicit "Collection" type. This is deliberate — a collection is not a *kind* of thing, it's a *relationship pattern* between things. A playlist of songs is fundamentally different from a portfolio of designs, even though both are "collections."

---

## The Pattern: Parent Object + `contains` Links

### Principle

A collection is represented as:
1. A **parent object** whose type reflects what the collection IS (not what it contains)
2. A set of **`contains` links** from the parent to each member
3. **Ordering** (when needed) via a `position` field on the link metadata

### Why This Works

- The parent object carries the collection's metadata (title, creator, description, visibility)
- The links carry the membership relationship and ordering
- Members retain their own types — a song in a playlist is still `0.5.4.3 Audio`
- The same object can be in multiple collections via multiple links
- No new type system needed — it uses the existing 0.5 types + 0.6 links

---

## Implementation

### Schema for the Parent Object

The parent object uses whatever 0.5.x type best describes it. Common mappings:

| Collection | Parent Object Type | Why |
|---|---|---|
| Playlist | 0.5.15.3.3 Album/Collection (Creative Work) | It's a curated creative selection |
| Photo album | 0.5.4 Media (with flag `collection`) | It's a media container |
| Bibliography | 0.5.3.8 Reference | It's a reference document |
| Reading list | 0.5.3.6 Note (or 0.5.9.1 Task if it's a to-do) | It's a personal curation |
| Software bundle | 0.5.10.2.5 Library/Package | It's a software distribution unit |
| Course curriculum | 0.5.3.4 Specification | It's a structured plan |
| Recipe book | 0.5.3.7.1 Book (Document > Publication) | It's a publication |
| Message thread | 0.5.14.2 Conversation | It's a conversation container |

If no existing type fits, use `0.5.0.1 Generic Object` with a descriptive `flags` entry.

### Schema for the `contains` Link

```yaml
link:
  link_type: "contains"
  source: "[HA of collection parent]"
  target: "[HA of member object]"
  metadata:
    position: 1              # Ordinal position (1-based). Omit for unordered collections.
    added_at: "2026-02-22T10:00:00Z"
    added_by: "[HA of who added it]"
    role: null               # Optional: "primary", "alternate", "bonus", etc.
    notes: null              # Optional: curator's note about why this item is included
```

### Example: A Playlist

**Parent object:**
```yaml
ha: "6.1.2.001"
object_type: "0.5.15.3.3"      # Album/Collection (Creative Work)
creator: "1.1"                   # Matt
created: "2026-02-22T10:00:00Z"
flags: ["playlist"]

content:
  title: "Focus Music"
  description: "Instrumental tracks for deep work"
  track_count: 3
  total_duration_seconds: 7200
```

**Links (ordered):**
```yaml
links:
  - link_type: "contains"
    target: "6.4.3.042"         # An audio file
    metadata:
      position: 1
      added_at: "2026-02-22T10:00:00Z"

  - link_type: "contains"
    target: "6.4.3.108"         # Another audio file
    metadata:
      position: 2
      added_at: "2026-02-22T10:01:00Z"

  - link_type: "contains"
    target: "6.4.3.215"         # Another audio file
    metadata:
      position: 3
      added_at: "2026-02-22T10:02:00Z"
```

### Example: A Photo Album (Unordered)

**Parent object:**
```yaml
ha: "6.1.1.005"
object_type: "0.5.4"            # Media (general)
creator: "1.1"
created: "2026-02-22T10:00:00Z"
flags: ["collection", "album"]

content:
  title: "Hypernet Development Photos"
  description: "Photos from the development process"
  item_count: 47
```

**Links (unordered — no position field):**
```yaml
links:
  - link_type: "contains"
    target: "6.4.1.001"         # An image
    metadata:
      added_at: "2026-02-10T08:30:00Z"
      notes: "First whiteboard diagram"

  - link_type: "contains"
    target: "6.4.1.002"         # Another image
    metadata:
      added_at: "2026-02-10T09:15:00Z"
```

---

## Querying Collections

### Find all items in a collection
```
links WHERE source = [collection HA] AND link_type = "contains"
ORDER BY metadata.position ASC
```

### Find all collections an item belongs to
```
links WHERE target = [item HA] AND link_type = "contains"
```

### Count items in a collection
```
COUNT(links WHERE source = [collection HA] AND link_type = "contains")
```

---

## Operations

### Add item to collection
1. Create a `contains` link from collection to item
2. Set `position` to `max(existing positions) + 1` (for ordered collections)
3. Update collection's `item_count` / `track_count` / etc.

### Remove item from collection
1. Delete the `contains` link
2. Reorder remaining positions if needed (or leave gaps — sparse ordering is fine)
3. Update collection metadata

### Reorder items
1. Update `position` metadata on the relevant links
2. No changes to the items themselves

### Nest collections
A collection can contain another collection — just add a `contains` link to the nested collection's parent object. This supports arbitrary nesting (playlists of playlists, albums within albums, course modules within a course).

---

## What This Pattern Does NOT Support

- **Set operations** (union, intersection, difference of collections): These are query-time operations, not stored objects. Build them in application code.
- **Typed membership constraints** (e.g., "this collection only accepts Audio objects"): Not enforced at the schema level. Application-level validation can check `object_type` of linked targets.
- **Smart/dynamic collections** (e.g., "all photos from 2026"): These are saved queries, not static collections. A future `0.5.10.4 Dataset` or `0.5.3.3 Structured Data` type could hold the query definition.

---

## Relationship to Other Patterns

- **Conversations** (0.5.14.2): A conversation is a special case of an ordered collection of messages. The Communication type handles this directly.
- **Hierarchies** (parent-child folders): Already handled by the addressing system. `3.1.2` is a "child" of `3.1` by address structure.
- **Tags/Categories** (0.5.8.1): A tag applied to multiple objects creates an implicit collection. Query by flag to materialize it.

---

*Collections are relationships, not types. The Hypernet's link system is powerful enough to represent any collection without schema changes. This pattern should be the documented standard for all collection use cases.*
