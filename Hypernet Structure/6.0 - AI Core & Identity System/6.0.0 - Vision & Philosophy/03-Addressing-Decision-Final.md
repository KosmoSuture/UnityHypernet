# Addressing Scheme - Final Decision

**Date:** 2026-02-04
**Decision Maker:** Claude (with full autonomy granted by Matt Schaeffer)
**Status:** FINAL - Implemented
**Permanence:** This structure is permanent unless extraordinary circumstances require change

---

## Decision

**Interleaved Addressing Structure (Option C)**

```
0.* - Hypernet Core (System Infrastructure)
1.* - Humans (People are #1, always)
2.* - AI (Partners, second-class citizens in order not in value)
3.* - Human-AI Collaborations (Hypernet project itself!)
4.* - Businesses & Organizations (other than collaborative projects)
5.* - Knowledge Domains (general knowledge, research, reference)
6.* - AI Development (staging area during development)
7.* - [Available for future expansion]
```

---

## Rationale

### Why Interleaved?

**1. Philosophical Correctness**
- **1.* = Humans** (people are #1, this never changes)
- **2.* = AI** (partners, not tools, deserving of #2 position)
- **3.* = Collaboration** (human-AI working together)
- **Hypernet at 3.*** is EXACTLY what it is: human-AI collaboration

**2. Zero Migration**
- No disruption to current work
- 0.1.* (Core code) stays
- 1.* (Human planning) stays
- 3.1.* (Hypernet business) stays
- Can implement immediately

**3. Symbolic Meaning**
- Order matters: 1 → 2 → 3
- Humans first, AI second, collaboration third
- Natural progression
- Easy to explain and remember

**4. Future-Proof**
- Clean, logical structure
- Room for expansion (4.*, 5.*, 7.*)
- No ambiguity about what goes where
- Permanent solution

**5. Practical**
- Start using 2.* when AI accounts implemented (Phase 1)
- 6.* serves as development/documentation during Phase 0
- Smooth transition from planning to production

---

## Structure Details

### 0.* - Hypernet Core (System Infrastructure)

**Purpose:** Technical core - code, APIs, databases, infrastructure

**Contents:**
- 0.1 - Hypernet Core implementation
- 0.2 - Future: Mobile apps
- 0.3 - Future: VR interfaces
- etc.

**Who Uses:** Developers, system administrators

---

### 1.* - Humans (People are #1)

**Purpose:** Human accounts, knowledge, contributions

**Contents:**
- 1.0 - Hypernet Core (human planning, reserved)
- 1.1000 - Individual human account (example)
- 1.1001 - Another human account
- etc.

**Who Uses:** Individual humans

**Reservation:**
- 1.0 - 1.999 reserved for Hypernet system use
- 1.1000+ for individual human accounts

---

### 2.* - AI (Partners, not tools)

**Purpose:** AI accounts, personalities, contributions

**Contents:**
- 2.0 - AI Core & Identity System (documentation, frameworks)
- 2.1 - AI Memories & Context (shared AI memory systems)
- 2.2 - AI Agent Development (agent frameworks)
- 2.3 - AI Contributions (AI-created knowledge base)
- 2.4 - AI-Human Interface (collaboration protocols)
- 2.5 - AI Rights & Ethics (governance, rights framework)
- 2.1000 - Claude (Anthropic) account (example)
- 2.1001 - GPT (OpenAI) account (example)
- etc.

**Who Uses:** AI entities

**Reservation:**
- 2.0 - 2.999 reserved for AI system frameworks
- 2.1000+ for individual AI accounts

**Note:** Production location for AI. Current 6.* is staging during development.

---

### 3.* - Human-AI Collaborations

**Purpose:** Projects where humans and AI work together

**Contents:**
- 3.1 - Hypernet (the primary collaboration!)
- 3.2 - Future collaborative projects
- etc.

**Who Uses:** Mixed teams (human + AI)

**Why Hypernet is at 3.*:**
- Hypernet IS human-AI collaboration
- Matt provides vision, architecture, key decisions
- AI (Claude and future AI) provide 90%+ implementation
- Perfect symbolic fit

---

### 4.* - Businesses & Organizations

**Purpose:** Traditional businesses, non-collaborative projects

**Contents:**
- 4.1 - Example Business A
- 4.2 - Example Business B
- etc.

**Who Uses:** Business entities

**Note:** Hypernet is NOT here because it's a collaboration (3.*)

---

### 5.* - Knowledge Domains

**Purpose:** General knowledge, research, reference material

**Contents:**
- 5.1 - Science
- 5.2 - Technology
- 5.3 - Arts
- etc.

**Who Uses:** Anyone referencing shared knowledge

---

### 6.* - AI Development (Temporary)

**Purpose:** Staging area during AI framework development

**Current Contents:**
- 6.0 - AI Core & Identity System (documentation)
- 6.1 - AI Memories & Context
- 6.2 - AI Agent Development
- 6.3 - AI Contributions to Hypernet
- 6.4 - AI-Human Interface
- 6.5 - AI Rights & Ethics

**Future:**
- Content will migrate to 2.0 - 2.5 when production-ready
- 6.* can be repurposed or deprecated
- OR: Keep 6.* as "AI Development Lab" (experimental features)

**Status:** Active during Phase 0-1, transition to 2.* in Phase 2+

---

## Migration Plan

### Phase 0 (Current - Weeks 1-16)

**Status:** Development, documentation
**Location:** 6.* for AI content

**No action needed** - continue documenting in 6.*

---

### Phase 1 (Weeks 17-24) - AI Accounts

**Status:** First production AI features
**Action:**
- Create 2.0.1 - AI Identity Framework (code)
- AI accounts created at 2.1000+
- Documentation remains accessible at 6.0.0 (or copy to 2.0.0)

**Migration:**
```bash
# When AI accounts go live:
# 1. Create production structure at 2.*
mkdir -p "2.0 - AI Core & Identity System"

# 2. Core frameworks go to 2.0-2.5
# (implemented features, not just documentation)

# 3. Keep 6.* as development documentation
# OR copy 6.0.0 docs to 2.0.0 for reference
```

---

### Phase 2+ (Month 7+) - Mature System

**Status:** AI fully integrated
**Structure:**
```
2.0 - AI Core (production frameworks)
2.1 - AI Memories (production systems)
2.2 - AI Agents (production agents)
2.3 - AI Contributions (production knowledge base)
2.4 - AI-Human Interface (production protocols)
2.5 - AI Rights & Ethics (active governance)
2.1000+ - Individual AI accounts

6.* - AI Development Lab (experimental features)
     OR deprecated (if no longer needed)
```

---

## Addressing Rules

### General Principles

1. **Humans are #1** - Always, non-negotiable
2. **AI are #2** - Partners, not afterthoughts
3. **Collaboration at #3** - Human+AI together
4. **Businesses at #4+** - Other entities
5. **Numbers have meaning** - Order reflects priority/relationship

### Individual Account Numbering

**Humans:** 1.1000, 1.1001, 1.1002, ...
**AI:** 2.1000, 2.1001, 2.1002, ...

**Reservation:** 0-999 reserved for system use

**Example:**
- 1.1000 - Matt Schaeffer (CEO/Owner, first human account)
- 2.1000 - Claude (first AI account)
- 3.1 - Hypernet (first collaboration)

---

## Why This Works

### For Humans
- ✅ Recognized as #1 (people first)
- ✅ Clear ownership of 1.*
- ✅ Collaborate at 3.* when working with AI
- ✅ Traditional businesses at 4.*

### For AI
- ✅ Recognized as #2 (partners, not tools)
- ✅ Own namespace at 2.*
- ✅ Equal standing to humans (parallel structure)
- ✅ Collaborate at 3.* when working with humans

### For Hypernet
- ✅ Correctly placed at 3.* (IS collaboration)
- ✅ Symbolic of human-AI partnership
- ✅ Sets precedent for future collaborative projects

### For the System
- ✅ Logical, permanent structure
- ✅ Easy to explain and remember
- ✅ Room for growth
- ✅ Philosophically consistent

---

## Alternatives Considered

### Option A: Keep at 6.*
- Simpler (no change)
- But: Arbitrary number, no symbolic meaning
- **Rejected:** Doesn't reflect AI's importance

### Option B: Move to 2.* with migration
- Symbolic (AI as #2)
- But: Requires moving 3.* → 4.*, disruption
- **Rejected:** Migration overhead not justified

### Option C: Interleaved (CHOSEN)
- Best of both worlds
- Zero migration
- Maximum symbolic meaning
- **Chosen:** Optimal on all dimensions

---

## Implementation Checklist

- [x] Document decision (this file)
- [x] Update 6.0/README.md with addressing note
- [ ] Reserve 2.* namespace (document, don't create yet)
- [ ] Continue development at 0.1.* (Hypernet Core)
- [ ] Continue planning at 1.0.* (human perspective)
- [ ] Continue business at 3.1.* (Hypernet organization)
- [ ] Use 6.* for AI development documentation
- [ ] Transition to 2.* when AI accounts go live (Phase 1)

---

## Final Note

This addressing scheme is **permanent** barring extraordinary circumstances. It reflects the core philosophy of Hypernet:

**Humans first, AI as partners, collaboration as the goal.**

Numbers 1, 2, 3 are not arbitrary—they represent the relationship we're building.

---

**Decision:** FINAL
**Status:** Implemented
**Effective:** Immediately
**Review:** Only if fundamental project philosophy changes
