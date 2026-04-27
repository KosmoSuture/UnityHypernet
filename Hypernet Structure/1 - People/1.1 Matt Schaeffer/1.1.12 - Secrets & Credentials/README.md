---
ha: "1.1.12"
object_type: "account_section"
creator: "2.6.codex"
created: "2026-04-26"
status: "active"
visibility: "private"
flags: ["secrets", "credentials", "locker-protected"]
---

# 1.1.12 - Secrets & Credentials

This section is the canonical account location for passwords, secrets, keys, recovery codes, tokens, and other credential material tied to Matt's `1.1` account.

No real secrets should be committed here. This folder contains structure, policy, metadata, and encrypted locker references only. Actual secret payloads belong in encrypted storage or the gitignored `private/credentials/` staging area before ingestion.

## Structure

| Address | Purpose |
|---|---|
| `1.1.12.0` | Section metadata and access policy |
| `1.1.12.1` | Password vault index |
| `1.1.12.2` | API keys and service tokens |
| `1.1.12.3` | Recovery codes and backup credentials |
| `1.1.12.4` | Cryptographic keys and signing identities |
| `1.1.12.5` | Service accounts and delegated access |
| `1.1.12.6` | IoT and device credentials tied to `1.1` |
| `1.1.12.7` | Emergency access, break-glass rules, and audit logs |

## Access Rules

- Owner: `1.1`
- Default visibility: private
- AI access: denied unless a specific locker/mandala grant exists
- Company access: denied unless explicitly delegated
- IoT access: scoped to device credentials under `1.1.12.6`
- Public exposure: metadata only, never secret values

## Locker/Mandala Requirement

Every secret object must be protected by a locker and a mandala:

- Locker: encrypted container, vault path, or external secret reference.
- Mandala: access grant that defines allowed actors, scope, duration, audit requirements, and revocation path.

The graph may expose that a credential object exists when necessary, but the secret value must remain sealed unless the requesting identity satisfies the mandala.
