# Hypernet Core 0.1 - Phase 1 Development Roadmap

**Version:** 0.1.0
**Last Updated:** 2026-02-03
**Target Completion:** Q2 2026 (estimated 3-4 months)
**Status:** Planning

---

## Table of Contents

1. [Phase 1 Objectives](#phase-1-objectives)
2. [Success Criteria](#success-criteria)
3. [Milestone Breakdown](#milestone-breakdown)
4. [Task Prioritization](#task-prioritization)
5. [Team & Resources](#team--resources)
6. [Risk Management](#risk-management)
7. [Dependencies](#dependencies)

---

## Phase 1 Objectives

### Primary Goal
Build the **foundational architecture** for Hypernet Core with one working end-to-end integration to prove the concept.

### Scope

**In Scope:**
- ✅ Core system architecture (partition management, immutable infrastructure)
- ✅ API foundation (authentication, basic CRUD, versioning)
- ✅ Database layer (schema design, ORM, migrations)
- ✅ Security framework (input validation, encryption, audit logging)
- ✅ **One complete integration** (e.g., Instagram or Google Photos) from API to storage
- ✅ Photo/video upload and retrieval
- ✅ Basic user management (authentication, authorization)
- ✅ Deployment tooling (system image builder, update mechanism)
- ✅ Developer documentation
- ✅ Testing framework and basic test coverage

**Out of Scope (Phase 2+):**
- ❌ Multiple integrations (just one to prove concept)
- ❌ Advanced features (AI tagging, facial recognition, etc.)
- ❌ Web UI (API only for Phase 1)
- ❌ Mobile apps
- ❌ Multi-server deployment
- ❌ Federation/distributed nodes
- ❌ Advanced analytics or reporting

### Key Deliverables

1. **Working Hypernet Core API** (v0.1.0)
2. **One functional integration** (social media or cloud storage)
3. **Secure deployment** (self-hosted, single-server)
4. **Comprehensive documentation** (architecture, API, deployment guide)
5. **Automated testing** (unit + integration tests, >70% coverage)
6. **System image builder** (reproducible, signed images)

---

## Success Criteria

Phase 1 is complete when:

- [ ] A user can **deploy Hypernet** on a Ubuntu server following documentation
- [ ] A user can **authenticate** via API (JWT tokens)
- [ ] A user can **upload a photo** via API and it's stored securely
- [ ] A user can **retrieve their photos** via API with metadata
- [ ] A user can **connect an integration** (e.g., Instagram) and import photos
- [ ] Imported photos are **deduplicated** (don't re-import duplicates)
- [ ] All API inputs are **validated and sanitized**
- [ ] All data is **encrypted at rest** (LUKS2 partitions)
- [ ] All API traffic is **encrypted in transit** (TLS 1.3)
- [ ] All security events are **logged** to audit trail
- [ ] System can be **updated atomically** (A/B partition update)
- [ ] Automated tests run and pass (CI/CD pipeline)
- [ ] API documentation is auto-generated and accurate

**Stretch Goals:**
- [ ] Two integrations working (e.g., Instagram + Google Photos)
- [ ] Basic CLI client for API testing
- [ ] Prometheus metrics endpoint
- [ ] Database backup/restore scripts

---

## Milestone Breakdown

### Milestone 0: Planning & Design (Weeks 1-2)
**Status:** In Progress

**Tasks:**
- [x] System architecture design
- [x] Partition layout specification
- [ ] API design (object model, endpoints)
- [ ] Database schema design (research + implementation)
- [ ] Security framework specification
- [ ] Integration plugin architecture design
- [ ] Development environment setup

**Deliverables:**
- Architecture documentation (00-System-Architecture-Overview.md)
- Partition management spec (01-Partition-Management-And-Updates.md)
- API specification (OpenAPI/Swagger)
- Database schema (ERD + migrations)
- Security requirements doc
- Development roadmap (this document)

**Key Decisions Needed:**
- Finalize object/link data model
- Choose ORM (SQLAlchemy vs. alternatives)
- Define authentication strategy (JWT details, OAuth2 integration)
- Select first integration to build (Instagram, Google Photos, or other)

---

### Milestone 1: Foundation (Weeks 3-5)
**Goal:** Core infrastructure working (no integrations yet)

**Tasks:**

#### 1.1 Development Environment
- [ ] Set up Ubuntu 24.04 VM or dev server
- [ ] Install Python 3.11+, PostgreSQL, Redis
- [ ] Create project structure (`0.1.1 - Core System/`, etc.)
- [ ] Set up Git repository (if not already)
- [ ] Configure IDE/editor (VS Code, PyCharm)
- [ ] Install dev dependencies (pytest, ruff, mypy, etc.)

#### 1.2 Database Layer
- [ ] Design database schema (users, media, metadata, links)
- [ ] Set up PostgreSQL database
- [ ] Implement ORM models (SQLAlchemy)
- [ ] Create database migration system (Alembic)
- [ ] Write initial migration (create tables)
- [ ] Implement database connection pooling
- [ ] Add database health checks

#### 1.3 API Core
- [ ] Initialize FastAPI project
- [ ] Implement basic API structure (routes, middleware)
- [ ] Add request logging
- [ ] Add error handling and exception middleware
- [ ] Implement health check endpoint (`/health`)
- [ ] Set up CORS configuration
- [ ] Add API versioning (`/api/v1/...`)

#### 1.4 Authentication & Authorization
- [ ] Design JWT token structure (access + refresh tokens)
- [ ] Implement user registration endpoint
- [ ] Implement login endpoint (returns JWT)
- [ ] Implement refresh token endpoint
- [ ] Create authentication middleware (verify JWT on protected routes)
- [ ] Implement role-based access control (RBAC) foundation
- [ ] Add password hashing (bcrypt or argon2)

#### 1.5 Security Foundation
- [ ] Implement input validation (Pydantic models)
- [ ] Add SQL injection prevention (ORM + parameterized queries)
- [ ] Implement rate limiting (Redis-backed)
- [ ] Add CSRF protection for state-changing operations
- [ ] Configure secure headers (HSTS, CSP, X-Frame-Options)
- [ ] Set up TLS certificates (Let's Encrypt or self-signed for dev)

**Deliverables:**
- Working API with `/health`, `/auth/register`, `/auth/login`
- Database with users table
- Authentication working (can get JWT token)
- Basic security measures in place

**Testing:**
```bash
# Should work by end of Milestone 1:
curl https://localhost:8443/health
# → {"status": "healthy"}

curl -X POST https://localhost:8443/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123!"}'
# → {"user_id": "...", "email": "..."}

curl -X POST https://localhost:8443/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123!"}'
# → {"access_token": "...", "refresh_token": "...", "token_type": "Bearer"}
```

---

### Milestone 2: Media Management (Weeks 6-8)
**Goal:** Upload, store, and retrieve photos/videos

**Tasks:**

#### 2.1 Data Models
- [ ] Design Media object model (Photo, Video classes)
- [ ] Design Metadata model (EXIF, tags, dates, locations)
- [ ] Implement ORM models for media
- [ ] Create database migrations for media tables
- [ ] Design file storage structure in `/media` partition

#### 2.2 Upload Functionality
- [ ] Implement file upload endpoint (`POST /api/v1/media/upload`)
- [ ] Add file type validation (MIME type checking)
- [ ] Add file size limits (configurable, e.g., 50MB max)
- [ ] Implement malware scanning (ClamAV integration)
- [ ] Extract EXIF metadata from photos (exifread or pillow)
- [ ] Generate unique IDs for media objects (UUID)
- [ ] Save files to `/media/{user-id}/photos/{year}/{month}/{id}.{ext}`
- [ ] Save metadata to database
- [ ] Create thumbnails (small, medium, large)
- [ ] Return media object JSON to client

#### 2.3 Retrieval Functionality
- [ ] Implement media listing endpoint (`GET /api/v1/media`)
- [ ] Add pagination (limit, offset or cursor-based)
- [ ] Add filtering (by date, type, tags)
- [ ] Add sorting (by date, name, size)
- [ ] Implement single media retrieval (`GET /api/v1/media/{id}`)
- [ ] Implement thumbnail retrieval (`GET /api/v1/media/{id}/thumbnail/{size}`)
- [ ] Add original file download (`GET /api/v1/media/{id}/download`)

#### 2.4 Security & Performance
- [ ] Implement per-user access control (users can only see their own media)
- [ ] Add file encryption (optional, defer if complex)
- [ ] Optimize database queries (indexes, select only needed fields)
- [ ] Add response caching (Redis) for media listings
- [ ] Implement streaming for large files (chunked transfer)

**Deliverables:**
- Working media upload and retrieval
- Photo metadata extraction
- Thumbnail generation
- User isolation (can't access others' photos)

**Testing:**
```bash
# Upload a photo
curl -X POST https://localhost:8443/api/v1/media/upload \
  -H "Authorization: Bearer {token}" \
  -F "file=@photo.jpg"
# → {"id": "...", "filename": "photo.jpg", "size": 1234567, ...}

# List photos
curl https://localhost:8443/api/v1/media \
  -H "Authorization: Bearer {token}"
# → {"items": [{...}, {...}], "total": 42, "page": 1}

# Get specific photo
curl https://localhost:8443/api/v1/media/{id} \
  -H "Authorization: Bearer {token}"
# → {"id": "...", "url": "/media/{id}/download", ...}
```

---

### Milestone 3: First Integration (Weeks 9-11)
**Goal:** One working social media or cloud storage integration

**Integration Options (Choose One):**

1. **Instagram** (via Meta Graph API)
   - Pros: Popular, good API documentation
   - Cons: Requires Meta app approval, rate limits

2. **Google Photos** (via Google Photos Library API)
   - Pros: Excellent API, good for testing cloud integration
   - Cons: OAuth2 setup complexity

3. **Local folder sync** (simple file watcher)
   - Pros: Easy to build, no external dependencies
   - Cons: Less impressive, doesn't test API integration skills

**Recommended:** Start with **Google Photos** (good balance of complexity and value)

#### 3.1 Plugin Architecture
- [ ] Design plugin interface (base class or protocol)
- [ ] Implement plugin registry/loader
- [ ] Create plugin configuration system
- [ ] Add plugin lifecycle (initialize, sync, shutdown)
- [ ] Implement plugin sandboxing/isolation (if possible)

#### 3.2 OAuth2 Flow
- [ ] Implement OAuth2 authorization flow (for Google Photos)
- [ ] Create OAuth2 callback endpoint
- [ ] Store OAuth tokens securely (encrypted in database)
- [ ] Implement token refresh mechanism
- [ ] Add OAuth token management endpoints (connect, disconnect, status)

#### 3.3 Integration Implementation
- [ ] Create Google Photos plugin
- [ ] Implement photo listing from Google Photos API
- [ ] Implement photo download from Google Photos
- [ ] Map Google Photos metadata to Hypernet schema
- [ ] Implement deduplication (check if photo already exists)
- [ ] Create links between Hypernet media and Google Photos items
- [ ] Handle rate limiting (exponential backoff)
- [ ] Implement pagination for large libraries
- [ ] Add error handling and retry logic

#### 3.4 Sync Functionality
- [ ] Implement sync endpoint (`POST /api/v1/integrations/google-photos/sync`)
- [ ] Track sync state (last sync time, cursor position)
- [ ] Implement incremental sync (only new items)
- [ ] Add sync status endpoint (progress, errors)
- [ ] Create background job system (optional, or just sync on-demand)

**Deliverables:**
- Working Google Photos integration
- Users can connect their Google account
- Users can import photos from Google Photos
- Deduplication works (no duplicate imports)
- Metadata preserved (dates, captions, locations)

**Testing:**
```bash
# Start OAuth flow
curl https://localhost:8443/api/v1/integrations/google-photos/connect \
  -H "Authorization: Bearer {token}"
# → {"auth_url": "https://accounts.google.com/..."}

# (User visits auth_url, authorizes, redirected back to callback)

# Trigger sync
curl -X POST https://localhost:8443/api/v1/integrations/google-photos/sync \
  -H "Authorization: Bearer {token}"
# → {"status": "syncing", "job_id": "..."}

# Check sync status
curl https://localhost:8443/api/v1/integrations/google-photos/sync-status \
  -H "Authorization: Bearer {token}"
# → {"status": "complete", "imported": 150, "skipped": 5, "errors": 0}

# List media (should now include Google Photos imports)
curl https://localhost:8443/api/v1/media \
  -H "Authorization: Bearer {token}"
# → {"items": [...], "total": 150}
```

---

### Milestone 4: Deployment & Operations (Weeks 12-13)
**Goal:** Production-ready deployment process

**Tasks:**

#### 4.1 System Image Builder
- [ ] Create build script for system image
- [ ] Set up Docker or VM for reproducible builds
- [ ] Automate dependency installation (apt, pip)
- [ ] Pre-compile Python bytecode
- [ ] Generate filesystem image (squashfs or ext4)
- [ ] Implement GPG signing for images
- [ ] Create image verification script

#### 4.2 Deployment Tooling
- [ ] Write partition setup script (for fresh installs)
- [ ] Create configuration template (for `/config`)
- [ ] Implement secrets encryption script (TPM or passphrase)
- [ ] Write A/B partition update script (`hypernet-admin update`)
- [ ] Create rollback script (`hypernet-admin rollback`)
- [ ] Write health check script (runs on boot)

#### 4.3 Documentation
- [ ] Write deployment guide (step-by-step for Ubuntu)
- [ ] Document configuration options
- [ ] Create API documentation (OpenAPI + examples)
- [ ] Write developer guide (for contributors)
- [ ] Create troubleshooting guide (common issues)
- [ ] Write security hardening guide

#### 4.4 Monitoring & Logging
- [ ] Implement structured logging (JSON format)
- [ ] Add log rotation (logrotate)
- [ ] Create Prometheus metrics endpoint (`/metrics`)
- [ ] Implement audit logging (all security events)
- [ ] Add performance tracing (optional - OpenTelemetry)

#### 4.5 Backup & Recovery
- [ ] Write database backup script (pg_dump)
- [ ] Write media backup script (Restic or rsync)
- [ ] Document restore procedure
- [ ] Test backup and restore (verify data integrity)

**Deliverables:**
- Deployable system image
- Complete deployment guide
- API documentation
- Automated backups
- Monitoring and logging

---

### Milestone 5: Testing & Hardening (Weeks 14-15)
**Goal:** Comprehensive testing and security review

**Tasks:**

#### 5.1 Automated Testing
- [ ] Write unit tests for core functions (pytest)
- [ ] Write integration tests for API endpoints
- [ ] Write tests for authentication flow
- [ ] Write tests for media upload/retrieval
- [ ] Write tests for integration sync
- [ ] Achieve >70% code coverage
- [ ] Set up CI/CD pipeline (GitHub Actions or GitLab CI)
- [ ] Automate tests on every commit

#### 5.2 Security Testing
- [ ] Run security scanner (Bandit, Safety)
- [ ] Test input validation (fuzz testing)
- [ ] Test authentication bypass attempts
- [ ] Test authorization (users can't access others' data)
- [ ] Test SQL injection vulnerabilities
- [ ] Test XSS and CSRF protection
- [ ] Run dependency vulnerability scan
- [ ] Penetration testing (basic, or hire professional)

#### 5.3 Performance Testing
- [ ] Load test API endpoints (Locust or k6)
- [ ] Test file upload with large files
- [ ] Test media listing with large datasets (10k+ photos)
- [ ] Optimize slow queries (database indexes)
- [ ] Test rate limiting under load
- [ ] Profile Python code (cProfile, py-spy)

#### 5.4 Documentation Review
- [ ] Review all documentation for accuracy
- [ ] Test deployment guide (fresh install on clean VM)
- [ ] Test API examples (make sure they work)
- [ ] Add diagrams and visuals where helpful
- [ ] Spell check and grammar review

**Deliverables:**
- >70% test coverage
- All security tests passing
- Performance benchmarks documented
- CI/CD pipeline running
- Reviewed and accurate documentation

---

### Milestone 6: Release (Week 16)
**Goal:** Public release of Hypernet Core 0.1.0

**Tasks:**

#### 6.1 Release Preparation
- [ ] Finalize version number (0.1.0)
- [ ] Create release notes (features, known issues, limitations)
- [ ] Tag Git repository (v0.1.0)
- [ ] Build final system image
- [ ] Sign and publish system image to release server
- [ ] Update documentation with final version numbers

#### 6.2 Announcement
- [ ] Write announcement blog post
- [ ] Post to relevant communities (Reddit, Hacker News, etc.)
- [ ] Share on social media
- [ ] Notify early testers and supporters

#### 6.3 Post-Release
- [ ] Monitor for issues and bug reports
- [ ] Provide user support (GitHub issues, Discord, forums)
- [ ] Plan Phase 2 features based on feedback
- [ ] Create Phase 2 roadmap

**Deliverables:**
- Hypernet Core 0.1.0 released
- Public announcement
- Active support and issue tracking

---

## Task Prioritization

### Must Have (P0)
1. API foundation (auth, basic CRUD)
2. Database layer (models, migrations)
3. Media upload and retrieval
4. Input validation and security basics
5. One working integration
6. Deployment guide

### Should Have (P1)
7. Automated testing (>50% coverage)
8. System image builder
9. A/B partition updates
10. Audit logging
11. TLS encryption
12. API documentation (OpenAPI)

### Nice to Have (P2)
13. >70% test coverage
14. Prometheus metrics
15. CLI client
16. Database backup scripts
17. Thumbnail generation optimization
18. Performance profiling

### Defer to Phase 2 (P3)
19. Multiple integrations
20. Web UI
21. Mobile apps
22. Advanced search
23. AI tagging
24. Facial recognition
25. Federation support

---

## Team & Resources

### Team Structure (Ideal)

- **1x Backend Developer** (Python/FastAPI, databases, security)
- **1x DevOps Engineer** (deployment, infrastructure, monitoring)
- **0.5x Security Consultant** (code review, penetration testing)
- **0.5x Technical Writer** (documentation)

**Reality for Phase 1:** Likely 1-2 people wearing multiple hats

### Time Estimates

- **Full-time (1 person):** 12-16 weeks
- **Part-time (1 person, 20 hrs/week):** 24-32 weeks
- **Team (2 people full-time):** 8-10 weeks

### Tools & Services Needed

**Free/Open-Source:**
- Ubuntu Server 24.04 LTS (OS)
- Python 3.11+ (language)
- PostgreSQL 15+ (database)
- Redis (cache)
- Git + GitHub (version control)
- pytest (testing)
- Let's Encrypt (TLS certificates)

**Paid (Optional):**
- VPS/dedicated server ($10-50/month)
- Domain name ($10-15/year)
- Security audit ($500-2000 one-time)

**Total Budget:** ~$100-500 for Phase 1 (mostly hosting)

---

## Risk Management

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **API design needs major changes** | Medium | High | Thorough design review in Milestone 0, get feedback early |
| **Database schema doesn't scale** | Medium | Medium | Research best practices, design for flexibility, use migrations |
| **Integration API changes/breaks** | Medium | Medium | Abstract integration layer, version API contracts, handle gracefully |
| **Security vulnerability discovered** | Low | High | Regular security audits, automated scanning, follow best practices |
| **Performance issues at scale** | Medium | Medium | Load testing, profiling, optimize early, design for scalability |
| **Deployment complexity too high** | Low | Medium | Document thoroughly, test on fresh VMs, simplify where possible |
| **Scope creep (too many features)** | High | Medium | Stick to roadmap, defer non-essential features to Phase 2 |
| **Timeline slips** | Medium | Low | Prioritize ruthlessly, cut nice-to-haves if needed, adjust timeline |

---

## Dependencies

### External Dependencies

- **Google Photos API** (or chosen integration)
  - Risk: API changes, rate limits, approval process
  - Mitigation: Abstract integration layer, have backup integration option

- **Let's Encrypt** (for TLS certificates)
  - Risk: Service downtime, certificate renewal issues
  - Mitigation: Fallback to self-signed certs, automate renewal

- **Ubuntu package repositories**
  - Risk: Package availability, version compatibility
  - Mitigation: Pin versions, mirror critical packages

### Internal Dependencies

- **Architecture design** must be complete before implementation starts
- **API design** must be complete before Milestone 2
- **Database schema** must be finalized before Milestone 2
- **Authentication** must work before testing integrations
- **Media management** must work before integration sync

---

## Next Steps

### Immediate Actions (This Week)

1. [ ] **Finalize API design** - Define object model, link model, endpoints (see `API-Design/` folder)
2. [ ] **Research database schema** - How to store objects, links, metadata (see `Database-Design/` folder)
3. [ ] **Choose first integration** - Google Photos, Instagram, or simple folder sync?
4. [ ] **Set up development environment** - Ubuntu VM, Python, PostgreSQL, IDE
5. [ ] **Create project structure** - Initialize Python project in `0.1.1 - Core System/`

### This Month

1. [ ] Complete Milestone 0 (Planning & Design)
2. [ ] Begin Milestone 1 (Foundation)
3. [ ] Set up CI/CD pipeline (GitHub Actions)
4. [ ] Write first unit tests

### This Quarter

1. [ ] Complete Milestones 1-3 (Foundation, Media, Integration)
2. [ ] Have working prototype (can upload photos, sync from one integration)
3. [ ] Begin Milestone 4 (Deployment)

---

## Success Metrics

Track these metrics weekly:

- **Lines of code written** (rough progress indicator)
- **Test coverage %** (target: >70%)
- **API endpoints implemented** (target: 15-20 for Phase 1)
- **Documentation pages written**
- **Milestone completion %**
- **Open bugs/issues**
- **Security vulnerabilities** (target: 0 critical)

---

## Appendix: Technology Decisions Summary

| Component | Technology Choice | Rationale |
|-----------|------------------|-----------|
| **OS** | Ubuntu Server 24.04 LTS | Stable, long support, familiar |
| **Language** | Python 3.11+ | Rapid development, good libraries, future AI/ML |
| **Web Framework** | FastAPI | Async, fast, auto-documentation, modern |
| **Database** | PostgreSQL 15+ | ACID, JSON support, mature, excellent for relational |
| **Cache** | Redis | Fast, mature, good for sessions and rate limiting |
| **ORM** | SQLAlchemy | Mature, flexible, good PostgreSQL support |
| **Testing** | pytest | Standard Python testing, good plugin ecosystem |
| **Documentation** | OpenAPI (Swagger) | Auto-generated from FastAPI, interactive |
| **Encryption** | LUKS2 (disk), Fernet (secrets) | Standard, secure, well-tested |
| **TLS** | Let's Encrypt + certbot | Free, automated, trusted |
| **CI/CD** | GitHub Actions | Free for open-source, integrated with Git |

---

**Status:** Roadmap defined, ready to begin Milestone 0 (API and Database design)
**Next Document:** API-Design/Object-Model-Specification.md (CRITICAL - ties to everything)
