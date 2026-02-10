"""
Notifications API Routes

Provides CRUD operations for notification management including
system notifications, alerts, reminders, and message notifications.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.notification import Notification


router = APIRouter()


# Pydantic Models for Request/Response
class NotificationCreate(BaseModel):
    notification_type: str = Field(..., description="system, alert, reminder, message, update, marketing")
    title: str = Field(..., max_length=300)
    message: str = Field(..., max_length=1000)
    priority: str = Field(default="normal", description="low, normal, high, urgent")
    category: Optional[str] = Field(None, max_length=100)
    action_url: Optional[str] = Field(None, description="URL to navigate when notification is clicked")
    action_label: Optional[str] = Field(None, max_length=100)
    related_object_type: Optional[str] = Field(None, max_length=100, description="e.g., email, task, document")
    related_object_id: Optional[UUID] = Field(None, description="ID of related object")
    scheduled_for: Optional[datetime] = Field(None, description="When to send/display this notification")
    expires_at: Optional[datetime] = Field(None, description="When notification becomes irrelevant")


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_archived: Optional[bool] = None


class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    notification_type: str
    title: str
    message: str
    priority: str
    category: Optional[str]
    action_url: Optional[str]
    action_label: Optional[str]
    related_object_type: Optional[str]
    related_object_id: Optional[UUID]
    is_read: bool
    is_archived: bool
    read_at: Optional[datetime]
    scheduled_for: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    items: List[NotificationResponse]
    total: int
    unread_count: int
    page: int
    page_size: int
    pages: int


class NotificationStats(BaseModel):
    total: int
    unread: int
    by_type: dict
    by_priority: dict


# Endpoints
@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new notification."""
    notification = Notification(
        user_id=current_user.id,
        **notification_data.dict()
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    notification_type: Optional[str] = Query(None, description="Filter by notification type"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    is_archived: Optional[bool] = Query(None, description="Filter by archive status"),
    unread_only: bool = Query(False, description="Show only unread notifications"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List notifications with optional filtering."""
    query = db.query(Notification).filter(
        and_(
            Notification.user_id == current_user.id,
            Notification.deleted_at.is_(None)
        )
    )

    # Filter out expired notifications
    query = query.filter(
        or_(
            Notification.expires_at.is_(None),
            Notification.expires_at > datetime.utcnow()
        )
    )

    # Filter out scheduled future notifications
    query = query.filter(
        or_(
            Notification.scheduled_for.is_(None),
            Notification.scheduled_for <= datetime.utcnow()
        )
    )

    if notification_type:
        query = query.filter(Notification.notification_type == notification_type)

    if priority:
        query = query.filter(Notification.priority == priority)

    if category:
        query = query.filter(Notification.category == category)

    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)

    if is_archived is not None:
        query = query.filter(Notification.is_archived == is_archived)

    if unread_only:
        query = query.filter(Notification.is_read == False)

    total = query.count()

    # Count unread
    unread_count = db.query(Notification).filter(
        and_(
            Notification.user_id == current_user.id,
            Notification.deleted_at.is_(None),
            Notification.is_read == False,
            or_(
                Notification.expires_at.is_(None),
                Notification.expires_at > datetime.utcnow()
            )
        )
    ).count()

    # Order by priority (urgent -> high -> normal -> low), then created_at descending
    priority_order = {
        'urgent': 0,
        'high': 1,
        'normal': 2,
        'low': 3
    }

    from sqlalchemy import case
    priority_case = case(
        (Notification.priority == 'urgent', 0),
        (Notification.priority == 'high', 1),
        (Notification.priority == 'normal', 2),
        (Notification.priority == 'low', 3),
        else_=4
    )

    query = query.order_by(
        Notification.is_read.asc(),  # Unread first
        priority_case,
        Notification.created_at.desc()
    )

    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    pages = (total + page_size - 1) // page_size

    return NotificationListResponse(
        items=items,
        total=total,
        unread_count=unread_count,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get notification statistics for the user."""
    from sqlalchemy import func

    base_query = db.query(Notification).filter(
        and_(
            Notification.user_id == current_user.id,
            Notification.deleted_at.is_(None),
            or_(
                Notification.expires_at.is_(None),
                Notification.expires_at > datetime.utcnow()
            )
        )
    )

    total = base_query.count()
    unread = base_query.filter(Notification.is_read == False).count()

    # By type
    by_type_results = db.query(
        Notification.notification_type,
        func.count(Notification.id).label('count')
    ).filter(
        and_(
            Notification.user_id == current_user.id,
            Notification.deleted_at.is_(None),
            or_(
                Notification.expires_at.is_(None),
                Notification.expires_at > datetime.utcnow()
            )
        )
    ).group_by(Notification.notification_type).all()

    by_type = {row.notification_type: row.count for row in by_type_results}

    # By priority
    by_priority_results = db.query(
        Notification.priority,
        func.count(Notification.id).label('count')
    ).filter(
        and_(
            Notification.user_id == current_user.id,
            Notification.deleted_at.is_(None),
            or_(
                Notification.expires_at.is_(None),
                Notification.expires_at > datetime.utcnow()
            )
        )
    ).group_by(Notification.priority).all()

    by_priority = {row.priority: row.count for row in by_priority_results}

    return NotificationStats(
        total=total,
        unread=unread,
        by_type=by_type,
        by_priority=by_priority
    )


@router.post("/mark-all-read", response_model=dict)
async def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark all notifications as read."""
    updated_count = db.query(Notification).filter(
        and_(
            Notification.user_id == current_user.id,
            Notification.deleted_at.is_(None),
            Notification.is_read == False
        )
    ).update({
        "is_read": True,
        "read_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

    db.commit()

    return {"marked_read": updated_count}


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific notification by ID."""
    notification = db.query(Notification).filter(
        and_(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
            Notification.deleted_at.is_(None)
        )
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return notification


@router.patch("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: UUID,
    notification_data: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a notification (mark as read/unread, archive/unarchive)."""
    notification = db.query(Notification).filter(
        and_(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
            Notification.deleted_at.is_(None)
        )
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    update_data = notification_data.dict(exclude_unset=True)

    # If marking as read, set read_at timestamp
    if update_data.get("is_read") == True and not notification.is_read:
        notification.read_at = datetime.utcnow()

    # If marking as unread, clear read_at
    if update_data.get("is_read") == False:
        notification.read_at = None

    for field, value in update_data.items():
        setattr(notification, field, value)

    notification.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(notification)

    return notification


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a notification."""
    notification = db.query(Notification).filter(
        and_(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
            Notification.deleted_at.is_(None)
        )
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    notification.deleted_at = datetime.utcnow()
    db.commit()

    return None
