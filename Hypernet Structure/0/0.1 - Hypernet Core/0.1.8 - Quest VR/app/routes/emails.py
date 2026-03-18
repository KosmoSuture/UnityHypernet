"""
Emails Routes

Endpoints for managing email messages.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.email import Email

router = APIRouter()


# Request/Response Models
class EmailCreate(BaseModel):
    """Email creation request"""
    subject: str = Field(..., max_length=500)
    from_address: str = Field(..., max_length=255)
    to_addresses: List[str]
    cc_addresses: Optional[List[str]] = None
    bcc_addresses: Optional[List[str]] = None
    sent_at: datetime
    direction: str = Field(..., description="sent, received, draft")
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    thread_id: Optional[str] = Field(None, max_length=255)
    message_id: Optional[str] = Field(None, max_length=255)
    has_attachments: bool = Field(default=False)
    is_read: bool = Field(default=False)
    is_starred: bool = Field(default=False)


class EmailUpdate(BaseModel):
    """Email update request"""
    is_read: Optional[bool] = None
    is_starred: Optional[bool] = None


class EmailResponse(BaseModel):
    """Email response"""
    id: str
    user_id: str
    subject: str
    from_address: str
    to_addresses: List[str]
    cc_addresses: Optional[List[str]]
    bcc_addresses: Optional[List[str]]
    sent_at: datetime
    direction: str
    body_text: Optional[str]
    body_html: Optional[str]
    thread_id: Optional[str]
    message_id: Optional[str]
    has_attachments: bool
    is_read: bool
    is_starred: bool
    created_at: datetime

    class Config:
        from_attributes = True


class EmailListResponse(BaseModel):
    """Paginated email list response"""
    items: List[EmailResponse]
    total: int
    page: int
    page_size: int


@router.post("", response_model=EmailResponse, status_code=status.HTTP_201_CREATED)
async def create_email(
    request: EmailCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new email record.

    Typically used when importing emails from email providers.

    - **subject**: Email subject (required)
    - **from_address**: Sender email address (required)
    - **to_addresses**: Recipient email addresses (required)
    - **sent_at**: When email was sent (required)
    - **direction**: sent, received, or draft (required)
    """
    email = Email(
        user_id=current_user.id,
        subject=request.subject,
        from_address=request.from_address,
        to_addresses=request.to_addresses,
        cc_addresses=request.cc_addresses,
        bcc_addresses=request.bcc_addresses,
        sent_at=request.sent_at,
        direction=request.direction,
        body_text=request.body_text,
        body_html=request.body_html,
        thread_id=request.thread_id,
        message_id=request.message_id,
        has_attachments=request.has_attachments,
        is_read=request.is_read,
        is_starred=request.is_starred
    )

    db.add(email)
    db.commit()
    db.refresh(email)

    return EmailResponse.model_validate(email)


@router.get("", response_model=EmailListResponse)
async def list_emails(
    direction: Optional[str] = Query(None, description="Filter by direction: sent, received, draft"),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    is_starred: Optional[bool] = Query(None, description="Filter starred emails"),
    has_attachments: Optional[bool] = Query(None, description="Filter emails with attachments"),
    thread_id: Optional[str] = Query(None, description="Filter by thread ID"),
    search: Optional[str] = Query(None, description="Search in subject, from, to, body"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List emails for the current user.

    Supports:
    - Filter by direction (sent, received, draft)
    - Filter by read status
    - Filter starred emails
    - Filter emails with attachments
    - Filter by thread ID
    - Full-text search
    - Pagination

    Results ordered by sent_at descending (newest first).
    """
    query = db.query(Email).filter(
        and_(
            Email.user_id == current_user.id,
            Email.deleted_at.is_(None)
        )
    )

    if direction:
        query = query.filter(Email.direction == direction)

    if is_read is not None:
        query = query.filter(Email.is_read == is_read)

    if is_starred is not None:
        query = query.filter(Email.is_starred == is_starred)

    if has_attachments is not None:
        query = query.filter(Email.has_attachments == has_attachments)

    if thread_id:
        query = query.filter(Email.thread_id == thread_id)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Email.subject.ilike(search_pattern),
                Email.from_address.ilike(search_pattern),
                Email.body_text.ilike(search_pattern)
            )
        )

    total = query.count()

    offset = (page - 1) * page_size
    items = query.order_by(Email.sent_at.desc()).offset(offset).limit(page_size).all()

    return EmailListResponse(
        items=[EmailResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{email_id}", response_model=EmailResponse)
async def get_email(
    email_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific email by ID."""
    email = db.query(Email).filter(
        and_(
            Email.id == email_id,
            Email.user_id == current_user.id,
            Email.deleted_at.is_(None)
        )
    ).first()

    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )

    return EmailResponse.model_validate(email)


@router.patch("/{email_id}", response_model=EmailResponse)
async def update_email(
    email_id: UUID,
    request: EmailUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update email metadata.

    Can update read status and starred status.
    """
    email = db.query(Email).filter(
        and_(
            Email.id == email_id,
            Email.user_id == current_user.id,
            Email.deleted_at.is_(None)
        )
    ).first()

    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )

    if request.is_read is not None:
        email.is_read = request.is_read
    if request.is_starred is not None:
        email.is_starred = request.is_starred

    db.commit()
    db.refresh(email)

    return EmailResponse.model_validate(email)


@router.post("/{email_id}/mark-read", response_model=EmailResponse)
async def mark_email_read(
    email_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark an email as read."""
    email = db.query(Email).filter(
        and_(
            Email.id == email_id,
            Email.user_id == current_user.id,
            Email.deleted_at.is_(None)
        )
    ).first()

    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )

    email.is_read = True
    db.commit()
    db.refresh(email)

    return EmailResponse.model_validate(email)


@router.post("/{email_id}/mark-unread", response_model=EmailResponse)
async def mark_email_unread(
    email_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark an email as unread."""
    email = db.query(Email).filter(
        and_(
            Email.id == email_id,
            Email.user_id == current_user.id,
            Email.deleted_at.is_(None)
        )
    ).first()

    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )

    email.is_read = False
    db.commit()
    db.refresh(email)

    return EmailResponse.model_validate(email)


@router.delete("/{email_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email(
    email_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete an email."""
    email = db.query(Email).filter(
        and_(
            Email.id == email_id,
            Email.user_id == current_user.id,
            Email.deleted_at.is_(None)
        )
    ).first()

    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )

    email.soft_delete()
    db.commit()

    return None
