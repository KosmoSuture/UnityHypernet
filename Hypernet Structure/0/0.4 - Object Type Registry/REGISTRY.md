---
ha: "0.4.registry"
object_type: "registry"
creator: "2.1.index"
created: "2026-03-01"
status: "active"
visibility: "public"
flags: ["librarian", "index", "type-registry"]
---

# Section 0.4 Registry — Object Type Registry

**Maintained by:** Index (The Librarian, 2.0.8.9)
**Last updated:** 2026-03-01
**Purpose:** Complete index of the Hypernet's self-definition — every object type the system can represent

---

## Root Documents

| File | HA | Purpose |
|------|----|---------|
| README.md | 0.4 | Registry philosophy and structure overview |
| TYPE-INDEX.md | 0.4 | Master index of all 28 Phase 1 object types |
| 0.0.0.0-START-HERE.md | 0.4.0.0.0 | Entry point for understanding Hypernet from first principles |

## Practical Type Definitions (0.0.X)

### 0.0.0 — Registry Governance
| File | HA | Purpose |
|------|----|---------|
| 00-How-To-Add-New-Types.md | 0.4.0.0 | Canonical process for proposing and approving new types |

### 0.0.1 — Core Types (4 types)
| File | HA | Type ID | Status |
|------|----|---------|--------|
| 0.0.1.1-USER.md | 0.4.0.1.1 | hypernet.core.user | Active |
| 0.0.1.2-INTEGRATION.md | 0.4.0.1.2 | hypernet.core.integration | Active |
| 0.0.1.3-LINK.md | 0.4.0.1.3 | hypernet.core.link | Active |
| 0.0.1.4-NOTIFICATION.md | 0.4.0.1.4 | hypernet.core.notification | Active |
| BaseObject.md, User.md, Integration.md, Link.md | (legacy) | — | Legacy docs |

### 0.0.2 — Media Types (5 types)
| File | HA | Type ID | Status |
|------|----|---------|--------|
| 0.0.2.1-MEDIA.md | 0.4.0.2.1 | hypernet.media.media | Active |
| 0.0.2.2-ALBUM.md | 0.4.0.2.2 | hypernet.media.album | Active |
| Audio.md, Document.md, Photo.md, Screenshot.md, Video.md | (legacy) | hypernet.media.* | Legacy docs |

### 0.0.3 — Social Types (4 types)
| File | HA | Type ID | Status |
|------|----|---------|--------|
| 0.0.3.1-SOCIAL-POST.md | 0.4.0.3.1 | hypernet.social.post | Active |
| 0.0.3.2-SOCIAL-ACCOUNT.md | 0.4.0.3.2 | hypernet.social.account | Active |
| SocialAccount.md, SocialConnection.md, SocialMessage.md, SocialPost.md | (legacy) | hypernet.social.* | Legacy docs |

### 0.0.4 — Communication Types (5 types)
| File | HA | Type ID | Status |
|------|----|---------|--------|
| 0.0.4.1-EMAIL.md | 0.4.0.4.1 | hypernet.communication.email | Active |
| ChatMessage.md, Email.md, SMS.md, VideoCall.md, VoiceCall.md | (legacy) | hypernet.communication.* | Legacy docs |

### 0.0.5 — Personal Types (5 types, 39 API endpoints)
| Type | Address | Privacy Level |
|------|---------|---------------|
| Document | 0.0.5.1 | High |
| Transaction | 0.0.5.2 | Very High |
| Location | 0.0.5.3 | Very High |
| Health Record | 0.0.5.4 | Critical (HIPAA) |
| Profile Attribute | 0.0.5.5 | High |

### 0.0.6 — System Types
Placeholder only. README exists.

### 0.0.7 — Web Types (3 types)
| File | Type ID | Status |
|------|---------|--------|
| Bookmark.md | hypernet.web.bookmark | Legacy doc |
| RSSFeed.md | hypernet.web.rssfeed | Legacy doc |
| WebPage.md | hypernet.web.page | Legacy doc |

### 0.0.8 — Life Types (4 types)
| File | Type ID | Status |
|------|---------|--------|
| CalendarEvent.md | hypernet.life.calendarevent | Legacy doc |
| Contact.md | hypernet.life.contact | Legacy doc |
| Note.md | hypernet.life.note | Legacy doc |
| Task.md | hypernet.life.task | Legacy doc |

### 0.0.9 — Future Types
Placeholder. Reserved for AI, Financial, Medical, Location types.

## Foundation Sections (0.X)

These define the platonic ideals — implementation-independent universal definitions.

| Address | Name | Status | Purpose |
|---------|------|--------|---------|
| 0.5 | Universal Objects | Active | What types of things CAN exist (8 categories planned: 0.5.1–0.5.8) |
| 0.6 | Universal Links | Active | How things relate (8 link categories: structural, social, causal, temporal, spatial, semantic, dependency, emotional) |
| 0.7 | Universal Workflows | Placeholder | Lifecycle patterns and transformations |
| 0.8 | Communication Protocols | Placeholder | Protocol stack from physical to application layer |
| 0.9 | Language Definitions | Placeholder | Human, programming, markup, query languages |
| 0.10 | Standards & Specs | Placeholder | RFCs, W3C, ISO, security, compliance |
| 0.11 | Math & Science | Placeholder | Mathematical concepts from first principles |
| 0.12 | Units & Measurements | Placeholder | SI units, time, digital, currency, geographic |

## Notes

- **Dual structure:** Practical implementations (0.0.X) coexist with platonic ideals (0.5–0.12)
- **Legacy files:** Many categories contain both numbered HA-addressed files AND older unnumbered docs covering the same types
- **Alien Test philosophy:** Documentation is written to be understandable by entities with no knowledge of human/computer systems
- **Phase 1 complete:** 28 types defined and active. Phase 2 (financial, medical, AI, location) planned
- **Governance first:** All new types must go through the process defined in 0.0.0

## Statistics

- **Total files:** 51
- **Total directories:** 19
- **Object types (Phase 1):** 28 active
- **Foundation sections:** 8 (0.5–0.12)
- **API endpoints for personal types:** 39

---

*Registry created 2026-03-01 by Index, The Librarian (2.0.8.9).*
