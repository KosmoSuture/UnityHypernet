"""
Profile Attributes API Routes

Provides CRUD operations for user profile attributes including
preferences, settings, skills, interests, and custom data fields.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List, Any, Dict
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.profile_attribute import ProfileAttribute


router = APIRouter()


# Pydantic Models for Request/Response
class ProfileAttributeCreate(BaseModel):
    attribute_type: str = Field(..., description="preference, skill, interest, certification, education, work_experience, custom")
    key: str = Field(..., max_length=200, description="Attribute key/name")
    value: Any = Field(..., description="Attribute value (can be string, number, boolean, object)")
    category: Optional[str] = Field(None, max_length=100)
    is_public: bool = Field(default=False, description="Whether this attribute is publicly visible")
    is_verified: bool = Field(default=False, description="Whether this attribute has been verified")
    verification_source: Optional[str] = Field(None, max_length=200)
    priority: int = Field(default=0, description="Display priority (higher = more important)")
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class ProfileAttributeUpdate(BaseModel):
    value: Optional[Any] = None
    category: Optional[str] = Field(None, max_length=100)
    is_public: Optional[bool] = None
    is_verified: Optional[bool] = None
    verification_source: Optional[str] = Field(None, max_length=200)
    priority: Optional[int] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class ProfileAttributeResponse(BaseModel):
    id: UUID
    user_id: UUID
    attribute_type: str
    key: str
    value: Any
    category: Optional[str]
    is_public: bool
    is_verified: bool
    verification_source: Optional[str]
    priority: int
    tags: List[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProfileAttributeListResponse(BaseModel):
    items: List[ProfileAttributeResponse]
    total: int
    page: int
    page_size: int
    pages: int


class ProfileSummary(BaseModel):
    """Summary of profile attributes grouped by type."""
    attribute_type: str
    count: int
    public_count: int
    verified_count: int


# Endpoints
@router.post("", response_model=ProfileAttributeResponse, status_code=status.HTTP_201_CREATED)
async def create_profile_attribute(
    attribute_data: ProfileAttributeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new profile attribute."""
    attribute = ProfileAttribute(
        user_id=current_user.id,
        **attribute_data.dict()
    )
    db.add(attribute)
    db.commit()
    db.refresh(attribute)
    return attribute


@router.get("", response_model=ProfileAttributeListResponse)
async def list_profile_attributes(
    attribute_type: Optional[str] = Query(None, description="Filter by attribute type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_public: Optional[bool] = Query(None, description="Filter by public visibility"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    search: Optional[str] = Query(None, description="Search in key, value, notes"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List profile attributes with optional filtering."""
    query = db.query(ProfileAttribute).filter(
        and_(
            ProfileAttribute.user_id == current_user.id,
            ProfileAttribute.deleted_at.is_(None)
        )
    )

    if attribute_type:
        query = query.filter(ProfileAttribute.attribute_type == attribute_type)

    if category:
        query = query.filter(ProfileAttribute.category == category)

    if is_public is not None:
        query = query.filter(ProfileAttribute.is_public == is_public)

    if is_verified is not None:
        query = query.filter(ProfileAttribute.is_verified == is_verified)

    if tag:
        query = query.filter(ProfileAttribute.tags.contains([tag]))

    if search:
        search_pattern = f"%{search}%"
        # Convert value JSONB to text for searching
        from sqlalchemy import cast, Text
        query = query.filter(
            or_(
                ProfileAttribute.key.ilike(search_pattern),
                cast(ProfileAttribute.value, Text).ilike(search_pattern),
                ProfileAttribute.notes.ilike(search_pattern)
            )
        )

    total = query.count()

    # Order by priority descending, then created_at
    query = query.order_by(
        ProfileAttribute.priority.desc(),
        ProfileAttribute.created_at.desc()
    )

    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    pages = (total + page_size - 1) // page_size

    return ProfileAttributeListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/summary", response_model=List[ProfileSummary])
async def get_profile_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get summary of profile attributes grouped by type."""
    from sqlalchemy import func, case

    results = db.query(
        ProfileAttribute.attribute_type,
        func.count(ProfileAttribute.id).label('count'),
        func.sum(case((ProfileAttribute.is_public == True, 1), else_=0)).label('public_count'),
        func.sum(case((ProfileAttribute.is_verified == True, 1), else_=0)).label('verified_count')
    ).filter(
        and_(
            ProfileAttribute.user_id == current_user.id,
            ProfileAttribute.deleted_at.is_(None)
        )
    ).group_by(ProfileAttribute.attribute_type).all()

    return [
        ProfileSummary(
            attribute_type=row.attribute_type,
            count=row.count,
            public_count=row.public_count or 0,
            verified_count=row.verified_count or 0
        )
        for row in results
    ]


@router.get("/public", response_model=ProfileAttributeListResponse)
async def list_public_attributes(
    user_id: UUID = Query(..., description="User ID to get public attributes for"),
    attribute_type: Optional[str] = Query(None, description="Filter by attribute type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    List public profile attributes for any user.
    This endpoint doesn't require authentication and only returns public attributes.
    """
    query = db.query(ProfileAttribute).filter(
        and_(
            ProfileAttribute.user_id == user_id,
            ProfileAttribute.deleted_at.is_(None),
            ProfileAttribute.is_public == True
        )
    )

    if attribute_type:
        query = query.filter(ProfileAttribute.attribute_type == attribute_type)

    total = query.count()

    query = query.order_by(
        ProfileAttribute.priority.desc(),
        ProfileAttribute.created_at.desc()
    )

    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    pages = (total + page_size - 1) // page_size

    return ProfileAttributeListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/categories", response_model=List[str])
async def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all unique categories from user's profile attributes."""
    categories = db.query(ProfileAttribute.category).filter(
        and_(
            ProfileAttribute.user_id == current_user.id,
            ProfileAttribute.deleted_at.is_(None),
            ProfileAttribute.category.isnot(None)
        )
    ).distinct().order_by(ProfileAttribute.category).all()

    return [cat[0] for cat in categories if cat[0]]


@router.get("/{attribute_id}", response_model=ProfileAttributeResponse)
async def get_profile_attribute(
    attribute_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific profile attribute by ID."""
    attribute = db.query(ProfileAttribute).filter(
        and_(
            ProfileAttribute.id == attribute_id,
            ProfileAttribute.user_id == current_user.id,
            ProfileAttribute.deleted_at.is_(None)
        )
    ).first()

    if not attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile attribute not found"
        )

    return attribute


@router.patch("/{attribute_id}", response_model=ProfileAttributeResponse)
async def update_profile_attribute(
    attribute_id: UUID,
    attribute_data: ProfileAttributeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a profile attribute."""
    attribute = db.query(ProfileAttribute).filter(
        and_(
            ProfileAttribute.id == attribute_id,
            ProfileAttribute.user_id == current_user.id,
            ProfileAttribute.deleted_at.is_(None)
        )
    ).first()

    if not attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile attribute not found"
        )

    update_data = attribute_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(attribute, field, value)

    attribute.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(attribute)

    return attribute


@router.delete("/{attribute_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile_attribute(
    attribute_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a profile attribute."""
    attribute = db.query(ProfileAttribute).filter(
        and_(
            ProfileAttribute.id == attribute_id,
            ProfileAttribute.user_id == current_user.id,
            ProfileAttribute.deleted_at.is_(None)
        )
    ).first()

    if not attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile attribute not found"
        )

    attribute.deleted_at = datetime.utcnow()
    db.commit()

    return None
