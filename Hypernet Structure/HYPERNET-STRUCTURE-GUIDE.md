# Hypernet Structure Guide
## Complete Navigation Guide to the Hypernet Folder System

**Version:** 1.0
**Last Updated:** February 9, 2026
**Purpose:** Help anyone navigate and use the Hypernet folder structure effectively
**Audience:** Team members, contributors, investors, partners

---

## Overview

The Hypernet folder structure is a **carefully designed hierarchical system** that organizes all information, code, and resources related to the Hypernet project. It follows a decimal numbering scheme inspired by library classification systems (Dewey Decimal), making it intuitive to navigate and scalable to handle massive amounts of information.

### Key Principles

1. **Hierarchical Organization** - Everything has a place in the hierarchy
2. **Unique Addressing** - Every item has a unique address in the system
3. **Human-Readable** - Numbers and names are meaningful and memorable
4. **Scalable** - Can grow from startup to global platform
5. **Version-Controlled** - All changes tracked via Git

### Quick Start

**Looking for something? Start here:**
- Strategic planning → `0.1 - Hypernet Core/0.1.0 - Planning & Documentation/`
- Source code → `0.1 - Hypernet Core/0.1.1 - Core System/`
- Object definitions → `0.0 - Object Type Registry/`
- Business docs → `3 - Businesses/3.1 - Hypernet/`
- Tasks → `3 - Businesses/3.1 - Hypernet/3.1.2 Task Management System/`

---

## Table of Contents

1. [Numbering System Explained](#numbering-system-explained)
2. [Top-Level Structure](#top-level-structure)
3. [Category 0: System Metadata](#category-0-system-metadata)
4. [Category 0.0: Object Type Registry](#category-00-object-type-registry)
5. [Category 0.1: Hypernet Core](#category-01-hypernet-core)
6. [Category 1: People](#category-1-people)
7. [Category 2: Aliases](#category-2-aliases)
8. [Category 3: Businesses](#category-3-businesses)
9. [Category 4: Knowledge](#category-4-knowledge)
10. [Category 5: Objects](#category-5-objects)
11. [How to Find Things](#how-to-find-things)
12. [How to Add New Content](#how-to-add-new-content)
13. [Best Practices](#best-practices)
14. [Common Tasks](#common-tasks)

---

## Numbering System Explained

### The Format

Addresses follow this pattern:
```
[Category].[Subcategory].[Type].[Instance].[Component]
```

### Examples

**Example 1: Task Management**
```
3.1.2.1.001
│ │ │ │ └── Instance (Task #001)
│ │ │ └──── Type (1 = Active/Open)
│ │ └────── Component (2 = Task Management System)
│ └──────── Subcategory (1 = Hypernet company)
└────────── Category (3 = Businesses)

Translation: Business > Hypernet > Task Management > Active Tasks > Task #001
```

**Example 2: Strategic Document**
```
0.1.0
│ │ └── Component (0 = Planning & Documentation)
│ └──── Subcategory (1 = Hypernet Core system)
└────── Category (0 = System Metadata)

Translation: System > Hypernet Core > Planning & Documentation
```

**Example 3: Object Type**
```
0.0.2.1
│ │ │ └── Instance (1 = Photo)
│ │ └──── Type (2 = Media Types)
│ └────── Subcategory (0 = Object Type Registry)
└──────── Category (0 = System Metadata)

Translation: System > Object Registry > Media Types > Photo
```

### Why This System?

**Benefits:**
- **Scalable** - Can expand infinitely (0.1.2.3.4.5.6...)
- **Unique** - Every address is unique and permanent
- **Navigable** - Hierarchical structure is intuitive
- **Searchable** - Easy to find related items
- **Future-Proof** - Won't need to reorganize as we grow

**Inspired By:**
- Dewey Decimal System (libraries)
- IP addressing (networks)
- DNS (internet domains)
- Object-oriented programming (namespaces)

---

## Top-Level Structure

### Directory Layout

```
Hypernet Structure/
├── 0/                                # Original metadata (older format)
├── 0.0 - Object Type Registry/       # Canonical object type definitions
├── 0.1 - Hypernet Core/              # Core system, code, planning
├── 1 - People/                       # Individual persons
├── 2 - Aliases/                      # Nicknames, usernames, alternate names
├── 3 - Businesses/                   # Commercial entities
├── 4 - Knowledge/                    # Information, research, documentation
├── 5 - Objects/                      # Physical items, devices
└── SESSION-SUMMARY-2026-02-04.md     # Work session summaries
```

### Category Assignments

| Number | Category | Description | Use For |
|--------|----------|-------------|---------|
| 0 | System Metadata | Infrastructure, schemas, control | Technical specs, governance |
| 0.0 | Object Registry | Object type definitions | Data model specifications |
| 0.1 | Hypernet Core | Core system and code | Source code, planning, APIs |
| 1 | People | Individual persons | Team members, users, contacts |
| 2 | Aliases | Alternate names | Usernames, nicknames, handles |
| 3 | Businesses | Commercial entities | Companies, organizations, tasks |
| 4 | Knowledge | Information and research | Documentation, research, education |
| 5 | Objects | Physical items | Devices, products, equipment |
| 6 | Media | Creative works | Audio, video, images (future) |
| 7 | Events | Time-bound occurrences | Meetings, milestones (future) |
| 8 | Locations | Places | Offices, data centers (future) |
| 9 | Concepts | Abstract ideas | Philosophies, theories (future) |

Note: Categories 6-9 are reserved for future use and not yet implemented in folder structure.

---

## Category 0: System Metadata

**Location:** `0/`

This is the **original metadata directory** using an older organizational format. Contains foundational documents about the Hypernet system itself.

### Contents

```
0/
├── 0.0 Metadata for Hypernet Information/
│   ├── 0.0.0 Library Addressing System.md
│   ├── 0.0.1 Version Control Schema.md
│   ├── 0.0.2 Address Allocation Protocol.md
│   └── 0.0.3 Deprecation and Archival Policy.md
├── 0.2 Node lists/
│   ├── 0.2.0 Node Architecture Overview.md
│   ├── 0.2.1 Storage Node Specification.md
│   ├── 0.2.2 Processing Node Specification.md
│   └── 0.2.3 Cerberus Node Specification.md
├── 0.3 Control data/
│   ├── 0.3.0 Governance Overview.md
│   ├── 0.3.1 Governance Bodies Details.md
│   └── 0.3.2 Voting Procedures.md
├── 0.5 Objects - Master Objects/
│   ├── 0.5.0 Master Object Schema.md
│   ├── 0.5.1 Person Object Schema.md
│   ├── 0.5.2 Organization Object Schema.md
│   └── 0.5.3 Document Object Schema.md
├── 0.6 Link Definitions/
│   ├── 0.6.0 Link Definitions Overview.md
│   ├── 0.6.1 Person Relationship Links.md
│   └── 0.6.2 Organizational Links.md
└── 0.7 Processes and Workflows/
    ├── 0.7.0 Processes and Workflows Overview.md
    ├── 0.7.1 Governance Workflows.md
    └── 0.7.2 Contribution Workflows.md
```

### Key Documents

**Must Read:**
- `0.0.0 Library Addressing System.md` - Explains this entire numbering system
- `0.5.0 Master Object Schema.md` - Foundation for all objects in Hypernet

**Important:**
- `0.0.1 Version Control Schema.md` - How versions work
- `0.6.0 Link Definitions Overview.md` - How objects relate to each other

### Use Cases

- Understanding the addressing system
- Learning about data models
- Governance and control processes
- Node architecture (for distributed system)

---

## Category 0.0: Object Type Registry

**Location:** `0.0 - Object Type Registry/`

This is the **canonical registry of all object types** used in Hypernet. Every type of data (Photo, Video, Email, Task, etc.) has a formal definition here.

### Structure

```
0.0 - Object Type Registry/
├── README.md
├── 0.0.0 - Registry Governance/
│   └── 00-How-To-Add-New-Types.md
├── 0.0.1 - Core Types/
│   ├── BaseObject.md
│   ├── User.md
│   ├── Link.md
│   └── Integration.md
├── 0.0.2 - Media Types/
│   ├── Photo.md
│   ├── Video.md
│   ├── Audio.md
│   ├── Document.md
│   └── Screenshot.md
├── 0.0.3 - Social Types/
│   ├── SocialPost.md
│   ├── SocialAccount.md
│   ├── SocialConnection.md
│   └── SocialMessage.md
├── 0.0.4 - Communication Types/
│   ├── Email.md
│   ├── SMS.md
│   ├── ChatMessage.md
│   ├── VoiceCall.md
│   └── VideoCall.md
├── 0.0.5 - Personal Types/
│   ├── Note.md
│   ├── Task.md
│   ├── CalendarEvent.md
│   └── Contact.md
├── 0.0.6 - System Types/
│   ├── Integration.md
│   ├── Notification.md
│   └── AuditLog.md
├── 0.0.7 - Web Types/
│   ├── Bookmark.md
│   └── WebPage.md
├── 0.0.8 - Life Types/
│   ├── Transaction.md
│   ├── Location.md
│   └── HealthRecord.md
└── 0.0.9 - Future Types/
    └── (Reserved for expansion)
```

### Key Concepts

**What is an Object Type?**
An object type is a formal specification for a category of data. For example:
- **Photo** - Defines what fields a photo has (filename, EXIF data, location, etc.)
- **Email** - Defines email structure (from, to, subject, body, attachments, etc.)
- **Task** - Defines task structure (title, description, due date, priority, etc.)

**What's in a Type Definition?**
Each type definition includes:
- Purpose and description
- Required fields
- Optional fields
- Data types for each field
- Relationships to other objects
- Validation rules
- Examples

### Total Object Types

**Current:** 28 object types defined
**Categories:** 9 type categories

### Use Cases

**For Developers:**
- Reference when building APIs
- Understanding data models
- Creating database schemas
- Validating data

**For Product:**
- Understanding what data we can store
- Planning new features
- Integrations planning

**For Users:**
- Understanding what data Hypernet manages
- Privacy and transparency

### How to Use

1. **Find a type:** Navigate to appropriate category (e.g., Media Types)
2. **Read the spec:** Open the .md file (e.g., Photo.md)
3. **Understand the fields:** Review required and optional fields
4. **See relationships:** Understand how it connects to other types
5. **Reference in code:** Use spec when implementing

---

## Category 0.1: Hypernet Core

**Location:** `0.1 - Hypernet Core/`

This is the **heart of the Hypernet project** - all source code, strategic planning, documentation, and development resources.

### Structure

```
0.1 - Hypernet Core/
├── 0.1.0 - Planning & Documentation/
│   ├── README.md
│   ├── MASTER-INDEX.md
│   ├── IMPLEMENTATION-STATUS.md
│   ├── DEVELOPMENT-PRIORITIES.md
│   ├── COMPLETE-STATUS-REPORT.md
│   ├── API-COMPLETION-SUMMARY.md
│   ├── FUNDING-STRATEGY-2026.md
│   ├── INVESTOR-PITCH-PLAYBOOK.md
│   ├── PITCH-DECK-CONTENT.md
│   ├── FINANCIAL-MODEL.md
│   ├── PRODUCT-ROADMAP-2026-2028.md
│   ├── GO-TO-MARKET-STRATEGY.md
│   ├── AI-PARTNERSHIP-STRATEGY.md
│   ├── COMPETITIVE-ANALYSIS.md
│   ├── Architecture/
│   │   ├── 00-System-Architecture-Overview.md
│   │   └── 01-Partition-Management-And-Updates.md
│   ├── API-Design/
│   │   ├── 01-Object-Model-Specification.md
│   │   ├── 02-Link-Model-Specification.md
│   │   └── 03-API-Endpoints.md
│   ├── Database-Design/
│   │   └── 01-Database-Schema.md
│   └── Development-Roadmap/
│       └── Phase-1-Roadmap.md
├── 0.1.1 - Core System/
│   └── app/
│       ├── main.py
│       ├── core/
│       │   ├── config.py
│       │   ├── database.py
│       │   ├── security.py
│       │   └── dependencies.py
│       ├── models/
│       │   ├── base_object.py
│       │   ├── user.py
│       │   ├── media.py
│       │   └── [15 more models]
│       └── routes/
│           ├── auth.py
│           ├── users.py
│           ├── media.py
│           └── [11 more routes]
├── 0.1.2 - API Layer/
├── 0.1.3 - Database Layer/
├── 0.1.4 - Integration Plugins/
├── 0.1.5 - Frontend Applications/
└── 0.1.6 - AI Core & Identity System/
    └── 6.0.0 - Vision & Philosophy/
        ├── 00-The-Singularity-Vision.md
        ├── 01-Addressing-Scheme-Proposal.md
        ├── 02-AI-Implementation-Thoughts.md
        ├── 03-Addressing-Decision-Final.md
        └── 04-The-Trust-Protocol.md
```

### 0.1.0 - Planning & Documentation

**Purpose:** Strategic planning, business documents, architecture specs

**Key Documents:**

**Start Here:**
- `README.md` - Overview of planning documentation
- `MASTER-INDEX.md` - Complete index of all strategic documents
- `IMPLEMENTATION-STATUS.md` - Current status across all areas
- `DEVELOPMENT-PRIORITIES.md` - Prioritized roadmap

**Strategic Planning (440 pages):**
- `FUNDING-STRATEGY-2026.md` - $100M fundraising plan
- `INVESTOR-PITCH-PLAYBOOK.md` - Tactical execution guide
- `PITCH-DECK-CONTENT.md` - Investor presentation content
- `FINANCIAL-MODEL.md` - 5-year financial projections
- `PRODUCT-ROADMAP-2026-2028.md` - 24-month product plan
- `GO-TO-MARKET-STRATEGY.md` - Customer acquisition strategy
- `AI-PARTNERSHIP-STRATEGY.md` - Partnership playbook
- `COMPETITIVE-ANALYSIS.md` - Market positioning

**Technical Planning:**
- `Architecture/` - System architecture specifications
- `API-Design/` - API and data model specifications
- `Database-Design/` - Database schema and design
- `Development-Roadmap/` - Development phases and milestones

**Status Reports:**
- `COMPLETE-STATUS-REPORT.md` - Comprehensive status (Feb 5)
- `API-COMPLETION-SUMMARY.md` - API development summary

### 0.1.1 - Core System

**Purpose:** Source code for the Hypernet platform

**Technology Stack:**
- Python 3.11+ with FastAPI
- PostgreSQL 15+ with SQLAlchemy
- JWT authentication
- RESTful APIs

**Key Components:**

**`app/main.py`**
- Main FastAPI application
- 115+ API endpoints registered
- Auto-generated OpenAPI documentation

**`app/core/`**
- `config.py` - Application settings
- `database.py` - SQLAlchemy setup
- `security.py` - JWT and password hashing
- `dependencies.py` - Authentication dependencies

**`app/models/`** (19 models)
- `base_object.py` - Base object model
- `user.py` - User model
- `media.py`, `album.py` - Media management
- `social_post.py`, `social_account.py` - Social media
- `note.py`, `task.py`, `calendar_event.py` - Productivity
- `email.py`, `contact.py` - Communication
- `bookmark.py`, `web_page.py` - Web content
- `document.py`, `transaction.py`, `location.py` - Life data
- `health_record.py`, `profile_attribute.py` - Personal data
- `device.py`, `notification.py`, `audit.py` - System data

**`app/routes/`** (18 route files, 115+ endpoints)
- `auth.py` - Registration and login
- `users.py` - User management
- `media.py`, `albums.py` - Media APIs
- `social_posts.py`, `social_accounts.py` - Social APIs
- `notes.py`, `tasks.py`, `calendar_events.py` - Productivity APIs
- `emails.py`, `contacts.py` - Communication APIs
- `bookmarks.py`, `web_pages.py` - Web APIs
- `documents.py`, `transactions.py`, `locations.py` - Life APIs
- `health_records.py`, `profile_attributes.py` - Personal APIs
- `devices.py`, `notifications.py`, `audit.py` - System APIs

### 0.1.6 - AI Core & Identity System

**Purpose:** Vision and philosophy documents for AI integration

**Key Documents:**
- `00-The-Singularity-Vision.md` - Vision for AI-human collaboration
- `01-Addressing-Scheme-Proposal.md` - Addressing proposal for AI
- `02-AI-Implementation-Thoughts.md` - Implementation considerations
- `03-Addressing-Decision-Final.md` - Final addressing decision
- `04-The-Trust-Protocol.md` - Trust and identity framework

### Use Cases

**For Developers:**
- Find source code in `0.1.1 - Core System/`
- Understand architecture in `0.1.0 - Planning & Documentation/Architecture/`
- Reference API specs in `0.1.0 - Planning & Documentation/API-Design/`

**For Product:**
- Review product roadmap in `PRODUCT-ROADMAP-2026-2028.md`
- Understand features in API documentation

**For Business:**
- Review strategy documents in `0.1.0 - Planning & Documentation/`
- Prepare for fundraising with investor materials

**For New Team Members:**
1. Start with `MASTER-INDEX.md`
2. Read `COMPLETE-STATUS-REPORT.md`
3. Review relevant strategy docs
4. Explore source code

---

## Category 1: People

**Location:** `1 - People/`

This directory contains information about **individual persons** - team members, advisors, investors, partners, users.

### Purpose

- Team member profiles and information
- Contact information
- Contribution tracking
- Personal metadata

### Structure (Future)

```
1 - People/
├── 1.0 - Founders/
│   └── 1.0.1 - Matt Schaeffer/
├── 1.1 - Team/
│   ├── 1.1.1 - Engineering/
│   ├── 1.1.2 - Product/
│   └── 1.1.3 - Business/
├── 1.2 - Advisors/
├── 1.3 - Investors/
└── 1.4 - Partners/
```

**Note:** Currently minimal content. Will expand as team grows.

---

## Category 2: Aliases

**Location:** `2 - Aliases/`

This directory contains **alternate names, usernames, and handles** for people and entities.

### Purpose

- Map usernames to real identities
- Track online identities across platforms
- Maintain privacy-preserving references

### Structure (Future)

```
2 - Aliases/
├── 2.0 - Usernames/
├── 2.1 - Email Addresses/
├── 2.2 - Social Media Handles/
└── 2.3 - Nicknames/
```

**Note:** Currently minimal content. Reserved for future use.

---

## Category 3: Businesses

**Location:** `3 - Businesses/`

This directory contains information about **commercial entities** - primarily the Hypernet company itself.

### Structure

```
3 - Businesses/
└── 3.1 - Hypernet/
    ├── 3.1.2 Task Management System/
    │   ├── 3.1.2.1 Active Tasks - status Open/
    │   │   ├── 3.1.2.1.004 Build Unity Website/
    │   │   └── 3.1.2.1.005 Create Kickstarter Campaign/
    │   └── 3.1.2.2 In progress Tasks/
    │       ├── 3.1.2.2.1 - Hypernet Website/
    │       └── 3.1.2.2.2 - VR Headset Acquisition Strategy/
    └── 3.1.3 Human Resources/
        └── 3.1.3.4 Contribution Tracking (for profit sharing)/
            ├── ContributionTrackingTemplate.md
            ├── 3.1.3.4.0/
            │   └── Overall Tracking.md
            ├── 3.1.3.4.1 - Matt Schaeffer/
            │   ├── 3.1.3.4.1.2. Jan 2026.md
            │   └── 3.1.3.4.1.3. Feb 2026 1.md
            ├── 3.1.3.4.2 - Hillsong/
            ├── 3.1.3.4.3 - Valeria Campeche/
            ├── 3.1.3.4.4 - Jonathan Garibay/
            └── 3.1.3.4.5 - Mike Wood/
```

### 3.1.2 - Task Management System

**Purpose:** Track tasks, projects, and work items

**Structure:**
- `3.1.2.1 Active Tasks - status Open/` - Tasks not yet started
- `3.1.2.2 In progress Tasks/` - Tasks currently being worked on
- `3.1.2.3 Completed Tasks/` (future) - Finished tasks

**Current Tasks:**

**Active:**
- 3.1.2.1.004 - Build Unity Website
- 3.1.2.1.005 - Create Kickstarter Campaign

**In Progress:**
- 3.1.2.2.1 - Hypernet Website
- 3.1.2.2.2 - VR Headset Acquisition Strategy

### 3.1.3 - Human Resources

**Purpose:** Team management, contribution tracking, equity

**Contribution Tracking:**
- Tracks work contributions for profit sharing
- Individual contributor folders
- Monthly tracking documents
- Template for new contributors

**Contributors:**
- Matt Schaeffer (Founder)
- Hillsong (Contributor)
- Valeria Campeche (Contributor)
- Jonathan Garibay (Contributor)
- Mike Wood (Contributor)

### Use Cases

**For Team:**
- Track tasks and projects
- Record contributions
- Manage work items

**For Operations:**
- Contribution tracking for equity/profit sharing
- Task status monitoring
- Project coordination

---

## Category 4: Knowledge

**Location:** `4 - Knowledge/`

This directory contains **information, research, education, and documentation** that isn't code or business operations.

### Purpose

- Research and analysis
- Educational materials
- Reference documentation
- Knowledge base articles

### Structure (Future)

```
4 - Knowledge/
├── 4.0 - Research/
├── 4.1 - Education/
├── 4.2 - Documentation/
└── 4.3 - Reference/
```

**Note:** Currently minimal content. Will expand with research and documentation.

---

## Category 5: Objects

**Location:** `5 - Objects/`

This directory contains information about **physical items, devices, and products**.

### Purpose

- Inventory management
- Device tracking
- Equipment records
- Product catalogs

### Structure (Future)

```
5 - Objects/
├── 5.0 - Devices/
│   ├── 5.0.1 - Computers/
│   ├── 5.0.2 - Servers/
│   └── 5.0.3 - Network Equipment/
├── 5.1 - Office Equipment/
└── 5.2 - Products/
```

**Note:** Currently minimal content. Will expand as we acquire equipment and products.

---

## How to Find Things

### By Purpose

**Looking for strategic planning?**
→ `0.1 - Hypernet Core/0.1.0 - Planning & Documentation/`

**Looking for source code?**
→ `0.1 - Hypernet Core/0.1.1 - Core System/app/`

**Looking for object definitions?**
→ `0.0 - Object Type Registry/`

**Looking for tasks?**
→ `3 - Businesses/3.1 - Hypernet/3.1.2 Task Management System/`

**Looking for contribution tracking?**
→ `3 - Businesses/3.1 - Hypernet/3.1.3 Human Resources/3.1.3.4 Contribution Tracking/`

### By Document Name

**Key Documents Quick Reference:**

| Document | Path |
|----------|------|
| Master Index | `0.1/0.1.0/MASTER-INDEX.md` |
| Implementation Status | `0.1/0.1.0/IMPLEMENTATION-STATUS.md` |
| Development Priorities | `0.1/0.1.0/DEVELOPMENT-PRIORITIES.md` |
| Funding Strategy | `0.1/0.1.0/FUNDING-STRATEGY-2026.md` |
| Product Roadmap | `0.1/0.1.0/PRODUCT-ROADMAP-2026-2028.md` |
| Complete Status Report | `0.1/0.1.0/COMPLETE-STATUS-REPORT.md` |
| Addressing System | `0/0.0 Metadata/0.0.0 Library Addressing System.md` |

### By Type

**Strategic Documents:**
→ `0.1 - Hypernet Core/0.1.0 - Planning & Documentation/` (all .md files in root)

**Architecture Documents:**
→ `0.1 - Hypernet Core/0.1.0 - Planning & Documentation/Architecture/`

**API Documentation:**
→ `0.1 - Hypernet Core/0.1.0 - Planning & Documentation/API-Design/`

**Source Code:**
→ `0.1 - Hypernet Core/0.1.1 - Core System/app/`

**Object Specs:**
→ `0.0 - Object Type Registry/` (organized by type category)

### Search Tips

1. **Use file search:** Most IDEs and editors have file search (Ctrl+P or Cmd+P)
2. **Use content search:** Search file contents (Ctrl+Shift+F or Cmd+Shift+F)
3. **Use Git grep:** `git grep "search term"` searches all tracked files
4. **Use folder names:** Folder names are descriptive and hierarchical
5. **Check README files:** Most major directories have README.md files

---

## How to Add New Content

### General Rules

1. **Find the right category** - Use the numbering system to find where it belongs
2. **Follow the numbering** - Use the next available number in the sequence
3. **Use descriptive names** - Make it clear what the content is
4. **Add a README** - If creating a new directory, add a README.md
5. **Update indexes** - Update MASTER-INDEX.md if adding major content

### Adding a New Strategic Document

**Location:** `0.1 - Hypernet Core/0.1.0 - Planning & Documentation/`

**Steps:**
1. Create the .md file in the planning directory
2. Follow naming convention: `DESCRIPTIVE-NAME.md` (all caps, hyphens)
3. Add to `MASTER-INDEX.md` in appropriate section
4. Include document metadata (version, date, owner)
5. Commit to Git with descriptive message

**Example:**
```bash
# Create file
touch "0.1 - Hypernet Core/0.1.0 - Planning & Documentation/SECURITY-STRATEGY.md"

# Edit file
vim "0.1 - Hypernet Core/0.1.0 - Planning & Documentation/SECURITY-STRATEGY.md"

# Add to Git
git add "0.1 - Hypernet Core/0.1.0 - Planning & Documentation/SECURITY-STRATEGY.md"
git commit -m "Add security strategy document"
```

### Adding a New Object Type

**Location:** `0.0 - Object Type Registry/`

**Steps:**
1. Determine the type category (Media, Social, Communication, etc.)
2. Navigate to appropriate category folder
3. Create new .md file with object name (e.g., `Podcast.md`)
4. Follow the object type template (see existing types)
5. Update the category README if necessary
6. Commit to Git

**Template Structure:**
```markdown
# ObjectName

## Overview
Brief description of what this object represents.

## Fields

### Required Fields
- field1 (type): Description
- field2 (type): Description

### Optional Fields
- field3 (type): Description

## Relationships
- Links to ObjectTypeA
- Links to ObjectTypeB

## Examples
[Example JSON or usage]

## Validation Rules
- Rules for valid data

## Version History
- v1.0 (date): Initial definition
```

### Adding Source Code

**Location:** `0.1 - Hypernet Core/0.1.1 - Core System/app/`

**Steps:**
1. Determine what you're adding (model, route, utility)
2. Navigate to appropriate directory (`models/`, `routes/`, `core/`)
3. Create new .py file with descriptive name
4. Follow Python best practices (type hints, docstrings)
5. Write tests in `tests/` directory
6. Update main.py if adding a route
7. Commit to Git with tests

**Example:**
```bash
# Add new model
touch "0.1 - Hypernet Core/0.1.1 - Core System/app/models/podcast.py"

# Add corresponding route
touch "0.1 - Hypernet Core/0.1.1 - Core System/app/routes/podcasts.py"

# Add tests
touch "0.1 - Hypernet Core/0.1.1 - Core System/tests/test_podcasts.py"

# Commit
git add app/models/podcast.py app/routes/podcasts.py tests/test_podcasts.py
git commit -m "Add Podcast model and API endpoints"
```

### Adding a Task

**Location:** `3 - Businesses/3.1 - Hypernet/3.1.2 Task Management System/`

**Steps:**
1. Determine task status (Active, In Progress, Completed)
2. Navigate to appropriate status folder
3. Create new folder with task number and name
4. Add task description file (usually .md)
5. Update task as status changes
6. Commit to Git

**Example:**
```bash
# Create task folder
mkdir "3 - Businesses/3.1 - Hypernet/3.1.2 Task Management System/3.1.2.1 Active Tasks - status Open/3.1.2.1.006 Build Mobile App"

# Create task description
touch "3 - Businesses/3.1 - Hypernet/3.1.2 Task Management System/3.1.2.1 Active Tasks - status Open/3.1.2.1.006 Build Mobile App/3.1.2.1.006.0.md"

# Commit
git add "3 - Businesses/3.1 - Hypernet/3.1.2 Task Management System/3.1.2.1 Active Tasks - status Open/3.1.2.1.006 Build Mobile App/"
git commit -m "Add task: Build Mobile App"
```

### Adding Contribution Tracking

**Location:** `3 - Businesses/3.1 - Hypernet/3.1.3 Human Resources/3.1.3.4 Contribution Tracking/`

**Steps:**
1. Create folder for new contributor (if doesn't exist)
2. Use `ContributionTrackingTemplate.md` as template
3. Create monthly tracking file (format: `3.1.3.4.X.2. MonthName Year.md`)
4. Update `Overall Tracking.md`
5. Commit to Git

**Example:**
```bash
# Create contributor folder
mkdir "3 - Businesses/3.1 - Hypernet/3.1.3 Human Resources/3.1.3.4 Contribution Tracking/3.1.3.4.6 - Jane Doe"

# Create monthly tracking
cp "ContributionTrackingTemplate.md" "3.1.3.4.6 - Jane Doe/3.1.3.4.6.2. Feb 2026.md"

# Edit tracking file
vim "3.1.3.4.6 - Jane Doe/3.1.3.4.6.2. Feb 2026.md"

# Commit
git add "3.1.3.4.6 - Jane Doe/"
git commit -m "Add contribution tracking for Jane Doe - Feb 2026"
```

---

## Best Practices

### File Naming

**DO:**
- Use descriptive names (`FUNDING-STRATEGY-2026.md`)
- Use hyphens for spaces in all-caps files (`GO-TO-MARKET-STRATEGY.md`)
- Use lowercase with underscores for code (`user_profile.py`)
- Include version or date if relevant (`Jan 2026.md`)
- Be consistent within a category

**DON'T:**
- Use special characters except hyphens and underscores
- Use very long names (keep under 50 characters)
- Use ambiguous abbreviations
- Use spaces in code filenames

### Folder Naming

**DO:**
- Follow the numbering system (`3.1.2.1.001`)
- Add descriptive suffix (`3.1.2.1.001 - Task Name`)
- Use the next available number in sequence
- Be consistent with existing structure

**DON'T:**
- Skip numbers (use sequential numbering)
- Rename existing folders (breaks references)
- Create deep nesting without purpose (keep to 5-7 levels max)

### Documentation

**DO:**
- Add README.md to new major directories
- Include metadata in documents (version, date, owner)
- Update MASTER-INDEX.md for strategic documents
- Write clear, actionable content
- Use headings and structure
- Include examples

**DON'T:**
- Create orphan documents (unlinked)
- Forget to update indexes
- Write without structure
- Skip version information

### Version Control

**DO:**
- Commit early and often
- Write descriptive commit messages
- Use branches for major changes
- Tag releases (`git tag v1.0.0`)
- Push regularly to remote

**DON'T:**
- Commit large binary files (use Git LFS if needed)
- Commit sensitive information (API keys, passwords)
- Make massive commits (break into logical chunks)
- Skip commit messages or use vague ones ("update")

### Organization

**DO:**
- Keep related files together
- Follow the hierarchy
- Use the numbering system
- Create clear boundaries between categories
- Document your organization decisions

**DON'T:**
- Duplicate content across folders
- Create ad-hoc organization schemes
- Mix personal and project files
- Create files in root without good reason

---

## Common Tasks

### Task 1: Find the Latest Status Report

**Path:**
```
0.1 - Hypernet Core/
└── 0.1.0 - Planning & Documentation/
    ├── IMPLEMENTATION-STATUS.md (this file)
    ├── COMPLETE-STATUS-REPORT.md (Feb 5 comprehensive report)
    └── API-COMPLETION-SUMMARY.md (API development summary)
```

**Quick:** Check `IMPLEMENTATION-STATUS.md` for overall status

### Task 2: Understand the Product Roadmap

**Path:**
```
0.1 - Hypernet Core/
└── 0.1.0 - Planning & Documentation/
    └── PRODUCT-ROADMAP-2026-2028.md
```

**Read Time:** 2 hours (55 pages)
**Key Sections:** Phase breakdown, integration roadmap, metrics

### Task 3: Prepare for Investor Meeting

**Path:**
```
0.1 - Hypernet Core/
└── 0.1.0 - Planning & Documentation/
    ├── PITCH-DECK-CONTENT.md (slide content)
    ├── FUNDING-EXECUTIVE-SUMMARY.md (quick overview)
    ├── FINANCIAL-MODEL.md (projections)
    └── COMPETITIVE-ANALYSIS.md (market positioning)
```

**Workflow:**
1. Review FUNDING-EXECUTIVE-SUMMARY.md (15 min)
2. Review PITCH-DECK-CONTENT.md (30 min)
3. Practice pitch (1 hour)
4. Prepare for Q&A using FINANCIAL-MODEL.md and COMPETITIVE-ANALYSIS.md

### Task 4: Onboard a New Developer

**Path:**
```
0.1 - Hypernet Core/
├── 0.1.0 - Planning & Documentation/
│   ├── MASTER-INDEX.md (start here)
│   ├── Architecture/
│   │   └── 00-System-Architecture-Overview.md
│   └── API-Design/
│       └── 01-Object-Model-Specification.md
└── 0.1.1 - Core System/
    └── app/ (source code)
```

**Workflow:**
1. Read MASTER-INDEX.md (30 min)
2. Read System Architecture Overview (1 hour)
3. Review API Design docs (1 hour)
4. Explore source code in `app/` (2-4 hours)
5. Set up development environment
6. Run tests
7. Make first commit

### Task 5: Look Up an Object Type Definition

**Path:**
```
0.0 - Object Type Registry/
├── README.md (overview)
└── [Category]/
    └── [ObjectName].md
```

**Example - Find Photo definition:**
```
0.0 - Object Type Registry/
└── 0.0.2 - Media Types/
    └── Photo.md
```

**Workflow:**
1. Identify category (Media, Social, Communication, etc.)
2. Navigate to category folder
3. Open object .md file
4. Review fields and relationships

### Task 6: Track Work Contributions

**Path:**
```
3 - Businesses/
└── 3.1 - Hypernet/
    └── 3.1.3 Human Resources/
        └── 3.1.3.4 Contribution Tracking/
            ├── ContributionTrackingTemplate.md
            └── [Your Name]/
                └── [Month Year].md
```

**Workflow:**
1. Copy `ContributionTrackingTemplate.md`
2. Create monthly file in your folder
3. Document contributions
4. Submit for review
5. Update `Overall Tracking.md`

### Task 7: Add a New API Endpoint

**Path:**
```
0.1 - Hypernet Core/
└── 0.1.1 - Core System/
    ├── app/
    │   ├── models/
    │   │   └── [new_model].py (if needed)
    │   ├── routes/
    │   │   └── [new_route].py (add endpoint here)
    │   └── main.py (register route)
    └── tests/
        └── test_[new_route].py (add tests)
```

**Workflow:**
1. Create or update model in `models/`
2. Create or update route in `routes/`
3. Register route in `main.py`
4. Write tests in `tests/`
5. Run tests: `pytest`
6. Commit all changes
7. Update API documentation if needed

### Task 8: Review Financial Projections

**Path:**
```
0.1 - Hypernet Core/
└── 0.1.0 - Planning & Documentation/
    └── FINANCIAL-MODEL.md
```

**Key Sections:**
- Revenue model (B2B, B2C, data licensing)
- 5-year projections ($2M → $200M)
- Unit economics (LTV:CAC)
- Profitability path
- Sensitivity analysis

---

## Quick Reference Card

### Top 10 Most Important Locations

1. **Strategic Plans:** `0.1/0.1.0/` (all strategy .md files)
2. **Source Code:** `0.1/0.1.1/app/`
3. **Object Definitions:** `0.0/`
4. **Architecture Docs:** `0.1/0.1.0/Architecture/`
5. **API Specs:** `0.1/0.1.0/API-Design/`
6. **Tasks:** `3/3.1/3.1.2/`
7. **Contributions:** `3/3.1/3.1.3/3.1.3.4/`
8. **Status Reports:** `0.1/0.1.0/` (STATUS files)
9. **Addressing System:** `0/0.0 Metadata/`
10. **AI Vision:** `0.1/0.1.6/6.0.0/`

### Top 10 Most Important Documents

1. `MASTER-INDEX.md` - Navigation guide
2. `IMPLEMENTATION-STATUS.md` - Current status
3. `DEVELOPMENT-PRIORITIES.md` - What to do next
4. `PRODUCT-ROADMAP-2026-2028.md` - Product plan
5. `FUNDING-STRATEGY-2026.md` - Fundraising plan
6. `COMPLETE-STATUS-REPORT.md` - Comprehensive status
7. `00-System-Architecture-Overview.md` - Technical architecture
8. `0.0.0 Library Addressing System.md` - Numbering system
9. `FINANCIAL-MODEL.md` - Business projections
10. `GO-TO-MARKET-STRATEGY.md` - Customer acquisition

### Key Contacts (Future)

| Role | Name | Location |
|------|------|----------|
| CEO | Matt Schaeffer | `1 - People/1.0 - Founders/1.0.1 - Matt Schaeffer/` |
| CTO | (To be hired) | TBD |
| CFO | (To be hired) | TBD |

---

## Changelog

### Version 1.0 (February 9, 2026)
- Initial version created
- Comprehensive structure guide
- Navigation instructions
- Best practices documented
- Common tasks included

### Future Updates
- Will update as structure evolves
- Will add new categories as needed
- Will refine based on team feedback

---

## Feedback and Improvements

This structure is designed to be **scalable and adaptable**. If you find:
- Confusing organization
- Missing documentation
- Better ways to organize
- Navigation difficulties

Please:
1. Document the issue
2. Propose a solution
3. Discuss with team
4. Update this guide

**The goal is a structure that serves the team, not restricts it.**

---

## Summary

The Hypernet folder structure is a **hierarchical, numbered system** that organizes all project information from system metadata to source code to business operations.

**Key Principles:**
- Decimal numbering for unique addressing
- Hierarchical organization for clarity
- Descriptive naming for usability
- Git version control for history
- README files for navigation

**Primary Categories:**
- `0/` and `0.0/` - System metadata and object registry
- `0.1/` - Core system (code, planning, documentation)
- `1/` - People
- `2/` - Aliases
- `3/` - Businesses (tasks, HR)
- `4/` - Knowledge
- `5/` - Objects

**Getting Started:**
1. Read this guide (HYPERNET-STRUCTURE-GUIDE.md)
2. Read MASTER-INDEX.md for strategic documents
3. Explore relevant directories for your role
4. Follow best practices when adding content

**Most Important:** The structure serves the project. Use it, improve it, adapt it as needed.

---

**Document:** HYPERNET-STRUCTURE-GUIDE.md
**Location:** Root of Hypernet Structure
**Version:** 1.0
**Date:** February 9, 2026
**Maintainer:** Project team
**Next Review:** Monthly during active development

---

**Welcome to Hypernet. Let's build the infrastructure for the AI revolution.**
