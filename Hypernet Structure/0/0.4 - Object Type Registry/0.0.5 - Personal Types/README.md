---
ha: "0.4.0.5"
object_type: "document"
creator: "1.1"
created: "2026-02-09"
status: "active"
visibility: "public"
flags: ["registry"]
---

# 0.0.5 - Personal Types

## Category Overview

Personal Types encompass object types related to personal documents, financial records, location data, health information, and profile attributes. These types store sensitive personal information and require strong privacy controls.

**Parent Category:** 0.0 - Object Type Registry
**Subcategory Code:** 0.0.5
**Number of Types:** 5

## Object Types in This Category

### 0.0.5.1 - Document
**Purpose:** Personal and business documents including contracts, receipts, certificates, IDs

**Core Fields:**
- `document_type`: contract, receipt, invoice, tax_document, identification, certificate, insurance, legal, medical, other
- `file_path`: Storage path or URL
- `file_size_bytes`: File size
- `mime_type`: Document MIME type
- `category`: User-defined category
- `issue_date`: When document was issued
- `expiry_date`: When document expires (if applicable)
- `issuer`: Who issued the document
- `recipient`: Document recipient
- `document_number`: Reference number
- `is_important`: Importance flag
- `tags`: Array of tags
- `notes`: User notes

**Privacy Level:** High - Contains sensitive personal/business documents
**Retention:** Permanent (user-controlled)
**API Endpoint:** `/api/v1/documents`

**Use Cases:**
- Store scanned receipts and invoices
- Manage contracts and agreements
- Track government IDs and certificates
- Organize tax documents
- Medical document storage

---

### 0.0.5.2 - Transaction
**Purpose:** Financial transactions including purchases, payments, transfers

**Core Fields:**
- `transaction_type`: purchase, payment, transfer, refund, subscription, income, other
- `amount`: Transaction amount (Decimal)
- `currency`: Currency code (USD, EUR, etc.)
- `merchant`: Merchant name
- `category`: Transaction category
- `description`: Transaction description
- `transaction_date`: When transaction occurred
- `payment_method`: Payment method used
- `status`: pending, completed, failed, cancelled, refunded
- `account_last_four`: Last 4 digits of account
- `receipt_url`: Receipt URL/path
- `tags`: Array of tags
- `is_recurring`: Recurring transaction flag
- `notes`: User notes

**Privacy Level:** Very High - Contains financial information
**Retention:** 7 years (tax purposes)
**API Endpoint:** `/api/v1/transactions`

**Advanced Features:**
- Spending analytics by category
- Total amount calculations
- Date range queries
- Recurring transaction tracking

**Use Cases:**
- Personal expense tracking
- Budget management
- Tax preparation
- Financial reporting
- Subscription tracking

---

### 0.0.5.3 - Location
**Purpose:** Location history, GPS coordinates, places, check-ins

**Core Fields:**
- `location_type`: gps_point, address, place, checkin, route
- `latitude`: GPS latitude (Decimal)
- `longitude`: GPS longitude (Decimal)
- `altitude`: Altitude in meters
- `accuracy`: Accuracy in meters
- `address`: Full street address
- `city`: City name
- `state`: State/province
- `country`: Country name
- `postal_code`: Postal code
- `place_name`: Place name
- `place_category`: Category of place
- `timestamp`: When location was recorded
- `source_app`: App that recorded location
- `activity_type`: Activity type (walking, driving, etc.)
- `notes`: User notes

**Privacy Level:** Very High - Contains sensitive location data
**Retention:** Permanent (user-controlled)
**API Endpoint:** `/api/v1/locations`

**Advanced Features:**
- Nearby search with Haversine formula
- Location history queries
- Geographic filtering
- Activity type tracking

**Use Cases:**
- Location history tracking
- Travel logging
- Place discovery
- Activity tracking
- Geographic data analysis

---

### 0.0.5.4 - Health Record
**Purpose:** Medical records, appointments, medications, vital signs

**Core Fields:**
- `record_type`: appointment, medication, lab_result, vital_sign, diagnosis, immunization, allergy, procedure, other
- `record_date`: Date of record
- `provider_name`: Healthcare provider
- `facility_name`: Medical facility
- `description`: Record description
- `diagnosis_codes`: Array of diagnosis codes
- `medication_name`: Medication name
- `dosage`: Medication dosage
- `frequency`: Medication frequency
- `measurement_type`: Type of measurement (blood_pressure, weight, etc.)
- `measurement_value`: Measurement value
- `measurement_unit`: Unit of measurement
- `file_paths`: Array of file paths (scanned documents)
- `is_important`: Importance flag
- `notes`: User notes

**Privacy Level:** Critical - HIPAA-level protection
**Retention:** Permanent (medical records)
**API Endpoint:** `/api/v1/health-records`

**Advanced Features:**
- Active medication tracking (within 90 days)
- Provider/facility filtering
- Measurement trend analysis
- Immunization history

**Use Cases:**
- Medical history management
- Medication tracking
- Appointment scheduling
- Lab result storage
- Health monitoring

---

### 0.0.5.5 - Profile Attribute
**Purpose:** User profile attributes, skills, interests, preferences, credentials

**Core Fields:**
- `attribute_type`: preference, skill, interest, certification, education, work_experience, custom
- `key`: Attribute name/key
- `value`: Attribute value (JSONB - any type)
- `category`: Attribute category
- `is_public`: Public visibility flag
- `is_verified`: Verification status
- `verification_source`: Verification source
- `priority`: Display priority (higher = more important)
- `tags`: Array of tags
- `notes`: User notes

**Privacy Level:** Variable (user-controlled)
**Retention:** Permanent (user-controlled)
**API Endpoint:** `/api/v1/profile-attributes`

**Advanced Features:**
- Public/private visibility control
- Verification system
- Priority-based ordering
- Flexible JSONB value storage
- Public profile endpoint (unauthenticated)

**Use Cases:**
- User profile management
- Skills and interests tracking
- Education and certifications
- Work experience
- Custom profile fields
- Public portfolio

---

## Category Characteristics

### Privacy Requirements
**All Personal Types require:**
- Strong encryption at rest
- Access control and permissions
- Audit logging for all access
- GDPR/CCPA compliance
- User consent for data sharing
- Right to deletion support

### Data Sensitivity Levels
- **Critical:** Health Records (HIPAA-level)
- **Very High:** Transactions, Locations
- **High:** Documents, Profile Attributes

### Compliance Requirements
- **GDPR:** Right to access, right to erasure, data portability
- **CCPA:** Consumer data rights, opt-out mechanisms
- **HIPAA:** For health records only
- **SOC 2:** Data security and availability

### Retention Policies
- **Financial:** 7 years (tax requirements)
- **Medical:** Permanent (medical records)
- **Location:** User-controlled (can delete anytime)
- **Documents:** User-controlled
- **Profile:** User-controlled

## Implementation Status

### Database Models
- ✅ Document model defined (`app/models/document.py`)
- ✅ Transaction model defined (`app/models/transaction.py`)
- ✅ Location model defined (`app/models/location.py`)
- ✅ HealthRecord model defined (`app/models/health_record.py`)
- ✅ ProfileAttribute model defined (`app/models/profile_attribute.py`)

### API Endpoints
- ✅ Documents API complete (7 endpoints)
- ✅ Transactions API complete (8 endpoints with analytics)
- ✅ Locations API complete (8 endpoints with nearby search)
- ✅ Health Records API complete (8 endpoints)
- ✅ Profile Attributes API complete (8 endpoints with public access)

### Total Endpoints: 39
All endpoints include:
- CRUD operations
- Soft delete support
- Pagination
- Advanced filtering
- Full-text search (where applicable)

## Privacy & Security

### Encryption
- At rest: Database-level encryption
- In transit: TLS/SSL
- Field-level: Consider for sensitive fields (SSN, credit cards)

### Access Control
- User owns all their personal data
- Permission-based sharing
- Granular privacy settings
- Audit trail for all access

### Data Sharing
- Explicit user consent required
- Granular permissions per AI company
- Revocable access
- Usage tracking and reporting

## Related Categories

- **0.0.1 - Core Types:** User, Integration, Link
- **0.0.6 - System Types:** Device, Notification, Audit
- **0.0.8 - Life Types:** Task, CalendarEvent, Note (overlap with personal)

## Use in Hypernet Platform

Personal Types are central to Hypernet's value proposition:
1. **User Control:** Users own and control all personal data
2. **Privacy First:** Strong privacy by default
3. **AI Access:** Controlled sharing with AI companies
4. **Data Portability:** Easy export and migration
5. **Monetization:** Users can sell access to their data

## Next Steps

1. Implement field-level encryption for most sensitive data
2. Build privacy dashboard for users
3. Create data export functionality
4. Implement granular permission system
5. Add data usage tracking
6. Build compliance reporting

---

**Category Status:** ✅ Implemented
**Models:** 5/5 Complete
**APIs:** 39 endpoints
**Created:** February 5, 2026
**Last Updated:** February 5, 2026
**Maintained By:** Hypernet Core Team
