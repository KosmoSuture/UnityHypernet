"""
Hypernet MVP Data Models
Python models for the minimal viable database schema
Using Pydantic for validation and FastAPI integration
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator
import json


# ============================================================================
# ENUMS
# ============================================================================

class PrivacyLevel(str, Enum):
    """Privacy levels for objects"""
    PRIVATE = "private"
    FAMILY = "family"
    FRIENDS = "friends"
    PROFESSIONAL = "professional"
    PUBLIC = "public"
    AI_ACCESS = "ai_access"
    LEGACY = "legacy"


class ObjectStatus(str, Enum):
    """Status of objects"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ObjectType(str, Enum):
    """Types of objects in Hypernet"""
    PHOTO = "photo"
    EMAIL = "email"
    PERSON = "person"
    EVENT = "event"
    LOCATION = "location"
    DOCUMENT = "document"
    NOTE = "note"
    TASK = "task"


class LinkType(str, Enum):
    """Types of relationships between objects"""
    DEPICTS = "depicts"  # Photo depicts a person
    MENTIONS = "mentions"  # Email mentions a person
    LOCATED_AT = "located_at"  # Photo taken at location
    RELATED_TO = "related_to"  # Generic relationship
    PARENT_OF = "parent_of"  # Person is parent of person
    CHILD_OF = "child_of"  # Person is child of person
    SPOUSE_OF = "spouse_of"  # Person is spouse of person
    OCCURRED_AT = "occurred_at"  # Event occurred at location
    ATTENDED_BY = "attended_by"  # Event attended by person
    ATTACHED_TO = "attached_to"  # Document attached to email


# ============================================================================
# BASE MODELS
# ============================================================================

class HypernetObject(BaseModel):
    """Base model for all Hypernet objects"""
    id: Optional[int] = None
    hypernet_address: str
    object_type: ObjectType
    owner_address: str
    status: ObjectStatus = ObjectStatus.ACTIVE

    title: Optional[str] = None
    description: Optional[str] = None
    privacy_level: PrivacyLevel = PrivacyLevel.PRIVATE

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    original_date: Optional[datetime] = None

    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None

    metadata: Optional[Dict[str, Any]] = None
    search_text: Optional[str] = None

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def to_db_dict(self) -> dict:
        """Convert to dictionary for database insertion"""
        data = self.model_dump()
        # Convert datetime to ISO string
        if data.get('created_at'):
            data['created_at'] = data['created_at'].isoformat()
        if data.get('updated_at'):
            data['updated_at'] = data['updated_at'].isoformat()
        if data.get('original_date'):
            data['original_date'] = data['original_date'].isoformat()
        # Convert metadata dict to JSON string
        if data.get('metadata'):
            data['metadata'] = json.dumps(data['metadata'])
        return data


class Link(BaseModel):
    """Link between two Hypernet objects"""
    id: Optional[int] = None
    hypernet_address: str

    source_address: str
    target_address: str
    link_type: LinkType

    strength: float = Field(default=1.0, ge=0.0, le=1.0)
    bidirectional: bool = False

    context: Optional[str] = None
    created_by: str = "system"

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    status: ObjectStatus = ObjectStatus.ACTIVE
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        use_enum_values = True


# ============================================================================
# SPECIFIC OBJECT MODELS
# ============================================================================

class Photo(BaseModel):
    """Photo object with EXIF metadata"""
    id: Optional[int] = None
    object_id: Optional[int] = None
    hypernet_address: str

    # Dimensions
    width: Optional[int] = None
    height: Optional[int] = None
    orientation: Optional[int] = None

    # Camera info
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    lens_model: Optional[str] = None

    # Settings
    iso: Optional[int] = None
    aperture: Optional[float] = None
    shutter_speed: Optional[str] = None
    focal_length: Optional[float] = None
    flash: Optional[bool] = None

    # Location
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude: Optional[float] = None
    location_name: Optional[str] = None

    # When taken
    taken_at: Optional[datetime] = None

    # Thumbnails
    thumbnail_small: Optional[str] = None
    thumbnail_medium: Optional[str] = None
    thumbnail_large: Optional[str] = None

    # AI metadata
    ai_caption: Optional[str] = None
    ai_tags: Optional[List[str]] = None
    ai_detected_faces: Optional[List[Dict[str, Any]]] = None

    # Duplicate detection
    perceptual_hash: Optional[str] = None

    def to_db_dict(self) -> dict:
        """Convert to dictionary for database insertion"""
        data = self.model_dump()
        if data.get('taken_at'):
            data['taken_at'] = data['taken_at'].isoformat()
        if data.get('ai_tags'):
            data['ai_tags'] = json.dumps(data['ai_tags'])
        if data.get('ai_detected_faces'):
            data['ai_detected_faces'] = json.dumps(data['ai_detected_faces'])
        return data


class Person(BaseModel):
    """Person (living or deceased)"""
    id: Optional[int] = None
    object_id: Optional[int] = None
    hypernet_address: str

    # Name
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    preferred_name: Optional[str] = None
    suffix: Optional[str] = None

    # Dates
    birth_date: Optional[datetime] = None
    death_date: Optional[datetime] = None

    # Contact
    email: Optional[str] = None
    phone: Optional[str] = None

    # Relationships
    relationship_to_owner: Optional[str] = None

    # Profile
    profile_photo_address: Optional[str] = None
    bio: Optional[str] = None

    # Status
    is_living: bool = True
    is_hypernet_user: bool = False

    @property
    def full_name(self) -> str:
        """Get full name"""
        parts = [self.first_name, self.middle_name, self.last_name, self.suffix]
        return " ".join(p for p in parts if p)

    @property
    def display_name(self) -> str:
        """Get display name (preferred or full)"""
        if self.preferred_name:
            return self.preferred_name
        return self.full_name

    def to_db_dict(self) -> dict:
        """Convert to dictionary for database insertion"""
        data = self.model_dump()
        if data.get('birth_date'):
            data['birth_date'] = data['birth_date'].isoformat()
        if data.get('death_date'):
            data['death_date'] = data['death_date'].isoformat()
        return data


class Event(BaseModel):
    """Event (birthday, holiday, trip, meeting, etc.)"""
    id: Optional[int] = None
    object_id: Optional[int] = None
    hypernet_address: str

    event_type: str

    # When
    start_date: datetime
    end_date: Optional[datetime] = None
    all_day: bool = False

    # Where
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Recurrence
    recurrence_rule: Optional[str] = None

    # Attendees
    attendees: Optional[List[str]] = None  # List of person HAs

    def to_db_dict(self) -> dict:
        """Convert to dictionary for database insertion"""
        data = self.model_dump()
        if data.get('start_date'):
            data['start_date'] = data['start_date'].isoformat()
        if data.get('end_date'):
            data['end_date'] = data['end_date'].isoformat()
        if data.get('attendees'):
            data['attendees'] = json.dumps(data['attendees'])
        return data


class Email(BaseModel):
    """Email message"""
    id: Optional[int] = None
    object_id: Optional[int] = None
    hypernet_address: str

    # Headers
    message_id: str
    subject: Optional[str] = None
    from_address: str
    from_name: Optional[str] = None
    to_addresses: List[str]
    cc_addresses: Optional[List[str]] = None
    bcc_addresses: Optional[List[str]] = None

    # Content
    body_plain: Optional[str] = None
    body_html: Optional[str] = None

    # Metadata
    sent_at: datetime
    received_at: Optional[datetime] = None

    # Threading
    in_reply_to: Optional[str] = None
    thread_id: Optional[str] = None

    # Flags
    is_read: bool = False
    is_starred: bool = False
    is_archived: bool = False

    # Attachments
    attachments: Optional[List[str]] = None

    def to_db_dict(self) -> dict:
        """Convert to dictionary for database insertion"""
        data = self.model_dump()
        if data.get('sent_at'):
            data['sent_at'] = data['sent_at'].isoformat()
        if data.get('received_at'):
            data['received_at'] = data['received_at'].isoformat()
        if data.get('to_addresses'):
            data['to_addresses'] = json.dumps(data['to_addresses'])
        if data.get('cc_addresses'):
            data['cc_addresses'] = json.dumps(data['cc_addresses'])
        if data.get('bcc_addresses'):
            data['bcc_addresses'] = json.dumps(data['bcc_addresses'])
        if data.get('attachments'):
            data['attachments'] = json.dumps(data['attachments'])
        return data


class Location(BaseModel):
    """Physical location"""
    id: Optional[int] = None
    object_id: Optional[int] = None
    hypernet_address: str

    # Details
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None

    # Coordinates
    latitude: float
    longitude: float

    # Type
    location_type: Optional[str] = None

    # Visits
    first_visit_date: Optional[datetime] = None
    last_visit_date: Optional[datetime] = None
    visit_count: int = 0

    def to_db_dict(self) -> dict:
        """Convert to dictionary for database insertion"""
        data = self.model_dump()
        if data.get('first_visit_date'):
            data['first_visit_date'] = data['first_visit_date'].isoformat()
        if data.get('last_visit_date'):
            data['last_visit_date'] = data['last_visit_date'].isoformat()
        return data


# ============================================================================
# API REQUEST/RESPONSE MODELS
# ============================================================================

class PhotoWithLinks(BaseModel):
    """Photo with its associated links"""
    photo: Photo
    object: HypernetObject
    people: List[Person] = []
    location: Optional[Location] = None
    events: List[Event] = []


class SearchRequest(BaseModel):
    """Search request"""
    query: str
    object_types: Optional[List[ObjectType]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    owner_address: Optional[str] = None
    limit: int = Field(default=50, le=1000)
    offset: int = 0


class SearchResult(BaseModel):
    """Search result"""
    hypernet_address: str
    object_type: ObjectType
    title: Optional[str]
    description: Optional[str]
    thumbnail: Optional[str] = None
    relevance_score: float
    original_date: Optional[datetime] = None


class TimelineRequest(BaseModel):
    """Request for timeline view"""
    owner_address: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    object_types: Optional[List[ObjectType]] = None
    limit: int = Field(default=100, le=1000)


class AIQueryRequest(BaseModel):
    """Request for AI query"""
    query: str
    owner_address: str
    include_types: Optional[List[ObjectType]] = None
    max_results: int = Field(default=10, le=100)


class AIQueryResponse(BaseModel):
    """Response from AI query"""
    answer: str
    sources: List[SearchResult]
    query_interpretation: str
    execution_time_ms: float


# ============================================================================
# HYPERNET ADDRESS UTILITIES
# ============================================================================

class HypernetAddress:
    """Utility class for Hypernet Address manipulation"""

    @staticmethod
    def generate(category: int, subcategory: int, type_: int,
                 subtype: int, instance: int) -> str:
        """Generate a Hypernet Address"""
        return f"{category}.{subcategory}.{type_}.{subtype}.{instance:05d}"

    @staticmethod
    def parse(address: str) -> Dict[str, int]:
        """Parse a Hypernet Address into components"""
        parts = address.split('.')
        if len(parts) == 2:
            # Short form like "1.1" (person)
            return {
                'category': int(parts[0]),
                'subcategory': int(parts[1]),
                'type': None,
                'subtype': None,
                'instance': None
            }
        elif len(parts) == 5:
            # Full form like "1.1.8.0.00001"
            return {
                'category': int(parts[0]),
                'subcategory': int(parts[1]),
                'type': int(parts[2]),
                'subtype': int(parts[3]),
                'instance': int(parts[4])
            }
        else:
            raise ValueError(f"Invalid Hypernet Address: {address}")

    @staticmethod
    def is_valid(address: str) -> bool:
        """Check if address is valid"""
        try:
            HypernetAddress.parse(address)
            return True
        except:
            return False

    @staticmethod
    def get_next_instance(category: int, subcategory: int,
                         type_: int, subtype: int,
                         existing_instances: List[int]) -> int:
        """Get next available instance number"""
        if not existing_instances:
            return 1
        return max(existing_instances) + 1


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example: Create a photo object
    photo_obj = HypernetObject(
        hypernet_address="1.1.8.0.00001",
        object_type=ObjectType.PHOTO,
        owner_address="1.1",
        title="Family Christmas 2023",
        description="Christmas dinner at our house",
        privacy_level=PrivacyLevel.FAMILY,
        original_date=datetime(2023, 12, 25, 18, 30),
        file_path="/photos/2023/12/IMG_1234.jpg",
        file_size=2_500_000,
        mime_type="image/jpeg"
    )

    photo = Photo(
        hypernet_address="1.1.8.0.00001",
        width=4032,
        height=3024,
        camera_make="Apple",
        camera_model="iPhone 14 Pro",
        taken_at=datetime(2023, 12, 25, 18, 30),
        latitude=47.6062,
        longitude=-122.3321,
        location_name="Seattle, WA",
        ai_caption="Family gathered around dinner table with Christmas decorations",
        ai_tags=["christmas", "family", "dinner", "indoor"]
    )

    # Example: Create links
    link_to_sarah = Link(
        hypernet_address="0.5.1.1.00001",
        source_address="1.1.8.0.00001",
        target_address="1.2",
        link_type=LinkType.DEPICTS,
        strength=1.0,
        context="Sarah is in the photo"
    )

    link_to_event = Link(
        hypernet_address="0.5.1.1.00002",
        source_address="1.1.8.0.00001",
        target_address="1.1.9.5.00012",  # Christmas 2023 event
        link_type=LinkType.RELATED_TO,
        strength=1.0,
        context="Photo taken during Christmas 2023 event"
    )

    print("Photo object:", photo_obj.model_dump_json(indent=2))
    print("\nPhoto details:", photo.model_dump_json(indent=2))
    print("\nLink:", link_to_sarah.model_dump_json(indent=2))
