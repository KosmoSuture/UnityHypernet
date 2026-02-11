# 1.1.6.2 - Data Permissions

**Hypernet Address:** `1.1.6.2`
**Owner:** Matt Schaeffer (1.1)
**Category:** Personal Data - Data Permissions
**Last Updated:** February 10, 2026

---

## Purpose

This folder manages granular permissions for who can access, view, edit, share, and delete specific data within your Hypernet account. This is the detailed access control system.

---

## What Goes Here

### Permission Management
- **User Permissions:** Who can access what data
- **Group Permissions:** Access rights for groups
- **Application Permissions:** Third-party app access
- **AI Permissions:** AI assistant access rights
- **Integration Permissions:** Service integration access
- **API Access:** API key management and permissions
- **Temporary Access:** Time-limited permissions
- **Emergency Access:** Break-glass emergency access

### Permission Types

#### Read Permission
- View data
- Search data
- Generate reports
- Export read-only copies

#### Write Permission
- Create new data
- Modify existing data
- Add comments/annotations
- Tag and categorize

#### Delete Permission
- Delete data (move to trash)
- Permanently delete
- Bulk delete
- Cascade delete (related data)

#### Share Permission
- Share with others
- Create public links
- Set sharing permissions
- Revoke shared access

#### Admin Permission
- Manage permissions
- Add/remove users
- Configure settings
- Access audit logs

---

## Permission Levels

### Owner (You)
**Access:** Full control over all data
**Permissions:**
- Read, Write, Delete, Share, Admin
- Cannot be revoked
- Can delegate any permission level
- Can revoke any delegated permission
- Master encryption key holder

### Full Access
**Access:** Complete access like owner (except admin)
**Permissions:**
- Read, Write, Delete, Share
- Cannot manage permissions
- Cannot access admin settings
- Trusted family member or executor
**Use Case:** Spouse, digital executor

### Edit Access
**Access:** Can view and modify
**Permissions:**
- Read, Write
- Cannot delete or share
- Can add/edit but not remove
- Collaborative access
**Use Case:** Project collaborator, family calendar

### View Access
**Access:** Read-only
**Permissions:**
- Read only
- Cannot modify, delete, or share
- Can search and export (if allowed)
- Observer role
**Use Case:** Sharing photos with friends, read-only documents

### Limited Access
**Access:** Specific data only
**Permissions:**
- Read specific items
- Time-limited or context-limited
- Restricted to certain data types
- May expire automatically
**Use Case:** Temporary contractor, specific project access

### No Access (Default)
**Access:** Cannot see or access
**Permissions:**
- None
- Data invisible to user
- Cannot search or discover
- Default for everyone except owner

---

## Permission Grants

### Individual User Permissions

**Format:**
```
User: Sarah Johnson (sarah@email.com)
Data: Photo Album "Europe Vacation 2025"
Permission: View Access
Granted: February 10, 2026
Expires: Never
Can Download: Yes
Can Reshare: No
Granted By: Matt Schaeffer
Reason: Shared vacation memories
```

**Track:**
- Who has access
- What they can access
- Permission level
- When granted
- Expiration (if any)
- Granted by whom
- Access history

### Group Permissions

**Family Group:**
- Members: [List of family members]
- Default Permission: View Access
- Data Scope: Family photos, shared calendar, family documents
- Can add members: Matt and spouse only
- Automatic membership: Direct family

**Work Team:**
- Members: [Team members]
- Default Permission: Edit Access
- Data Scope: Project files, team documents
- Can add members: Team leads
- Membership expires: When leave team

**Friend Circle:**
- Members: [Close friends]
- Default Permission: View Access
- Data Scope: Social photos, event calendars
- Can add members: Matt only
- Membership: Manual only

---

## Third-Party Application Permissions

### Connected Apps
Track all third-party applications with access:

**Example: Photo Editing App**
```
App Name: Adobe Lightroom
Developer: Adobe Inc.
Permissions Granted:
  - Read: Photos, Albums
  - Write: Photo edits, metadata
  - Delete: No
  - Share: No
Granted: January 15, 2026
Last Used: February 9, 2026
Data Accessed: 142 photos
Revocable: Yes
Auto-revoke if unused: 90 days
```

### Permission Scopes
- **Photos:** Read/Write photos and albums
- **Calendar:** Read/Write calendar events
- **Contacts:** Read/Write contact information
- **Documents:** Read/Write documents
- **Email:** Read/Write email (rarely granted)
- **Location:** Access location history
- **Health:** Access health data
- **Financial:** Access financial data (rarely granted)

### App Vetting
Before granting permissions:
- Research app reputation
- Read privacy policy
- Check permissions requested
- Verify actually needed
- Prefer read-only when possible
- Set expiration if temporary need
- Monitor usage after granting

---

## AI Assistant Permissions

### AI Access Control
Separate permissions for each AI provider:

**Claude (Anthropic):**
- Documents: Query Only
- Photos: No Access
- Calendar: Query Only
- Email: No Access
- Tasks: Query Only
- Financial: No Access
- Health: No Access
- Training: Opt-out

**ChatGPT (OpenAI):**
- Documents: No Access
- Photos: No Access
- Calendar: No Access
- All Data: No Access
- Training: Opt-out

**Custom AI Assistant:**
- Scope: Work documents only
- Read-only access
- No export capability
- On-device processing only
- No cloud upload

### AI Use Cases
- **Query/Search:** AI helps find information
- **Summarize:** AI summarizes documents/emails
- **Analyze:** AI analyzes patterns and trends
- **Generate:** AI creates content based on your data
- **Recommend:** AI suggests actions or content
- **Train:** AI uses your data for training (opt-in only)

---

## Integration Permissions

### Service Integrations
Control what each integrated service can access:

**Google Drive:**
- Import: Documents, Photos
- Export: No
- Sync: Two-way
- Access: All Drive files
- Can Delete: No (Hypernet side only)

**Gmail:**
- Import: All email, attachments
- Export: No
- Sync: One-way (import only)
- Access: All mailboxes
- Can Delete: No

**Fitness Tracker:**
- Import: Workouts, health metrics
- Export: No
- Sync: Real-time
- Access: Activity data only
- Can Delete: No

**Bank (via Plaid):**
- Import: Transactions, balances
- Export: No
- Sync: Daily
- Access: Checking and savings only
- Can Delete: No

### Integration Security
- OAuth 2.0 authentication
- Limited scope tokens
- Revocable access
- Audit all API calls
- Rate limiting
- Expire inactive integrations
- Encrypted credentials

---

## API Access Management

### API Keys
If providing API access to your data:

**Personal API Key:**
```
Key ID: pk_live_abc123xyz789
Name: Personal Data Access
Created: February 1, 2026
Last Used: February 10, 2026
Permissions:
  - Read: All data
  - Write: Notes, Tasks
  - Delete: No
Rate Limit: 1000 requests/day
IP Restriction: Home IP only
Expires: Never (revocable)
```

**Application API Key:**
```
Key ID: pk_app_def456uvw012
Name: Mobile App Access
Created: January 15, 2026
Permissions:
  - Read: Photos, Calendar, Tasks
  - Write: Tasks, Calendar events
  - Delete: Tasks only
Rate Limit: 10000 requests/day
Device: Registered devices only
Expires: 1 year
```

### API Security
- Unique key per application/use
- Minimum necessary permissions
- Rate limiting
- IP whitelisting (when possible)
- Request logging
- Anomaly detection
- Auto-revoke on suspicious activity
- Rotate keys periodically

---

## Temporary Access

### Time-Limited Permissions
Grant access that automatically expires:

**Contractor Access:**
- User: John the Designer
- Permission: View & Edit
- Data Scope: Website project folder only
- Granted: February 1, 2026
- Expires: February 28, 2026
- Auto-revoke: Yes
- Reason: Website redesign project

**Event Shared Album:**
- Shared With: Party guests
- Permission: View & Download
- Data Scope: Birthday party photos
- Granted: February 10, 2026
- Expires: March 10, 2026 (30 days)
- Purpose: Share party photos

### One-Time Access
- Generate single-use access link
- Expires after first use
- No account required
- Password protected
- View only
- Cannot download (optional)
- Track when accessed

---

## Emergency Access

### Break-Glass Access
For emergencies when you're incapacitated:

**Emergency Contact: Spouse**
- Triggered: After 30 days of inactivity
- Notification: Email to designated contacts
- Waiting Period: 7 days before access granted
- Access Level: Full Access
- Data Included: All except specifically excluded
- Notification to You: Alerts before granting

**Emergency Medical Access:**
- Medical professionals can request access
- Verify credentials
- Limited to medical records only
- Requires emergency verification
- Automatic expiration: 7 days
- Full audit trail

---

## Permission Auditing

### Regular Audits
**Monthly Review:**
- [ ] Review all active permissions
- [ ] Check for unused access grants
- [ ] Verify AI permissions still appropriate
- [ ] Review app permissions
- [ ] Check integration access
- [ ] Monitor API usage
- [ ] Review audit logs for anomalies

**Quarterly Deep Review:**
- [ ] Review all group memberships
- [ ] Audit all third-party apps
- [ ] Review all API keys
- [ ] Check all temporary access grants
- [ ] Verify emergency access settings
- [ ] Test permission enforcement
- [ ] Review and update policies

### Audit Questions
- Who currently has access to my data?
- What apps have permissions?
- When was each permission last used?
- Are any permissions unused and revocable?
- Are permission levels still appropriate?
- Have any security events occurred?
- Is any data being accessed unexpectedly?

---

## Permission Revocation

### Immediate Revocation
Instantly revoke access when:
- Employee or contractor leaves
- Relationship ends
- App no longer used
- Security concern
- No longer needed
- Permission misused
- Account compromised

### Revocation Process
1. Identify permission to revoke
2. Click revoke/delete
3. Immediate effect (no grace period)
4. Notify affected user/app
5. Audit log entry
6. Verify revocation effective
7. Document reason

### Mass Revocation
- Revoke all app permissions
- Revoke all AI access
- Revoke all API keys
- Emergency lockdown mode
- Require re-authentication
- Review before re-granting

---

## Best Practices

1. **Principle of Least Privilege:** Grant minimum access needed
2. **Default Deny:** No access unless explicitly granted
3. **Regular Reviews:** Audit permissions monthly
4. **Time Limits:** Use expiration when possible
5. **Monitor Usage:** Track who accesses what
6. **Quick Revocation:** Remove access when not needed
7. **Document Grants:** Record why access granted
8. **Separate Contexts:** Different permissions for work vs personal
9. **Test Permissions:** Verify permissions work as intended
10. **Emergency Plan:** Have break-glass access configured

---

## Related Sections

- **1.1.6.0** - Hypernet Data Store (data being protected)
- **1.1.6.1** - Privacy Settings (high-level privacy configuration)
- **1.1.4** - Relationships (people who may have access)
- **1.1.10** - Passwords & Credentials (authentication)

---

**Status:** Active Access Control
**Review Frequency:** Monthly recommended
**Default Policy:** Deny all, grant explicitly
**Granularity:** Per-user, per-data-item, per-permission-type
**Revocability:** All permissions instantly revocable
**Audit Trail:** Complete history of all permission changes
**Emergency Access:** Configured with safeguards
**Third-Party Scrutiny:** Carefully vet all third-party access
