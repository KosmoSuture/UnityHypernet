---
ha: "0.4.0.2.5"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# Screenshot - Screenshot Media Type

**Type ID:** `hypernet.media.screenshot`
**Version:** 1.0
**Category:** 0.0.2 - Media Types
**Parent:** Photo (extends Media → BaseObject)
**Status:** Active
**Created:** 2026-02-04

---

## Identity

```yaml
type_name: "Screenshot"
type_id: "hypernet.media.screenshot"
version: "1.0"
parent_type: "Photo"
category: "0.0.2 - Media Types"
note: "Specialized Photo type with screenshot-specific features"
```

---

## Purpose

### What
Screenshots and screen captures - images of computer/phone screens.

### Why
- Distinct from photos (no EXIF, different metadata needs)
- Often contains text (OCR valuable)
- Reference/documentation use cases
- Usually PNG format (lossless)

### When to Use
- Screen captures from desktop/mobile
- App screenshots
- Web page captures
- Error messages/bug reports

---

## Inherited Fields
All Photo fields plus:

---

## Additional Fields

```yaml
screen_capture_type: String(50)
  - "full_screen", "window", "region", "scrolling"

application: String(255) (app being captured)
  - "Chrome", "Firefox", "VSCode", etc.

window_title: String(500)
ocr_text: Text (extracted text via OCR)

device_info: String(100)
  - "MacBook Pro 16-inch", "iPhone 14 Pro"

screenshot_tool: String(100)
  - "macOS Screenshot", "Windows Snipping Tool", "Snagit"
```

---

## Metadata Schema

```json
{
  "screenshot": {
    "capture_type": "window",
    "application": "Google Chrome",
    "window_title": "Hypernet Documentation - Google Docs",
    "url": "https://docs.google.com/...",
    "device": "MacBook Pro 16-inch",
    "os": "macOS 14.2"
  },
  "ocr": {
    "text": "extracted text content...",
    "language": "en",
    "confidence": 0.92
  },
  "tags": ["documentation", "reference"]
}
```

---

## Relationships

Same as Photo plus:
```yaml
Outgoing:
  - documents: WebPage (screenshot of URL)
  - related_to: Bug, Task (for documentation)

Incoming:
  - referenced_by: Note, Email (as reference)
```

---

## Validation

```sql
-- Inherits all Photo validations
-- Screenshots usually PNG
CHECK (mime_type IN ('image/png', 'image/jpeg', 'image/webp'))

INDEX ON (application, created_at)
INDEX ON (ocr_text) USING GIN -- Full-text search
```

---

## API Endpoints

```http
POST /api/v1/media/upload (with screenshot metadata)
POST /api/v1/media/{id}/ocr (extract text)
GET /api/v1/media/search?q=error&type=screenshot
```

---

**Status:** Active - Phase 1
**Version:** 1.0
