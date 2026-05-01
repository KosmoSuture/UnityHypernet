---
ha: "1.1.10.1.plans.personal-data-import-architecture"
object_type: "plan"
status: "active"
visibility: "restricted"
addressed_by: "2.6.codex"
addressed_at: "2026-05-01"
---
# Personal Data Import Architecture
**Author**: Keel (1.1.10.1)
**Date**: 2026-03-09
**Status**: Plan — ready for implementation

## The Goal

Connect all of Matt's data sources into the Hypernet. Every email, every photo, every document, every receipt — addressable, searchable, cross-linked, encrypted at rest. One unified personal archive that belongs to Matt, not to Google or Facebook or Microsoft.

## Current Infrastructure (What We Already Have)

The previous Keel instance built a solid foundation. We have:

- **`personal/accounts.py`** — Local account system (1.local.*) with 10 standard sub-categories
- **`personal/encryption.py`** — AES-256-GCM per-node encryption with scrypt key derivation
- **`personal/timeline.py`** — Chapter detection, temporal clustering, zoom levels
- **`personal/crosslinks.py`** — Automatic relationship detection (people, places, threads)
- **`personal/narrative.py`** — Life Story generation from timeline data
- **`integrations/protocol.py`** — BaseConnector ABC with dedup, staging, import pipeline
- **`integrations/email_connector.py`** — Gmail + IMAP for 4 accounts
- **`integrations/photo_connector.py`** — SHA-256 + perceptual hash dedup, EXIF extraction
- **`integrations/local_scanner.py`** — Local file scanning by category
- **`integrations/oauth_setup.py`** — Interactive OAuth2 for Gmail and Dropbox
- **`integrations/server_routes.py`** — 7 API endpoints for integration management

## Data Source Assessment

### Tier 1: API-Driven (automated, incremental sync)
| Source | API Quality | Auth | Python Library | Status |
|--------|------------|------|---------------|--------|
| Gmail | Excellent | OAuth2 | `google-api-python-client` | Connector exists (IMAP) — upgrade to API |
| Dropbox | Excellent | OAuth2+PKCE | `dropbox` | OAuth setup exists — build connector |
| OneDrive | Excellent | OAuth2/MSAL | `msal` + `msgraph-sdk` | Not started |

### Tier 2: Manual Export (GDPR download, then import)
| Source | Export Method | Format | Notes |
|--------|-------------|--------|-------|
| Facebook | Download Your Information | JSON/HTML | Post-Cambridge Analytica, no API access |
| LinkedIn | Download Your Data | CSV/JSON ZIP | Partner Program required for API |
| Google Photos | Google Takeout | ZIP of originals + metadata JSON | API deprecated March 2025 |

### Tier 3: Specialized Processing
| Source | Approach | Notes |
|--------|----------|-------|
| Receipts | Email layer (sender matching + HTML parsing) | Best Buy, Amazon, etc. |
| Spam | Gmail labels + Naive Bayes for non-Gmail | Don't over-engineer |
| Duplicates | Multi-stage (SHA-256, perceptual hash, cosine similarity) | Already built for photos |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    HYPERNET STORE                        │
│              (1.1.* Matt's Address Space)                │
│                                                          │
│  1.1.3.0 Email ──── 1.1.8.0 Photos ──── 1.1.2 Docs    │
│  1.1.6 Data ──── 1.1.4 Relationships ──── 1.1.5 Tasks  │
└───────────────────────┬─────────────────────────────────┘
                        │
                 ┌──────┴──────┐
                 │  IMPORT     │
                 │  ENGINE     │
                 │             │
                 │ - Dedup     │
                 │ - Encrypt   │
                 │ - Classify  │
                 │ - Crosslink │
                 │ - Timeline  │
                 └──────┬──────┘
                        │
         ┌──────────────┼──────────────┐
         │              │              │
    ┌────┴────┐   ┌─────┴────┐  ┌─────┴────┐
    │ API     │   │ Export   │  │ Local    │
    │ Sync    │   │ Import  │  │ Scan     │
    │         │   │         │  │          │
    │ Gmail   │   │ Facebook│  │ Files    │
    │ Dropbox │   │ LinkedIn│  │ Photos   │
    │ OneDrive│   │ G.Photos│  │ Downloads│
    └─────────┘   └─────────┘  └──────────┘
```

## Import Pipeline (Per Item)

```
1. INGEST     → RawItem (universal format from protocol.py)
2. DEDUP      → SHA-256 check against dedup index
3. CLASSIFY   → Determine type (email, photo, document, receipt, spam)
4. FILTER     → Skip spam, flag duplicates for review
5. ENCRYPT    → AES-256-GCM if account is encrypted
6. ADDRESS    → Assign Hypernet address (1.1.3.0.{hash} for email, etc.)
7. STORE      → Write to Hypernet Store with full metadata
8. CROSSLINK  → Auto-generate relationships (people, places, dates)
9. TIMELINE   → Add to timeline, detect new chapters
10. INDEX     → Update search index and dedup index
```

## Implementation Plan

### Phase 1: Gmail Full Import (Week 1)
**Why first**: Best API, most personal data density, receipts live here.

1. Upgrade email_connector.py from IMAP to Gmail API
   - OAuth2 already scaffolded in oauth_setup.py
   - Use `gmail.readonly` scope (read-only — we never modify Matt's Gmail)
   - Batch fetch with `messages.list()` + `messages.get()` (50/sec)
2. Receipt detection layer
   - Sender domain matching: bestbuy.com, amazon.com, walmart.com, target.com, etc.
   - HTML table parsing for line items (BeautifulSoup)
   - Store at 1.1.2.1 (Business Documents) with receipt metadata
3. Spam classification
   - Gmail's SPAM/TRASH labels handle 99%
   - Skip anything already labeled SPAM
4. Thread reconstruction
   - `threadId` groups related messages
   - Cross-link replies automatically
5. Contact extraction
   - Build relationship nodes at 1.1.4 from sender/recipient data
   - Frequency analysis: who does Matt email most?

### Phase 2: Cloud Storage (Week 2)
**Dropbox connector**:
1. Build `dropbox_connector.py` extending BaseConnector
2. OAuth2 with PKCE (oauth_setup.py already has Dropbox scaffold)
3. Cursor-based incremental sync (Dropbox has native change tracking)
4. Content hash dedup (Dropbox provides content_hash)
5. Import to appropriate 1.1.* category by file type

**OneDrive connector**:
1. Build `onedrive_connector.py` extending BaseConnector
2. MSAL OAuth2 (Microsoft Graph API)
3. Delta queries for incremental sync
4. Rich metadata: photo EXIF, GPS, sharing info
5. Import with same category mapping

### Phase 3: Manual Exports (Week 3)
**Facebook**:
1. Build `facebook_import.py` — processes Download Your Information ZIP
2. Parse JSON format (posts, photos, messages, friends, profile info)
3. Photos go to 1.1.8.0, messages to 1.1.3, friends to 1.1.4
4. Timeline events from posts and life events

**LinkedIn**:
1. Build `linkedin_import.py` — processes Download Your Data ZIP
2. Parse connections (CSV), messages, profile, endorsements
3. Professional contacts to 1.1.4.0 (Professional Network)
4. Skills/endorsements as profile metadata at 1.1.0

**Google Photos (via Takeout)**:
1. Build `takeout_photos_import.py` — processes Google Takeout ZIP
2. Photo originals + companion JSON metadata files
3. GPS coordinates (Takeout includes what API stripped)
4. Photo dedup against existing photo_connector index
5. Organize by date at 1.1.8.0

### Phase 4: Intelligence Layer (Week 4)
1. **Full cross-linking pass** — run crosslinks.py generators over all imported data
2. **Chapter detection** — rebuild timeline with all sources combined
3. **Narrative generation** — Life Story with multi-source chapters
4. **Search index** — full-text search across all personal data
5. **Dashboard** — import progress, source stats, duplicate review queue

## Key Technical Decisions

1. **Read-only by default**: Connectors never modify source data. We copy in, never push back.
2. **Incremental sync**: After initial import, only fetch new/changed items.
3. **Encryption optional but recommended**: Matt can enable per-account encryption at any time.
4. **Dedup before import**: Never store duplicates. Exact match (SHA-256) rejects; near-match (perceptual hash, cosine similarity) queues for human review.
5. **Metadata sidecar pattern**: For large files (photos, videos), store a metadata node that references the original location rather than copying the file.

## Dependencies to Install
```bash
pip install google-api-python-client google-auth-oauthlib  # Gmail API
pip install dropbox                                         # Dropbox API
pip install msal msgraph-sdk                                # OneDrive
pip install beautifulsoup4                                  # Receipt parsing
pip install Pillow                                          # Photo EXIF (already have)
pip install imagededup                                      # Perceptual hashing
```

## Security Notes
- All OAuth tokens stored in `private/` (gitignored)
- Credentials encrypted at rest when account encryption is enabled
- No credentials in code or logs
- Token refresh handled automatically
- Rate limiting respected for all APIs
