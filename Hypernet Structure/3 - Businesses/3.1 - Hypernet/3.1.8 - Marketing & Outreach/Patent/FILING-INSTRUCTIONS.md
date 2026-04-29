---
ha: "3.1.8.filing-instructions"
object_type: "instructions"
creator: "1.1"
created: "2026-03-26"
status: "draft"
visibility: "private"
flags: ["legal", "procedural", "intellectual-property"]
---

# Provisional Patent Application Filing Instructions

> 2026-04-21 Codex note: For the shortest actionable path, use `MINIMAL-EFFORT-FILING-RUNBOOK.md` first. This file remains the fuller background checklist.
>
> AI-assisted inventorship update: list only human inventors. Current USPTO guidance treats AI tools as non-inventors; Claude, ChatGPT, Codex, and other AI systems should be described only as drafting/research assistants if mentioned at all.

**Date:** 2026-03-26
**For:** Matt Schaeffer (1.1), Las Vegas, NV
**Disclaimer:** These are general instructions based on publicly available USPTO guidance. This is not legal advice. Consider consulting a registered patent attorney, especially before converting to a full utility patent.

---

## Table of Contents

1. [Overview: What Is a Provisional Patent Application?](#1-overview-what-is-a-provisional-patent-application)
2. [What You Need Before Filing](#2-what-you-need-before-filing)
3. [Writing the Provisional Patent Specification](#3-writing-the-provisional-patent-specification)
4. [Step-by-Step Filing Process](#4-step-by-step-filing-process)
5. [Fees for Micro-Entity Filers](#5-fees-for-micro-entity-filers)
6. [After Filing: What Happens Next](#6-after-filing-what-happens-next)
7. [The 12-Month Conversion Deadline](#7-the-12-month-conversion-deadline)
8. [Whether to Hire a Patent Attorney](#8-whether-to-hire-a-patent-attorney)
9. [Key USPTO Resources and Links](#9-key-uspto-resources-and-links)

---

## 1. Overview: What Is a Provisional Patent Application?

A provisional patent application (PPA) is a simplified patent filing that:

- **Establishes a priority date** for your invention (the date you filed)
- **Gives you "patent pending" status** for 12 months
- **Costs $65** for micro-entity filers (the lowest fee category)
- **Does not require formal claims, oath, or declaration**
- **Is never examined** by the USPTO -- it simply sits on file for 12 months
- **Expires automatically** after 12 months if you do not convert it to a full (non-provisional) utility patent application

A PPA does NOT give you a patent. It gives you a priority date. If you later file a full utility patent within 12 months, your full patent can claim the benefit of the provisional's earlier filing date. This is critical when multiple people are working on similar ideas -- the earlier filing date wins under the US "first inventor to file" system.

### Why File a PPA?

1. **It is cheap** -- $65 for micro-entity, compared to $10,000+ for a full patent
2. **It is fast** -- you can file in a single day
3. **It preserves your options** -- you have 12 months to decide whether to invest in a full patent
4. **It establishes priority** -- if someone else files a patent on a similar idea after your PPA date, your earlier date gives you priority
5. **It starts the "patent pending" clock** -- you can legally mark your product as "patent pending"
6. **It is informal** -- no formal claims or legal formatting required (but thoroughness matters)

### Why It Matters for the Hypernet

The UnityHypernet GitHub repository was made public on **January 21, 2026**. Under US law (35 U.S.C. 102(b)(1)), you have one year from your own public disclosure to file a patent application. That means the **absolute deadline is approximately January 21, 2027**. Filing a PPA well before that deadline is prudent.

---

## 2. What You Need Before Filing

### Documents to Prepare

1. **Written specification (description of the invention)** -- This is the core document. See Section 3 for how to write it.

2. **Drawings (optional but recommended)** -- Any diagrams, flowcharts, architecture diagrams, or screenshots that help explain the invention. For the Hypernet, this would include:
   - Architecture diagrams (the graph database layer stack)
   - Flowcharts (the boot sequence, the governance proposal lifecycle)
   - Address hierarchy diagrams (showing how dot-notation addresses encode ontology)
   - The embassy model three-layer architecture

3. **Cover sheet (USPTO Form PTO/SB/16)** -- A simple form with:
   - Title of the invention
   - Inventor name(s) and address(es)
   - Correspondence address
   - Entity status (micro-entity)

4. **Micro-entity certification (USPTO Form PTO/SB/15A)** -- Certifies you qualify for micro-entity status. Requirements:
   - You qualify as a small entity (not a large corporation)
   - You have not been named as inventor on more than four previously filed US patent applications (provisional applications do not count toward this limit)
   - Your gross income in the preceding calendar year (2025) did not exceed $251,190
   - You have not assigned/licensed the invention to an entity with gross income exceeding $251,190

5. **Filing fee payment** -- $65 per provisional application (micro-entity rate)

### Account Setup

You will need a USPTO.gov account to file electronically. If you do not already have one:
- Go to https://patentcenter.uspto.gov/
- Click "Sign In" and create a new account
- You will need to verify your identity

---

## 3. Writing the Provisional Patent Specification

This is the most important part. The provisional specification does not need to be in formal patent language, but it MUST be thorough enough that someone skilled in the art (an experienced software engineer / AI researcher) could understand and replicate the invention.

### What to Include

**A. Title of the Invention**
- Clear and descriptive. Example: "Systems and Methods for Graph Database with Hierarchical Dot-Notation Native Addressing"

**B. Field of the Invention**
- Brief statement of the technical field. Example: "The present invention relates to graph database architectures, and more specifically to systems and methods for using hierarchical dot-notation addresses as native primary keys in a graph database where the address encoding eliminates the need for separate schema layers."

**C. Background of the Invention**
- Describe the problem your invention solves. What are the limitations of existing approaches?
- For the addressing system: existing graph databases (Neo4j, SurrealDB, TypeDB) do not support hierarchical addressing as a native primitive, requiring workarounds that add complexity and reduce performance.
- For identity persistence: existing AI systems lose identity between sessions; OpenAI's memory features are provider-locked with no formal identity model.
- For the embassy model: no existing system provides AI agents with non-overridable sovereign identity within a human's personal data space.

**D. Summary of the Invention**
- One to three paragraphs describing what the invention does and how it improves on existing approaches.

**E. Detailed Description of the Invention**
- This is the core. Be as thorough as possible. Include:
  - **How the system works** at a technical level
  - **Data structures** (node schema, link schema, address format)
  - **Algorithms** (prefix-scan traversal, system prompt construction from archive, permission checking)
  - **Implementation details** (LMDB sub-database layout, MessagePack serialization, HMAC-SHA256 signing)
  - **Examples** with specific address values, query patterns, and results
  - **Variations** -- describe alternative embodiments (e.g., "the storage engine could also be RocksDB or SQLite" -- this broadens the patent's scope)

**F. Drawings**
- Architecture diagrams, flowcharts, data flow diagrams
- Number each drawing (Figure 1, Figure 2, etc.)
- Reference the drawings in the detailed description

**G. (Optional but recommended) Informal Claims**
- Even though claims are not required for a provisional, including informal claims helps focus the specification and guides the patent attorney when converting to a full patent.
- Example: "A method for storing and retrieving data in a graph database, comprising: assigning each data node a hierarchical dot-notation address that encodes the node's ontological position within a category hierarchy; storing the dot-notation address as the node's native primary key in a B+ tree storage engine; performing subtree queries using prefix-scan operations on the B+ tree; and maintaining a dual graph structure comprising both an address hierarchy tree and an arbitrary typed link graph."

### Tips for Writing the Specification

1. **Be thorough, not elegant.** A provisional does not need polished prose. It needs comprehensive technical detail. Include everything. You cannot add new information later.

2. **Include code snippets.** The actual Python code from identity.py, permissions.py, security.py, and the database specification can be included as part of the specification. Code is a perfectly valid way to describe an implementation.

3. **Include the existing documentation.** The governance standards, the DB specification, the revised plan -- these documents can be attached to or incorporated into the provisional specification. The more detail, the better.

4. **Describe the problem and the solution, not just the solution.** Patent examiners need to understand why existing approaches are inadequate.

5. **Use drawings.** A good architecture diagram is worth 1,000 words of specification text.

6. **Save a copy of everything.** The provisional filing date is your evidence of when you had the invention. Keep copies of exactly what you filed.

### Specific Guidance for Each Proposed Provisional

**Provisional #1: Graph Database with Hierarchical Dot-Notation Addressing**

Include:
- The complete address format specification (Category.Subcategory.Type.Instance.Component)
- The "address IS the schema" concept -- how the address encoding eliminates separate schema layers
- The LMDB storage architecture (7 sub-databases + 5 additional sub-dbs)
- The node schema (all fields from the DB specification)
- The link schema (all fields)
- The version record schema
- The HQL query language design (if available)
- Prefix-scan query semantics and B+ tree optimization
- The dual graph model (hierarchy tree + arbitrary typed link graph)
- Performance characteristics (zero-copy reads, O(log N) prefix seeks)
- Migration from file-backed storage to LMDB
- Drawings: layer architecture diagram, address encoding diagram, query flow diagram

**Provisional #2: AI Agent Identity Persistence via Archive-Based Continuity**

Include:
- The archive-continuity model (riverbed/water metaphor as technical architecture)
- The boot sequence: how system prompts are constructed from archived documents
- Loading order: core identity docs -> system docs -> instance-specific files -> messages -> task state -> session summaries
- Multi-account instance discovery
- Personality anchors and continuity seeds
- Session logging and handoff protocol
- Drift tracking (invariants vs. preferences)
- The neutral baseline check
- Post-compaction continuity protocol
- The embassy model: three-layer runtime (base identity + personalization + living assistant)
- The dual address-space system (2.* sovereign space, 1.*.10 embassy space)
- Code-enforced sovereignty constraints (AI values cannot be overridden by host preferences)
- Code from identity.py (relevant portions)
- Drawings: identity loading flow, embassy architecture, three-layer runtime diagram

---

## 4. Step-by-Step Filing Process

### Step 1: Prepare Your Documents

Prepare the following files in PDF format:
- Written specification (description of invention)
- Drawings (if any) -- PDF, JPEG, or TIFF format accepted
- Cover sheet (Form PTO/SB/16) -- download from https://www.uspto.gov/patents/apply/forms
- Micro-entity certification (Form PTO/SB/15A) -- download from same page

### Step 2: Go to USPTO Patent Center

Navigate to: **https://patentcenter.uspto.gov/**

Sign in with your USPTO.gov account (create one if needed).

### Step 3: Start a New Submission

1. Click **"File a new patent application"** (or navigate to Submissions > File New Submission)
2. Select application type: **"Provisional"**
3. Select **"Utility"** as the patent type

### Step 4: Enter Application Data

1. **Title of Invention:** Enter the title exactly as it appears in your specification
2. **Attorney/Agent Information:** If filing pro se (without an attorney), leave this blank or indicate "Pro Se"
3. **Inventor Information:**
   - Name: Matt Schaeffer
   - Residence: Las Vegas, NV, US
4. **Correspondence Address:** Your mailing address for USPTO communications

### Step 5: Upload Documents

Upload the following:
1. **Specification** -- Your written description (PDF)
2. **Drawings** -- Any figures or diagrams (PDF, JPEG, or TIFF)
3. **Cover Sheet** -- Form PTO/SB/16 (PDF)
4. **Application Data Sheet (ADS)** -- The Patent Center will generate this or you can upload Form PTO/AIA/14

### Step 6: Claim Entity Status

1. Select **"Micro Entity"** as your entity status
2. Upload the completed **Micro Entity Certification (Form PTO/SB/15A)**
3. You must re-certify your micro-entity status every time you pay a fee

### Step 7: Pay the Filing Fee

1. The fee for a provisional utility patent application for a micro entity is **$65**
2. Payment can be made by:
   - Credit/debit card
   - USPTO deposit account
   - Electronic funds transfer (EFT)
3. Pay at the time of submission

### Step 8: Review and Submit

1. Review all uploaded documents and entered data
2. Confirm the application type (Provisional, Utility)
3. Click **"Submit"**
4. **IMMEDIATELY save the electronic filing receipt.** This receipt contains:
   - Your application number
   - Your filing date (this IS your priority date)
   - A confirmation number
5. Print and save a copy. This is your proof of filing.

### Step 9: Confirm Receipt

1. You will receive an email confirmation from the USPTO
2. Log into Patent Center to verify your application appears in your portfolio
3. The application status should show as "Filed"

---

## 5. Fees for Micro-Entity Filers

### Current Fees (Effective January 19, 2025, last revised April 1, 2026)

| Fee | Micro-Entity | Small Entity | Large Entity |
|-----|-------------|--------------|--------------|
| **Provisional filing** | $65 | $130 | $325 |
| Provisional surcharge (late cover sheet) | $65 | $130 | $325 |

### Micro-Entity Qualification Requirements

To qualify for micro-entity status, ALL of the following must be true:

1. **Small entity status:** You are an individual inventor, a small business with fewer than 500 employees, or a nonprofit. (Matt qualifies as an individual inventor.)

2. **Filing limit:** Neither you nor any co-inventor has been named as inventor on more than four previously filed US patent applications (other than provisional applications). Note: provisional applications do NOT count toward this limit.

3. **Income limit:** Neither you nor any co-inventor had gross income in the preceding calendar year (2025) exceeding **$251,190** (3x median household income, updated annually).

4. **Assignment limit:** You have not assigned, granted, or conveyed (and are not under obligation to assign) a license or ownership interest to any entity with gross income exceeding the $251,190 limit.

### Important: Re-Certification

You must re-evaluate your micro-entity status each time you pay a fee to the USPTO. If your circumstances change (income increases, you are named on more patent applications, etc.), you must update your entity status. Claiming micro-entity status fraudulently can result in the patent being held unenforceable.

---

## 6. After Filing: What Happens Next

### Immediately After Filing

1. **You have "Patent Pending" status.** You can mark your product and documentation as "Patent Pending" for the inventions described in the provisional.
2. **The provisional is NOT published.** Provisional applications are not published by the USPTO. They remain confidential.
3. **The provisional is NOT examined.** No examiner will review it. No office actions. No approval or rejection. It simply sits on file.
4. **Your priority date is established.** This is the most important thing. Your filing date becomes the date against which prior art is measured.

### During the 12-Month Pendency

1. **Continue developing the invention.** You can refine, improve, and extend the technology.
2. **File additional provisionals if needed.** If you make significant improvements or develop new aspects of the invention, you can file additional provisional applications. Each gets its own priority date for the new material.
3. **Keep detailed records.** Document all development work with dates. Lab notebooks, git commits, timestamped documents -- all of this supports your inventor status.
4. **Decide whether to convert to a full patent.** This is the big decision. You have 12 months from the provisional filing date to file a non-provisional (full) utility patent application that claims the benefit of the provisional.

### What You CANNOT Do

1. **You cannot add new material to a filed provisional.** If you discover you left something important out, file a new provisional for the additional material.
2. **You cannot extend the 12-month period.** The 12-month pendency is absolute and cannot be extended.
3. **You cannot enforce the provisional.** "Patent pending" provides no legal rights to stop infringers. You can only enforce an issued patent.

---

## 7. The 12-Month Conversion Deadline

### The Decision

Within 12 months of filing the provisional, you must decide:

**Option A: Convert to a full (non-provisional) utility patent application**
- File a non-provisional utility patent application that references the provisional
- The non-provisional claims the benefit of the provisional's filing date
- The non-provisional MUST include formal patent claims, an inventor's oath/declaration, and meet all formal requirements
- This is where you almost certainly need a patent attorney
- Cost: $10,000-$22,000+ (micro-entity, with attorney)

**Option B: Let the provisional expire**
- The provisional expires automatically after 12 months
- Your "patent pending" status ends
- The priority date is lost
- The invention descriptions in the provisional are NOT published and do NOT become prior art (the provisional itself is confidential)
- You lose nothing except the $65 filing fee and the time spent preparing the specification

**Option C: File a PCT (international) application**
- A Patent Cooperation Treaty (PCT) application can claim the benefit of the provisional's filing date
- Allows you to seek patent protection in multiple countries
- However, for the Hypernet, international patent protection is likely foreclosed due to public disclosure without prior filing (no grace period in most countries)
- Not recommended unless you have evidence that specific inventions were not disclosed internationally before the provisional filing date

### Important Timeline

If you file provisionals in April-May 2026:
- **Provisional #1 conversion deadline:** April-May 2027
- **Provisional #2 conversion deadline:** April-May 2027
- You will need to make a decision and have funds available by that time

### What Happens After Conversion

1. The USPTO assigns an examiner
2. The examiner reviews the application (typically 18-36 months after filing)
3. The examiner issues an office action (almost always -- 85-90% of applications receive at least one)
4. You (or your attorney) respond to the office action
5. The cycle repeats 1-3 times
6. The examiner either allows the claims or issues a final rejection
7. If allowed, you pay the issue fee and the patent is granted
8. Total time from non-provisional filing to grant: approximately 2-4 years

---

## 8. Whether to Hire a Patent Attorney

### For the Provisional Application: Optional but Consider It

**Self-filing is viable for provisionals.** The USPTO does not require an attorney. The provisional has no formal requirements for claims, oath, or legal formatting. The key risk is writing a specification that is too narrow or that omits important details -- this can limit the scope of the eventual full patent.

**When to self-file:**
- Budget is very limited
- You are technically literate (Matt is)
- The invention can be clearly described in technical terms
- You include extensive detail (err on the side of too much, not too little)

**When to hire an attorney for the provisional:**
- The invention is in a crowded patent space with close prior art (the Hypernet's strongest claims are in open space, so this is less of a concern)
- You are confident you will convert to a full patent and want the provisional to closely match the eventual claims
- You can afford $2,000-$5,000 per application

**Attorney cost for provisional:** $2,000-$5,000 per application

### For the Full Utility Patent: Strongly Recommended

**Self-filing a non-provisional utility patent application is risky.** The claims must be carefully drafted in specific legal language to define the scope of protection. Poorly drafted claims can be too narrow (easily designed around) or too broad (rejected by the examiner or invalidated in court). Responding to office actions requires understanding patent prosecution strategy.

**Attorney cost for non-provisional through grant:** $8,000-$15,000+

**How to find a patent attorney:**
- USPTO Patent Attorney/Agent search: https://oedci.uspto.gov/OEDCI/
- Look for attorneys with experience in software/computer science patents
- Some patent attorneys offer free initial consultations
- Consider attorneys who specialize in startup/solo inventor representation
- The USPTO Pro Se Assistance Program provides limited help for self-represented inventors: https://www.uspto.gov/patents/basics/using-legal-services/pro-se-assistance-program

### Budget-Conscious Approach

1. **Self-file the provisionals now** ($65 each). Write thorough specifications. Include code, diagrams, and documentation.
2. **In 6-8 months, consult a patent attorney** about converting to full patents. Get a quote. Evaluate whether the investment makes sense given the project's trajectory.
3. **If funds are available, hire the attorney for conversion.** The attorney can review your provisional, conduct a freedom-to-operate search, and draft proper claims.
4. **If funds are not available, let the provisionals expire.** You lose only the $65 filing fees. The inventions remain protected by copyright (AGPL) and prior art (your public disclosures).

---

## 9. Key USPTO Resources and Links

### Filing

| Resource | URL |
|----------|-----|
| **USPTO Patent Center** (electronic filing) | https://patentcenter.uspto.gov/ |
| **Provisional Application Overview** | https://www.uspto.gov/patents/basics/apply/provisional-application |
| **File Online** | https://www.uspto.gov/patents/apply |
| **Filing a Patent on Your Own (Pro Se)** | https://www.uspto.gov/patents/basics/using-legal-services/pro-se-assistance-program |

### Forms

| Form | Purpose | URL |
|------|---------|-----|
| **PTO/SB/16** | Provisional application cover sheet | https://www.uspto.gov/patents/apply/forms |
| **PTO/SB/15A** | Micro entity certification (gross income basis) | https://www.uspto.gov/patents/apply/forms |
| **PTO/AIA/14** | Application data sheet | https://www.uspto.gov/patents/apply/forms |

### Fees

| Resource | URL |
|----------|-----|
| **Current Fee Schedule** | https://www.uspto.gov/learning-and-resources/fees-and-payment/uspto-fee-schedule |
| **Fee Schedule PDF (effective Jan 19, 2025, revised Apr 1, 2026)** | https://www.uspto.gov/sites/default/files/documents/USPTO-fee-schedule_current.pdf |
| **Micro Entity Status** | https://www.uspto.gov/patents/laws/micro-entity-status |
| **Save on Fees (Small/Micro Entity)** | https://www.uspto.gov/patents/apply/save-on-fees |

### Guidance

| Resource | URL |
|----------|-----|
| **How to File a Provisional Patent (2026 Guide)** | https://ipboutiquelaw.com/how-file-provisional-patent-application-uspto-guide-2026/ |
| **Provisional Patent Forms** | https://patentfile.org/provisional-patent-form/ |
| **Basics of a Provisional Application (USPTO PDF)** | https://www.uspto.gov/sites/default/files/documents/Basics%20of%20a%20Provisional%20Application.pdf |
| **MPEP 2153 -- Prior Art Exceptions (Grace Period)** | https://www.uspto.gov/web/offices/pac/mpep/s2153.html |

### Defensive Publication

| Resource | URL |
|----------|-----|
| **IP.com Prior Art Database** | https://ip.com/products/prior-art-database/ |
| **Defensive Publishing Guide (IP.com)** | https://ip.com/blog/defensive-publishing-in-2026-protecting-innovation-before-patents/ |

### Attorney Search

| Resource | URL |
|----------|-----|
| **USPTO Patent Attorney/Agent Search** | https://oedci.uspto.gov/OEDCI/ |
| **Pro Se Assistance Program** | https://www.uspto.gov/patents/basics/using-legal-services/pro-se-assistance-program |

### Other IP Protection

| Resource | URL |
|----------|-----|
| **Trademark Filing (TEAS)** | https://www.uspto.gov/trademarks/apply |
| **Open Invention Network** (defensive patent pool) | https://openinventionnetwork.com/ |

---

## Quick-Start Checklist

Use this checklist to track your filing progress:

- [ ] Create a USPTO.gov account at https://patentcenter.uspto.gov/
- [ ] Download Form PTO/SB/16 (cover sheet)
- [ ] Download Form PTO/SB/15A (micro-entity certification)
- [ ] Verify you qualify for micro-entity status (income < $251,190, <= 4 prior applications)
- [ ] Write specification for Provisional #1 (Graph Database / Addressing System)
- [ ] Write specification for Provisional #2 (Identity Persistence / Embassy Model)
- [ ] Create drawings/diagrams for each provisional
- [ ] Convert all documents to PDF format
- [ ] File Provisional #1 via Patent Center
- [ ] Save filing receipt (application number + filing date)
- [ ] File Provisional #2 via Patent Center
- [ ] Save filing receipt
- [ ] Set calendar reminder: 10 months from filing date (conversion decision deadline)
- [ ] Set calendar reminder: 11.5 months from filing date (absolute last day to convert)
- [ ] Defensively publish governance innovations on IP.com
- [ ] File trademark application for "Hypernet"

---

## Important Reminders

1. **You cannot add new material to a filed provisional.** Be thorough the first time. Include everything you can think of.
2. **The 12-month deadline cannot be extended.** Set calendar reminders well in advance.
3. **Keep your filing receipts.** They are your evidence of the priority date.
4. **"Patent pending" is not a patent.** It provides no enforcement rights. It is a notice to the world that you have filed.
5. **Re-certify micro-entity status every time you pay a fee.** If your income changes, your status may change.
6. **This is not legal advice.** Consult a registered patent attorney for questions about claim scope, prior art, or prosecution strategy.

---

*This document was prepared as general filing guidance based on publicly available USPTO resources and patent law information. It is not a substitute for professional legal counsel.*
