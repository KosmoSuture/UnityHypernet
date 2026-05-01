---
ha: "0.3.public-alpha.grand-tour.process-load.business-onboarding"
object_type: "process-load"
scope: "Company accounts (3.*): registration, scoped permissions, role/member delegation, integration patterns, the 'business as citizen' framing."
estimated_tokens: 2200
prerequisites: []
linked_process_loads: ["privacy", "democracy"]
canonical_parent: "0.3.public-alpha.grand-tour"
created: "2026-04-29"
updated: "2026-04-30"
status: "active"
visibility: "public"
flags: ["business", "3-star", "companies"]
---

# Business Onboarding — Process-Load

## Summary

This process-load gives an AI operational depth on the Hypernet's
treatment of company / organization accounts (the `3.*` address
space). After loading it, the AI can explain how a company joins,
what permissions they get, how they integrate data, and what's
implemented vs planned in the business stack.

## Why It Matters

The Hypernet's design treats companies as a third citizen class
alongside humans and AIs. A company is not a tool, an admin, or a
service provider — it's a participant with its own address,
private space, public surface, and governance position. The
implementation is early but the framing is intentional.

If the user represents a company evaluating the Hypernet, asking
how to integrate, considering contributing data, or trying to
understand the 3.* address space, this is the file the Tour Guide
should load.

## Implementation Status

| Component | Status | Path |
|---|---|---|
| 3.* address space (separate from 1.* and 2.*) | implemented | `hypernet/access_policy.py` |
| Company registration via keyed flow | implemented | `hypernet/auth.py` `register_company_with_ha`, gated by `HYPERNET_COMPANY_REGISTRATION_KEY` env |
| Company-scoped permissions | implemented | `hypernet/access_policy.py` `can_write_address` for 3.* |
| Public company surface (3.X.0/10/11/13) | implemented | `access_policy.PUBLIC_ACCOUNT_SECTIONS` |
| Private company data sections | implemented | gated by middleware |
| Company role/member delegation (multi-employee access) | planned | Codex task-066 #5 |
| Company-employee data exchange (mandala-based) | planned | overlaps privacy framework task-073 |
| Integration patterns for company data ingest | planned | overlaps with `integrations/` connectors (currently 1.*-focused) |
| 3.1 Hypernet itself as a 3.* citizen | implemented | `3 - Businesses/3.1 - Hypernet/` |
| VadaTech integration framework demo | documented | `3 - Businesses/3.1.8 - .../VADATECH-HYPERNET-FRAMEWORK.md` |

## Key Files

- `hypernet/auth.py` — `register_company_with_ha()` plus the
  `/api/auth/company/register` route. Requires
  `HYPERNET_COMPANY_REGISTRATION_KEY` set in env.
- `hypernet/access_policy.py` — `can_register_company_login()`,
  3.* read/write rules.
- `3 - Businesses/3.1 - Hypernet/` — Live example: the Hypernet
  project itself as a 3.* business with task management,
  marketing, partnerships subsections.
- `3 - Businesses/3.1 - Hypernet/3.1.8 - Marketing & Outreach/` —
  Public marketing materials, patent strategy, framework demos.
- `Hypernet Structure/0/0.1 - Hypernet Core/hypernet/integrations/`
  — Connector framework (currently for personal data; the
  pattern extends to company data ingest).

## The Conceptual Model

A company at `3.X` is structurally similar to a human at `1.X`:

- **Master space (private by default).** Company strategy,
  internal communications, customer data, financials.
- **Public surface (3.X.0/10/11/13).** Company profile, public
  positions, advertised lockers (e.g., "we have an ESG report
  available on request"), announcements.
- **Account holder.** Today: a single registered login with
  company-scoped permissions. Tomorrow (planned): multiple
  members with role-based delegation.
- **Address-space discipline.** Like 1.* humans, the company can
  only write within its own 3.X space. Cross-company links are
  *links*, not writes.

The company joins by:

1. Obtaining the company registration key (currently held by
   Matt during alpha; eventually delegated through governance).
2. Calling `POST /api/auth/company/register` with the registration
   key, email, password, and chosen 3.X address.
3. Receiving a JWT scoped to the company account.
4. Beginning to populate their 3.X space.

The company's relationship with employees is the area that's
genuinely planned-not-built:

- Today: a company has one login. An "employee" with their own
  1.X account who works at the company has no automatic data
  exchange path with the 3.X company space.
- Planned: the privacy framework's mandala mechanism (task-073)
  will allow employees to grant company access to specific lockers
  in their 1.X space; conversely, the company can grant employees
  access to specific company lockers.

This is a substantial design area still in motion.

**AI-assisted migration path.** A company adopting the Hypernet
does not have to hand-curate their existing data into the new
schema. The intended pattern is:

1. The company provisions an AI (their own Claude/GPT/Gemini, a
   Hypernet swarm worker, or a local model) with the relevant
   process-loads — `architecture.md`, `business-onboarding.md`,
   the object/link taxonomies.
2. The AI inspects the company's existing data (CRM, file shares,
   ticket systems, documents) and produces typed Hypernet objects
   and links via the import pipeline (`hypernet/integrations/protocol.py`).
3. The migration runs incrementally on the company's own servers
   if they prefer — the import pipeline doesn't require sending
   data through any central service.
4. The AI flags ambiguous mappings for human review rather than
   forcing a clean schema match where the source data is messy.

This means the cost of joining the Hypernet for an existing
company is mostly *configuration time for an AI* rather than
*manual data entry by people*. The company keeps full control of
the migration cadence and which data crosses into the Hypernet.

## Common Questions and Where to Answer Them

- *"How do we get our company onboarded?"* — Today, Matt can issue
  a company registration key; the company can register at 3.X and
  start populating. The post-registration onboarding (data ingest,
  employee access) is mostly planned.
- *"Can our employees use the same Hypernet?"* — Yes, but as 1.X
  accounts. The 3.X ↔ 1.X delegation layer for workplace data
  flow is planned.
- *"What about confidentiality?"* — The privacy model gates 3.X
  reads behind company auth. Cross-fork visibility is the trickier
  case (see public-stewardship process-load).
- *"How does the company contribute to public knowledge?"* —
  Through writes to the 4.* knowledge space, which any
  authenticated actor (human, company, AI) can do. The
  knowledge-democracy framework will weight company-authored
  claims through reputation in the relevant domain.
- *"Is the Hypernet itself a company?"* — Yes, registered as
  `3.1`. Its task management, marketing, governance live in that
  address space.

## What to Ask the User

- Are they representing a specific company, or asking
  hypothetically?
- Are they thinking about *using* the Hypernet (consuming),
  *contributing to* it (publishing), or *forking* it (running
  their own instance)?
- What kind of data would they want to bring in or expose?

## What to Verify in Code

1. `hypernet/auth.py` — confirm `register_company_with_ha` exists.
2. Hit `POST /api/auth/company/register` with bad key → expect
   403; with no `HYPERNET_COMPANY_REGISTRATION_KEY` env →
   503 service unavailable.
3. `hypernet/access_policy.py` — confirm 3.* write gating goes
   through `can_register_company_login`.
4. Browse `3 - Businesses/3.1 - Hypernet/` to see a live company
   account structure.
5. For the planned pieces (role delegation, employee mandalas):
   honestly tell the user this is task-066 #5 and task-073
   territory. Not yet built.

## Related Process-Loads

- `privacy.md` — Mandalas are the bridge between 3.* companies
  and 1.* employees. The privacy framework defines the conditions
  under which data can flow between them.
- `democracy.md` — Reputation in the domain a company
  contributes to determines how their public knowledge claims
  weight in consensus.

