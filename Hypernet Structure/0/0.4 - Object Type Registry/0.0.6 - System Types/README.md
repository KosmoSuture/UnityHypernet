# 0.0.6 - System Types

## Category Overview

System Types encompass object types related to system functionality, device management, notifications, and audit logging. These types support the platform's operational infrastructure and security requirements.

**Parent Category:** 0.0 - Object Type Registry
**Subcategory Code:** 0.0.6
**Number of Types:** 3

## Object Types in This Category

### 0.0.6.1 - Device
**Purpose:** User devices including phones, computers, tablets, IoT devices

**Core Fields:**
- `device_type`: phone, computer, tablet, wearable, iot, smart_home, vehicle, other
- `device_name`: User-assigned device name
- `manufacturer`: Device manufacturer
- `model`: Device model
- `os_name`: Operating system name
- `os_version`: Operating system version
- `device_identifier`: IMEI, serial number, MAC address, etc.
- `ip_address`: Current IP address
- `is_primary`: Primary device flag
- `is_trusted`: Trust status
- `last_seen_at`: Last activity timestamp
- `purchase_date`: When device was purchased
- `warranty_expiry`: Warranty expiration date
- `notes`: User notes

**Privacy Level:** Medium - Contains device metadata
**Retention:** Permanent (user-controlled)
**API Endpoint:** `/api/v1/devices`

**Advanced Features:**
- Heartbeat tracking (last_seen_at updates)
- Trust/untrust actions
- Primary device auto-management
- IP address history
- Warranty tracking

**Use Cases:**
- Multi-device account management
- Security monitoring
- Device trust levels
- Two-factor authentication
- IoT device management
- Smart home integration
- Vehicle tracking

**Security Considerations:**
- Only one primary device at a time
- Trusted devices get extended sessions
- Untrusted devices require re-authentication
- IP address tracking for security monitoring
- Device fingerprinting for fraud prevention

---

### 0.0.6.2 - Notification
**Purpose:** System notifications, alerts, reminders, messages

**Core Fields:**
- `notification_type`: system, alert, reminder, message, update, marketing
- `title`: Notification title
- `message`: Notification message (max 1000 chars)
- `priority`: low, normal, high, urgent
- `category`: Notification category
- `action_url`: URL to navigate when clicked
- `action_label`: Label for action button
- `related_object_type`: Type of related object (email, task, etc.)
- `related_object_id`: ID of related object
- `is_read`: Read status
- `is_archived`: Archive status
- `read_at`: When notification was read
- `scheduled_for`: When to send notification (future scheduling)
- `expires_at`: When notification becomes irrelevant

**Privacy Level:** Low - System messages
**Retention:** 90 days (auto-cleanup)
**API Endpoint:** `/api/v1/notifications`

**Advanced Features:**
- Priority-based ordering (urgent → high → normal → low)
- Scheduling for future delivery
- Expiration and auto-cleanup
- Related object linking
- Action URLs for click-through
- Unread count tracking
- Bulk mark-as-read
- Statistics by type and priority

**Use Cases:**
- System notifications (updates, maintenance)
- User alerts (security, errors)
- Reminders (tasks, events)
- Messages (from other users)
- Update announcements
- Marketing messages (opt-in)
- Action-required items

**Notification Flow:**
1. **Creation:** System or user creates notification
2. **Scheduling:** Optional future delivery time
3. **Delivery:** Show in user's notification center
4. **Action:** User clicks, marks read, or dismisses
5. **Expiration:** Auto-delete after expiry date or 90 days
6. **Archive:** User can archive old notifications

---

### 0.0.6.3 - Audit
**Purpose:** Audit logs for security, compliance, and forensic analysis

**Core Fields:**
- `action`: Action performed (create, update, delete, login, logout, etc.)
- `resource_type`: Type of resource affected (media, task, etc.)
- `resource_id`: ID of resource affected
- `ip_address`: IP address of request
- `user_agent`: Browser/app user agent
- `request_method`: HTTP method (GET, POST, etc.)
- `request_path`: API endpoint called
- `status_code`: HTTP status code
- `changes`: JSONB of before/after values
- `metadata`: Additional metadata
- `timestamp`: When action occurred

**Privacy Level:** System - Restricted access
**Retention:** 7 years (compliance)
**API Endpoint:** `/api/v1/audit` (READ-ONLY)

**Read-Only:** No create, update, or delete endpoints
**Access:** User can view their own audit logs only

**Advanced Features:**
- Complete action history
- Change tracking (before/after)
- Security monitoring (unusual IPs, failed logins)
- Resource history tracking
- IP address analysis
- Activity summaries
- Recent activity queries

**Use Cases:**
- **Compliance:** GDPR, CCPA, SOC 2, HIPAA
- **Security:** Monitoring for unauthorized access
- **Forensics:** Investigating data breaches or issues
- **Support:** Understanding user actions
- **Analytics:** User behavior analysis

**Audit Events Tracked:**
- User registration and login
- Password changes
- Two-factor auth events
- Data access (read)
- Data modifications (create, update, delete)
- Privacy setting changes
- Integration connections/disconnections
- Data exports
- Permission grants/revocations
- API key creation/rotation

**Compliance Requirements:**
- **SOC 2:** Complete audit trail required
- **GDPR:** Track data access and modifications
- **HIPAA:** Healthcare data access logging
- **PCI DSS:** Payment data access tracking (if applicable)

---

## Category Characteristics

### Purpose
System Types provide operational infrastructure:
- **Device:** Account security and device management
- **Notification:** User engagement and communication
- **Audit:** Compliance, security, and forensics

### System-Level Features
All System Types:
- Support platform operations
- Enable security and compliance
- Provide user communication channels
- Track system activity

### Privacy Considerations
- **Device:** Medium privacy (metadata only, no personal content)
- **Notification:** Low privacy (system messages)
- **Audit:** System-level (restricted access, compliance-focused)

## Implementation Status

### Database Models
- ✅ Device model defined (`app/models/device.py`)
- ✅ Notification model defined (`app/models/notification.py`)
- ✅ Audit model defined (`app/models/audit.py`)

### API Endpoints
- ✅ Devices API complete (9 endpoints)
  - Heartbeat tracking
  - Trust/untrust actions
  - Primary device management
- ✅ Notifications API complete (9 endpoints)
  - Priority ordering
  - Scheduling support
  - Statistics dashboard
  - Bulk actions
- ✅ Audit API complete (8 endpoints, READ-ONLY)
  - Activity summaries
  - Resource history
  - IP tracking
  - Recent activity

### Total Endpoints: 26
All endpoints include authentication and authorization

## Security Architecture

### Device Security
**Trust Levels:**
- **Trusted:** Extended session, fewer auth prompts
- **Untrusted:** Frequent re-auth, limited access

**Primary Device:**
- Only one primary at a time
- Auto-unmarks others when setting new primary
- Gets preferential treatment for notifications

**Heartbeat System:**
- Regular updates to last_seen_at
- IP address tracking
- Presence monitoring

### Notification Security
**Access Control:**
- Users only see their own notifications
- No cross-user visibility
- Admin notifications visible to all

**Privacy:**
- No sensitive data in notification messages
- Links to actual data (don't embed)
- Expiration prevents stale data exposure

### Audit Security
**Immutability:**
- No modification or deletion of audit logs
- Append-only design
- Tamper-evident

**Access Control:**
- Users can view their own audit logs
- Admins can view all (with audit trail)
- No bulk export (prevent data mining)

**Retention:**
- 7 years minimum (compliance)
- Encrypted at rest
- Secured backup and archival

## Compliance & Regulations

### SOC 2 Type II
**Requirements:**
- Complete audit trail
- Access control logs
- Security monitoring
- Change management logs

**System Types Support:**
- Audit logs provide trail
- Device management for security
- Notifications for security alerts

### GDPR
**Requirements:**
- Data access logging
- Right to access audit logs
- Data deletion tracking

**System Types Support:**
- Audit logs track all data access
- Users can view their audit history
- Deletion events logged

### HIPAA (Healthcare)
**Requirements:**
- Complete audit trail for health data
- Access control and monitoring
- Security incident tracking

**System Types Support:**
- Audit logs for health record access
- Device trust for access control
- Notifications for security events

## Integration with Other Categories

### Device + 0.0.1 (User)
- Devices belong to users
- Used for authentication
- Session management

### Notification + All Types
- Notifications reference any object type
- Alerts for important events
- Action items for user

### Audit + All Types
- Tracks all user actions
- Monitors data access
- Provides change history

## Performance Considerations

### Device
- Heartbeat updates are write-heavy
- Index on user_id and last_seen_at
- Periodic cleanup of inactive devices

### Notification
- High read volume (notification center)
- Auto-expiration reduces storage
- Index on user_id, is_read, created_at

### Audit
- Write-heavy (every user action)
- Very large table (billions of rows)
- Partitioning by date
- Archive old records to cold storage
- Read optimization for recent logs

## Next Steps

### Device Management
1. Implement device fingerprinting
2. Add push notification support
3. Build device trust scoring
4. Implement geolocation tracking

### Notification System
1. Add push notifications (web, mobile)
2. Build notification preferences UI
3. Implement digest mode (daily summary)
4. Add notification channels (email, SMS, push)

### Audit System
1. Set up log aggregation
2. Implement anomaly detection
3. Build compliance reporting
4. Create forensic analysis tools
5. Add security alerting

---

**Category Status:** ✅ Implemented
**Models:** 3/3 Complete
**APIs:** 26 endpoints
**Created:** February 5, 2026
**Last Updated:** February 5, 2026
**Maintained By:** Hypernet Core Team
