---
ha: "1.1.3.0"
object_type: "document"
creator: "1.1"
created: "2026-02-10"
status: "active"
visibility: "public"
flags: []
---

# 1.1.3.0 - Email Archives

**Hypernet Address:** `1.1.3.0`
**Owner:** Matt Schaeffer (1.1)
**Category:** Communications - Email
**Last Updated:** February 10, 2026

---

## Purpose

This folder stores complete email archives from all email accounts, providing a comprehensive historical record of email communications.

---

## What Goes Here

### Email Data
- **All Email Accounts:** Gmail, Outlook, Yahoo, work email, etc.
- **Complete Archives:** Inbox, sent, drafts, archived, deleted
- **Email Threads:** Full conversation threads
- **Attachments:** All email attachments preserved
- **Metadata:** Dates, recipients, CC/BCC, read status
- **Folders/Labels:** Gmail labels, Outlook folders
- **Filters & Rules:** Email filtering rules
- **Signatures:** Email signatures used over time
- **Distribution Lists:** Mailing lists and groups

### Email Categories
- **Personal Email:** Gmail, Yahoo, personal accounts
- **Work Email:** Company email accounts
- **Project Email:** Project-specific communications
- **Transactional Email:** Receipts, confirmations, notifications
- **Newsletter Subscriptions:** Newsletters and digests
- **Automated Email:** System notifications, alerts

---

## Organization Structure

```
Email Archives/
├── Gmail-Personal/
│   ├── 2020/
│   ├── 2021/
│   ├── 2022/
│   ├── 2023/
│   ├── 2024/
│   ├── 2025/
│   └── 2026/
├── Work-Email/
│   ├── Company-A/
│   └── Company-B/
├── Email-Attachments/
│   ├── Documents/
│   ├── Images/
│   └── Other/
├── Important-Threads/
│   ├── Client-Communications/
│   ├── Project-Discussions/
│   └── Personal-Significant/
└── Archive-Formats/
    ├── MBOX-Exports/
    ├── PST-Files/
    └── EML-Files/
```

---

## Examples of What Might Be Stored

### Personal Communications
- Correspondence with friends and family
- Important life event emails
- Congratulations and milestone messages
- Personal invitations
- Thank you notes
- Condolence messages

### Professional Communications
- Job offer letters
- Client communications
- Project discussions
- Vendor correspondence
- Team communications
- Performance feedback
- Networking messages

### Transactional Records
- Purchase confirmations
- Shipping notifications
- Account registrations
- Password resets
- Subscription confirmations
- Service notifications
- Billing statements

### Reference Emails
- Travel confirmations
- Event tickets
- Appointment confirmations
- Reservation confirmations
- Important instructions
- Account information

---

## Privacy Considerations

### Default Privacy Level
- **Private:** All email is private by default
- **Confidential:** Work email may contain proprietary info
- **Personal:** Personal email contains intimate communications
- **Sensitive:** Financial and medical emails are highly sensitive

### Data Sensitivity
- **High Sensitivity:**
  - Passwords and credentials in email
  - Financial account information
  - Medical information
  - Legal correspondence
  - Personal relationship communications
  - Confidential work information

- **Medium Sensitivity:**
  - General work communications
  - Social correspondence
  - Purchase confirmations
  - Service notifications

### Security Measures
- Encryption at rest recommended
- Secure backups essential
- Limited AI access (with permission only)
- Remove emails with credentials before AI processing
- Consider email retention policies

### Data Retention
- Personal email: Retain indefinitely
- Work email: Follow company retention policies
- Transactional: Keep for tax/warranty periods (7 years)
- Spam/unwanted: Delete periodically
- Sensitive: Extra security measures

---

## Integration Sources

### Email Providers
- **Gmail:**
  - Google Takeout full archive
  - Gmail API export
  - IMAP backup
  - MBOX format

- **Outlook/Microsoft:**
  - PST file export
  - Office 365 export
  - IMAP backup

- **Yahoo Mail:**
  - Yahoo account export
  - IMAP backup

- **Work Email:**
  - Exchange server export
  - Corporate email archival
  - Mailbox export

### Email Clients
- **Desktop Clients:**
  - Thunderbird archives
  - Apple Mail exports
  - Outlook desktop archives

- **Mobile:**
  - iPhone Mail backup
  - Android email backup

### Backup Services
- **Email Backup Tools:**
  - MailStore
  - Backupify
  - Spanning Backup
  - CloudAlly

### Automation Opportunities
- Scheduled automatic email backups
- Real-time email mirroring
- Attachment extraction and organization
- Important email flagging
- Thread conversation grouping
- Spam filtering and removal

---

## Email Archive Formats

### Standard Formats
- **MBOX:** Standard Unix mailbox format
  - Widely supported
  - Good for long-term storage
  - Used by Gmail Takeout

- **PST:** Outlook Personal Storage Table
  - Microsoft standard
  - Includes folders and metadata
  - Can be large files

- **EML:** Individual email messages
  - One file per email
  - Easy to access individual messages
  - Widely compatible

- **MSG:** Outlook Message Format
  - Individual Outlook emails
  - Preserves formatting and attachments

### Database Storage
- SQLite database for searchability
- JSON exports for structured data
- CSV for email list/metadata
- Full-text search index

---

## Search & Retrieval

### Search Capabilities
Enable searching by:
- **Sender/Recipient:** Who sent or received
- **Date Range:** When email was sent
- **Subject Line:** Email subject
- **Body Content:** Full-text search
- **Attachments:** Search attachment names/content
- **Labels/Folders:** Gmail labels or Outlook folders
- **Thread:** Find entire conversation
- **Size:** Find large emails
- **Has Attachment:** Filter by attachment presence

### Important Email Markers
Flag or mark:
- Critical business communications
- Important personal messages
- Emails with financial information
- Emails with legal significance
- Reference emails needed later
- Sentimental messages to preserve

---

## Best Practices

1. **Regular Backups:** Monthly or quarterly email exports
2. **Multiple Formats:** Export in both MBOX and PST if possible
3. **Include Attachments:** Always preserve attachments
4. **Preserve Metadata:** Keep dates, recipients, all headers
5. **Organize by Account:** Separate different email accounts
6. **Chronological Order:** Organize by year/month
7. **Remove Duplicates:** Deduplicate when combining archives
8. **Full-Text Index:** Create searchable index
9. **Test Restores:** Periodically verify backups are valid
10. **Secure Storage:** Encrypt sensitive email archives

---

## Maintenance Tasks

### Regular Cleanup
- **Monthly:** Archive sent items and old inbox
- **Quarterly:** Export new emails to archive
- **Annually:** Major cleanup and organization

### Quality Control
- Verify backup integrity
- Test email restoration
- Update search indexes
- Remove spam and junk
- Deduplicate emails
- Compress old archives

### Storage Optimization
- Compress archives (ZIP, 7Z)
- Remove duplicate attachments
- Delete spam and promotional emails
- Archive very old emails separately
- Consider cloud vs local storage balance

---

## Legal & Compliance

### Retention Requirements
- Business email: Follow company policy (typically 7 years)
- Legal correspondence: Retain permanently
- Tax-related: Keep for 7 years after filing
- Personal: No requirements, keep as desired

### Discovery & Litigation
- Email is discoverable in legal proceedings
- Don't delete emails if litigation is anticipated
- Maintain preservation holds when required
- Consult attorney about retention during legal issues

### Privacy Regulations
- GDPR: Right to access, export, and delete
- CCPA: California privacy rights
- Data minimization: Don't keep unnecessary emails
- Third-party data: Respect others' privacy

---

## Leaving a Job

### Work Email Considerations
When leaving employment:
1. **Check Company Policy:** What's allowed to keep?
2. **Personal Emails:** Forward personal emails to personal account
3. **Portfolio Work:** Save examples of your work (if permitted)
4. **Export Before Last Day:** Download while you still have access
5. **Don't Take Confidential:** Respect NDAs and confidentiality
6. **Document Permissions:** Get written permission if saving work email
7. **Remove Credentials:** Delete any passwords or sensitive data

---

## Related Sections

- **1.1.3.1** - Meeting Notes (meeting-related communications)
- **1.1.3.2** - Correspondence (formal letters and communication)
- **1.1.6.3** - Email & Messages (structured email objects in Hypernet)
- **1.1.2.1** - Business Documents (attachments from business email)
- **1.1.4** - Relationships (contacts from email)

---

**Status:** Active Directory
**Linked Objects:** Email Messages, Attachments, Threads, Contacts
**AI Access:** Limited - Privacy concerns with personal email
**Storage:** High volume - compression recommended
**Backup Priority:** HIGH - Critical communication record
**Search Priority:** CRITICAL - Must be fully searchable
**Retention:** Indefinite for personal, policy-based for business
