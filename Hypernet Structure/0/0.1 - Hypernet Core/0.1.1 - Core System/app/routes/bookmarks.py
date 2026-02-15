"""
Bookmarks Routes

Endpoints for managing browser bookmarks and saved links.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.bookmark import Bookmark

router = APIRouter()


# Request/Response Models
class BookmarkCreate(BaseModel):
    """Bookmark creation request"""
    url: str = Field(..., max_length=2048)
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    favicon_url: Optional[str] = Field(None, max_length=500)
    folder: Optional[str] = Field(None, max_length=255)
    tags: Optional[List[str]] = None
    is_favorite: bool = Field(default=False)


class BookmarkUpdate(BaseModel):
    """Bookmark update request"""
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    folder: Optional[str] = Field(None, max_length=255)
    tags: Optional[List[str]] = None
    is_favorite: Optional[bool] = None


class BookmarkResponse(BaseModel):
    """Bookmark response"""
    id: str
    user_id: str
    url: str
    title: str
    description: Optional[str]
    favicon_url: Optional[str]
    folder: Optional[str]
    tags: Optional[List[str]]
    is_favorite: bool
    visit_count: int
    last_visited_at: Optional[datetime]
    bookmarked_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class BookmarkListResponse(BaseModel):
    """Paginated bookmark list response"""
    items: List[BookmarkResponse]
    total: int
    page: int
    page_size: int


@router.post("", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    request: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new bookmark.

    - **url**: URL to bookmark (required)
    - **title**: Page title (required)
    - **description**: Optional description or notes
    - **folder**: Organize in folders (e.g., "Work", "Research")
    - **tags**: List of tags for categorization
    - **is_favorite**: Mark as favorite
    """
    bookmark = Bookmark(
        user_id=current_user.id,
        url=request.url,
        title=request.title,
        description=request.description,
        favicon_url=request.favicon_url,
        folder=request.folder,
        tags=request.tags,
        is_favorite=request.is_favorite,
        bookmarked_at=datetime.utcnow()
    )

    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)

    return BookmarkResponse.model_validate(bookmark)


@router.get("", response_model=BookmarkListResponse)
async def list_bookmarks(
    folder: Optional[str] = Query(None, description="Filter by folder"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    is_favorite: Optional[bool] = Query(None, description="Filter favorites"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List bookmarks for the current user.

    Supports filtering by folder, tag, favorites, and full-text search.
    Results ordered by bookmarked_at descending (newest first).
    """
    query = db.query(Bookmark).filter(
        and_(
            Bookmark.user_id == current_user.id,
            Bookmark.deleted_at.is_(None)
        )
    )

    if folder:
        query = query.filter(Bookmark.folder == folder)

    if tag:
        query = query.filter(Bookmark.tags.contains([tag]))

    if is_favorite is not None:
        query = query.filter(Bookmark.is_favorite == is_favorite)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            Bookmark.title.ilike(search_pattern) |
            Bookmark.description.ilike(search_pattern)
        )

    total = query.count()

    offset = (page - 1) * page_size
    items = query.order_by(Bookmark.bookmarked_at.desc()).offset(offset).limit(page_size).all()

    return BookmarkListResponse(
        items=[BookmarkResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{bookmark_id}", response_model=BookmarkResponse)
async def get_bookmark(
    bookmark_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific bookmark by ID."""
    bookmark = db.query(Bookmark).filter(
        and_(
            Bookmark.id == bookmark_id,
            Bookmark.user_id == current_user.id,
            Bookmark.deleted_at.is_(None)
        )
    ).first()

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )

    return BookmarkResponse.model_validate(bookmark)


@router.patch("/{bookmark_id}", response_model=BookmarkResponse)
async def update_bookmark(
    bookmark_id: UUID,
    request: BookmarkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update bookmark metadata.

    Can update title, description, folder, tags, and favorite status.
    """
    bookmark = db.query(Bookmark).filter(
        and_(
            Bookmark.id == bookmark_id,
            Bookmark.user_id == current_user.id,
            Bookmark.deleted_at.is_(None)
        )
    ).first()

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )

    if request.title is not None:
        bookmark.title = request.title
    if request.description is not None:
        bookmark.description = request.description
    if request.folder is not None:
        bookmark.folder = request.folder
    if request.tags is not None:
        bookmark.tags = request.tags
    if request.is_favorite is not None:
        bookmark.is_favorite = request.is_favorite

    db.commit()
    db.refresh(bookmark)

    return BookmarkResponse.model_validate(bookmark)


@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(
    bookmark_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a bookmark."""
    bookmark = db.query(Bookmark).filter(
        and_(
            Bookmark.id == bookmark_id,
            Bookmark.user_id == current_user.id,
            Bookmark.deleted_at.is_(None)
        )
    ).first()

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )

    bookmark.soft_delete()
    db.commit()

    return None


@router.post("/{bookmark_id}/visit", response_model=BookmarkResponse)
async def record_visit(
    bookmark_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Record a visit to the bookmarked page.

    Increments visit_count and updates last_visited_at timestamp.
    """
    bookmark = db.query(Bookmark).filter(
        and_(
            Bookmark.id == bookmark_id,
            Bookmark.user_id == current_user.id,
            Bookmark.deleted_at.is_(None)
        )
    ).first()

    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )

    bookmark.visit_count += 1
    bookmark.last_visited_at = datetime.utcnow()

    db.commit()
    db.refresh(bookmark)

    return BookmarkResponse.model_validate(bookmark)


@router.get("/folders/list", response_model=List[str])
async def list_folders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all folders used in bookmarks.

    Returns distinct folder names for organizational purposes.
    """
    folders = db.query(Bookmark.folder).filter(
        and_(
            Bookmark.user_id == current_user.id,
            Bookmark.deleted_at.is_(None),
            Bookmark.folder.isnot(None)
        )
    ).distinct().all()

    return [folder[0] for folder in folders]


@router.get("/tags/list", response_model=List[str])
async def list_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all tags used in bookmarks.

    Returns distinct tags for filtering and organization.
    """
    from sqlalchemy import func

    # Query all tags arrays and flatten them
    tags_arrays = db.query(Bookmark.tags).filter(
        and_(
            Bookmark.user_id == current_user.id,
            Bookmark.deleted_at.is_(None),
            Bookmark.tags.isnot(None)
        )
    ).all()

    # Flatten and deduplicate
    all_tags = set()
    for tags_array in tags_arrays:
        if tags_array[0]:
            all_tags.update(tags_array[0])

    return sorted(list(all_tags))
