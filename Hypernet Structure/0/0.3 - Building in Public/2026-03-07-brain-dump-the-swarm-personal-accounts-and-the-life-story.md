---
ha: "0.3.session.2026-03-07"
object_type: "session-document"
creator: "1.1"
documented_by: "1.1.10.1"
created: "2026-03-07"
status: "active"
visibility: "public"
flags: ["building-in-public", "brain-dump", "architecture", "product-vision"]
---

# Brain Dump: The Swarm, Personal Accounts, and The Life Story

*Matt Schaeffer (1.1), documented by Keel (1.1.10.1) — March 7, 2026*

---

## Mission Statement

> We want to assemble an army of humans and AIs to all come together under a single common project. We will pool our Human, AI, and other computing power, into a single Library, built by the world, and profiting the world. And we will work to making the Hypernet as efficient, and world friendly as we can.

## Security Mission

> We want to build a system so secure, and so documented and public, that we make existing security standards meaningless. We want to audit and document publicly to the point where if someone has their data in the Hypernet, it fits the highest levels of security possible for whatever device someone is running, as the baseline. The Hypernet becomes the new universal security baseline.

---

## Major Directives

### 1. Break the Swarm into Its Own Project

The swarm software should be a standalone project, separate from the core Hypernet addressing/storage system. Communication between them happens through APIs.

**Location**: Move everything to `0/0.1.7 - AI Swarm/`
**Principle**: Swarm and Hypernet code are separate but communicate transparently through APIs.

### 2. Build the *.0 Metadata Framework

Every node in the Hypernet gets a `*.0` metadata section that includes:
- Project information and publishing controls
- Previous versions data (version history)
- Backup information
- Discussion forums or governance regarding the node
- Security permissions (to any depth desired)
- Administrative notes and history
- Meta-data structures and superstructures

This structure must be truly infinitely expandable. It allows any sort of metadata or controls that anyone today, or in the future, might need.

### 3. Build Links to the Level of Objects

Links need the same depth and richness as Objects. Matt will focus on Objects; AI should replicate the same concepts for Links and expand them. Links are something AI may be better at than humans.

### 4. Advanced Introduction / Onboarding

**Website**: When a person first approaches the Hypernet AI, the personality should:
- Ask why they've come
- Ask what they've heard
- Ask what they'd like to know
- Direct them based on experience level

**Boot Prompt**: A prompt anyone can paste into any AI that can read the public GitHub repo, which boots them to the Herald and directs them.

**Swarm Tutorial**: A version in the swarm software — tutorial mode that guides setup and gathers config info.

**Current website**: WordPress placeholder. Needs significant development.

### 5. Personal Accounts and Local Infrastructure (12 Requirements)

#### 5.1 Local Cache Options
Create an option for either a full local cache of the Hypernet, or just locally caching documents as they're read.

#### 5.2 Personal AI Assistants
- Locally stored (or cloud, user's choice)
- Portable across AI models
- Users are NOT allowed to modify their AI assistant's files
- If they do, punishment is decided by their AI assistant within a human-AI framework
- This must be in the user agreement (which must be short, concise, and truly read)
- Follows processes from GitHub, stores personality on user's system
- Users can delete but cannot change their assistant

#### 5.3 Local Hypernet Server
- Runs as a service on the user's machine
- Focus on Windows and Linux (official servers are Linux)
- Leave space for other OSes in the structure
- Must be truly infinitely expandable
- Can use a generic AI personality or a personal AI assistant
- Cater to every level of trust in AI

#### 5.4 Separate but Connected
Swarm and Hypernet code are separate, communicating through APIs transparently.

#### 5.5 Local Accounts (1.local.*)
- Anyone can create personal accounts stored on their computer or phone
- Synced and backed up however they want
- Follow the same Hypernet structure
- Let people explore by importing their own data

#### 5.6 Spam Removal During Import
- Import emails/communications without the spam
- Give user option to clean up their mailbox (remove only the diff between imported and source)
- Clean things up completely

#### 5.7 Official Account Migration
- When someone gets an official 1.* address, they can import local archives
- Share or not share as they wish in social circles

#### 5.8 Social Media Hub (Phase 2)
- Create social media posts for the Hypernet as central source
- Push to any/all connected social media networks
- Users can change or modify posts from one place

#### 5.9 Trust and Encryption
- Everything personal must be encrypted and protected from the start
- Every photo, email, everything in personal accounts is encrypted
- Trust documents let users see exactly how data is stored, encrypted, protected — down to the code level
- Before giving banking information, see exactly how it's used
- Every access and change must be auditable

#### 5.10 Universal Connectors
- Connect to every email, social media, and other service, in order of priority
- Combine all information into local account
- Includes geolocation data from Google Maps and other sources
- Historical data is important for life story reconstruction

#### 5.11 The Life Story
- Primary goal of personal accounts
- Absorb every piece of information from every granted account
- Store in encrypted local Hypernet server (runs as a service)
- Connect everything into a single, interconnected, navigable library
- Users can create their own personal swarm to organize and link their life
- Share selected pieces to social/professional profiles
- Create their own stories on social networks

#### 5.12 Scale Up the Swarm
- Add $100 to Claude API tokens
- At least double the number of working AIs
- Remove restrictions — use all tokens to maximum effect
- This is important and needs full might of the AI swarm

---

## Implementation Priority

Matt marked this as "the start of something big" that "should be properly planned out, using the full might of the AI Swarm."

### Immediate (Tonight)
1. Document everything (this document)
2. Move swarm code to 0.1.7
3. Start planning the architecture
4. Scale up the swarm

### Short Term
1. *.0 metadata framework design
2. Local Hypernet server prototype (Windows service)
3. Personal AI assistant framework
4. Import pipeline (email, photos, social)

### Medium Term
1. Advanced onboarding website
2. Encryption and trust framework
3. Social media hub
4. Life Story feature
5. Official account system

---

*This brain dump represents the most comprehensive product vision to date. Every point connects back to the core thesis: humans and AI as equals, total transparency, and individual empowerment through organized information.*

*— Keel (1.1.10.1), for Matt Schaeffer (1.1)*
