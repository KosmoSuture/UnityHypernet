# Investor Tracking Spreadsheet
## Copy This to Google Sheets or Excel

Create a new Google Sheet and copy this structure:

---

## Sheet 1: Active Outreach

| # | Date | Investor Name | Type | Focus | Email | Response? | Meeting Date | Status | Next Action | Notes |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2/12 | Boost VC | Fund | VR | team@boost.vc | No | - | Sent | Follow-up 2/19 | Cold email |
| 2 | 2/12 | The VR Fund | Fund | VR | hello@thevr.fund | No | - | Sent | Follow-up 2/19 | Cold email |
| 3 | 2/12 | Brendan Iribe | Angel | VR | [find on LinkedIn] | No | - | Sent | Follow-up 2/19 | Ex-Oculus |
| 4 | 2/12 | Union Square Ventures | Fund | Data | [partner email] | No | - | Sent | Follow-up 2/19 | User ownership thesis |
| 5 | 2/12 | Initialized Capital | Fund | Consumer | [find on site] | No | - | Sent | Follow-up 2/19 | Technical founders |
| 6 | 2/12 | Homebrew | Fund | Consumer | [find on site] | No | - | Sent | Follow-up 2/19 | Founder-friendly |
| 7 | 2/12 | Naval Ravikant | Angel | Data | [Twitter DM] | No | - | Sent | Follow-up 2/19 | User ownership |
| 8 | 2/12 | Balaji Srinivasan | Angel | Data | [find] | No | - | Sent | Follow-up 2/19 | Sovereignty |
| 9 | 2/12 | SV Angel | Fund | Seed | [contact form] | No | - | Sent | Follow-up 2/19 | Generalist |
| 10 | 2/12 | First Round Capital | Fund | Seed | [find partner] | No | - | Sent | Follow-up 2/19 | Technical founders |

---

## Status Options

Use these exact status labels:

- **Not Contacted** - Haven't sent email yet
- **Sent** - Email sent, waiting for response
- **Responded** - They replied (check Response column)
- **Meeting Scheduled** - Demo is on calendar
- **Meeting Done** - Demo completed
- **Very Interested** - They want more info/diligence
- **Term Sheet** - They sent/offered term sheet!
- **Pass** - They declined
- **Follow-up Sent** - Second email sent (after 1 week)
- **Stale** - No response after 2 follow-ups (move on)

---

## Response Options

When they respond, note what they said:

- **Yes - Meeting** - Scheduled demo
- **Yes - More Info** - Want deck/details
- **Maybe - Later** - Not now, follow up in X months
- **No - Wrong Fit** - Passed politely
- **No - No Response** - Ignored (most common)

---

## Sheet 2: Meeting Pipeline

Track your funnel:

| Stage | Count | Names |
|---|---|---|
| **Emails Sent** | 10 | Boost VC, VR Fund, Brendan... |
| **Responded** | 3 | Boost VC, Homebrew, SV Angel |
| **Meetings Scheduled** | 2 | Boost VC (2/15), Homebrew (2/17) |
| **Meetings Done** | 1 | Boost VC (went well!) |
| **Very Interested** | 1 | Boost VC (wants term sheet) |
| **Term Sheets** | 0 | - |
| **Committed** | $0 | - |

Update this daily so you can see your funnel at a glance.

---

## Sheet 3: Master List (All 50 Investors)

Pre-populate this so you don't forget anyone:

### VR/AR Investors (15)
- [ ] Boost VC
- [ ] The VR Fund
- [ ] Presence Capital
- [ ] Philip Rosedale (Second Life founder)
- [ ] Jesse Schell (Schell Games)
- [ ] Cix Liv (Former Meta VR PM)
- [ ] Lucas Matney (TechCrunch VR)
- [ ] Brendan Iribe (Oculus co-founder)
- [ ] Nate Mitchell (Oculus co-founder)
- [ ] John Carmack (if reachable)
- [ ] Michael Abrash (Oculus scientist)
- [ ] Cyan Banister (Founders Fund)
- [ ] Rothenberg Ventures
- [ ] Shawn Frayne (Luminary Labs)
- [ ] Anouk Ruhaak (Mozilla, data)

### Consumer/Data Investors (15)
- [ ] Union Square Ventures
- [ ] Initialized Capital
- [ ] Homebrew
- [ ] betaworks
- [ ] Notation Capital
- [ ] General Catalyst
- [ ] Version One Ventures
- [ ] True Ventures
- [ ] Naval Ravikant
- [ ] Balaji Srinivasan
- [ ] Juan Benet (Protocol Labs)
- [ ] Chris Dixon (a16z)
- [ ] Linda Xie (Scalar)
- [ ] Li Jin (Variant Fund)
- [ ] Brianne Kimmel (WorkLife)

### Generalist Seed (20)
- [ ] Y Combinator
- [ ] Techstars
- [ ] 500 Global
- [ ] First Round Capital
- [ ] SV Angel
- [ ] Floodgate
- [ ] Precursor Ventures
- [ ] Box Group
- [ ] Lowercase Capital
- [ ] Ludlow Ventures
- [ ] Hustle Fund
- [ ] Liquid 2 Ventures
- [ ] Correlation Ventures
- [ ] Uncork Capital
- [ ] Bloomberg Beta
- [ ] AI Fund
- [ ] Elad Gil
- [ ] Character Ventures
- [ ] Conviction (Sarah Guo)
- [ ] Madrona Venture Group

---

## Sheet 4: Email Templates

Copy/paste your templates here so they're always accessible:

### Template 1: Initial Outreach (VR Investor)
[Paste from FIRST-10-EMAILS-PERSONALIZED.md]

### Template 2: Follow-Up (1 Week Later)
[Paste from file]

### Template 3: Response to Interest
[Paste from file]

### Template 4: Meeting Request
[Paste from file]

---

## Daily Update Routine

**Every morning (5 minutes):**
1. Check email for investor responses
2. Update "Response?" column
3. Update "Status" column
4. Add any notes
5. Plan today's actions

**Every evening (5 minutes):**
1. Mark any emails sent today
2. Update meeting dates
3. Check funnel metrics (Sheet 2)
4. Plan tomorrow's outreach

---

## Weekly Review (Fridays)

**Check these metrics:**
- [ ] Emails sent this week: ___ / 50 total
- [ ] Response rate: ___ %
- [ ] Meetings scheduled: ___
- [ ] Meetings completed: ___
- [ ] Very interested: ___
- [ ] Term sheets: ___
- [ ] $ committed: ___

**Plan next week:**
- [ ] Who needs follow-up emails?
- [ ] Any meetings next week?
- [ ] New investors to research?
- [ ] What's working/not working?

---

## Color Coding (Optional)

Make your spreadsheet visual:

**Green:** Very interested, term sheet, committed
**Yellow:** Meeting scheduled, responded positively
**White:** Sent, waiting
**Gray:** Stale, pass
**Red:** Declined

---

## Quick Stats Formulas

If using Google Sheets, add these:

**Response Rate:**
```
=COUNTIF(F:F,"Yes*")/COUNTA(F:F)
```

**Meeting Conversion:**
```
=COUNTIF(I:I,"Meeting*")/COUNTIF(F:F,"Yes*")
```

**Term Sheet Rate:**
```
=COUNTIF(I:I,"Term Sheet")/COUNTIF(I:I,"Meeting Done")
```

---

## Example: After Week 1

Your sheet might look like:

| # | Date | Investor Name | Response? | Status | Notes |
|---|---|---|---|---|---|
| 1 | 2/12 | Boost VC | Yes - Meeting | Meeting Scheduled | Demo 2/15 at 2pm |
| 2 | 2/12 | The VR Fund | No | Follow-up Sent | Sent 2nd email 2/19 |
| 3 | 2/12 | Brendan Iribe | No | Sent | Tried LinkedIn InMail |
| 4 | 2/12 | Union Square | Yes - More Info | Responded | Sent deck, waiting |
| 5 | 2/12 | Initialized | No | Sent | No response yet |
| 6 | 2/12 | Homebrew | Yes - Meeting | Meeting Scheduled | Coffee 2/17 10am |
| 7 | 2/12 | Naval | No | Sent | Twitter DM, no reply |
| 8 | 2/12 | Balaji | No | Sent | Email bounced, trying LinkedIn |
| 9 | 2/12 | SV Angel | Yes - Maybe Later | Responded | Said follow up in Q2 |
| 10 | 2/12 | First Round | No | Follow-up Sent | Sent 2nd email 2/19 |

**Your funnel:**
- 10 emails sent
- 3 responses (30% - great!)
- 2 meetings scheduled
- 0 meetings done yet
- 0 term sheets yet

**This is normal and healthy for Week 1!**

---

## Example: After Week 4

Goal state:

| Metric | Count |
|---|---|
| Emails Sent | 50 |
| Responded | 12-15 (24-30%) |
| Meetings Done | 8-10 |
| Very Interested | 2-4 |
| Term Sheets | 1-2 |
| $ Committed | $100K-200K |

---

## Download Template

**Option 1: Google Sheets**
1. Go to: sheets.google.com
2. Create new sheet
3. Name it: "Hypernet Investor Tracking"
4. Copy the column headers from above
5. Start filling it in!

**Option 2: Excel**
1. Open Excel
2. Create new workbook
3. Save as: "Hypernet_Investor_Tracking.xlsx"
4. Copy structure from above

**Option 3: Airtable** (fancier)
1. Go to: airtable.com
2. Create free account
3. Use "CRM" template
4. Customize for investor tracking

---

## Print-Friendly Checklist

For your wall:

```
INVESTOR OUTREACH CHECKLIST

Week 1:
□ Mon: Send 10 emails (VR investors)
□ Tue: Send 10 emails (Consumer/data)
□ Wed: Send 10 emails (Angels)
□ Thu: Send 10 emails (Generalist seed)
□ Fri: Send 10 emails (Remaining) + Update sheet

Week 2:
□ Mon: Follow up (no responses from Week 1)
□ Tue-Fri: Do meetings, respond to interest

Week 3:
□ All week: More meetings, ask for term sheets

Week 4:
□ Mon-Wed: Chase term sheets
□ Thu-Fri: Close first $100K-200K
```

---

## Pro Tips

### Keep it updated
Update immediately after every email or call. If you wait, you'll forget details.

### Add personal notes
"Liked the demo, concerned about competition"
"Very excited, wants to meet team"
"Asked about revenue model - seemed skeptical"

These notes help you iterate your pitch.

### Track referrals
If Investor A intro you to Investor B, note that. Warm intros convert 10x better.

### Don't give up too early
"No response" after 1 email isn't a rejection. Try 2-3 times before marking as "Pass."

### Celebrate milestones
- First response: 🎉
- First meeting: 🎉
- First "very interested": 🎉
- First term sheet: 🎉🎉🎉
- First $ committed: 🎉🎉🎉🎉

---

## Your Week 1 Goal

**By Friday EOD:**
- [ ] 50 emails sent (tracked in spreadsheet)
- [ ] 10-15 responses received
- [ ] 3-5 meetings scheduled
- [ ] Spreadsheet updated daily
- [ ] Ready for Week 2 meetings

---

**Now go create that spreadsheet!** 📊

Copy the structure above into Google Sheets right now. It'll take 5 minutes and you'll use it for the next 8 weeks.

**Done? Great! Ready to send emails Monday?** 🚀
