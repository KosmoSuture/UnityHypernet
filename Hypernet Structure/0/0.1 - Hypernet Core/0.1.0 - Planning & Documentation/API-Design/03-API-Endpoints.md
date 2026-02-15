# Hypernet Core - API Endpoints Specification

**Version:** 0.1.0 (Phase 1)
**Last Updated:** 2026-02-03
**Status:** Design Phase
**Base URL:** `https://{server}:8443/api/v1`

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Common Patterns](#common-patterns)
4. [Auth Endpoints](#auth-endpoints)
5. [User Endpoints](#user-endpoints)
6. [Media Endpoints](#media-endpoints)
7. [Album Endpoints](#album-endpoints)
8. [Integration Endpoints](#integration-endpoints)
9. [Link Endpoints](#link-endpoints)
10. [System Endpoints](#system-endpoints)
11. [Error Responses](#error-responses)

---

## Overview

### API Design Principles

1. **RESTful** - Resources identified by URLs, operations via HTTP methods
2. **Versioned** - `/api/v1/...` allows future breaking changes in v2
3. **JSON** - All request/response bodies in JSON (except file uploads)
4. **Stateless** - JWT tokens, no server-side sessions
5. **Paginated** - Large result sets use cursor or offset pagination
6. **Filterable** - Common filters: `?type=photo&date_from=2026-01-01`
7. **Sortable** - `?sort_by=created_at&sort_order=desc`
8. **HATEOAS** - Responses include links to related resources (optional Phase 2)

### HTTP Methods

| Method | Purpose | Idempotent | Safe |
|--------|---------|------------|------|
| `GET` | Retrieve resource(s) | Yes | Yes |
| `POST` | Create new resource | No | No |
| `PUT` | Replace entire resource | Yes | No |
| `PATCH` | Update partial resource | No | No |
| `DELETE` | Delete resource | Yes | No |

### Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| `200 OK` | Success | GET, PATCH, PUT successful |
| `201 Created` | Resource created | POST successful |
| `204 No Content` | Success, no body | DELETE successful |
| `400 Bad Request` | Invalid input | Validation failed |
| `401 Unauthorized` | Not authenticated | Missing/invalid token |
| `403 Forbidden` | Not authorized | Authenticated but no permission |
| `404 Not Found` | Resource doesn't exist | ID not found |
| `409 Conflict` | Duplicate/constraint violation | Unique constraint failed |
| `422 Unprocessable Entity` | Semantic error | Business logic failed |
| `429 Too Many Requests` | Rate limited | Exceeded rate limit |
| `500 Internal Server Error` | Server error | Unexpected error |

---

## Authentication

### JWT Bearer Tokens

All authenticated endpoints require:
```http
Authorization: Bearer {access_token}
```

### Token Structure

**Access Token:**
- Short-lived (15 minutes)
- Contains: `user_id`, `email`, `is_admin`, `exp`, `iat`
- Used for API requests

**Refresh Token:**
- Long-lived (30 days)
- Used only to get new access tokens
- Stored securely by client (httpOnly cookie or secure storage)

---

## Common Patterns

### Pagination

**Offset-Based (Default):**
```http
GET /api/v1/media?limit=50&offset=0
```

**Response:**
```json
{
  "items": [...],
  "total": 250,
  "limit": 50,
  "offset": 0,
  "has_more": true
}
```

**Cursor-Based (for large datasets):**
```http
GET /api/v1/media?limit=50&cursor=abc123xyz
```

**Response:**
```json
{
  "items": [...],
  "next_cursor": "def456uvw",
  "has_more": true
}
```

### Filtering

```http
GET /api/v1/media?type=photo&date_from=2026-01-01&date_to=2026-01-31
```

**Common Filters:**
- `type` - Object type or media type
- `date_from`, `date_to` - Date range (ISO 8601)
- `search` - Full-text search (filename, description)
- `tag` - Filter by tag (Phase 2)

### Sorting

```http
GET /api/v1/media?sort_by=taken_at&sort_order=desc
```

**Common Sort Fields:**
- `created_at` - When object was created
- `updated_at` - When object was last modified
- `taken_at` - When photo/video was taken (media only)
- `name` - Alphabetical (albums)
- `size` - File size (media)

### Partial Responses (Future)

```http
GET /api/v1/media/123?fields=id,filename,size
```

Only returns requested fields (reduces bandwidth).

---

## Auth Endpoints

### Register

Create new user account.

```http
POST /api/v1/auth/register
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "display_name": "John Smith"
}
```

**Validation:**
- `email`: Valid email format, unique, max 255 chars
- `password`: Min 12 chars, must include uppercase, lowercase, number, special char
- `display_name`: Optional, max 100 chars

**Response (201 Created):**
```json
{
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "display_name": "John Smith",
    "email_verified": false,
    "created_at": "2026-02-03T12:00:00Z"
  },
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 900
}
```

**Errors:**
- `409 Conflict` - Email already registered
- `400 Bad Request` - Invalid email or password format

---

### Login

Authenticate user and get tokens.

```http
POST /api/v1/auth/login
```

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "display_name": "John Smith"
  },
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 900
}
```

**Errors:**
- `401 Unauthorized` - Invalid email or password
- `403 Forbidden` - Account disabled

---

### Refresh Token

Get new access token using refresh token.

```http
POST /api/v1/auth/refresh
```

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 900
}
```

**Errors:**
- `401 Unauthorized` - Invalid or expired refresh token

---

### Logout

Invalidate refresh token (revoke access).

```http
POST /api/v1/auth/logout
Authorization: Bearer {access_token}
```

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response (204 No Content)**

---

## User Endpoints

### Get Current User

Get authenticated user's profile.

```http
GET /api/v1/users/me
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "display_name": "John Smith",
  "avatar_url": null,
  "email_verified": true,
  "is_active": true,
  "is_admin": false,
  "created_at": "2026-01-01T00:00:00Z",
  "last_login_at": "2026-02-03T12:00:00Z",
  "storage_used": 15728640000,
  "storage_quota": 107374182400,
  "metadata": {}
}
```

---

### Update User Profile

Update authenticated user's profile.

```http
PATCH /api/v1/users/me
Authorization: Bearer {access_token}
```

**Request:**
```json
{
  "display_name": "John A. Smith",
  "avatar_url": "https://example.com/avatar.jpg",
  "metadata": {
    "timezone": "America/Los_Angeles",
    "language": "en-US"
  }
}
```

**Response (200 OK):**
```json
{
  "id": "user-uuid",
  "display_name": "John A. Smith",
  "avatar_url": "https://example.com/avatar.jpg",
  ...
}
```

---

### Change Password

Change authenticated user's password.

```http
POST /api/v1/users/me/change-password
Authorization: Bearer {access_token}
```

**Request:**
```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewPassword456!"
}
```

**Response (204 No Content)**

**Errors:**
- `401 Unauthorized` - Current password incorrect
- `400 Bad Request` - New password doesn't meet requirements

---

## Media Endpoints

### Upload Media

Upload photo, video, or file.

```http
POST /api/v1/media/upload
Authorization: Bearer {access_token}
Content-Type: multipart/form-data
```

**Request:**
```
file: (binary data)
description: "Optional description"
tags: ["vacation", "beach"]
```

**Processing Steps:**
1. Validate file type and size
2. Scan for malware (ClamAV)
3. Generate unique ID (UUID)
4. Extract EXIF metadata
5. Calculate hash (SHA-256)
6. Save to `/media/{user_id}/media/{year}/{month}/{id}.{ext}`
7. Generate thumbnails (async)
8. Insert into database
9. Return media object

**Response (201 Created):**
```json
{
  "id": "media-uuid",
  "type": "media",
  "filename": "photo.jpg",
  "media_type": "photo",
  "mime_type": "image/jpeg",
  "size": 2457600,
  "width": 4032,
  "height": 3024,
  "file_path": "users/.../media/2026/02/media-uuid.jpg",
  "hash": "9f86d081...",
  "taken_at": "2026-02-01T14:23:45Z",
  "processing_status": "processing",
  "thumbnail_generated": false,
  "created_at": "2026-02-03T12:00:00Z",
  "metadata": {
    "exif": {...},
    "tags": ["vacation", "beach"],
    "description": "Optional description"
  }
}
```

**Errors:**
- `400 Bad Request` - Invalid file type or size
- `413 Payload Too Large` - File exceeds size limit
- `422 Unprocessable Entity` - Malware detected
- `507 Insufficient Storage` - User quota exceeded

---

### List Media

List user's media with filtering and pagination.

```http
GET /api/v1/media?type=photo&limit=50&offset=0&sort_by=taken_at&sort_order=desc
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `type` - Media type: `photo`, `video`, `document`, `other`
- `date_from`, `date_to` - Taken date range (ISO 8601)
- `search` - Search filename or description
- `limit` - Items per page (default: 50, max: 100)
- `offset` - Pagination offset (default: 0)
- `sort_by` - Sort field: `taken_at`, `created_at`, `filename`, `size`
- `sort_order` - Sort direction: `asc`, `desc` (default)

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "media-1-uuid",
      "filename": "beach.jpg",
      "media_type": "photo",
      "taken_at": "2026-02-01T14:00:00Z",
      "thumbnail_url": "/api/v1/media/media-1-uuid/thumbnail/medium",
      ...
    },
    {
      "id": "media-2-uuid",
      "filename": "sunset.jpg",
      ...
    }
  ],
  "total": 250,
  "limit": 50,
  "offset": 0,
  "has_more": true
}
```

---

### Get Media

Get single media object by ID.

```http
GET /api/v1/media/{media_id}
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": "media-uuid",
  "type": "media",
  "filename": "photo.jpg",
  "media_type": "photo",
  "size": 2457600,
  "width": 4032,
  "height": 3024,
  "taken_at": "2026-02-01T14:23:45Z",
  "latitude": 34.0195,
  "longitude": -118.4912,
  "download_url": "/api/v1/media/media-uuid/download",
  "thumbnail_url": "/api/v1/media/media-uuid/thumbnail/large",
  "metadata": {
    "exif": {...},
    "tags": ["vacation", "beach"]
  },
  "created_at": "2026-02-03T12:00:00Z",
  "updated_at": "2026-02-03T12:00:00Z"
}
```

**Errors:**
- `404 Not Found` - Media ID doesn't exist or user doesn't own it

---

### Download Media

Download original media file.

```http
GET /api/v1/media/{media_id}/download
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```
Content-Type: image/jpeg (or appropriate MIME type)
Content-Disposition: attachment; filename="photo.jpg"
Content-Length: 2457600

(binary data)
```

**Streaming:** Uses chunked transfer for large files.

---

### Get Thumbnail

Get thumbnail of media.

```http
GET /api/v1/media/{media_id}/thumbnail/{size}
Authorization: Bearer {access_token}
```

**Sizes:**
- `small` - 150x150px
- `medium` - 400x400px
- `large` - 800x800px

**Response (200 OK):**
```
Content-Type: image/jpeg
Content-Length: 45678

(binary data - thumbnail)
```

**Caching:** Includes `Cache-Control` and `ETag` headers for browser caching.

---

### Update Media

Update media metadata.

```http
PATCH /api/v1/media/{media_id}
Authorization: Bearer {access_token}
```

**Request:**
```json
{
  "metadata": {
    "description": "Updated description",
    "tags": ["vacation", "beach", "sunset"]
  }
}
```

**Immutable Fields:**
- Cannot change: `filename`, `size`, `hash`, `taken_at` (from EXIF)
- Can update: `metadata` (description, tags, etc.)

**Response (200 OK):**
```json
{
  "id": "media-uuid",
  "metadata": {
    "description": "Updated description",
    "tags": ["vacation", "beach", "sunset"],
    "exif": {...}
  },
  "updated_at": "2026-02-03T14:00:00Z"
}
```

---

### Delete Media

Soft delete media (can be restored).

```http
DELETE /api/v1/media/{media_id}
Authorization: Bearer {access_token}
```

**Response (204 No Content)**

**Side Effects:**
- Sets `deleted_at` timestamp
- Deletes all links to/from media
- Does NOT delete file immediately (deleted after retention period)
- Decrements user's `storage_used` (eventually)

---

## Album Endpoints

### Create Album

Create new album.

```http
POST /api/v1/albums
Authorization: Bearer {access_token}
```

**Request:**
```json
{
  "name": "Vacation 2026",
  "description": "Photos from California trip",
  "sort_order": "date_desc"
}
```

**Response (201 Created):**
```json
{
  "id": "album-uuid",
  "type": "album",
  "name": "Vacation 2026",
  "description": "Photos from California trip",
  "cover_media_id": null,
  "sort_order": "date_desc",
  "media_count": 0,
  "visibility": "private",
  "created_at": "2026-02-03T12:00:00Z",
  "metadata": {}
}
```

---

### List Albums

List user's albums.

```http
GET /api/v1/albums?limit=50&offset=0
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "album-1-uuid",
      "name": "Vacation 2026",
      "media_count": 42,
      "cover_media_id": "media-uuid",
      "cover_thumbnail_url": "/api/v1/media/media-uuid/thumbnail/medium"
    },
    {
      "id": "album-2-uuid",
      "name": "Family Photos",
      "media_count": 150
    }
  ],
  "total": 10,
  "limit": 50,
  "offset": 0
}
```

---

### Get Album

Get album details.

```http
GET /api/v1/albums/{album_id}
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": "album-uuid",
  "name": "Vacation 2026",
  "description": "Photos from California trip",
  "media_count": 42,
  "cover_media_id": "media-uuid",
  "created_at": "2026-02-03T12:00:00Z"
}
```

---

### Get Album Media

Get media in album (convenience endpoint for links).

```http
GET /api/v1/albums/{album_id}/media?limit=50&offset=0
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "media-1-uuid",
      "filename": "beach.jpg",
      "taken_at": "2026-02-01T14:00:00Z",
      "thumbnail_url": "...",
      "link_id": "link-uuid",  // Link that connects media to album
      "sort_order": 0
    },
    {
      "id": "media-2-uuid",
      "filename": "sunset.jpg",
      "link_id": "link-uuid-2",
      "sort_order": 1
    }
  ],
  "total": 42
}
```

---

### Add Media to Album

Add media to album (creates link).

```http
POST /api/v1/albums/{album_id}/media
Authorization: Bearer {access_token}
```

**Request:**
```json
{
  "media_ids": ["media-1-uuid", "media-2-uuid"],
  "sort_order": "append"  // or specific positions
}
```

**Response (201 Created):**
```json
{
  "links_created": 2,
  "links": [
    {
      "id": "link-1-uuid",
      "from_object_id": "album-uuid",
      "to_object_id": "media-1-uuid",
      "sort_order": 0
    },
    {
      "id": "link-2-uuid",
      "from_object_id": "album-uuid",
      "to_object_id": "media-2-uuid",
      "sort_order": 1
    }
  ]
}
```

---

### Remove Media from Album

Remove media from album (deletes link).

```http
DELETE /api/v1/albums/{album_id}/media/{media_id}
Authorization: Bearer {access_token}
```

**Response (204 No Content)**

**Note:** Deletes link but does NOT delete media object.

---

### Update Album

Update album properties.

```http
PATCH /api/v1/albums/{album_id}
Authorization: Bearer {access_token}
```

**Request:**
```json
{
  "name": "California Vacation 2026",
  "cover_media_id": "media-uuid"
}
```

**Response (200 OK):**
```json
{
  "id": "album-uuid",
  "name": "California Vacation 2026",
  "cover_media_id": "media-uuid",
  "updated_at": "2026-02-03T14:00:00Z"
}
```

---

### Delete Album

Delete album (soft delete).

```http
DELETE /api/v1/albums/{album_id}
Authorization: Bearer {access_token}
```

**Response (204 No Content)**

**Side Effects:**
- Deletes all links where album is `from_object`
- Does NOT delete media in album (only links)

---

## Integration Endpoints

### List Integrations

List user's connected integrations.

```http
GET /api/v1/integrations
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "integration-uuid",
      "integration_type": "instagram",
      "integration_name": "@johnsmith",
      "status": "connected",
      "is_enabled": true,
      "last_sync_at": "2026-02-03T10:00:00Z",
      "items_synced": 150,
      "metadata": {
        "username": "johnsmith",
        "profile_url": "https://instagram.com/johnsmith"
      }
    }
  ],
  "total": 1
}
```

**Note:** `access_token` and `refresh_token` are NEVER returned in responses.

---

### Connect Integration (OAuth Start)

Start OAuth flow for integration.

```http
GET /api/v1/integrations/{type}/connect
Authorization: Bearer {access_token}
```

**Example:** `GET /api/v1/integrations/google-photos/connect`

**Response (200 OK):**
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...&redirect_uri=...&scope=...",
  "state": "random-state-token"
}
```

**Client Flow:**
1. Client receives `auth_url`
2. Client redirects user to `auth_url`
3. User authorizes on external service (Google, Instagram, etc.)
4. External service redirects to callback URL with code
5. Callback handler exchanges code for tokens and creates Integration object

---

### OAuth Callback (Internal)

Handle OAuth callback from external service.

```http
GET /api/v1/integrations/{type}/callback?code=abc123&state=xyz789
```

**Processing:**
1. Verify `state` parameter
2. Exchange `code` for `access_token` and `refresh_token`
3. Get user info from external API
4. Create Integration object
5. Encrypt and store tokens
6. Redirect client to success page

**Response:** Redirect to frontend success page

---

### Sync Integration

Trigger sync from integration.

```http
POST /api/v1/integrations/{integration_id}/sync
Authorization: Bearer {access_token}
```

**Request (Optional):**
```json
{
  "full_sync": false,  // false = incremental, true = full re-sync
  "limit": 100  // Max items to sync in this batch
}
```

**Response (202 Accepted):**
```json
{
  "status": "syncing",
  "job_id": "sync-job-uuid",
  "started_at": "2026-02-03T12:00:00Z"
}
```

**Sync Process (Async):**
1. Fetch items from external API (paginated)
2. For each item:
   - Check if already imported (via source link)
   - If new, download media and create Media object
   - Create Link (media → integration)
3. Update integration sync state (cursor, last_sync_at)
4. Return sync status

---

### Get Sync Status

Check status of sync job.

```http
GET /api/v1/integrations/{integration_id}/sync-status
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "status": "complete",  // "pending", "syncing", "complete", "failed"
  "started_at": "2026-02-03T12:00:00Z",
  "completed_at": "2026-02-03T12:05:00Z",
  "items_synced": 25,
  "items_skipped": 5,  // Already existed
  "items_failed": 0,
  "errors": []
}
```

---

### Disconnect Integration

Disconnect integration (soft delete).

```http
DELETE /api/v1/integrations/{integration_id}
Authorization: Bearer {access_token}
```

**Response (204 No Content)**

**Options:**
```json
{
  "delete_media": false  // If true, also delete all media imported from this integration
}
```

**Side Effects:**
- Revokes OAuth tokens (calls external API if supported)
- Deletes Integration object
- Optionally deletes linked Media objects

---

## Link Endpoints

### Create Link

Create relationship between objects.

```http
POST /api/v1/links
Authorization: Bearer {access_token}
```

**Request:**
```json
{
  "from_object_id": "album-uuid",
  "from_object_type": "album",
  "to_object_id": "media-uuid",
  "to_object_type": "media",
  "link_type": "contains",
  "sort_order": 0
}
```

**Response (201 Created):**
```json
{
  "id": "link-uuid",
  "from_object_id": "album-uuid",
  "to_object_id": "media-uuid",
  "link_type": "contains",
  "strength": 1.0,
  "created_at": "2026-02-03T12:00:00Z"
}
```

**Errors:**
- `400 Bad Request` - Invalid link type or object combination
- `404 Not Found` - from_object or to_object doesn't exist
- `409 Conflict` - Link already exists

---

### List Links

List links for an object.

```http
GET /api/v1/objects/{object_id}/links?direction=outgoing&type=contains
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `direction` - `outgoing` (from object), `incoming` (to object), `both`
- `type` - Filter by link type

**Response (200 OK):**
```json
{
  "links": [
    {
      "id": "link-uuid",
      "link_type": "contains",
      "from_object_id": "album-uuid",
      "to_object_id": "media-uuid",
      "to_object": {  // Embedded for convenience
        "id": "media-uuid",
        "type": "media",
        "filename": "photo.jpg"
      }
    }
  ],
  "total": 1
}
```

---

### Update Link

Update link properties.

```http
PATCH /api/v1/links/{link_id}
Authorization: Bearer {access_token}
```

**Request:**
```json
{
  "sort_order": 10,
  "strength": 1.0,
  "metadata": {
    "user_confirmed": true
  }
}
```

**Immutable:** Cannot change `from_object_id`, `to_object_id`, `link_type`.

---

### Delete Link

Delete relationship.

```http
DELETE /api/v1/links/{link_id}
Authorization: Bearer {access_token}
```

**Response (204 No Content)**

---

## System Endpoints

### Health Check

Check if API is running.

```http
GET /health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-02-03T12:00:00Z"
}
```

---

### Version Info

Get API version and capabilities.

```http
GET /api/v1/version
```

**Response (200 OK):**
```json
{
  "version": "0.1.0",
  "api_version": "v1",
  "capabilities": ["media", "albums", "integrations"],
  "integrations_available": ["instagram", "google-photos"]
}
```

---

### Metrics (Admin Only)

Prometheus metrics endpoint.

```http
GET /metrics
Authorization: Bearer {admin_access_token}
```

**Response (200 OK):**
```
# TYPE hypernet_api_requests_total counter
hypernet_api_requests_total{method="GET",endpoint="/api/v1/media",status="200"} 1234
...
```

---

## Error Responses

### Standard Error Format

All errors return RFC 7807 Problem Details:

```json
{
  "type": "https://hypernet.io/errors/validation-error",
  "title": "Validation Error",
  "status": 400,
  "detail": "Invalid email format",
  "instance": "/api/v1/auth/register",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

### Common Error Types

**Validation Error (400):**
```json
{
  "type": "validation-error",
  "title": "Validation Error",
  "status": 400,
  "errors": [
    {"field": "email", "message": "Email is required"},
    {"field": "password", "message": "Password must be at least 12 characters"}
  ]
}
```

**Unauthorized (401):**
```json
{
  "type": "unauthorized",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Invalid or expired token"
}
```

**Forbidden (403):**
```json
{
  "type": "forbidden",
  "title": "Forbidden",
  "status": 403,
  "detail": "You don't have permission to access this resource"
}
```

**Not Found (404):**
```json
{
  "type": "not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "Media object with ID 'abc123' not found"
}
```

**Rate Limited (429):**
```json
{
  "type": "rate-limited",
  "title": "Too Many Requests",
  "status": 429,
  "detail": "Rate limit exceeded. Try again in 60 seconds.",
  "retry_after": 60
}
```

---

## Next Steps

- [ ] Review API endpoints
- [ ] Generate OpenAPI/Swagger spec (auto-generated from FastAPI)
- [ ] Implement endpoint handlers in FastAPI
- [ ] Write integration tests for each endpoint
- [ ] Add rate limiting middleware
- [ ] Set up API documentation UI (Swagger/ReDoc)

---

**Status:** Draft - Ready for implementation
**Next:** Database schema design and implementation
