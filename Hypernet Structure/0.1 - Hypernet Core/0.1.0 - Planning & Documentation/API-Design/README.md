# API Design Documentation

## Overview

This directory contains the complete API design specification for Hypernet Core 0.1, including object models, link semantics, and RESTful endpoint definitions.

---

## Documents

### 1. Object Model Specification (27KB)
**File:** `01-Object-Model-Specification.md`

Defines all object types, their fields, validation rules, and lifecycle.

**Object Types:**
- **User** - Account and authentication
- **Media** - Photos, videos, files
- **Album** - Collections of media
- **Integration** - Connected external services
- **Link** - Relationships between objects

**Key Decisions:**
- ✅ Hybrid schema (core fields + JSON metadata)
- ✅ Immutable UUIDs for all objects
- ✅ Soft deletes by default
- ✅ Source tracking for all objects
- ✅ Audit timestamps (created_at, updated_at, deleted_at)

### 2. Link Model Specification (22KB)
**File:** `02-Link-Model-Specification.md`

Defines how relationships work as first-class objects.

**Link Types (Phase 1):**
- `contains` - Album → Media, Album → Album
- `source` - Media → Integration
- `duplicate_of` - Media ↔ Media
- `variant_of` - Media → Media (thumbnails, edits)

**Key Features:**
- ✅ First-class link objects (not just foreign keys)
- ✅ Directional with bidirectional support
- ✅ Strength/confidence scores (0.0 to 1.0)
- ✅ Ordered relationships (sort_order)
- ✅ Rich metadata on relationships

### 3. API Endpoints (28KB)
**File:** `03-API-Endpoints.md`

Complete RESTful API specification with all endpoints.

**Endpoint Groups:**
- **Auth** - Register, login, refresh, logout
- **Users** - Profile management
- **Media** - Upload, list, get, download, thumbnail, update, delete
- **Albums** - Create, list, get, update, delete, add/remove media
- **Integrations** - Connect, sync, disconnect
- **Links** - Create, list, update, delete
- **System** - Health, version, metrics

**Total Endpoints:** ~30 endpoints across 7 resource types

---

## API Design Principles

1. **RESTful** - Resources, HTTP methods, standard status codes
2. **Versioned** - `/api/v1/...` allows future evolution
3. **JSON** - All request/response bodies (except file uploads)
4. **Stateless** - JWT tokens, no server sessions
5. **Paginated** - Offset and cursor pagination
6. **Filterable & Sortable** - Query parameters for filtering/sorting
7. **Secure** - Input validation, authentication, authorization, rate limiting

---

## Key Architectural Decisions

### Hybrid Object Model

**Problem:** How to balance structure and flexibility?

**Solution:** Core fields + JSON metadata
- Common fields (id, user_id, created_at) are strongly typed
- Integration-specific data in flexible `metadata` JSONB column
- Best of both: performant queries + extensibility

### First-Class Links

**Problem:** How to represent relationships?

**Solution:** Links as objects (not just foreign keys)
- Media can be in multiple albums (many-to-many)
- Rich metadata on relationships (when added, why, confidence)
- Enables graph queries and complex relationships

### Source Tracking

**Problem:** How to prevent duplicate imports?

**Solution:** Every object tracks its source
- `source_type` and `source_id` fields
- Links connect media to integrations
- Deduplication by checking existing source links

### Soft Deletes

**Problem:** How to handle accidental deletions?

**Solution:** Soft delete by default
- Set `deleted_at` timestamp instead of removing
- Can be restored by admin
- Permanently deleted after retention period (30 days)

---

## Object Relationships

```
User
 ├── owns → Media (1:N)
 ├── owns → Album (1:N)
 ├── owns → Integration (1:N)
 └── owns → Link (1:N)

Album
 ├── contains → Media (via Link, M:N)
 ├── contains → Album (via Link, nested)
 └── has cover → Media (foreign key)

Media
 ├── in → Album (via Link, M:N)
 ├── sourced from → Integration (via Link)
 ├── duplicate of → Media (via Link, bidirectional)
 └── variant of → Media (via Link, thumbnails/edits)

Integration
 └── sourced → Media (via Link, 1:N)
```

---

## Data Flow Examples

### Upload Photo
```
1. POST /api/v1/media/upload (multipart)
2. Validate file, scan malware
3. Generate UUID, extract EXIF
4. Save to /media/{user_id}/media/{year}/{month}/{id}.jpg
5. Generate thumbnails (async)
6. Insert Media object to database
7. Return Media object JSON
```

### Add Photo to Album
```
1. POST /api/v1/albums/{album_id}/media
2. Validate album and media exist, user owns both
3. Create Link object (album → media, type "contains")
4. Update album.media_count (denormalized)
5. Return Link object
```

### Sync from Instagram
```
1. POST /api/v1/integrations/{id}/sync
2. Fetch items from Instagram API (paginated)
3. For each item:
   a. Check if Link exists (media → integration, source_id)
   b. If exists, skip (already imported)
   c. If new, download media, create Media object
   d. Create Link (media → integration, type "source")
4. Update integration sync state (cursor, last_sync_at)
5. Return sync status
```

---

## API Authentication Flow

### Registration
```
POST /api/v1/auth/register
  {email, password, display_name}
→ Create User object
→ Return {user, access_token, refresh_token}
```

### Login
```
POST /api/v1/auth/login
  {email, password}
→ Verify password
→ Generate access_token (15min) + refresh_token (30days)
→ Return {user, access_token, refresh_token}
```

### API Request
```
GET /api/v1/media
  Authorization: Bearer {access_token}
→ Verify JWT signature
→ Extract user_id from token
→ Query media WHERE user_id = {user_id} AND deleted_at IS NULL
→ Return {items, total, pagination}
```

### Token Refresh
```
POST /api/v1/auth/refresh
  {refresh_token}
→ Verify refresh_token
→ Generate new access_token
→ Return {access_token}
```

---

## Validation & Security

### Input Validation

All inputs validated using Pydantic models:

```python
class MediaUploadRequest(BaseModel):
    file: UploadFile
    description: str | None = None
    tags: list[str] = []

    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 50:
            raise ValueError('Max 50 tags')
        return v
```

### Authorization

Every endpoint checks:
1. **Authentication:** Valid JWT token?
2. **Ownership:** Does user own this resource?
3. **Permission:** Does user have required permission?

```python
async def get_media(media_id: UUID, user: User = Depends(get_current_user)):
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(404, "Not found")
    if media.user_id != user.id and not user.is_admin:
        raise HTTPException(403, "Forbidden")
    return media
```

### Rate Limiting

Per-user rate limits enforced via Redis:

```python
RATE_LIMITS = {
    "/api/v1/media/upload": "10/minute",  # Max 10 uploads per minute
    "/api/v1/auth/login": "5/minute",     # Max 5 login attempts
    "/api/v1/*": "1000/hour",             # Global limit
}
```

---

## Database Schema Preview

**Users Table:**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    ...
);
```

**Media Table:**
```sql
CREATE TABLE media (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    media_type VARCHAR(50) NOT NULL,
    file_path VARCHAR(1024) NOT NULL,
    hash VARCHAR(64) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    ...
);

CREATE INDEX idx_media_user ON media(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_media_hash ON media(hash);
```

**Links Table:**
```sql
CREATE TABLE links (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    from_object_id UUID NOT NULL,
    from_object_type VARCHAR(50) NOT NULL,
    to_object_id UUID NOT NULL,
    to_object_type VARCHAR(50) NOT NULL,
    link_type VARCHAR(50) NOT NULL,
    strength FLOAT DEFAULT 1.0,
    sort_order INTEGER,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE,
    ...
);

CREATE INDEX idx_links_from ON links(from_object_id, link_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_links_to ON links(to_object_id, link_type) WHERE deleted_at IS NULL;
CREATE UNIQUE INDEX idx_links_unique ON links(from_object_id, to_object_id, link_type) WHERE deleted_at IS NULL;
```

**Full schema:** See `Database-Design/` folder

---

## Implementation Checklist

### Phase 1 - Core API (Weeks 3-5)

- [ ] Set up FastAPI project structure
- [ ] Implement Pydantic models for request/response validation
- [ ] Implement SQLAlchemy ORM models
- [ ] Create database migrations (Alembic)
- [ ] Implement authentication (JWT)
- [ ] Implement authorization middleware
- [ ] Implement rate limiting
- [ ] Add input validation and sanitization
- [ ] Set up error handling (RFC 7807 Problem Details)
- [ ] Generate OpenAPI/Swagger docs (auto from FastAPI)

### Phase 2 - Media Endpoints (Weeks 6-8)

- [ ] Implement file upload handling (multipart/form-data)
- [ ] Add EXIF extraction (exifread or pillow)
- [ ] Implement malware scanning (ClamAV)
- [ ] Add thumbnail generation (Pillow or ImageMagick)
- [ ] Implement file download/streaming
- [ ] Add pagination helpers
- [ ] Implement filtering and sorting
- [ ] Write tests for all media endpoints

### Phase 3 - Integration Endpoints (Weeks 9-11)

- [ ] Implement OAuth2 flow (Google Photos or Instagram)
- [ ] Create integration plugin architecture
- [ ] Implement sync logic (incremental + full)
- [ ] Add deduplication (check existing source links)
- [ ] Handle rate limiting from external APIs
- [ ] Implement background job system (Celery or RQ)
- [ ] Write tests for integration sync

### Phase 4 - API Documentation (Week 12)

- [ ] Review auto-generated OpenAPI spec
- [ ] Add examples to all endpoints
- [ ] Write API usage guide
- [ ] Set up Swagger UI
- [ ] Set up ReDoc
- [ ] Create Postman collection

---

## Open Questions

1. **GraphQL in Phase 2?**
   - REST is sufficient for Phase 1
   - GraphQL could simplify complex queries (get album + media + links in one request)
   - Defer decision to Phase 2

2. **Webhooks for integrations?**
   - Some integrations support webhooks (Instagram, Facebook)
   - Could enable real-time sync instead of polling
   - Defer to Phase 2

3. **Batch operations?**
   - Bulk upload, bulk delete, bulk tag?
   - Could improve efficiency
   - Defer to Phase 2 if needed

4. **API versioning strategy?**
   - Currently `/api/v1/...`
   - When to bump to v2? Only for breaking changes
   - Maintain v1 for how long? (1 year minimum)

---

## Next Steps

1. ✅ Complete API design (this folder)
2. 🔄 Design database schema (see `Database-Design/`)
3. ⏳ Implement API in FastAPI
4. ⏳ Write integration tests
5. ⏳ Deploy and test

---

**Status:** API design complete, ready for implementation
**Completion:** ~75KB of detailed specification across 3 documents
**Next Critical Step:** Database schema design
