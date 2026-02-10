# 1.0 - People Definitions

## Purpose

This folder contains the foundational definitions, templates, and governance for the People node system in Hypernet.

## Contents

### PERSON-FOLDER-TEMPLATE.md
Standard folder structure template that should be applied to all person nodes (1.1, 1.2, 1.3, etc.).

### Person Numbering System

**1.1 - 1.10:** Core Team & Family
- 1.1 - Matt Schaeffer (Founder & CEO)
- 1.2 - Sarah Schaeffer
- 1.3 - John Schaeffer
- 1.4 - Bridget Schaeffer
- 1.5 - Mark Schaeffer
- 1.6 - Richard Schaeffer
- 1.7 - Ollie Schaeffer
- 1.8-1.10 - Reserved for additional core family

**1.11 - 1.30:** Early Contributors & Co-founders
- 1.21 - Pedro Hillsong
- 1.22 - Valeria
- 1.23 - Jonathan G
- 1.24 - Mike Wood
- 1.11-1.20 - Reserved for other early contributors
- 1.25-1.30 - Reserved for early advisors

**1.31 - 1.100:** Founding Team Members
- Initial hires (CTO, VP Engineering, VP Partnerships, etc.)
- First 50-70 employees
- Key advisors and board members

**1.101 - 1.1000:** Extended Team
- Employees hired after founding period
- Regular contractors
- Active community contributors
- Strategic partners (individuals)

**1.1001+:** General Community
- All other individuals in the ecosystem
- Users with Hypernet accounts
- Contributors
- Community members
- Partners

## Person Node Structure

Each person node follows the template defined in PERSON-FOLDER-TEMPLATE.md:

```
1.X - [Person Name]/
├── 1.X.0 - Profile & Identity
├── 1.X.1 - Projects
├── 1.X.2 - Documents
├── 1.X.3 - Communications
├── 1.X.4 - Relationships
├── 1.X.5 - Tasks & Workflows
├── 1.X.6 - Personal Data (Hypernet)
├── 1.X.7 - Contributions
├── 1.X.8 - Media
└── 1.X.9 - Notes & Knowledge
```

## Relationship to Hypernet Platform

### User Account Linkage
- Person nodes with Hypernet accounts link to user_id in database
- Personal data accessible via API in 1.X.6.0 - Hypernet Data Store
- Privacy controlled via 1.X.6.1 - Privacy Settings

### Data Storage
- Person metadata stored in this file system
- Personal Hypernet data stored in PostgreSQL database
- Media files stored in cloud storage (S3/equivalent)
- Links maintain connection between systems

## Privacy & Access Control

### Public Information (1.X.0)
- Name, role, public biography
- Public projects and contributions
- Contact information (as permitted)

### Private Information
- Personal documents (1.X.2)
- Communications (1.X.3)
- Personal data (1.X.6)
- Requires authentication and authorization

### Access Levels
1. **Public** - Anyone can view
2. **Team** - Hypernet team members only
3. **Private** - Person + authorized individuals only
4. **System** - System access only (encrypted)

## Implementation Status

- [x] Template created (PERSON-FOLDER-TEMPLATE.md)
- [ ] Reference implementation (1.1 - Matt Schaeffer)
- [ ] Core team structures created
- [ ] Early contributor structures created
- [ ] API integration for personal data
- [ ] Privacy settings implementation
- [ ] Access control system

## Next Steps

1. Build out 1.1 - Matt Schaeffer as reference implementation
2. Clone structure for 1.2-1.10 (core team)
3. Create structures for 1.21-1.24 (early contributors)
4. Add README files to all folders
5. Populate with available information
6. Implement API integration for 1.X.6 folders
7. Set up privacy and access controls

---

**Status:** In Development
**Owner:** Hypernet Core Team
**Last Updated:** February 5, 2026
