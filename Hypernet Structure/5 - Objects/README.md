---
ha: "5"
object_type: "document"
creator: "1.1"
created: "2026-02-06"
status: "active"
visibility: "public"
flags: []
---

# 5 - Objects

**Status:** Foundational Structure - Ready for Implementation
**Purpose:** Storage and management of instantiated objects across all Hypernet types
**Authority:** All concrete instances of types defined in 0.0 - Object Type Registry

---

## What This Is

**Objects are where definitions become reality.**

The Objects node (5) stores actual instances of the types defined in the Object Type Registry (0.0). While 0.0 defines WHAT can exist, 5 stores WHAT DOES exist.

**Think of it this way:**
- **0.0** is the blueprint library (definitions)
- **5** is the constructed buildings (instances)

---

## Core Concept

### Definition vs. Instance

**Definition (0.0 - Object Type Registry):**
```yaml
Type: Photo
Fields:
  - filename: String
  - width: Integer
  - height: Integer
  - created_at: DateTime
```

**Instance (5 - Objects):**
```yaml
Object ID: 550e8400-e29b-41d4-a716-446655440000
Type: Photo
Data:
  filename: "vacation.jpg"
  width: 1920
  height: 1080
  created_at: "2026-02-01T14:30:00Z"
```

**Key Distinction:**
- 0.0 defines the schema
- 5 stores the actual data

---

## Relationship to 0.0 Object Type Registry

### The Tight Coupling

**Every object in 5.* MUST have a corresponding type in 0.0.**

```
0.0 - Object Type Registry (THE LIBRARY)
  ├── Defines: Photo type
  ↓
5 - Objects
  ├── Stores: photo1.jpg (instance)
  ├── Stores: photo2.jpg (instance)
  └── Stores: photo3.jpg (instance)
```

**Rule:** You cannot create an object in 5.* unless its type exists in 0.0 first.

### Type Categories Map to Object Storage

```
0.0.1 - Core Types          → 5.1 - Core Objects
0.0.2 - Media Types         → 5.2 - Media Objects
0.0.3 - Social Types        → 5.3 - Social Objects
0.0.4 - Communication Types → 5.4 - Communication Objects
0.0.5 - Financial Types     → 5.5 - Financial Objects
0.0.6 - Medical Types       → 5.6 - Medical Objects
0.0.7 - Web Types           → 5.7 - Web Objects
0.0.8 - Life Types          → 5.8 - Life Objects
0.0.9 - AI Types            → 5.9 - AI Objects
```

---

## Structure

### Top-Level Organization

```
5 - Objects/
├── 5.0 - Object System Definitions
│   └── Storage patterns, governance, lifecycle management
│
├── 5.1 - Core Objects
│   ├── User instances
│   ├── Link instances
│   └── Integration instances
│
├── 5.2 - Media Objects
│   ├── Photos
│   ├── Videos
│   ├── Audio files
│   └── Documents
│
├── 5.3 - Social Objects
│   ├── Social posts
│   ├── Social accounts
│   └── Social messages
│
├── 5.4 - Communication Objects
│   ├── Emails
│   ├── SMS messages
│   └── Chat messages
│
├── 5.5 - Financial Objects
│   ├── Transactions
│   ├── Accounts
│   └── Receipts
│
├── 5.6 - Medical Objects
│   ├── Medical records
│   ├── Prescriptions
│   └── Lab results
│
├── 5.7 - Web Objects
│   ├── Bookmarks
│   ├── Web pages
│   └── RSS items
│
├── 5.8 - Life Objects
│   ├── Calendar events
│   ├── Tasks
│   └── Notes
│
└── 5.9 - AI Objects
    ├── AI personalities
    ├── AI memories
    └── AI contributions
```

---

## 5.0 - Object System Definitions

### Purpose

Defines how objects are created, stored, updated, and deleted across Hypernet.

### Contents

**5.0.0 - Storage Patterns**
- File system storage (media files)
- Database storage (metadata)
- Hybrid storage (large files + metadata)
- Partitioning strategies (by user, date, type)

**5.0.1 - Object Lifecycle**
- Creation (instantiation from type)
- Reading (retrieval and access)
- Updating (modification and versioning)
- Deletion (soft delete, hard delete, archiving)

**5.0.2 - Access Control**
- Ownership (who owns object)
- Permissions (who can access)
- Sharing (temporary access grants)
- Privacy settings

**5.0.3 - Object Governance**
- Validation rules (enforce type schema)
- Quota limits (per user, per type)
- Retention policies (how long to keep)
- Cleanup procedures (removing orphaned objects)

---

## How Objects Are Instantiated

### Creation Flow

```
1. Type defined in 0.0
   ↓
2. API endpoint created in 0.2
   ↓
3. User calls API with data
   ↓
4. System validates against type schema (0.0)
   ↓
5. Object created in database
   ↓
6. File stored (if applicable)
   ↓
7. Metadata saved
   ↓
8. Object ID returned
   ↓
9. Object accessible via 5.X path
```

### Example: Creating a Photo Object

**Step 1: Type exists in 0.0**
```yaml
Type: Photo (hypernet.media.photo)
Version: 1.0
```

**Step 2: User uploads photo via API**
```bash
POST /api/v1/media/upload
Content-Type: multipart/form-data

file: vacation.jpg
metadata: {"tags": ["beach", "sunset"]}
```

**Step 3: System creates object**
```yaml
Object ID: photo-550e8400-e29b-41d4-a716-446655440000
Type: hypernet.media.photo
User ID: user-123
Filename: vacation.jpg
File Path: /media/user-123/photos/2026/02/vacation.jpg
Width: 1920
Height: 1080
File Size: 2048576
MIME Type: image/jpeg
Created At: 2026-02-06T10:30:00Z
Metadata:
  tags: ["beach", "sunset"]
  exif: {...}
```

**Step 4: Object stored in 5.2 - Media Objects**
```
5.2 - Media Objects/
  └── 5.2.1 - Photos/
      └── 5.2.1-550e8400/ (object folder)
          ├── metadata.json (structured data)
          ├── vacation.jpg (actual file)
          └── README.md (human-readable info)
```

---

## Storage Patterns

### Pattern 1: Database Only (Small Objects)

**Used for:** Tasks, notes, calendar events, links

**Storage:**
- All data in PostgreSQL
- No separate files
- Fast queries and updates

**Example:**
```sql
-- Task object stored entirely in database
INSERT INTO tasks (id, user_id, title, description, status, due_date)
VALUES (
  'task-123',
  'user-456',
  'Review API docs',
  'Complete review of all API documentation',
  'pending',
  '2026-02-10'
);
```

### Pattern 2: File + Metadata (Large Objects)

**Used for:** Photos, videos, audio, documents

**Storage:**
- File stored on disk (or cloud storage)
- Metadata in PostgreSQL
- File path in database

**Example:**
```sql
-- Photo metadata in database
INSERT INTO media (id, user_id, filename, file_path, width, height)
VALUES (
  'photo-550e8400',
  'user-123',
  'vacation.jpg',
  '/media/user-123/photos/2026/02/vacation.jpg',
  1920,
  1080
);

-- Actual file stored at:
-- /media/user-123/photos/2026/02/vacation.jpg
```

### Pattern 3: Hybrid (Complex Objects)

**Used for:** Web archives, email with attachments, documents with embedded media

**Storage:**
- Primary data in database
- Related files on disk
- Relationships maintained

**Example:**
```sql
-- Email in database
INSERT INTO emails (id, user_id, subject, body, received_at)
VALUES (...);

-- Attachments as separate objects
INSERT INTO media (id, user_id, parent_id, filename, file_path)
VALUES (...);

-- Link between email and attachments
INSERT INTO links (source_id, target_id, link_type)
VALUES ('email-123', 'attachment-456', 'has_attachment');
```

---

## Object Naming and Organization

### Object ID Format

**UUID-based:**
```
[type-prefix]-[uuid]

Examples:
photo-550e8400-e29b-41d4-a716-446655440000
email-7c9e6679-7425-40de-944b-e07fc1f90ae7
task-8f7b9a2d-3e5c-4b8a-9d1f-6a4e8c9d2f1b
```

**Benefits:**
- Globally unique (no collisions)
- Type identifiable (prefix)
- URL-safe
- Sortable

### File Organization

**By User:**
```
5.2 - Media Objects/
  └── 5.2.1 - Photos/
      ├── user-123/
      │   ├── 2026/
      │   │   ├── 01/
      │   │   ├── 02/
      │   │   └── ...
      │   └── 2025/
      └── user-456/
```

**By Type:**
```
5 - Objects/
  ├── 5.2 - Media Objects/
  │   ├── 5.2.1 - Photos/
  │   ├── 5.2.2 - Videos/
  │   └── 5.2.3 - Audio/
  └── 5.8 - Life Objects/
      ├── 5.8.1 - Tasks/
      └── 5.8.2 - Notes/
```

**By Date (within type):**
```
5.2.1 - Photos/
  └── user-123/
      ├── 2026/
      │   ├── 01/  (January 2026)
      │   ├── 02/  (February 2026)
      │   └── ...
      └── 2025/
          └── ...
```

---

## Object Lifecycle Management

### Creation

**Process:**
1. Validate against type schema (0.0)
2. Assign unique object ID
3. Set ownership (user_id)
4. Store data (database + files)
5. Create initial metadata
6. Return object ID to creator

**Validation:**
- Required fields present
- Field types correct
- Constraints satisfied
- File size within limits
- User has quota available

### Reading

**Access Patterns:**
```
GET /api/v1/objects/{object_id}
→ Returns single object

GET /api/v1/objects?type=photo&user_id=123
→ Returns list of objects (filtered)

GET /api/v1/objects?date_from=2026-01-01&date_to=2026-02-01
→ Returns objects in date range
```

**Performance:**
- Index by user_id, type, created_at
- Cache frequently accessed objects
- Lazy-load large files
- Pagination for lists

### Updating

**Update Types:**
1. **Metadata Update** - Change title, tags, description
2. **File Replacement** - Upload new version
3. **Relationship Change** - Add/remove links
4. **Status Change** - Mark as favorite, archive, etc.

**Versioning:**
- Track update history
- Store previous versions (optional)
- Record who changed what and when
- Enable undo/rollback

### Deletion

**Soft Delete (Default):**
```sql
UPDATE objects
SET deleted_at = NOW(), status = 'deleted'
WHERE id = 'object-123';
```

**Benefits:**
- Recoverable (undo delete)
- Maintains referential integrity
- Audit trail preserved

**Hard Delete (Rare):**
```sql
DELETE FROM objects WHERE id = 'object-123';
-- Also delete associated files
```

**Used for:**
- User account deletion (GDPR)
- Cleanup of orphaned objects
- Security incidents (remove data immediately)

---

## Object Relationships (Links)

### Link Object Type

Links are first-class objects that connect other objects.

**Defined in:** 0.0.1 - Core Types / Link

**Structure:**
```yaml
Link ID: link-123
Source Object: photo-550e8400
Target Object: album-789
Link Type: "contained_in"
Created At: 2026-02-06T10:30:00Z
Metadata:
  order: 5 (position in album)
```

### Common Link Types

**Containment:**
- Photo → Album ("contained_in")
- Email → Folder ("stored_in")
- Task → Project ("part_of")

**Source/Origin:**
- Photo → Instagram ("sourced_from")
- Email → EmailAccount ("received_via")
- Post → SocialAccount ("posted_by")

**Relationships:**
- Photo → Photo ("duplicate_of")
- Person → Person ("related_to")
- Document → Document ("references")

**Hierarchy:**
- Task → Task ("subtask_of")
- Folder → Folder ("parent_of")
- Category → Category ("child_of")

---

## Access Control

### Ownership

**Every object has an owner:**
```yaml
Object ID: photo-550e8400
User ID: user-123  # Owner
```

**Owner rights:**
- Read, update, delete
- Grant access to others
- Change privacy settings

### Permissions

**Levels:**
1. **Private** - Owner only
2. **Shared** - Owner + specific users
3. **Team** - Owner + organization members
4. **Public** - Anyone with link

**Implementation:**
```sql
CREATE TABLE object_permissions (
  object_id UUID,
  user_id UUID,
  permission ENUM('read', 'write', 'admin'),
  granted_at TIMESTAMP
);
```

### Privacy Settings

**Per-Object Privacy:**
```yaml
Object: photo-550e8400
Privacy: private
Shared With:
  - user-456 (read)
  - user-789 (write)
```

**Per-Type Privacy:**
```yaml
User: user-123
Default Photo Privacy: private
Default Note Privacy: team
Default Task Privacy: public
```

---

## Object Metadata

### Core Metadata (All Objects)

```yaml
id: UUID
user_id: UUID (owner)
object_type: String (e.g., "hypernet.media.photo")
created_at: DateTime
updated_at: DateTime
deleted_at: DateTime (nullable)
status: Enum ['active', 'archived', 'deleted']
```

### Type-Specific Metadata

**Photos:**
```yaml
width: Integer
height: Integer
file_size: Integer
mime_type: String
exif: JSON (camera settings, GPS, etc.)
```

**Tasks:**
```yaml
title: String
description: Text
status: Enum ['pending', 'in_progress', 'completed']
due_date: DateTime
priority: Enum ['low', 'medium', 'high']
```

### Custom Metadata (Extensible)

```yaml
metadata: JSON
{
  "tags": ["beach", "sunset"],
  "rating": 5,
  "custom_field": "custom_value"
}
```

---

## Use Cases

### 1. Media Library

**Scenario:** Store and organize all photos, videos, documents

**Implementation:**
- Photos in 5.2.1
- Videos in 5.2.2
- Documents in 5.2.4
- Albums link photos together
- Tags and search for discovery

### 2. Email Archive

**Scenario:** Import and store all email history

**Implementation:**
- Emails in 5.4.1
- Attachments in 5.2.4 (linked to emails)
- Folders organize emails
- Full-text search enabled
- Relationships to contacts (1.*)

### 3. Task Management

**Scenario:** Track tasks and projects

**Implementation:**
- Tasks in 5.8.1
- Projects in 5.8.1 (special task type)
- Subtasks linked to parent tasks
- Calendar events in 5.8.3
- Integration with notifications

### 4. Social Media Archive

**Scenario:** Backup all social media posts

**Implementation:**
- Posts in 5.3.1
- Photos/videos in 5.2.* (linked)
- Comments in 5.3.4 (linked to posts)
- Accounts in 5.3.2
- Relationships between posts

### 5. Knowledge Base

**Scenario:** Build personal wiki

**Implementation:**
- Notes in 5.8.2
- Articles in 5.8.2 (long-form)
- Links between notes
- Tags for categorization
- Full-text search across all notes

---

## Integration with Hypernet Platform

### Object Creation

**Via API:**
```bash
POST /api/v1/objects
Content-Type: application/json

{
  "type": "hypernet.media.photo",
  "file": "base64_encoded_image",
  "metadata": {
    "tags": ["vacation", "2026"]
  }
}
```

**Via Integrations:**
```
Google Photos Integration
  ↓
Syncs photos to Hypernet
  ↓
Creates Photo objects in 5.2.1
  ↓
Links to Integration object
```

### Object Retrieval

**API Endpoints:**
```
GET /api/v1/objects/{id}
GET /api/v1/objects?type={type}
GET /api/v1/objects?user_id={user_id}
GET /api/v1/objects?query={search_term}
```

**Search:**
- Full-text search across metadata
- Filter by type, date, tags
- Sort by relevance, date, name
- Pagination for large result sets

---

## Quota and Limits

### Per-User Quotas

**Storage Limits:**
- Free Tier: 5 GB
- Pro Tier: 100 GB
- Enterprise: Unlimited

**Object Count Limits:**
- Free Tier: 10,000 objects
- Pro Tier: 1,000,000 objects
- Enterprise: Unlimited

**Rate Limits:**
- API calls: 1,000/hour
- Uploads: 100/hour
- Bulk operations: 10/hour

### Enforcement

**Pre-Check:**
```python
def can_create_object(user_id, file_size):
    current_usage = get_user_storage(user_id)
    quota = get_user_quota(user_id)

    if current_usage + file_size > quota:
        raise QuotaExceededError()

    return True
```

**Monitoring:**
- Track usage per user
- Alert when approaching limits
- Offer upgrade options

---

## Cleanup and Maintenance

### Orphaned Objects

**Definition:** Objects with no owner or invalid references

**Detection:**
```sql
-- Find objects with deleted owners
SELECT id FROM objects
WHERE user_id NOT IN (SELECT id FROM users);

-- Find objects with no links and old deleted_at
SELECT id FROM objects
WHERE deleted_at < NOW() - INTERVAL '90 days'
AND id NOT IN (SELECT source_id FROM links)
AND id NOT IN (SELECT target_id FROM links);
```

**Cleanup:**
- Weekly job to identify orphans
- Grace period (90 days)
- Hard delete after grace period

### Retention Policies

**Default:**
- Active objects: Kept indefinitely
- Deleted objects: 90 days retention
- Archived objects: 1 year then delete

**Configurable per user:**
```yaml
User: user-123
Retention:
  deleted_photos: 30 days
  deleted_emails: 365 days
  archived_tasks: 90 days
```

---

## Implementation Status

### Phase 1: Foundation (Current)
- [x] Folder structure created
- [x] README documentation
- [x] Storage patterns defined
- [x] Lifecycle documented

### Phase 2: Core Objects (Next)
- [ ] User objects (authentication)
- [ ] Link objects (relationships)
- [ ] Integration objects (connections)
- [ ] Basic CRUD API

### Phase 3: Media Objects (Month 2)
- [ ] Photo storage and retrieval
- [ ] Video storage
- [ ] Document storage
- [ ] Media upload API

### Phase 4: Additional Types (Month 3-6)
- [ ] Social objects
- [ ] Communication objects
- [ ] Life objects (tasks, notes, calendar)
- [ ] Complete API coverage

---

## Next Steps

### Immediate (This Week)
1. Define object storage schema in database
2. Implement object CRUD API endpoints
3. Build file upload/download system
4. Create first object type (Photo)

### Short Term (This Month)
1. Add object search and filtering
2. Implement soft delete
3. Build quota enforcement
4. Add object metadata support

### Long Term (This Quarter)
1. Complete all object types from 0.0
2. Implement object versioning
3. Build relationship (link) system
4. Add advanced search features

---

## Best Practices

### DO:
- Validate all objects against type schema
- Store large files separately from metadata
- Use soft delete by default
- Index frequently queried fields
- Implement pagination for large lists

### DON'T:
- Store objects without type definition
- Duplicate objects (use links instead)
- Hard delete unless absolutely necessary
- Store sensitive data unencrypted
- Allow unlimited object creation

---

## Meta-Note

Objects are the lifeblood of Hypernet. They represent your actual data - your photos, emails, notes, tasks, everything. The Object Registry (0.0) defines what CAN exist. Objects (5) stores what DOES exist. Together, they create a flexible, extensible, and maintainable data platform.

**Remember: Every object is an instance of a type. No type, no object.**

---

**Status:** Structure Defined - Ready for Implementation
**Priority:** Critical (core data storage layer)
**Owner:** Hypernet Core Team
**Created:** 2026-02-06
**Last Updated:** 2026-02-06
