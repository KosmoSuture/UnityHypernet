"""
Social Accounts Routes

Endpoints for managing social media account profiles.
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
from app.models.social_account import SocialAccount

router = APIRouter()


# Request/Response Models
class SocialAccountCreate(BaseModel):
    """Social account creation request"""
    platform: str = Field(..., description="instagram, twitter, facebook, tiktok, linkedin")
    username: str = Field(..., max_length=100)
    account_type: str = Field(..., description="own, following, other")
    display_name: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = None
    profile_url: Optional[str] = Field(None, max_length=500)
    profile_photo_url: Optional[str] = Field(None, max_length=500)
    followers_count: Optional[int] = Field(None, ge=0)
    following_count: Optional[int] = Field(None, ge=0)
    posts_count: Optional[int] = Field(None, ge=0)
    is_verified: bool = Field(default=False)


class SocialAccountUpdate(BaseModel):
    """Social account update request"""
    display_name: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = None
    profile_url: Optional[str] = Field(None, max_length=500)
    profile_photo_url: Optional[str] = Field(None, max_length=500)
    followers_count: Optional[int] = Field(None, ge=0)
    following_count: Optional[int] = Field(None, ge=0)
    posts_count: Optional[int] = Field(None, ge=0)
    is_verified: Optional[bool] = None


class SocialAccountResponse(BaseModel):
    """Social account response"""
    id: str
    user_id: str
    platform: str
    username: str
    account_type: str
    display_name: Optional[str]
    bio: Optional[str]
    profile_url: Optional[str]
    profile_photo_url: Optional[str]
    followers_count: Optional[int]
    following_count: Optional[int]
    posts_count: Optional[int]
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SocialAccountListResponse(BaseModel):
    """Paginated social account list response"""
    items: List[SocialAccountResponse]
    total: int
    page: int
    page_size: int


@router.post("", response_model=SocialAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_social_account(
    request: SocialAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new social account record.

    - **platform**: instagram, twitter, facebook, tiktok, linkedin (required)
    - **username**: Account username/handle (required)
    - **account_type**: own, following, other (required)
    - **display_name**: Display name on the platform
    - **bio**: Account bio/description
    - **followers_count**: Number of followers
    - **following_count**: Number of accounts following
    """
    account = SocialAccount(
        user_id=current_user.id,
        platform=request.platform,
        username=request.username,
        account_type=request.account_type,
        display_name=request.display_name,
        bio=request.bio,
        profile_url=request.profile_url,
        profile_photo_url=request.profile_photo_url,
        followers_count=request.followers_count,
        following_count=request.following_count,
        posts_count=request.posts_count,
        is_verified=request.is_verified
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return SocialAccountResponse.model_validate(account)


@router.get("", response_model=SocialAccountListResponse)
async def list_social_accounts(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    account_type: Optional[str] = Query(None, description="Filter by account type"),
    is_verified: Optional[bool] = Query(None, description="Filter verified accounts"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List social accounts for the current user.

    Supports:
    - Filter by platform (instagram, twitter, facebook, tiktok, linkedin)
    - Filter by account_type (own, following, other)
    - Filter verified accounts
    - Pagination

    Results ordered by platform, then username.
    """
    query = db.query(SocialAccount).filter(
        and_(
            SocialAccount.user_id == current_user.id,
            SocialAccount.deleted_at.is_(None)
        )
    )

    if platform:
        query = query.filter(SocialAccount.platform == platform)

    if account_type:
        query = query.filter(SocialAccount.account_type == account_type)

    if is_verified is not None:
        query = query.filter(SocialAccount.is_verified == is_verified)

    total = query.count()

    offset = (page - 1) * page_size
    items = query.order_by(
        SocialAccount.platform.asc(),
        SocialAccount.username.asc()
    ).offset(offset).limit(page_size).all()

    return SocialAccountListResponse(
        items=[SocialAccountResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{account_id}", response_model=SocialAccountResponse)
async def get_social_account(
    account_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific social account by ID."""
    account = db.query(SocialAccount).filter(
        and_(
            SocialAccount.id == account_id,
            SocialAccount.user_id == current_user.id,
            SocialAccount.deleted_at.is_(None)
        )
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Social account not found"
        )

    return SocialAccountResponse.model_validate(account)


@router.patch("/{account_id}", response_model=SocialAccountResponse)
async def update_social_account(
    account_id: UUID,
    request: SocialAccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update social account metadata.

    Typically used to update follower counts and profile information
    when syncing from the platform.
    """
    account = db.query(SocialAccount).filter(
        and_(
            SocialAccount.id == account_id,
            SocialAccount.user_id == current_user.id,
            SocialAccount.deleted_at.is_(None)
        )
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Social account not found"
        )

    if request.display_name is not None:
        account.display_name = request.display_name
    if request.bio is not None:
        account.bio = request.bio
    if request.profile_url is not None:
        account.profile_url = request.profile_url
    if request.profile_photo_url is not None:
        account.profile_photo_url = request.profile_photo_url
    if request.followers_count is not None:
        account.followers_count = request.followers_count
    if request.following_count is not None:
        account.following_count = request.following_count
    if request.posts_count is not None:
        account.posts_count = request.posts_count
    if request.is_verified is not None:
        account.is_verified = request.is_verified

    db.commit()
    db.refresh(account)

    return SocialAccountResponse.model_validate(account)


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_social_account(
    account_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a social account."""
    account = db.query(SocialAccount).filter(
        and_(
            SocialAccount.id == account_id,
            SocialAccount.user_id == current_user.id,
            SocialAccount.deleted_at.is_(None)
        )
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Social account not found"
        )

    account.soft_delete()
    db.commit()

    return None
