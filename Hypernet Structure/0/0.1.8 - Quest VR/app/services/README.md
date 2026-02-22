# Services - Business Logic Layer

**Purpose:** Business logic services for Hypernet Core application

**Status:** Active development

---

## Overview

This directory contains the **service layer** for Hypernet Core - the business logic that sits between the API routes and the database models. Services encapsulate complex operations, enforce business rules, and coordinate between multiple models.

---

## Architecture Pattern

Hypernet follows a **layered architecture**:

```
┌─────────────────────────────────────────────┐
│  Routes (app/routes/)                       │
│  - Handle HTTP requests/responses           │
│  - Validate input (Pydantic)                │
│  - Authentication/authorization checks      │
│  - Call service layer                       │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│  Services (app/services/) ← YOU ARE HERE    │
│  - Business logic                           │
│  - Transaction management                   │
│  - Orchestrate multiple models              │
│  - Enforce business rules                   │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│  Models (app/models/)                       │
│  - SQLAlchemy ORM models                    │
│  - Database schema definitions              │
│  - Basic CRUD operations                    │
└────────────────┬────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────┐
│  Database (PostgreSQL)                      │
│  - Persistent storage                       │
└─────────────────────────────────────────────┘
```

---

## Why Services?

### Problems Services Solve

**1. Fat Routes**
```python
# ❌ BAD: Business logic in route handler
@router.post("/albums/{album_id}/media")
async def add_media_to_album(album_id: UUID, media_id: UUID, db: Session):
    # Complex logic mixed with HTTP handling
    album = db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise HTTPException(404)
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(404)
    link = Link(from_object_id=album_id, to_object_id=media_id, ...)
    db.add(link)
    album.media_count += 1
    db.commit()
    return link
```

**2. Duplicated Code**
```python
# Same logic repeated in multiple routes
@router.post("/albums/{id}/media")  # Adds to album.media_count
@router.delete("/albums/{id}/media/{media_id}")  # Decrements album.media_count
# Both need same logic - better in service!
```

**3. Hard to Test**
```python
# Testing routes requires mocking HTTP layer
# Testing services only requires database session
```

**4. Transaction Management**
```python
# Multiple database operations need to be atomic
# Services handle transaction boundaries
```

### Benefits of Services

✅ **Reusability:** Logic can be called from routes, background jobs, CLI tools
✅ **Testability:** Easy to unit test without HTTP mocking
✅ **Maintainability:** Business logic in one place
✅ **Transactions:** Proper transaction boundaries
✅ **Separation of Concerns:** Routes handle HTTP, services handle business logic

---

## Service Structure

### Naming Convention

Files named after the primary model they work with:

```
app/services/
├── __init__.py
├── user_service.py         # User account operations
├── media_service.py        # Media upload, processing, metadata
├── album_service.py        # Album creation, media organization
├── integration_service.py  # Integration connection, sync
├── link_service.py         # Link creation, querying
└── auth_service.py         # Authentication, token management
```

### Service Class Structure

```python
# app/services/media_service.py
from sqlalchemy.orm import Session
from app.models.media import Media
from app.models.link import Link
from uuid import UUID

class MediaService:
    """
    Business logic for media operations.

    Responsibilities:
    - Upload and process media files
    - Extract metadata (EXIF)
    - Generate thumbnails
    - Manage media lifecycle
    - Link media to albums and integrations
    """

    def __init__(self, db: Session):
        """
        Initialize service with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def upload_media(self, user_id: UUID, file, metadata: dict) -> Media:
        """
        Upload and process a media file.

        Args:
            user_id: Owner of the media
            file: Uploaded file object
            metadata: Additional metadata

        Returns:
            Created Media object

        Raises:
            ValueError: Invalid file type or size
            StorageError: Failed to save file
        """
        # Business logic here
        pass

    def add_to_album(self, media_id: UUID, album_id: UUID, user_id: UUID) -> Link:
        """
        Add media to an album.

        This is a transactional operation:
        1. Create link object
        2. Increment album.media_count
        3. Commit or rollback both

        Args:
            media_id: Media to add
            album_id: Target album
            user_id: User performing operation (for authorization)

        Returns:
            Created Link object

        Raises:
            NotFoundError: Media or album doesn't exist
            PermissionError: User doesn't own media or album
            DuplicateError: Media already in album
        """
        # Business logic here
        pass
```

---

## Service Patterns

### 1. Create Operation

```python
def create_album(self, user_id: UUID, name: str, description: str = None) -> Album:
    """Create a new album."""

    # Validate business rules
    if not name or len(name.strip()) == 0:
        raise ValueError("Album name cannot be empty")

    if len(name) > 100:
        raise ValueError("Album name too long (max 100 characters)")

    # Create object
    album = Album(
        user_id=user_id,
        name=name.strip(),
        description=description.strip() if description else None,
        media_count=0
    )

    # Save to database
    self.db.add(album)
    self.db.commit()
    self.db.refresh(album)

    return album
```

### 2. Read/Query Operation

```python
def get_album_media(
    self,
    album_id: UUID,
    user_id: UUID,
    limit: int = 50,
    offset: int = 0
) -> list[Media]:
    """Get media in an album (paginated)."""

    # Verify ownership
    album = self.db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise NotFoundError(f"Album {album_id} not found")

    if album.user_id != user_id:
        raise PermissionError("You don't own this album")

    # Query with joins
    media = (
        self.db.query(Media)
        .join(Link, Link.to_object_id == Media.id)
        .filter(
            Link.from_object_id == album_id,
            Link.link_type == "contains",
            Link.deleted_at.is_(None),
            Media.deleted_at.is_(None)
        )
        .order_by(Link.sort_order)
        .limit(limit)
        .offset(offset)
        .all()
    )

    return media
```

### 3. Update Operation

```python
def update_album(
    self,
    album_id: UUID,
    user_id: UUID,
    name: str = None,
    description: str = None
) -> Album:
    """Update album details."""

    # Get and verify ownership
    album = self.db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise NotFoundError(f"Album {album_id} not found")

    if album.user_id != user_id:
        raise PermissionError("You don't own this album")

    # Update fields
    if name is not None:
        if not name.strip():
            raise ValueError("Album name cannot be empty")
        album.name = name.strip()

    if description is not None:
        album.description = description.strip() if description else None

    # Save changes
    self.db.commit()
    self.db.refresh(album)

    return album
```

### 4. Delete Operation (Soft Delete)

```python
def delete_album(self, album_id: UUID, user_id: UUID) -> None:
    """Soft delete an album."""

    # Get and verify ownership
    album = self.db.query(Album).filter(Album.id == album_id).first()
    if not album:
        raise NotFoundError(f"Album {album_id} not found")

    if album.user_id != user_id:
        raise PermissionError("You don't own this album")

    # Soft delete (set deleted_at)
    from datetime import datetime, timezone
    album.deleted_at = datetime.now(timezone.utc)

    # Also soft delete all links
    self.db.query(Link).filter(
        Link.from_object_id == album_id,
        Link.deleted_at.is_(None)
    ).update({"deleted_at": datetime.now(timezone.utc)})

    self.db.commit()
```

### 5. Complex Transaction

```python
def sync_from_integration(
    self,
    integration_id: UUID,
    user_id: UUID,
    limit: int = 100
) -> dict:
    """
    Sync media from an integration.

    This is a complex multi-step transaction:
    1. Fetch items from external API
    2. Check for duplicates
    3. Download new media
    4. Create Media objects
    5. Create Link objects (media → integration)
    6. Update integration sync state

    Returns:
        Sync summary (new_count, skipped_count, error_count)
    """

    try:
        # Get integration
        integration = self.db.query(Integration).filter(
            Integration.id == integration_id,
            Integration.user_id == user_id
        ).first()

        if not integration:
            raise NotFoundError("Integration not found")

        # Fetch from external API (using integration-specific client)
        client = self._get_integration_client(integration)
        items = client.fetch_media(cursor=integration.sync_cursor, limit=limit)

        new_count = 0
        skipped_count = 0

        for item in items:
            # Check if already imported
            existing = self.db.query(Link).filter(
                Link.to_object_id == integration_id,
                Link.link_type == "source",
                Link.metadata["external_id"].astext == item.id
            ).first()

            if existing:
                skipped_count += 1
                continue

            # Download and create media
            file_path = self._download_media(item.url)
            media = self._create_media(user_id, file_path, item.metadata)

            # Create source link
            link = Link(
                user_id=user_id,
                from_object_id=media.id,
                to_object_id=integration_id,
                link_type="source",
                metadata={"external_id": item.id, "external_url": item.url}
            )
            self.db.add(link)

            new_count += 1

        # Update sync cursor
        integration.sync_cursor = items[-1].cursor if items else integration.sync_cursor
        integration.last_sync_at = datetime.now(timezone.utc)

        self.db.commit()

        return {
            "new_count": new_count,
            "skipped_count": skipped_count,
            "next_cursor": integration.sync_cursor
        }

    except Exception as e:
        self.db.rollback()
        raise SyncError(f"Sync failed: {str(e)}")
```

---

## Error Handling

### Custom Exceptions

Define service-specific exceptions:

```python
# app/services/exceptions.py

class ServiceError(Exception):
    """Base exception for service errors."""
    pass

class NotFoundError(ServiceError):
    """Resource not found."""
    pass

class PermissionError(ServiceError):
    """User doesn't have permission."""
    pass

class ValidationError(ServiceError):
    """Business rule validation failed."""
    pass

class DuplicateError(ServiceError):
    """Resource already exists."""
    pass

class StorageError(ServiceError):
    """File storage operation failed."""
    pass

class SyncError(ServiceError):
    """Integration sync failed."""
    pass
```

### Routes Handle HTTP Status

```python
# app/routes/albums.py
from fastapi import HTTPException
from app.services.album_service import AlbumService
from app.services.exceptions import NotFoundError, PermissionError

@router.get("/albums/{album_id}")
async def get_album(album_id: UUID, db: Session = Depends(get_db)):
    service = AlbumService(db)

    try:
        album = service.get_album(album_id, user_id=current_user.id)
        return album

    except NotFoundError:
        raise HTTPException(status_code=404, detail="Album not found")

    except PermissionError:
        raise HTTPException(status_code=403, detail="Access denied")
```

---

## Testing Services

### Unit Tests

Services are easy to test:

```python
# tests/services/test_album_service.py
import pytest
from app.services.album_service import AlbumService
from app.services.exceptions import NotFoundError, ValidationError

def test_create_album(db_session, test_user):
    """Test album creation."""
    service = AlbumService(db_session)

    album = service.create_album(
        user_id=test_user.id,
        name="Vacation Photos",
        description="Summer 2026"
    )

    assert album.id is not None
    assert album.name == "Vacation Photos"
    assert album.media_count == 0

def test_create_album_empty_name(db_session, test_user):
    """Test album creation with empty name fails."""
    service = AlbumService(db_session)

    with pytest.raises(ValidationError):
        service.create_album(user_id=test_user.id, name="")

def test_get_album_not_found(db_session, test_user):
    """Test getting non-existent album."""
    service = AlbumService(db_session)

    from uuid import uuid4
    with pytest.raises(NotFoundError):
        service.get_album(album_id=uuid4(), user_id=test_user.id)
```

---

## Service Dependencies

### Dependency Injection

Services can depend on other services:

```python
class MediaService:
    def __init__(self, db: Session, link_service: LinkService = None):
        self.db = db
        self.link_service = link_service or LinkService(db)

    def add_to_album(self, media_id: UUID, album_id: UUID, user_id: UUID):
        # Use link_service to create link
        link = self.link_service.create_link(
            from_object_id=album_id,
            to_object_id=media_id,
            link_type="contains",
            user_id=user_id
        )

        # Update denormalized count
        album = self.db.query(Album).filter(Album.id == album_id).first()
        album.media_count += 1
        self.db.commit()

        return link
```

---

## Background Jobs

Services can be called from background workers:

```python
# app/workers/sync_worker.py
from celery import Celery
from app.services.integration_service import IntegrationService
from app.core.database import SessionLocal

app = Celery('hypernet')

@app.task
def sync_integration_task(integration_id: str, user_id: str):
    """Background task to sync from integration."""

    db = SessionLocal()
    try:
        service = IntegrationService(db)
        result = service.sync_from_integration(
            integration_id=UUID(integration_id),
            user_id=UUID(user_id)
        )
        return result
    finally:
        db.close()
```

---

## Planned Services

### Phase 1 (Weeks 3-16)

1. **AuthService** - Authentication and token management
   - `register_user()`
   - `authenticate_user()`
   - `create_tokens()`
   - `refresh_access_token()`

2. **UserService** - User account management
   - `get_user()`
   - `update_user()`
   - `change_password()`
   - `delete_user()`

3. **MediaService** - Media upload and processing
   - `upload_media()`
   - `get_media()`
   - `update_media()`
   - `delete_media()`
   - `generate_thumbnail()`
   - `extract_exif()`

4. **AlbumService** - Album organization
   - `create_album()`
   - `get_album()`
   - `update_album()`
   - `delete_album()`
   - `get_album_media()`
   - `add_media_to_album()`
   - `remove_media_from_album()`

5. **IntegrationService** - External integrations
   - `connect_integration()`
   - `sync_from_integration()`
   - `disconnect_integration()`
   - `get_sync_status()`

6. **LinkService** - Relationship management
   - `create_link()`
   - `get_links()`
   - `delete_link()`
   - `find_related()`

### Phase 2+ (Future)

7. **SearchService** - Full-text search
8. **TagService** - AI-powered tagging
9. **ShareService** - Sharing and permissions
10. **ExportService** - Data export (GDPR)

---

## Best Practices

### 1. Single Responsibility
Each service focuses on one domain:
```python
# ✅ GOOD
class MediaService:  # Only media operations
class AlbumService:  # Only album operations

# ❌ BAD
class MediaAlbumService:  # Mixed responsibilities
```

### 2. Explicit Dependencies
```python
# ✅ GOOD
def __init__(self, db: Session):
    self.db = db

# ❌ BAD
def __init__(self):
    from app.core.database import db  # Hidden dependency
    self.db = db
```

### 3. Return Domain Objects
```python
# ✅ GOOD
def get_album(self, album_id: UUID) -> Album:
    return album  # ORM model

# ❌ BAD
def get_album(self, album_id: UUID) -> dict:
    return {"id": ..., "name": ...}  # Route should convert to dict
```

### 4. Handle Transactions
```python
# ✅ GOOD
def complex_operation(self):
    try:
        # Multiple DB operations
        self.db.commit()
    except:
        self.db.rollback()
        raise

# ❌ BAD
def complex_operation(self):
    # Operations without transaction handling
```

### 5. Validate Business Rules
```python
# ✅ GOOD
if album.media_count >= 10000:
    raise ValidationError("Album cannot exceed 10,000 items")

# ❌ BAD
# No validation, let database fail
```

---

## Quick Reference

### Creating a New Service

1. Create file: `app/services/[domain]_service.py`
2. Define service class with `__init__(self, db: Session)`
3. Add methods for business operations
4. Define custom exceptions if needed
5. Write unit tests in `tests/services/test_[domain]_service.py`
6. Use in routes via `service = DomainService(db)`

### Service Method Signature

```python
def operation_name(
    self,
    # Required parameters
    resource_id: UUID,
    user_id: UUID,
    # Optional parameters
    optional_param: str = None,
    # Pagination
    limit: int = 50,
    offset: int = 0
) -> ReturnType:
    """
    Brief description.

    Args:
        resource_id: Description
        user_id: For authorization
        optional_param: Description
        limit: Max results
        offset: Skip N results

    Returns:
        Description of return value

    Raises:
        NotFoundError: When resource doesn't exist
        PermissionError: When user lacks permission
        ValidationError: When business rule violated
    """
```

---

## Status

**Services Implemented:** 0 (folder ready for development)
**Next Services to Build:**
1. AuthService (authentication)
2. UserService (user management)
3. MediaService (file upload and processing)

**Priority:** High - Needed for API implementation

---

**Location:** `C:\Hypernet\Hypernet Structure\0.1 - Hypernet Core\0.1.1 - Core System\app\services\`
**Version:** 1.0
**Created:** 2026-02-10
**Maintainer:** Hypernet Development Team
