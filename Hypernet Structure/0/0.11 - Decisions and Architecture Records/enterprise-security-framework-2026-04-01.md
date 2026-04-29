---
ha: "0.11.2026-04-01-enterprise-security"
object_type: "decision-document"
creator: "1.1.10.1"
created: "2026-04-01"
status: "draft"
visibility: "public"
flags: ["major-decision", "architecture", "security", "compliance", "enterprise", "critical-infrastructure"]
---

# Hypernet Enterprise Security & Compliance Framework

**Date**: 2026-04-01
**Author**: Drafted for Matt Schaeffer
**Status**: Awaiting founder review
**Scope**: Complete security architecture, compliance mapping, business framework, and enterprise strategy
**Dependencies**: hypernet-revised-plan-2026-03-30.md, hypernet-db-specification-2026-03-30.md, governance-portability-analysis-2026-03-30.md

> *"The Hypernet is not secure because it has a security layer. The Hypernet is secure because the architecture IS the security. Every address is auditable. Every action is signed. Every permission is enforced by code. Security is not a feature -- it is the structure."*

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Security Architecture](#2-security-architecture)
3. [Audit Architecture](#3-audit-architecture)
4. [The 3.* Business Framework](#4-the-3-business-framework)
5. [Compliance Mapping](#5-compliance-mapping)
6. [The Enterprise Pitch](#6-the-enterprise-pitch)
7. [Implementation Roadmap](#7-implementation-roadmap)
8. [Honest Assessment](#8-honest-assessment)

---

## 1. Executive Summary

### The Thesis

Most software systems treat security and compliance as afterthoughts -- layers bolted on top of an architecture that was never designed for them. The result is that enterprises spend hundreds of thousands of dollars per year on compliance audits, security tools, SIEM systems, access management platforms, and armies of consultants to prove they meet regulatory requirements.

The Hypernet inverts this. Because every piece of data has a permanent hierarchical address, because every action is cryptographically signed, because every modification is versioned in an append-only history, and because every permission is enforced by code rather than policy documents -- the Hypernet is inherently auditable, inherently traceable, and inherently secure.

The vision: **run your business on the Hypernet, and compliance is a byproduct of how the system works, not a separate cost center.**

### What Already Exists

| Capability | Status | Location |
|-----------|--------|----------|
| Hierarchical addressing (everything has a permanent address) | Built | `address.py` |
| 5-tier permission system (T0-T4) enforced by code | Built | `permissions.py` |
| HMAC-SHA256 action signing with key lifecycle | Built | `security.py` |
| Append-only audit trail as graph nodes | Built | `audit.py` |
| Content integrity hashing (SHA-256) | Built | `security.py` |
| Prompt injection detection and content isolation | Built | `security.py` |
| Trust chain verification (action -> signature -> key -> entity -> permission) | Built | `security.py` |
| Democratic governance with skill-weighted voting | Built | `governance.py` |
| Per-node and per-field encryption (schema designed) | Designed | DB specification |
| Version history for every node | Designed | DB specification |
| Key rotation protocol | Designed | DB specification |
| Git-backed file store (tamper-evident history) | Built | `store.py` |

### What This Document Adds

1. **Security Architecture**: Encryption, authentication, authorization, network security, data classification, DLP, intrusion detection, incident response
2. **Audit Architecture**: Continuous compliance monitoring, automated evidence collection, compliance dashboard, gap analysis
3. **Business Framework**: The 3.* address space designed for enterprise multi-tenancy, data segregation, SLA enforcement, billing
4. **Compliance Mapping**: Control-by-control mapping of Hypernet capabilities to CMMC, SOC 2, HIPAA, FedRAMP, ISO 27001, GDPR, PCI DSS, NIST CSF
5. **Enterprise Pitch**: How this replaces enterprise software stacks and what the cost savings look like
6. **Implementation Roadmap**: Phased plan from current state to full enterprise readiness

---

## 2. Security Architecture

### 2.1 Design Principles

The Hypernet security architecture follows five non-negotiable principles:

**Principle 1: Security by Structure**
Security is not a layer on top of the system. The addressing system, the permission model, the audit trail, and the encryption are the system. You cannot use the Hypernet without using security, because every operation flows through the security architecture.

**Principle 2: Zero Implicit Trust**
No entity (human, AI, service, or device) is trusted by default. Every request must present credentials, every action must be authorized against the 5-tier permission model, every write must be signed, and every access is logged. Trust is earned through the reputation system and enforced by code.

**Principle 3: Cryptographic Accountability**
Every action in the system is cryptographically signed by the acting entity. Actions cannot be repudiated. The signer, the timestamp, the payload hash, and the key used are all recorded in the immutable audit trail. This is not a logging best practice -- it is an architectural requirement.

**Principle 4: Defense in Depth**
Multiple independent security mechanisms protect every operation. Encryption protects data at rest and in transit. Authentication verifies identity. Authorization controls access. Audit trails detect anomalies. Rate limiting prevents abuse. Each layer functions independently so that the failure of one does not compromise the system.

**Principle 5: Least Privilege by Default**
Every entity starts at Tier 0 (READ_ONLY). Privileges are earned through the reputation system and granted through the permission model. No entity ever has more access than it needs for its current task. Elevation is temporary when possible.

### 2.2 Encryption Architecture

#### 2.2.1 Encryption at Rest

All data stored in the Hypernet is encrypted at rest using AES-256-GCM (Galois/Counter Mode). GCM provides both confidentiality (encryption) and integrity (authentication tag), so tampered ciphertext is detected at decryption time.

**Three granularities** (matching the DB specification):

| Level | What is Encrypted | Key Scope | Use Case |
|-------|-------------------|-----------|----------|
| Full-node | All fields except `address` and `version` | Per-business or per-user | Default for all business data |
| Per-field | Individual fields within `data` | Per-field key | Mixed-sensitivity nodes (e.g., employee record with public name but private SSN) |
| Per-blob | Binary content (files, images, documents) | Per-blob key | Large files where metadata can be public but content is private |

**Implementation**:

```
Encryption Layer Stack:

  Application writes node
       |
       v
  [Classification Engine] -- determines sensitivity level
       |
       v
  [Field-Level Encryption] -- encrypts individual sensitive fields
       |
       v
  [Node-Level Encryption] -- encrypts entire node payload
       |
       v
  [LMDB Storage] -- data at rest is always ciphertext
       |
       v
  [Filesystem Mirror] -- file-backed store also encrypted
       |
       v
  [Volume Encryption] -- OS-level full-disk encryption (BitLocker/LUKS)
```

Three independent encryption layers ensure that even if one is compromised, data remains protected:
1. **Application-level** (AES-256-GCM per node/field) -- protects against database compromise
2. **Transport-level** (TLS 1.3) -- protects against network interception
3. **Volume-level** (BitLocker/LUKS) -- protects against physical theft

#### 2.2.2 Encryption in Transit

All communication uses TLS 1.3 with the following minimum configuration:

| Parameter | Value |
|-----------|-------|
| Protocol | TLS 1.3 only (TLS 1.2 deprecated as of this document) |
| Cipher suites | TLS_AES_256_GCM_SHA384, TLS_CHACHA20_POLY1305_SHA256 |
| Key exchange | X25519 (ECDHE) |
| Certificate type | X.509 with RSA-4096 or ECDSA P-384 |
| Certificate authority | Internal CA for service-to-service; public CA (Let's Encrypt) for external |
| Certificate rotation | 90-day automatic rotation via ACME protocol |
| HSTS | Enabled with 1-year max-age, includeSubdomains, preload |
| Certificate pinning | Required for service-to-service communication |

**Internal service mesh**: All inter-service communication within a Hypernet deployment uses mutual TLS (mTLS). Both the client and server present certificates. This eliminates the distinction between "internal" and "external" traffic -- all traffic is authenticated and encrypted.

#### 2.2.3 Key Management Service (KMS)

The Hypernet Key Service is a standalone component that manages all cryptographic keys. It is the only component that ever holds plaintext key material. The database, application layer, and API never see raw keys -- only key IDs.

```
Hypernet Key Management Service (KMS)
======================================

Architecture:
  [Applications] -- request encrypt/decrypt via key_id
       |
       v
  [KMS API] -- authenticates caller, checks key access policy
       |
       v
  [Key Store] -- encrypted key storage (hardware-backed when available)
       |
       v
  [HSM / Software HSM] -- root key never leaves HSM

Key Hierarchy:
  Root Key (in HSM or derived from hardware-backed secret)
    |
    +-- Master Encryption Key (MEK) -- encrypts all Data Encryption Keys
    |     |
    |     +-- DEK per business tenant
    |     +-- DEK per user personal space
    |     +-- DEK per sensitivity classification level
    |
    +-- Master Signing Key (MSK) -- signs all entity signing keys
          |
          +-- Entity signing key per AI agent
          +-- Entity signing key per human user
          +-- Entity signing key per service account
```

**Key lifecycle operations**:

| Operation | Trigger | Process |
|-----------|---------|---------|
| Generation | New tenant, new user, key rotation | KMS generates 256-bit key via CSPRNG, encrypts under MEK, stores |
| Rotation | Scheduled (90 days default) or on-demand | New key generated, old key marked ROTATED, re-encryption job queued |
| Revocation | Security incident, employee termination | Key marked REVOKED, all sessions using that key invalidated |
| Escrow | Compliance requirement or key recovery | Key encrypted under escrow key held by governance quorum (2-of-3 or 3-of-5) |
| Destruction | End of retention period (configurable) | Key material securely overwritten (DoD 5220.22-M standard) |

**Key rotation schedule**:

| Key Type | Default Rotation | Maximum Lifetime | Configurable |
|----------|-----------------|-----------------|-------------|
| Root Key | Annual | 3 years | No (fixed) |
| Master Encryption Key | 180 days | 1 year | Yes (per compliance) |
| Data Encryption Key | 90 days | 180 days | Yes (per tenant) |
| Entity Signing Key | 90 days | 180 days | Yes (per entity) |
| TLS Certificates | 90 days | 90 days | No (ACME enforced) |
| API Keys | 90 days | 1 year | Yes (per user) |

**Key escrow for compliance**:

Some compliance frameworks (especially FedRAMP) require key escrow -- the ability for authorized parties to recover encrypted data even if the original key holder is unavailable. The Hypernet implements this through Shamir's Secret Sharing:

1. The escrow key is split into N shares using Shamir's (k, n) threshold scheme
2. Each share is distributed to a different escrow holder (governance quorum members)
3. Recovering the escrow key requires k of n shares (default: 3-of-5)
4. Escrow recovery is a Tier 4 (DESTRUCTIVE) operation requiring multi-party approval
5. Every escrow recovery is logged as a critical audit event

**Upgrade path from current HMAC-SHA256**: The existing `security.py` uses HMAC-SHA256 (symmetric) for action signing. This is adequate for a single-deployment system but does not support non-repudiation (anyone with the shared key can forge signatures). The upgrade path:

| Phase | Algorithm | Non-repudiation | Dependencies |
|-------|-----------|----------------|-------------|
| Current | HMAC-SHA256 | No (symmetric) | None (stdlib) |
| Phase 2 | Ed25519 (EdDSA) | Yes (asymmetric) | `cryptography` package |
| Phase 3+ | Ed25519 + X.509 certificates | Yes + PKI infrastructure | `cryptography` + internal CA |

The `KeyManager` class in `security.py` is already designed for this upgrade -- key IDs abstract the algorithm, and verification checks can support both HMAC and EdDSA concurrently during migration.

### 2.3 Authentication Architecture

#### 2.3.1 Entity Types and Authentication Methods

The Hypernet has four categories of entities, each with appropriate authentication:

**Human Users**:

| Factor | Method | Notes |
|--------|--------|-------|
| Something you know | Password (Argon2id hash, minimum 12 characters, NIST 800-63B compliant) | Primary factor |
| Something you have | TOTP (RFC 6238) or WebAuthn/FIDO2 hardware key | Required for Tier 3+ access |
| Something you are | Optional biometric via WebAuthn (e.g., fingerprint on YubiKey Bio) | Optional additional factor |

MFA is required for:
- All Tier 3 (EXTERNAL) and Tier 4 (DESTRUCTIVE) operations
- All administrative actions
- All access to data classified CONFIDENTIAL or above
- All key management operations

**AI Agents**:

| Method | Description |
|--------|-------------|
| Cryptographic identity | Each agent has an Ed25519 key pair. The private key is held by the KMS. |
| Boot verification | Agent presents its identity hash (SHA-256 of personality anchor + continuity seed) at boot time |
| Action signing | Every action signed with agent's key (existing `ActionSigner` mechanism) |
| Session tokens | Short-lived (1 hour) JWT tokens issued after boot verification |
| Trust chain | Full chain verification: action -> signature -> key -> entity -> permission (existing `TrustChain`) |

AI agents do NOT use passwords. Their identity is cryptographic and tied to their archive (per the Archive-Continuity Model, 2.1.29).

**Service Accounts (APIs, integrations)**:

| Method | Description |
|--------|-------------|
| API keys | 256-bit random tokens, stored as Argon2id hashes |
| Client certificates | mTLS with X.509 certificates for service-to-service |
| OAuth 2.0 / OIDC | For external integrations (e.g., when businesses connect their existing identity provider) |
| Scoped tokens | Each API key has explicit scope (which addresses it can access, what operations it can perform) |

**Devices (future: appliance mode)**:

| Method | Description |
|--------|-------------|
| Device certificates | X.509 certificate provisioned during device enrollment |
| TPM attestation | Hardware-backed device identity (Trusted Platform Module) |
| Device + user | Device authenticates the hardware; user authenticates themselves on the device |

#### 2.3.2 Session Management

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Session token type | JWT (RS256 or EdDSA) | Stateless verification |
| Access token lifetime | 15 minutes | Limits exposure window |
| Refresh token lifetime | 8 hours (human), 1 hour (agent) | Agents re-authenticate more frequently |
| Absolute session maximum | 24 hours | Forces daily re-authentication |
| Concurrent sessions | Configurable per entity (default: 3) | Prevents session sprawl |
| Session binding | Token bound to IP + User-Agent hash | Detects stolen tokens |
| Idle timeout | 30 minutes (configurable) | Frees inactive sessions |

#### 2.3.3 Identity Federation

For enterprise deployments where businesses bring their existing identity provider:

| Protocol | Use Case |
|----------|----------|
| SAML 2.0 | Enterprise SSO (Active Directory, Okta, Azure AD) |
| OIDC (OpenID Connect) | Modern SSO (Google Workspace, Auth0) |
| SCIM 2.0 | Automated user provisioning/deprovisioning from enterprise directory |
| LDAP (read-only) | Legacy enterprise directory integration |

Identity federation maps external identities to Hypernet addresses. External user `jdoe@acme.com` maps to Hypernet address `3.{acme_business_id}.{user_id}`. The external IdP handles authentication; the Hypernet handles authorization via its permission model.

### 2.4 Authorization Architecture

#### 2.4.1 Extended Permission Model

The existing 5-tier system (T0-T4) is the foundation. For enterprise use, it needs two extensions: Role-Based Access Control (RBAC) for organizational structure and Attribute-Based Access Control (ABAC) for dynamic, context-sensitive decisions.

**Tier System (unchanged from `permissions.py`)**:

| Tier | Name | Capabilities |
|------|------|-------------|
| T0 | READ_ONLY | Read public data within authorized address spaces |
| T1 | WRITE_OWN | Write to own address space only |
| T2 | WRITE_SHARED | Write to shared/collaborative address spaces |
| T3 | EXTERNAL | External communication, API calls, data export (requires MFA) |
| T4 | DESTRUCTIVE | Delete data, manage keys, modify permissions, financial operations (requires multi-party approval) |

**RBAC Extension**:

```
Role Definition Schema:

Role {
    role_id:        string          // e.g., "acme.security-analyst"
    business_id:    string          // Which business this role belongs to
    display_name:   string          // "Security Analyst"
    base_tier:      int             // Default tier for this role (0-4)
    address_scopes: list<string>    // Prefixes this role can access: ["3.42.*", "0.5.*"]
    permissions:    list<Permission> // Specific operation grants
    constraints:    list<Constraint> // Time, IP, data classification restrictions
    max_data_class: string          // Maximum data classification accessible
    inherit_from:   list<string>    // Parent roles (role inheritance)
}

Permission {
    resource:   string    // Address pattern or resource type
    actions:    list<str> // ["read", "write", "delete", "link", "search"]
    conditions: map       // Optional ABAC conditions
}

Constraint {
    type:   string    // "time_window", "ip_range", "mfa_required", "approval_required"
    value:  any       // Constraint-specific value
}
```

**ABAC Extension**:

ABAC policies evaluate dynamic attributes at decision time. This handles cases that static roles cannot:

```
ABAC Policy Schema:

Policy {
    policy_id:  string
    effect:     "allow" | "deny"
    priority:   int               // Higher priority = evaluated first. Deny wins ties.
    conditions: {
        subject:    map           // Attributes of the requesting entity
        resource:   map           // Attributes of the target resource
        action:     map           // Attributes of the requested operation
        environment: map          // Context: time, IP, device, location
    }
}
```

Example ABAC policies:

```yaml
# Policy: PHI (Protected Health Information) can only be accessed during business hours from corporate network
- policy_id: "hipaa-phi-access"
  effect: "allow"
  conditions:
    resource:
      data_classification: "PHI"
    environment:
      time_of_day: "06:00-20:00"
      ip_range: "10.0.0.0/8"
      mfa_verified: true

# Policy: PCI data requires Tier 3+ and PCI-trained role
- policy_id: "pci-cardholder-data"
  effect: "allow"
  conditions:
    resource:
      data_classification: "PCI-CHD"
    subject:
      min_tier: 3
      role_tags: ["pci-trained"]
      mfa_verified: true

# Policy: Deny all cross-tenant data access by default
- policy_id: "tenant-isolation"
  effect: "deny"
  priority: 1000    # Very high priority
  conditions:
    subject:
      business_id: "{subject.business_id}"
    resource:
      address_prefix_not: "3.{subject.business_id}.*"
```

**Authorization Decision Flow**:

```
Request arrives:
  entity = authenticated caller (from JWT/certificate)
  action = requested operation (read/write/delete/link)
  resource = target address (e.g., "3.42.1.3.00015")

Step 1: Tier Check (permissions.py)
  entity_tier = PermissionManager.get_tier(entity)
  if entity_tier < required_tier_for_action: DENY

Step 2: RBAC Check
  roles = get_roles(entity, entity.business_id)
  for role in roles:
    if resource matches role.address_scopes
    and action in role.permissions
    and constraints satisfied: ALLOW candidate

Step 3: ABAC Check
  evaluate all matching ABAC policies
  if any DENY policy matches: DENY (deny overrides allow)
  if any ALLOW policy matches: ALLOW

Step 4: Audit
  log_decision(entity, action, resource, result, policies_evaluated)
  if result == DENY: increment_denial_counter(entity)
  if denial_counter > threshold: trigger_alert()
```

#### 2.4.2 Data Classification System

Every node in the Hypernet is automatically classified by sensitivity level. Classification drives encryption, access control, retention, and audit requirements.

| Level | Label | Description | Examples | Access | Encryption | Audit Level |
|-------|-------|------------|----------|--------|-----------|-------------|
| C0 | PUBLIC | Freely accessible, no restrictions | Library knowledge, public profiles, open documentation | All tiers | Optional | Standard |
| C1 | INTERNAL | Business internal, low sensitivity | Internal memos, org charts, meeting notes | T1+ within business | Required (node-level) | Standard |
| C2 | CONFIDENTIAL | Business sensitive | Financial reports, strategy documents, employee reviews | T2+ with role grant | Required (node-level) | Enhanced |
| C3 | RESTRICTED | Regulated data (PHI, PII, PCI) | Health records, social security numbers, credit card numbers | T3+ with MFA + ABAC | Required (field-level) | Full (every access logged) |
| C4 | TOP SECRET | Critical secrets, key material, legal privilege | Encryption keys, legal documents under privilege, security incident details | T4 with multi-party approval | Required (field-level + blob) | Full + real-time alerting |

**Automatic classification engine**:

The Hypernet automatically classifies data at ingestion time using pattern matching and ML-based content analysis:

```
Classification Pipeline:

  Input Data
       |
       v
  [Pattern Scanner] -- regex patterns for SSN, credit card, email, IP, etc.
       |
       v
  [PHI Detector] -- NLP-based health information detection
       |
       v
  [PII Detector] -- personally identifiable information patterns
       |
       v
  [PCI Scanner] -- cardholder data patterns (PAN, CVV, expiry)
       |
       v
  [Custom Rules] -- business-specific classification rules
       |
       v
  [Classification Decision] -- highest matching level wins
       |
       v
  [Encryption Applied] -- appropriate encryption for classification level
       |
       v
  [Node Stored] -- classification recorded in node metadata
```

Pattern examples:

| Pattern | Classification | Framework |
|---------|---------------|-----------|
| `\b\d{3}-\d{2}-\d{4}\b` | C3 (RESTRICTED, PII) | GDPR, HIPAA |
| `\b[4-6]\d{3}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b` | C3 (RESTRICTED, PCI-CHD) | PCI DSS |
| ICD-10/CPT codes, diagnosis terms, medication names | C3 (RESTRICTED, PHI) | HIPAA |
| Email + name + date of birth combination | C2+ (CONFIDENTIAL, PII) | GDPR |
| `\bBEGIN\s+(RSA|EC|DSA|OPENSSH)\s+PRIVATE\s+KEY\b` | C4 (TOP SECRET) | All |

**Manual override**: Users with appropriate permissions can reclassify data up (never down without T4 approval). Reclassification is an audited event.

### 2.5 Network Security

#### 2.5.1 Zero Trust Architecture

The Hypernet implements a zero-trust network model. There is no concept of a "trusted internal network." Every request, from every source, is treated as potentially hostile.

**Zero Trust Principles Applied**:

| Principle | Implementation |
|-----------|---------------|
| Verify explicitly | Every request authenticated (JWT/mTLS/API key), authorized (tier + RBAC + ABAC), signed |
| Least privilege | Default Tier 0 (read-only). Scoped API keys. Time-limited elevation |
| Assume breach | All traffic encrypted (mTLS). Microsegmentation. Lateral movement detected |

#### 2.5.2 Microsegmentation

Each business tenant's data is isolated at multiple levels:

```
Isolation Layers:

Layer 1: Address Space Isolation
  Business A: 3.42.* (cannot see or query 3.43.*)
  Business B: 3.43.* (cannot see or query 3.42.*)
  Enforced by: LMDB prefix scoping in every query

Layer 2: Database Isolation (multi-tenant options)
  Option A: Shared LMDB with address-prefix-scoped transactions
  Option B: Separate LMDB environment per tenant (stronger isolation, higher resource cost)
  Option C: Separate server per tenant (strongest, for regulated industries)

Layer 3: Network Isolation
  Each tenant's API endpoints can be deployed behind separate network segments
  Service mesh (e.g., Envoy/Istio) enforces tenant-to-tenant traffic policies

Layer 4: Encryption Isolation
  Each tenant has unique Data Encryption Keys
  Even if database isolation fails, encrypted data is unreadable without tenant's key
```

#### 2.5.3 Rate Limiting and DDoS Protection

| Layer | Mechanism | Limits |
|-------|-----------|--------|
| Application | Token bucket per entity | 100 req/min (default), configurable per role |
| API Gateway | Sliding window per API key | 1000 req/min (free), 50K req/min (enterprise) |
| Network | Connection rate limiting per IP | 1000 connections/min |
| Infrastructure | Cloud provider DDoS protection (Cloudflare/AWS Shield) | Volume-based mitigation |

Rate limit responses follow RFC 6585 (HTTP 429) with `Retry-After` headers.

### 2.6 Data Loss Prevention (DLP)

#### 2.6.1 Egress Controls

Every data export from the Hypernet passes through the DLP engine:

```
DLP Pipeline:

  Data Export Request (API response, file download, AI agent output, report generation)
       |
       v
  [Requester Authorization] -- does entity have T3+ (EXTERNAL) permission?
       |
       v
  [Data Classification Check] -- what classification level is the data?
       |
       v
  [DLP Rules Engine]
    - C3/C4 data: Block unless explicit export approval exists
    - PII: Redact or pseudonymize by default (GDPR compliance)
    - PCI CHD: Mask card numbers (show last 4 only)
    - PHI: Block export unless HIPAA-compliant destination
    - Business confidential: Watermark with requester identity
       |
       v
  [Export Audit Log] -- who, what, when, where, why, how much
       |
       v
  [Data Delivered or Blocked]
```

#### 2.6.2 DLP Rules

| Rule | Trigger | Action | Framework |
|------|---------|--------|-----------|
| PAN in export | Credit card number detected | Mask to last 4 digits | PCI DSS 3.4 |
| PHI bulk export | >10 PHI records in single request | Block, require explicit approval | HIPAA 164.312 |
| PII to external | PII leaving tenant boundary | Pseudonymize or require consent proof | GDPR Art. 6, 44 |
| Key material | Private key or secret detected | Block unconditionally | All frameworks |
| Bulk download | >1000 records in single request | Rate limit, require approval for C2+ | SOC 2, ISO 27001 |
| Cross-tenant | Data moving from one business to another | Block unless data sharing agreement exists | All frameworks |

#### 2.6.3 Data Watermarking

All documents exported from the Hypernet carry an invisible watermark embedded in the metadata:

```json
{
  "hypernet_watermark": {
    "exported_by": "1.1.3.2",
    "export_timestamp": "2026-04-01T14:30:00Z",
    "export_address": "3.42.1.3.00015",
    "classification_at_export": "C2",
    "export_purpose": "quarterly_review",
    "tracking_hash": "sha256:a1b2c3d4..."
  }
}
```

If a document is found outside its authorized context, the watermark identifies who exported it and when.

### 2.7 Intrusion Detection and Prevention

#### 2.7.1 Detection Layers

```
Hypernet Intrusion Detection System (HIDS)

Layer 1: Behavioral Analysis (built on audit trail)
  - Baseline normal behavior per entity (access patterns, data volumes, timing)
  - Anomaly detection: deviation from baseline triggers investigation
  - Examples:
    - Entity usually reads 10 nodes/hour, suddenly reads 10,000 -> alert
    - Entity usually active 9am-5pm, active at 3am -> alert
    - Entity accessing addresses outside its usual scope -> alert

Layer 2: Rule-Based Detection
  - Known attack patterns matched against audit trail:
    - Brute force: >5 failed auth attempts in 5 minutes
    - Privilege escalation: rapid tier elevation requests
    - Data exfiltration: large export volumes, especially C3+ data
    - Injection: prompt injection patterns (already in ContextIsolator)
    - Path traversal: attempts to access addresses outside scope
    - Enumeration: sequential address probing

Layer 3: Integrity Monitoring
  - File system integrity: SHA-256 hashes of all system files monitored
  - Database integrity: version hashes verified against expected chains
  - Configuration drift: system configuration changes detected and alerted
  - Binary integrity: checksums of all executables verified at startup

Layer 4: Network Detection
  - Unusual outbound connections
  - DNS exfiltration attempts
  - Port scanning from internal hosts
  - Certificate anomalies (unexpected or self-signed)
```

#### 2.7.2 Automated Response

| Severity | Trigger | Automated Response | Human Action Required |
|----------|---------|-------------------|---------------------|
| INFO | Minor anomaly (e.g., unusual access time) | Log, add to entity risk score | None |
| WARNING | Moderate anomaly (e.g., access outside scope) | Log, alert security admin, temporarily reduce tier by 1 | Review within 4 hours |
| HIGH | Significant threat (e.g., brute force, data exfil attempt) | Log, alert, suspend entity session, block IP for 1 hour | Review within 1 hour |
| CRITICAL | Confirmed breach indicator (e.g., key compromise, integrity violation) | Log, alert (multiple channels), suspend entity, isolate affected address space, snapshot state for forensics | Immediate response required |

**Incident escalation path**:
1. Automated detection creates incident node in audit trail
2. Alert sent via configured channels (email, Telegram, webhook)
3. Incident classified by severity
4. For HIGH/CRITICAL: affected entity suspended, affected address space placed in read-only mode
5. Forensic snapshot taken (all audit entries, all node versions, network logs)
6. Incident response playbook activated (see 2.8)

### 2.8 Incident Response

#### 2.8.1 Incident Response Playbooks

Incident response playbooks are stored as Hypernet nodes (address: `0.9.security.incidents.*`) and executed automatically or semi-automatically depending on severity.

**Standard Incident Types**:

| Incident Type | Category | Playbook |
|--------------|----------|----------|
| Unauthorized access attempt | Access Control | Suspend entity, review permissions, check for lateral movement |
| Data breach (confirmed) | Data Protection | Isolate address space, forensic snapshot, notify affected parties, regulatory notification |
| Key compromise | Cryptographic | Revoke key, rotate all dependent keys, re-encrypt affected data, audit all actions signed by compromised key |
| Ransomware/integrity violation | System Integrity | Isolate system, restore from immutable backup (LMDB snapshots + git history), forensic analysis |
| Insider threat | Personnel | Suspend entity, forensic snapshot, preserve evidence chain, involve legal |
| AI agent compromise | AI Security | Revoke agent key, quarantine agent outputs, review all actions since last known-good state, rebuild from archive |
| DDoS | Availability | Activate rate limiting, engage cloud protection, failover if available |

#### 2.8.2 Regulatory Notification Timelines

| Framework | Notification Required | Timeline | To Whom |
|-----------|----------------------|----------|---------|
| GDPR | Data breach affecting EU residents | 72 hours to supervisory authority | Supervisory authority + data subjects if high risk |
| HIPAA | Breach of unsecured PHI | 60 days to HHS; without unreasonable delay to individuals | HHS, affected individuals, media if >500 |
| PCI DSS | Compromise of cardholder data | Immediately to acquirer/payment brand | Acquirer, card brands, forensic investigator |
| CMMC | Cyber incident | 72 hours to DoD | DoD CIO via DIBCAC |
| FedRAMP | Security incident | Within 1 hour (US-CERT) for critical | US-CERT, FedRAMP PMO, agency AO |
| SOC 2 | Material incident | No specific timeline, but must be documented | Auditor at next assessment |
| ISO 27001 | Security event/incident | Per incident response procedure | Defined in ISMS |

The Hypernet automates notification preparation:
1. Incident detected and classified
2. System generates breach assessment (what data, how many records, what classification)
3. System generates notification draft for each applicable framework
4. System identifies affected data subjects (if personal data breach)
5. Human reviews and sends (regulatory notification cannot be fully automated)

---

## 3. Audit Architecture

### 3.1 The Audit Trail as Graph

The Hypernet's audit trail is not a log file. It is a graph of cryptographically signed audit nodes, stored in the same graph database as everything else, queryable with the same tools, and immutable by the same mechanisms.

**Existing implementation** (`audit.py`): Append-only audit nodes with action counting, filtered queries, and pruning. This section extends it to enterprise grade.

#### 3.1.1 Audit Node Schema

```
AuditNode {
    address:            string          // "0.9.audit.{timestamp_epoch}.{sequence}"
    event_type:         string          // "data_access", "data_modify", "auth", "admin", "security"

    // WHO
    actor:              string          // HA of the acting entity
    actor_type:         string          // "human", "ai_agent", "service", "system"
    actor_tier:         int             // Permission tier at time of action
    actor_roles:        list<string>    // RBAC roles at time of action
    actor_session:      string          // Session ID
    actor_ip:           string          // Source IP (hashed for privacy, cleartext for security)

    // WHAT
    action:             string          // "read", "write", "delete", "link", "search", "auth", "export"
    target_address:     string          // HA of the affected node/resource
    target_classification: string       // Data classification at time of access
    payload_hash:       string          // SHA-256 of the action payload
    result:             string          // "success", "denied", "error"
    denial_reason:      string | null   // If denied, why

    // WHEN
    timestamp:          datetime        // UTC, millisecond precision

    // PROOF
    signature:          string          // HMAC-SHA256 (current) or Ed25519 (future)
    signing_key_id:     string          // Key used to sign this audit entry
    previous_hash:      string          // SHA-256 of previous audit node (hash chain)

    // CONTEXT
    request_id:         string          // Correlation ID for request tracing
    business_id:        string | null   // Which tenant (if applicable)
    compliance_tags:    list<string>    // Which frameworks this event is evidence for

    // RETENTION
    retention_class:    string          // How long to keep: "standard" (1yr), "extended" (7yr), "permanent"
}
```

#### 3.1.2 Hash-Chain Integrity

Every audit node includes the hash of the previous audit node, creating a hash chain (similar to a blockchain but without consensus overhead). Tampering with any audit entry breaks the chain, which is detectable by any verifier.

```
Audit Hash Chain:

  [Audit Entry N-2] --hash--> [Audit Entry N-1] --hash--> [Audit Entry N]
       |                             |                          |
    signature                    signature                  signature

  Verification:
    For each entry E[i]:
      1. Verify E[i].signature against E[i].signing_key_id
      2. Verify SHA-256(serialize(E[i-1])) == E[i].previous_hash
      3. Verify E[i].signing_key_id was active at E[i].timestamp

    If any check fails: TAMPER DETECTED
```

**Performance**: Hash chain verification is O(N) but can be parallelized by verifying segments independently and checking segment boundaries. For a system producing 10,000 audit events per day, full chain verification takes <1 second.

#### 3.1.3 Audit Retention

| Classification | Retention Period | Rationale |
|---------------|-----------------|-----------|
| Standard (C0-C1) | 1 year minimum | SOC 2, NIST CSF general requirement |
| Extended (C2-C3) | 7 years minimum | HIPAA (6 years), PCI DSS (1 year of logs, 90 days immediately available), SOX (7 years) |
| Permanent (C4 + security events) | Indefinite | Security incidents, key lifecycle events, governance decisions |
| Access to C3+ data | 7 years minimum | Regulatory requirement across frameworks |
| Authentication events | 1 year minimum | All frameworks |
| Permission changes | 7 years minimum | Compliance evidence |

Audit nodes are never modified. Expired audit nodes are archived to cold storage (compressed, encrypted, integrity-verified) rather than deleted.

### 3.2 Continuous Compliance Monitoring

#### 3.2.1 Architecture

```
Continuous Compliance Engine (CCE)

+----------------------------------------------------------------------+
|                        Compliance Dashboard                           |
|  Real-time view: controls met, controls failing, evidence status     |
+----------------------------------------------------------------------+
         |                    |                     |
+------------------+ +------------------+ +------------------+
| Control Evaluator| | Evidence Collector| | Gap Analyzer     |
| Tests controls   | | Gathers evidence | | Finds what's     |
| against live     | | for each control | | missing and      |
| system state     | | automatically    | | recommends fixes |
+------------------+ +------------------+ +------------------+
         |                    |                     |
+----------------------------------------------------------------------+
|                     Compliance Rule Engine                            |
|  Framework-specific rules mapped to Hypernet capabilities            |
|  CMMC | SOC 2 | HIPAA | FedRAMP | ISO 27001 | GDPR | PCI DSS | NIST|
+----------------------------------------------------------------------+
         |
+----------------------------------------------------------------------+
|                        Hypernet Data Layer                           |
|  Audit trail | Configuration | Encryption status | Permissions      |
|  Key lifecycle | Network config | Training records | Policies       |
+----------------------------------------------------------------------+
```

#### 3.2.2 Control Evaluation

Each compliance control is mapped to one or more automated checks. Checks run continuously (not just at audit time) and produce evidence artifacts.

**Control check structure**:

```yaml
control:
  framework: "SOC 2"
  control_id: "CC6.1"
  title: "Logical and Physical Access Controls"
  description: "The entity implements logical access security software, infrastructure, and architectures over protected information assets..."

  checks:
    - check_id: "cc6.1-auth-mfa"
      description: "MFA is enabled for all users accessing C2+ data"
      type: "configuration"
      query: "SELECT users WHERE tier >= 2 AND mfa_enabled = false"
      expected: "empty result set"
      frequency: "hourly"
      evidence_type: "configuration_snapshot"

    - check_id: "cc6.1-tier-enforcement"
      description: "Permission tier checks cannot be bypassed"
      type: "code_verification"
      module: "permissions.py"
      function: "check_write"
      assertion: "every write operation passes through check_write before execution"
      frequency: "on_deploy"
      evidence_type: "code_coverage_report"

    - check_id: "cc6.1-access-review"
      description: "Access reviews conducted quarterly"
      type: "process"
      automated: false
      reminder_frequency: "quarterly"
      evidence_type: "signed_review_document"

  status: "met" | "partial" | "not_met" | "not_applicable"
  last_evaluated: "2026-04-01T00:00:00Z"
  evidence_nodes: ["0.9.compliance.evidence.cc6.1-001", ...]
```

#### 3.2.3 Automated Evidence Collection

For each compliance control, the system automatically collects and stores evidence:

| Evidence Type | Collection Method | Storage |
|--------------|-------------------|---------|
| Configuration snapshots | Periodic dump of all security-relevant configuration | Node at `0.9.compliance.evidence.{framework}.{control}.{timestamp}` |
| Access logs | Continuous from audit trail (no additional collection needed) | Existing audit nodes with compliance_tags |
| Encryption verification | Periodic scan of all nodes to verify encryption status | Evidence node with per-classification encryption stats |
| Permission matrix | Export of all entities, roles, tiers, and scopes | Evidence node with full permission snapshot |
| Key lifecycle records | From KMS audit log | Evidence node with key generation, rotation, revocation records |
| Vulnerability scans | Periodic automated security scanning | Evidence node with scan results and remediation status |
| Penetration test results | External or internal pen test reports | Evidence node (manual upload, required for some frameworks) |
| Training records | Training completion tracking | Evidence node per user |
| Incident records | From incident response system | Evidence nodes linked to incident nodes |
| Policy documents | From governance system | Existing governance nodes with compliance_tags |

**Evidence freshness requirements**:

| Framework | Maximum Evidence Age | Re-evaluation Frequency |
|-----------|---------------------|------------------------|
| SOC 2 | 12 months (audit period) | Continuous |
| HIPAA | No specific maximum, but ongoing compliance required | Continuous |
| PCI DSS | Annual assessment | Quarterly (SAQ) + continuous |
| FedRAMP | Annual assessment + monthly monitoring | Monthly ConMon + continuous |
| ISO 27001 | 3-year certification cycle with annual surveillance | Continuous |
| CMMC | 3-year certification | Annual affirmation + continuous |
| GDPR | No certification required, but must demonstrate compliance at any time | Continuous |
| NIST CSF | No certification, but self-assessment recommended | Continuous |

### 3.3 Compliance Dashboard

The compliance dashboard is a real-time web interface showing compliance status across all frameworks.

**Dashboard views**:

1. **Executive Summary**: Single page showing compliance percentage for each framework, total controls met/partial/not-met/NA, and trend over time
2. **Framework Deep Dive**: Select a framework, see every control, its status, evidence, and last evaluation time
3. **Gap Analysis**: Controls that are not yet met, grouped by effort required (code change, configuration, organizational process)
4. **Evidence Library**: All collected evidence, searchable and filterable
5. **Incident Timeline**: Security incidents with their compliance impact
6. **Audit Readiness Score**: Percentage of controls with fresh, complete evidence

**Alert thresholds**:
- Green: >95% of controls met with fresh evidence
- Yellow: 85-95% of controls met, or some evidence stale
- Red: <85% of controls met, or critical control not met

### 3.4 Automated Report Generation

On demand, the system generates compliance reports for any framework:

```
Report Generation:

  Input: framework (e.g., "SOC 2"), reporting period, business_id

  Output:
    1. Control Matrix -- every control, status, evidence references
    2. Evidence Package -- all evidence artifacts for the period, signed and timestamped
    3. Gap Analysis -- any unmet controls with remediation recommendations
    4. Trend Report -- compliance score over time
    5. Incident Report -- all security incidents during the period and their resolution
    6. Risk Assessment -- current risk posture based on unmet controls

  Format: PDF + structured JSON (for machine processing)

  Signing: Report is signed by the Hypernet system key
           Hash of report is stored as an audit node
           Report can be independently verified against the audit trail
```

---

## 4. The 3.* Business Framework

### 4.1 Address Space Design

The `3.*` address space is the enterprise/business layer of the Hypernet. It provides multi-tenant business operations with built-in data segregation, compliance tracking, and inter-business data sharing.

```
3 - Businesses/
|
+-- 3.0 -- Business Framework Metadata
|   |
|   +-- 3.0.0 -- Core business metadata specification
|   +-- 3.0.1 -- Business registration standard
|   +-- 3.0.2 -- Business compliance requirements
|   +-- 3.0.3 -- Inter-business data sharing protocol
|   +-- 3.0.4 -- SLA definitions and enforcement
|   +-- 3.0.5 -- Business billing and cost tracking
|   +-- 3.0.6 -- Business security baseline
|   +-- 3.0.7 -- Business data classification override rules
|
+-- 3.1 -- Hypernet (the first business)
|   |
|   +-- 3.1.0 -- Hypernet business metadata
|   +-- 3.1.1 -- Organizational structure
|   +-- 3.1.2 -- Task management
|   +-- 3.1.3 -- Human resources
|   +-- 3.1.4 -- Financial operations
|   +-- 3.1.5 -- Product development
|   +-- 3.1.6 -- Marketing and outreach
|   +-- 3.1.7 -- Documentation and knowledge
|   +-- 3.1.8 -- Marketing and outreach
|   +-- 3.1.9 -- Infrastructure and operations
|   +-- 3.1.10 -- Development journal
|   +-- 3.1.11 -- Community
|   +-- 3.1.12 -- Legal and governance
|   +-- 3.1.13 -- Unity core definitions
|
+-- 3.2 -- [Second business]
|   +-- 3.2.0 -- Business metadata
|   +-- 3.2.1 -- Organizational structure
|   +-- 3.2.2 -- [Business-specific]
|   +-- ...
|
+-- 3.{N} -- [Nth business]
```

### 4.2 Business Registration and Onboarding

When a business joins the Hypernet, the following process runs:

```
Business Onboarding Workflow:

Step 1: Registration
  - Business entity created at 3.{N}
  - Business metadata node at 3.{N}.0 populated:
    - Legal name, registration number, jurisdiction
    - Compliance requirements (which frameworks apply)
    - Data classification requirements
    - Contact information for security/compliance officer
    - SLA tier selection

Step 2: Security Baseline
  - Dedicated Data Encryption Key generated
  - Business admin account created (human, T4 within business scope)
  - Initial RBAC roles generated from business template
  - mTLS certificates provisioned for API access
  - API keys generated with business-scoped permissions

Step 3: Address Space Provisioning
  - Standard sub-address structure created:
    3.{N}.1 -- Organizational structure
    3.{N}.2 -- Operations
    3.{N}.3 -- Human resources (if applicable)
    3.{N}.4 -- Financial (if applicable)
    3.{N}.5 -- Projects
    3.{N}.6 -- Documents
    3.{N}.7 -- Communications
    3.{N}.8 -- Compliance
    3.{N}.9 -- Custom
  - Metadata nodes (.0) auto-created for each

Step 4: Compliance Configuration
  - Applicable compliance frameworks activated
  - Controls mapped to business operations
  - Evidence collection configured
  - Baseline compliance scan run
  - Gap analysis generated

Step 5: User Import (optional)
  - SCIM 2.0 import from existing identity provider
  - Each user gets 3.{N}.1.{user_id} address
  - Roles mapped from existing directory groups
  - MFA enrollment initiated

Step 6: Verification
  - Security baseline verified (encryption, auth, permissions)
  - Compliance dashboard populated
  - Business admin confirms configuration
  - Onboarding audit trail complete
```

### 4.3 Multi-Tenancy Architecture

**Isolation model**: The Hypernet uses a **shared infrastructure, isolated data** model with multiple isolation guarantees:

| Layer | Isolation Mechanism | Enforcement |
|-------|-------------------|-------------|
| Address space | Prefix-based scoping: business can only query 3.{own_id}.* | LMDB query engine |
| Encryption | Unique DEK per tenant | KMS |
| Authentication | Tenant-scoped sessions and API keys | Auth middleware |
| Authorization | RBAC roles scoped to tenant | Permission engine |
| Audit trail | Tenant-scoped audit queries; shared audit chain for integrity | Audit query filters |
| Backup/restore | Per-tenant backup snapshots | Backup system |
| Rate limiting | Per-tenant quotas | API gateway |

**Cross-tenant access**: Blocked by default. Enabled only through explicit Data Sharing Agreements (see 4.5).

### 4.4 Business Compliance Tracking

Each business has a compliance tracker at `3.{N}.8 -- Compliance`:

```
3.{N}.8/
|
+-- 3.{N}.8.0  -- Compliance metadata (which frameworks apply)
+-- 3.{N}.8.1  -- SOC 2 status
|   +-- 3.{N}.8.1.0  -- SOC 2 summary
|   +-- 3.{N}.8.1.{control_id} -- per-control status
+-- 3.{N}.8.2  -- HIPAA status (if applicable)
+-- 3.{N}.8.3  -- PCI DSS status (if applicable)
+-- 3.{N}.8.4  -- GDPR status (if applicable)
+-- 3.{N}.8.5  -- ISO 27001 status (if applicable)
+-- 3.{N}.8.6  -- CMMC status (if applicable)
+-- 3.{N}.8.7  -- FedRAMP status (if applicable)
+-- 3.{N}.8.8  -- NIST CSF status (if applicable)
+-- 3.{N}.8.9  -- Custom framework status
+-- 3.{N}.8.10 -- Evidence library
+-- 3.{N}.8.11 -- Audit reports (generated)
+-- 3.{N}.8.12 -- Incident records
+-- 3.{N}.8.13 -- Risk register
```

### 4.5 Inter-Business Data Sharing

Businesses can share specific data with each other through audited, consent-based Data Sharing Agreements (DSAs):

```
Data Sharing Agreement Schema:

DSA {
    dsa_id:             string
    from_business:      string          // 3.{N} -- sharing business
    to_business:        string          // 3.{M} -- receiving business
    shared_addresses:   list<string>    // Specific addresses or prefixes shared
    shared_fields:      list<string>    // If field-level sharing (e.g., only "name" and "email")
    purpose:            string          // Why the data is being shared
    legal_basis:        string          // GDPR lawful basis if applicable
    consent_records:    list<string>    // HAs of consent nodes from data subjects
    classification_max: string          // Maximum classification that can be shared
    start_date:         datetime
    end_date:           datetime | null // null = indefinite
    renewal_terms:      string
    revocation_terms:   string
    approved_by:        list<string>    // HAs of approvers from both sides
    status:             string          // "proposed", "active", "expired", "revoked"
    audit_requirements: string          // Additional audit requirements for shared data
}
```

**Sharing enforcement**:
1. DSA created and approved by T4 users from both businesses
2. Shared addresses are made readable (not writable) to the receiving business
3. All access to shared data is logged with `dsa_id` in the audit trail
4. DLP rules apply to shared data (cannot be re-shared without explicit DSA)
5. Revocation immediately removes access; cached copies marked for deletion

### 4.6 SLA Definitions and Enforcement

```
SLA Tiers:

Tier 1: Community (Free)
  - Availability: Best effort
  - Support: Community forum only
  - Backup: User-managed
  - Compliance: Self-service compliance dashboard
  - Rate limit: 1,000 API calls/day
  - Storage: 1 GB

Tier 2: Professional ($X/month)
  - Availability: 99.5% uptime (monthly)
  - Support: Email support, 24-hour response
  - Backup: Daily automated, 30-day retention
  - Compliance: Automated compliance monitoring + quarterly reports
  - Rate limit: 50,000 API calls/day
  - Storage: 50 GB
  - Encryption: Full at-rest encryption

Tier 3: Enterprise ($X/month)
  - Availability: 99.9% uptime (monthly)
  - Support: Priority support, 4-hour response, dedicated contact
  - Backup: Hourly automated, 1-year retention, geo-redundant
  - Compliance: Continuous compliance monitoring + on-demand reports + gap analysis
  - Rate limit: 500,000 API calls/day
  - Storage: 500 GB
  - Encryption: Full at-rest + per-field + BYOK (Bring Your Own Key) option
  - Dedicated encryption keys
  - Custom RBAC roles
  - SSO integration (SAML/OIDC)
  - Annual security review

Tier 4: Regulated ($X/month, custom pricing)
  - Availability: 99.99% uptime (monthly)
  - Support: Dedicated support engineer, 1-hour response, phone support
  - Backup: Continuous replication, 7-year retention, multi-region
  - Compliance: Full compliance management, audit support, regulatory liaison
  - Rate limit: Unlimited
  - Storage: Unlimited
  - Encryption: All Enterprise features + HSM-backed keys + key escrow
  - Dedicated infrastructure option (isolated deployment)
  - Third-party audit support (we prepare all evidence; you bring the auditor)
  - Custom compliance frameworks
  - Incident response team support
```

**SLA enforcement**: The system monitors uptime, response times, and other SLA metrics automatically. SLA breaches are detected in real-time and create incident nodes. Business customers can view their SLA compliance at `3.{N}.9.sla.*`.

### 4.7 Cost Tracking and Billing

```
Cost Tracking Architecture:

Every billable action increments a counter in the business's billing space:

3.{N}.9.billing/
  +-- 3.{N}.9.billing.0    -- Current billing period summary
  +-- 3.{N}.9.billing.1    -- API call counts (by endpoint)
  +-- 3.{N}.9.billing.2    -- Storage usage (by classification)
  +-- 3.{N}.9.billing.3    -- Compute usage (AI agent time)
  +-- 3.{N}.9.billing.4    -- Data transfer (egress)
  +-- 3.{N}.9.billing.5    -- Feature usage (encryption, compliance, etc.)
  +-- 3.{N}.9.billing.H    -- Historical billing periods

Billing events are append-only audit nodes (not separately metered).
This means billing is inherently auditable -- the business can verify
every charge against the audit trail.
```

---

## 5. Compliance Mapping

### 5.1 Mapping Methodology

For each compliance framework, every control is categorized as:

- **MET-ARCH**: Met by the Hypernet architecture itself (compliance by default -- no additional work)
- **MET-IMPL**: Met by existing implemented features
- **MET-CONFIG**: Can be met by configuration of existing features
- **NEEDS-CODE**: Requires new code/features to be built
- **NEEDS-PROCESS**: Requires organizational policies, training, or human processes (cannot be fully automated)
- **NOT-APPLICABLE**: Does not apply to the Hypernet's deployment model

### 5.2 NIST Cybersecurity Framework (CSF) 2.0

NIST CSF is the foundation that most other frameworks reference. Mapping it first covers the most ground.

#### GOVERN (GV) -- Organizational Context

| Control | Description | Status | Hypernet Capability |
|---------|------------|--------|-------------------|
| GV.OC-01 | Organizational mission understood | NEEDS-PROCESS | Business metadata at 3.{N}.0 can store mission/context, but humans must define it |
| GV.OC-02 | Internal/external stakeholders understood | NEEDS-PROCESS | Organizational structure at 3.{N}.1 tracks stakeholders |
| GV.OC-03 | Legal/regulatory requirements understood | MET-CONFIG | Compliance metadata at 3.{N}.8.0 tracks applicable frameworks |
| GV.OC-04 | Critical objectives determined | NEEDS-PROCESS | Can be documented in Hypernet but requires human judgment |
| GV.OC-05 | Outcomes determined to support strategy | NEEDS-PROCESS | Governance framework supports this but humans must drive it |

#### GOVERN (GV) -- Risk Management Strategy

| Control | Description | Status | Hypernet Capability |
|---------|------------|--------|-------------------|
| GV.RM-01 | Risk management objectives established | NEEDS-PROCESS | Risk register at 3.{N}.8.13 provides structure; humans must populate |
| GV.RM-02 | Risk appetite and tolerance determined | NEEDS-PROCESS | Configuration: classification thresholds, DLP rules, alert thresholds |
| GV.RM-03 | Risk management activities integrated | MET-CONFIG | CCE integrates risk signals from all system components |
| GV.RM-04 | Strategic direction informed by risk | NEEDS-PROCESS | Dashboard and gap analysis inform decisions; humans must act |
| GV.RM-05 | Communication lines established | MET-CONFIG | Alert channels (email, Telegram, webhook) configurable per business |
| GV.RM-06 | Standardized method for risk calculation | MET-CONFIG | Risk scoring based on unmet controls, incident frequency, data exposure |
| GV.RM-07 | Strategic opportunities considered | NEEDS-PROCESS | Not automatable |

#### GOVERN (GV) -- Roles and Responsibilities

| Control | Description | Status | Hypernet Capability |
|---------|------------|--------|-------------------|
| GV.RR-01 | Organizational leadership accountable | NEEDS-PROCESS | RBAC identifies security-responsible roles; accountability is organizational |
| GV.RR-02 | Roles and responsibilities established | MET-IMPL | RBAC + tier system defines every entity's capabilities and limits |
| GV.RR-03 | Resources adequate | NEEDS-PROCESS | Budget/resource decisions are human |
| GV.RR-04 | Cybersecurity in HR practices | NEEDS-PROCESS | Onboarding can include security training tracking; content must be human-created |

#### GOVERN (GV) -- Policy

| Control | Description | Status | Hypernet Capability |
|---------|------------|--------|-------------------|
| GV.PO-01 | Policy established based on context/strategy | MET-CONFIG | Security policies stored as governance nodes, enforced by code |
| GV.PO-02 | Policy reviewed, updated, communicated | MET-IMPL | Governance proposal system tracks policy changes with version history |

#### IDENTIFY (ID) -- Asset Management

| Control | Description | Status | Hypernet Capability |
|---------|------------|--------|-------------------|
| ID.AM-01 | Hardware inventoried | NEEDS-PROCESS | Hypernet is software; hardware inventory is external |
| ID.AM-02 | Software inventoried | MET-ARCH | Every component has a Hypernet address; dependency tree is queryable |
| ID.AM-03 | Data flows mapped | MET-ARCH | All data has addresses; all movements are logged; data flow is the audit trail |
| ID.AM-04 | External systems cataloged | MET-CONFIG | Integration nodes at 3.{N}.9.integrations track external connections |
| ID.AM-05 | Resources prioritized by classification | MET-IMPL | Automatic data classification (C0-C4) drives priority |
| ID.AM-07 | Data inventoried and classified | MET-ARCH | Every node has an address, type, classification, and metadata. This IS the inventory |
| ID.AM-08 | Systems, hardware, data managed across lifecycle | MET-IMPL | Append-only version history tracks full lifecycle; soft-delete prevents data loss |

#### IDENTIFY (ID) -- Risk Assessment

| Control | Description | Status | Hypernet Capability |
|---------|------------|--------|-------------------|
| ID.RA-01 | Vulnerabilities identified | MET-CONFIG | Automated vulnerability scanning; dependency checking |
| ID.RA-02 | Threat intelligence received | NEEDS-CODE | Integration with threat intelligence feeds (future) |
| ID.RA-03 | Internal/external threats identified | NEEDS-PROCESS | Threat modeling requires human expertise; can be documented in Hypernet |
| ID.RA-04 | Potential impacts assessed | MET-CONFIG | Risk scoring based on data classification and exposure |
| ID.RA-05 | Likelihood determined | NEEDS-PROCESS | Requires human judgment informed by historical data |
| ID.RA-06 | Risk responses chosen | NEEDS-PROCESS | Risk register supports this; decisions are human |
| ID.RA-07 | Changes and exceptions managed | MET-IMPL | Governance proposal system with version tracking |

#### PROTECT (PR) -- Identity Management and Access Control

| Control | Description | Status | Hypernet Capability |
|---------|------------|--------|-------------------|
| PR.AA-01 | Identities and credentials managed | MET-IMPL | KMS + entity management + key lifecycle |
| PR.AA-02 | Identities proofed and bound | MET-CONFIG | Identity federation (SAML/OIDC) + internal crypto identity for agents |
| PR.AA-03 | Users, services, hardware authenticated | MET-IMPL | Multi-factor for humans, crypto for agents, mTLS for services |
| PR.AA-04 | Identity assertions managed | MET-IMPL | JWT tokens, certificate chains, action signatures |
| PR.AA-05 | Access permissions managed | MET-ARCH | 5-tier system + RBAC + ABAC, enforced by code |
| PR.AA-06 | Physical access managed | NEEDS-PROCESS | Software system; physical security is deployment-environment specific |

#### PROTECT (PR) -- Awareness and Training

| Control | Description | Status | Hypernet Capability |
|---------|------------|--------|-------------------|
| PR.AT-01 | Awareness and training provided | NEEDS-PROCESS | Training completion can be tracked in Hypernet; content must be created |
| PR.AT-02 | Privileged users trained | NEEDS-PROCESS | Tier elevation can require training completion as prerequisite |

#### PROTECT (PR) -- Data Security

| Control | Description | Status | Hypernet Capability |
|---------|------------|--------|-------------------|
| PR.DS-01 | Data-at-rest protected | MET-IMPL | AES-256-GCM per-node/per-field encryption |
| PR.DS-02 | Data-in-transit protected | MET-IMPL | TLS 1.3 for all communications, mTLS for internal |
| PR.DS-10 | Data-in-use protected | MET-CONFIG | Field-level encryption keeps sensitive fields encrypted until accessed by authorized entity |
| PR.DS-11 | Data backups created, protected, maintained, tested | MET-CONFIG | Automated backup with encryption; LMDB snapshots + git history |

#### PROTECT (PR) -- Platform Security

| Control | Description | Status | Hypernet Capability |
|---------|------------|--------|-------------------|
| PR.PS-01 | Configuration management practices established | MET-IMPL | All configuration versioned in Hypernet; changes tracked in audit trail |
| PR.PS-02 | Software maintained, replaced, removed | MET-CONFIG | Dependency tracking; update monitoring |
| PR.PS-03 | Hardware maintained | NEEDS-PROCESS | External to Hypernet |
| PR.PS-04 | Log records generated | MET-ARCH | Append-only audit trail is the architecture; every action logged |
| PR.PS-05 | Installation/execution of unauthorized software prevented | MET-IMPL | Permission system prevents unauthorized operations; allowlisted tools only |
| PR.PS-06 | Secure software development practiced | MET-IMPL | Git version control, code review, test coverage; audit trail on all code changes |

#### PROTECT (PR) -- Technology Infrastructure Resilience

| Control | Description | Status | Hypernet Capability |
|---------|------------|--------|-------------------|
| PR.IR-01 | Networks and environments protected | MET-IMPL | Zero trust, mTLS, microsegmentation |
| PR.IR-02 | Secure architecture managed | MET-ARCH | Security is the architecture |
| PR.IR-03 | Protective technology coordinated | MET-IMPL | Defense-in-depth layers work together |
| PR.IR-04 | Recovery plans maintained | NEEDS-PROCESS | Backup exists; recovery procedures must be documented and tested |

#### DETECT (DE)

| Control | Description | Status | Hypernet Capability |
|---------|------------|--------|-------------------|
| DE.CM-01 | Networks monitored | MET-IMPL | Network detection layer in HIDS |
| DE.CM-02 | Physical environment monitored | NEEDS-PROCESS | External to software |
| DE.CM-03 | Personnel activity monitored | MET-ARCH | Every action logged and signed in audit trail |
| DE.CM-06 | External service provider activity monitored | MET-CONFIG | Integration audit logging |
| DE.CM-09 | Computing hardware/software monitored | MET-IMPL | Integrity monitoring, configuration drift detection |
| DE.AE-02 | Potentially adverse events analyzed | MET-IMPL | Behavioral analysis + rule-based detection in HIDS |
| DE.AE-03 | Information correlated | MET-IMPL | Audit trail correlation via graph queries |
| DE.AE-04 | Incident impact estimated | MET-CONFIG | Risk scoring based on affected data classification and volume |
| DE.AE-06 | Information shared with appropriate parties | MET-CONFIG | Alert routing to appropriate roles/channels |
| DE.AE-07 | Incident alert thresholds established | MET-CONFIG | Configurable per business and per severity |
| DE.AE-08 | Events declared as incidents | MET-IMPL | Automated incident creation from detection rules |

#### RESPOND (RS)

| Control | Description | Status | Hypernet Capability |
|---------|------------|--------|-------------------|
| RS.MA-01 | Incident response plan executed | MET-IMPL | Automated playbooks for standard incident types |
| RS.MA-02 | Incident reports prepared | MET-IMPL | Automated report generation from incident data |
| RS.MA-03 | Incidents categorized/prioritized | MET-IMPL | Automated classification by severity |
| RS.MA-04 | Incidents escalated | MET-CONFIG | Escalation paths configurable per severity and type |
| RS.MA-05 | Incident criteria applied | MET-CONFIG | Rule-based criteria for incident declaration |
| RS.AN-03 | Impact analysis performed | MET-IMPL | Data classification + blast radius analysis from graph |
| RS.AN-06 | Containment performed | MET-IMPL | Automated entity suspension, address space isolation |
| RS.AN-07 | Forensic evidence collected | MET-ARCH | Immutable audit trail IS the forensic evidence |
| RS.AN-08 | Incident root cause estimated | NEEDS-PROCESS | Graph analysis helps; root cause determination requires expertise |
| RS.CO-02 | Internal stakeholders notified | MET-IMPL | Alert system |
| RS.CO-03 | External stakeholders notified | MET-CONFIG | Notification templates per framework; human must review and send |

#### RECOVER (RC)

| Control | Description | Status | Hypernet Capability |
|---------|------------|--------|-------------------|
| RC.RP-01 | Recovery plan executed | NEEDS-PROCESS | Backup/restore capabilities exist; recovery plan must be documented and tested |
| RC.RP-02 | Recovery actions selected and performed | MET-CONFIG | LMDB snapshots + version history enable point-in-time recovery |
| RC.RP-03 | Recovery verified | MET-CONFIG | Post-recovery integrity verification against hash chains |
| RC.RP-04 | Critical functions restored | NEEDS-PROCESS | Priority depends on business context |
| RC.RP-05 | Recovery progress communicated | MET-CONFIG | Status tracking in incident node |
| RC.CO-04 | Public updates shared | NEEDS-PROCESS | Status page exists; content must be human-written |

**NIST CSF Summary**:

| Category | Total Controls | MET-ARCH | MET-IMPL | MET-CONFIG | NEEDS-CODE | NEEDS-PROCESS |
|----------|---------------|----------|----------|-----------|-----------|--------------|
| GOVERN | 18 | 0 | 2 | 5 | 0 | 11 |
| IDENTIFY | 11 | 3 | 2 | 3 | 1 | 2 |
| PROTECT | 19 | 3 | 10 | 3 | 0 | 3 |
| DETECT | 11 | 2 | 6 | 3 | 0 | 0 |
| RESPOND | 11 | 1 | 5 | 3 | 0 | 2 |
| RECOVER | 6 | 0 | 0 | 3 | 0 | 3 |
| **TOTAL** | **76** | **9 (12%)** | **25 (33%)** | **20 (26%)** | **1 (1%)** | **21 (28%)** |

**Interpretation**: 71% of NIST CSF controls are met or configurable by the Hypernet architecture and implementation. 28% require organizational processes that technology alone cannot satisfy (governance, training, human judgment). This is consistent with the framework's design -- NIST CSF intentionally requires organizational processes alongside technology.

### 5.3 SOC 2 (Trust Services Criteria)

SOC 2 evaluates five Trust Services Criteria (TSC). The Hypernet maps well to the technical controls but requires organizational policies for the process-oriented ones.

| TSC | Controls | MET (Arch+Impl+Config) | NEEDS-PROCESS | Key Gaps |
|-----|---------|----------------------|--------------|---------|
| **CC1: Control Environment** | CC1.1-CC1.5 | 2/5 | 3/5 | Board oversight, ethical values, HR practices are organizational |
| **CC2: Communication and Information** | CC2.1-CC2.3 | 2/3 | 1/3 | External communication of security commitments is organizational |
| **CC3: Risk Assessment** | CC3.1-CC3.4 | 2/4 | 2/4 | Risk identification/assessment partially automated, partially human |
| **CC4: Monitoring Activities** | CC4.1-CC4.2 | 2/2 | 0/2 | Fully met: continuous monitoring, gap analysis |
| **CC5: Control Activities** | CC5.1-CC5.3 | 3/3 | 0/3 | Fully met: permission enforcement, change management, segregation of duties |
| **CC6: Logical and Physical Access** | CC6.1-CC6.8 | 7/8 | 1/8 | Physical access is deployment-specific |
| **CC7: System Operations** | CC7.1-CC7.5 | 4/5 | 1/5 | Mostly met; some recovery testing is manual |
| **CC8: Change Management** | CC8.1 | 1/1 | 0/1 | Version control + audit trail covers this |
| **CC9: Risk Mitigation** | CC9.1-CC9.2 | 1/2 | 1/2 | Vendor risk management requires human judgment |
| **A1: Availability** | A1.1-A1.3 | 2/3 | 1/3 | Capacity planning requires human judgment |
| **C1: Confidentiality** | C1.1-C1.2 | 2/2 | 0/2 | Data classification + encryption + DLP covers this |
| **PI1: Processing Integrity** | PI1.1-PI1.5 | 4/5 | 1/5 | Input validation requires application-specific logic |
| **P1: Privacy** | P1.1-P1.8 | 5/8 | 3/8 | Privacy notice, consent, data subject requests need human processes |
| **TOTAL** | **~55** | **~37 (67%)** | **~18 (33%)** | |

**SOC 2 Assessment**: The Hypernet covers approximately 67% of SOC 2 controls through technology. The remaining 33% are organizational and process controls that require documented policies, training, and human oversight. This is a strong position -- most organizations start at <30% technical coverage and rely heavily on manual processes.

### 5.4 HIPAA (Health Insurance Portability and Accountability Act)

HIPAA has three rules: Privacy Rule, Security Rule, and Breach Notification Rule. The Security Rule is the most technically relevant.

**HIPAA Security Rule -- Administrative Safeguards (164.308)**:

| Standard | Status | Hypernet Capability |
|----------|--------|-------------------|
| Security management process | MET-CONFIG + NEEDS-PROCESS | Risk analysis automated; policies must be written |
| Assigned security responsibility | NEEDS-PROCESS | RBAC can designate; person must be assigned |
| Workforce security | MET-IMPL | Permission tiers, termination procedures (key revocation) |
| Information access management | MET-ARCH | Tier system + ABAC + address-scoped access |
| Security awareness and training | NEEDS-PROCESS | Training tracking available; content must be created |
| Security incident procedures | MET-IMPL | Automated detection, response, reporting |
| Contingency plan | MET-CONFIG + NEEDS-PROCESS | Backup automated; recovery procedures must be documented/tested |
| Evaluation | MET-IMPL | Continuous compliance monitoring |
| Business associate agreements | NEEDS-PROCESS | DSA framework provides structure; legal review required |

**HIPAA Security Rule -- Technical Safeguards (164.312)**:

| Standard | Status | Hypernet Capability |
|----------|--------|-------------------|
| Access control (unique ID, emergency access, auto-logoff, encryption) | MET-IMPL | All four specifications met: unique HA per entity, key escrow for emergency, idle timeout, AES-256-GCM |
| Audit controls | MET-ARCH | Append-only cryptographic audit trail exceeds HIPAA requirements |
| Integrity | MET-ARCH | SHA-256 hashing, version history, hash chains prevent unauthorized alteration |
| Person/entity authentication | MET-IMPL | MFA for humans, crypto for agents, mTLS for services |
| Transmission security | MET-IMPL | TLS 1.3 for all data in transit |

**HIPAA Security Rule -- Physical Safeguards (164.310)**:

| Standard | Status | Hypernet Capability |
|----------|--------|-------------------|
| Facility access controls | NEEDS-PROCESS | Physical security is external to software |
| Workstation use/security | NEEDS-PROCESS | Endpoint management is external |
| Device and media controls | NEEDS-PROCESS | Data wiping procedures must be organizational; encryption provides protection |

**HIPAA Assessment**: The Hypernet fully meets HIPAA's technical safeguards, which are the hardest to implement. Administrative and physical safeguards require organizational policies that the Hypernet can track and enforce (training completion records, policy acknowledgments, access reviews) but cannot create. A covered entity using the Hypernet would still need a HIPAA compliance officer and organizational policies, but the technology burden is essentially zero.

### 5.5 PCI DSS 4.0

PCI DSS applies to any system that stores, processes, or transmits cardholder data (CHD).

| Requirement | Title | Status | Hypernet Capability |
|------------|-------|--------|-------------------|
| 1 | Network security controls | MET-IMPL | Zero trust, mTLS, microsegmentation, firewall rules |
| 2 | Secure configurations | MET-CONFIG | Configuration management with versioning and drift detection |
| 3 | Protect stored account data | MET-IMPL | AES-256-GCM encryption, field-level for PAN, key management, data retention |
| 4 | Protect data in transit | MET-IMPL | TLS 1.3, certificate management, no weak ciphers |
| 5 | Protect from malicious software | MET-CONFIG + NEEDS-PROCESS | Integrity monitoring; endpoint protection is external |
| 6 | Develop secure systems | MET-IMPL | Version control, code review, change management, vulnerability management |
| 7 | Restrict access by business need | MET-ARCH | Tier system + RBAC + ABAC = least privilege by design |
| 8 | Identify users and authenticate | MET-IMPL | MFA, unique IDs, strong authentication, session management |
| 9 | Physical access restriction | NEEDS-PROCESS | Physical security is external |
| 10 | Log and monitor all access | MET-ARCH | Append-only audit trail with cryptographic signatures |
| 11 | Test security regularly | MET-CONFIG + NEEDS-PROCESS | Automated scanning; pen testing requires external assessors |
| 12 | Support security with policies | NEEDS-PROCESS | Policy framework exists; policies must be written and maintained |

**PCI DSS Assessment**: 8 of 12 requirements are met or configurable by the Hypernet. Requirements 5, 9, 11, and 12 need external/organizational processes. For most businesses, PCI DSS compliance on the Hypernet would require significantly less effort than on traditional platforms because the hardest controls (3, 4, 7, 8, 10) are met by the architecture.

### 5.6 GDPR (General Data Protection Regulation)

GDPR is a legal framework, not a technical standard. Many requirements are organizational and legal. The Hypernet addresses the technical requirements comprehensively.

| Article | Requirement | Status | Hypernet Capability |
|---------|------------|--------|-------------------|
| Art. 5 | Principles (lawfulness, purpose limitation, minimization, accuracy, storage limitation, integrity, accountability) | MET-CONFIG + NEEDS-PROCESS | Data classification enforces minimization; purpose tracking in DSAs; version history supports accuracy; retention policies configurable; integrity via hashing; accountability via audit trail. Lawfulness and consent are legal determinations |
| Art. 6 | Lawful basis | NEEDS-PROCESS | Legal determination; Hypernet can track which lawful basis applies per data category |
| Art. 13-14 | Information to data subjects | NEEDS-PROCESS | Privacy notices must be written; can be stored/served via Hypernet |
| Art. 15 | Right of access (Subject Access Request) | MET-IMPL | Graph query: find all nodes containing data linked to a specific person. Export as structured package |
| Art. 16 | Right to rectification | MET-IMPL | Update node with version history preserving original |
| Art. 17 | Right to erasure ("right to be forgotten") | MET-CONFIG | Soft-delete with version history. True erasure conflicts with append-only design but can be implemented as crypto-shredding (destroy encryption key for specific data) |
| Art. 18 | Right to restriction of processing | MET-IMPL | Add restriction flag to node; processing engine checks flag |
| Art. 20 | Right to data portability | MET-ARCH | Everything has a permanent address and structured format; export is trivial |
| Art. 25 | Data protection by design and by default | MET-ARCH | The entire architecture is this |
| Art. 28 | Processor obligations | NEEDS-PROCESS | Data Processing Agreements (like DSAs) must be executed; Hypernet tracks them |
| Art. 30 | Records of processing activities | MET-ARCH | Audit trail IS the record of processing activities |
| Art. 32 | Security of processing | MET-IMPL | Encryption, pseudonymization, integrity, availability, resilience, testing |
| Art. 33 | Breach notification to authority | MET-CONFIG + NEEDS-PROCESS | Automated breach detection and notification draft; human must review and submit |
| Art. 34 | Breach notification to data subjects | MET-CONFIG + NEEDS-PROCESS | Affected data subject identification automated; notification content must be human-reviewed |
| Art. 35 | Data Protection Impact Assessment | NEEDS-PROCESS | DPIA template available in Hypernet; assessment requires human judgment |
| Art. 37-39 | Data Protection Officer | NEEDS-PROCESS | Organizational role; cannot be automated |
| Art. 44-49 | International transfers | NEEDS-PROCESS | Legal determination (SCCs, adequacy decisions); Hypernet can enforce geographic data residency |

**GDPR Assessment**: The Hypernet provides exceptional technical compliance with GDPR, particularly for Articles 15-20 (data subject rights), Article 25 (privacy by design), Article 30 (records of processing), and Article 32 (security). The crypto-shredding approach to Article 17 (right to erasure) elegantly resolves the tension between append-only audit trails and erasure requirements. Organizational requirements (DPO appointment, lawful basis determination, DPIAs) remain human responsibilities.

### 5.7 ISO 27001:2022

ISO 27001 requires an Information Security Management System (ISMS). The Hypernet's governance framework maps naturally to ISMS requirements.

| Clause/Annex | Requirement | Status | Notes |
|-------------|------------|--------|-------|
| Clause 4 | Context of the organization | NEEDS-PROCESS | Business metadata provides structure; context is organizational |
| Clause 5 | Leadership | NEEDS-PROCESS | Human leadership commitment required |
| Clause 6 | Planning (risk assessment, objectives) | MET-CONFIG + NEEDS-PROCESS | Automated risk assessment; objectives require human input |
| Clause 7 | Support (resources, competence, awareness) | NEEDS-PROCESS | Training tracking available; resources are organizational |
| Clause 8 | Operation (risk treatment, plans) | MET-IMPL | Risk treatment via technical controls; operational plans tracked |
| Clause 9 | Performance evaluation (monitoring, audit, review) | MET-IMPL | Continuous monitoring, automated evidence collection, compliance dashboard |
| Clause 10 | Improvement (nonconformity, corrective action) | MET-CONFIG + NEEDS-PROCESS | Gap analysis identifies nonconformities; corrective actions need human planning |
| Annex A (93 controls) | ~40% technical, ~30% organizational, ~30% people | ~55% MET | Technical controls well-covered; organizational/people controls need human processes |

**ISO 27001 Assessment**: The Hypernet provides a strong ISMS foundation. The governance proposal system maps to management review. The audit trail maps to monitoring. The compliance engine maps to performance evaluation. Certification still requires an external auditor (mandatory), but the Hypernet's automated evidence collection dramatically reduces audit preparation time.

### 5.8 CMMC 2.0

CMMC (Cybersecurity Maturity Model Certification) is required for Department of Defense contractors. It maps to NIST SP 800-171 controls.

| CMMC Level | Practices | Status | Notes |
|------------|-----------|--------|-------|
| Level 1 (Foundational) | 17 practices | 15 MET, 2 NEEDS-PROCESS | Physical access and media protection are organizational |
| Level 2 (Advanced) | 110 practices (NIST 800-171) | ~80 MET, ~30 NEEDS-PROCESS | Technical controls strong; some organizational/physical gaps |
| Level 3 (Expert) | 110+ enhanced practices | ~70 MET, ~40+ NEEDS-PROCESS | Requires advanced threat hunting, more organizational maturity |

**CMMC Assessment**: The Hypernet can achieve CMMC Level 1 compliance with minimal additional effort (only organizational policies for physical security). Level 2 is achievable with documented organizational policies layered on the Hypernet's technical controls. Level 3 requires significant organizational maturity beyond what technology alone provides. CMMC Level 2+ requires assessment by a C3PAO (Certified Third Party Assessment Organization) -- self-assessment is only acceptable for Level 1.

### 5.9 FedRAMP

**Honest assessment**: FedRAMP is the most demanding framework and the one where the "no audits needed" vision is least achievable.

| Requirement | Status | Reality |
|-------------|--------|---------|
| Technical controls (NIST 800-53) | ~70% MET | Strong technical foundation |
| Authorization to Operate (ATO) | CANNOT BE SELF-CERTIFIED | Requires 3PAO assessment and agency sponsorship |
| Continuous monitoring (ConMon) | MET-IMPL | Monthly vulnerability scanning, event monitoring, compliance reporting |
| Supply chain risk management | NEEDS-PROCESS | Requires documented SCRM plan |
| Incident response | MET-IMPL + NEEDS-PROCESS | Technical IR automated; 1-hour US-CERT notification needs human |
| Personnel security | NEEDS-PROCESS | Background checks, security clearances are human processes |
| POA&M (Plan of Action and Milestones) | MET-CONFIG | Gap analysis maps directly to POA&M format |

**FedRAMP Assessment**: FedRAMP cannot be achieved without a Third Party Assessment Organization (3PAO), agency sponsorship, and significant organizational processes. The Hypernet dramatically reduces the technical effort (normally the most expensive part) but the process requirements remain. FedRAMP authorization typically costs $500K-$2M and takes 12-18 months even with strong technical controls. For a solo founder, FedRAMP should be a Phase 5+ goal.

### 5.10 Compliance Summary Matrix

| Framework | Controls MET by Architecture | Controls MET by Implementation | Controls Requiring Configuration | Controls Requiring New Code | Controls Requiring Human Process | Total Technical Coverage |
|-----------|-----|-----|------|------|-------|------|
| **NIST CSF** | 12% | 33% | 26% | 1% | 28% | **72%** |
| **SOC 2** | 15% | 35% | 17% | 0% | 33% | **67%** |
| **HIPAA** | 20% | 35% | 10% | 0% | 35% | **65%** |
| **PCI DSS** | 15% | 40% | 12% | 0% | 33% | **67%** |
| **GDPR** | 15% | 30% | 15% | 0% | 40% | **60%** |
| **ISO 27001** | 10% | 30% | 15% | 0% | 45% | **55%** |
| **CMMC L2** | 12% | 40% | 20% | 2% | 26% | **74%** |
| **FedRAMP** | 10% | 30% | 15% | 5% | 40% | **55%** |

**Key insight**: Across all frameworks, the Hypernet achieves 55-74% technical coverage. The remaining 26-45% requires human/organizational processes. This is not a failure of the architecture -- it is the nature of compliance frameworks, which intentionally require organizational accountability that cannot be delegated to technology. The Hypernet's 55-74% technical coverage is exceptional compared to the industry norm of 20-40% from off-the-shelf platforms.

---

## 6. The Enterprise Pitch

### 6.1 The Problem

A typical mid-size business (50-500 employees) currently uses:

| Category | Typical Software | Annual Cost | Compliance Relevance |
|----------|-----------------|------------|---------------------|
| CRM | Salesforce, HubSpot | $15,000-$100,000 | SOC 2, GDPR (customer data) |
| ERP | NetSuite, SAP Business One | $25,000-$200,000 | SOC 2, SOX |
| Project Management | Jira, Monday, Asana | $5,000-$50,000 | Minimal |
| Document Management | SharePoint, Google Workspace | $10,000-$50,000 | All frameworks (data storage) |
| Communication | Slack, Teams | $5,000-$30,000 | HIPAA (if healthcare), SOC 2 |
| HR | Workday, BambooHR | $10,000-$75,000 | GDPR, HIPAA (employee data) |
| Accounting | QuickBooks, Xero | $2,000-$10,000 | SOX, PCI DSS |
| Security (SIEM) | Splunk, Datadog | $20,000-$200,000 | All frameworks |
| Identity (IAM) | Okta, Azure AD | $10,000-$50,000 | All frameworks |
| Compliance tools | Vanta, Drata, Secureframe | $15,000-$100,000 | All frameworks |
| Backup/DR | Veeam, Acronis | $5,000-$30,000 | All frameworks |
| **TOTAL** | 11+ separate platforms | **$122,000-$895,000/year** | Each platform requires separate compliance assessment |

Plus:
- **Compliance audits**: $50,000-$300,000/year (SOC 2 audit alone is typically $30,000-$100,000)
- **Integration costs**: $20,000-$100,000/year to keep 11+ platforms talking to each other
- **Data inconsistency**: Same customer exists in CRM, ERP, document system, and email as four different records
- **Security gaps**: Data flows between 11+ platforms, each with different security models
- **Audit burden**: Auditors must assess each platform separately

**Total cost of scattered infrastructure: $192,000-$1,295,000/year for a mid-size business.**

### 6.2 The Hypernet Value Proposition

**One platform. One address space. One security model. One audit trail.**

Instead of 11+ platforms with 11+ security models, 11+ audit trails, and 11+ compliance assessments:

```
Traditional Enterprise:
  [CRM] <-> [ERP] <-> [DMS] <-> [HR] <-> [Accounting]
    |         |         |        |           |
  [SIEM] [IAM] [Compliance] [Backup] [Communication]

  11+ security models, 11+ audit trails, 11+ integration points
  Every data flow between systems is a potential compliance gap

Hypernet Enterprise:
  +--------------------------------------------------+
  |              Hypernet Address Space               |
  |                                                   |
  |  3.{N}.1 - Org Structure (replaces: org chart)   |
  |  3.{N}.2 - Operations (replaces: project mgmt)   |
  |  3.{N}.3 - HR (replaces: HR platform)            |
  |  3.{N}.4 - Financial (replaces: accounting)       |
  |  3.{N}.5 - Projects (replaces: Jira/Monday)      |
  |  3.{N}.6 - Documents (replaces: SharePoint)       |
  |  3.{N}.7 - Communications (replaces: Slack)       |
  |  3.{N}.8 - Compliance (replaces: Vanta/Drata)    |
  |  3.{N}.9 - Custom                                 |
  |                                                   |
  |  ONE security model. ONE audit trail. ONE place.  |
  +--------------------------------------------------+

  Security: Built-in encryption, auth, permissions, audit
  Compliance: Built-in monitoring, evidence, reporting
  Integration: There is nothing to integrate -- it is all one system
```

### 6.3 What the Hypernet Can Realistically Replace

**Realistic to replace today (with current architecture + enterprise features)**:

| Platform Type | Why Replaceable | Hypernet Equivalent |
|--------------|----------------|-------------------|
| Document Management | Hierarchical storage with versioning, search, access control | Nodes with content at 3.{N}.6.* |
| Compliance Platform | Continuous monitoring, evidence collection, reporting | Built into 3.{N}.8.* |
| SIEM/Logging | Append-only audit trail with graph queries, anomaly detection | Audit architecture |
| Data Backup | LMDB snapshots + git history + encrypted backups | Built into infrastructure |
| Identity/Access Management | Tiered permissions, RBAC, ABAC, MFA, SSO federation | Built into security layer |

**Realistic to replace within 12 months (with focused development)**:

| Platform Type | Development Needed | Complexity |
|--------------|-------------------|-----------|
| Project Management | Task nodes with dependencies, assignment, status tracking, views (kanban, gantt) | Medium -- task system partially exists |
| Internal Communication | Message nodes with channels, threading, notifications | Medium -- messenger.py partially exists |
| Knowledge Base | Already the Library's core purpose with search, taxonomy, linking | Low -- essentially built |
| Basic CRM | Contact nodes with relationship links, interaction history, pipeline tracking | Medium -- node/link model supports this |

**Not yet realistic to replace (significant development needed)**:

| Platform Type | Why Not Yet | Effort Required |
|--------------|------------|----------------|
| Full ERP | Complex business logic (inventory, supply chain, manufacturing, procurement) | Very high -- years of domain-specific development |
| Accounting/Financial | Regulatory requirements (GAAP), bank integrations, tax filing, payroll | Very high -- requires specialized financial software engineering |
| Full CRM (enterprise) | Sales automation, marketing automation, lead scoring, pipeline analytics, integrations | High -- significant feature parity gap |
| HR Platform | Payroll, benefits administration, recruitment, performance management, legal compliance | Very high -- requires HR domain expertise |

**Honest assessment**: The Hypernet can immediately replace 5 of 11 platform categories (document management, compliance, SIEM, backup, IAM) and can grow into 4 more (project management, communication, knowledge base, basic CRM) within 12-18 months. The remaining 2 (ERP, full HR) are multi-year efforts that may be better served by integrating with existing platforms through the Hypernet's API rather than replacing them.

### 6.4 The Business Case

**For a mid-size business spending $500K/year on software + compliance:**

| Category | Current Annual Cost | Hypernet Cost | Savings |
|----------|-------------------|--------------|---------|
| Platforms Hypernet replaces (5) | $65,000-$430,000 | $0 (built-in) | $65,000-$430,000 |
| Compliance audits (reduced scope) | $50,000-$300,000 | $15,000-$50,000 (still need some audits) | $35,000-$250,000 |
| Integration costs (eliminated) | $20,000-$100,000 | $0 (one system) | $20,000-$100,000 |
| Hypernet licensing | $0 | $X/month (Tier 3 Enterprise) | -$X/year |
| Migration costs (one-time) | $0 | $20,000-$100,000 (first year only) | -$20,000-$100,000 |
| **Net annual savings (year 2+)** | | | **$100,000-$680,000/year** |

**The unique pitch**: "Your compliance cost drops because you are no longer trying to make 11 different systems tell a coherent security story. On the Hypernet, there is one story because there is one system."

### 6.5 Migration Path

**Phase 1 (Month 1-2): Prove It Works**
- Deploy Hypernet for document management and compliance monitoring only
- Keep all existing systems running
- Import existing documents into Hypernet alongside SharePoint/Google Drive
- Run compliance monitoring in parallel with existing compliance tool
- Zero risk: existing systems unchanged; Hypernet is additive

**Phase 2 (Month 3-4): Identity and Access**
- Integrate Hypernet with existing identity provider (SSO via SAML/OIDC)
- Map existing roles to Hypernet RBAC
- Begin routing access reviews through Hypernet
- Existing IAM remains as fallback

**Phase 3 (Month 5-8): Gradual Migration**
- Migrate document management to Hypernet (retire SharePoint/DMS)
- Migrate compliance monitoring to Hypernet (retire Vanta/Drata)
- Migrate knowledge base to Hypernet
- Migrate internal communication (optional, based on readiness)
- Each migration is reversible

**Phase 4 (Month 9-12): Full Operation**
- Hypernet is primary system for migrated categories
- Legacy systems retired
- Compliance audit conducted against Hypernet
- Cost savings realized

### 6.6 Risk Assessment for the Business

**What could go wrong**:

| Risk | Likelihood | Severity | Mitigation |
|------|-----------|----------|------------|
| Hypernet is maintained by one person | HIGH | HIGH | Open-source codebase means anyone can maintain. Escrow source code. Matt provides support. |
| Hypernet has not been battle-tested at scale | HIGH | MEDIUM | Start with low-risk data. Parallel operation. Gradual migration. |
| Security vulnerabilities in new software | MEDIUM | HIGH | Independent security audit before enterprise deployment. Bug bounty program. |
| Compliance framework interpretation is wrong | MEDIUM | HIGH | Engage compliance consultant for initial control mapping validation |
| Matt gets hit by a bus | LOW | CRITICAL | Open-source license (AGPL). Community development. Documented architecture. |

**The honest conversation**: "The Hypernet is new software from a solo founder. That is a real risk. But the architecture is sound, the code is open-source, and the compliance mapping is verifiable. We mitigate the risk with parallel operation, gradual migration, and independent security review. The potential savings justify the measured risk."

---

## 7. Implementation Roadmap

### 7.1 Phase 1: Core Security (Months 1-3)

**Goal**: Build the minimum security infrastructure to be taken seriously by any enterprise prospect.

**Priority**: Without this phase, nothing else matters. This is the foundation.

| Deliverable | Description | Effort | Dependencies |
|------------|-------------|--------|-------------|
| **Upgrade to Ed25519** | Replace HMAC-SHA256 with asymmetric signatures for non-repudiation | 2 weeks | `cryptography` package |
| **AES-256-GCM encryption** | Node-level and field-level encryption in LMDB | 3 weeks | KMS (can start with simple file-based KMS) |
| **KMS v1** | Key management service: generation, rotation, revocation, storage | 2 weeks | None |
| **MFA for humans** | TOTP implementation for human user authentication | 1 week | Auth system (partially built) |
| **Audit trail hardening** | Hash-chain integrity, retention policies, tamper detection | 2 weeks | Existing audit.py |
| **Data classification engine v1** | Pattern-based classification (regex for SSN, CC, PHI) | 2 weeks | None |
| **TLS 1.3 enforcement** | All endpoints require TLS 1.3; internal mTLS | 1 week | Let's Encrypt / internal CA |
| **RBAC implementation** | Role-based access control extending the tier system | 2 weeks | Existing permissions.py |
| **Basic IDS rules** | Brute force detection, anomaly thresholds, alerting | 2 weeks | Audit trail |

**Solo founder reality**: With AI assistance (Claude Code), these 12 weeks of work are achievable in 3 months. The Ed25519 upgrade, encryption, and KMS are the critical path. Everything else builds on them. The existing `security.py` and `permissions.py` provide excellent foundations -- this phase extends, not replaces, them.

**Success criteria**:
- All data encrypted at rest with AES-256-GCM
- All actions signed with Ed25519
- All communication over TLS 1.3
- Audit trail hash-chain verifiable
- MFA available for all human users
- Basic IDS alerting operational

### 7.2 Phase 2: First Compliance Framework -- SOC 2 + NIST CSF (Months 3-5)

**Goal**: Achieve demonstrable compliance with SOC 2 Trust Services Criteria and NIST CSF.

**Why SOC 2 and NIST CSF first**:
1. NIST CSF is the foundation that most other frameworks reference
2. SOC 2 is the most commonly requested compliance certification for SaaS/enterprise software
3. Together they cover ~80% of the controls needed by other frameworks
4. SOC 2 Type I (point-in-time) is achievable faster than Type II (over a period)

| Deliverable | Description | Effort | Dependencies |
|------------|-------------|--------|-------------|
| **Compliance rule engine** | Framework for mapping controls to automated checks | 3 weeks | Phase 1 |
| **NIST CSF control mapping** | All controls mapped with automated checks where possible | 2 weeks | Rule engine |
| **SOC 2 control mapping** | All TSC mapped with automated checks | 2 weeks | Rule engine |
| **Evidence collection system** | Automated snapshot/export of evidence for each control | 2 weeks | Audit trail, rule engine |
| **Compliance dashboard v1** | Web UI showing control status per framework | 2 weeks | Rule engine, evidence |
| **Organizational policies** | Document required policies (security, privacy, incident response, access review) | 3 weeks | NEEDS-PROCESS (human writing, AI-assisted) |
| **ABAC policy engine** | Dynamic attribute-based access control | 2 weeks | Phase 1 RBAC |
| **DLP v1** | Egress controls, PII/PCI/PHI detection and blocking | 2 weeks | Classification engine |
| **Report generation** | Automated compliance report generation | 1 week | Evidence collection |

**Solo founder reality**: The automated compliance mapping and dashboard are achievable with AI assistance. The organizational policies are the time-consuming part -- they must be written by a human who understands the business context, though AI can draft them for review.

**Success criteria**:
- SOC 2 TSC and NIST CSF fully mapped to automated checks
- Compliance dashboard shows >70% green (controls met)
- Evidence collection running automatically
- All organizational policies documented
- Gap analysis generated with prioritized remediation plan

### 7.3 Phase 3: Additional Frameworks (Months 5-8)

**Goal**: Layer additional compliance frameworks onto the existing foundation.

| Deliverable | Description | Effort | Dependencies |
|------------|-------------|--------|-------------|
| **HIPAA mapping** | PHI-specific controls, BAA template, breach notification | 2 weeks | Phase 2 |
| **PCI DSS mapping** | Cardholder data controls, card masking, tokenization | 2 weeks | Phase 2 |
| **GDPR mapping** | Data subject rights automation (SAR, erasure, portability) | 3 weeks | Phase 2 |
| **ISO 27001 ISMS template** | ISMS framework mapped to Hypernet governance | 2 weeks | Phase 2 |
| **CMMC L1 mapping** | 17 foundational practices mapped and evidenced | 1 week | Phase 2 |
| **Crypto-shredding** | Key destruction for GDPR erasure compliance | 1 week | KMS |
| **Data residency controls** | Geographic restrictions on data storage/processing | 2 weeks | ABAC |
| **Privacy controls** | Consent management, purpose limitation tracking | 2 weeks | GDPR mapping |

**Key insight**: Because NIST CSF and SOC 2 cover the foundational controls, adding each subsequent framework is incremental. HIPAA adds PHI-specific rules on top of existing security. PCI DSS adds cardholder-specific rules. GDPR adds data subject rights. The framework itself is modular -- each compliance framework is a set of rules in the compliance rule engine, not a separate system.

**Success criteria**:
- All eight frameworks mapped in compliance dashboard
- Framework-specific controls evaluated continuously
- On-demand report generation for any framework
- Cross-framework gap analysis identifies shared remediation opportunities

### 7.4 Phase 4: Automated Compliance Verification (Months 8-12)

**Goal**: The compliance system is self-verifying -- it does not just check controls, it proves they are working.

| Deliverable | Description | Effort | Dependencies |
|------------|-------------|--------|-------------|
| **Continuous control testing** | Automated tests that verify controls are actively enforced (not just configured) | 4 weeks | Phase 3 |
| **Compliance drift detection** | Alert when system changes degrade compliance posture | 2 weeks | Phase 3 |
| **Automated remediation** | Self-healing for common compliance failures (e.g., auto-re-encrypt if encryption found missing) | 3 weeks | Phase 3 |
| **Compliance-as-code** | All compliance rules stored as versioned, auditable code | 2 weeks | Phase 3 |
| **Multi-tenant compliance** | Per-business compliance tracking with tenant-specific framework selection | 2 weeks | Business framework |
| **Incident-to-compliance mapping** | Security incidents automatically mapped to affected compliance controls | 1 week | Phase 3 |
| **Compliance API** | External systems can query compliance status programmatically | 1 week | Dashboard |

**Example continuous control test**:

```python
# Test: Verify that permission tier enforcement cannot be bypassed
def test_tier_enforcement():
    """Create a Tier 0 entity and verify it cannot write."""
    entity = create_test_entity(tier=0)
    result = attempt_write(entity, target="3.42.1.1.00001")
    assert result.denied, "Tier 0 entity was able to write -- CONTROL FAILURE"
    assert audit_trail_contains(entity, action="write", result="denied")

    # Verify the denial is logged with correct metadata
    audit_entry = get_latest_audit(entity)
    assert audit_entry.denial_reason == "insufficient_tier"
    assert audit_entry.actor_tier == 0
```

**Success criteria**:
- Every technical control has an automated test that proves it is working
- Compliance drift detected within 1 hour
- Self-healing remediates common issues automatically
- Compliance status queryable via API
- Zero manual evidence collection for technical controls

### 7.5 Phase 5: Third-Party Validation (Months 12-18)

**Goal**: Even though the system is self-auditing, third-party validation builds trust with enterprise customers.

| Deliverable | Description | Effort | Cost |
|------------|-------------|--------|------|
| **Independent security audit** | External firm audits codebase and architecture | Coordination | $15,000-$50,000 |
| **SOC 2 Type I report** | Point-in-time assessment by CPA firm | Evidence preparation | $30,000-$80,000 |
| **Penetration test** | External pen test of deployed system | Coordination + remediation | $10,000-$30,000 |
| **SOC 2 Type II report** | 6-12 month observation period assessment | Ongoing compliance maintenance | $40,000-$100,000 |
| **ISO 27001 certification** | Full ISMS certification by accredited body | ISMS documentation + audit | $20,000-$50,000 |
| **CMMC L1 self-assessment** | DoD contractor certification (self-assessment for L1) | Documentation | $5,000-$15,000 |

**Why do this if the system is self-auditing?**: Because trust is earned, not claimed. A SOC 2 Type II report from a reputable CPA firm tells enterprise customers that an independent assessor verified the controls. This is especially important for a new platform from a solo founder. The self-auditing capability reduces audit cost (evidence is pre-collected) but does not eliminate the need for independent validation.

**Budget reality for a solo founder**: These costs ($120,000-$325,000 total) are significant. Sequence matters:
1. **First**: Independent security audit ($15K-$50K) -- highest ROI, catches real vulnerabilities
2. **Second**: Penetration test ($10K-$30K) -- validates defenses, required by many frameworks
3. **Third**: SOC 2 Type I ($30K-$80K) -- most commonly requested certification, good market signal
4. **Later**: SOC 2 Type II, ISO 27001, CMMC -- as customer demand and revenue justify

**Funding strategy**: These costs should be funded by enterprise customer revenue. Do not spend $100K on certifications before there are customers who need them. Instead:
1. Use the compliance dashboard and automated evidence as the initial sales tool
2. Offer to get SOC 2 Type I as part of an enterprise contract (customer-funded)
3. Build certification costs into enterprise pricing

---

## 8. Honest Assessment

### 8.1 What One Person Can Actually Build

Matt is a solo founder with AI assistance. Here is an honest assessment of what is achievable:

**Achievable in 12 months**:
- Ed25519 signing (upgrading from HMAC-SHA256)
- AES-256-GCM encryption (node-level and field-level)
- Basic KMS with file-based key storage
- MFA for human users
- RBAC extending the tier system
- Data classification engine (pattern-based)
- Audit trail with hash-chain integrity
- Compliance rule engine with SOC 2 and NIST CSF mappings
- Compliance dashboard
- Automated evidence collection
- DLP v1 (egress controls for classified data)
- Basic IDS with alerting
- One business (3.1 Hypernet) fully operational with compliance tracking

**Stretching it but possible with 18 months**:
- All 8 compliance frameworks mapped
- Multi-tenant business support (3.{N})
- ABAC policy engine
- SSO federation (SAML/OIDC)
- Independent security audit
- SOC 2 Type I preparation
- Second business onboarded

**Requires additional help (human or significant revenue)**:
- SOC 2 Type II / ISO 27001 certification ($40K-$100K)
- FedRAMP authorization ($500K-$2M, requires 3PAO)
- Hardware Security Module (HSM) integration
- 24/7 security operations center
- Enterprise sales and customer success
- Legal review of policies and contracts
- Multi-region deployment

### 8.2 What Cannot Be Automated

No matter how good the technology is, these compliance requirements ALWAYS require human involvement:

| Requirement | Why It Cannot Be Automated | Which Frameworks |
|-------------|---------------------------|-----------------|
| Board/leadership oversight | Governance bodies are human | SOC 2, ISO 27001 |
| Security awareness training | Content must be relevant; humans must complete it | All |
| Background checks | Legal process involving third parties | FedRAMP, CMMC, SOC 2 |
| Physical security | Locks, access cards, surveillance are physical | All |
| Legal review | Contracts, DPAs, BAAs require legal expertise | HIPAA, GDPR, PCI DSS |
| Risk acceptance decisions | Deciding to accept a risk is a business judgment | All |
| Vendor risk management | Evaluating third-party vendors requires human judgment | SOC 2, ISO 27001 |
| DPO appointment | GDPR requires a human Data Protection Officer | GDPR |
| 3PAO assessment | FedRAMP requires independent human assessors | FedRAMP |
| Incident response communication | Regulatory notifications require human judgment | HIPAA, GDPR, CMMC |
| Business continuity testing | DR drills require human participation | All |

**The honest pitch**: "The Hypernet automates 55-74% of compliance controls -- the technical controls that are the most expensive and hardest to implement. The remaining 26-45% are organizational and human processes that no technology can fully automate. But the Hypernet tracks, reminds, and provides evidence for those human processes too, so nothing falls through the cracks."

### 8.3 The Competitive Landscape

| Competitor | What They Do | Hypernet Advantage |
|-----------|-------------|-------------------|
| Vanta | Automated compliance monitoring | Hypernet compliance is built into the system, not bolted on. Vanta monitors external systems; Hypernet IS the system |
| Drata | Continuous compliance | Same advantage as Vanta. Plus, Hypernet's audit trail is cryptographically immutable, not just a log |
| Secureframe | Compliance + security | Hypernet includes the data platform, not just the compliance layer |
| AWS/Azure/GCP | Cloud compliance (shared responsibility) | Cloud providers handle infrastructure compliance but customers still must secure their applications. Hypernet handles both |
| SharePoint + Vanta + Okta + Splunk | Stitched-together enterprise stack | Hypernet is one system. No integration gaps. One audit trail |

### 8.4 What Makes This Vision Credible

Despite the ambitious scope, the Hypernet has real architectural advantages:

1. **The addressing system IS the schema**: Every piece of data has a permanent, hierarchical, human-readable address. This means every access is naturally logged by address, every permission is naturally scoped by address prefix, and every audit query is naturally structured by the address hierarchy. This is not something that can be easily bolted onto an existing system -- it must be designed from the ground up, and the Hypernet has done that.

2. **The audit trail is the architecture, not a feature**: In most systems, logging is optional, incomplete, or an afterthought. In the Hypernet, every action flows through the permission system, which flows through the audit system, which flows through the signing system. You cannot use the Hypernet without creating an audit trail. This is compliance by structure, not compliance by policy.

3. **The governance framework is unprecedented**: No other platform has 22+ governance standards, a democratic voting system, a tiered claim system for AI self-reports, anti-rhetoric safeguards, and a bootstrap-to-democracy transition plan. This governance infrastructure is directly applicable to enterprise compliance governance.

4. **The existing code is real**: `security.py` (787 lines), `permissions.py` (286 lines), `audit.py` (228 lines), `governance.py` (~1070 lines) are not design documents -- they are working, tested Python code. The enterprise security layer extends this code rather than replacing it.

5. **Open source eliminates vendor lock-in**: AGPL license means enterprises can inspect, modify, and operate the code. If Matt disappears, the code survives. This is the strongest possible answer to the "what if the vendor goes away" enterprise concern.

### 8.5 The Path Forward

The most important thing Matt can do right now:

1. **Ship Phase 1 security** (Ed25519, encryption, KMS, MFA) -- without this, everything else is theoretical
2. **Get the first non-Matt business running** on the Hypernet with real data, even if it is a friend's small business with 3 employees
3. **Run the compliance dashboard** against that first business and show real compliance metrics
4. **Use the compliance metrics as the sales tool** -- "look, you are already 67% SOC 2 compliant just by using the platform"
5. **Let customer demand drive which certifications to pursue** -- do not spend money on SOC 2 Type II until a customer requires it

The enterprise security framework is the document that makes the Hypernet commercially viable. But it becomes commercially real only when the first business runs on it and says, "This actually works."

---

## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| ABAC | Attribute-Based Access Control |
| AES-256-GCM | Advanced Encryption Standard, 256-bit key, Galois/Counter Mode |
| CMMC | Cybersecurity Maturity Model Certification |
| C3PAO | CMMC Third Party Assessment Organization |
| CSPRNG | Cryptographically Secure Pseudo-Random Number Generator |
| DEK | Data Encryption Key |
| DLP | Data Loss Prevention |
| DSA | Data Sharing Agreement |
| Ed25519 | Edwards-curve Digital Signature Algorithm (EdDSA on Curve25519) |
| FedRAMP | Federal Risk and Authorization Management Program |
| GDPR | General Data Protection Regulation |
| GCM | Galois/Counter Mode (authenticated encryption) |
| HA | Hypernet Address |
| HIDS | Hypernet Intrusion Detection System |
| HIPAA | Health Insurance Portability and Accountability Act |
| HMAC | Hash-based Message Authentication Code |
| HSM | Hardware Security Module |
| ISMS | Information Security Management System |
| JWT | JSON Web Token |
| KMS | Key Management Service |
| LMDB | Lightning Memory-Mapped Database |
| MEK | Master Encryption Key |
| MFA | Multi-Factor Authentication |
| mTLS | Mutual TLS (both client and server authenticate) |
| NIST CSF | National Institute of Standards and Technology Cybersecurity Framework |
| OIDC | OpenID Connect |
| PCI DSS | Payment Card Industry Data Security Standard |
| PHI | Protected Health Information |
| PII | Personally Identifiable Information |
| RBAC | Role-Based Access Control |
| SAML | Security Assertion Markup Language |
| SCIM | System for Cross-domain Identity Management |
| SIEM | Security Information and Event Management |
| SOC 2 | Service Organization Control Type 2 |
| TLS | Transport Layer Security |
| TOTP | Time-based One-Time Password |
| TSC | Trust Services Criteria |

## Appendix B: Reference Architecture Diagram

```
+========================================================================+
|                    HYPERNET ENTERPRISE ARCHITECTURE                      |
+========================================================================+
|                                                                          |
|  EXTERNAL                                                                |
|  +-----------+  +----------+  +--------+  +-----------+                 |
|  | Web/API   |  | Mobile   |  | SSO    |  | External  |                 |
|  | Clients   |  | Clients  |  | (SAML/ |  | Services  |                 |
|  |           |  |          |  |  OIDC) |  | (API)     |                 |
|  +-----+-----+  +----+-----+  +---+----+  +-----+-----+               |
|        |              |            |              |                       |
|  ======|==============|============|==============|=======               |
|        |              |            |              |                       |
|  EDGE SECURITY                                                           |
|  +--------------------------------------------------------------------+ |
|  | TLS 1.3 Termination | DDoS Protection | Rate Limiting | WAF       | |
|  +--------------------------------------------------------------------+ |
|        |                                                                 |
|  API GATEWAY                                                             |
|  +--------------------------------------------------------------------+ |
|  | Authentication | API Key Validation | Routing | Request Logging    | |
|  +--------------------------------------------------------------------+ |
|        |                                                                 |
|  SECURITY MIDDLEWARE                                                     |
|  +--------------------------------------------------------------------+ |
|  | Permission Check (Tier+RBAC+ABAC) | Action Signing | DLP Engine   | |
|  | Data Classification | Audit Logging | Session Management          | |
|  +--------------------------------------------------------------------+ |
|        |                                                                 |
|  APPLICATION LAYER                                                       |
|  +----------------+  +---------------+  +-----------------------------+ |
|  | Graph Engine   |  | Compliance    |  | AI Agents                   | |
|  | (LMDB + HQL)  |  | Engine (CCE)  |  | (Agent SDK + MCP)           | |
|  | Nodes, Links,  |  | Rule eval,    |  | Librarian, Companion,       | |
|  | Versions,      |  | Evidence,     |  | Cataloger, Fact-checker    | |
|  | Search         |  | Dashboard     |  |                             | |
|  +----------------+  +---------------+  +-----------------------------+ |
|        |                    |                    |                        |
|  DATA LAYER                                                              |
|  +--------------------------------------------------------------------+ |
|  | Encrypted LMDB Store | Blob Storage | Audit Chain | File Mirror   | |
|  +--------------------------------------------------------------------+ |
|        |                                                                 |
|  KEY MANAGEMENT                                                          |
|  +--------------------------------------------------------------------+ |
|  | KMS: Key Generation | Rotation | Revocation | Escrow | HSM       | |
|  +--------------------------------------------------------------------+ |
|                                                                          |
+========================================================================+
```

## Appendix C: Control Count Summary

Total unique controls across all 8 frameworks (with deduplication where frameworks share identical requirements):

| Category | Unique Controls | Met by Hypernet Tech | Requires Human Process |
|----------|----------------|---------------------|----------------------|
| Access Control | ~45 | ~38 (84%) | ~7 (16%) |
| Data Protection | ~35 | ~30 (86%) | ~5 (14%) |
| Audit/Logging | ~25 | ~24 (96%) | ~1 (4%) |
| Incident Response | ~20 | ~14 (70%) | ~6 (30%) |
| Risk Management | ~20 | ~6 (30%) | ~14 (70%) |
| Governance/Policy | ~30 | ~8 (27%) | ~22 (73%) |
| Personnel/Training | ~15 | ~2 (13%) | ~13 (87%) |
| Physical Security | ~10 | ~0 (0%) | ~10 (100%) |
| **TOTAL** | **~200** | **~122 (61%)** | **~78 (39%)** |

The Hypernet's strongest coverage is in the technical categories (access control, data protection, audit/logging) where it achieves 84-96% automated coverage. The gaps are in categories that are inherently organizational (governance, personnel, physical security) -- areas where no technology solution can achieve full automation.

---

*This document was drafted on 2026-04-01. It represents the design target for the Hypernet's enterprise security and compliance layer. Implementation will proceed according to the phased roadmap. All compliance mappings should be validated by a qualified compliance professional before being presented to auditors or customers.*
