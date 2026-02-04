# Hypernet Core 0.1 - Planning & Documentation

## Overview

This directory contains all planning, architecture, and design documentation for Hypernet Core version 0.1.

---

## Directory Structure

```
0.1.0 - Planning & Documentation/
├── README.md (this file)
├── Architecture/
│   ├── 00-System-Architecture-Overview.md
│   ├── 01-Partition-Management-And-Updates.md
│   └── (more architecture docs to come)
├── API-Design/
│   └── (CRITICAL - Object model and API specifications)
├── Database-Design/
│   └── (Schema design and storage research)
├── Security-Framework/
│   └── (Security specifications and guidelines)
├── Development-Roadmap/
│   └── Phase-1-Roadmap.md
└── Research/
    └── (Research notes and evaluations)
```

---

## Document Reading Order

### For Understanding the Project

1. **Start here:** `Architecture/00-System-Architecture-Overview.md`
   - Complete system architecture
   - Design principles
   - Technology stack
   - Partition layout
   - Security model

2. **Deep dive:** `Architecture/01-Partition-Management-And-Updates.md`
   - How immutable infrastructure works
   - A/B partition updates
   - Configuration management
   - Backup strategy

3. **Implementation plan:** `Development-Roadmap/Phase-1-Roadmap.md`
   - 6 milestone breakdown (16 weeks)
   - Task prioritization
   - Success criteria
   - Risk management

### For Developers

Start with:
1. Architecture overview (understand the system)
2. Development roadmap (understand the plan)
3. **API Design** (NEXT - critical for implementation)
4. Database Design (schema and storage)
5. Security Framework (validation, encryption, auditing)

---

## Current Status

### Completed Documents ✅

- [x] System Architecture Overview
- [x] Partition Management and Updates
- [x] Phase 1 Development Roadmap

### In Progress 🚧

- [ ] **API Design** - CRITICAL NEXT STEP
  - Object model specification
  - Link model specification
  - API endpoint definitions
  - Request/response schemas
  - Authentication and authorization

- [ ] **Database Design** - NEEDS RESEARCH
  - Schema design for objects and links
  - Storage strategy (relational vs. graph vs. document)
  - Migration strategy
  - Performance considerations

### Not Started ⏳

- [ ] Security Framework (input validation, encryption, audit logging)
- [ ] Integration Plugin Architecture
- [ ] Testing Strategy
- [ ] Deployment Guide

---

## Key Design Decisions

### Architecture

1. **Immutable Infrastructure**
   - Read-only system partition
   - Atomic A/B updates
   - Verified system images

2. **Multi-Partition Layout**
   - `/` - System (immutable)
   - `/config` - Configuration
   - `/data` - Database
   - `/media` - User uploads
   - `/logs` - Audit trails
   - `/cache` - Temporary data

3. **API-First Design**
   - All functionality via REST API
   - Versioned endpoints (`/api/v1/...`)
   - JWT authentication
   - Rate limiting and throttling

4. **Security in Depth**
   - Encrypted partitions (LUKS2)
   - TLS 1.3 for all traffic
   - Input validation and sanitization
   - Audit logging
   - RBAC authorization

### Technology Stack

- **Backend:** Python 3.11+ with FastAPI
- **Database:** PostgreSQL 15+ (relational + JSONB)
- **Cache:** Redis (sessions, rate limiting)
- **Storage:** XFS (media), ext4 (database)
- **Encryption:** LUKS2 (disk), Fernet (secrets)
- **Testing:** pytest with >70% coverage target
- **CI/CD:** GitHub Actions
- **Deployment:** Ubuntu Server 24.04 LTS

---

## Phase 1 Scope

### Included ✅

- Core API (auth, media management)
- Database layer (PostgreSQL + SQLAlchemy)
- One working integration (Google Photos or Instagram)
- Security foundation (validation, encryption, audit logging)
- Deployment tooling (system image builder, updates)
- Documentation (architecture, API, deployment guide)
- Testing (unit + integration, >70% coverage)

### Excluded (Phase 2+) ❌

- Multiple integrations
- Web UI
- Mobile apps
- Multi-server deployment
- Federation/distributed nodes
- Advanced features (AI tagging, search, etc.)

---

## Critical Path Items

### 1. API Design (BLOCKING EVERYTHING)

**Why Critical:**
- Defines how data is structured (objects, links)
- Determines database schema
- Affects integration design
- Difficult to change later

**Needs to Define:**
- Object types (Photo, Video, Post, Message, etc.)
- Link types (relationships between objects)
- API endpoints and operations
- Request/response formats
- Authentication and authorization model

**Status:** 🔴 Not started - HIGHEST PRIORITY

### 2. Database Schema (DEPENDS ON API DESIGN)

**Why Critical:**
- Must efficiently store objects and links
- Performance implications for queries
- Difficult to change after deployment

**Research Needed:**
- How to store flexible object types?
- How to represent links/relationships?
- Graph database vs. relational vs. hybrid?
- Indexing strategy for performance

**Status:** 🔴 Not started - NEEDS RESEARCH

### 3. Integration Plugin Architecture

**Why Important:**
- Determines how easy it is to add integrations
- Security implications (plugin sandboxing)
- Affects OAuth2 and API client design

**Status:** 🟡 Concept defined, needs detailed design

---

## Open Questions

### Architecture

1. **dm-verity for system partition?**
   - Pros: Block-level integrity checking, prevents tampering
   - Cons: Complexity, performance overhead
   - Decision: Defer to Phase 2?

2. **Automatic vs. Manual updates?**
   - Phase 1: Manual updates only
   - Phase 2: Add automatic update option

3. **Configuration migration strategy?**
   - How complex will config changes be between versions?
   - Need automated migration scripts?

### API Design

1. **Object model flexibility?**
   - Fixed schema vs. flexible attributes?
   - How to handle integration-specific fields?

2. **Link representation?**
   - First-class objects or just foreign keys?
   - Graph query capabilities needed?

3. **GraphQL vs. REST?**
   - REST for Phase 1, GraphQL in Phase 2?
   - Or both from the start?

### Database

1. **Relational vs. Graph vs. Document?**
   - PostgreSQL with JSONB (hybrid approach)?
   - Dedicated graph DB (Neo4j, ArangoDB)?
   - How to handle complex relationships?

2. **Per-field encryption?**
   - Encrypt sensitive fields in database?
   - Trade-off: Security vs. query performance

3. **Multi-tenancy strategy?**
   - One database per user (extreme isolation)?
   - Shared database with user_id foreign keys?

---

## Next Steps

### Immediate (This Week)

1. **API Design** - Define object model and link model
2. **Database Research** - Evaluate storage options for objects/links
3. **Integration Selection** - Choose first integration to build
4. **Dev Environment Setup** - Ubuntu VM, Python, PostgreSQL

### This Month

1. Complete all design documents
2. Set up development environment
3. Begin Milestone 1 (Foundation)
4. Create initial database schema
5. Implement basic API skeleton

### This Quarter

1. Complete Milestones 1-3 (Foundation, Media, Integration)
2. Working prototype (upload photos, sync from integration)
3. Begin deployment tooling
4. Start testing and hardening

---

## Contributing

### For Internal Team

1. Read Architecture Overview first
2. Review Development Roadmap
3. Check task assignments in roadmap
4. Follow coding standards (to be defined)
5. Write tests for all new code
6. Update documentation as you go

### For External Contributors (Future)

1. Read all planning docs
2. Check GitHub issues for open tasks
3. Discuss major changes before implementing
4. Follow contribution guide (to be written)
5. Sign contributor agreement (if required)

---

## Feedback and Questions

If you have questions or feedback on the architecture or roadmap:

1. Create a GitHub issue (for technical discussions)
2. Tag relevant team members
3. Reference specific document sections
4. Propose alternatives if suggesting changes

---

## Version History

- **v0.1.0** (2026-02-03) - Initial planning documents
  - System Architecture Overview
  - Partition Management spec
  - Phase 1 Development Roadmap

---

**Status:** Planning phase - Ready to begin API and Database design
**Next Critical Step:** Define object model and link model in `API-Design/`
