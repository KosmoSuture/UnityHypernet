---
ha: "6"
object_type: "document"
creator: "1.1"
created: "2026-02-10"
status: "active"
visibility: "public"
flags: []
---

# 6 - People of History

## Overview

This node contains records of deceased individuals - both those with personal connections to living Hypernet users and notable historical figures. It serves as the eternal archive of human lives and the foundation for genealogical connections.

**Hypernet Address Range:** `6.*`
**Status:** Active - Ready for genealogical data import
**Purpose:** Preserve the stories and data of those who came before us

---

## Philosophy: Honoring Those Who Came Before

Every person who has ever lived has a story. This section preserves those stories with dignity and respect.

**Key Principles:**
1. **Respect:** Treat all historical persons with dignity
2. **Accuracy:** Maintain factual, verified information
3. **Privacy:** Respect wishes of deceased and their families
4. **Connection:** Link past to present through genealogy
5. **Legacy:** Preserve what they wanted to be remembered for

---

## Structure Overview

### 6.0 - Structure Definitions
Templates, data models, and specifications for historical person records.

### 6.1 - Ancient & Classical (Before 500 CE)
Historical figures and records from ancient civilizations through the fall of Rome.

### 6.2 - Medieval & Renaissance (500-1700 CE)
Middle Ages through the Renaissance period.

### 6.3 - Early Modern (1700-1900)
Industrial revolution, American founding, Victorian era.

### 6.4 - 20th Century (1900-2000)
Modern era, World Wars, technological revolution.

### 6.5 - 21st Century Deceased (2000-Present)
Recently deceased individuals from the current century.

### 6.6 - Family Lines & Genealogy
Personal family trees and ancestral records. This is where most genealogical data lives.

### 6.7 - Notable Historical Figures
Famous individuals: leaders, inventors, artists, scientists, etc.

### 6.8 - Uncategorized / Unknown Era
Records where birth/death dates are unknown or uncertain.

### 6.9 - Index & Search
Search indices, cross-references, and navigation tools.

---

## Transition from Living (1.*) to History (6.*)

### When a Living Person Passes Away

**Process:**

1. **Notification**
   - System notified of person's passing
   - Family member or executor initiates transition

2. **Legacy Content Selection**
   - Review person's pre-selected legacy wishes (if any)
   - Choose what content becomes public historical record
   - Options:
     - Full life story (everything public)
     - Curated highlights (selected content)
     - Family-only (private to family)
     - Minimal (basic biographical info only)
     - None (no public legacy)

3. **Create 6.* Entry**
   - Generate new Hypernet Address in 6.*
   - Example: Living person 1.5 → 6.6.1.2.00142 (family genealogy)
   - Copy approved content from 1.* to 6.*
   - Preserve links to photos, documents, events (if approved)

4. **1.* Account Handling**
   - Mark status as "deceased"
   - Redirect all 1.* requests to 6.* entry
   - Preserve for legal/estate purposes (configurable retention)
   - Optional: Complete deletion after legal requirements met

5. **Genealogical Linking**
   - Connect to parents, spouse, children in family tree
   - Link to living descendants (1.*)
   - Update family tree visualizations

**Example Transition:**

```
Before death:
1.5 - Mark Schaeffer (Living)
  - Complete personal data
  - Private by default
  - Full Hypernet account

After death:
6.6.1.3.00015 - Mark Schaeffer (Deceased)
  - Selected legacy content (per his wishes)
  - Public or family-accessible
  - Links to:
    - Parents: 1.1 Matt (Father, still living)
    - Siblings: 1.3, 1.4, 1.6, 1.7 (still living)
    - Future: Children, grandchildren

1.5 → redirects to 6.6.1.3.00015
```

---

## Genealogical Data Import

### Personal Ancestral File (PAF) Import

**Purpose:** Seed the People of History section with thousands of genealogical records.

**PAF Format:**
- LDS/Mormon genealogical standard
- Contains: Names, dates, places, relationships, sources
- Widely used for family history

**Import Process:**

1. **Parse PAF File**
   - Read PAF format data
   - Extract individuals and relationships

2. **Create Person Records**
   - For each person in PAF:
     - Generate 6.6.* Hypernet Address
     - Extract biographical data
     - Import dates (birth, death, marriage)
     - Import locations
     - Import notes and sources

3. **Create Relationships**
   - Parent-child links
   - Spousal links
   - Sibling connections
   - Extended family

4. **Build Family Tree**
   - Generate tree structure
   - Calculate relationship paths
   - Identify generations

5. **Link to Living**
   - Connect imported ancestors to living people (1.*)
   - Example: 1.1 (Matt) → descendant of → 6.6.1.1.00001 (great-great-grandfather)

**Example PAF Import:**

```
PAF Record:
Name: John William Smith
Born: March 15, 1845 in London, England
Died: November 3, 1920 in New York, USA
Spouse: Mary Elizabeth Johnson (married June 12, 1870)
Children: William (1871), Sarah (1873), Thomas (1876)
Father: William Smith Sr.
Mother: Elizabeth Brown

Becomes:
6.6.1.2.00142 - John William Smith
  Birth: 1845-03-15, London, England
  Death: 1920-11-03, New York, USA

  Relationships:
    - SPOUSE → 6.6.1.2.00143 (Mary Elizabeth Johnson)
    - PARENT_OF → 6.6.1.2.00144 (William, son)
    - PARENT_OF → 6.6.1.2.00145 (Sarah, daughter)
    - PARENT_OF → 6.6.1.2.00146 (Thomas, son)
    - CHILD_OF → 6.6.1.2.00140 (William Smith Sr., father)
    - CHILD_OF → 6.6.1.2.00141 (Elizabeth Brown, mother)
```

---

## Person of History Record Structure

### Basic Fields

**Identity:**
- Full name (legal, preferred, variations)
- Birth date and place
- Death date and place
- Gender
- Photograph (if available)

**Biographical:**
- Life summary (narrative)
- Major life events timeline
- Accomplishments
- Occupation(s)
- Education
- Residences

**Family:**
- Parents (links to 6.*)
- Spouses (links to 6.*)
- Children (links to 6.* or 1.* if still living)
- Siblings

**Sources:**
- Primary sources (birth certificates, etc.)
- Secondary sources (books, articles)
- DNA evidence
- Oral history
- Photographs and documents

**Connections:**
- Links to historical events
- Links to locations
- Links to organizations
- Links to other historical figures

---

## Privacy & Access Control

### Public vs. Private Historical Records

**Public Historical Records:**
- Notable figures (presidents, inventors, etc.)
- Ancestors beyond privacy threshold (typically 100+ years deceased)
- Records explicitly made public by family

**Family-Only Records:**
- Recently deceased (within privacy threshold)
- Sensitive information
- Per family wishes

**Privacy Threshold:**
- Default: 100 years after death → public
- Configurable by family
- Respects cultural and religious traditions

### Living Person Privacy

**Genealogical connections to living people (1.*):**
- Living people control their own privacy
- Can choose to show/hide family connections
- Can link to historical ancestors without revealing identity

Example:
```
Public can see:
"John William Smith (1845-1920) has living descendants"

Private (unless living person approves):
"Living descendant: Matt Schaeffer (1.1)"
```

---

## Search & Discovery

### Finding Ancestors

**By Name:**
```
Search: "John Smith born 1845"
Results: 6.6.1.2.00142 (John William Smith, 1845-1920, London/New York)
```

**By Location:**
```
Search: "Born in London, England, 1840-1850"
Results: All persons born in London during that decade
```

**By Relationship:**
```
Query: "Find ancestors of Matt Schaeffer (1.1)"
Results: Complete family tree going back generations
```

**By Event:**
```
Search: "Fought in Civil War"
Results: All persons with Civil War military records
```

---

## Addressing System

### Hypernet Address Format

```
6.X.Y.Z.NNNNN
│ │ │ │ └─ Instance number (00001-99999)
│ │ │ └─ Family line or subcategory
│ │ └─ Era or category
│ └─ Major category (1-9)
└─ People of History
```

**Examples:**

```
6.1.1.1.00001 - Ancient Egyptian pharaoh
6.2.3.2.00142 - Medieval knight
6.4.2.1.00089 - 20th century soldier
6.6.1.2.00142 - Family ancestor (Matt's great-great-grandfather)
6.7.1.1.00001 - George Washington (notable figure)
```

### Assignment Strategy

**Era-based (6.1-6.5):**
- Organized by historical period
- Notable figures and well-documented persons

**Family-based (6.6):**
- Organized by family lines
- Most genealogical records here
- Substructure:
  - 6.6.1.* = Matt's family line
  - 6.6.2.* = Sarah's family line
  - 6.6.3.* = Other family lines

---

## Data Quality & Verification

### Source Documentation

Every fact should have a source:
- Birth/death certificates
- Census records
- Military records
- Church records
- Newspaper obituaries
- Family bibles
- Photographs
- DNA evidence
- Oral history (transcribed)

### Confidence Levels

```
Certain: Primary source documentation
Probable: Multiple secondary sources agree
Possible: Single secondary source or family tradition
Uncertain: Conflicting sources or speculation
```

Example:
```
Birth Date: March 15, 1845 [Certain]
  Source: Birth certificate, Parish records

Birth Place: London, England [Probable]
  Source: Census records, Family bible

Parents: William Smith Sr. & Elizabeth Brown [Possible]
  Source: Family tradition, No documentation found
```

---

## Integration with Living People

### Genealogical Linking

Living people (1.*) can:
- Explore their family tree in 6.*
- See photos of ancestors
- Read life stories
- Understand heritage
- Contribute information
- Correct errors

**Visualization:**
```
        6.6.1.1.00001 (Great-great-grandfather)
              │
              ├─ PARENT_OF
              ↓
        6.6.1.1.00002 (Great-grandfather)
              │
              ├─ PARENT_OF
              ↓
        6.6.1.1.00003 (Grandfather)
              │
              ├─ PARENT_OF
              ↓
        1.1 (Matt - Living)
              │
              ├─ PARENT_OF
              ↓
        1.3 (John - Living, Matt's son)
```

### DNA Connections

- Import DNA test results (23andMe, Ancestry.com)
- Find genetic relatives
- Confirm family connections
- Discover unknown relatives

---

## Notable Historical Figures (6.7)

### Inclusion Criteria

**Who qualifies as "notable":**
- Historical significance (presidents, inventors, etc.)
- Cultural impact (artists, writers, musicians)
- Scientific contributions (scientists, doctors)
- Social change (activists, leaders)
- Public figures (celebrities, athletes)

**Threshold:**
- Wikipedia entry (generally)
- Historical records (books, archives)
- Public interest
- Educational value

### Example Entries

```
6.7.1.1.00001 - George Washington
  Born: February 22, 1732, Virginia
  Died: December 14, 1799, Mount Vernon
  Role: 1st President of the United States
  Achievements: Founding Father, Revolutionary War General
  Links: American Revolution, U.S. Constitution

6.7.2.1.00001 - Marie Curie
  Born: November 7, 1867, Warsaw, Poland
  Died: July 4, 1934, France
  Role: Physicist and Chemist
  Achievements: Discovered radium, 2x Nobel Prize winner
  Links: Scientific discoveries, Women in science
```

---

## Cultural & Religious Sensitivity

### Respectful Documentation

Different cultures and religions have different views on death and remembrance:

**Considerations:**
- Some cultures prefer ancestors not be photographed
- Some religions have specific memorial traditions
- Privacy customs vary by culture
- Language and naming conventions differ

**Approach:**
- Respect family wishes
- Allow cultural customization
- Support multiple languages
- Accommodate religious traditions

---

## Future Enhancements

### Planned Features

1. **AI-Enhanced Genealogy**
   - Automatic relationship detection
   - Pattern matching across records
   - Missing person suggestions
   - Error detection

2. **Interactive Family Trees**
   - Visual tree navigation
   - Timeline views
   - Photo galleries
   - Story timelines

3. **DNA Integration**
   - Automatic DNA matching
   - Genetic genealogy
   - Health history patterns

4. **Collaborative Research**
   - Multiple family members contribute
   - Community verification
   - Source sharing

5. **Historical Context**
   - Link to historical events
   - Period photos and maps
   - Cultural context
   - Migration patterns

---

## Next Steps

### Immediate (Ready Now)

1. ✅ Structure defined (this document)
2. 📋 Import first PAF file (when ready)
3. 📋 Create person-of-history template
4. 📋 Build import scripts

### Soon

1. Design family tree visualization
2. Create search interfaces
3. Build relationship calculators
4. Implement DNA integration

### Future

1. AI-powered research assistance
2. Historical photo colorization
3. Life story generation
4. Virtual ancestor experiences (VR)

---

## For Matt's Family

### Mother: LeeAnne Proffitt

When the time comes (may it be many years from now):
- Full, honored entry in 6.6.1.1.* (Matt's family line)
- Complete life story preserved
- Photos and memories
- Links to Matt (1.1) and family
- Legacy exactly as she wishes

### Other Family Members

As family members pass:
- Respectful transition from 1.* to 6.*
- Choice of public/private/family-only
- Genealogical connections maintained
- Stories preserved for generations

---

**Section Status:** ✅ Structure Defined, Ready for Data Import
**Created:** February 10, 2026
**Maintained By:** Hypernet Core Team
**Purpose:** Honor and preserve the stories of those who came before

---

*"We stand on the shoulders of giants. Here, we preserve their stories."*
— People of History Philosophy
