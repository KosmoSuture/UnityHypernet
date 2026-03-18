"""
Calendar Events Routes

Endpoints for managing calendar events and appointments.
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
from app.models.calendar_event import CalendarEvent

router = APIRouter()


# Request/Response Models
class CalendarEventCreate(BaseModel):
    """Calendar event creation request"""
    title: str = Field(..., max_length=500)
    starts_at: datetime
    ends_at: Optional[datetime] = None
    event_type: str = Field(default='event', description="event, meeting, appointment, reminder")
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=500)
    meeting_url: Optional[str] = Field(None, max_length=500)
    is_all_day: bool = Field(default=False)
    is_recurring: bool = Field(default=False)
    recurrence_rule: Optional[str] = Field(None, max_length=500)
    attendees: Optional[List[str]] = None


class CalendarEventUpdate(BaseModel):
    """Calendar event update request"""
    title: Optional[str] = Field(None, max_length=500)
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    event_type: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=500)
    meeting_url: Optional[str] = Field(None, max_length=500)
    is_all_day: Optional[bool] = None
    is_recurring: Optional[bool] = None
    recurrence_rule: Optional[str] = Field(None, max_length=500)
    attendees: Optional[List[str]] = None


class CalendarEventResponse(BaseModel):
    """Calendar event response"""
    id: str
    user_id: str
    title: str
    starts_at: datetime
    ends_at: Optional[datetime]
    event_type: str
    description: Optional[str]
    location: Optional[str]
    meeting_url: Optional[str]
    is_all_day: bool
    is_recurring: bool
    recurrence_rule: Optional[str]
    attendees: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CalendarEventListResponse(BaseModel):
    """Paginated calendar event list response"""
    items: List[CalendarEventResponse]
    total: int
    page: int
    page_size: int


@router.post("", response_model=CalendarEventResponse, status_code=status.HTTP_201_CREATED)
async def create_calendar_event(
    request: CalendarEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new calendar event.

    - **title**: Event title (required)
    - **starts_at**: Event start time (required)
    - **ends_at**: Event end time
    - **event_type**: event, meeting, appointment, reminder
    - **location**: Physical location or address
    - **meeting_url**: Video meeting URL (Zoom, Teams, etc.)
    """
    event = CalendarEvent(
        user_id=current_user.id,
        title=request.title,
        starts_at=request.starts_at,
        ends_at=request.ends_at,
        event_type=request.event_type,
        description=request.description,
        location=request.location,
        meeting_url=request.meeting_url,
        is_all_day=request.is_all_day,
        is_recurring=request.is_recurring,
        recurrence_rule=request.recurrence_rule,
        attendees=request.attendees
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return CalendarEventResponse.model_validate(event)


@router.get("", response_model=CalendarEventListResponse)
async def list_calendar_events(
    start_date: Optional[datetime] = Query(None, description="Filter events starting after this date"),
    end_date: Optional[datetime] = Query(None, description="Filter events ending before this date"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List calendar events for the current user.

    Supports:
    - Filter by date range (start_date, end_date)
    - Filter by event_type
    - Pagination

    Results ordered by starts_at ascending (soonest first).
    """
    query = db.query(CalendarEvent).filter(
        and_(
            CalendarEvent.user_id == current_user.id,
            CalendarEvent.deleted_at.is_(None)
        )
    )

    if start_date:
        query = query.filter(CalendarEvent.starts_at >= start_date)

    if end_date:
        query = query.filter(CalendarEvent.starts_at <= end_date)

    if event_type:
        query = query.filter(CalendarEvent.event_type == event_type)

    total = query.count()

    offset = (page - 1) * page_size
    items = query.order_by(CalendarEvent.starts_at.asc()).offset(offset).limit(page_size).all()

    return CalendarEventListResponse(
        items=[CalendarEventResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{event_id}", response_model=CalendarEventResponse)
async def get_calendar_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific calendar event by ID."""
    event = db.query(CalendarEvent).filter(
        and_(
            CalendarEvent.id == event_id,
            CalendarEvent.user_id == current_user.id,
            CalendarEvent.deleted_at.is_(None)
        )
    ).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar event not found"
        )

    return CalendarEventResponse.model_validate(event)


@router.patch("/{event_id}", response_model=CalendarEventResponse)
async def update_calendar_event(
    event_id: UUID,
    request: CalendarEventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a calendar event.

    All fields are optional. Only provided fields will be updated.
    """
    event = db.query(CalendarEvent).filter(
        and_(
            CalendarEvent.id == event_id,
            CalendarEvent.user_id == current_user.id,
            CalendarEvent.deleted_at.is_(None)
        )
    ).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar event not found"
        )

    if request.title is not None:
        event.title = request.title
    if request.starts_at is not None:
        event.starts_at = request.starts_at
    if request.ends_at is not None:
        event.ends_at = request.ends_at
    if request.event_type is not None:
        event.event_type = request.event_type
    if request.description is not None:
        event.description = request.description
    if request.location is not None:
        event.location = request.location
    if request.meeting_url is not None:
        event.meeting_url = request.meeting_url
    if request.is_all_day is not None:
        event.is_all_day = request.is_all_day
    if request.is_recurring is not None:
        event.is_recurring = request.is_recurring
    if request.recurrence_rule is not None:
        event.recurrence_rule = request.recurrence_rule
    if request.attendees is not None:
        event.attendees = request.attendees

    db.commit()
    db.refresh(event)

    return CalendarEventResponse.model_validate(event)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_calendar_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a calendar event."""
    event = db.query(CalendarEvent).filter(
        and_(
            CalendarEvent.id == event_id,
            CalendarEvent.user_id == current_user.id,
            CalendarEvent.deleted_at.is_(None)
        )
    ).first()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calendar event not found"
        )

    event.soft_delete()
    db.commit()

    return None
