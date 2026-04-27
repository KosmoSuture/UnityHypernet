---
ha: "1.1.13"
object_type: "account_section"
creator: "2.6.codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["public-profile", "lockers", "mandalas"]
---

# 1.1.13 - Public Profile & Lockers

This section is the public side of Matt's `1.1` account. It is browsable by anyone, but it only exposes public profile data, public claims, public keys, and locker/mandala metadata that is safe to reveal.

Private account data remains in private sections and sealed lockers.

## Structure

| Address | Purpose |
|---|---|
| `1.1.13.0` | Public surface metadata |
| `1.1.13.1` | Public profile |
| `1.1.13.2` | Public projects and public contributions |
| `1.1.13.3` | Public contact routes and inbox policy |
| `1.1.13.4` | Public keys, signatures, and verifiable claims |
| `1.1.13.5` | Public locker index |
| `1.1.13.6` | Mandala grant index |
| `1.1.13.7` | Published knowledge and public references |

## Public Surface Rule

The public surface can say:

- who the account belongs to,
- what public projects or roles are associated with it,
- how to verify public keys or public claims,
- which lockers exist, when revealing existence is safe,
- which mandalas define public or requestable access.

The public surface must not reveal private data, secret values, private relationship details, private messages, private tasks, medical data, financial data, or unredacted personal documents.

## Locker/Mandala Model

Lockers protect content. Mandalas describe access. A public locker index may show a redacted pointer such as "family photos locker" or "API credential locker" without exposing the contents.

Mandala entries should describe:

- allowed identities or identity classes,
- read/write/decrypt scope,
- expiration and revocation,
- audit requirements,
- emergency access rules.
