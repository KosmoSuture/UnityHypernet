# Hypernet Core - Database Schema

**Version:** 0.1.0
**Database:** PostgreSQL 15+
**ORM:** SQLAlchemy 2.0+
**Migrations:** Alembic
**Last Updated:** 2026-02-03

---

## Overview

This document defines the PostgreSQL database schema for Hypernet Core 0.1, implementing the object model and link model specifications.

### Design Principles

1. **Normalized** - Minimize redundancy, maintain data integrity
2. **Performant** - Indexes on frequently queried fields
3. **Extensible** - JSONB metadata for flexibility
4. **Secure** - Row-level security, encrypted sensitive fields
5. **Auditable** - Timestamps and soft deletes on all tables

---

## Tables

### 1. users

User accounts and authentication.

```sql
CREATE TABLE users (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Authentication
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,

    -- Profile
    display_name VARCHAR(100),
    avatar_url VARCHAR(1024),

    -- Account Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,

    -- Storage Quotas
    storage_used BIGINT NOT NULL DEFAULT 0,
    storage_quota BIGINT NOT NULL DEFAULT 10737418240, -- 10 GB

    -- Extensibility
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Indexes
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_created_at ON users(created_at);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

### 2. media

Photos, videos, and other media files.

```sql
CREATE TABLE media (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Ownership
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Basic Info
    filename VARCHAR(255) NOT NULL,
    media_type VARCHAR(50) NOT NULL, -- 'photo', 'video', 'document', 'other'
    mime_type VARCHAR(100) NOT NULL,

    -- File Information
    size BIGINT NOT NULL,
    width INTEGER,
    height INTEGER,
    duration DOUBLE PRECISION, -- seconds (for videos)

    -- Storage
    file_path VARCHAR(1024) NOT NULL,
    thumbnail_path VARCHAR(1024),
    hash VARCHAR(64) NOT NULL, -- SHA-256

    -- Dates and Location
    taken_at TIMESTAMP WITH TIME ZONE,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,

    -- Source Tracking
    source_type VARCHAR(50), -- 'upload', 'integration', 'import'
    source_id VARCHAR(255),

    -- Processing Status
    processing_status VARCHAR(50) NOT NULL DEFAULT 'pending', -- 'pending', 'processing', 'complete', 'failed'
    thumbnail_generated BOOLEAN NOT NULL DEFAULT FALSE,
    metadata_extracted BOOLEAN NOT NULL DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,

    -- Extensibility
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Constraints
    CONSTRAINT chk_media_type CHECK (media_type IN ('photo', 'video', 'document', 'other')),
    CONSTRAINT chk_processing_status CHECK (processing_status IN ('pending', 'processing', 'complete', 'failed')),
    CONSTRAINT chk_latitude CHECK (latitude IS NULL OR (latitude >= -90 AND latitude <= 90)),
    CONSTRAINT chk_longitude CHECK (longitude IS NULL OR (longitude >= -180 AND longitude <= 180))
);

-- Indexes
CREATE INDEX idx_media_user_id ON media(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_media_hash ON media(hash);
CREATE INDEX idx_media_taken_at ON media(taken_at) WHERE deleted_at IS NULL;
CREATE INDEX idx_media_media_type ON media(media_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_media_source ON media(user_id, source_type, source_id) WHERE deleted_at IS NULL;

-- GIN index for metadata (allows querying inside JSONB)
CREATE INDEX idx_media_metadata ON media USING GIN(metadata);

-- Trigger for updated_at
CREATE TRIGGER media_updated_at BEFORE UPDATE ON media
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

### 3. albums

Collections of media.

```sql
CREATE TABLE albums (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Ownership
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Basic Info
    name VARCHAR(200) NOT NULL,
    description TEXT,

    -- Display
    cover_media_id UUID REFERENCES media(id) ON DELETE SET NULL,
    sort_order VARCHAR(50) NOT NULL DEFAULT 'date_desc', -- 'date_asc', 'date_desc', 'manual'

    -- Counts (denormalized for performance)
    media_count INTEGER NOT NULL DEFAULT 0,

    -- Privacy (future use)
    visibility VARCHAR(50) NOT NULL DEFAULT 'private', -- 'private', 'unlisted', 'public'

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,

    -- Source Tracking
    source_type VARCHAR(50),
    source_id VARCHAR(255),

    -- Extensibility
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Constraints
    CONSTRAINT chk_sort_order CHECK (sort_order IN ('date_asc', 'date_desc', 'manual')),
    CONSTRAINT chk_visibility CHECK (visibility IN ('private', 'unlisted', 'public')),
    CONSTRAINT chk_media_count CHECK (media_count >= 0)
);

-- Indexes
CREATE INDEX idx_albums_user_id ON albums(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_albums_name ON albums(user_id, name) WHERE deleted_at IS NULL;

-- Trigger for updated_at
CREATE TRIGGER albums_updated_at BEFORE UPDATE ON albums
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

### 4. integrations

Connected external services.

```sql
CREATE TABLE integrations (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Ownership
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Integration Details
    integration_type VARCHAR(50) NOT NULL, -- 'instagram', 'google_photos', 'facebook', etc.
    integration_name VARCHAR(200) NOT NULL,

    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- 'connected', 'disconnected', 'error', 'pending'
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,

    -- OAuth2 (encrypted in separate table - see integration_secrets)
    token_expires_at TIMESTAMP WITH TIME ZONE,

    -- Sync State
    last_sync_at TIMESTAMP WITH TIME ZONE,
    last_sync_status VARCHAR(50), -- 'success', 'partial', 'failed'
    sync_cursor TEXT, -- Pagination cursor for incremental sync

    -- Statistics
    items_synced INTEGER NOT NULL DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,

    -- Source Tracking
    source_type VARCHAR(50),
    source_id VARCHAR(255),

    -- Extensibility
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Constraints
    CONSTRAINT chk_integration_status CHECK (status IN ('connected', 'disconnected', 'error', 'pending')),
    CONSTRAINT chk_sync_status CHECK (last_sync_status IS NULL OR last_sync_status IN ('success', 'partial', 'failed')),
    CONSTRAINT chk_items_synced CHECK (items_synced >= 0)
);

-- Indexes
CREATE INDEX idx_integrations_user_id ON integrations(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_integrations_type ON integrations(user_id, integration_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_integrations_status ON integrations(status) WHERE deleted_at IS NULL;

-- Trigger for updated_at
CREATE TRIGGER integrations_updated_at BEFORE UPDATE ON integrations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

### 5. integration_secrets

OAuth tokens and secrets (encrypted at rest).

**Note:** Stored separately for additional security. Can be encrypted at database level using pgcrypto.

```sql
CREATE TABLE integration_secrets (
    -- Identity
    integration_id UUID PRIMARY KEY REFERENCES integrations(id) ON DELETE CASCADE,

    -- OAuth2 Tokens (should be encrypted)
    access_token TEXT,
    refresh_token TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- No indexes needed (always queried by integration_id primary key)

-- Trigger for updated_at
CREATE TRIGGER integration_secrets_updated_at BEFORE UPDATE ON integration_secrets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

### 6. links

Relationships between objects (first-class links).

```sql
CREATE TABLE links (
    -- Identity
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Ownership
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Link Endpoints
    from_object_id UUID NOT NULL,
    from_object_type VARCHAR(50) NOT NULL,
    to_object_id UUID NOT NULL,
    to_object_type VARCHAR(50) NOT NULL,

    -- Link Type
    link_type VARCHAR(50) NOT NULL, -- 'contains', 'source', 'duplicate_of', 'variant_of'

    -- Link Properties
    strength DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    is_bidirectional BOOLEAN NOT NULL DEFAULT FALSE,

    -- Ordering (for ordered relationships like album -> photos)
    sort_order INTEGER,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE,

    -- Source Tracking
    source_type VARCHAR(50),
    source_id VARCHAR(255),

    -- Extensibility
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Constraints
    CONSTRAINT chk_link_type CHECK (link_type IN ('contains', 'source', 'duplicate_of', 'variant_of', 'related_to')),
    CONSTRAINT chk_strength CHECK (strength >= 0.0 AND strength <= 1.0),
    CONSTRAINT chk_not_self_link CHECK (from_object_id != to_object_id OR from_object_type != to_object_type)
);

-- Indexes
CREATE INDEX idx_links_user_id ON links(user_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_links_from ON links(from_object_id, link_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_links_to ON links(to_object_id, link_type) WHERE deleted_at IS NULL;
CREATE INDEX idx_links_ordered ON links(from_object_id, sort_order) WHERE deleted_at IS NULL AND sort_order IS NOT NULL;

-- Unique constraint: No duplicate links
CREATE UNIQUE INDEX idx_links_unique ON links(from_object_id, to_object_id, link_type) WHERE deleted_at IS NULL;

-- Trigger for updated_at
CREATE TRIGGER links_updated_at BEFORE UPDATE ON links
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## Additional Tables (Future / Optional)

### 7. refresh_tokens (for JWT refresh token management)

```sql
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(64) NOT NULL UNIQUE, -- SHA-256 of token
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    revoked_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_hash ON refresh_tokens(token_hash) WHERE revoked_at IS NULL;
```

---

### 8. audit_log (security audit trail)

```sql
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL, -- 'login', 'upload', 'delete', etc.
    resource_type VARCHAR(50), -- 'media', 'album', etc.
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
CREATE INDEX idx_audit_log_action ON audit_log(action);
```

---

## Views

### active_media (media not deleted)

```sql
CREATE VIEW active_media AS
SELECT * FROM media WHERE deleted_at IS NULL;
```

### active_albums (albums not deleted)

```sql
CREATE VIEW active_albums AS
SELECT * FROM albums WHERE deleted_at IS NULL;
```

### active_links (links not deleted)

```sql
CREATE VIEW active_links AS
SELECT * FROM links WHERE deleted_at IS NULL;
```

---

## Common Queries

### Get all media for user

```sql
SELECT * FROM media
WHERE user_id = $1 AND deleted_at IS NULL
ORDER BY taken_at DESC NULLS LAST
LIMIT 50 OFFSET 0;
```

### Get media in album (with links)

```sql
SELECT m.*, l.sort_order, l.id AS link_id
FROM media m
JOIN links l ON l.to_object_id = m.id
WHERE l.from_object_id = $1  -- album_id
  AND l.from_object_type = 'album'
  AND l.to_object_type = 'media'
  AND l.link_type = 'contains'
  AND l.deleted_at IS NULL
  AND m.deleted_at IS NULL
ORDER BY l.sort_order NULLS LAST;
```

### Get source integration for media

```sql
SELECT i.*
FROM integrations i
JOIN links l ON l.to_object_id = i.id
WHERE l.from_object_id = $1  -- media_id
  AND l.from_object_type = 'media'
  AND l.to_object_type = 'integration'
  AND l.link_type = 'source'
  AND l.deleted_at IS NULL
  AND i.deleted_at IS NULL;
```

### Find duplicates of media

```sql
SELECT m.*
FROM media m
JOIN links l ON l.to_object_id = m.id
WHERE l.from_object_id = $1  -- media_id
  AND l.from_object_type = 'media'
  AND l.to_object_type = 'media'
  AND l.link_type = 'duplicate_of'
  AND l.deleted_at IS NULL
  AND m.deleted_at IS NULL;
```

### Check for existing import (deduplication)

```sql
SELECT m.id
FROM media m
JOIN links l ON l.from_object_id = m.id
WHERE m.user_id = $1
  AND l.to_object_id = $2  -- integration_id
  AND l.link_type = 'source'
  AND m.metadata->>'external_id' = $3  -- external media ID
  AND m.deleted_at IS NULL
  AND l.deleted_at IS NULL
LIMIT 1;
```

---

## Performance Considerations

### Indexes

**Users:**
- `email` - Fast login lookups
- `created_at` - User statistics

**Media:**
- `user_id` - Fast user media queries
- `hash` - Deduplication
- `taken_at` - Timeline views
- `media_type` - Filter by type
- `(user_id, source_type, source_id)` - Sync deduplication

**Links:**
- `(from_object_id, link_type)` - Fast "get all links from X"
- `(to_object_id, link_type)` - Fast "get all links to X"
- `(from_object_id, to_object_id, link_type)` - Prevent duplicates, fast lookups

### Query Optimization

1. **Always filter by deleted_at IS NULL** in WHERE clauses
2. **Use LIMIT** for large result sets
3. **Index JSONB fields** selectively (GIN indexes)
4. **Denormalize counts** (e.g., `album.media_count`) for performance
5. **Use partial indexes** (WHERE deleted_at IS NULL) to exclude soft-deleted rows

---

## Data Integrity

### Foreign Keys

- All `user_id` columns reference `users(id)` with `ON DELETE CASCADE`
- Deleting user deletes all their data
- `cover_media_id` uses `ON DELETE SET NULL` (album survives if cover deleted)

### Constraints

- `CHECK` constraints for enum-like fields (media_type, status, etc.)
- `CHECK` constraints for valid ranges (latitude, longitude, strength)
- `UNIQUE` constraints prevent duplicates (email, links)

### Soft Deletes

- `deleted_at` timestamp instead of hard delete
- Partial indexes exclude soft-deleted rows
- Can be restored by setting `deleted_at = NULL`
- Hard delete after retention period (cron job)

---

## Security

### Encryption at Rest

**Database-level encryption (LUKS2):**
- Entire `/data` partition encrypted
- Protects all tables

**Column-level encryption (optional):**
```sql
-- Using pgcrypto extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt access_token before insert
INSERT INTO integration_secrets (integration_id, access_token)
VALUES ($1, pgp_sym_encrypt($2, 'encryption-key'));

-- Decrypt on read
SELECT pgp_sym_decrypt(access_token::bytea, 'encryption-key') AS access_token
FROM integration_secrets WHERE integration_id = $1;
```

### Row-Level Security (RLS)

**Enable RLS on tables:**
```sql
ALTER TABLE media ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own media
CREATE POLICY media_user_isolation ON media
    FOR ALL
    USING (user_id = current_setting('app.current_user_id')::uuid);
```

**Set user context in application:**
```sql
SET app.current_user_id = 'user-uuid';
```

---

## Migration Strategy

### Initial Migration (0001_initial.sql)

See `02-Initial-Migration.sql`

### Future Migrations

```sql
-- Example: Add new column
ALTER TABLE media ADD COLUMN ai_tags TEXT[];

-- Example: Create new index
CREATE INDEX idx_media_ai_tags ON media USING GIN(ai_tags);

-- Example: Add new link type
ALTER TABLE links DROP CONSTRAINT chk_link_type;
ALTER TABLE links ADD CONSTRAINT chk_link_type
    CHECK (link_type IN ('contains', 'source', 'duplicate_of', 'variant_of', 'tagged_with'));
```

---

## Backup and Maintenance

### Daily Backups

```bash
# Backup database
pg_dump -U hypernet -d hypernet -F c -f /backup/db/hypernet-$(date +%Y%m%d).dump

# Restore
pg_restore -U hypernet -d hypernet /backup/db/hypernet-20260203.dump
```

### Vacuum and Analyze

```sql
-- Regular maintenance (run weekly)
VACUUM ANALYZE;

-- Per table
VACUUM ANALYZE media;
```

### Clean up soft-deleted rows

```sql
-- Delete media soft-deleted > 30 days ago
DELETE FROM media
WHERE deleted_at IS NOT NULL
  AND deleted_at < NOW() - INTERVAL '30 days';
```

---

## Next Steps

1. ✅ Review schema design
2. ⏳ Create initial migration SQL
3. ⏳ Implement SQLAlchemy models
4. ⏳ Test schema with sample data
5. ⏳ Optimize indexes based on query patterns

---

**Status:** Ready for implementation
**Next:** `02-Initial-Migration.sql` - SQL script to create all tables
