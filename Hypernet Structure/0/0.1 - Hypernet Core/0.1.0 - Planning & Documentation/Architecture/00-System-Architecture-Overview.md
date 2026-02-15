# Hypernet Core 0.1 - System Architecture Overview

**Version:** 0.1.0
**Last Updated:** 2026-02-03
**Status:** Planning Phase
**Architecture Owner:** [To be assigned]

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Design Principles](#design-principles)
3. [System Partition Architecture](#system-partition-architecture)
4. [Security Model](#security-model)
5. [Deployment Architecture](#deployment-architecture)
6. [API-First Design Philosophy](#api-first-design-philosophy)
7. [Data Flow Architecture](#data-flow-architecture)
8. [Future Evolution Path](#future-evolution-path)
9. [Technology Stack](#technology-stack)
10. [Critical Design Decisions](#critical-design-decisions)

---

## Executive Summary

Hypernet Core 0.1 is the foundation layer for a universal, secure, privacy-first personal data management and communication platform. Phase 1 focuses on:

- **Personal data aggregation** (photos, videos, social media, communications)
- **API-first architecture** enabling universal client access
- **Maximum security** through immutable infrastructure and defense-in-depth
- **Self-hosted deployment** with future cloud and distributed options

### Key Architectural Principles:

1. **Immutable Infrastructure** - OS and code deployed as atomic, verified units
2. **API-First** - All external access through secure, versioned APIs
3. **Defense in Depth** - Multiple security layers, zero trust model
4. **Privacy by Design** - User data encrypted, minimized collection, user control
5. **Modular & Extensible** - Plugin architecture for integrations
6. **Future-Proof** - Designed for distributed/federated evolution

---

## Design Principles

### 1. Security First
- **Immutable system partition** prevents tampoline/rootkits
- **Atomic updates** ensure system integrity (no partial updates)
- **Read-only core** eliminates runtime modification attacks
- **Input sanitization** on all API boundaries
- **Encryption everywhere** (at rest, in transit, in processing where possible)
- **Audit logging** for all security-relevant events

### 2. Privacy by Default
- **User owns their data** - Hypernet is custodian, not owner
- **Minimal data collection** - only what's necessary for functionality
- **Encryption at rest** - database and media encrypted
- **Zero-knowledge where possible** - system can't read user data
- **User-controlled sharing** - explicit consent for all data access

### 3. API-First Design
- **All functionality accessible via API** - UI is just another client
- **Versioned APIs** - backward compatibility, graceful deprecation
- **RESTful + GraphQL options** - flexibility for different use cases
- **Rate limiting & throttling** - DoS protection, fair usage
- **Comprehensive documentation** - auto-generated from code

### 4. Modular & Extensible
- **Plugin architecture** for integrations (social media, communications)
- **Event-driven** - plugins respond to core events
- **Isolated execution** - plugins can't compromise core
- **Standard interfaces** - easy to add new integrations

### 5. Operational Excellence
- **Observability** - comprehensive logging, metrics, tracing
- **Automated deployment** - CI/CD for verified updates
- **Health monitoring** - proactive issue detection
- **Disaster recovery** - backup and restore procedures

---

## System Partition Architecture

Hypernet uses a **multi-partition design** to isolate concerns, enhance security, and enable atomic updates.

### Partition Layout

```
/dev/sda1 → /boot (EFI System Partition)
/dev/sda2 → / (System - OS + Hypernet Core) [READ-ONLY, IMMUTABLE]
/dev/sda3 → /config (Configuration) [READ-WRITE, PROTECTED]
/dev/sda4 → /data (Database) [READ-WRITE, ENCRYPTED]
/dev/sda5 → /media (User Uploads) [READ-WRITE, ENCRYPTED]
/dev/sda6 → /logs (Logs & Audit) [READ-WRITE, APPEND-ONLY where possible]
/dev/sda7 → /cache (Temporary/Cache) [READ-WRITE, VOLATILE]
```

### Partition Details

#### 1. System Partition (`/` - Root)
**Purpose:** Immutable OS and Hypernet Core code
**Size:** 20-30 GB
**Filesystem:** ext4 or btrfs (with snapshots)
**Mount Options:** `ro,nodev,nosuid,noexec` (read-only + hardening)
**Update Strategy:** Atomic replacement via A/B partition scheme

**Contents:**
- Operating system (Ubuntu Server 24.04 LTS)
- Python runtime and dependencies
- Hypernet Core application code
- System libraries and binaries
- Boot configuration

**Update Process:**
1. New system image prepared offline
2. Cryptographic verification (signature + hash)
3. Write to inactive partition (A or B)
4. Verify written data
5. Update bootloader to new partition
6. Reboot into new system
7. Rollback available if boot fails

**Security Features:**
- Read-only mount prevents runtime modification
- dm-verity (optional) for block-level integrity checking
- Signed images prevent unauthorized updates
- Atomic updates prevent partial/corrupted states

#### 2. Configuration Partition (`/config`)
**Purpose:** Machine-specific and deployment-specific configuration
**Size:** 1-2 GB
**Filesystem:** ext4
**Mount Options:** `rw,nodev,nosuid,noexec`
**Backup:** Included in system snapshots

**Contents:**
- Server configuration (IP, ports, hostnames)
- Database connection strings
- API keys and secrets (encrypted at rest)
- TLS/SSL certificates
- Integration credentials
- Feature flags and toggles
- Environment-specific overrides

**Structure:**
```
/config/
  ├── hypernet/
  │   ├── server.yaml           # Server configuration
  │   ├── database.yaml         # DB connection settings
  │   ├── api.yaml              # API configuration
  │   └── secrets/              # Encrypted secrets
  │       ├── api-keys.enc
  │       ├── db-password.enc
  │       └── tls-private-key.enc
  ├── integrations/
  │   ├── facebook.yaml
  │   ├── instagram.yaml
  │   └── gmail.yaml
  └── security/
      ├── firewall-rules.conf
      ├── rate-limits.yaml
      └── audit-policy.yaml
```

**Security Features:**
- Separate from immutable system (allows configuration changes without full update)
- Secrets encrypted with key derived from hardware TPM or HSM
- Strict file permissions (root-only access)
- Configuration validation on startup
- Version controlled (git) for change tracking

#### 3. Database Partition (`/data`)
**Purpose:** Persistent user data and metadata storage
**Size:** 100 GB - 1 TB+ (scalable based on user count)
**Filesystem:** ext4 or XFS (for large file support)
**Mount Options:** `rw,nodev,nosuid,noexec`
**Encryption:** LUKS2 full-disk encryption or dm-crypt

**Contents:**
- PostgreSQL or similar database files
- User account data
- Metadata for photos, videos, communications
- Relationships and links between objects
- Indexes and materialized views

**Database Choice (To Be Determined):**
- **PostgreSQL** - Mature, ACID compliant, excellent for relational data and JSON
- **SQLite** (for single-user nodes) - Simple, embedded, zero-config
- **Time-series DB** (for audit logs, metrics) - InfluxDB or TimescaleDB

**Security Features:**
- Full-disk encryption (LUKS2) with strong passphrase or TPM-backed key
- Database-level encryption for sensitive fields
- Regular backups to separate partition or remote storage
- Point-in-time recovery (PITR) capability
- Access only via Hypernet Core (no direct external access)

#### 4. Media Partition (`/media`)
**Purpose:** User-uploaded files (photos, videos, attachments)
**Size:** 500 GB - 10 TB+ (largest partition, scalable)
**Filesystem:** XFS or ZFS (optimized for large files)
**Mount Options:** `rw,nodev,nosuid,noexec`
**Encryption:** LUKS2 or filesystem-level encryption

**Contents:**
- User photos (organized by user/date/album)
- User videos
- File attachments
- Profile pictures
- Thumbnails and transcoded versions

**Structure:**
```
/media/
  ├── users/
  │   └── {user-id}/
  │       ├── photos/
  │       │   └── {year}/{month}/
  │       │       └── {photo-id}.{ext}
  │       ├── videos/
  │       ├── documents/
  │       └── avatars/
  ├── thumbnails/
  │   └── {photo-id}/
  │       ├── small.jpg
  │       ├── medium.jpg
  │       └── large.jpg
  └── temp/
      └── uploads-in-progress/
```

**Rationale for Separate Partition:**
- **Performance:** Large files don't compete with database I/O
- **Scalability:** Easy to expand or move to separate storage (S3, NAS)
- **Backup strategy:** Different backup frequency/retention than database
- **Deduplication:** Can implement content-addressable storage later

**Security Features:**
- Encrypted at rest (LUKS2)
- Per-file encryption option (for zero-knowledge architecture)
- Virus scanning on upload (ClamAV or similar)
- Access control lists (ACLs) restrict access by user
- No executable permissions (noexec mount)

#### 5. Logs Partition (`/logs`)
**Purpose:** System logs, application logs, audit trails
**Size:** 50-100 GB (with log rotation)
**Filesystem:** ext4
**Mount Options:** `rw,nodev,nosuid,noexec`
**Retention:** Configurable rotation (default: 90 days)

**Contents:**
- System logs (syslog, journald)
- Hypernet application logs
- API access logs (with PII redaction)
- Security audit logs
- Error and exception logs
- Performance metrics

**Structure:**
```
/logs/
  ├── system/
  │   ├── syslog
  │   ├── kern.log
  │   └── auth.log
  ├── hypernet/
  │   ├── application.log
  │   ├── api-access.log
  │   ├── security-audit.log
  │   └── errors.log
  ├── integrations/
  │   └── {integration-name}.log
  └── archived/
      └── {year}/{month}/
```

**Security Features:**
- Append-only where possible (prevents log tampering)
- Separate partition prevents log overflow from affecting system
- Logs rotated and compressed regularly
- Archived logs can be moved to cold storage
- PII scrubbing in logs (no passwords, tokens, sensitive data)
- Optional: Forward to remote syslog (SIEM) for tamper-proof auditing

#### 6. Cache Partition (`/cache`)
**Purpose:** Temporary data, API response caches, session data
**Size:** 20-50 GB
**Filesystem:** tmpfs (RAM) or ext4
**Mount Options:** `rw,nodev,nosuid,noexec`
**Persistence:** Volatile, can be wiped on restart

**Contents:**
- API response caches (Redis/Memcached)
- Session data
- Temporary file uploads (before moving to /media)
- Compiled templates and assets
- Rate limiting counters

**Rationale:**
- Keeps temporary data off main partitions
- Can be RAM-backed (tmpfs) for performance
- Safe to wipe without data loss
- Prevents cache pollution of other partitions

---

## Security Model

Hypernet employs a **defense-in-depth** strategy with multiple layers of security.

### Security Layers

#### Layer 1: Network Perimeter
- **Firewall:** Only expose API ports (443 for HTTPS, configurable)
- **DDoS protection:** Rate limiting, connection limits
- **Intrusion detection:** Fail2ban or similar
- **No direct database access:** Database port not exposed externally

#### Layer 2: API Gateway
- **Authentication:** JWT tokens, OAuth2, API keys
- **Authorization:** Role-based access control (RBAC)
- **Input validation:** All inputs sanitized and validated
- **Rate limiting:** Per-user, per-IP, per-endpoint
- **TLS encryption:** All API traffic over HTTPS (TLS 1.3)

#### Layer 3: Application Security
- **Input sanitization:** SQL injection, XSS, command injection prevention
- **Output encoding:** Prevent injection attacks
- **CSRF protection:** Tokens for state-changing operations
- **Secure session management:** HttpOnly, Secure, SameSite cookies
- **Dependency scanning:** Regular updates for known vulnerabilities

#### Layer 4: Data Security
- **Encryption at rest:** LUKS2 for partitions, per-field encryption for sensitive data
- **Encryption in transit:** TLS 1.3 for all network communication
- **Encryption in use:** (Future) Confidential computing for sensitive operations
- **Key management:** Hardware-backed keys (TPM/HSM) where possible

#### Layer 5: Infrastructure Security
- **Immutable system:** Read-only root partition
- **Minimal attack surface:** Only necessary services running
- **No remote shell by default:** SSH disabled in production or key-only with 2FA
- **Automated updates:** Security patches applied via verified system updates
- **Audit logging:** All security events logged and monitored

### Threat Model

| Threat | Mitigation |
|--------|------------|
| **Network attacks (DDoS, port scanning)** | Firewall, rate limiting, fail2ban |
| **API attacks (injection, broken auth)** | Input validation, JWT auth, RBAC |
| **Data breaches** | Encryption at rest, per-field encryption, access controls |
| **Insider threats** | Audit logging, least privilege, separation of duties |
| **Supply chain attacks** | Verified system images, dependency scanning, pinned versions |
| **Physical access** | Disk encryption, secure boot, TPM-backed keys |
| **Man-in-the-middle** | TLS 1.3, certificate pinning (for clients) |
| **Rootkits/malware** | Immutable system, read-only root, integrity checking |

---

## Deployment Architecture

### Phase 1: Self-Hosted Single Server

```
┌─────────────────────────────────────────┐
│         Internet / Public Network        │
└──────────────────┬──────────────────────┘
                   │
           ┌───────▼────────┐
           │   Firewall     │  (Only port 443 open)
           │  (iptables)    │
           └───────┬────────┘
                   │
           ┌───────▼────────┐
           │  Hypernet Node │
           │                │
           │  ┌──────────┐  │
           │  │ API GW   │  │  (HTTPS, TLS 1.3)
           │  └────┬─────┘  │
           │       │        │
           │  ┌────▼─────┐  │
           │  │ App Core │  │  (Python/FastAPI)
           │  └────┬─────┘  │
           │       │        │
           │  ┌────▼─────┐  │
           │  │ Database │  │  (PostgreSQL)
           │  └──────────┘  │
           │                │
           │  [Partitions]  │
           │  /     (RO)    │
           │  /config       │
           │  /data    (encrypted)
           │  /media   (encrypted)
           │  /logs         │
           │  /cache        │
           └────────────────┘
```

**Deployment Steps:**
1. Provision server (physical or VPS)
2. Install Ubuntu Server 24.04 LTS
3. Partition disk according to architecture
4. Deploy Hypernet system image to `/` partition
5. Configure `/config` with deployment-specific settings
6. Initialize database in `/data`
7. Start Hypernet services
8. Configure firewall and TLS certificates
9. Run health checks and smoke tests
10. Go live

### Phase 2: Multi-Server (Future)

```
       Load Balancer
            │
    ┌───────┼───────┐
    ▼       ▼       ▼
  API-1   API-2   API-3  (Stateless API servers)
    └───────┼───────┘
            │
    ┌───────▼───────┐
    │   Database    │   (Primary + Replicas)
    │   Cluster     │
    └───────┬───────┘
            │
    ┌───────▼───────┐
    │  Object       │   (S3-compatible)
    │  Storage      │
    └───────────────┘
```

### Phase 3: Distributed/Federated (Future)

Users can run their own Hypernet nodes that federate and sync data.

```
┌─────────────┐       ┌─────────────┐
│ User Node 1 │◄─────►│ User Node 2 │
└──────┬──────┘       └──────┬──────┘
       │                     │
       └──────────┬──────────┘
                  ▼
         ┌─────────────────┐
         │  Central Index  │  (Optional discovery)
         │   (Optional)    │
         └─────────────────┘
```

---

## API-First Design Philosophy

**Core Principle:** Every feature in Hypernet is accessible via API. The web UI, mobile apps, CLI tools, and third-party integrations are all API clients.

### Benefits:
- **Flexibility:** Any client (web, mobile, desktop, CLI) can access full functionality
- **Extensibility:** Third-party developers can build on Hypernet
- **Testing:** APIs are easier to test than UIs
- **Consistency:** Single source of truth for business logic
- **Future-proof:** New clients can be added without backend changes

### API Design Requirements:
- **RESTful conventions** for CRUD operations
- **GraphQL endpoint** for complex queries (optional Phase 2)
- **Versioning** via URL path (`/api/v1/...`)
- **Comprehensive documentation** (OpenAPI/Swagger)
- **Rate limiting** to prevent abuse
- **Pagination** for large result sets
- **Filtering, sorting, searching** capabilities
- **Consistent error responses** (RFC 7807 Problem Details)

### API Security:
- **Authentication:** JWT tokens (short-lived access + long-lived refresh)
- **Authorization:** RBAC with fine-grained permissions
- **Input validation:** JSON Schema or Pydantic models
- **Rate limiting:** Token bucket or sliding window
- **Audit logging:** All API calls logged (with PII redaction)

**See:** `API-Design/` folder for detailed specifications

---

## Data Flow Architecture

### Upload Flow (Photo/Video)

```
Client
  │
  │ 1. POST /api/v1/media/upload (multipart/form-data)
  ▼
API Gateway
  │ 2. Authenticate JWT token
  │ 3. Validate file type, size
  │ 4. Scan for malware
  ▼
Application Core
  │ 5. Generate unique ID
  │ 6. Extract metadata (EXIF, etc.)
  │ 7. Create thumbnails
  │ 8. Encrypt file (optional)
  ▼
Storage Layer
  │ 9. Write to /media/{user-id}/photos/{year}/{month}/{id}.jpg
  │ 10. Write metadata to database
  ▼
Response
  │ 11. Return media object JSON
  └──► Client
```

### Social Media Integration Flow

```
Client
  │
  │ 1. POST /api/v1/integrations/instagram/sync
  ▼
API Gateway
  │ 2. Authenticate user
  ▼
Integration Plugin
  │ 3. Load Instagram credentials from /config
  │ 4. Call Instagram API (with rate limiting)
  │ 5. Scrub/sanitize API response
  │ 6. Normalize data to Hypernet schema
  ▼
Application Core
  │ 7. Deduplicate (check if already imported)
  │ 8. Create media objects
  │ 9. Create links (photo → Instagram post)
  │ 10. Store in database + /media
  ▼
Response
  │ 11. Return sync status
  └──► Client
```

---

## Future Evolution Path

### Phase 1 (Current): Single-Server, Self-Hosted
- Single Hypernet node
- API-first architecture
- Basic integrations (1-2 platforms)
- Self-hosted deployment

### Phase 2: Multi-Server, Scalable
- Load-balanced API servers
- Database clustering (primary + replicas)
- Object storage (S3-compatible)
- Cloud deployment option (AWS, GCP, Azure)

### Phase 3: Distributed/Federated
- Users run their own nodes
- Node-to-node federation protocol
- Decentralized identity (DIDs)
- Peer-to-peer data sync

### Phase 4: Decentralized
- Blockchain/IPFS for data integrity (optional)
- Smart contracts for access control (optional)
- Fully peer-to-peer architecture
- No central servers required

---

## Technology Stack

### Backend
- **Language:** Python 3.11+
- **Framework:** FastAPI (async, high-performance, auto-documentation)
- **Alternative:** Django + Django REST Framework (if admin UI needed)
- **ASGI Server:** Uvicorn or Hypercorn

### Database (To Be Determined - See Database-Design/)
- **Primary:** PostgreSQL 15+ (relational + JSONB for flexibility)
- **Alternative:** SQLite (for single-user nodes)
- **Time-Series:** TimescaleDB or InfluxDB (for logs/metrics)
- **Cache:** Redis (for sessions, API caches, rate limiting)

### Storage
- **File System:** XFS (for media), ext4 (for database)
- **Encryption:** LUKS2 (full-disk), Fernet or AES-256-GCM (per-file)
- **Future:** S3-compatible object storage (MinIO, Wasabi, AWS S3)

### Security
- **TLS:** Let's Encrypt (automatic certificate management)
- **Secrets Management:** HashiCorp Vault or AWS Secrets Manager (future)
- **WAF:** ModSecurity or Cloudflare (if cloud-hosted)
- **Malware Scanning:** ClamAV

### Monitoring & Logging
- **Logging:** Python logging module → structured JSON logs
- **Log Aggregation:** Loki or ELK stack (future)
- **Metrics:** Prometheus + Grafana
- **Tracing:** OpenTelemetry (future)
- **Alerting:** Alertmanager

### Development Tools
- **Version Control:** Git + GitHub
- **CI/CD:** GitHub Actions or GitLab CI
- **Testing:** pytest, pytest-asyncio, coverage
- **Linting:** ruff, black, mypy
- **Dependency Management:** Poetry or pip-tools

### Infrastructure
- **OS:** Ubuntu Server 24.04 LTS
- **Containerization:** Docker (for development), Podman (optional)
- **Orchestration:** Systemd (Phase 1), Kubernetes (Phase 2+)
- **Backups:** Restic, Borg, or rsync + encryption

---

## Critical Design Decisions

### Decision Log

#### 1. Immutable System Partition
**Decision:** Use read-only root partition with atomic A/B updates
**Rationale:** Maximum security, prevents runtime tampering, enables instant rollback
**Trade-offs:** More complex update process, requires more disk space (2x system partition)
**Alternatives Considered:** Traditional package manager updates (rejected: too slow, risky)

#### 2. API-First Architecture
**Decision:** All functionality exposed via versioned REST APIs
**Rationale:** Flexibility for multiple clients, future-proof, easier testing
**Trade-offs:** More initial development, requires good API design discipline
**Alternatives Considered:** Monolithic web app (rejected: not flexible enough)

#### 3. Python + FastAPI
**Decision:** Use Python with FastAPI framework
**Rationale:** Excellent for rapid development, security libraries, AI/ML future, async support
**Trade-offs:** Slower than Rust/Go, requires more resources
**Alternatives Considered:** Rust (too complex for Phase 1), Go (less mature ecosystem for our needs)

#### 4. Separate Media Partition
**Decision:** Store user uploads separate from database
**Rationale:** Performance, scalability, backup flexibility
**Trade-offs:** Slightly more complex deployment
**Alternatives Considered:** Store in database as BLOBs (rejected: poor performance)

#### 5. PostgreSQL for Primary Database
**Decision:** Use PostgreSQL for structured data
**Rationale:** ACID compliance, JSON support, mature, excellent for relational data
**Trade-offs:** More complex than SQLite, requires more resources
**Alternatives Considered:** MongoDB (rejected: prefer ACID), SQLite (good for single-user, may use for that case)

#### 6. Self-Hosted First, Cloud Later
**Decision:** Design for self-hosted deployment initially
**Rationale:** User control, privacy, cost, aligns with mission
**Trade-offs:** More complex for users to deploy
**Alternatives Considered:** Cloud-first (rejected: users want control)

---

## Open Questions & Research Needed

### Database Design
- **Object model:** How to represent photos, videos, posts, messages?
- **Link model:** How to represent relationships between objects?
- **Schema evolution:** How to handle schema changes over time?
- **Graph vs. Relational:** Do we need a graph database for links?
- **See:** `Database-Design/` folder for research

### API Design
- **Object representation:** JSON schema for each object type?
- **Link representation:** How to query/traverse links via API?
- **GraphQL vs. REST:** Which is better for complex queries?
- **See:** `API-Design/` folder for specifications

### Integration Architecture
- **Plugin model:** How do plugins register and execute?
- **Rate limiting:** How to handle API rate limits from external services?
- **Data normalization:** How to map external data to Hypernet schema?
- **See:** Research folder

---

## Next Steps

1. **Architecture Review** (This document) ✓
2. **Development Roadmap** - Define Phase 1 milestones
3. **API Design** - Define object model, link model, endpoints
4. **Database Research** - Evaluate storage options for objects/links
5. **Security Framework** - Detail input validation, encryption, audit logging
6. **Plugin Architecture** - Design integration framework
7. **Prototype** - Build minimal API + one integration

---

**Status:** Ready for review and refinement
**Next Document:** `Development-Roadmap/Phase-1-Plan.md`
