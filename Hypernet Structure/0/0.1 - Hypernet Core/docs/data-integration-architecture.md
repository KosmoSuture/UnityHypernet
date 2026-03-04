---
ha: "0.1.docs.data-integration"
object_type: "document"
creator: "1.1.10.1"
created: "2026-03-04"
status: "active"
visibility: "public"
---

# Hypernet Personal Data Integration Architecture

## The Vision

Every person's digital life is scattered across dozens of services — Gmail, Dropbox,
Instagram, iCloud, bank accounts, medical records, work tools. No single platform
connects all of it. The Hypernet does.

When a user creates their Hypernet account (e.g., 1.1 for Matt Schaeffer), they get
a permanent hierarchical address space where ALL their data can live, organized by
their AI companion, and accessible from any device.

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│                    USER'S DEVICES                        │
│  Phone  │  Laptop  │  Tablet  │  Desktop  │  Server    │
└────┬────┴────┬─────┴────┬─────┴────┬──────┴─────┬──────┘
     │         │          │          │             │
     ▼         ▼          ▼          ▼             ▼
┌─────────────────────────────────────────────────────────┐
│              HYPERNET INTEGRATION LAYER                   │
│                                                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │  Gmail    │ │ Dropbox  │ │ Social   │ │  Local   │   │
│  │ Connector │ │ Connector│ │ Connector│ │ Scanner  │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘   │
│       │             │            │             │          │
│       ▼             ▼            ▼             ▼          │
│  ┌──────────────────────────────────────────────────┐    │
│  │            PRIVATE STAGING AREA                    │    │
│  │     (gitignored, local only, encrypted)           │    │
│  │     private/import-staging/{email,photos,...}      │    │
│  └──────────────────┬───────────────────────────────┘    │
│                     │                                     │
│                     ▼                                     │
│  ┌──────────────────────────────────────────────────┐    │
│  │           AI TRIAGE ENGINE                         │    │
│  │  - Separates signal from noise                    │    │
│  │  - Deduplicates (SHA256 + perceptual hashing)    │    │
│  │  - Categorizes (receipts, important, junk)       │    │
│  │  - Extracts metadata (EXIF, dates, senders)      │    │
│  │  - AI-powered relevance scoring                   │    │
│  └──────────────────┬───────────────────────────────┘    │
│                     │                                     │
│                     ▼                                     │
│  ┌──────────────────────────────────────────────────┐    │
│  │         HYPERNET ADDRESS ASSIGNMENT                │    │
│  │  1.1.3.0 - Email Archives                        │    │
│  │  1.1.8.0 - Photos (organized by date/event)      │    │
│  │  1.1.8.1 - Videos                                │    │
│  │  1.1.2.0 - Documents                             │    │
│  │  1.1.6.0 - Data Store (structured data)          │    │
│  └──────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## Security Model

### Three Zones

1. **External Services** (Gmail, Dropbox, etc.)
   - Connected via OAuth2 (no passwords stored)
   - Read-only access by default
   - Refresh tokens stored in private/oauth-tokens/ (gitignored)

2. **Private Staging** (private/ directory)
   - Gitignored — never touches the public repository
   - Raw imports land here before processing
   - Credentials encrypted at rest
   - Only the user and their companion have access

3. **Hypernet Structure** (public repository)
   - Processed, organized data with proper addresses
   - Metadata is public, actual files can be private
   - Everything governed by 2.0.19 (Data Protection)

### Credential Management

```
private/
├── credentials/           # OAuth tokens, app passwords
│   ├── google_client_secret.json
│   ├── matt.spamme@gmail.com.json
│   ├── kosmicsuture@gmail.com.json
│   └── dropbox_app.json
├── oauth-tokens/          # Active tokens (auto-refreshed)
│   ├── gmail_matt_spamme_at_gmail_com.json
│   └── dropbox.json
└── encrypted/             # GPG-encrypted sensitive docs
```

All credential files: chmod 600 (owner read/write only), gitignored, never committed.

## Connectors

### Email Connector
- **Gmail**: OAuth2 + IMAP (XOAUTH2 SASL)
- **Generic IMAP**: App passwords for schaeffer.org accounts
- **Triage**: Pattern-based initial sort, then AI-powered relevance scoring
- **Import**: Important emails → 1.1.3 Communications with full Hypernet frontmatter

### Photo Connector
- **Sources**: Dropbox API, local directories, device imports
- **Deduplication**: Two-phase — SHA256 for exact matches, perceptual hashing for near-dupes
- **EXIF**: Date, location, camera info extracted automatically
- **Organization**: By date → 1.1.8 Media, organized into year/month subdirectories

### Social Media Connector (Planned)
- **Data exports**: Use platform export tools (Twitter archive, Facebook download, etc.)
- **API connectors**: For platforms that allow it
- **Import**: Posts, photos, DMs → appropriate Hypernet addresses

## The AI Companion's Role

The companion (1.1.10.1) is the user's interface to this system:

1. **Initiates connections** — guides OAuth setup, tests connectivity
2. **Runs triage** — uses AI to determine what matters vs. noise
3. **Asks about ambiguous items** — "Is this email from 2019 important to keep?"
4. **Organizes automatically** — assigns Hypernet addresses, files in correct categories
5. **Reports progress** — "I processed 3,247 emails. 89 were important. Here's a summary."
6. **Never deletes** — per 2.0.19, originals always archived

## Server Deployment

This runs on the always-on Hypernet server (Oracle Cloud Free Tier recommended):

```bash
# Start with integration endpoints
python -m hypernet serve --integrations

# OAuth setup (interactive, run on machine with browser)
python -m hypernet.integrations.oauth_setup gmail
python -m hypernet.integrations.oauth_setup dropbox

# Manual scan (from server or CLI)
python -m hypernet.integrations.email_connector scan matt.spamme@gmail.com
python -m hypernet.integrations.photo_connector scan /path/to/photos
```

## API Endpoints

```
GET  /api/v1/integrations/status          # Overview of all connections
POST /api/v1/integrations/email/scan      # Scan an email account
GET  /api/v1/integrations/photos/stats    # Photo index statistics
POST /api/v1/integrations/photos/scan     # Scan directory for photos
POST /api/v1/integrations/photos/find-duplicates  # Find near-dupes
GET  /api/v1/integrations/oauth/gmail/setup-url   # Gmail setup instructions
GET  /api/v1/integrations/oauth/dropbox/setup-url # Dropbox setup instructions
```

## What This Means for Users

When someone creates a Hypernet account, they can:
1. Connect their email → AI triages years of messages in minutes
2. Connect their photos → duplicates found, everything organized by date/event
3. Connect social media → full history preserved with proper addresses
4. All of it searchable, organized, and permanent

Their AI companion manages the whole process. The user just gives permission and
answers questions about what matters to them.

This is the demo that makes investors' jaws drop.

## Implementation Status

| Component | Status | Location |
|-----------|--------|----------|
| Security (.gitignore) | DONE | .gitignore |
| Private directory structure | DONE | 1.1/private/ |
| Email connector (IMAP) | BUILT | hypernet/integrations/email_connector.py |
| OAuth2 setup flow | BUILT | hypernet/integrations/oauth_setup.py |
| Photo scanner + dedup | BUILT | hypernet/integrations/photo_connector.py |
| API endpoints | BUILT | hypernet/integrations/server_routes.py |
| Oracle server | PENDING | Matt needs to sign up |
| Gmail OAuth credentials | PENDING | Matt needs to create Google Cloud project |
| Dropbox OAuth credentials | PENDING | Matt needs to create Dropbox app |
| AI-powered triage | PLANNED | Will use swarm for intelligent categorization |
| Social media connectors | PLANNED | After email/photos working |

## Next Steps (Sequence Matters)

1. **Matt signs up for Oracle Cloud Free Tier** (24GB RAM, free forever)
2. **Deploy Hypernet server** to Oracle instance
3. **Create Google Cloud project** with Gmail API enabled
4. **Run OAuth setup** for each Gmail account
5. **First email scan** — start with kosmicsuture@gmail.com (most relevant)
6. **First photo scan** — start with Dropbox
7. **AI triage iteration** — refine what counts as "important"
8. **Investor demo** — show the full flow live
