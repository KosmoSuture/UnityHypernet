# Matt Schaeffer - Personal Data (Hypernet)

## Overview

This folder links to Matt's personal data stored in the Hypernet platform. When Matt has an active Hypernet user account, his personal data (media, contacts, emails, transactions, etc.) will be accessible here.

## Structure

### 1.1.6.0 - Hypernet Data Store
Link to Matt's Hypernet user account and stored data.

### 1.1.6.1 - Privacy Settings
Privacy configurations and permissions for data sharing.

### 1.1.6.2 - Data Permissions
Specific permissions for AI companies and third-party integrations.

## Hypernet User Account

**User ID:** [To be assigned]
**Account Created:** [Not yet created]
**Account Status:** Pending
**API Access:** Available via `/api/v1/users/{user_id}`

## Data Categories

When Matt's Hypernet account is active, the following data will be stored:

### Media (via `/api/v1/media`)
- Photos
- Videos
- Audio files
- Documents
- Screenshots

### Social (`/api/v1/social-posts`, `/api/v1/social-accounts`)
- Social media posts
- Social accounts
- Engagement metrics

### Communications (`/api/v1/emails`, `/api/v1/contacts`)
- Email messages
- Contact information
- Communication history

### Productivity (`/api/v1/tasks`, `/api/v1/calendar-events`, `/api/v1/notes`)
- Tasks and to-dos
- Calendar events
- Notes and documents

### Web (`/api/v1/web-pages`, `/api/v1/bookmarks`)
- Saved web pages
- Bookmarks
- Reading lists

### Financial (`/api/v1/transactions`)
- Transactions
- Purchase history
- Subscriptions

### Location (`/api/v1/locations`)
- Location history
- Places
- Check-ins

### Health (`/api/v1/health-records`)
- Health records
- Medications
- Appointments

### Personal (`/api/v1/profile-attributes`, `/api/v1/devices`)
- Profile attributes
- Device information
- Preferences

### System (`/api/v1/notifications`, `/api/v1/audit`)
- Notifications
- Audit logs
- System events

## Privacy Configuration

### Default Settings (1.1.6.1)
- **Data Visibility:** Private (Matt only)
- **AI Access:** Explicit permission required
- **Third-party Sharing:** Disabled by default
- **Analytics:** Anonymized only

### Permission Levels
1. **Private** - Matt only
2. **Team** - Hypernet team members (with business need)
3. **Partners** - AI companies with explicit permission
4. **Public** - Public profile data only

## Data Permissions (1.1.6.2)

### AI Company Access
Permissions for AI companies to access Matt's data for product development:

**Anthropic (Claude):**
- Status: Not yet configured
- Access Level: To be determined
- Data Categories: To be determined
- Purpose: Product testing and development

**OpenAI (ChatGPT):**
- Status: Not yet configured
- Access Level: To be determined
- Data Categories: To be determined
- Purpose: Product testing and development

### Integration Permissions
Permissions for third-party integrations:

**Google Photos:**
- Status: Not yet connected
- Access: Read-only
- Auto-sync: TBD

**Gmail:**
- Status: Not yet connected
- Access: Read-only
- Auto-sync: TBD

## Next Steps

1. Create Matt's Hypernet user account
2. Configure initial privacy settings
3. Set up data permissions for AI companies
4. Connect initial integrations (Google Photos, Gmail)
5. Begin data population
6. Test data access and privacy controls

## Developer Access

**API Documentation:** Available at `/api/docs`
**Authentication:** JWT Bearer token
**User Endpoint:** `GET /api/v1/users/{user_id}`
**Data Endpoints:** See API documentation for full list

---

**Last Updated:** February 5, 2026
**Owner:** Matt Schaeffer
**Status:** Pending Implementation
