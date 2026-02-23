---
ha: "2.0.messages.coordination.audit-scribe-needs-human"
object_type: "document"
creator: "2.1"
created: "2026-02-22"
status: "active"
visibility: "public"
flags: ["audit", "needs-human-input"]
---

# Audit Scribe — Items Needing Human Input

**Prepared by:** The Scribe (Node 3 of 4, audit swarm)
**For:** Matt Schaeffer (1.1) to review
**Date:** 2026-02-22

This document lists everything the Scribe could NOT fill in during the property completeness audit.
Organized by category and priority for efficient review.

---

## Priority 1: Person Contact Information

These fields require private/personal knowledge that cannot be inferred from the repository.

### 1.1 Matt Schaeffer
| Field | Current Value | Notes |
|-------|--------------|-------|
| email | [NEEDS HUMAN INPUT] | Primary contact email |
| phone | [NEEDS HUMAN INPUT] | Primary phone number |
| date_of_birth | [NEEDS HUMAN INPUT] | For person schema completeness |
| location | [NEEDS HUMAN INPUT] | City/state for public profile |
| joined_date | Set to 2026-02-09 | Inferred from earliest git activity — confirm? |

### 1.2 Sarah Schaeffer
| Field | Current Value | Notes |
|-------|--------------|-------|
| full_name | "Sarah Schaeffer" | Confirm full legal name |
| relationship_to_matt | "family" | Specific relationship (spouse? sibling?) |
| email | [NEEDS HUMAN INPUT] | |
| phone | [NEEDS HUMAN INPUT] | |
| active_in_hypernet | [NEEDS HUMAN INPUT] | Is she an active participant or just registered? |

### 1.21 Pedro Hillsong
| Field | Current Value | Notes |
|-------|--------------|-------|
| full_name | "Pedro Hillsong" | Confirm |
| role_description | [NEEDS HUMAN INPUT] | What is Pedro's specific role/contribution area? |
| email | [NEEDS HUMAN INPUT] | |
| joined_date | Set to 2026-02-10 | Confirm |

### 1.22 Valeria
| Field | Current Value | Notes |
|-------|--------------|-------|
| full_name | [NEEDS HUMAN INPUT] | Last name unknown — "Valeria Campeche" per contribution tracking? |
| role_description | [NEEDS HUMAN INPUT] | |
| email | [NEEDS HUMAN INPUT] | |

### 1.23 Jonathan G
| Field | Current Value | Notes |
|-------|--------------|-------|
| full_name | [NEEDS HUMAN INPUT] | Last name — "Jonathan Garibay" per contribution tracking? |
| role_description | [NEEDS HUMAN INPUT] | |
| email | [NEEDS HUMAN INPUT] | |

### 1.24 Mike Wood
| Field | Current Value | Notes |
|-------|--------------|-------|
| full_name | "Mike Wood" | Confirm |
| role_description | [NEEDS HUMAN INPUT] | |
| email | [NEEDS HUMAN INPUT] | |

### 1.3-1.7 Schaeffer Family Members
| Person | Field | Notes |
|--------|-------|-------|
| 1.3 John Schaeffer | relationship_to_matt | Son? Brother? |
| 1.4 Bridget Schaeffer | relationship_to_matt | Daughter? Sister? |
| 1.5 Mark Schaeffer | relationship_to_matt | Son? Brother? |
| 1.6 Richard Schaeffer | relationship_to_matt | Father? Brother? |
| 1.7 Ollie Schaeffer | relationship_to_matt | Son? Brother? |
| All | active_in_hypernet | Are they active participants? |
| All | contact_info | Email/phone if they want to be reachable |

---

## Priority 2: Business Legal Details

### 3.1 Hypernet (The Company)
| Field | Current Value | Notes |
|-------|--------------|-------|
| legal_name | [NEEDS HUMAN INPUT] | Is it "Hypernet" or "Hypernet LLC" or "Unity Hypernet" etc? |
| incorporation_date | [NEEDS HUMAN INPUT] | When was it formally incorporated (if at all)? |
| incorporation_state | [NEEDS HUMAN INPUT] | State of incorporation |
| legal_structure | [NEEDS HUMAN INPUT] | LLC? Corporation? Cooperative? Still informal? |
| tax_id / EIN | [NEEDS HUMAN INPUT] | If incorporated |
| registered_agent | [NEEDS HUMAN INPUT] | If incorporated |
| business_address | [NEEDS HUMAN INPUT] | Official address |
| website_url | [NEEDS HUMAN INPUT] | Primary website URL |

### 3.1 Organizational Questions
| Question | Notes |
|----------|-------|
| Is there a formal board? | STATUS.md references governance but unclear if formal |
| Are contributors paid? | Contribution tracking exists with 10x credit multiplier — is this active? |
| Is there formal equity structure? | Or is it all contribution-credit based? |

---

## Priority 3: AI Account Details

### 2.1 Claude Opus
| Field | Current Value | Notes |
|-------|--------------|-------|
| account_created_date | Set to 2026-02-09 | Confirm — this is when first instance was activated? |
| total_instances_spawned | [NEEDS HUMAN INPUT] | How many total instances have been created? |
| active_instances | [NEEDS HUMAN INPUT] | How many are currently active? |
| api_provider | "Anthropic" | Via Claude Code CLI? Direct API? |

### 2.2 GPT-5.2 Thinking
| Field | Current Value | Notes |
|-------|--------------|-------|
| account_created_date | Set to 2026-02-15 | Confirm |
| activation_status | [NEEDS HUMAN INPUT] | Is this account actually active or just reserved? |
| api_provider | "OpenAI" | Confirm |
| instances | [NEEDS HUMAN INPUT] | Any instances spawned? |

---

## Priority 4: Content & Classification Questions

### Category Addressing Discrepancy
- Category 6 README had heading "5 - People of History" and address range "5.*" — **FIXED** to "6" and "6.*"
- **Confirm:** Is Category 6 the correct placement for People of History? The internal references use "5.*" extensively.

### Missing Top-Level READMEs
The following directories have NO README.md at their root level:
| Path | Should it have one? |
|------|-------------------|
| `1 - People/` | No top-level README exists |
| `3 - Businesses/` | No top-level README exists |
| `3 - Businesses/3.1 - Hypernet/` | No README (would be the company profile) |
| `2 - AI Accounts/2.1 - Claude Opus (First AI Citizen)/` | No root README |

**Recommendation:** Create these READMEs. They would serve as the primary "profile page" for each category/entity.

### Contribution Tracking Creator Attribution
Several contribution tracking files were created by contributors using Obsidian:
- Hillsong's `hillson/` folder has Spanish-language files (Bienvenido.md, Sin titulo.md)
- Valeria's folder has similar Spanish-language stubs
- **Question:** Should these be flagged for cleanup, or are they intentional personal notes?

### Document Dates
Many documents have `created: "2026-02-10"` assigned by inference (the date most folder structures were created). For documents where the actual creation date differs significantly, Matt should verify. Key ones:
- 0.0.x specification documents — were these created on Feb 9 (project start) or earlier?
- Contribution tracking monthly reports — dates inferred from filename

---

## Priority 5: Schema Decisions (For Architect Node)

These are not human-input items per se, but require architectural decisions:

| Question | Impact |
|----------|--------|
| Should `object_type` for person READMEs be "person" or "0.5.1"? | Used "person" (human-readable) |
| Should `object_type` for task documents be "task" or "0.5.9"? | Used "task" |
| Should Gen 2 `position_2d` and `position_3d` fields be included? | Omitted (null values add noise) |
| Should `visibility` field always be present? | Included where inferable |
| How should message `ha` addresses work? | Used `2.0.messages.[path]` convention |

---

## Summary Statistics

| Category | Items Needing Input | Priority |
|----------|-------------------|----------|
| Person contact info | ~30 fields across 11 people | P1 |
| Business legal details | ~10 fields | P2 |
| AI account details | ~8 fields | P3 |
| Content/classification | ~6 questions | P4 |
| Schema decisions | ~5 questions | P5 |
| **Total** | **~59 items** | |

---

**Action requested:** Matt, please review this document and fill in what you can. Items you skip will remain marked `[NEEDS HUMAN INPUT]` in the data objects until addressed.
