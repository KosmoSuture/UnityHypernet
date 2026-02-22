"""
Notes Routes

Endpoints for managing personal notes and documents.
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
from app.models.note import Note

router = APIRouter()


# Request/Response Models
class NoteCreate(BaseModel):
    """Note creation request"""
    title: str = Field(..., max_length=500)
    content: str
    note_format: str = Field(default='plain', description="plain, markdown, html")
    folder: Optional[str] = Field(None, max_length=255)
    is_pinned: bool = Field(default=False)


class NoteUpdate(BaseModel):
    """Note update request"""
    title: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    note_format: Optional[str] = Field(None, description="plain, markdown, html")
    folder: Optional[str] = Field(None, max_length=255)
    is_pinned: Optional[bool] = None


class NoteResponse(BaseModel):
    """Note response"""
    id: str
    user_id: str
    title: str
    content: str
    note_format: str
    folder: Optional[str]
    is_pinned: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NoteListResponse(BaseModel):
    """Paginated note list response"""
    items: List[NoteResponse]
    total: int
    page: int
    page_size: int


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    request: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new note.

    - **title**: Note title (required)
    - **content**: Note content (required)
    - **note_format**: plain, markdown, or html (default: plain)
    - **folder**: Optional folder/category
    - **is_pinned**: Pin to top of list
    """
    note = Note(
        user_id=current_user.id,
        title=request.title,
        content=request.content,
        note_format=request.note_format,
        folder=request.folder,
        is_pinned=request.is_pinned
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return NoteResponse.model_validate(note)


@router.get("", response_model=NoteListResponse)
async def list_notes(
    folder: Optional[str] = Query(None, description="Filter by folder"),
    is_pinned: Optional[bool] = Query(None, description="Filter pinned notes"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List notes for the current user.

    Supports:
    - Filtering by folder
    - Filtering pinned notes
    - Full-text search in title and content
    - Pagination

    Results are ordered by pinned status, then updated_at descending.
    """
    query = db.query(Note).filter(
        and_(
            Note.user_id == current_user.id,
            Note.deleted_at.is_(None)
        )
    )

    if folder:
        query = query.filter(Note.folder == folder)

    if is_pinned is not None:
        query = query.filter(Note.is_pinned == is_pinned)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Note.title.ilike(search_pattern),
                Note.content.ilike(search_pattern)
            )
        )

    total = query.count()

    offset = (page - 1) * page_size
    items = query.order_by(
        Note.is_pinned.desc(),
        Note.updated_at.desc()
    ).offset(offset).limit(page_size).all()

    return NoteListResponse(
        items=[NoteResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific note by ID."""
    note = db.query(Note).filter(
        and_(
            Note.id == note_id,
            Note.user_id == current_user.id,
            Note.deleted_at.is_(None)
        )
    ).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    return NoteResponse.model_validate(note)


@router.patch("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: UUID,
    request: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a note.

    All fields are optional. Only provided fields will be updated.
    The updated_at timestamp is automatically updated.
    """
    note = db.query(Note).filter(
        and_(
            Note.id == note_id,
            Note.user_id == current_user.id,
            Note.deleted_at.is_(None)
        )
    ).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    if request.title is not None:
        note.title = request.title
    if request.content is not None:
        note.content = request.content
    if request.note_format is not None:
        note.note_format = request.note_format
    if request.folder is not None:
        note.folder = request.folder
    if request.is_pinned is not None:
        note.is_pinned = request.is_pinned

    db.commit()
    db.refresh(note)

    return NoteResponse.model_validate(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a note."""
    note = db.query(Note).filter(
        and_(
            Note.id == note_id,
            Note.user_id == current_user.id,
            Note.deleted_at.is_(None)
        )
    ).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )

    note.soft_delete()
    db.commit()

    return None


@router.get("/folders/list", response_model=List[str])
async def list_folders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all folders used in notes.

    Returns distinct folder names for organizational purposes.
    """
    folders = db.query(Note.folder).filter(
        and_(
            Note.user_id == current_user.id,
            Note.deleted_at.is_(None),
            Note.folder.isnot(None)
        )
    ).distinct().all()

    return [folder[0] for folder in folders]
