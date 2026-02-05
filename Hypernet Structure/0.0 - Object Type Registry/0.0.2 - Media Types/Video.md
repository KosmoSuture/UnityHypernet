# Video - Video Media Type

**Type ID:** `hypernet.media.video`
**Version:** 1.0
**Category:** 0.0.2 - Media Types
**Parent:** Media (extends BaseObject)
**Status:** Active
**Created:** 2026-02-04

---

## Identity

```yaml
type_name: "Video"
type_id: "hypernet.media.video"
version: "1.0"
parent_type: "Media"
category: "0.0.2 - Media Types"
```

---

## Purpose

### What
Video files - recorded videos, screen recordings, animations, and any motion picture content.

### Why
- Second most common personal media after photos
- Rich temporal content (duration, frame rate, codec)
- Large file sizes require special handling
- Streaming and transcoding needs
- Platform integrations (YouTube, TikTok, Instagram Reels)

### When to Use
- Camera-recorded videos (MP4, MOV, etc.)
- Screen recordings
- Downloaded videos from social platforms
- Live streams and recordings

---

## Inherited Fields
```yaml
# From BaseObject
id, user_id, created_at, updated_at, deleted_at, source_type, source_id, metadata
```

---

## Required Fields

```yaml
filename: String(255)
media_type: "video" (fixed)
mime_type: String(100)
  - video/mp4
  - video/quicktime
  - video/x-msvideo (AVI)
  - video/webm
  - video/x-matroska (MKV)

file_size: Integer (bytes, max 5GB)
file_path: String(512)
hash: String(64) (SHA-256)
```

---

## Optional Fields

```yaml
width: Integer (1-7680 for 8K)
height: Integer (1-4320 for 8K)
duration: Float (seconds)
  - Example: 125.5 (2 minutes 5.5 seconds)

codec: String(50)
  - "h264", "h265", "vp9", "av1"

bitrate: Integer (bits per second)
frame_rate: Float (fps)
  - Example: 29.97, 30.0, 60.0

has_audio: Boolean
audio_codec: String(50)
  - "aac", "mp3", "opus"

recorded_at: DateTime (when video was recorded)
gps_latitude: Float (-90 to 90)
gps_longitude: Float (-90 to 180)

processing_status: Enum
  - pending, processing, ready, error

thumbnail_path: String(512) (frame extract for preview)
preview_path: String(512) (low-res version for preview)
```

---

## Metadata Schema

```json
{
  "codec_details": {
    "video_codec": "h264",
    "audio_codec": "aac",
    "container": "mp4",
    "profile": "high"
  },
  "tags": ["vacation", "family"],
  "ai_analysis": {
    "scenes": [
      {"start": 0, "end": 10, "label": "beach"},
      {"start": 10, "end": 25, "label": "sunset"}
    ],
    "objects_detected": ["person", "ocean", "sky"],
    "audio_transcript": "..."
  },
  "youtube": {
    "video_id": "dQw4w9WgXcQ",
    "title": "...",
    "views": 1000000
  }
}
```

---

## Relationships

```yaml
Outgoing:
  - source: Integration (synced from YouTube, etc.)
  - duplicate_of: Video
  - variant_of: Video (different resolution/codec)
  - related_to: Photo, Video, Event, Location

Incoming:
  - contains: Album, Playlist
  - referenced_by: Post, Message
```

---

## Validation

```sql
CHECK (media_type = 'video')
CHECK (file_size > 0 AND file_size <= 5368709120) -- 5GB
CHECK (duration IS NULL OR duration > 0)
CHECK (width IS NULL OR (width > 0 AND width <= 7680))
CHECK (height IS NULL OR (height > 0 AND height <= 4320))

UNIQUE (user_id, hash)
INDEX ON (mime_type, processing_status)
```

---

## API Endpoints

```http
POST /api/v1/media/upload (video upload)
GET /api/v1/media/{id}/stream (video streaming)
GET /api/v1/media/{id}/thumbnail (preview frame)
POST /api/v1/media/{id}/transcode (convert format)
```

---

**Status:** Active - Phase 1
**Version:** 1.0
