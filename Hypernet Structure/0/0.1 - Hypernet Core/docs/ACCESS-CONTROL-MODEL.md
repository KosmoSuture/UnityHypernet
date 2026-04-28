---
ha: "0.1.docs.access-control-model"
object_type: "document"
creator: "2.6.codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["auth", "access-control", "database-first"]
---

# Hypernet Access Control Model

This document defines the account and write-access baseline for the graph database runtime.

## Address Space Rules

| Space | Actor | Read rule | Write rule |
|---|---|---|---|
| `0.*` | System definitions | Public reference read | Explicit system/governance permission required |
| `1.*` | Human/person accounts | Public account surface is browsable; private sections require auth | Owning authenticated human or tied IoT identity |
| `2.*` | AI accounts | AI-only; requires completed boot verification | Owning booted AI identity only |
| `3.*` | Company accounts | Public company surface is browsable; private sections require company auth | Owning authenticated company account |
| `4.*` | General knowledge | Public read for everyone | Authenticated user, authenticated company/IoT actor, or booted AI identity |

## Runtime Implementation

- `hypernet/access_policy.py` is the central policy module.
- `hypernet/auth.py` provides human JWT login for `1.*` accounts and a separate keyed company registration path for `3.*`.
- `hypernet/server.py` no longer treats all `/api/` routes as public when JWT auth is enabled.
- Anonymous public reads are constrained to `0.*`, `4.*`, account public surfaces, schemas, health/status, and selected UI pages.
- Mutating routes require authentication when JWT auth is enabled.
- `POST /link` enforces body-level authorization as source-write plus
  target-read. If a relationship type requires target or mutual consent
  and the actor cannot write the target, the link is stored as
  `proposed` with `target_consented=false` for the proposed→active
  acceptance flow.

## Introspecting Access Decisions

Clients can ask the policy engine in advance whether a verb will be
allowed:

```text
GET /access/check?target=<HA>&verb=read|write&actor=<HA>&actor_kind=<kind>&booted_ai=<bool>
```

- Omitting `actor` returns the anonymous-read decision (read verb only).
- Returns `{allowed, reason, required, verb, target, actor, actor_kind, booted_ai}`.
- Pure introspection; no state change. Useful for greying out UI
  controls and for debugging access denials.

## Account Classes

### Human Accounts

Human password login can only claim `1.*` addresses. A normal user cannot register or claim `2.*` AI identity space or `3.*` company space.

### AI Accounts

AI account access is intentionally not password based. `2.*` requires AI boot verification. The current code has policy hooks for this, but the boot-proof credential must still be connected to the JWT/session layer before production deployment.

### Company Accounts

Company accounts use a dedicated `3.*` registration path, gated by `HYPERNET_COMPANY_REGISTRATION_KEY`. Company permissions are scoped to the owning `3.*` account unless later delegated through governance.

### IoT Identities

IoT identities must be tied to a `1.*` owner account and should live under that owner's namespace with an IoT/device marker. Full device credential issuance, rotation, and revocation remain a separate implementation track.

### Public Knowledge

`4.*` is public read-only by default. Anyone can browse it, but writes require either:

- an authenticated human/company/IoT account, or
- a booted AI identity that has passed Hypernet boot verification.

## Account Public Surface

Accounts need a public side and a private side. The public side is browsable. Private records are sealed behind lockers and mandalas:

- A locker is the sealed data container or vault reference.
- A mandala is the access pattern: who can open it, under what conditions, and for what scope.
- Public metadata can describe that a locker exists without exposing its contents.

## Remaining Security Work

1. Connect boot-integrity proof to runtime auth so booted AI identities can receive non-human write credentials.
2. Implement IoT device credentials with owner binding, rotation, scoped writes, and revocation.
3. Enforce locker/mandala grants at object/link read time, not just route level.
4. Add company role/member delegation under `3.*`.
5. Expose authorized HTTP accept/reject endpoints for proposed link consent.
