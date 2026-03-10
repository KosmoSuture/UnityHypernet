"""
Documents API Routes

Provides CRUD operations for document management including files,
contracts, receipts, and other personal documents.
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
from app.models.document import Document


router = APIRouter()


# Pydantic Models for Request/Response
class DocumentCreate(BaseModel):
    title: str = Field(..., max_length=500)
    document_type: str = Field(..., description="contract, receipt, invoice, tax_document, identification, certificate, insurance, legal, medical, other")
    file_path: str = Field(..., description="Storage path or URL to document file")
    file_size_bytes: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, max_length=200)
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    issuer: Optional[str] = Field(None, max_length=300)
    recipient: Optional[str] = Field(None, max_length=300)
    document_number: Optional[str] = Field(None, max_length=200)
    is_important: bool = Field(default=False)
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=200)
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    issuer: Optional[str] = Field(None, max_length=300)
    recipient: Optional[str] = Field(None, max_length=300)
    document_number: Optional[str] = Field(None, max_length=200)
    is_important: Optional[bool] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class DocumentResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    document_type: str
    file_path: str
    file_size_bytes: Optional[int]
    mime_type: Optional[str]
    category: Optional[str]
    issue_date: Optional[datetime]
    expiry_date: Optional[datetime]
    issuer: Optional[str]
    recipient: Optional[str]
    document_number: Optional[str]
    is_important: bool
    tags: List[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    items: List[DocumentResponse]
    total: int
    page: int
    page_size: int
    pages: int


# Endpoints
@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_data: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new document record."""
    document = Document(
        user_id=current_user.id,
        **document_data.dict()
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    is_important: Optional[bool] = Query(None, description="Filter important documents"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    expiring_soon: Optional[bool] = Query(None, description="Documents expiring in next 30 days"),
    search: Optional[str] = Query(None, description="Search in title, issuer, recipient, notes"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List documents with optional filtering."""
    query = db.query(Document).filter(
        and_(
            Document.user_id == current_user.id,
            Document.deleted_at.is_(None)
        )
    )

    if document_type:
        query = query.filter(Document.document_type == document_type)

    if category:
        query = query.filter(Document.category == category)

    if is_important is not None:
        query = query.filter(Document.is_important == is_important)

    if tag:
        query = query.filter(Document.tags.contains([tag]))

    if expiring_soon:
        from datetime import timedelta
        future_date = datetime.utcnow() + timedelta(days=30)
        query = query.filter(
            and_(
                Document.expiry_date.isnot(None),
                Document.expiry_date <= future_date,
                Document.expiry_date >= datetime.utcnow()
            )
        )

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Document.title.ilike(search_pattern),
                Document.issuer.ilike(search_pattern),
                Document.recipient.ilike(search_pattern),
                Document.notes.ilike(search_pattern)
            )
        )

    total = query.count()

    # Order by importance, then issue_date descending
    query = query.order_by(
        Document.is_important.desc(),
        Document.issue_date.desc().nullslast()
    )

    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    pages = (total + page_size - 1) // page_size

    return DocumentListResponse(
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
    """Get all unique categories for user's documents."""
    categories = db.query(Document.category).filter(
        and_(
            Document.user_id == current_user.id,
            Document.deleted_at.is_(None),
            Document.category.isnot(None)
        )
    ).distinct().all()

    return [cat[0] for cat in categories if cat[0]]


@router.get("/tags", response_model=List[str])
async def list_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all unique tags used in user's documents."""
    from sqlalchemy import func

    # PostgreSQL unnest to get individual tags
    tags = db.query(func.unnest(Document.tags)).filter(
        and_(
            Document.user_id == current_user.id,
            Document.deleted_at.is_(None)
        )
    ).distinct().all()

    return [tag[0] for tag in tags if tag[0]]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific document by ID."""
    document = db.query(Document).filter(
        and_(
            Document.id == document_id,
            Document.user_id == current_user.id,
            Document.deleted_at.is_(None)
        )
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    return document


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    document_data: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a document's metadata."""
    document = db.query(Document).filter(
        and_(
            Document.id == document_id,
            Document.user_id == current_user.id,
            Document.deleted_at.is_(None)
        )
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    update_data = document_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(document, field, value)

    document.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(document)

    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a document."""
    document = db.query(Document).filter(
        and_(
            Document.id == document_id,
            Document.user_id == current_user.id,
            Document.deleted_at.is_(None)
        )
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    document.deleted_at = datetime.utcnow()
    db.commit()

    return None
