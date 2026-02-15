"""
Audit API Routes

Provides read-only access to audit logs for security and compliance.
Audit logs track all user actions, API calls, and system events.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.audit import Audit


router = APIRouter()


# Pydantic Models for Response (No Create/Update - audit logs are system-generated)
class AuditResponse(BaseModel):
    id: UUID
    user_id: UUID
    action: str
    resource_type: Optional[str]
    resource_id: Optional[UUID]
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_method: Optional[str]
    request_path: Optional[str]
    status_code: Optional[int]
    changes: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime

    class Config:
        from_attributes = True


class AuditListResponse(BaseModel):
    items: List[AuditResponse]
    total: int
    page: int
    page_size: int
    pages: int


class AuditSummary(BaseModel):
    """Summary of audit events."""
    action: str
    count: int
    first_seen: datetime
    last_seen: datetime


# Endpoints
@router.get("", response_model=AuditListResponse)
async def list_audit_logs(
    action: Optional[str] = Query(None, description="Filter by action (e.g., create, update, delete, login)"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type (e.g., media, document, task)"),
    resource_id: Optional[UUID] = Query(None, description="Filter by specific resource ID"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    ip_address: Optional[str] = Query(None, description="Filter by IP address"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List audit logs for the current user.
    Audit logs are read-only and cannot be modified or deleted.
    """
    query = db.query(Audit).filter(Audit.user_id == current_user.id)

    if action:
        query = query.filter(Audit.action == action)

    if resource_type:
        query = query.filter(Audit.resource_type == resource_type)

    if resource_id:
        query = query.filter(Audit.resource_id == resource_id)

    if start_date:
        query = query.filter(Audit.timestamp >= datetime.combine(start_date, datetime.min.time()))

    if end_date:
        query = query.filter(Audit.timestamp <= datetime.combine(end_date, datetime.max.time()))

    if ip_address:
        query = query.filter(Audit.ip_address == ip_address)

    total = query.count()

    # Order by timestamp descending (most recent first)
    query = query.order_by(Audit.timestamp.desc())

    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    pages = (total + page_size - 1) // page_size

    return AuditListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/summary", response_model=List[AuditSummary])
async def get_audit_summary(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get summary of audit events grouped by action."""
    from sqlalchemy import func

    query = db.query(
        Audit.action,
        func.count(Audit.id).label('count'),
        func.min(Audit.timestamp).label('first_seen'),
        func.max(Audit.timestamp).label('last_seen')
    ).filter(Audit.user_id == current_user.id)

    if start_date:
        query = query.filter(Audit.timestamp >= datetime.combine(start_date, datetime.min.time()))

    if end_date:
        query = query.filter(Audit.timestamp <= datetime.combine(end_date, datetime.max.time()))

    results = query.group_by(Audit.action).order_by(func.count(Audit.id).desc()).all()

    return [
        AuditSummary(
            action=row.action,
            count=row.count,
            first_seen=row.first_seen,
            last_seen=row.last_seen
        )
        for row in results
    ]


@router.get("/actions", response_model=List[str])
async def list_actions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all unique action types from user's audit logs."""
    actions = db.query(Audit.action).filter(
        Audit.user_id == current_user.id
    ).distinct().order_by(Audit.action).all()

    return [action[0] for action in actions if action[0]]


@router.get("/resource-types", response_model=List[str])
async def list_resource_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all unique resource types from user's audit logs."""
    resource_types = db.query(Audit.resource_type).filter(
        and_(
            Audit.user_id == current_user.id,
            Audit.resource_type.isnot(None)
        )
    ).distinct().order_by(Audit.resource_type).all()

    return [rt[0] for rt in resource_types if rt[0]]


@router.get("/ip-addresses", response_model=List[str])
async def list_ip_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all unique IP addresses from user's audit logs.
    Useful for security monitoring and detecting unusual access patterns.
    """
    ips = db.query(Audit.ip_address).filter(
        and_(
            Audit.user_id == current_user.id,
            Audit.ip_address.isnot(None)
        )
    ).distinct().all()

    return [ip[0] for ip in ips if ip[0]]


@router.get("/recent", response_model=AuditListResponse)
async def get_recent_activity(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back (max 7 days)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recent audit activity for the user."""
    from datetime import timedelta

    cutoff_time = datetime.utcnow() - timedelta(hours=hours)

    query = db.query(Audit).filter(
        and_(
            Audit.user_id == current_user.id,
            Audit.timestamp >= cutoff_time
        )
    ).order_by(Audit.timestamp.desc()).limit(limit)

    items = query.all()
    total = db.query(Audit).filter(
        and_(
            Audit.user_id == current_user.id,
            Audit.timestamp >= cutoff_time
        )
    ).count()

    return AuditListResponse(
        items=items,
        total=total,
        page=1,
        page_size=limit,
        pages=1
    )


@router.get("/{audit_id}", response_model=AuditResponse)
async def get_audit_log(
    audit_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific audit log entry by ID."""
    audit_log = db.query(Audit).filter(
        and_(
            Audit.id == audit_id,
            Audit.user_id == current_user.id
        )
    ).first()

    if not audit_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )

    return audit_log


@router.get("/resource/{resource_type}/{resource_id}", response_model=AuditListResponse)
async def get_resource_history(
    resource_type: str,
    resource_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get audit history for a specific resource.
    Shows all actions taken on a particular resource.
    """
    query = db.query(Audit).filter(
        and_(
            Audit.user_id == current_user.id,
            Audit.resource_type == resource_type,
            Audit.resource_id == resource_id
        )
    )

    total = query.count()

    query = query.order_by(Audit.timestamp.desc())

    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    pages = (total + page_size - 1) // page_size

    return AuditListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )
