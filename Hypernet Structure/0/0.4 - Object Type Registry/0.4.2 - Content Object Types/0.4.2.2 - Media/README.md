---
ha: "0.4.2.2"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.2.2 - Media

**Type Name:** Media
**Category:** Content (0.4.2)
**Full Schema:** 0.5.4 Media Object Schema

## Schema

```yaml
media:
  media_type: enum       # image | video | audio
  mime_type: string      # MIME type (e.g., "image/jpeg")
  file_path: string      # Location of the binary file
  file_size: integer     # Size in bytes
  duration: float        # For video/audio, in seconds
  dimensions: object     # For images/video: width, height
  captured_at: datetime  # When the media was originally created
  device: string         # HA of the capturing device
  location: object       # GPS coordinates if available
  thumbnails: list       # Generated preview versions
```

## Validation Rules

1. Media type must match MIME type category
2. File must exist at the declared path
3. Dimensions are required for image and video types
4. Duration is required for video and audio types
