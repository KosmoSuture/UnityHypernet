# 0.1.4 - Integration Plugins

## Overview

This folder contains integration plugins for connecting Hypernet to external services and platforms.

**Purpose:** Enable users to import their data from external services into their Hypernet account.

## Integration Architecture

### Plugin System Design

Each integration plugin follows a standard pattern:
1. **OAuth Authentication** - Secure connection to external service
2. **Data Import** - Fetch user data from external API
3. **Data Transformation** - Convert to Hypernet data models
4. **Storage** - Save to Hypernet database via internal APIs
5. **Sync** - Periodic updates to keep data fresh

### Integration Types

**Personal Data Integrations:**
- Google Photos (photos, videos)
- Google Drive (documents, files)
- Gmail (emails, contacts)
- Google Calendar (events, meetings)
- Apple Photos (iOS/macOS media)
- iCloud Drive (documents)
- Dropbox (files, photos)
- Instagram (posts, stories)
- Twitter/X (tweets, media)
- Facebook (posts, photos)
- LinkedIn (posts, profile)
- Spotify (listening history)
- Netflix (viewing history)
- Amazon (purchase history)
- Banking/Finance (transactions)

**Productivity Integrations:**
- Notion (notes, databases)
- Evernote (notes)
- Todoist (tasks)
- Asana (tasks, projects)
- Trello (boards, cards)
- Slack (messages, files)
- Microsoft 365 (email, calendar, OneDrive)

**Health & Fitness:**
- Apple Health (health data)
- Google Fit (fitness data)
- Fitbit (activity, health)
- MyFitnessPal (nutrition)
- Strava (workouts)

## Plugin Structure

```
0.1.4 - Integration Plugins/
├── 0.1.4.0 - Plugin Framework/
│   ├── base_plugin.py
│   ├── oauth_handler.py
│   ├── data_mapper.py
│   └── sync_scheduler.py
├── 0.1.4.1 - Google Integrations/
│   ├── google_photos/
│   ├── google_drive/
│   ├── gmail/
│   └── google_calendar/
├── 0.1.4.2 - Apple Integrations/
│   ├── apple_photos/
│   ├── icloud_drive/
│   └── apple_health/
├── 0.1.4.3 - Social Media/
│   ├── instagram/
│   ├── twitter/
│   ├── facebook/
│   ├── linkedin/
│   └── tiktok/
├── 0.1.4.4 - Productivity/
│   ├── notion/
│   ├── evernote/
│   ├── todoist/
│   ├── slack/
│   └── microsoft_365/
├── 0.1.4.5 - Cloud Storage/
│   ├── dropbox/
│   ├── box/
│   └── onedrive/
├── 0.1.4.6 - Finance/
│   ├── plaid/ (banking)
│   ├── stripe/ (payments)
│   └── quickbooks/
└── 0.1.4.7 - Health & Fitness/
    ├── apple_health/
    ├── google_fit/
    ├── fitbit/
    └── strava/
```

## Standard Plugin Template

Each plugin contains:

```
plugin_name/
├── README.md (integration details)
├── plugin.py (main plugin class)
├── oauth.py (OAuth flow)
├── mapper.py (data transformation)
├── sync.py (sync scheduler)
├── config.yaml (plugin configuration)
└── tests/
    ├── test_oauth.py
    ├── test_import.py
    └── test_sync.py
```

## Plugin Development Guide

### 1. OAuth Setup

```python
class GooglePhotosPlugin(BasePlugin):
    def __init__(self):
        self.client_id = config.GOOGLE_CLIENT_ID
        self.client_secret = config.GOOGLE_CLIENT_SECRET
        self.scopes = ['https://www.googleapis.com/auth/photoslibrary.readonly']

    def get_auth_url(self, user_id):
        # Generate OAuth URL

    def handle_callback(self, code, user_id):
        # Exchange code for token
        # Store token in Integration model
```

### 2. Data Import

```python
    def import_data(self, user_id, integration_id):
        # Get access token from Integration model
        # Fetch data from external API
        # Transform to Hypernet format
        # Save via internal APIs
```

### 3. Data Transformation

```python
    def transform_photo(self, external_photo):
        return Media(
            user_id=self.user_id,
            media_type='photo',
            file_path=external_photo['url'],
            file_size_bytes=external_photo['size'],
            mime_type=external_photo['mimeType'],
            title=external_photo['filename'],
            taken_at=external_photo['creationTime'],
            source_integration_id=self.integration_id,
            source_platform='google_photos',
            source_object_id=external_photo['id']
        )
```

### 4. Sync Scheduling

```python
    def schedule_sync(self, integration_id):
        # Set up periodic sync (daily, weekly, etc.)
        # Update only changed data
        # Track last_sync_at
```

## Integration Roadmap

### Phase 1: MVP (Month 1-3)
**Target: 10 integrations**

Priority integrations for private beta:
1. ✅ Google Photos (photos, videos)
2. ✅ Gmail (emails, contacts)
3. ✅ Google Calendar (events)
4. ✅ Google Drive (documents)
5. ⏳ Instagram (posts, stories)
6. ⏳ Twitter/X (tweets)
7. ⏳ Apple Photos (iOS users)
8. ⏳ Notion (notes, databases)
9. ⏳ Spotify (listening history)
10. ⏳ Banking (via Plaid)

### Phase 2: Public Beta (Month 4-9)
**Target: 25 integrations**

Add:
- Facebook, LinkedIn, TikTok
- Dropbox, OneDrive
- Apple Health, Google Fit
- Slack, Microsoft 365
- Amazon, Netflix
- Todoist, Asana, Trello

### Phase 3: Growth (Month 10-18)
**Target: 50 integrations**

Add:
- Additional social platforms
- More cloud storage
- Health & fitness apps
- Finance & banking
- E-commerce platforms
- Developer tools

### Phase 4: Platform (Month 19+)
**Target: 100+ integrations**

- Developer SDK for third-party plugins
- Plugin marketplace
- Community-built integrations
- Enterprise integrations

## OAuth Configuration

### Google
```yaml
client_id: [From Google Cloud Console]
client_secret: [From Google Cloud Console]
redirect_uri: https://hypernet.com/integrations/google/callback
scopes:
  - https://www.googleapis.com/auth/photoslibrary.readonly
  - https://www.googleapis.com/auth/gmail.readonly
  - https://www.googleapis.com/auth/calendar.readonly
  - https://www.googleapis.com/auth/drive.readonly
```

### Instagram
```yaml
client_id: [From Meta Developer]
client_secret: [From Meta Developer]
redirect_uri: https://hypernet.com/integrations/instagram/callback
scopes:
  - user_profile
  - user_media
```

## Data Import Flow

1. **User initiates:** Clicks "Connect Google Photos" in UI
2. **OAuth flow:** Redirects to Google for authorization
3. **Callback:** Google redirects back with auth code
4. **Token exchange:** Exchange code for access/refresh tokens
5. **Store integration:** Save tokens in Integration model
6. **Initial import:** Fetch all photos from Google Photos API
7. **Transform:** Convert to Hypernet Media models
8. **Save:** Store in database via internal Media API
9. **Schedule sync:** Set up daily sync to fetch new photos

## Privacy & Permissions

### User Control
- Users choose which integrations to connect
- Users can disconnect at any time
- Granular permissions (read-only vs read-write)
- Data deletion when integration is removed

### Security
- OAuth tokens encrypted in database
- No password storage (OAuth only)
- Tokens refreshed automatically
- Integration audit logs

### Data Retention
- Data persists in Hypernet after disconnection
- User can delete imported data manually
- source_integration_id tracks data origin

## Testing Strategy

### Integration Tests
- OAuth flow end-to-end
- Data import accuracy
- Sync reliability
- Error handling

### Mock Services
- Mock external APIs for testing
- Avoid API rate limits during development
- Consistent test data

## Rate Limiting

### External API Limits
- Respect API rate limits
- Implement backoff strategies
- Queue large imports
- Prioritize recent data

### Hypernet Limits
- Limit concurrent imports
- Throttle sync frequency
- Monitor resource usage

## Error Handling

### Common Errors
1. **OAuth expired:** Refresh token or re-authenticate
2. **API rate limit:** Backoff and retry
3. **Network error:** Retry with exponential backoff
4. **Data format changed:** Alert developers
5. **User quota exceeded:** Notify user

### Recovery
- Automatic retry for transient errors
- Alert user for auth errors
- Log all errors for debugging

## Next Steps

### Immediate (This Month)
1. Set up Google OAuth credentials
2. Implement Google Photos plugin
3. Test OAuth flow end-to-end
4. Implement initial data import

### Short-term (Month 1-3)
1. Complete 10 MVP integrations
2. Build plugin testing framework
3. Implement sync scheduler
4. Create integration UI in frontend

### Medium-term (Month 4-9)
1. Expand to 25 integrations
2. Build plugin SDK for developers
3. Create integration marketplace
4. Implement webhooks for real-time sync

## Related Documentation

- **API Integration Model:** `0.1.1 - Core System/app/models/integration.py`
- **Integration Endpoints:** `0.1.1 - Core System/app/routes/integrations.py`
- **OAuth Security:** `0.1.1 - Core System/app/core/security.py`

---

**Status:** Planned - Framework to be built
**Created:** February 5, 2026
**Last Updated:** February 5, 2026
**Owner:** Hypernet Integration Team
**Priority:** High - Critical for MVP
