"""
Health Records API Routes

Provides CRUD operations for health and medical record management
including appointments, medications, measurements, and medical history.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.health_record import HealthRecord


router = APIRouter()


# Pydantic Models for Request/Response
class HealthRecordCreate(BaseModel):
    record_type: str = Field(..., description="appointment, medication, lab_result, vital_sign, diagnosis, immunization, allergy, procedure, other")
    record_date: datetime
    provider_name: Optional[str] = Field(None, max_length=300)
    facility_name: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = Field(None, max_length=1000)
    diagnosis_codes: List[str] = Field(default_factory=list)
    medication_name: Optional[str] = Field(None, max_length=300)
    dosage: Optional[str] = Field(None, max_length=200)
    frequency: Optional[str] = Field(None, max_length=200)
    measurement_type: Optional[str] = Field(None, max_length=100, description="e.g., blood_pressure, weight, temperature, heart_rate")
    measurement_value: Optional[str] = Field(None, max_length=100)
    measurement_unit: Optional[str] = Field(None, max_length=50)
    file_paths: List[str] = Field(default_factory=list)
    is_important: bool = Field(default=False)
    notes: Optional[str] = None


class HealthRecordUpdate(BaseModel):
    description: Optional[str] = Field(None, max_length=1000)
    diagnosis_codes: Optional[List[str]] = None
    medication_name: Optional[str] = Field(None, max_length=300)
    dosage: Optional[str] = Field(None, max_length=200)
    frequency: Optional[str] = Field(None, max_length=200)
    is_important: Optional[bool] = None
    notes: Optional[str] = None


class HealthRecordResponse(BaseModel):
    id: UUID
    user_id: UUID
    record_type: str
    record_date: datetime
    provider_name: Optional[str]
    facility_name: Optional[str]
    description: Optional[str]
    diagnosis_codes: List[str]
    medication_name: Optional[str]
    dosage: Optional[str]
    frequency: Optional[str]
    measurement_type: Optional[str]
    measurement_value: Optional[str]
    measurement_unit: Optional[str]
    file_paths: List[str]
    is_important: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HealthRecordListResponse(BaseModel):
    items: List[HealthRecordResponse]
    total: int
    page: int
    page_size: int
    pages: int


# Endpoints
@router.post("", response_model=HealthRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_health_record(
    record_data: HealthRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new health record."""
    record = HealthRecord(
        user_id=current_user.id,
        **record_data.dict()
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=HealthRecordListResponse)
async def list_health_records(
    record_type: Optional[str] = Query(None, description="Filter by record type"),
    provider_name: Optional[str] = Query(None, description="Filter by provider"),
    facility_name: Optional[str] = Query(None, description="Filter by facility"),
    measurement_type: Optional[str] = Query(None, description="Filter by measurement type"),
    is_important: Optional[bool] = Query(None, description="Filter important records"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search in description, medication, notes"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List health records with optional filtering."""
    query = db.query(HealthRecord).filter(
        and_(
            HealthRecord.user_id == current_user.id,
            HealthRecord.deleted_at.is_(None)
        )
    )

    if record_type:
        query = query.filter(HealthRecord.record_type == record_type)

    if provider_name:
        query = query.filter(HealthRecord.provider_name.ilike(f"%{provider_name}%"))

    if facility_name:
        query = query.filter(HealthRecord.facility_name.ilike(f"%{facility_name}%"))

    if measurement_type:
        query = query.filter(HealthRecord.measurement_type == measurement_type)

    if is_important is not None:
        query = query.filter(HealthRecord.is_important == is_important)

    if start_date:
        query = query.filter(HealthRecord.record_date >= datetime.combine(start_date, datetime.min.time()))

    if end_date:
        query = query.filter(HealthRecord.record_date <= datetime.combine(end_date, datetime.max.time()))

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                HealthRecord.description.ilike(search_pattern),
                HealthRecord.medication_name.ilike(search_pattern),
                HealthRecord.notes.ilike(search_pattern)
            )
        )

    total = query.count()

    # Order by importance, then record_date descending
    query = query.order_by(
        HealthRecord.is_important.desc(),
        HealthRecord.record_date.desc()
    )

    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    pages = (total + page_size - 1) // page_size

    return HealthRecordListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/medications", response_model=HealthRecordListResponse)
async def list_medications(
    active_only: bool = Query(True, description="Only show current medications"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List medications with special focus on active prescriptions."""
    query = db.query(HealthRecord).filter(
        and_(
            HealthRecord.user_id == current_user.id,
            HealthRecord.deleted_at.is_(None),
            HealthRecord.record_type == 'medication'
        )
    )

    if active_only:
        # Consider medication active if record_date is within last 90 days
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        query = query.filter(HealthRecord.record_date >= cutoff_date)

    total = query.count()

    query = query.order_by(HealthRecord.record_date.desc())

    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    pages = (total + page_size - 1) // page_size

    return HealthRecordListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/providers", response_model=List[str])
async def list_providers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all unique provider names from user's health records."""
    providers = db.query(HealthRecord.provider_name).filter(
        and_(
            HealthRecord.user_id == current_user.id,
            HealthRecord.deleted_at.is_(None),
            HealthRecord.provider_name.isnot(None)
        )
    ).distinct().order_by(HealthRecord.provider_name).all()

    return [provider[0] for provider in providers if provider[0]]


@router.get("/facilities", response_model=List[str])
async def list_facilities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all unique facility names from user's health records."""
    facilities = db.query(HealthRecord.facility_name).filter(
        and_(
            HealthRecord.user_id == current_user.id,
            HealthRecord.deleted_at.is_(None),
            HealthRecord.facility_name.isnot(None)
        )
    ).distinct().order_by(HealthRecord.facility_name).all()

    return [facility[0] for facility in facilities if facility[0]]


@router.get("/{record_id}", response_model=HealthRecordResponse)
async def get_health_record(
    record_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific health record by ID."""
    record = db.query(HealthRecord).filter(
        and_(
            HealthRecord.id == record_id,
            HealthRecord.user_id == current_user.id,
            HealthRecord.deleted_at.is_(None)
        )
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health record not found"
        )

    return record


@router.patch("/{record_id}", response_model=HealthRecordResponse)
async def update_health_record(
    record_id: UUID,
    record_data: HealthRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a health record's metadata."""
    record = db.query(HealthRecord).filter(
        and_(
            HealthRecord.id == record_id,
            HealthRecord.user_id == current_user.id,
            HealthRecord.deleted_at.is_(None)
        )
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health record not found"
        )

    update_data = record_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)

    record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(record)

    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_health_record(
    record_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a health record."""
    record = db.query(HealthRecord).filter(
        and_(
            HealthRecord.id == record_id,
            HealthRecord.user_id == current_user.id,
            HealthRecord.deleted_at.is_(None)
        )
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health record not found"
        )

    record.deleted_at = datetime.utcnow()
    db.commit()

    return None
