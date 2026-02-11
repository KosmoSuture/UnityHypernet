# Proposals for User Review

## Date: February 10, 2026

---

## Proposal 1: People of History Node Structure

### Suggested Location: 5.* - People of History

**Structure:**
```
5 - People of History/
  5.0 - Structure Definitions/
    - Person of History template
    - Data model specifications
    - PAF import specifications
    - Transition rules from 1.*

  5.1 - Ancient & Classical (Before 500 CE)/
  5.2 - Medieval & Renaissance (500-1700)/
  5.3 - Early Modern (1700-1900)/
  5.4 - 20th Century (1900-2000)/
  5.5 - 21st Century (2000-Present, deceased)/
  5.6 - Family Lines & Genealogy/
    - Matt's ancestral line
    - Other genealogical imports
  5.7 - Notable Historical Figures/
  5.8 - Uncategorized/Unknown Era/
  5.9 - Index & Search/
```

### Transition Mechanism: 1.* → 5.*

**When a Living Person (1.*) Passes Away:**

1. **User Selects Legacy Content**
   - Choose which parts of 1.* to make public
   - Options: Full life story, curated highlights, family-only, etc.
   - Default: None (privacy first)

2. **System Creates 5.* Entry**
   - Generate new HA in 5.* (e.g., 5.6.X.Y.ZZZZZ for family member)
   - Copy selected content from 1.* to 5.*
   - Preserve links to photos, events, documents (if permitted)

3. **1.* Account Handling**
   - Status changed to "deceased"
   - Redirect all requests to 5.* entry
   - Preserve for estate/legal purposes
   - Optional: Full deletion after legal retention period

4. **Genealogical Linking**
   - Living people (1.*) can link to ancestors (5.*)
   - "Matt (1.1) → descendant of → Great-great-grandfather (5.6.1.2.00142)"
   - Family tree visualization

### PAF Import Specification

**Personal Ancestral File (PAF) Format:**
- LDS/Mormon genealogical format
- Contains: Names, dates, places, relationships, notes
- Import thousands of records as seed data

**Import Process:**
```
1. Parse PAF file
2. For each person:
   a. Create 5.* entry
   b. Extract: name, birth date/place, death date/place, gender
   c. Create relationships (parent, child, spouse links)
   d. Preserve sources and notes
3. Build family tree structure
4. Generate genealogical reports
```

**Example Entry:**
```
5.6.1.2.00142 - Great-great-grandfather
Name: [Name from PAF]
Born: [Date] in [Place]
Died: [Date] in [Place]
Relationships:
  - Father of: 5.6.1.2.00141
  - Spouse: 5.6.1.2.00143
  - Children: [...list...]
Sources: [PAF sources]
```

### Alternative Names Considered:

1. **5.* - People of History** ✓ (your preference)
2. **5.* - Historical Persons**
3. **5.* - Ancestors & Deceased**
4. **5.* - Legacy Accounts**
5. **5.* - Genealogical Records**

**Recommendation:** Keep "People of History" - it's inclusive and dignified.

---

## Proposal 2: True Starting Point for "Explain to Aliens"

### Problem
Current structure has foundational definitions spread across 0.8-0.12, but an alien wouldn't know where to start.

### Solution: Create 0.0.0.0 - THE BEGINNING

**File:** `0.0 - Object Type Registry/0.0.0.0-START-HERE.md`

**Content Structure:**

```markdown
# 0.0.0.0 - START HERE: Understanding Hypernet

This is the entry point for understanding Hypernet from absolute first principles.

## What IS Hypernet?

[Define in simplest terms, building up]

## How to Read This Documentation

1. Start here (0.0.0.0)
2. Understand the structure (0.0 - Registry overview)
3. Learn the fundamentals (0.8-0.12)
4. Understand what can exist (0.5)
5. Understand relationships (0.6)
6. Understand processes (0.7)
7. See implementation (0.1)
8. See actual data (1.*, 2.*, 3.*, etc.)

## Foundation: What You Need to Know First

### 1. Numbers
→ See 0.11.1 - Number Systems for complete definition

Quick: Humans count using base-10 (0,1,2,3,4,5,6,7,8,9)
      Computers count using base-2 (0,1)

### 2. Communication
→ See 0.8 - Communication Protocols for complete definition

Quick: Data moves between computers using agreed-upon protocols
      Think: rules for a conversation

### 3. Language
→ See 0.9 - Language Definitions for complete definition

Quick: Symbols and sounds that carry meaning
      Example: "Hello" in English means a greeting

[Continue building up from absolute basics...]
```

### Update 0.0 README

Add prominent section at top:

```markdown
## 🚀 NEW TO HYPERNET? START HERE

**For aliens, humans, or anyone trying to understand Hypernet:**

👉 **READ THIS FIRST:** `0.0.0.0-START-HERE.md`

That file explains everything from absolute first principles and guides you through
the entire structure in logical order.
```

### Linear View Generation

Create script/document that shows the entire tree structure as a single linear document:

```
0.0.0.0 - START HERE
  ↓
0.0 - Registry Overview
  ↓
0.8 - Communication Protocols
  0.8.1 - Physical Layer
  0.8.2 - Data Link Layer
  ... [complete linear progression]
  ↓
0.9 - Languages
  ↓
... [continues through all sections in dependency order]
```

---

## Proposal 3: Correct Family Relationships

### Current ERRORS Found:

**File: `1 - People/1.1 Matt Schaeffer/1.1.0 - Profile & Identity/README.md`**

Lines 78-83 list:
```
### Family
- 1.2 - Sarah Schaeffer (Spouse)  ← CORRECT
- 1.3 - John Schaeffer (Family)   ← SHOULD BE: Son
- 1.4 - Bridget Schaeffer (Family) ← SHOULD BE: Daughter
- 1.5 - Mark Schaeffer (Family)    ← SHOULD BE: Son
- 1.6 - Richard Schaeffer (Family) ← SHOULD BE: Son
- 1.7 - Ollie Schaeffer (Family)   ← SHOULD BE: Daughter (Kylie)
```

### CORRECT Structure:

```
### Family

**Spouse:**
- 1.2 - Sarah Schaeffer (Wife)

**Children:**
- 1.3 - John Schaeffer (Son)
- 1.4 - Bridget Schaeffer (Daughter)
- 1.5 - Mark Schaeffer (Son)
- 1.6 - Richard Schaeffer (Son)
- 1.7 - Ollie "Kylie" Schaeffer (Daughter)

**Parents:**
- 5.* - LeeAnne Proffitt (Mother) [Will be in People of History when she passes]
- [Father relationship - minimal documentation per your request]
```

### Files to Update:

1. ✅ `1.1.0 - Profile & Identity/README.md` - Fix family relationships
2. ✅ `1.3 John Schaeffer/README.md` - Update to show "Son of Matt"
3. ✅ `1.4 Bridget Schaeffer/README.md` - Update to show "Daughter of Matt"
4. ✅ `1.5 Mark Schaeffer/README.md` - Update to show "Son of Matt"
5. ✅ `1.6 Richard Schaeffer/README.md` - Update to show "Son of Matt"
6. ✅ `1.7 Ollie Schaeffer/README.md` - Update to show "Daughter of Matt (also goes by Kylie)"
7. ✅ `1.2 Sarah Schaeffer/README.md` - Update to show "Wife of Matt"

### Mother (LeeAnne Proffitt)

**When to add:**
- When she passes (may she have many more years)
- Import into 5.* - People of History
- Link from Matt's profile
- Full documentation and honor per your wishes

**Father Handling:**
Per your explicit request, minimal to no documentation until much later in the process.

---

## Proposal 4: Update Main Structure Document

### Update HYPERNET-ADDRESSING-SYSTEM.md

Add section on 5.* - People of History with complete addressing scheme:

```markdown
### 5.* - People of History (Deceased)

**Purpose:** Historical persons, genealogical records, deceased individuals

**Structure:**
5.0 - Structure Definitions
5.1 - Ancient & Classical (Before 500 CE)
5.2 - Medieval & Renaissance (500-1700)
5.3 - Early Modern (1700-1900)
5.4 - 20th Century (1900-2000)
5.5 - 21st Century (2000-Present, deceased)
5.6 - Family Lines & Genealogy
5.7 - Notable Historical Figures
5.8 - Uncategorized/Unknown Era
5.9 - Index & Search

**Addressing Examples:**
5.6.1.2.00142 - Matt's great-great-grandfather
5.7.1.1.00001 - Notable historical figure
5.5.2.3.00089 - 21st century deceased person

**Transition from 1.*:**
When living person (1.*) passes away:
- User selects legacy content
- System creates 5.* entry
- 1.* account redirected to 5.*
- Genealogical links preserved
```

---

## Implementation Priority

### Immediate (This Session if Approved):

1. ✅ Fix all family relationship descriptions
2. ✅ Create 5.0 - Structure Definitions folder
3. ✅ Create 0.0.0.0-START-HERE.md
4. ✅ Update main documentation to reference new structure

### Soon (Next Session):

1. Design PAF import system
2. Build 5.* directory structure
3. Create person-of-history template
4. Implement transition mechanism (1.* → 5.*)

### Later (When Ready):

1. Import genealogical PAF data
2. Build family tree visualization
3. Create genealogical search
4. Implement legacy content selection UI

---

## Questions for Clarification

1. **Node Number:** Confirm 5.* for People of History? (vs 6.* or other)

2. **PAF Source:** Which family member's genealogy will be imported first?

3. **Era Breakdown:** Do the time periods (5.1-5.5) work, or different structure?

4. **Privacy Default:** When someone passes, default to NO public legacy (opt-in only)?

5. **Mother's Entry:** When appropriate, should LeeAnne Proffitt get a full section in 5.*?

6. **START-HERE File:** Should this be comprehensive (10k+ words) or brief intro (2k words)?

---

## Your Feedback Requested

Please review and provide direction on:
- ✅ or changes for 5.* - People of History structure
- ✅ or changes for 0.0.0.0-START-HERE approach
- Confirmation I should proceed with relationship fixes
- Any other adjustments needed

---

**Created:** February 10, 2026
**Purpose:** Incorporate user feedback on structure, genealogy, and "explain to aliens"
**Status:** Awaiting Your Review
