---
ha: "0.4.0.2.1"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# Photo - Image Media Type

**Type ID:** `hypernet.media.photo`
**Version:** 1.0
**Category:** 0.0.2 - Media Types
**Parent:** Media (extends BaseObject)
**Status:** Active
**Created:** 2026-02-04

---

## Identity

```yaml
type_name: "Photo"
type_id: "hypernet.media.photo"
version: "1.0"
parent_type: "Media" (which extends BaseObject)
category: "0.0.2 - Media Types"
abstract: false (can be instantiated)
```

---

## Purpose

### What

**Photo represents digital images** - photographs, screenshots, scanned documents, digital artwork, or any visual content stored as an image file.

### Why

Photos are central to personal digital life:
- Primary medium for capturing memories
- Most common content type across platforms
- Rich metadata (EXIF, GPS, tags)
- Foundation for AI analysis (object detection, face recognition)
- Heavily integrated (Instagram, Google Photos, iCloud, etc.)

### When to Use

Use Photo type for:
- Camera photographs (JPEG, HEIC, RAW)
- Screenshots and screen captures
- Scanned documents stored as images
- Digital artwork and graphics (PNG, WebP)
- Social media images
- Profile pictures and avatars

**Do NOT use for:**
- Video files (use Video type)
- PDF documents (use Document type)
- Multi-page scans (use Document type)

---

## Inherited Fields (from BaseObject)

```yaml
# See BaseObject.md for complete details
id: UUID
user_id: UUID
created_at: DateTime
updated_at: DateTime
deleted_at: DateTime (nullable)
source_type: String (nullable)
source_id: String (nullable)
metadata: JSONB
```

---

## Type-Specific Required Fields

### File Identity

```yaml
filename:
  type: String
  required: true
  max_length: 255
  indexed: false
  description: "Original filename"
  validation: Not empty, no path separators
  examples:
    - "IMG_2024.jpg"
    - "Screenshot 2024-01-15.png"
    - "vacation_beach.heic"

media_type:
  type: String (Enum)
  required: true
  fixed_value: "photo"
  indexed: true
  description: "Discriminator for media subtypes"
  note: "Always 'photo' for Photo objects"

mime_type:
  type: String
  required: true
  max_length: 100
  indexed: true
  description: "MIME type of the image file"
  allowed_values:
    - "image/jpeg"
    - "image/png"
    - "image/heic"
    - "image/heif"
    - "image/webp"
    - "image/gif"
    - "image/tiff"
    - "image/bmp"
  examples:
    - "image/jpeg" (most common)
    - "image/png" (screenshots, graphics)
    - "image/heic" (iPhone photos)
```

### File Storage

```yaml
file_size:
  type: Integer
  required: true
  indexed: false
  min: 1
  max: 104857600 (100MB, configurable)
  description: "Size of image file in bytes"
  examples:
    - 2048576 (2MB JPEG)
    - 524288 (512KB PNG)

file_path:
  type: String
  required: true
  max_length: 512
  indexed: false
  description: "Relative path to file on storage"
  pattern: "/media/{user_id}/{year}/{month}/{filename}"
  examples:
    - "/media/user-123/2024/01/IMG_2024.jpg"
    - "/media/ai-456/2024/01/generated_image.png"

hash:
  type: String
  required: true
  length: 64
  indexed: true
  description: "SHA-256 hash for deduplication"
  format: "Lowercase hexadecimal"
  use_case: "Detect duplicate uploads"
  example: "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"
```

---

## Type-Specific Optional Fields

### Image Dimensions

```yaml
width:
  type: Integer
  required: false
  nullable: true
  min: 1
  max: 50000
  description: "Image width in pixels"
  examples:
    - 4032 (iPhone 14 Pro)
    - 1920 (Full HD screenshot)

height:
  type: Integer
  required: false
  nullable: true
  min: 1
  max: 50000
  description: "Image height in pixels"
  examples:
    - 3024 (iPhone 14 Pro)
    - 1080 (Full HD screenshot)
```

### Temporal Data

```yaml
taken_at:
  type: DateTime
  required: false
  nullable: true
  timezone: true (UTC)
  description: "When photo was captured (not uploaded)"
  source: "Extracted from EXIF or user-provided"
  note: "Different from created_at (which is upload time)"
  examples:
    - "2024-01-15T14:30:00Z" (EXIF timestamp)
    - "2023-12-25T09:00:00Z" (Christmas morning photo)
```

### Geolocation

```yaml
gps_latitude:
  type: Float
  required: false
  nullable: true
  min: -90.0
  max: 90.0
  description: "Latitude where photo was taken"
  source: "Extracted from EXIF GPS data"
  examples:
    - 37.7749 (San Francisco)
    - -33.8688 (Sydney)

gps_longitude:
  type: Float
  required: false
  nullable: true
  min: -180.0
  max: 180.0
  description: "Longitude where photo was taken"
  source: "Extracted from EXIF GPS data"
  examples:
    - -122.4194 (San Francisco)
    - 151.2093 (Sydney)
```

### Processing

```yaml
processing_status:
  type: String (Enum)
  required: false
  nullable: true
  default: "pending"
  indexed: true
  description: "Status of post-upload processing"
  allowed_values:
    - "pending" (upload complete, processing not started)
    - "processing" (extracting EXIF, generating thumbnails)
    - "ready" (fully processed and available)
    - "error" (processing failed)
  examples:
    - "ready" (most photos)
    - "processing" (large uploads)

thumbnail_path:
  type: String
  required: false
  nullable: true
  max_length: 512
  description: "Path to generated thumbnail"
  pattern: "/media/{user_id}/{year}/{month}/{filename}_thumb.jpg"
  size: "Usually 300x300 or 400x400"
  examples:
    - "/media/user-123/2024/01/IMG_2024_thumb.jpg"
```

---

## Metadata Schema

The `metadata` JSONB field contains extensible photo-specific data:

### EXIF Data

```json
{
  "exif": {
    "camera_make": "Apple",
    "camera_model": "iPhone 14 Pro",
    "lens_make": "Apple",
    "lens_model": "iPhone 14 Pro back dual wide camera 6.86mm f/1.78",
    "f_number": 1.78,
    "exposure_time": "1/120",
    "iso": 100,
    "focal_length": 6.86,
    "flash": false,
    "orientation": 1,
    "software": "iOS 17.2",
    "date_time_original": "2024:01:15 14:30:00"
  }
}
```

### User Tags

```json
{
  "tags": [
    "vacation",
    "beach",
    "sunset",
    "san francisco"
  ]
}
```

### AI Analysis

```json
{
  "ai_labels": [
    "beach",
    "ocean",
    "sky",
    "sunset",
    "outdoor"
  ],
  "ai_confidence": {
    "beach": 0.95,
    "ocean": 0.92,
    "sky": 0.98
  },
  "faces": [
    {
      "person_id": "person-uuid-123",
      "bbox": [100, 150, 200, 250],
      "confidence": 0.89
    }
  ],
  "objects": [
    {
      "label": "surfboard",
      "bbox": [300, 400, 150, 80],
      "confidence": 0.76
    }
  ]
}
```

### Platform-Specific (Instagram)

```json
{
  "instagram": {
    "post_id": "instagram:Abc123Xyz",
    "post_url": "https://instagram.com/p/Abc123Xyz",
    "caption": "Beautiful sunset at the beach! 🌅",
    "likes_count": 142,
    "comments_count": 23,
    "filter": "valencia",
    "posted_at": "2024-01-15T20:00:00Z"
  }
}
```

### Processing Details

```json
{
  "processing": {
    "thumbnail_generated": true,
    "exif_extracted": true,
    "ai_analysis_completed": true,
    "face_detection_completed": false,
    "processing_duration_ms": 1245
  }
}
```

---

## Relationships (Link Types)

### Outgoing Links (Photo → Other Objects)

```yaml
contains:
  - None (photos don't contain other objects)

source:
  - Integration (photo synced from Instagram, Google Photos, etc.)
  - "Photo --source--> Integration"

duplicate_of:
  - Photo (same content, different upload)
  - "Photo --duplicate_of--> Photo (original)"

variant_of:
  - Photo (edited version, different size)
  - "Photo (edited) --variant_of--> Photo (original)"

related_to:
  - Photo (similar content, same event)
  - Video (same event)
  - Location (where taken)
  - CalendarEvent (when taken)
  - Person (who's in photo)
  - "Photo --related_to--> {Photo|Video|Location|Event|Person}"
```

### Incoming Links (Other Objects → Photo)

```yaml
contains:
  - Album (photo is in album)
  - "Album --contains--> Photo"

referenced_by:
  - SocialPost (photo is in post)
  - Email (photo attached to email)
  - ChatMessage (photo shared in chat)
  - Document (photo embedded in document)
  - "Post --referenced_by--> Photo"

profile_image_of:
  - User (photo is profile picture)
  - SocialAccount (photo is avatar)
  - "User --profile_image_of--> Photo"
```

---

## Validation Rules

### On Upload/Creation

```yaml
filename:
  - Not empty
  - No path separators (/, \)
  - Max 255 characters
  - Suggested format: original filename or generated unique name

media_type:
  - Must be exactly "photo"

mime_type:
  - Must be in allowed list
  - Must match actual file content (validated server-side)

file_size:
  - Must be > 0
  - Must be <= max_upload_size (100MB default, configurable)

file_path:
  - Must be unique
  - Must follow pattern /media/{user_id}/{year}/{month}/...
  - File must exist on disk after upload

hash:
  - Must be 64-character lowercase hex (SHA-256)
  - Calculated server-side from file content
  - Used to detect duplicates

width, height:
  - If provided, must be > 0 and <= 50000
  - Auto-extracted from image if not provided

gps_latitude:
  - If provided, must be >= -90 and <= 90

gps_longitude:
  - If provided, must be >= -180 and <= 180

processing_status:
  - Must be one of: pending, processing, ready, error

metadata:
  - Must be valid JSON object
  - Max 1MB total size
```

### Constraints

```sql
-- Check constraints
CHECK (media_type = 'photo')
CHECK (file_size > 0 AND file_size <= 104857600)
CHECK (width IS NULL OR (width > 0 AND width <= 50000))
CHECK (height IS NULL OR (height > 0 AND height <= 50000))
CHECK (gps_latitude IS NULL OR (gps_latitude >= -90 AND gps_latitude <= 90))
CHECK (gps_longitude IS NULL OR (gps_longitude >= -180 AND gps_longitude <= 180))
CHECK (processing_status IN ('pending', 'processing', 'ready', 'error'))

-- Unique hash per user (same user can't upload same photo twice)
UNIQUE (user_id, hash)

-- Indexes
CREATE INDEX idx_photos_mime_type ON photos(mime_type);
CREATE INDEX idx_photos_hash ON photos(hash);
CREATE INDEX idx_photos_taken_at ON photos(taken_at) WHERE taken_at IS NOT NULL;
CREATE INDEX idx_photos_gps ON photos(gps_latitude, gps_longitude)
  WHERE gps_latitude IS NOT NULL AND gps_longitude IS NOT NULL;
CREATE INDEX idx_photos_processing_status ON photos(processing_status)
  WHERE processing_status != 'ready';
```

---

## API Endpoints

### Upload Photo

```http
POST /api/v1/media/upload
Content-Type: multipart/form-data

Body:
  file: (binary data)
  filename: "IMG_2024.jpg" (optional, extracted from file if not provided)
  taken_at: "2024-01-15T14:30:00Z" (optional)
  tags: ["vacation", "beach"] (optional)

Response: 201 Created
{
  "id": "photo-uuid",
  "user_id": "current-user-uuid",
  "filename": "IMG_2024.jpg",
  "media_type": "photo",
  "mime_type": "image/jpeg",
  "file_size": 2048576,
  "file_path": "/media/user-123/2024/01/IMG_2024.jpg",
  "hash": "a665a459...",
  "width": 4032,
  "height": 3024,
  "taken_at": "2024-01-15T14:30:00Z",
  "gps_latitude": 37.7749,
  "gps_longitude": -122.4194,
  "processing_status": "processing",
  "thumbnail_path": null,
  "created_at": "2024-01-15T15:00:00Z",
  "updated_at": "2024-01-15T15:00:00Z",
  "deleted_at": null,
  "source_type": "upload",
  "source_id": null,
  "metadata": {
    "tags": ["vacation", "beach"]
  }
}
```

### Get Photo

```http
GET /api/v1/media/{id}

Response: 200 OK
{full photo object}
```

### Get Photo File

```http
GET /api/v1/media/{id}/file

Response: 200 OK
Content-Type: image/jpeg
Content-Disposition: inline; filename="IMG_2024.jpg"

(binary image data)
```

### Get Thumbnail

```http
GET /api/v1/media/{id}/thumbnail

Response: 200 OK
Content-Type: image/jpeg

(thumbnail binary data)
```

### List Photos

```http
GET /api/v1/media?media_type=photo&limit=50&offset=0

Response: 200 OK
{
  "items": [
    {photo object},
    {photo object},
    ...
  ],
  "total": 1543,
  "limit": 50,
  "offset": 0
}
```

### Update Photo Metadata

```http
PATCH /api/v1/media/{id}
Content-Type: application/json

{
  "metadata": {
    "tags": ["vacation", "beach", "sunset"]
  }
}

Response: 200 OK
{updated photo object}
```

### Delete Photo

```http
DELETE /api/v1/media/{id}

Response: 204 No Content
(Photo soft-deleted, file remains on disk)
```

### Search Photos

```http
GET /api/v1/media/search?q=beach&media_type=photo&limit=20

Response: 200 OK
{
  "items": [
    {photos matching "beach" in tags, AI labels, or EXIF}
  ],
  "total": 47,
  "limit": 20,
  "offset": 0
}
```

---

## Implementation

### SQLAlchemy Model

```python
from sqlalchemy import Column, String, Integer, Float, DateTime, CheckConstraint, Index
from app.models.base import BaseObject

class Photo(BaseObject):
    """Photo/image media type"""

    __tablename__ = "photos"

    # File Identity
    filename = Column(String(255), nullable=False)
    media_type = Column(String(50), nullable=False, default='photo')
    mime_type = Column(String(100), nullable=False, index=True)

    # File Storage
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(512), nullable=False, unique=True)
    hash = Column(String(64), nullable=False, index=True)

    # Image Dimensions
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)

    # Temporal
    taken_at = Column(DateTime(timezone=True), nullable=True, index=True)

    # Geolocation
    gps_latitude = Column(Float, nullable=True)
    gps_longitude = Column(Float, nullable=True)

    # Processing
    processing_status = Column(
        String(50),
        nullable=True,
        default='pending',
        index=True
    )
    thumbnail_path = Column(String(512), nullable=True)

    # Constraints
    __table_args__ = (
        CheckConstraint("media_type = 'photo'", name='chk_media_type_photo'),
        CheckConstraint("file_size > 0 AND file_size <= 104857600", name='chk_file_size'),
        CheckConstraint("width IS NULL OR (width > 0 AND width <= 50000)", name='chk_width'),
        CheckConstraint("height IS NULL OR (height > 0 AND height <= 50000)", name='chk_height'),
        CheckConstraint("gps_latitude IS NULL OR (gps_latitude >= -90 AND gps_latitude <= 90)", name='chk_latitude'),
        CheckConstraint("gps_longitude IS NULL OR (gps_longitude >= -180 AND gps_longitude <= 180)", name='chk_longitude'),
        CheckConstraint("processing_status IN ('pending', 'processing', 'ready', 'error')", name='chk_processing_status'),
        Index('idx_photos_user_hash', 'user_id', 'hash', unique=True),
        Index('idx_photos_gps', 'gps_latitude', 'gps_longitude', postgresql_where=Column('gps_latitude').isnot(None)),
    )

    def __repr__(self):
        return f"<Photo(id={self.id}, filename={self.filename})>"
```

---

## Examples

### Simple Photo Upload

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-123",
  "filename": "IMG_2024.jpg",
  "media_type": "photo",
  "mime_type": "image/jpeg",
  "file_size": 2048576,
  "file_path": "/media/user-123/2024/01/IMG_2024.jpg",
  "hash": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
  "width": 4032,
  "height": 3024,
  "taken_at": "2024-01-15T14:30:00Z",
  "gps_latitude": 37.7749,
  "gps_longitude": -122.4194,
  "processing_status": "ready",
  "thumbnail_path": "/media/user-123/2024/01/IMG_2024_thumb.jpg",
  "created_at": "2024-01-15T15:00:00Z",
  "updated_at": "2024-01-15T15:05:00Z",
  "deleted_at": null,
  "source_type": "upload",
  "source_id": null,
  "metadata": {}
}
```

### Instagram Photo (with metadata)

```json
{
  "id": "instagram-photo-uuid",
  "user_id": "user-456",
  "filename": "instagram_Abc123Xyz.jpg",
  "media_type": "photo",
  "mime_type": "image/jpeg",
  "file_size": 1524288,
  "file_path": "/media/user-456/2024/01/instagram_Abc123Xyz.jpg",
  "hash": "b775b559...",
  "width": 1080,
  "height": 1080,
  "taken_at": "2024-01-14T18:30:00Z",
  "gps_latitude": null,
  "gps_longitude": null,
  "processing_status": "ready",
  "thumbnail_path": "/media/user-456/2024/01/instagram_Abc123Xyz_thumb.jpg",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:05:00Z",
  "deleted_at": null,
  "source_type": "integration",
  "source_id": "instagram:Abc123Xyz",
  "metadata": {
    "instagram": {
      "post_id": "Abc123Xyz",
      "post_url": "https://instagram.com/p/Abc123Xyz",
      "caption": "Beautiful sunset! 🌅",
      "likes_count": 142,
      "comments_count": 23,
      "filter": "valencia"
    },
    "tags": ["sunset", "beach"],
    "ai_labels": ["sunset", "sky", "ocean"]
  }
}
```

---

**Status:** Active - Phase 1 Priority
**Version:** 1.0
**Parent:** Media → BaseObject
**Created:** 2026-02-04
**Authority:** 0.0.2 - Media Types
