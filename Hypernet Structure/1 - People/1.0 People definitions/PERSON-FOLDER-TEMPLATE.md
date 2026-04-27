---
ha: "1.0.doc.person-folder-template"
object_type: "document"
creator: "1.1"
created: "2026-02-10"
status: "active"
visibility: "public"
flags: []
---

# Person Folder Structure Template

This document defines the standard folder structure for all person nodes in the Hypernet system.

## Purpose

Each person in the Hypernet ecosystem has a standardized folder structure to store:
- Personal information and metadata
- Projects and contributions
- Documents and files
- Communications
- Relationships and connections
- Tasks and workflows
- Personal data (from Hypernet platform usage)

## Standard Folder Structure

```
1.X - [Person Name]/
├── 1.X.0 - Account Metadata/        ** RESERVED for metadata (per .0 rule) **
│   └── README.md (How this person node is organized)
├── 1.X.1 - Projects/
│   ├── 1.X.1.0 - Section Metadata/   ** RESERVED **
│   ├── 1.X.1.1 - Completed Projects/
│   ├── 1.X.1.2 - Archived Projects/
│   └── 1.X.1.3 - Active Projects/
├── 1.X.2 - Documents/
│   ├── 1.X.2.0 - Section Metadata/   ** RESERVED **
│   ├── 1.X.2.1 - Business Documents/
│   ├── 1.X.2.2 - Legal Documents/
│   ├── 1.X.2.3 - Reference Materials/
│   └── 1.X.2.4 - Personal Documents/
├── 1.X.3 - Communications/
│   ├── 1.X.3.0 - Section Metadata/   ** RESERVED **
│   ├── 1.X.3.1 - Meeting Notes/
│   ├── 1.X.3.2 - Correspondence/
│   └── 1.X.3.3 - Email Archives/
├── 1.X.4 - Relationships/
│   ├── 1.X.4.0 - Section Metadata/   ** RESERVED **
│   ├── 1.X.4.1 - Personal Network/
│   ├── 1.X.4.2 - Organizational Affiliations/
│   └── 1.X.4.3 - Professional Network/
├── 1.X.5 - Tasks & Workflows/
│   ├── 1.X.5.0 - Section Metadata/   ** RESERVED **
│   ├── 1.X.5.1 - Completed Tasks/
│   ├── 1.X.5.2 - Recurring Workflows/
│   └── 1.X.5.3 - Active Tasks/
├── 1.X.6 - Personal Data/
│   ├── 1.X.6.0 - Section Metadata/   ** RESERVED **
│   ├── 1.X.6.1 - Privacy Settings/
│   ├── 1.X.6.2 - Data Permissions/
│   └── 1.X.6.3 - Hypernet Data Store/
├── 1.X.7 - Contributions/
│   ├── 1.X.7.0 - Section Metadata/   ** RESERVED **
│   ├── 1.X.7.1 - Documentation/
│   ├── 1.X.7.2 - Design Work/
│   ├── 1.X.7.3 - Other Contributions/
│   └── 1.X.7.4 - Code Contributions/
├── 1.X.8 - Media/
│   ├── 1.X.8.0 - Section Metadata/   ** RESERVED **
│   ├── 1.X.8.1 - Videos/
│   ├── 1.X.8.2 - Audio/
│   └── 1.X.8.3 - Photos/
├── 1.X.9 - Notes & Knowledge/
│   ├── 1.X.9.0 - Section Metadata/   ** RESERVED **
│   ├── 1.X.9.1 - Research/
│   ├── 1.X.9.2 - Learning Materials/
│   └── 1.X.9.3 - Personal Notes/
├── 1.X.10 - Profile & Identity/      (data: bio, contact, skills)
    ├── README.md (Basic info, contact, role)
    ├── BIOGRAPHY.md
    ├── SKILLS.md
    ├── RESUME.md (if applicable)
    └── CONTACT-INFO.md
├── 1.X.11 - Secrets & Credentials/   (private: lockers only, no committed secret values)
└── 1.X.12 - Public Profile & Lockers/ (public side: profile, public keys, locker/mandala index)
```

**IMPORTANT: The .0 Rule**

Every `.0` address is ALWAYS reserved for metadata about the parent node. Data starts at `.1`. This applies recursively at every level of the hierarchy. See 0.0.4 (Node Metadata Framework) for the full specification.

## Folder Descriptions

### 1.X.0 - Account Metadata
**RESERVED** for metadata about the person node. Contains organization instructions, not personal data. Per the .0 metadata rule (0.0.4).

### 1.X.1 - Projects
All projects associated with this person, organized by status (active, completed, archived).

### 1.X.2 - Documents
Personal and business documents, contracts, agreements, reference materials.

### 1.X.3 - Communications
Email archives, meeting notes, correspondence with others.

### 1.X.4 - Relationships
Network connections, both professional and personal, organizational memberships.

### 1.X.5 - Tasks & Workflows
Task management, workflows, processes this person is responsible for.

### 1.X.6 - Personal Data
Data stored in the Hypernet platform for this person (media, contacts, transactions, etc.).

### 1.X.7 - Contributions
Contributions to Hypernet or other projects (code, docs, design, etc.).

### 1.X.8 - Media
Photos, videos, audio files related to this person.

### 1.X.9 - Notes & Knowledge
Personal notes, research, learning materials, knowledge base.

### 1.X.10 - Profile & Identity
Public and private identity material, biography, contact policy, skills, resumes, and profile claims.

### 1.X.11 - Secrets & Credentials
Passwords, API tokens, recovery codes, cryptographic keys, service accounts, and IoT credentials. Actual secret values must live in encrypted lockers or gitignored private staging, never in committed plaintext.

### 1.X.12 - Public Profile & Lockers
The account's public side: public profile, public keys, public claims, contact routes, public locker index, and mandala grant metadata. Public locker entries may reveal safe metadata, not private contents.

Existing accounts may have extension addresses shifted when a slot was already assigned before this standard was updated. Matt's reference account uses `1.1.12` for secrets and `1.1.13` for the public locker surface because `1.1.11` already existed as Profile & Identity.

## Usage Guidelines

1. **Create folders as needed** - Not all people will need all folders
2. **Use README.md** - Each folder should have a README explaining its contents
3. **Maintain privacy** - Respect privacy settings and permissions
4. **Link to Hypernet** - Person nodes link to their Hypernet user account
5. **Keep updated** - Profile information should stay current

## Person Categories

### Core Team (1.1-1.10)
Matt Schaeffer and immediate family/co-founders

### Early Contributors (1.11-1.30)
First contributors to Hypernet project

### Team Members (1.31-1.100)
Employees and regular contributors

### Community (1.101-1.1000)
Community members, users, partners

### General (1.1001+)
All other individuals in the system

## Relationship to Hypernet Platform

When a person has a Hypernet user account:
- 1.X.6.3 - Hypernet Data Store links to their user_id in the system
- Their personal data (media, contacts, tasks, etc.) is accessible via API
- Privacy settings in 1.X.6.1 control who can access what data
- Data permissions in 1.X.6.2 define what integrations can access

## Next Steps for Implementation

1. Create this structure for 1.1 - Matt Schaeffer (reference implementation)
2. Clone structure for other core team members
3. Add basic README files to each folder
4. Populate with available information
5. Link to Hypernet user accounts where applicable

---

**Template Version:** 1.0
**Created:** February 5, 2026
**Last Updated:** February 5, 2026
**Maintained By:** Hypernet Core Team
