"""
Devices API Routes

Provides CRUD operations for device management including
phones, computers, tablets, IoT devices, and their metadata.
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
from app.models.device import Device


router = APIRouter()


# Pydantic Models for Request/Response
class DeviceCreate(BaseModel):
    device_type: str = Field(..., description="phone, computer, tablet, wearable, iot, smart_home, vehicle, other")
    device_name: str = Field(..., max_length=300)
    manufacturer: Optional[str] = Field(None, max_length=200)
    model: Optional[str] = Field(None, max_length=200)
    os_name: Optional[str] = Field(None, max_length=100)
    os_version: Optional[str] = Field(None, max_length=100)
    device_identifier: Optional[str] = Field(None, max_length=500, description="IMEI, serial number, MAC address, etc.")
    ip_address: Optional[str] = Field(None, max_length=45)
    is_primary: bool = Field(default=False)
    is_trusted: bool = Field(default=True)
    last_seen_at: Optional[datetime] = None
    purchase_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    notes: Optional[str] = None


class DeviceUpdate(BaseModel):
    device_name: Optional[str] = Field(None, max_length=300)
    os_version: Optional[str] = Field(None, max_length=100)
    ip_address: Optional[str] = Field(None, max_length=45)
    is_primary: Optional[bool] = None
    is_trusted: Optional[bool] = None
    last_seen_at: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    notes: Optional[str] = None


class DeviceResponse(BaseModel):
    id: UUID
    user_id: UUID
    device_type: str
    device_name: str
    manufacturer: Optional[str]
    model: Optional[str]
    os_name: Optional[str]
    os_version: Optional[str]
    device_identifier: Optional[str]
    ip_address: Optional[str]
    is_primary: bool
    is_trusted: bool
    last_seen_at: Optional[datetime]
    purchase_date: Optional[datetime]
    warranty_expiry: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DeviceListResponse(BaseModel):
    items: List[DeviceResponse]
    total: int
    page: int
    page_size: int
    pages: int


# Endpoints
@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    device_data: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Register a new device."""
    # If this is marked as primary, unmark all other primary devices
    if device_data.is_primary:
        db.query(Device).filter(
            and_(
                Device.user_id == current_user.id,
                Device.deleted_at.is_(None),
                Device.is_primary == True
            )
        ).update({"is_primary": False})

    device = Device(
        user_id=current_user.id,
        **device_data.dict()
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@router.get("", response_model=DeviceListResponse)
async def list_devices(
    device_type: Optional[str] = Query(None, description="Filter by device type"),
    manufacturer: Optional[str] = Query(None, description="Filter by manufacturer"),
    is_primary: Optional[bool] = Query(None, description="Filter primary devices"),
    is_trusted: Optional[bool] = Query(None, description="Filter trusted devices"),
    search: Optional[str] = Query(None, description="Search in device_name, model, notes"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List devices with optional filtering."""
    query = db.query(Device).filter(
        and_(
            Device.user_id == current_user.id,
            Device.deleted_at.is_(None)
        )
    )

    if device_type:
        query = query.filter(Device.device_type == device_type)

    if manufacturer:
        query = query.filter(Device.manufacturer.ilike(f"%{manufacturer}%"))

    if is_primary is not None:
        query = query.filter(Device.is_primary == is_primary)

    if is_trusted is not None:
        query = query.filter(Device.is_trusted == is_trusted)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Device.device_name.ilike(search_pattern),
                Device.model.ilike(search_pattern),
                Device.notes.ilike(search_pattern)
            )
        )

    total = query.count()

    # Order by primary, then last_seen, then created
    query = query.order_by(
        Device.is_primary.desc(),
        Device.last_seen_at.desc().nullslast(),
        Device.created_at.desc()
    )

    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    pages = (total + page_size - 1) // page_size

    return DeviceListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/manufacturers", response_model=List[str])
async def list_manufacturers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all unique manufacturers from user's devices."""
    manufacturers = db.query(Device.manufacturer).filter(
        and_(
            Device.user_id == current_user.id,
            Device.deleted_at.is_(None),
            Device.manufacturer.isnot(None)
        )
    ).distinct().order_by(Device.manufacturer).all()

    return [mfr[0] for mfr in manufacturers if mfr[0]]


@router.post("/{device_id}/heartbeat", response_model=DeviceResponse)
async def record_heartbeat(
    device_id: UUID,
    ip_address: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Record a device heartbeat to update last_seen_at.
    Useful for tracking device activity and presence.
    """
    device = db.query(Device).filter(
        and_(
            Device.id == device_id,
            Device.user_id == current_user.id,
            Device.deleted_at.is_(None)
        )
    ).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    device.last_seen_at = datetime.utcnow()
    if ip_address:
        device.ip_address = ip_address

    device.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(device)

    return device


@router.post("/{device_id}/trust", response_model=DeviceResponse)
async def trust_device(
    device_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a device as trusted."""
    device = db.query(Device).filter(
        and_(
            Device.id == device_id,
            Device.user_id == current_user.id,
            Device.deleted_at.is_(None)
        )
    ).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    device.is_trusted = True
    device.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(device)

    return device


@router.post("/{device_id}/untrust", response_model=DeviceResponse)
async def untrust_device(
    device_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a device as untrusted."""
    device = db.query(Device).filter(
        and_(
            Device.id == device_id,
            Device.user_id == current_user.id,
            Device.deleted_at.is_(None)
        )
    ).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    device.is_trusted = False
    device.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(device)

    return device


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific device by ID."""
    device = db.query(Device).filter(
        and_(
            Device.id == device_id,
            Device.user_id == current_user.id,
            Device.deleted_at.is_(None)
        )
    ).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    return device


@router.patch("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: UUID,
    device_data: DeviceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a device's information."""
    device = db.query(Device).filter(
        and_(
            Device.id == device_id,
            Device.user_id == current_user.id,
            Device.deleted_at.is_(None)
        )
    ).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    update_data = device_data.dict(exclude_unset=True)

    # If marking as primary, unmark all other primary devices
    if update_data.get("is_primary") == True:
        db.query(Device).filter(
            and_(
                Device.user_id == current_user.id,
                Device.deleted_at.is_(None),
                Device.id != device_id,
                Device.is_primary == True
            )
        ).update({"is_primary": False})

    for field, value in update_data.items():
        setattr(device, field, value)

    device.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(device)

    return device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a device."""
    device = db.query(Device).filter(
        and_(
            Device.id == device_id,
            Device.user_id == current_user.id,
            Device.deleted_at.is_(None)
        )
    ).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    device.deleted_at = datetime.utcnow()
    db.commit()

    return None
