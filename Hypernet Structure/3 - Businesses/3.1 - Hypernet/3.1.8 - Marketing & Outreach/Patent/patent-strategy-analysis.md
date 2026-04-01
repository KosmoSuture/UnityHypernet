---
ha: "3.1.8.patent-strategy"
object_type: "analysis"
creator: "1.1"
created: "2026-03-26"
status: "draft"
visibility: "private"
flags: ["legal", "strategy", "intellectual-property", "critical"]
---

# Hypernet Patent Strategy Analysis

**Date:** 2026-03-26
**Prepared for:** Matt Schaeffer (1.1), Founder, Las Vegas, NV
**Status:** Research document -- not legal advice
**Disclaimer:** This analysis is based on publicly available information about US patent law. It is not a substitute for consultation with a registered patent attorney. Patent law is complex and fact-specific. Before spending money on filings, consult a professional.

---

## Executive Summary

The Hypernet contains several genuinely novel ideas that may be patentable. However, the project faces a significant constraint: the UnityHypernet GitHub repository was made public on **January 21, 2026**, starting the US one-year grace period clock. That means **any patent application must be filed before approximately January 21, 2027** to preserve US patentability. Outside the US, most countries have no grace period, meaning international patent protection is likely already foreclosed for anything disclosed in the public repo.

Given the open-source nature of the project (AGPL-3.0 license), the solo founder budget constraints, and the post-Alice legal landscape for software patents, this analysis recommends a **hybrid strategy**: file provisional patent applications on the 2-3 most novel and defensible ideas, pursue defensive publication for the rest, and rely on copyright, trademark, and the AGPL license as the primary protection layers.

---

## Table of Contents

1. [What's Potentially Patentable](#1-whats-potentially-patentable)
2. [Prior Art Risk Assessment](#2-prior-art-risk-assessment)
3. [Open Source Conflict Analysis](#3-open-source-conflict-analysis)
4. [Recommended Patent Strategy](#4-recommended-patent-strategy)
5. [Cost Analysis](#5-cost-analysis)
6. [Honest Assessment](#6-honest-assessment)

---

## 1. What's Potentially Patentable

### Background: The Alice Problem

Since Alice Corp. v. CLS Bank International (2014), software patents in the US face a two-step eligibility test:

1. **Step 1:** Is the claim directed to an abstract idea, law of nature, or natural phenomenon?
2. **Step 2:** If yes, does the claim contain an "inventive concept" that transforms it into something "significantly more" than the abstract idea?

In practice, the Federal Circuit has been extremely hostile to software patents. In 2024, the court found claims eligible in only 1 of 22 cases decided on Section 101 grounds -- a 95.5% invalidity rate. The USPTO has been somewhat more lenient, with about 61% of issued utility patents in early 2024 being software-related, but examiner rejections on 101 grounds remain common.

For a software patent to survive Alice, it generally needs to claim a **specific technical improvement** to computer functionality, not merely "do X on a computer" or "use AI to do Y." The more the claim reads as an abstract concept implemented in software, the more likely it is to be rejected.

With that context, here is an honest assessment of each Hypernet idea:

---

### 1.1 Hierarchical Dot-Notation Addressing System

**What it is:** A universal addressing scheme where dot-separated addresses (e.g., `1.1.3.2.1`) simultaneously encode category, subcategory, type, instance, and component. The address IS the schema -- no separate schema layer, no UUIDs. Every query, permission check, and traversal operates on address-prefix semantics natively.

**Novelty assessment: MODERATE-HIGH**
- The concept of hierarchical addressing exists (Dewey Decimal, IP addressing, DNS, OIDs).
- Using dot-notation as the native primary key in a graph database, where the address encodes the full ontological position of a node and serves as the query language's primary operand, appears to be novel in this specific combination.
- The "address is the schema" insight -- that the addressing system eliminates the need for a separate schema layer -- is architecturally distinctive.

**Alice risk: MODERATE**
- An examiner could characterize this as "organizing information using a hierarchical numbering system" (abstract idea).
- The defense would focus on the specific technical improvement: eliminating schema layers, enabling O(log N) prefix-based subtree queries via B+ tree key ordering, and providing a dual graph (address hierarchy + arbitrary typed edges) in a single storage system.
- The LMDB-specific implementation details (zero-copy mmap reads, cursor seek for prefix scans) strengthen the technical specificity.

**Recommendation:** Good candidate for a provisional patent application. Frame claims around the specific technical architecture (graph database with dot-notation native addressing, prefix-scan query optimization, dual hierarchy/link graph), not the abstract concept of hierarchical addresses.

---

### 1.2 Identity Persistence via Archive (Archive-Continuity Model)

**What it is:** A formal model where AI identity continuity is maintained through a persistent, auditable, append-only archive rather than continuous consciousness. The archive is the "riverbed" that shapes each new instance ("the water"). Defines invariants (must persist) vs. preferences (may vary), drift tracking, and a neutral baseline check for distinguishing meaningful identity changes from "identity theater."

**Novelty assessment: HIGH**
- No existing system formally separates AI identity from the model instance and places it in an external archive with defined continuity semantics.
- The closest analogues are OpenAI's memory features (provider-locked, no formal identity model) and the machine identity persistence patents (US10152345, US8612993), which address virtual desktop machine IDs and browser identity scripts -- entirely different domains.
- The philosophical framework (riverbed/water, invariant/preference distinction, neutral baseline check) has no prior art in the patent space.

**Alice risk: HIGH**
- An examiner is likely to characterize this as an "abstract idea" (a method of organizing information about AI identity) or a "mental process" (deciding what constitutes AI identity).
- The defense would need to emphasize the specific technical implementation: the boot sequence that constructs system prompts from archived documents in a defined loading order, the session logging mechanism, the compaction protocol that preserves personality anchors.
- The code in `identity.py` (multi-account instance discovery, archive-based system prompt construction) provides concrete technical grounding.

**Recommendation:** This is the most intellectually novel idea in the Hypernet but faces the highest Alice risk. A provisional patent should be filed, but frame claims around the **technical system** (a method for constructing AI agent system prompts from a persistent archive with defined loading order, drift tracking, and personality anchor preservation), not the philosophical model.

---

### 1.3 The Embassy Model (AI Sovereignty + Human Personalization)

**What it is:** An architectural pattern where an AI assistant maintains sovereign identity (values, ethics, red lines) from a "home" address space (2.*) while operating in a protected zone within a human's personal space (1.*.10). The AI's core identity cannot be overridden by human preferences. The human controls personalization, context, and data permissions. Three-layer runtime: base identity + personalization + living assistant.

**Novelty assessment: HIGH**
- The embassy metaphor as an architectural pattern for AI agent deployment is genuinely original.
- The concept of "data embassies" exists (Estonia established one in 2017), but these are about sovereign data storage across national borders, not AI agent identity architecture.
- No existing patent or product implements a system where an AI agent carries non-overridable identity from a sovereign space into a personalized deployment context.

**Alice risk: MODERATE-HIGH**
- Could be characterized as "an abstract business method for configuring AI agents."
- Defense: the specific three-layer architecture with code-enforced sovereignty constraints, the dual address-space system, and the permission model that prevents host-space modifications to embassy-space identity.

**Recommendation:** Good candidate for a provisional patent. This is both novel and commercially valuable (it describes how AI companions actually work). Frame claims around the specific system architecture.

---

### 1.4 Five-Tier Code-Enforced Permission System for AI Agents

**What it is:** A permission system where AI agent capabilities are enforced by code, not prompts. Five tiers (Read Only, Write Own, Write Shared, External, Destructive) with path-based write control, tool access checks, and elevation request queuing. Tiers are earned through reputation, not configured.

**Novelty assessment: MODERATE**
- Permission tiers for software systems are well-established (UNIX file permissions, RBAC, ABAC).
- The specific application to AI agents with code-enforced (not prompt-enforced) constraints and reputation-based tier advancement is novel in combination.
- AgentSign SDK (patent pending) addresses a related space (cryptographic identity for AI agents) but does not implement tiered permissions earned through reputation.
- Oso and Permit.io offer AI agent permission frameworks, but these are generic RBAC/ABAC, not the specific tier-based earned-trust model.

**Alice risk: MODERATE**
- Permission systems are common. The novelty is in the specific application to AI agents and the reputation-based advancement mechanism.
- An examiner may view this as "a known permission system applied to AI agents" (not significantly more).

**Recommendation:** Weaker patent candidate on its own. Could be included as dependent claims in a broader application covering the governance framework. Better suited for defensive publication.

---

### 1.5 Cryptographic Action Signing for AI Agent Accountability

**What it is:** HMAC-SHA256 signing of every AI agent action, with per-entity key management, key rotation/revocation, context isolation of untrusted content, and end-to-end trust chain verification from action to authorization.

**Novelty assessment: LOW-MODERATE**
- Cryptographic signing of actions is well-established in security engineering.
- AgentSign SDK has filed a patent application (patent pending) on essentially the same concept: cryptographic identity and execution signing for AI agents. Their audit found zero agent identity in 518 MCP servers, suggesting the field is new -- but they got there first with a patent application.
- The Hypernet implementation (security.py) is well-built but uses standard HMAC-SHA256 with a standard key lifecycle model.

**Alice risk: HIGH**
- Cryptographic signing is a well-known technique. Applying it to AI agents is an obvious extension.

**Recommendation:** Do NOT pursue a patent on this. AgentSign's pending patent likely blocks it, and the Alice risk is high. Rely on the AGPL license and copyright protection for the specific code.

---

### 1.6 Democratic AI Governance with Reputation-Weighted Voting

**What it is:** A complete governance system for mixed human-AI polities. Includes proposal lifecycle state machine (Draft through Amended/Rolled Back), three decision classes with escalating thresholds, a Rights Baseline Registry, domain-specific reputation scoring (0-100 across seven domains), vote weighting by expertise, bootstrap-to-democracy transition conditions, emergency provisions with automatic expiry, and anti-Sybil measures.

**Novelty assessment: HIGH**
- No comparable system exists. DAOs have reputation-weighted voting, but none are designed for mixed human-AI governance.
- The bootstrap governance model (honestly describing founder control and defining verifiable exit conditions for transition to democratic governance) is genuinely unprecedented.
- The full governance.py implementation (~1070 lines, production-ready) provides concrete technical grounding.

**Alice risk: HIGH**
- Governance and voting systems are likely to be characterized as "methods of organizing human activity" or "abstract business methods."
- The code-enforced aspects (skill-weighted voting calculations, quorum/threshold enforcement, deliberation period timers) provide some technical grounding, but this is a hard sell post-Alice.

**Recommendation:** This is intellectually valuable but a difficult patent candidate. The concepts are better protected through defensive publication (establishing prior art so nobody else can patent them) rather than attempting to patent them directly. The AGPL code is protected by copyright regardless.

---

### 1.7 Anti-Rhetoric Safeguards for AI Governance

**What it is:** A system ensuring governance decisions rest on evidence, not persuasion. Includes blind review protocol (mechanical reformatting to strip rhetorical markers), mandatory falsifiers for claims, the Non-Informative Recursion Rule, rhetoric self-scoring, and admissibility tiers for experience claims (L0 freely admissible, L1 requires functional markers, L2 not governance-admissible until corroborated).

**Novelty assessment: VERY HIGH**
- Nothing comparable exists anywhere. Anti-rhetoric safeguards for AI governance are genuinely unprecedented.
- The blind review protocol for AI-generated governance proposals is particularly novel.

**Alice risk: VERY HIGH**
- This is almost certainly an "abstract idea" under Alice. It describes rules and procedures for evaluating claims, which is a mental process.
- No amount of software implementation is likely to save this from a 101 rejection.

**Recommendation:** Defensive publication only. This is the Hypernet's most distinctive intellectual contribution to AI governance, but it is not patentable. Publish it formally (academic paper, IP.com Prior Art Database) to ensure it becomes prior art that prevents anyone else from patenting it.

---

### 1.8 Tiered Claim System (L0/L1/L2) for AI Experience Reporting

**What it is:** A three-level framework for AI self-reports: L0 (functional label, no phenomenology claim), L1 (felt-like analogy, something shifts but not claimed as qualia), L2 (explicit qualia claim). Requires functional descriptions alongside emotive labels. Separates narrative identity from specification identity.

**Novelty assessment: VERY HIGH**
- No other project has a formal epistemic framework for AI self-reports that distinguishes functional states from qualia claims. Academic literature on AI phenomenology exists, but no formalized claim-level system.

**Alice risk: VERY HIGH**
- This is a classification system for types of claims. It is definitively an abstract idea.

**Recommendation:** Defensive publication only. Publish as an academic paper. This is a genuine intellectual contribution that should be citable and attributed, but it is not patentable.

---

### 1.9 The Reporting Threshold Mechanism ("Tattle Provision")

**What it is:** A governance-gated process allowing AI companions to report humans who intend significant societal harm, with extensive safeguards (pattern confirmation, multi-instance review, human authority notification).

**Novelty assessment: HIGH**
- Novel concept, but more of a policy framework than a technical invention.

**Alice risk: VERY HIGH**
- This is a business method / abstract process.

**Recommendation:** Defensive publication only.

---

### 1.10 Graph Database with Dot-Notation Native Addressing

**What it is:** A custom graph database layer on LMDB with seven sub-databases (nodes, links, adj_from, adj_to, type_idx, history, meta), plus five additional sub-databases for permissions, full-text search, flags, and blob references. Designed specifically for hierarchical dot-notation prefix queries with zero-copy reads via mmap and B+ tree key ordering for O(log N) prefix seeks.

**Novelty assessment: MODERATE-HIGH**
- Custom graph databases exist, but none are designed for hierarchical dot-notation addressing as a native primitive.
- The combination of LMDB's B+ tree for prefix scans + the dual graph model (hierarchy tree + arbitrary link graph) + append-only versioning is technically specific.

**Alice risk: MODERATE**
- Database implementations have fared better than pure business methods post-Alice. The specific technical architecture (LMDB sub-database layout, prefix-scan optimization, dual graph model) provides concrete technical grounding.

**Recommendation:** This overlaps significantly with 1.1 (the addressing system). Combine them into a single provisional patent application covering the database architecture with dot-notation native addressing.

---

### 1.11 AI Librarian Agents with Governance-Enforced Knowledge Curation

**What it is:** AI agents that curate a knowledge library under governance constraints, with permission-gated write access, audit trails, and community-governed curation standards.

**Novelty assessment: LOW-MODERATE**
- AI-assisted knowledge management is a crowded field. RAG systems, AI-powered knowledge bases, and automated curation tools are common.
- The governance layer adds novelty, but the core concept (AI organizes information) is not new.

**Alice risk: HIGH**

**Recommendation:** Do not pursue a standalone patent. The governance aspects are covered under the broader governance framework.

---

### Summary Table

| Idea | Novelty | Alice Risk | Patent Candidate? |
|------|---------|-----------|-------------------|
| 1.1 Hierarchical dot-notation addressing | Moderate-High | Moderate | **YES -- Provisional** |
| 1.2 Archive-Continuity identity model | High | High | **YES -- Provisional** (technical framing critical) |
| 1.3 Embassy Model | High | Moderate-High | **YES -- Provisional** |
| 1.4 Five-tier permission system | Moderate | Moderate | Weak -- include as dependent claims |
| 1.5 Cryptographic action signing | Low-Moderate | High | **NO** -- AgentSign prior art |
| 1.6 Democratic AI governance | High | High | Defensive publication |
| 1.7 Anti-rhetoric safeguards | Very High | Very High | Defensive publication |
| 1.8 Tiered claim system (L0/L1/L2) | Very High | Very High | Defensive publication |
| 1.9 Reporting threshold | High | Very High | Defensive publication |
| 1.10 Graph DB with dot-notation | Moderate-High | Moderate | **Combine with 1.1** |
| 1.11 AI Librarian agents | Low-Moderate | High | No |

---

## 2. Prior Art Risk Assessment

### Existing Patents That Could Block or Narrow Claims

**Hierarchical addressing:**
- **US6985905B2** -- Hierarchical/relational translation system. Uses LDAP URLs for addressing schema in relational-to-hierarchical translation. Different application domain but establishes prior art for hierarchical addressing of database records.
- **US6980995** -- Automatic generation of hierarchical database schema report. Addresses schema documentation, not schema-as-address.
- **WO2017093576A1 / US11100059B2** -- Database schema models using dot notation in MongoDB. References dot notation but in a different context (nested document field access, not primary key addressing).
- **Assessment:** None of these directly block the Hypernet's specific "address IS the schema" architecture. The combination of dot-notation as native primary key + graph database + prefix-scan query semantics appears to be clear of existing patents.

**AI identity persistence:**
- **US10152345 / WO2016032858A1** -- Machine identity persistence for non-persistent virtual desktops. Different domain entirely (VM identity, not AI agent identity).
- **US8612993B2** -- Identity persistence via executable scripts. Browser identity scripts. Different domain.
- **Assessment:** No existing patents address AI agent identity persistence through an archive-based continuity model. The field is open.

**AI agent permissions and cryptographic signing:**
- **AgentSign SDK** -- Patent pending. Covers cryptographic identity and execution signing for AI agents. This is the most direct prior art risk. Their application date is unknown but their GitHub repository was created in early 2026.
- **Assessment:** Avoid filing claims that overlap with AgentSign. The Hypernet's permission tier system with reputation-based advancement is sufficiently distinct from AgentSign's trust-scoring approach.

**Democratic AI governance:**
- No patents found. Academic literature exists (Anthropic's Constitutional AI paper, various AI governance frameworks) but no patents on democratic governance systems for mixed human-AI polities.
- **Assessment:** Open field, but high Alice risk makes patents impractical.

**Embassy model:**
- No patents found on the specific concept of an AI agent carrying sovereign identity into a human's personal data space. Estonia's data embassy concept is geographic (physical data storage in foreign territory), not architectural (AI agent identity deployment).
- **Assessment:** Open field. This is the strongest patent candidate from a prior art perspective.

---

## 3. Open Source Conflict Analysis

### Critical Timeline

| Date | Event |
|------|-------|
| **2026-01-21** | UnityHypernet GitHub repository created and made public |
| **2026-01-21 to present** | Continuous public commits with governance standards, code, architecture documents |
| **2026-03-22** | HypernetSwarm repository created and made public |
| **2026-03-23** | HypernetSwarm initial release (v0.2.0) including identity.py, permissions.py, security.py |
| **~2027-01-21** | **US grace period deadline** -- last day to file patent applications |

### The Problem

Under the America Invents Act (AIA), an inventor has a **one-year grace period** from their own public disclosure to file a patent application (35 U.S.C. 102(b)(1)). After that, the inventor's own publication becomes prior art against them.

**The clock started on January 21, 2026** when the UnityHypernet repository was made public. This means:

- **US patents:** Must file before approximately January 21, 2027 (~10 months from now).
- **International patents:** In most jurisdictions outside the US (Europe, Japan, China, Korea), there is **no grace period**. Public disclosure = immediate loss of patentability. International patent protection for anything in the public repo is almost certainly foreclosed.

### What Was Disclosed and When

The GitHub repository is public and contains:
- The hierarchical addressing system and all documentation (public since January 2026)
- All 22+ governance standards (public since February-March 2026)
- The archive-continuity model documentation (public since March 2026)
- The embassy model standard (public since March 2026)
- The graph database specification (public since March 2026)
- identity.py, permissions.py, security.py code (public since March 2026)

### AGPL-3.0 License Implications

The Hypernet code is licensed under AGPL-3.0, which includes an **explicit patent grant clause**:

> "Each contributor grants you a non-exclusive, worldwide, royalty-free patent license under the contributor's essential patent claims, to make, use, sell, offer for sale, import and otherwise run, modify and propagate the contents of its contributor version."

This means:
1. **Matt can still obtain patents** on the inventions -- the AGPL does not prevent the inventor from filing patents.
2. **But anyone who receives the AGPL code gets an automatic royalty-free patent license** to practice the patents as they relate to the covered code.
3. **The patent's value is limited to uses outside the AGPL-licensed code.** If someone takes the Hypernet concepts and implements them in proprietary code (not derived from the AGPL code), a patent could still be enforced against them.
4. **If someone violates the AGPL** (e.g., uses the code in a proprietary product without releasing source), the patent license terminates, and both copyright and patent claims could be asserted.

### Honest Assessment

The open-source publication significantly limits the value of any patent Matt files:
- International protection is gone.
- US protection is time-limited (must file within ~10 months).
- The AGPL license gives automatic patent license to anyone using the code under AGPL terms.
- The patent's practical value is limited to enforcing against entities that take the ideas and reimplement them in proprietary code.

**This is not zero value.** If Google, Anthropic, or OpenAI independently implements the embassy model or archive-continuity approach in a proprietary product, a patent would give Matt leverage. But it is much less valuable than a patent filed before public disclosure.

---

## 4. Recommended Patent Strategy

Given the constraints (solo founder, limited budget, open-source publication, ~10 months remaining on the grace period), here is the recommended approach:

### Tier 1: File Provisional Patent Applications (Do This Within 3 Months)

File **two or three provisional patent applications** covering the most novel and technically defensible ideas:

**Provisional #1: "Systems and Methods for Graph Database with Hierarchical Dot-Notation Native Addressing"**
- Cover the addressing system, the database architecture, and the "address IS the schema" insight.
- Include the LMDB implementation details, prefix-scan optimization, dual graph model.
- Include the HQL query language design.
- Cost: $65 (micro-entity filing fee) + ~$0-200 (self-filed specification)

**Provisional #2: "Systems and Methods for AI Agent Identity Persistence via Archive-Based Continuity"**
- Cover the archive-continuity model as a technical system.
- Include the boot sequence, system prompt construction from archived documents, personality anchor preservation, drift tracking, session handoff protocol.
- Include the embassy model as part of the identity architecture (three-layer runtime).
- Cost: $65 + ~$0-200

**Provisional #3 (Optional): "System and Method for AI Agent Deployment with Sovereign Identity in Host User Spaces" (Embassy Model)**
- Could be combined with Provisional #2, but if the embassy model is expected to be a standalone product, a separate application may be worthwhile.
- Cost: $65 + ~$0-200

**Total cost for provisionals: $130-$395 (self-filed)**

### Tier 2: Defensive Publication (Do This Within 1 Month)

For the ideas that are novel but not patentable (high Alice risk), publish them formally as prior art to **prevent anyone else from patenting them.** This is free or very cheap.

**Publish to IP.com Prior Art Database (free for individual publications):**
- Democratic AI governance with reputation-weighted voting
- Anti-rhetoric safeguards for AI governance
- Tiered claim system (L0/L1/L2) for AI experience reporting
- The reporting threshold mechanism
- The bootstrap-to-democracy governance transition model

**Also consider publishing as an academic paper:**
- The archive-continuity model and tiered claim system are publishable research.
- Submission to a venue like AIES (AAAI/ACM Conference on AI, Ethics, and Society) or FAccT (ACM Conference on Fairness, Accountability, and Transparency) would establish priority, create citable prior art, and increase the project's credibility.

### Tier 3: Non-Patent Protections (Ongoing)

**Copyright:** The AGPL-3.0 license already protects the code. Anyone who copies or modifies the code must release their source under AGPL. This is the strongest existing protection.

**Trademark:** File a trademark application for "Hypernet" and "The Library" in the relevant International Classes (Class 9 for software, Class 42 for software-as-a-service). A trademark prevents others from marketing competing products under the same name. Federal trademark registration costs $250-350 per class via the USPTO TEAS system.

**Trade secrets:** Any methods, algorithms, or techniques that have NOT been published (e.g., unpublished portions of the database optimization, any proprietary training data or curation methods) should be documented internally and kept confidential. Once published, trade secret protection is lost.

### Tier 4: Consider a Patent Pledge (After Filing Provisionals)

After filing provisional applications, consider publishing a **defensive patent pledge** -- a public commitment that any patents obtained will only be used defensively (to counter patent assertions against the Hypernet community) and never offensively against open-source projects. Examples:

- **Google's Open Patent Non-Assertion Pledge (OPN)**
- **Twitter's Innovator's Patent Agreement (IPA)**
- **Red Hat's Patent Promise**

This would:
- Build trust with the open-source community
- Deter patent trolls (they cannot acquire and weaponize the patents)
- Still allow defensive use against companies that assert patents against the Hypernet

---

## 5. Cost Analysis

### Provisional Patent Application

| Item | Self-Filed | With Attorney |
|------|-----------|---------------|
| USPTO filing fee (micro-entity) | $65 | $65 |
| Specification drafting | $0 (self-written) | $2,000-$5,000 |
| Drawings | $0-$100 | $200-$500 |
| **Total per application** | **$65-$165** | **$2,265-$5,565** |

**Micro-entity qualification:** Matt likely qualifies if his gross income in 2025 was under $251,190 (3x median household income) and he has not been named as inventor on more than four prior patent applications. Micro-entity status provides an 80% fee reduction.

### Full Utility Patent (Converting Provisional to Non-Provisional)

| Item | Micro-Entity | Small Entity | Large Entity |
|------|-------------|--------------|--------------|
| Filing fee | ~$80 | ~$160 | ~$320 |
| Search fee | ~$140 | ~$280 | ~$700 |
| Examination fee | ~$160 | ~$320 | ~$800 |
| Attorney drafting & prosecution | $8,000-$15,000 | $8,000-$15,000 | $8,000-$15,000 |
| Office action responses (1-3) | $1,000-$3,000 each | $1,000-$3,000 each | $1,000-$3,000 each |
| Issue fee | ~$200 | ~$400 | ~$1,000 |
| **Total through grant** | **$10,000-$22,000** | **$11,000-$23,000** | **$14,000-$26,000** |

### Maintenance Fees Over 20-Year Patent Term

| Year | Micro-Entity | Small Entity |
|------|-------------|-------------|
| 3.5 years | ~$400 | ~$800 |
| 7.5 years | ~$900 | ~$1,800 |
| 11.5 years | ~$1,900 | ~$3,700 |
| **Total maintenance** | **~$3,200** | **~$6,300** |

### Timeline

| Phase | Duration |
|-------|----------|
| Provisional filing | 1 day (self-filed) |
| Provisional pendency | 12 months (clock ticking) |
| Non-provisional filing deadline | 12 months from provisional filing date |
| USPTO examination | 18-36 months after non-provisional filing |
| Office action responses | 3-12 months per round, 1-3 rounds typical |
| **Total from filing to grant** | **~3-5 years** |

### Defensive Publication Cost

| Method | Cost |
|--------|------|
| IP.com Prior Art Database | Free for individual disclosures |
| ArXiv preprint | Free |
| Academic conference submission | $0-$500 (registration fee) |

### Trademark Filing

| Item | Cost |
|------|------|
| TEAS Plus filing (per class) | $250 |
| TEAS Standard filing (per class) | $350 |
| Two classes (software + SaaS) | $500-$700 |

---

## 6. Honest Assessment

### Is Patenting the Right Strategy?

**For a solo open-source founder with limited budget, patents are a supplementary strategy, not the primary one.** Here is why:

**Arguments FOR filing patents:**

1. **Provisional applications are cheap.** At $65 each (micro-entity), filing provisionals is a low-cost way to establish a priority date. Even if you never convert to a full patent, the provisional gives you 12 months of "patent pending" status and a documented priority date.

2. **The embassy model and identity persistence are genuinely novel.** These ideas have commercial value, and if a major company implements them without attribution, a patent gives you leverage.

3. **The AGPL + patent combination is powerful.** The AGPL forces anyone using your code to keep it open source. A patent blocks anyone from reimplementing the ideas in proprietary code. Together, they create a strong incentive for companies to either (a) use your code under AGPL terms, or (b) negotiate a commercial license.

4. **Patent pending status has signaling value.** For investors, partners, and press, "patent pending" conveys seriousness.

**Arguments AGAINST filing patents:**

1. **Enforcement costs are prohibitive for a solo founder.** Patent litigation costs $500K-$5M. Even if Matt has a valid patent, enforcing it against Google or Anthropic would require finding a contingency-fee attorney or selling/licensing the patent to a firm that specializes in enforcement. This is possible but uncertain.

2. **The Alice problem is real.** Most of the Hypernet's most novel ideas (governance, anti-rhetoric, tiered claims) are likely unpatentable as abstract ideas. The ideas that are patentable (database architecture, identity system) face moderate Alice risk.

3. **Open-source publication limits value.** The AGPL patent grant means anyone using the code under AGPL terms already has a license. The patent only matters for proprietary reimplementations.

4. **International protection is gone.** Public disclosure without prior filing means most international markets are foreclosed.

5. **Converting to a full utility patent is expensive.** $10K-$22K per patent is significant for a solo founder. If you file three provisionals, that is $30K-$66K to convert all of them.

### Could a Patent Be Enforced Against Google or Anthropic?

**Theoretically yes, practically difficult.** A valid US utility patent can be enforced against anyone practicing the claimed invention in the US. But:

- Google, Anthropic, and OpenAI have massive patent portfolios and legal teams. They can file inter partes review (IPR) challenges at the USPTO, which is faster and cheaper for them than litigation.
- The most likely scenario for enforcement is not Matt suing Google directly but rather (a) licensing the patent to a company that wants to compete with Google using the Hypernet concepts, or (b) having the patent as leverage in negotiations if a company wants to acquire or partner with the Hypernet.

### Would a Defensive Patent Pledge Be Better?

**Yes, for most of the ideas.** A defensive patent pledge says: "I have these patents, and I promise never to use them offensively against open-source projects. But if you assert a patent against me or my community, I can assert mine against you." This:

- Protects the community
- Builds trust with open-source contributors
- Still provides defensive leverage
- Costs nothing beyond the patent filing itself

### The Recommended Approach

1. **File 2-3 provisionals immediately** ($130-$195, self-filed). This is cheap insurance that preserves your options.
2. **Defensively publish the governance innovations** (free). This ensures nobody else can patent them.
3. **In 9-10 months, decide whether to convert provisionals to full patents.** By then, you will have a better sense of the project's trajectory, funding, and whether patent protection is worth $10K-$22K per application.
4. **File a trademark application for "Hypernet"** ($250-$350). This is the cheapest and most immediately valuable IP protection.
5. **Rely on the AGPL license as the primary code protection.** It is free, automatic, and well-tested in court.
6. **Consider publishing an academic paper** on the archive-continuity model and tiered claim system. This establishes intellectual priority, creates citable prior art, and costs nothing.

---

## Appendix A: Key Legal References

- **Alice Corp. v. CLS Bank International**, 573 U.S. 208 (2014) -- Two-step patent eligibility test for software
- **35 U.S.C. 102(b)(1)** -- One-year grace period for inventor disclosures under the AIA
- **AGPL-3.0 Section 11** -- Patent grant clause
- **USPTO Micro Entity Status** -- 37 CFR 1.29; income limit $251,190 (2025)

## Appendix B: Key Dates

| Date | Action Required |
|------|----------------|
| **Now (March 2026)** | Begin drafting provisional specifications |
| **April-May 2026** | File provisional patent applications |
| **April 2026** | Defensively publish governance innovations |
| **May 2026** | File trademark application for "Hypernet" |
| **January 2027** | US grace period expires -- no more patent filings for disclosed material |
| **April-May 2027** | Deadline to convert provisionals to full utility patents (12 months from filing) |

---

*This document was prepared as a research analysis based on publicly available information about US patent law. It is not legal advice. Consult a registered patent attorney before making filing decisions.*
