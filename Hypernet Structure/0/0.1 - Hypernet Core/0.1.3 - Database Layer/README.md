# 0.1.3 - Database Layer

## Overview

This folder will contain database-specific configurations, migrations, schemas, and tooling.

**Current Status:** Planning phase - Database models are in 0.1.1 - Core System

## Purpose

The Database Layer folder will house:
- Database migration files (Alembic)
- Schema documentation and diagrams
- Database backup and restore procedures
- Performance optimization configurations
- Indexing strategies
- Query optimization guides
- Database monitoring and health checks
- Seed data and fixtures

## Current Implementation Location

Database models and configuration are currently in:
- **Models:** `0.1.1 - Core System/app/models/`
- **Config:** `0.1.1 - Core System/app/core/database.py`

**Implementation Status:** ✅ Models Complete
- 19 SQLAlchemy models defined
- BaseObject and OwnedObject base classes
- Proper relationships and constraints
- Ready for migration creation

## Database Technology

**Database:** PostgreSQL 14+
**ORM:** SQLAlchemy 2.0
**Migration Tool:** Alembic (to be set up)
**Connection Pooling:** SQLAlchemy engine

## Data Models (19 Total)

### Core Models (4)
1. **User** - User accounts and authentication
2. **Integration** - OAuth connections to external services
3. **Link** - Data sharing links
4. **Notification** - System notifications

### Media Models (2)
5. **Media** - Photos, videos, audio, documents
6. **Album** - Media collections

### Social Models (2)
7. **SocialPost** - Social media posts
8. **SocialAccount** - Social media profiles

### Communication Models (2)
9. **Email** - Email messages
10. **Contact** - Address book contacts

### Web Models (2)
11. **WebPage** - Saved web pages/articles
12. **Bookmark** - Saved links

### Productivity Models (3)
13. **CalendarEvent** - Calendar events and meetings
14. **Task** - To-do items and workflows
15. **Note** - Personal notes

### Personal Models (4)
16. **Document** - Personal documents and files
17. **Transaction** - Financial transactions
18. **Location** - Location history
19. **HealthRecord** - Medical records

### Profile Models (2)
20. **ProfileAttribute** - User profile fields
21. **Device** - User devices

### System Models (1)
22. **Audit** - Audit logs (read-only)

## Future Structure

```
0.1.3 - Database Layer/
├── 0.1.3.0 - Migrations/
│   ├── alembic.ini
│   ├── env.py
│   ├── versions/
│   │   ├── 001_initial_schema.py
│   │   ├── 002_add_indexes.py
│   │   └── ...
│   └── README.md
├── 0.1.3.1 - Schema Documentation/
│   ├── ER-DIAGRAM.md
│   ├── TABLE-REFERENCE.md
│   └── RELATIONSHIPS.md
├── 0.1.3.2 - Backup & Restore/
│   ├── backup-procedures.md
│   ├── restore-procedures.md
│   └── backup-scripts/
├── 0.1.3.3 - Performance/
│   ├── indexing-strategy.md
│   ├── query-optimization.md
│   └── performance-tuning.md
├── 0.1.3.4 - Monitoring/
│   ├── health-checks.md
│   ├── monitoring-queries.sql
│   └── alerting-config.yaml
└── 0.1.3.5 - Seed Data/
    ├── test-fixtures/
    ├── demo-data/
    └── production-seeds/
```

## Database Schema Overview

### Universal Patterns

**All models inherit from BaseObject:**
```python
- id: UUID (primary key)
- created_at: DateTime
- updated_at: DateTime
- deleted_at: DateTime (soft delete)
- metadata: JSONB (flexible metadata)
- source_integration_id: UUID (data source tracking)
- source_platform: String (e.g., "google_photos")
- source_object_id: String (external ID)
```

**User-owned models inherit from OwnedObject:**
```python
- user_id: UUID (foreign key to users)
- All BaseObject fields
```

### Relationships

**User → Everything**
- One user has many: media, posts, contacts, tasks, etc.
- All personal data tied to user_id
- Cascading permissions and privacy

**Media → Albums**
- Many-to-many relationship
- One media item can be in multiple albums
- One album can contain multiple media items

**Tasks → Subtasks**
- Hierarchical self-referential relationship
- parent_task_id references other tasks
- Enables nested task structures

**Emails → Threads**
- thread_id groups related emails
- Enables conversation views

## Indexing Strategy

### Primary Indexes (Automatic)
- All `id` fields (UUID primary keys)

### Foreign Key Indexes (Needed)
- `user_id` on all user-owned tables
- `integration_id` on relevant tables
- `parent_task_id` on tasks
- `thread_id` on emails

### Query Performance Indexes (Needed)
- `created_at`, `updated_at` for temporal queries
- `deleted_at IS NULL` for soft delete filtering
- `platform` on social posts/accounts
- `status` on tasks
- `is_read` on emails/notifications
- Composite indexes for common query patterns

## Next Steps

### Immediate (This Week)
1. **Set up Alembic**
   ```bash
   pip install alembic
   alembic init migrations
   ```

2. **Create Initial Migration**
   ```bash
   alembic revision --autogenerate -m "Initial schema"
   alembic upgrade head
   ```

3. **Deploy PostgreSQL Database**
   - Local development: PostgreSQL via Docker
   - Production: Render/Railway/AWS RDS

### Short-term (Month 1-3)
1. Create database backup procedures
2. Set up monitoring and health checks
3. Optimize indexes based on query patterns
4. Create seed data for testing

### Medium-term (Month 3-6)
1. Implement query performance monitoring
2. Set up read replicas (if needed for scale)
3. Optimize for multi-tenant architecture
4. Implement database encryption at rest

## Database Deployment

### Development
```yaml
Database: PostgreSQL 14
Host: localhost
Port: 5432
Database: hypernet_dev
User: hypernet
Connection: SQLAlchemy engine with connection pooling
```

### Production (Planned)
```yaml
Database: PostgreSQL 14+ (managed service)
Provider: Render / Railway / AWS RDS
High Availability: Multi-AZ deployment
Backups: Automated daily, 30-day retention
Monitoring: PostgreSQL metrics + custom queries
Encryption: At rest and in transit
```

## Connection String Format

```
postgresql://{user}:{password}@{host}:{port}/{database}
```

Currently in: `0.1.1 - Core System/app/core/config.py`

## Migration Workflow

### Creating Migrations
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description"

# Review generated migration in versions/
# Edit if needed

# Apply migration
alembic upgrade head
```

### Rolling Back
```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade {revision_id}
```

## Data Privacy & Compliance

### GDPR Compliance
- Soft delete enables "right to be forgotten"
- Audit logs track all data access
- User data export via API
- Data retention policies

### Encryption
- Passwords: BCrypt (cost factor 12)
- Tokens: JWT with HS256
- At Rest: Database-level encryption
- In Transit: TLS/SSL connections

### Backup Strategy
- Automated daily backups
- 30-day retention
- Encrypted backup storage
- Tested restore procedures

## Related Folders

- **Models:** `0.1.1 - Core System/app/models/`
- **API:** `0.1.2 - API Layer/`
- **Config:** `0.1.1 - Core System/app/core/config.py`

---

**Status:** Placeholder - Models in 0.1.1
**Created:** February 5, 2026
**Last Updated:** February 5, 2026
**Owner:** Hypernet Core Team
**Next Action:** Set up Alembic migrations
