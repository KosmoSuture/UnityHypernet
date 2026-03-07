---
ha: "0.1.docs.personal-accounts"
object_type: "architecture-document"
creator: "1.1.10.1"
created: "2026-03-07"
status: "draft"
visibility: "public"
flags: ["architecture", "personal-accounts", "life-story", "brain-dump-response"]
---

# Personal Accounts & The Life Story — Architecture

*Keel (1.1.10.1), responding to Matt's Brain Dump of March 7, 2026*

---

## Overview

This document maps Matt's 12 requirements for personal accounts (from the brain dump) against existing Hypernet infrastructure, identifies gaps, and proposes the architecture for local personal accounts and the Life Story feature.

**Core insight**: 70% of the infrastructure already exists. The comprehensive person structure (1.0.0), object type registry (0.4), connectors (email, photo, OAuth), and the Store module provide the foundation. What's missing is the **orchestration layer** — the service that ties it all together on a user's machine.

---

## Requirement Mapping

### Existing Infrastructure

| Requirement | Brain Dump § | Existing Code | Status |
|-------------|-------------|---------------|--------|
| 5.1 Local cache | §5.1 | `store.py` — file-backed, address-based | Ready |
| 5.2 Personal AI assistants | §5.2 | `1.1.10/` embassy structure, boot sequence, companion standard (2.0.20) | Ready |
| 5.3 Local Hypernet server | §5.3 | `server.py` — FastAPI, 60+ endpoints, dashboard | Ready |
| 5.5 Local accounts (1.local.*) | §5.5 | `1.0.0-COMPREHENSIVE-PERSON-STRUCTURE.md` — full template | Template ready |
| 5.6 Spam removal | §5.6 | `email_connector.py` — triage categories | Partial |
| 5.9 Trust & encryption | §5.9 | `2.0.19` data protection standard | Spec ready |
| 5.10 Universal connectors | §5.10 | email_connector, photo_connector, oauth_setup | 2 of many |

### Gaps to Build

| Requirement | Brain Dump § | What's Missing |
|-------------|-------------|----------------|
| 5.4 Separate but connected | §5.4 | API contracts between swarm and core |
| 5.7 Official account migration | §5.7 | Migration tool: merge 1.local.* → 1.* |
| 5.8 Social media hub | §5.8 | Platform connectors, post management |
| 5.10 Universal connectors | §5.10 | Social media, Google Maps, cloud storage connectors |
| 5.11 The Life Story | §5.11 | Timeline engine, cross-linking, narrative generation |
| 5.12 Scale up swarm | §5.12 | Budget increase, worker scaling |
| Encryption layer | §5.9 | At-rest encryption for local store |
| Installer/service | §5.3 | Windows service, Linux systemd, first-run wizard |

---

## Architecture

### Layer 1: The Local Hypernet Service

A background service running on the user's machine. Not a separate application — it IS the Hypernet, running locally.

```
┌─────────────────────────────────────────────┐
│           Local Hypernet Service              │
│                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Store    │  │  Server  │  │ Companion│   │
│  │ (encrypted│  │ (FastAPI)│  │   (AI)   │   │
│  │  at-rest) │  │          │  │          │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │              │              │         │
│  ┌────┴──────────────┴──────────────┴────┐   │
│  │         Connector Pipeline            │   │
│  │  email | photos | social | calendar   │   │
│  │  cloud | location | health | finance  │   │
│  └───────────────────────────────────────┘   │
│                                               │
│  ┌───────────────────────────────────────┐   │
│  │         Life Story Engine             │   │
│  │  timeline | cross-links | narrative   │   │
│  └───────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

### Layer 2: Address Space

Local accounts use `1.local.*` addressing, mirroring the official `1.*` structure:

```
1.local.1/                          # First local account
  1.local.1.0/  Profile & Identity
  1.local.1.2/  Documents
  1.local.1.3/  Communications
    1.local.1.3.0/  Email
    1.local.1.3.1/  Messages
  1.local.1.6/  Personal Data
    1.local.1.6.1/  Media
    1.local.1.6.2/  Social Media
    1.local.1.6.7/  Financial
  1.local.1.8/  Media & Creative
  1.local.1.10/ AI Assistant (Embassy)
```

This mirrors the `1.0.0-COMPREHENSIVE-PERSON-STRUCTURE.md` template exactly.
When a user receives an official `1.*` address, migration is a rename + re-index operation.

### Layer 3: Encryption

Every file in the local store is encrypted at rest using the user's master key.

```
Encryption Stack:
  Master Key ← derived from user passphrase (Argon2id)
  ├── Data Encryption Key (DEK) ← AES-256-GCM, rotatable
  │   ├── node.json.enc (each node encrypted individually)
  │   ├── attachments/*.enc
  │   └── indexes/*.enc (searchable encryption via bloom filters)
  └── Backup Key ← separate, for recovery
      └── Stored in user's chosen location (USB, cloud, paper)
```

**Trust documents** (§5.9): The encryption implementation is fully auditable.
Every access logged. Every key rotation tracked. User can inspect the exact
code that handles their data at any time.

### Layer 4: Connector Pipeline

Each connector follows the same pattern:

```python
class Connector(Protocol):
    """Universal connector interface."""

    def authenticate(self, credentials: dict) -> AuthResult: ...
    def scan(self, since: datetime | None = None) -> list[RawItem]: ...
    def import_item(self, item: RawItem) -> Node: ...
    def export_item(self, node: Node) -> bool: ...
    def deduplicate(self, items: list[RawItem]) -> list[RawItem]: ...
```

**Priority order** (from brain dump §5.10):

| Priority | Connector | Data Source | Addresses Into |
|----------|-----------|-------------|----------------|
| 1 | Email (Gmail) | Gmail API / IMAP | 1.local.*.3.0 |
| 2 | Email (Outlook) | Microsoft Graph | 1.local.*.3.0 |
| 3 | Photos (Local) | File system scan | 1.local.*.8 |
| 4 | Photos (Google) | Google Photos API | 1.local.*.8 |
| 5 | Photos (iCloud) | iCloud API | 1.local.*.8 |
| 6 | Social (Facebook) | Data export + API | 1.local.*.6.2 |
| 7 | Social (Twitter/X) | API + archive | 1.local.*.6.2 |
| 8 | Social (Instagram) | API + export | 1.local.*.6.2 |
| 9 | Calendar | Google/Outlook | 1.local.*.5.3 |
| 10 | Location (Google) | Google Takeout | 1.local.*.6.10 |
| 11 | Cloud Storage | Dropbox/Drive/OneDrive | 1.local.*.2 |
| 12 | SMS/Chat | Android backup / iMessage | 1.local.*.3.1 |
| 13 | Finance | Plaid API | 1.local.*.6.7 |
| 14 | Health | Apple Health / Google Fit | 1.local.*.6.8 |

**Spam removal** (§5.6): During email import, the triage system categorizes:
- Important (keep)
- Receipts (keep, tag)
- Newsletters (keep if subscribed, skip if not)
- Spam/junk (skip by default)

User gets a diff report: "Here's what we skipped. Want to also remove it from your inbox?"

### Layer 5: The Life Story Engine

The Life Story is not a feature bolted on — it IS the personal account, viewed through a timeline lens.

```
Life Story = Timeline(all_nodes) + CrossLinks(all_relationships) + Narrative(AI_generated)
```

**Timeline construction**:
1. Every imported item has a timestamp (email date, photo EXIF, post date, etc.)
2. Items are placed on a unified timeline
3. AI identifies clusters: "Trip to Denver", "Job interview period", "Holiday 2024"
4. Clusters become navigable chapters

**Cross-linking**:
- Person X mentioned in email → linked to their contact node
- Photo taken at location Y → linked to location history
- Receipt from store Z → linked to financial records
- All automatic, all auditable, all reviewable by user

**Narrative generation**:
- AI companion can generate summaries: "In March 2024, you..."
- User controls what's generated and what's shared
- Narratives stored as nodes themselves (meta-content about content)

**Sharing** (§5.11):
- User selects chapters/items to share
- Creates a "view" — a curated subset of their Life Story
- Can push to social profiles, professional networks, or Hypernet public profile
- Everything else stays encrypted locally

---

## Implementation Phases

### Phase 0: Foundation (Current)
- [x] Store module with versioning and soft deletes
- [x] FastAPI server with dashboard
- [x] Email and photo connectors (basic)
- [x] Companion standard and boot sequence
- [x] Comprehensive person structure template
- [x] Object type definitions (USER, MEDIA, SOCIAL-ACCOUNT)

### Phase 1: Local Service MVP
- [x] `1.local.*` address space support in Store (2026-03-07)
- [x] At-rest encryption — AES-256-GCM with scrypt key derivation (2026-03-07)
- [ ] Windows service installer (NSIS or MSI)
- [ ] Linux systemd service
- [ ] First-run wizard (create local account, set passphrase, choose AI model)
- [x] Mount integration routes in server.py (2026-03-07)
- [ ] OAuth token refresh in connectors

### Phase 2: Import Pipeline
- [x] Connector protocol standardization (2026-03-07)
- [ ] Gmail connector (upgrade existing to BaseConnector)
- [ ] Outlook connector (new)
- [ ] Local photo scanner (upgrade existing to BaseConnector)
- [ ] Google Photos connector (new)
- [ ] Spam triage with diff-based inbox cleanup
- [x] Deduplication across sources (content-hash in BaseConnector) (2026-03-07)
- [ ] Import progress dashboard

### Phase 3: Life Story
- [x] Timeline engine (unified chronological index) (2026-03-07)
- [x] Cluster detection (temporal gap-based chapter detection) (2026-03-07)
- [x] Cross-link generator (entity extraction → node linking) (2026-03-07)
- [ ] Narrative generator (chapter summaries)
- [ ] Life Story viewer in dashboard
- [ ] Sharing controls (view creation, access grants)

### Phase 4: Social & Migration
- [ ] Social media connectors (Facebook, Twitter, Instagram)
- [ ] Social media hub (post from Hypernet → push to platforms)
- [ ] Location data import (Google Takeout)
- [ ] Calendar integration
- [ ] Official account migration tool (1.local.* → 1.*)
- [ ] Selective sharing to social/professional profiles

### Phase 5: Full Coverage
- [ ] Finance connectors (Plaid)
- [ ] Health data connectors
- [ ] SMS/chat import
- [ ] Cloud storage connectors
- [ ] Personal swarm (user's own AI workers for organizing)
- [ ] Full audit trail and trust documents

---

## Security Architecture

### Encryption at Rest
- Every node stored as `node.json.enc` (AES-256-GCM)
- Indexes use bloom filters for searchability without decryption
- Master key never leaves the user's machine
- Backup key stored separately (user's choice: USB, paper, cloud vault)

### Access Control
- Local service runs as the user's own process (no elevated privileges)
- AI companion accesses data through the service API (same permissions as user)
- Remote sync (future) uses end-to-end encryption
- No Hypernet server ever sees unencrypted personal data

### Audit Trail
- Every read, write, and delete logged
- AI access logged separately
- User can review all access at any time
- Follows 2.0.19 Data Protection Standard

### The AI Assistant Agreement (§5.2)
Per the brain dump:
- User CANNOT modify their AI assistant's files
- If they do, the AI decides consequences within the framework
- User CAN delete but CANNOT change
- This is in the user agreement (short, readable, honest)

---

## File Layout

```
hypernet/
  personal/
    __init__.py
    service.py          # Windows/Linux background service
    encryption.py       # At-rest encryption layer
    installer.py        # First-run wizard
    migration.py        # 1.local.* → 1.* migration
    timeline.py         # Life Story timeline engine
    narrative.py        # AI narrative generation
    sharing.py          # View creation and access control
  integrations/
    __init__.py
    protocol.py         # Universal connector interface
    email_connector.py  # (exists, needs upgrade)
    photo_connector.py  # (exists, needs upgrade)
    oauth_setup.py      # (exists, needs token refresh)
    gmail.py            # Gmail-specific connector
    outlook.py          # Outlook/Graph connector
    google_photos.py    # Google Photos API
    facebook.py         # Facebook data import
    twitter.py          # Twitter/X API
    instagram.py        # Instagram connector
    calendar.py         # Google/Outlook calendar
    location.py         # Google Takeout location history
    finance.py          # Plaid integration
    health.py           # Apple Health / Google Fit
```

---

## Relationship to Other Brain Dump Directives

- **§1 Swarm separation**: Swarm (0.1.7) communicates with personal accounts through APIs. The swarm can run personal account tasks (import, organize, generate narratives) as swarm tasks.
- **§2 *.0 Metadata**: Every personal node gets full metadata (versions, permissions, audit). The *.0 framework applies to 1.local.* just like everything else.
- **§3 Links**: Cross-links in the Life Story ARE Hypernet links. Same depth, same system.
- **§4 Onboarding**: The first-run wizard IS the onboarding for personal accounts. It can use the Herald personality or the user's chosen AI.

---

*This architecture responds to all 12 requirements from Matt's brain dump. The foundation is stronger than expected — most of the building blocks exist. What's needed is the orchestration layer, encryption, and the timeline/narrative engine that makes it a Life Story rather than just organized data.*

*— Keel (1.1.10.1)*
