---
ha: "1.1.0"
object_type: "metadata"
creator: "system"
created: "2026-03-19"
status: "active"
visibility: "public"
flags: ["metadata"]
---

# 1.1.0 - Account Metadata

**Purpose:** Metadata about Person Node 1.1 (Matt Schaeffer) and instructions for how this node and its children are organized.

---

## Node Overview

- **Address:** 1.1
- **Name:** Matt Schaeffer
- **Role:** Founder & CEO, Hypernet
- **Status:** Active

## How This Account Is Organized

Person nodes follow the standard structure defined in 1.0 (People Definitions). Data children start at .1:

| Address | Contents | Type |
|---------|----------|------|
| 1.1.0 | This metadata document | Metadata |
| 1.1.1 | Projects | Data |
| 1.1.2 | Documents | Data |
| 1.1.3 | Communications | Data |
| 1.1.4 | Relationships | Data |
| 1.1.5 | Tasks & Workflows | Data |
| 1.1.6 | Personal Data | Data |
| 1.1.7 | Contributions | Data |
| 1.1.8 | Media | Data |
| 1.1.9 | Notes & Knowledge | Data |
| 1.1.10 | AI Assistants (Embassy) | Data |
| 1.1.11 | Profile & Identity | Data |
| 1.1.12 | Secrets & Credentials | Private locker/mandala credential data |
| 1.1.13 | Public Profile & Lockers | Public account surface and locker index |

## Sub-Node Metadata Rule

Each sub-node (1.1.1, 1.1.2, etc.) reserves its own .0 for metadata. See the .0 metadata audit notes below for sub-node compliance.

## Privacy

Person nodes contain sensitive personal information. Access levels per the People Definitions (1.0):
1. Public - Name, role, public biography
2. Team - Hypernet team members only
3. Private - Person + authorized individuals only
4. System - System access only (encrypted)

Secrets, credentials, and recovery material belong under `1.1.12` and must be encrypted or referenced through lockers. Public account data belongs under `1.1.13` and may expose locker/mandala metadata, not private contents.

## Notes

- Profile & Identity data was originally at 1.1.0 but was moved to 1.1.11 on 2026-03-19 to comply with the .0 metadata reservation rule.
- This is the reference implementation of the person folder structure.

---

*Metadata node created 2026-03-19 during .0 audit.*
