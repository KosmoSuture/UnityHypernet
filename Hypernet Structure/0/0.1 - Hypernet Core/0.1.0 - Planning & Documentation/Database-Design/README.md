# Database Design Documentation

## Overview

This directory contains the complete PostgreSQL database schema for Hypernet Core 0.1, implementing the object model and link model specifications.

---

## Documents

### 1. Database Schema (15KB)
**File:** `01-Database-Schema.md`

Complete PostgreSQL schema design with:
- 8 tables (users, media, albums, integrations, integration_secrets, links, refresh_tokens, audit_log)
- Indexes for performance
- Constraints for data integrity
- Triggers for auto-updating timestamps
- Views for convenience queries
- Common query examples

### 2. Initial Migration SQL (7KB)
**File:** `02-Initial-Migration.sql`

Ready-to-run SQL script that creates:
- All tables
- All indexes
- All constraints
- All triggers
- Convenience views
- Test admin user

**Usage:**
```bash
psql -U hypernet -d hypernet -f 02-Initial-Migration.sql
```

---

## Schema Summary

### Core Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| **users** | Accounts & auth | email, password_hash, storage_quota |
| **media** | Photos/videos | filename, hash, file_path, metadata (JSONB) |
| **albums** | Collections | name, cover_media_id, media_count |
| **integrations** | External services | integration_type, status, sync_cursor |
| **integration_secrets** | OAuth tokens | access_token, refresh_token (encrypted) |
| **links** | Relationships | from/to object, link_type, strength |

### Supporting Tables

| Table | Purpose |
|-------|---------|
| **refresh_tokens** | JWT refresh token management |
| **audit_log** | Security audit trail |

---

## Key Design Decisions

### 1. Hybrid Schema (Core + Metadata)

**Core fields:** Strongly typed, indexed, frequently queried
```sql
filename VARCHAR(255) NOT NULL
media_type VARCHAR(50) NOT NULL
taken_at TIMESTAMP WITH TIME ZONE
```

**Metadata field:** Flexible JSONB for integration-specific data
```sql
metadata JSONB NOT NULL DEFAULT '{}'::jsonb
```

**Benefits:**
- ✅ Performant queries on common fields
- ✅ Extensible for new integrations
- ✅ No schema changes needed for new data types

### 2. Soft Deletes

All main tables have `deleted_at` column:
```sql
deleted_at TIMESTAMP WITH TIME ZONE
```

**Benefits:**
- Can restore accidentally deleted data
- Audit trail preserved
- Hard delete after retention period (30 days)

**Indexes exclude deleted:**
```sql
CREATE INDEX idx_media_user_id ON media(user_id) WHERE deleted_at IS NULL;
```

### 3. First-Class Links

Links are objects, not just foreign keys:

**Traditional approach:**
```sql
-- Media can only be in ONE album
ALTER TABLE media ADD COLUMN album_id UUID;
```

**Hypernet approach:**
```sql
-- Media can be in MANY albums via links
INSERT INTO links (from_object_id, to_object_id, link_type)
VALUES (album_id, media_id, 'contains');
```

**Benefits:**
- Many-to-many relationships
- Rich metadata on relationships
- Easy to query all relationships
- Flexible relationship types

### 4. UUIDs for All IDs

```sql
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
```

**Benefits:**
- Globally unique (can merge databases)
- No auto-increment race conditions
- Can generate client-side
- Security (not sequential)

### 5. Denormalized Counts

```sql
ALTER TABLE albums ADD COLUMN media_count INTEGER NOT NULL DEFAULT 0;
```

**Trade-off:**
- ✅ Fast reads (no COUNT query)
- ❌ Slower writes (must update count)
- ✅ Worth it for frequently displayed data

---

## Relationships

### Ownership (1:N)
```
User → Media (user_id foreign key)
User → Albums (user_id foreign key)
User → Integrations (user_id foreign key)
User → Links (user_id foreign key)
```

All with `ON DELETE CASCADE` - deleting user deletes all their data.

### Links (M:N via link objects)
```
Album → Media (via Link, type='contains')
Media → Integration (via Link, type='source')
Media ↔ Media (via Link, type='duplicate_of', bidirectional)
Media → Media (via Link, type='variant_of', thumbnails)
```

### Direct Foreign Keys
```
Album → Media (cover_media_id, ON DELETE SET NULL)
```

---

## Common Queries

### Get user's media (paginated)
```sql
SELECT * FROM media
WHERE user_id = $1 AND deleted_at IS NULL
ORDER BY taken_at DESC NULLS LAST
LIMIT 50 OFFSET 0;
```

### Get media in album
```sql
SELECT m.*, l.sort_order
FROM media m
JOIN links l ON l.to_object_id = m.id
WHERE l.from_object_id = $1  -- album_id
  AND l.link_type = 'contains'
  AND l.deleted_at IS NULL
  AND m.deleted_at IS NULL
ORDER BY l.sort_order;
```

### Check if media already imported
```sql
SELECT m.id FROM media m
JOIN links l ON l.from_object_id = m.id
WHERE m.user_id = $1
  AND l.to_object_id = $2  -- integration_id
  AND l.link_type = 'source'
  AND l.metadata->>'external_id' = $3
  AND m.deleted_at IS NULL
LIMIT 1;
```

---

## Indexes Strategy

### Partial Indexes (Exclude Soft-Deleted)
```sql
CREATE INDEX idx_media_user_id ON media(user_id)
WHERE deleted_at IS NULL;
```

**Benefit:** Index only includes active rows, smaller and faster.

### Composite Indexes
```sql
CREATE INDEX idx_media_source
ON media(user_id, source_type, source_id)
WHERE deleted_at IS NULL;
```

**Benefit:** Fast deduplication queries during sync.

### GIN Indexes (JSONB)
```sql
CREATE INDEX idx_media_metadata
ON media USING GIN(metadata);
```

**Benefit:** Query inside JSON metadata.
```sql
WHERE metadata->>'camera' = 'iPhone 15'
```

### Unique Indexes
```sql
CREATE UNIQUE INDEX idx_links_unique
ON links(from_object_id, to_object_id, link_type)
WHERE deleted_at IS NULL;
```

**Benefit:** Prevent duplicate links.

---

## Security

### Database-Level Encryption

Entire `/data` partition encrypted with LUKS2:
```bash
cryptsetup luksFormat /dev/sda4
cryptsetup open /dev/sda4 data-encrypted
mkfs.ext4 /dev/mapper/data-encrypted
```

### Column-Level Encryption (Optional)

For sensitive fields like OAuth tokens:
```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt on insert
INSERT INTO integration_secrets (access_token)
VALUES (pgp_sym_encrypt($1, 'encryption-key'));

-- Decrypt on read
SELECT pgp_sym_decrypt(access_token::bytea, 'encryption-key')
FROM integration_secrets WHERE integration_id = $1;
```

### Row-Level Security (Future)

```sql
ALTER TABLE media ENABLE ROW LEVEL SECURITY;

CREATE POLICY media_user_isolation ON media
FOR ALL
USING (user_id = current_setting('app.current_user_id')::uuid);
```

Application sets context:
```sql
SET app.current_user_id = 'user-uuid';
```

---

## Performance Optimization

### Query Performance
1. **Always filter by deleted_at IS NULL**
2. **Use LIMIT for large result sets**
3. **Leverage partial indexes** (WHERE deleted_at IS NULL)
4. **Use EXPLAIN ANALYZE** to check query plans

### Write Performance
1. **Batch inserts** when importing from integrations
2. **Update denormalized counts** asynchronously if needed
3. **Use transactions** for multi-step operations

### Maintenance
```sql
-- Run weekly
VACUUM ANALYZE;

-- Or per table
VACUUM ANALYZE media;
```

---

## Backup Strategy

### Daily Backups
```bash
# Backup
pg_dump -U hypernet -d hypernet -F c \
  -f /backup/db/hypernet-$(date +%Y%m%d).dump

# Restore
pg_restore -U hypernet -d hypernet \
  /backup/db/hypernet-20260203.dump
```

### Point-in-Time Recovery (PITR)

Enable WAL archiving in `postgresql.conf`:
```
wal_level = replica
archive_mode = on
archive_command = 'cp %p /backup/wal/%f'
```

---

## Migration Strategy

### Alembic (SQLAlchemy Migrations)

**Directory structure:**
```
alembic/
  ├── versions/
  │   ├── 0001_initial.py
  │   ├── 0002_add_ai_tags.py
  │   └── ...
  ├── env.py
  └── alembic.ini
```

**Create migration:**
```bash
alembic revision --autogenerate -m "Add AI tags to media"
```

**Apply migrations:**
```bash
alembic upgrade head
```

**Rollback:**
```bash
alembic downgrade -1
```

---

## Testing the Schema

### 1. Create Database
```bash
createdb -U postgres hypernet
psql -U postgres -d hypernet -c "CREATE ROLE hypernet WITH LOGIN PASSWORD 'secure-password';"
psql -U postgres -d hypernet -c "GRANT ALL PRIVILEGES ON DATABASE hypernet TO hypernet;"
```

### 2. Run Migration
```bash
psql -U hypernet -d hypernet -f 02-Initial-Migration.sql
```

### 3. Verify Tables
```sql
\dt  -- List tables
\d users  -- Describe users table
\di  -- List indexes
```

### 4. Insert Test Data
```sql
-- Create test user
INSERT INTO users (email, password_hash, display_name)
VALUES ('test@example.com', 'hashed-password', 'Test User');

-- Create test media
INSERT INTO media (user_id, filename, media_type, mime_type, size, file_path, hash)
VALUES (
  (SELECT id FROM users WHERE email = 'test@example.com'),
  'test-photo.jpg',
  'photo',
  'image/jpeg',
  1024000,
  'users/.../media/2026/02/test.jpg',
  'abcd1234...'
);

-- Create test album
INSERT INTO albums (user_id, name)
VALUES (
  (SELECT id FROM users WHERE email = 'test@example.com'),
  'Test Album'
);

-- Link media to album
INSERT INTO links (user_id, from_object_id, from_object_type, to_object_id, to_object_type, link_type)
VALUES (
  (SELECT id FROM users WHERE email = 'test@example.com'),
  (SELECT id FROM albums WHERE name = 'Test Album'),
  'album',
  (SELECT id FROM media WHERE filename = 'test-photo.jpg'),
  'media',
  'contains'
);

-- Query album media
SELECT m.filename, l.sort_order
FROM media m
JOIN links l ON l.to_object_id = m.id
JOIN albums a ON l.from_object_id = a.id
WHERE a.name = 'Test Album'
  AND l.link_type = 'contains';
```

---

## Open Questions

1. **Partitioning for scale?**
   - Partition `media` table by user_id or date?
   - Defer until >1M rows

2. **Read replicas?**
   - For Phase 2 multi-server deployment
   - PostgreSQL streaming replication

3. **Full-text search?**
   - PostgreSQL built-in (tsvector)?
   - Or external (Elasticsearch, Meilisearch)?
   - Defer to Phase 2

4. **Time-series data?**
   - Use TimescaleDB extension for audit_log?
   - Only if performance issues

---

## Next Steps

### Implementation (Phase 1)

1. ✅ Create database schema document
2. ✅ Write initial migration SQL
3. ⏳ Set up local PostgreSQL database
4. ⏳ Run migration and verify
5. ⏳ Create SQLAlchemy ORM models
6. ⏳ Write Alembic migration scripts
7. ⏳ Test with sample data
8. ⏳ Optimize based on query patterns

### Code Structure (Next Session)

```python
# app/models/user.py
from sqlalchemy import Column, String, Boolean, BigInteger
from app.models.base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    # ...
```

---

**Status:** Database schema complete and ready for implementation
**Total Size:** ~22KB across 3 files
**Tables:** 8 core tables, 3 convenience views
**Indexes:** 25+ indexes for performance
**Ready for:** SQLAlchemy model implementation and FastAPI integration
