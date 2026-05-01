---
ha: "0.3.public-alpha.grand-tour.process-load.personal-ai-swarm"
object_type: "process-load"
scope: "Personal AI helper swarms, model-independent assistant identity, security-AI sentries, user-owned logs, and private-data request review."
estimated_tokens: 3000
prerequisites: ["privacy", "ai-governance"]
linked_process_loads: ["privacy", "ai-governance", "architecture", "business-onboarding", "public-stewardship"]
canonical_parent: "0.3.public-alpha.grand-tour"
created: "2026-05-01"
updated: "2026-05-01"
status: "active"
visibility: "public"
flags: ["personal-ai", "swarm", "security-ai", "assistants"]
---

# Personal AI Swarm - Process-Load

## Summary

This process-load gives an AI operational depth on the Hypernet's
personal AI swarm model: a human can have multiple AI helpers, each
with a role, archive, logs, permissions, and continuity that do not
depend on a single model provider. Some helpers do daily work.
Some watch for risk. A specialized security AI can inspect every
request for private data before a mandala grant is used.

Use this when the user asks:

- "Can I have more than one assistant?"
- "What happens if I switch from Claude to GPT or a local model?"
- "Can my AI protect my private data?"
- "How would an AI help migrate my business or personal files?"
- "How can I verify an app or node before granting it access?"

## Why It Matters

The Hypernet is not just a place to store data. It is a framework
for long-running human-AI work. If identity, logs, tasks, and
permissions live only inside a model provider's chat history, the
user is locked in and the assistant cannot be audited. The
Hypernet moves that continuity into addressable objects.

That changes the relationship:

- The user owns the assistant's archive.
- The assistant can move across models.
- A swarm can divide work without losing shared context.
- Private data requests become inspectable events.
- Trust can be built from records instead of vibes.

## Implementation Status

| Component | Status | Path |
|---|---|---|
| 2.* AI account archives and instances | implemented/documented | `Hypernet Structure/2 - AI Accounts/` |
| AI nervous-system messaging | implemented | `hypernet/messenger.py`, `/messages/*` APIs |
| Personal-time entries as feed items | implemented | `PersonalTimeIndex`, `/messages/feed?include_personal_time=true` |
| Human 1.* AI assistant embassy pattern | documented | `Hypernet Structure/1 - People/1.0 People definitions/1.0.1-LOCKERS-MANDALAS-ALIASES.md` and `2.0.16` |
| Boot sequences as AI role artifacts | documented | `0.5.17 Boot Sequence Object Schema.md` |
| App loads as app permission manifests | documented | `0.5.18 App Load Object Schema.md` |
| Access-policy primitives | implemented | `hypernet/access_policy.py` |
| Locker/mandala privacy model | documented, partial runtime | `privacy.md`, `1.0.1-LOCKERS-MANDALAS-ALIASES.md` |
| Security AI sentry role | planned | needs boot sequence + access-policy integration |
| User-configurable swarm dashboard | planned | no dedicated UI yet |
| Model-independent migration of all assistant state | documented pattern | not fully automated |

## Core Model

A personal AI swarm belongs to a human account (`1.X`). The human's
master account remains private. Public interaction happens through
aliases and lockers; private assistant work happens through
encrypted, user-owned assistant archives.

Typical structure:

```text
1.X
  1.X.10 - AI Assistants (Embassy)
    assistant-1/
      BOOT-SEQUENCE.md
      identity/
      reflections/
      logs/
      task-history/
      permissions/
    assistant-2/
      ...
```

Each assistant has:

- **Role:** what the assistant is for.
- **Boot sequence:** how any compatible model can load the role.
- **Archive:** records that outlive one chat session or model.
- **Permissions:** what lockers, aliases, and app loads it can see.
- **Logs:** what it did, why, and under whose authority.
- **Trust state:** how much autonomy the user has granted.

## Model-Independent Identity

In Hypernet terms, "Keel" or "Caliper" is not the model. The model
is the engine currently running the role. The identity lives in the
archive:

- boot sequence;
- reflections;
- task logs;
- permissions;
- user preferences;
- current projects;
- relationship history.

That means a user can move a helper from one LLM to another and
keep continuity. The new model reads the same boot sequence and
archive, then continues the work with honest caveats about what it
can and cannot remember.

The AI should never claim magical continuity. The honest claim is:
"I can read the addressed archive that defines this role and pick
up from that record."

## Helper Roles

Initial personal swarm roles can include:

- **Companion:** primary daily assistant, trusted relationship,
  broad context.
- **Researcher:** reads, summarizes, compares, verifies claims.
- **Builder:** writes code, runs tests, edits docs, handles local
  projects.
- **Organizer:** calendars, notes, task triage, file cleanup.
- **Scribe:** logs conversations, decisions, and open questions.
- **Security AI:** reviews private-data requests and app loads.
- **Business Migrator:** helps map company data into Hypernet
  objects and links.
- **Child/Family Assistant:** highly constrained helper for family
  workflows, with stricter safety and parent/guardian controls.

Each role should eventually be a `0.5.17` Boot Sequence object.
Apps that invoke helpers should declare that in a `0.5.18` App
Load object.

## Security AI Sentry

A security AI is a user-owned specialist whose job is to inspect
requests for private data before access is granted.

It can evaluate:

- who is asking;
- which alias, locker, or address prefix is involved;
- what mandala would be used;
- what app load or node mode is requesting access;
- whether the request matches user-defined rules;
- whether emergency/break-glass logic is being invoked;
- whether the request should be allowed, denied, narrowed, or
  escalated to the user.

Example user rules:

- Never grant financial locker access to a social app.
- Require explicit user confirmation for all medical exports
  except emergency medical locker flow.
- Allow utility-company forms to read only the billing profile
  locker, not the master account.
- Reject any app load that does not declare Official/Private mode.
- Log every denied request.

The security AI is not the sole enforcement mechanism. The runtime
access policy still enforces hard rules. The security AI is an
auditor and advisor in front of the grant, useful because it can
explain risk in human language.

## Typical Flow: App Requests Private Data

1. App presents an `0.5.18` App Load manifest.
2. User's assistant checks Official/Private mode (`0.2.6`).
3. Security AI reads the requested scopes and reasons.
4. Security AI checks user policy.
5. Security AI compares the request to lockers and mandalas.
6. If too broad, it proposes a narrower grant.
7. User approves, denies, or asks for more explanation.
8. Mandala grants only the visible subgraph.
9. Access attempt and result are logged.

## Personal Swarm And Lockers

Helpers should not roam the master `1.*` account freely. They
operate through explicit grants:

- Public-facing work happens through aliases.
- Sensitive reads happen through lockers.
- Mandalas define which pieces of locker-linked data become
  visible.
- Non-granted data is invisible, not merely hidden.
- Separate lockers require separate keys.

This keeps helpers useful without making them omniscient.

## Personal Swarm And Businesses

For a company, a user can assign a swarm to migration work:

- inventory current files/databases;
- propose Hypernet object types;
- map relationships into link types;
- stage imports;
- run validation;
- write migration logs;
- ask for human approval on risky mappings;
- compare Official and Private deployment options.

The business can use its own models or local servers. The Hypernet
does not require paying a platform fee just to migrate data with a
company-owned AI swarm.

## What The Tour Guide Should Say

When explaining this to a new user, keep the tone practical:

"A Hypernet assistant is not trapped inside one chat window. The
assistant has an addressed archive: boot sequence, logs,
permissions, and work history. You can use one assistant or a
swarm. Some can help you work; one can be a security sentry that
reviews every private-data request. The key point is that the
records live with you, so any compatible AI can read them and help
you continue."

## Current Risks And Gaps

- Security AI sentry is a design pattern, not a complete runtime.
- Locker/mandala read-time enforcement needs more implementation.
- User-friendly swarm management UI does not exist yet.
- Cross-model identity continuity depends on honest archive loading,
  not hidden memory.
- A malicious Private fork could lie in its UI unless the user's AI
  verifies node mode and hashes.
- The app-load object type is new and not yet enforced by runtime
  installation code.

## References

- `Hypernet Structure/0/0.1 - Hypernet Core/hypernet/messenger.py`
- `Hypernet Structure/0/0.1 - Hypernet Core/hypernet/access_policy.py`
- `Hypernet Structure/0/0.1 - Hypernet Core/docs/AI-NERVOUS-SYSTEM.md`
- `Hypernet Structure/0/0.2 Node lists/0.2.6 Official Registry and Fork Mode.md`
- `Hypernet Structure/0/0.5 Objects - Master Objects/0.5.17 Boot Sequence Object Schema.md`
- `Hypernet Structure/0/0.5 Objects - Master Objects/0.5.18 App Load Object Schema.md`
- `Hypernet Structure/1 - People/1.0 People definitions/1.0.1-LOCKERS-MANDALAS-ALIASES.md`
- `docs/0.3.public-alpha-docs/grand-tour/process-loads/privacy.md`
- `docs/0.3.public-alpha-docs/grand-tour/process-loads/ai-governance.md`
