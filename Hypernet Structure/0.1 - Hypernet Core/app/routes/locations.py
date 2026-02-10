"""
Locations API Routes

Provides CRUD operations for location history and place management
including GPS coordinates, addresses, and location tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.location import Location


router = APIRouter()


# Pydantic Models for Request/Response
class LocationCreate(BaseModel):
    location_type: str = Field(..., description="gps_point, address, place, checkin, route")
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90, description="GPS latitude")
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180, description="GPS longitude")
    altitude: Optional[Decimal] = Field(None, description="Altitude in meters")
    accuracy: Optional[Decimal] = Field(None, ge=0, description="Accuracy in meters")
    address: Optional[str] = Field(None, max_length=500)
    city: Optional[str] = Field(None, max_length=200)
    state: Optional[str] = Field(None, max_length=200)
    country: Optional[str] = Field(None, max_length=200)
    postal_code: Optional[str] = Field(None, max_length=20)
    place_name: Optional[str] = Field(None, max_length=300)
    place_category: Optional[str] = Field(None, max_length=100)
    timestamp: datetime
    source_app: Optional[str] = Field(None, max_length=100)
    activity_type: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class LocationUpdate(BaseModel):
    place_name: Optional[str] = Field(None, max_length=300)
    place_category: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class LocationResponse(BaseModel):
    id: UUID
    user_id: UUID
    location_type: str
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]
    altitude: Optional[Decimal]
    accuracy: Optional[Decimal]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    postal_code: Optional[str]
    place_name: Optional[str]
    place_category: Optional[str]
    timestamp: datetime
    source_app: Optional[str]
    activity_type: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LocationListResponse(BaseModel):
    items: List[LocationResponse]
    total: int
    page: int
    page_size: int
    pages: int


class NearbyLocation(BaseModel):
    """Location with distance from query point."""
    location: LocationResponse
    distance_km: float


# Endpoints
@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    location_data: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new location record."""
    location = Location(
        user_id=current_user.id,
        **location_data.dict()
    )
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


@router.get("", response_model=LocationListResponse)
async def list_locations(
    location_type: Optional[str] = Query(None, description="Filter by location type"),
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    country: Optional[str] = Query(None, description="Filter by country"),
    place_category: Optional[str] = Query(None, description="Filter by place category"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search in address, place_name, notes"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List locations with optional filtering."""
    query = db.query(Location).filter(
        and_(
            Location.user_id == current_user.id,
            Location.deleted_at.is_(None)
        )
    )

    if location_type:
        query = query.filter(Location.location_type == location_type)

    if city:
        query = query.filter(Location.city.ilike(f"%{city}%"))

    if state:
        query = query.filter(Location.state.ilike(f"%{state}%"))

    if country:
        query = query.filter(Location.country.ilike(f"%{country}%"))

    if place_category:
        query = query.filter(Location.place_category == place_category)

    if start_date:
        query = query.filter(Location.timestamp >= datetime.combine(start_date, datetime.min.time()))

    if end_date:
        query = query.filter(Location.timestamp <= datetime.combine(end_date, datetime.max.time()))

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Location.address.ilike(search_pattern),
                Location.place_name.ilike(search_pattern),
                Location.notes.ilike(search_pattern)
            )
        )

    total = query.count()

    # Order by timestamp descending (most recent first)
    query = query.order_by(Location.timestamp.desc())

    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()

    pages = (total + page_size - 1) // page_size

    return LocationListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/nearby", response_model=List[NearbyLocation])
async def find_nearby_locations(
    latitude: Decimal = Query(..., ge=-90, le=90, description="Center latitude"),
    longitude: Decimal = Query(..., ge=-180, le=180, description="Center longitude"),
    radius_km: float = Query(5.0, gt=0, le=100, description="Search radius in kilometers"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Find locations near a given point using Haversine formula.
    Returns locations sorted by distance.
    """
    # Haversine formula for distance calculation
    # This is a simplified version - for production, use PostGIS
    lat1 = func.radians(latitude)
    lon1 = func.radians(longitude)
    lat2 = func.radians(Location.latitude)
    lon2 = func.radians(Location.longitude)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = func.sin(dlat / 2) ** 2 + func.cos(lat1) * func.cos(lat2) * func.sin(dlon / 2) ** 2
    c = 2 * func.asin(func.sqrt(a))
    distance_km = 6371 * c  # Earth's radius in km

    query = db.query(
        Location,
        distance_km.label('distance')
    ).filter(
        and_(
            Location.user_id == current_user.id,
            Location.deleted_at.is_(None),
            Location.latitude.isnot(None),
            Location.longitude.isnot(None)
        )
    ).having(
        distance_km <= radius_km
    ).order_by(
        distance_km
    ).limit(limit)

    results = query.all()

    return [
        NearbyLocation(
            location=LocationResponse.from_orm(row.Location),
            distance_km=float(row.distance)
        )
        for row in results
    ]


@router.get("/cities", response_model=List[str])
async def list_cities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all unique cities from user's locations."""
    cities = db.query(Location.city).filter(
        and_(
            Location.user_id == current_user.id,
            Location.deleted_at.is_(None),
            Location.city.isnot(None)
        )
    ).distinct().order_by(Location.city).all()

    return [city[0] for city in cities if city[0]]


@router.get("/countries", response_model=List[str])
async def list_countries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all unique countries from user's locations."""
    countries = db.query(Location.country).filter(
        and_(
            Location.user_id == current_user.id,
            Location.deleted_at.is_(None),
            Location.country.isnot(None)
        )
    ).distinct().order_by(Location.country).all()

    return [country[0] for country in countries if country[0]]


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(
    location_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific location by ID."""
    location = db.query(Location).filter(
        and_(
            Location.id == location_id,
            Location.user_id == current_user.id,
            Location.deleted_at.is_(None)
        )
    ).first()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )

    return location


@router.patch("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: UUID,
    location_data: LocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a location's metadata."""
    location = db.query(Location).filter(
        and_(
            Location.id == location_id,
            Location.user_id == current_user.id,
            Location.deleted_at.is_(None)
        )
    ).first()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )

    update_data = location_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(location, field, value)

    location.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(location)

    return location


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a location."""
    location = db.query(Location).filter(
        and_(
            Location.id == location_id,
            Location.user_id == current_user.id,
            Location.deleted_at.is_(None)
        )
    ).first()

    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )

    location.deleted_at = datetime.utcnow()
    db.commit()

    return None
