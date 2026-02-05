"""
Media Routes

Endpoints for media upload, retrieval, and management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.media import Media

router = APIRouter()


# Request/Response Models
class MediaCreate(BaseModel):
    """Media creation request"""
    media_type: str = Field(..., description="photo, video, audio, document, screenshot")
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    file_path: str = Field(..., max_length=512)
    file_size: int = Field(..., ge=0)
    mime_type: str = Field(..., max_length=100)
    width: Optional[int] = Field(None, ge=0)
    height: Optional[int] = Field(None, ge=0)
    duration: Optional[int] = Field(None, ge=0)
    taken_at: Optional[datetime] = None
    gps_latitude: Optional[float] = Field(None, ge=-90, le=90)
    gps_longitude: Optional[float] = Field(None, ge=-180, le=180)


class MediaUpdate(BaseModel):
    """Media update request"""
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_favorite: Optional[bool] = None


class MediaResponse(BaseModel):
    """Media response"""
    id: str
    user_id: str
    media_type: str
    title: Optional[str]
    description: Optional[str]
    file_path: str
    file_size: int
    mime_type: str
    width: Optional[int]
    height: Optional[int]
    duration: Optional[int]
    taken_at: Optional[datetime]
    created_at: datetime
    is_favorite: bool
    tags: Optional[List[str]]

    class Config:
        from_attributes = True


class MediaListResponse(BaseModel):
    """Paginated media list response"""
    items: List[MediaResponse]
    total: int
    page: int
    page_size: int


@router.post("", response_model=MediaResponse, status_code=status.HTTP_201_CREATED)
async def create_media(
    request: MediaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new media record.

    This endpoint creates a media database record. File upload should be handled
    separately by the upload endpoint.

    - **media_type**: photo, video, audio, document, screenshot
    - **file_path**: Path where the file is stored
    - **file_size**: Size in bytes
    - **mime_type**: MIME type (e.g., image/jpeg)
    """
    # Create media object
    media = Media(
        user_id=current_user.id,
        media_type=request.media_type,
        title=request.title,
        description=request.description,
        file_path=request.file_path,
        file_size=request.file_size,
        mime_type=request.mime_type,
        width=request.width,
        height=request.height,
        duration=request.duration,
        taken_at=request.taken_at,
        gps_latitude=request.gps_latitude,
        gps_longitude=request.gps_longitude,
        processing_status='ready'
    )

    db.add(media)
    db.commit()
    db.refresh(media)

    return MediaResponse.model_validate(media)


@router.get("", response_model=MediaListResponse)
async def list_media(
    media_type: Optional[str] = Query(None, description="Filter by media type"),
    is_favorite: Optional[bool] = Query(None, description="Filter favorites"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List media items for the current user.

    Supports filtering by:
    - **media_type**: photo, video, audio, document, screenshot
    - **is_favorite**: true/false
    - **tag**: Search for media with specific tag
    - Pagination with page and page_size
    """
    # Build query
    query = db.query(Media).filter(
        and_(
            Media.user_id == current_user.id,
            Media.deleted_at.is_(None)
        )
    )

    # Apply filters
    if media_type:
        query = query.filter(Media.media_type == media_type)

    if is_favorite is not None:
        query = query.filter(Media.is_favorite == is_favorite)

    if tag:
        query = query.filter(Media.tags.contains([tag]))

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    items = query.order_by(Media.created_at.desc()).offset(offset).limit(page_size).all()

    return MediaListResponse(
        items=[MediaResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{media_id}", response_model=MediaResponse)
async def get_media(
    media_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific media item by ID.

    Returns full media details including metadata.
    """
    media = db.query(Media).filter(
        and_(
            Media.id == media_id,
            Media.user_id == current_user.id,
            Media.deleted_at.is_(None)
        )
    ).first()

    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )

    return MediaResponse.model_validate(media)


@router.patch("/{media_id}", response_model=MediaResponse)
async def update_media(
    media_id: UUID,
    request: MediaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update media metadata.

    Can update:
    - **title**: Media title
    - **description**: Media description
    - **tags**: List of tags
    - **is_favorite**: Favorite status
    """
    media = db.query(Media).filter(
        and_(
            Media.id == media_id,
            Media.user_id == current_user.id,
            Media.deleted_at.is_(None)
        )
    ).first()

    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )

    # Update fields
    if request.title is not None:
        media.title = request.title
    if request.description is not None:
        media.description = request.description
    if request.tags is not None:
        media.tags = request.tags
    if request.is_favorite is not None:
        media.is_favorite = request.is_favorite

    db.commit()
    db.refresh(media)

    return MediaResponse.model_validate(media)


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    media_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Soft delete a media item.

    The media is not permanently deleted, just marked as deleted
    and can be restored later.
    """
    media = db.query(Media).filter(
        and_(
            Media.id == media_id,
            Media.user_id == current_user.id,
            Media.deleted_at.is_(None)
        )
    ).first()

    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )

    # Soft delete
    media.soft_delete()
    db.commit()

    return None


@router.post("/{media_id}/restore", response_model=MediaResponse)
async def restore_media(
    media_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Restore a soft-deleted media item.

    Brings back a media item that was previously deleted.
    """
    media = db.query(Media).filter(
        and_(
            Media.id == media_id,
            Media.user_id == current_user.id,
            Media.deleted_at.isnot(None)
        )
    ).first()

    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deleted media not found"
        )

    # Restore
    media.restore()
    db.commit()
    db.refresh(media)

    return MediaResponse.model_validate(media)
