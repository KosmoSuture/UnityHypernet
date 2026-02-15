"""
Web Pages Routes

Endpoints for managing saved web pages and articles.
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
from app.models.web_page import WebPage

router = APIRouter()


# Request/Response Models
class WebPageCreate(BaseModel):
    """Web page creation request"""
    url: str = Field(..., max_length=2048)
    title: str = Field(..., max_length=500)
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    screenshot_id: Optional[UUID] = None
    author: Optional[str] = Field(None, max_length=200)
    published_at: Optional[datetime] = None
    site_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    archive_path: Optional[str] = Field(None, max_length=512)


class WebPageUpdate(BaseModel):
    """Web page update request"""
    title: Optional[str] = Field(None, max_length=500)
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    screenshot_id: Optional[UUID] = None
    author: Optional[str] = Field(None, max_length=200)
    published_at: Optional[datetime] = None
    site_name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    archive_path: Optional[str] = Field(None, max_length=512)


class WebPageResponse(BaseModel):
    """Web page response"""
    id: str
    user_id: str
    url: str
    title: str
    html_content: Optional[str]
    text_content: Optional[str]
    screenshot_id: Optional[str]
    author: Optional[str]
    published_at: Optional[datetime]
    site_name: Optional[str]
    description: Optional[str]
    archive_path: Optional[str]
    saved_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class WebPageListResponse(BaseModel):
    """Paginated web page list response"""
    items: List[WebPageResponse]
    total: int
    page: int
    page_size: int


@router.post("", response_model=WebPageResponse, status_code=status.HTTP_201_CREATED)
async def create_web_page(
    request: WebPageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Save a new web page.

    - **url**: Page URL (required)
    - **title**: Page title (required)
    - **html_content**: Full HTML content
    - **text_content**: Extracted text content
    - **screenshot_id**: ID of screenshot media
    - **author**: Article author
    - **published_at**: Publication date
    - **site_name**: Website name
    - **description**: Page description/summary
    """
    web_page = WebPage(
        user_id=current_user.id,
        url=request.url,
        title=request.title,
        html_content=request.html_content,
        text_content=request.text_content,
        screenshot_id=request.screenshot_id,
        author=request.author,
        published_at=request.published_at,
        site_name=request.site_name,
        description=request.description,
        archive_path=request.archive_path,
        saved_at=datetime.utcnow()
    )

    db.add(web_page)
    db.commit()
    db.refresh(web_page)

    return WebPageResponse.model_validate(web_page)


@router.get("", response_model=WebPageListResponse)
async def list_web_pages(
    site_name: Optional[str] = Query(None, description="Filter by site name"),
    author: Optional[str] = Query(None, description="Filter by author"),
    search: Optional[str] = Query(None, description="Search in title, description, text"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List saved web pages for the current user.

    Supports:
    - Filter by site_name
    - Filter by author
    - Full-text search in title, description, text_content
    - Pagination

    Results ordered by saved_at descending (newest first).
    """
    query = db.query(WebPage).filter(
        and_(
            WebPage.user_id == current_user.id,
            WebPage.deleted_at.is_(None)
        )
    )

    if site_name:
        query = query.filter(WebPage.site_name.ilike(f"%{site_name}%"))

    if author:
        query = query.filter(WebPage.author.ilike(f"%{author}%"))

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                WebPage.title.ilike(search_pattern),
                WebPage.description.ilike(search_pattern),
                WebPage.text_content.ilike(search_pattern)
            )
        )

    total = query.count()

    offset = (page - 1) * page_size
    items = query.order_by(WebPage.saved_at.desc()).offset(offset).limit(page_size).all()

    return WebPageListResponse(
        items=[WebPageResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{page_id}", response_model=WebPageResponse)
async def get_web_page(
    page_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific saved web page by ID."""
    web_page = db.query(WebPage).filter(
        and_(
            WebPage.id == page_id,
            WebPage.user_id == current_user.id,
            WebPage.deleted_at.is_(None)
        )
    ).first()

    if not web_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Web page not found"
        )

    return WebPageResponse.model_validate(web_page)


@router.patch("/{page_id}", response_model=WebPageResponse)
async def update_web_page(
    page_id: UUID,
    request: WebPageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update web page metadata.

    All fields are optional. Only provided fields will be updated.
    """
    web_page = db.query(WebPage).filter(
        and_(
            WebPage.id == page_id,
            WebPage.user_id == current_user.id,
            WebPage.deleted_at.is_(None)
        )
    ).first()

    if not web_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Web page not found"
        )

    if request.title is not None:
        web_page.title = request.title
    if request.html_content is not None:
        web_page.html_content = request.html_content
    if request.text_content is not None:
        web_page.text_content = request.text_content
    if request.screenshot_id is not None:
        web_page.screenshot_id = request.screenshot_id
    if request.author is not None:
        web_page.author = request.author
    if request.published_at is not None:
        web_page.published_at = request.published_at
    if request.site_name is not None:
        web_page.site_name = request.site_name
    if request.description is not None:
        web_page.description = request.description
    if request.archive_path is not None:
        web_page.archive_path = request.archive_path

    db.commit()
    db.refresh(web_page)

    return WebPageResponse.model_validate(web_page)


@router.delete("/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_web_page(
    page_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a saved web page."""
    web_page = db.query(WebPage).filter(
        and_(
            WebPage.id == page_id,
            WebPage.user_id == current_user.id,
            WebPage.deleted_at.is_(None)
        )
    ).first()

    if not web_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Web page not found"
        )

    web_page.soft_delete()
    db.commit()

    return None
