# Integration - External Service Connection

**Type ID:** `hypernet.core.integration`
**Version:** 1.0
**Category:** 0.0.1 - Core Types
**Parent:** BaseObject
**Status:** Active
**Created:** 2026-02-04

---

## Identity

```yaml
type_name: "Integration"
type_id: "hypernet.core.integration"
version: "1.0"
parent_type: "BaseObject"
category: "0.0.1 - Core Types"
```

---

## Purpose

### What
Connections to external services (Instagram, Google Photos, Gmail, etc.).

### Why
- Central to data unification vision
- OAuth2 token management
- Sync state tracking
- Source attribution for imported data

### When to Use
- User connects Instagram account
- Syncing Google Photos
- Importing emails from Gmail
- Any external data source

---

## Required Fields

```yaml
integration_type: String(50)
  - "instagram", "google_photos", "gmail", "dropbox", etc.
  - Indexed for filtering

integration_name: String(200)
  - User-friendly name
  - Example: "My Instagram", "Work Gmail"

status: Enum
  - "pending" (OAuth in progress)
  - "connected" (active and working)
  - "disconnected" (user disconnected)
  - "error" (auth failed or expired)
```

---

## Optional Fields

```yaml
# OAuth2
token_expires_at: DateTime
  - When access token expires
  - Null if token doesn't expire

# Sync State
last_sync_at: DateTime
last_sync_status: Enum
  - "success", "partial", "failed"

sync_cursor: Text
  - Pagination cursor for incremental sync
  - Platform-specific format

items_synced: Integer
  - Count of items imported
  - Increments with each sync

# Status
is_enabled: Boolean
  - User can disable without deleting
```

---

## Metadata Schema

```json
{
  "instagram": {
    "username": "user123",
    "user_id": "17841405793187218",
    "profile_url": "https://instagram.com/user123"
  },
  "google": {
    "email": "user@gmail.com",
    "scope": ["photos", "drive"]
  },
  "sync_config": {
    "auto_sync": true,
    "sync_interval": "hourly",
    "import_likes": true
  },
  "statistics": {
    "total_photos": 1543,
    "total_videos": 87,
    "last_error": null
  }
}
```

---

## Relationships

```yaml
Outgoing:
  - None (integrations are sources, not targets)

Incoming:
  - source: All media types (Photo, Video, etc.)
    - "Photo --source--> Integration"
  - owns: User (user_id FK)
```

---

## Validation

```sql
CHECK (status IN ('pending', 'connected', 'disconnected', 'error'))
CHECK (last_sync_status IS NULL OR last_sync_status IN ('success', 'partial', 'failed'))
CHECK (items_synced >= 0)

INDEX ON (user_id, integration_type)
INDEX ON (status, is_enabled)
```

---

## API Endpoints

```http
# OAuth Flow
GET /api/v1/integrations/oauth/start?type=instagram
  → Redirects to Instagram OAuth
GET /api/v1/integrations/oauth/callback?code=...
  → Completes OAuth, creates Integration

# Management
GET /api/v1/integrations (list user's integrations)
GET /api/v1/integrations/{id}
PATCH /api/v1/integrations/{id} (update settings)
DELETE /api/v1/integrations/{id} (disconnect)

# Sync
POST /api/v1/integrations/{id}/sync (trigger sync)
GET /api/v1/integrations/{id}/sync-status
```

---

## OAuth2 Flow

```yaml
1. User clicks "Connect Instagram"
2. GET /integrations/oauth/start?type=instagram
3. Backend redirects to Instagram OAuth
4. User authorizes on Instagram
5. Instagram redirects to callback with code
6. Backend exchanges code for access_token
7. Creates Integration record (status=connected)
8. Stores access_token in IntegrationSecret table
9. Triggers initial sync
```

---

## Security

```yaml
# Tokens stored separately in IntegrationSecret table
# Never returned via API
# Encrypted at rest
# Rotated automatically when possible
```

---

**Status:** Active - Phase 1 Priority
**Version:** 1.0
