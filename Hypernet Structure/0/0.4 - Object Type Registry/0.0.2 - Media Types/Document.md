---
ha: "0.4.0.2.4"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# Document - Document Media Type

**Type ID:** `hypernet.media.document`
**Version:** 1.0
**Category:** 0.0.2 - Media Types
**Parent:** Media (extends BaseObject)
**Status:** Active
**Created:** 2026-02-04

---

## Identity

```yaml
type_name: "Document"
type_id: "hypernet.media.document"
version: "1.0"
parent_type: "Media"
category: "0.0.2 - Media Types"
```

---

## Purpose

### What
Documents - PDFs, Word docs, spreadsheets, presentations, text files.

### Why
- Critical personal/business documents
- Searchable text content
- Often contains structured data
- Needs versioning and collaboration

### When to Use
- PDF files
- Office documents (Word, Excel, PowerPoint)
- Text files, markdown, code
- E-books

---

## Required Fields

```yaml
filename: String(255)
media_type: "document" (fixed)
mime_type: String(100)
  - application/pdf
  - application/vnd.openxmlformats-officedocument.wordprocessingml.document (DOCX)
  - application/vnd.openxmlformats-officedocument.spreadsheetml.sheet (XLSX)
  - application/vnd.openxmlformats-officedocument.presentationml.presentation (PPTX)
  - text/plain
  - text/markdown
  - application/epub+zip

file_size: Integer (max 100MB)
file_path: String(512)
hash: String(64)
```

---

## Optional Fields

```yaml
document_type: String(50)
  - "pdf", "word", "excel", "powerpoint", "text", "markdown", "ebook"

page_count: Integer
word_count: Integer
language: String(10) (ISO 639-1)
  - "en", "es", "fr", "de", etc.

author: String(255) (from metadata)
title: String(500) (from metadata or filename)

created_date: DateTime (document creation, not upload)
modified_date: DateTime (last edit)

processing_status: Enum
  - pending, extracting_text, indexed, ready, error

text_content: Text (extracted text for search)
preview_path: String(512) (PDF preview images)
```

---

## Metadata Schema

```json
{
  "pdf_info": {
    "producer": "Adobe PDF",
    "pdf_version": "1.7",
    "encrypted": false,
    "page_count": 25
  },
  "office_info": {
    "application": "Microsoft Word",
    "created_by": "John Doe",
    "company": "Acme Corp"
  },
  "tags": ["contract", "legal", "2024"],
  "extracted_entities": {
    "emails": ["john@example.com"],
    "dates": ["2024-01-15"],
    "amounts": ["$1,000.00"]
  },
  "gdrive": {
    "doc_id": "...",
    "share_link": "..."
  }
}
```

---

## Relationships

```yaml
Outgoing:
  - source: Integration (Google Drive, Dropbox)
  - duplicate_of: Document
  - variant_of: Document (different version)
  - related_to: Email, Transaction, Event

Incoming:
  - contains: Folder, Project
  - referenced_by: Email, Note
```

---

## Validation

```sql
CHECK (media_type = 'document')
CHECK (file_size > 0 AND file_size <= 104857600) -- 100MB
CHECK (page_count IS NULL OR page_count > 0)

INDEX ON (mime_type, document_type)
INDEX ON (text_content) USING GIN -- Full-text search
```

---

## API Endpoints

```http
POST /api/v1/media/upload
GET /api/v1/media/{id}/preview (PDF page images)
GET /api/v1/media/{id}/text (extracted text)
POST /api/v1/media/{id}/extract (OCR if needed)
GET /api/v1/media/search?q=contract (full-text search)
```

---

**Status:** Active - Phase 1
**Version:** 1.0
