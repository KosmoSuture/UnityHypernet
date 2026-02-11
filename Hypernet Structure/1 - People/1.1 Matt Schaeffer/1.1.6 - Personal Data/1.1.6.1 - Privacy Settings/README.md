# 1.1.6.1 - Privacy Settings

**Hypernet Address:** `1.1.6.1`
**Owner:** Matt Schaeffer (1.1)
**Category:** Personal Data - Privacy Settings
**Last Updated:** February 10, 2026

---

## Purpose

This folder stores all privacy settings, preferences, and configurations that control who can access your personal data and how it can be used.

---

## What Goes Here

### Privacy Configuration
- **Privacy Level Defaults:** Default privacy for new data
- **Category Privacy Settings:** Privacy by data type
- **Sharing Rules:** Who can see what
- **AI Access Permissions:** Which AI companies can access what
- **Legacy Access:** Post-death data access rules
- **Data Retention Policies:** How long to keep data
- **Encryption Settings:** Encryption preferences
- **Audit Log Preferences:** What to log and for how long

### Privacy Levels

#### 1. Private (Default)
- **Access:** Only you
- **Visibility:** Hidden from everyone else
- **AI Access:** None (unless explicitly granted)
- **Use Cases:** Sensitive personal data, private thoughts, confidential information
- **Examples:** Medical records, financial details, personal journals

#### 2. Family
- **Access:** You + designated family members
- **Visibility:** Only specified family
- **AI Access:** Configurable per family member's AI usage
- **Use Cases:** Family photos, shared calendars, family documents
- **Examples:** Family vacation photos, shared grocery lists, family medical history

#### 3. Friends
- **Access:** You + designated friends
- **Visibility:** Only specified friends
- **AI Access:** Configurable
- **Use Cases:** Social content, shared interests
- **Examples:** Party photos, group event planning, shared playlists

#### 4. Professional
- **Access:** You + professional network (limited)
- **Visibility:** Professional contacts only
- **AI Access:** Limited to work-related AI
- **Use Cases:** Work portfolio, professional accomplishments
- **Examples:** Resume, portfolio pieces, professional blog posts

#### 5. Public
- **Access:** Anyone (use sparingly)
- **Visibility:** Publicly discoverable
- **AI Access:** May be used for AI training
- **Use Cases:** Public-facing content, marketing materials
- **Examples:** Published articles, public speaking videos, open-source contributions

#### 6. Legacy
- **Access:** Designated persons after your death
- **Visibility:** Per your legacy instructions
- **AI Access:** Per your legacy settings
- **Use Cases:** Digital inheritance, memorial content
- **Examples:** Letters to loved ones, digital asset access, family history

---

## Privacy by Data Type

### Default Privacy Settings by Category

**Photos & Videos:**
- Personal/Family: Family
- Events: Friends
- Professional: Professional
- Public speaking: Public

**Email & Messages:**
- All email: Private
- Work email: Private (work-owned)
- Personal messages: Private

**Financial Data:**
- Bank accounts: Private
- Transactions: Private
- Budgets: Private
- Investment portfolio: Private

**Health Data:**
- Medical records: Private
- Fitness data: Private
- Medications: Private
- Health metrics: Private (or Family if sharing)

**Documents:**
- Personal: Private
- Business: Private or Professional (case-by-case)
- Legal: Private
- Reference: Private

**Social Media:**
- Posts: Public or Friends (as originally posted)
- DMs: Private
- Profile data: Friends or Public

**Location Data:**
- Location history: Private
- Check-ins: Friends (if shared originally)
- Travel itineraries: Family or Friends

**Tasks & Calendar:**
- Personal tasks: Private
- Work tasks: Private
- Shared calendars: Family or Professional
- Public events: Public

**Contacts:**
- All contacts: Private
- Relationship notes: Private

**Notes:**
- Personal notes: Private
- Work notes: Private
- Shared notes: Per sharing settings

---

## AI Access Permissions

### Granular AI Control

**AI Company Permissions:**
- Anthropic (Claude): [Access level]
- OpenAI (ChatGPT): [Access level]
- Google (Gemini): [Access level]
- Microsoft (Copilot): [Access level]
- Others: [Access level]

**Access Levels:**
1. **No Access:** AI cannot see or access this data
2. **Query Only:** AI can answer questions but not train on data
3. **Limited Analysis:** AI can analyze but not store or train
4. **Full Access:** AI can access and use for training (with restrictions)

**Data Type AI Permissions:**
- Photos: No Access (too personal)
- Documents: Query Only (help find, don't train)
- Email: No Access (private communication)
- Calendar: Query Only (help schedule, don't train)
- Tasks: Query Only (help prioritize, don't train)
- Financial: No Access (never share financial data)
- Health: No Access (HIPAA-sensitive)
- Location: No Access (security risk)
- Social Media: Limited Analysis (already public)
- Notes: No Access (private thoughts)

### AI Training Opt-Out
- **Global Opt-Out:** Exclude all data from AI training
- **Selective Opt-In:** Only specific data can be used for training
- **Anonymization Required:** If used, must be anonymized
- **Audit Rights:** Right to know how data was used

---

## Sharing Rules

### Individual Sharing
Grant access to specific people for specific data:

**Example:**
```
Photo Album: "Europe Vacation 2025"
- Shared with: Sarah Johnson (friend)
- Permission: View only
- Expiration: Never
- Can download: Yes
- Can share: No
```

### Group Sharing
Create groups for easier sharing:

**Family Group:**
- Members: Spouse, Children, Parents
- Default access: View all family photos/videos
- Can add to shared calendar
- Can see family documents

**Work Team Group:**
- Members: Team members
- Access: Project documents and files
- Can edit: Collaborative documents
- Expires: When leave team

### Link Sharing
Generate shareable links:
- Password-protected
- Expiration date
- View count limit
- Download enabled/disabled
- Can be revoked anytime

---

## Privacy Preferences

### Communication Privacy
- **Email Tracking:** Block read receipts
- **Link Tracking:** Strip tracking parameters
- **Profile Visibility:** Control who sees your profile
- **Activity Status:** Show/hide online status
- **Read Receipts:** Send/don't send read receipts

### Data Collection Privacy
- **Analytics:** Opt in/out of usage analytics
- **Crash Reports:** Send/don't send crash reports
- **Feature Usage:** Share/don't share feature usage data
- **Performance Data:** Share/don't share performance metrics

### Third-Party Privacy
- **Integration Permissions:** Control third-party access
- **API Access:** Manage API keys and access
- **Export Permissions:** Who can export your data
- **Sync Services:** Control what syncs where

---

## Encryption Settings

### Encryption Options
- **End-to-End Encryption:** For maximum security categories
- **At-Rest Encryption:** All data encrypted when stored
- **In-Transit Encryption:** All data encrypted during transmission
- **Zero-Knowledge:** Hypernet can't decrypt your data
- **Local-Only Option:** Keep certain data on local device only

### Encryption Keys
- **Master Key:** Your master encryption key
- **Key Recovery:** Secure key recovery options
- **Key Rotation:** Periodic key rotation schedule
- **Key Escrow:** Optional key escrow for recovery
- **Multi-Factor:** Require MFA for key access

---

## Data Retention Policies

### Retention Rules
**Financial Data:**
- Retain: 7 years (tax purposes)
- After 7 years: Archive or delete

**Health Records:**
- Retain: Permanently
- Medical history important for future care

**Photos & Videos:**
- Retain: Permanently
- Memories to preserve forever

**Email:**
- Personal: Retain indefinitely
- Work: Follow company policy
- Spam: Delete after 30 days

**Social Media:**
- Posts: Retain indefinitely
- Deleted posts: Permanently delete after 90 days

**Location History:**
- Retain: 2 years
- Older: Aggregate to monthly summary

**Web Browsing:**
- Retain: 90 days
- Older: Delete unless bookmarked

### Auto-Deletion Rules
- Temporary files: Delete after 30 days
- Duplicate files: Deduplicate and remove copies
- Low-quality photos: Suggest deletion
- Spam messages: Auto-delete after 7 days
- Unused data: Flag for review after 1 year

---

## Audit Logging

### What's Logged
- **Access Logs:** Who accessed what and when
- **Modification Logs:** What was changed and by whom
- **Sharing Logs:** What was shared with whom
- **Export Logs:** What was exported and when
- **Deletion Logs:** What was deleted and when
- **Login Logs:** Login attempts and success/failure
- **Permission Changes:** Privacy setting modifications

### Audit Log Retention
- **Active Logs:** Last 90 days (detailed)
- **Archive Logs:** 2 years (summary)
- **Security Events:** 7 years (compliance)
- **Deletion Logs:** Permanent (audit trail)

### Audit Alerts
- **Unusual Access:** Alert on access from new location
- **Bulk Export:** Alert on large data exports
- **Permission Changes:** Alert on privacy changes
- **Failed Logins:** Alert on multiple failed attempts
- **New Device:** Alert on access from new device

---

## Privacy Compliance

### Regulatory Compliance
- **GDPR (EU):** Right to access, export, delete
- **CCPA (California):** California privacy rights
- **HIPAA (Health):** Health data privacy protections
- **COPPA (Children):** Children's privacy protections
- **SOC 2:** Security and privacy standards

### Your Rights
- **Right to Access:** View all your data
- **Right to Export:** Download all your data
- **Right to Delete:** Permanently delete data
- **Right to Rectify:** Correct inaccurate data
- **Right to Restrict:** Limit processing of data
- **Right to Object:** Object to certain uses
- **Right to Portability:** Move data to other platforms

---

## Legacy Access Planning

### After Death Provisions
**Digital Executor:**
- Designate person to manage digital assets after death
- Provide access instructions
- Specify what to preserve vs delete
- Memorial account options

**Legacy Access Levels:**
- **Full Access:** Executor gets complete access
- **Limited Access:** Specific data only
- **Memorial Only:** Create memorial, no data access
- **Delete All:** Permanently delete all data

**Instructions:**
- Letters to loved ones
- Important information location
- Account access details
- What to share publicly
- What to keep private
- Deletion requests

---

## Best Practices

1. **Review Regularly:** Review privacy settings quarterly
2. **Default Private:** Make new data private by default
3. **Least Privilege:** Grant minimum access necessary
4. **Audit Access:** Review who has access to what
5. **Revoke Unused:** Remove access that's no longer needed
6. **Strong Passwords:** Use unique, strong passwords
7. **Enable MFA:** Multi-factor authentication everywhere
8. **Careful Sharing:** Think before sharing
9. **Monitor Logs:** Check audit logs for unusual activity
10. **Update Legacy:** Keep legacy access plan current

---

## Privacy Review Checklist

### Quarterly Privacy Review
- [ ] Review all shared data and permissions
- [ ] Check AI access permissions
- [ ] Verify encryption settings
- [ ] Review audit logs for unusual activity
- [ ] Update legacy access plan if needed
- [ ] Remove access for inactive contacts
- [ ] Review retention policies
- [ ] Check for data that should be deleted
- [ ] Verify backup and export settings
- [ ] Test account recovery process

---

## Related Sections

- **1.1.6.0** - Hypernet Data Store (data being protected)
- **1.1.6.2** - Data Permissions (granular access control)
- **1.1.2.2** - Legal Documents (estate planning and legacy)
- **1.1.10** - Passwords & Credentials (authentication security)

---

**Status:** Active Configuration
**Review Frequency:** Quarterly recommended
**Default Stance:** Private and secure
**User Control:** Complete control over all privacy settings
**Compliance:** GDPR, CCPA, HIPAA compliant
**Transparency:** Full visibility into all access and usage
**Revocable:** All permissions revocable instantly
**Legacy Planning:** Essential for digital asset management
