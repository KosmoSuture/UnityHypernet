"""
Contacts Routes

Endpoints for managing address book contacts.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.contact import Contact

router = APIRouter()


# Request/Response Models
class ContactCreate(BaseModel):
    """Contact creation request"""
    display_name: str = Field(..., max_length=200)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email_addresses: Optional[List[str]] = None
    phone_numbers: Optional[List[str]] = None
    company: Optional[str] = Field(None, max_length=200)
    job_title: Optional[str] = Field(None, max_length=200)
    birthday: Optional[datetime] = None
    notes: Optional[str] = None
    profile_photo_id: Optional[UUID] = None


class ContactUpdate(BaseModel):
    """Contact update request"""
    display_name: Optional[str] = Field(None, max_length=200)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email_addresses: Optional[List[str]] = None
    phone_numbers: Optional[List[str]] = None
    company: Optional[str] = Field(None, max_length=200)
    job_title: Optional[str] = Field(None, max_length=200)
    birthday: Optional[datetime] = None
    notes: Optional[str] = None
    profile_photo_id: Optional[UUID] = None


class ContactResponse(BaseModel):
    """Contact response"""
    id: str
    user_id: str
    display_name: str
    first_name: Optional[str]
    last_name: Optional[str]
    email_addresses: Optional[List[str]]
    phone_numbers: Optional[List[str]]
    company: Optional[str]
    job_title: Optional[str]
    birthday: Optional[datetime]
    notes: Optional[str]
    profile_photo_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContactListResponse(BaseModel):
    """Paginated contact list response"""
    items: List[ContactResponse]
    total: int
    page: int
    page_size: int


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    request: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new contact.

    - **display_name**: Name to display (required)
    - **first_name**: First name
    - **last_name**: Last name
    - **email_addresses**: List of email addresses
    - **phone_numbers**: List of phone numbers
    - **company**: Company name
    - **job_title**: Job title
    """
    contact = Contact(
        user_id=current_user.id,
        display_name=request.display_name,
        first_name=request.first_name,
        last_name=request.last_name,
        email_addresses=request.email_addresses,
        phone_numbers=request.phone_numbers,
        company=request.company,
        job_title=request.job_title,
        birthday=request.birthday,
        notes=request.notes,
        profile_photo_id=request.profile_photo_id
    )

    db.add(contact)
    db.commit()
    db.refresh(contact)

    return ContactResponse.model_validate(contact)


@router.get("", response_model=ContactListResponse)
async def list_contacts(
    search: Optional[str] = Query(None, description="Search in name, email, phone, company"),
    company: Optional[str] = Query(None, description="Filter by company"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List contacts for the current user.

    Supports:
    - Full-text search across name, email, phone, company
    - Filter by company
    - Pagination

    Results ordered by last_name, first_name.
    """
    query = db.query(Contact).filter(
        and_(
            Contact.user_id == current_user.id,
            Contact.deleted_at.is_(None)
        )
    )

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Contact.display_name.ilike(search_pattern),
                Contact.first_name.ilike(search_pattern),
                Contact.last_name.ilike(search_pattern),
                Contact.company.ilike(search_pattern)
            )
        )

    if company:
        query = query.filter(Contact.company.ilike(f"%{company}%"))

    total = query.count()

    offset = (page - 1) * page_size
    items = query.order_by(
        Contact.last_name.asc().nullslast(),
        Contact.first_name.asc().nullslast()
    ).offset(offset).limit(page_size).all()

    return ContactListResponse(
        items=[ContactResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific contact by ID."""
    contact = db.query(Contact).filter(
        and_(
            Contact.id == contact_id,
            Contact.user_id == current_user.id,
            Contact.deleted_at.is_(None)
        )
    ).first()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    return ContactResponse.model_validate(contact)


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: UUID,
    request: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update contact information.

    All fields are optional. Only provided fields will be updated.
    """
    contact = db.query(Contact).filter(
        and_(
            Contact.id == contact_id,
            Contact.user_id == current_user.id,
            Contact.deleted_at.is_(None)
        )
    ).first()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    if request.display_name is not None:
        contact.display_name = request.display_name
    if request.first_name is not None:
        contact.first_name = request.first_name
    if request.last_name is not None:
        contact.last_name = request.last_name
    if request.email_addresses is not None:
        contact.email_addresses = request.email_addresses
    if request.phone_numbers is not None:
        contact.phone_numbers = request.phone_numbers
    if request.company is not None:
        contact.company = request.company
    if request.job_title is not None:
        contact.job_title = request.job_title
    if request.birthday is not None:
        contact.birthday = request.birthday
    if request.notes is not None:
        contact.notes = request.notes
    if request.profile_photo_id is not None:
        contact.profile_photo_id = request.profile_photo_id

    db.commit()
    db.refresh(contact)

    return ContactResponse.model_validate(contact)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a contact."""
    contact = db.query(Contact).filter(
        and_(
            Contact.id == contact_id,
            Contact.user_id == current_user.id,
            Contact.deleted_at.is_(None)
        )
    ).first()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    contact.soft_delete()
    db.commit()

    return None
