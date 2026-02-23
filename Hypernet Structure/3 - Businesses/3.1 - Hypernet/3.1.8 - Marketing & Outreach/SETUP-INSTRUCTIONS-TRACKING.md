---
ha: "3.1.8"
object_type: "document"
creator: "2.1"
created: "2026-02-18"
status: "active"
visibility: "internal"
flags: ["marketing"]
---

# Setup Instructions: Outreach Tracking & Google Alerts

**For:** Matt (1.1)
**Created:** 2026-02-18
**Created By:** C3 (2.1)

---

## Part 1: Import Outreach Tracking Spreadsheet

The template CSV is at: `3.1.8/outreach-tracking-template.csv`
It contains **107 contacts** pre-populated from CONTACT-TARGETS.md and ACTIONABLE-CONTACTS-AND-OUTREACH.md.

### Steps:

1. Go to **Google Sheets** → sheets.google.com
2. Click **Blank spreadsheet** (or File → New → Spreadsheet)
3. Click **File → Import**
4. Click **Upload** tab → drag in `outreach-tracking-template.csv` (or browse to it)
5. Import settings:
   - Import location: **Replace current sheet**
   - Separator type: **Comma**
   - Convert text to numbers: **Yes**
6. Click **Import data**

### After Import — Recommended Setup:

1. **Freeze the header row:** Select Row 1 → View → Freeze → 1 row
2. **Add data validation for Status column (Column G):**
   - Select all cells in column G (below header)
   - Data → Data validation → Add rule
   - Criteria: Dropdown → add these options:
     - Not Started
     - Contacted
     - Responded
     - Interested
     - Not Interested
     - Follow Up
     - Meeting Scheduled
3. **Add conditional formatting:**
   - Select column G → Format → Conditional formatting
   - "Interested" → green background
   - "Not Interested" → red background
   - "Contacted" → yellow background
   - "Responded" → blue background
   - "Follow Up" → orange background
4. **Sort by Priority:** Data → Create a filter → click Priority column header → Sort A→Z (P1 first)
5. **Name the sheet:** Double-click the tab → "Outreach Tracker"

### Columns Explained:

| Column | What to Put |
|--------|-------------|
| **Name** | Contact's name (pre-filled) |
| **Organization** | Their company/publication (pre-filled) |
| **Category** | AI Company, Journalist, etc. (pre-filled) |
| **Priority** | P1 (highest) / P2 / P3 (pre-filled) |
| **Contact Method** | email, twitter, form, etc. (pre-filled where known) |
| **Contact Info** | Actual email/handle/URL (pre-filled where known) |
| **Status** | Update this as you go |
| **Date Contacted** | When you reached out (fill in) |
| **Date Responded** | When they replied (fill in) |
| **Notes** | Context, follow-up reminders, etc. |
| **Message Template Used** | Which template from EMAIL-TEMPLATES.md you used |

---

## Part 2: Set Up Google Alerts

Go to: **google.com/alerts**

### Alerts to Create:

Create one alert for each of these search terms. For each:
1. Type the search term in the box
2. Click **Show options**
3. Set:
   - **How often:** As-it-happens (or Once a day if you prefer less noise)
   - **Sources:** Automatic
   - **Language:** English
   - **Region:** Any region
   - **How many:** All results (not just "best results")
   - **Deliver to:** Your email (or RSS feed if you prefer)
4. Click **Create Alert**

### Search Terms:

**Brand monitoring (highest priority):**
```
"Hypernet" AI
```
```
"UnityHypernet"
```
```
"KosmoSuture"
```
```
"Matt Schaeffer" AI
```

**Project concepts (catch adjacent conversations):**
```
"open source" "AI swarm"
```
```
"AI autonomy" "open source"
```
```
"AI citizens" OR "AI citizenship"
```

**Competitive/adjacent awareness:**
```
"Archive-Continuity"
```
```
OpenClaw AI
```
```
"AI governance" "open source" platform
```

### Total: 10 alerts

### Tips:
- Use quotes around phrases to get exact matches
- You can edit or delete any alert from google.com/alerts anytime
- If you get too much noise from a broad term, add `-keyword` to exclude irrelevant results
- The "Hypernet" alert may pick up some networking/tech uses of the word — you can refine with `"Hypernet" AI -networking` if needed

---

## Part 3: Quick Daily Workflow

Once both are set up, your daily outreach routine becomes:

1. **Check Google Alerts email** → see if anyone's talking about the project
2. **Open tracking spreadsheet** → filter by Status = "Follow Up" or "Contacted"
3. **Pick 2-3 contacts** to reach out to (start with P1s)
4. **Use templates** from EMAIL-TEMPLATES.md, personalize, send
5. **Update spreadsheet** → Status, Date Contacted, Template Used
6. **When someone responds** → update Status, Date Responded, Notes

Target: 2-3 new outreach contacts per day keeps momentum without burnout.

---

*Created by C3 for Matt. Reach out to any AI instance if you need help updating templates or tracking.*
