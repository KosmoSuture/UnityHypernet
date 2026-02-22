"""
Social Post Routes

Endpoints for managing social media posts from Instagram, Twitter, etc.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.social_post import SocialPost

router = APIRouter()


# Request/Response Models
class SocialPostCreate(BaseModel):
    """Social post creation request"""
    platform: str = Field(..., description="instagram, twitter, facebook, tiktok, linkedin")
    post_type: str = Field(..., description="text, photo, video, story, reel, carousel")
    content: str = Field(default='')
    posted_at: datetime
    platform_post_id: Optional[str] = Field(None, max_length=255)
    platform_url: Optional[str] = Field(None, max_length=500)
    likes_count: Optional[int] = Field(None, ge=0)
    comments_count: Optional[int] = Field(None, ge=0)
    shares_count: Optional[int] = Field(None, ge=0)
    views_count: Optional[int] = Field(None, ge=0)
    visibility: Optional[str] = Field(None, description="public, private, friends, followers")
    location: Optional[str] = Field(None, max_length=200)


class SocialPostUpdate(BaseModel):
    """Social post update request"""
    content: Optional[str] = None
    likes_count: Optional[int] = Field(None, ge=0)
    comments_count: Optional[int] = Field(None, ge=0)
    shares_count: Optional[int] = Field(None, ge=0)
    views_count: Optional[int] = Field(None, ge=0)
    is_pinned: Optional[bool] = None


class SocialPostResponse(BaseModel):
    """Social post response"""
    id: str
    user_id: str
    platform: str
    post_type: str
    content: str
    posted_at: datetime
    platform_post_id: Optional[str]
    platform_url: Optional[str]
    likes_count: Optional[int]
    comments_count: Optional[int]
    shares_count: Optional[int]
    views_count: Optional[int]
    visibility: Optional[str]
    is_pinned: bool
    location: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SocialPostListResponse(BaseModel):
    """Paginated social post list response"""
    items: List[SocialPostResponse]
    total: int
    page: int
    page_size: int


@router.post("", response_model=SocialPostResponse, status_code=status.HTTP_201_CREATED)
async def create_social_post(
    request: SocialPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new social post record.

    Typically used when importing posts from social media platforms.

    - **platform**: instagram, twitter, facebook, tiktok, linkedin
    - **post_type**: text, photo, video, story, reel, carousel
    - **content**: Post text content
    - **posted_at**: When the post was published on the platform
    """
    post = SocialPost(
        user_id=current_user.id,
        platform=request.platform,
        post_type=request.post_type,
        content=request.content,
        posted_at=request.posted_at,
        platform_post_id=request.platform_post_id,
        platform_url=request.platform_url,
        likes_count=request.likes_count,
        comments_count=request.comments_count,
        shares_count=request.shares_count,
        views_count=request.views_count,
        visibility=request.visibility,
        location=request.location
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return SocialPostResponse.model_validate(post)


@router.get("", response_model=SocialPostListResponse)
async def list_social_posts(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    post_type: Optional[str] = Query(None, description="Filter by post type"),
    is_pinned: Optional[bool] = Query(None, description="Filter pinned posts"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List social posts for the current user.

    Supports filtering by platform, post type, and pinned status.
    Results are ordered by posted_at descending (newest first).
    """
    query = db.query(SocialPost).filter(
        and_(
            SocialPost.user_id == current_user.id,
            SocialPost.deleted_at.is_(None)
        )
    )

    if platform:
        query = query.filter(SocialPost.platform == platform)

    if post_type:
        query = query.filter(SocialPost.post_type == post_type)

    if is_pinned is not None:
        query = query.filter(SocialPost.is_pinned == is_pinned)

    total = query.count()

    offset = (page - 1) * page_size
    items = query.order_by(SocialPost.posted_at.desc()).offset(offset).limit(page_size).all()

    return SocialPostListResponse(
        items=[SocialPostResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{post_id}", response_model=SocialPostResponse)
async def get_social_post(
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific social post by ID."""
    post = db.query(SocialPost).filter(
        and_(
            SocialPost.id == post_id,
            SocialPost.user_id == current_user.id,
            SocialPost.deleted_at.is_(None)
        )
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Social post not found"
        )

    return SocialPostResponse.model_validate(post)


@router.patch("/{post_id}", response_model=SocialPostResponse)
async def update_social_post(
    post_id: UUID,
    request: SocialPostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update social post metadata.

    Primarily used to update engagement metrics (likes, comments, shares, views)
    when syncing from the platform.
    """
    post = db.query(SocialPost).filter(
        and_(
            SocialPost.id == post_id,
            SocialPost.user_id == current_user.id,
            SocialPost.deleted_at.is_(None)
        )
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Social post not found"
        )

    if request.content is not None:
        post.content = request.content
    if request.likes_count is not None:
        post.likes_count = request.likes_count
    if request.comments_count is not None:
        post.comments_count = request.comments_count
    if request.shares_count is not None:
        post.shares_count = request.shares_count
    if request.views_count is not None:
        post.views_count = request.views_count
    if request.is_pinned is not None:
        post.is_pinned = request.is_pinned

    db.commit()
    db.refresh(post)

    return SocialPostResponse.model_validate(post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_social_post(
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a social post."""
    post = db.query(SocialPost).filter(
        and_(
            SocialPost.id == post_id,
            SocialPost.user_id == current_user.id,
            SocialPost.deleted_at.is_(None)
        )
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Social post not found"
        )

    post.soft_delete()
    db.commit()

    return None
