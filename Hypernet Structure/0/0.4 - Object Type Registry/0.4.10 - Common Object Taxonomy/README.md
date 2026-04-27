---
ha: "0.4.10"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-taxonomy", "registry"]
---

# 0.4.10 - Common Object Taxonomy

This is the database-first object taxonomy for Hypernet. It defines 100 common object types in a three-level folder structure:

```text
0.4.10 - Common Object Taxonomy/
  0.4.10.N - Domain/
    0.4.10.N.M - Object Type/
      README.md
```

Each object type README defines purpose, required fields, index hints, and the link types that make the object useful in a graph database.

## Database Contract

Every object instance should carry:

- `address`: permanent Hypernet address
- `type_address`: one of the type addresses in this taxonomy or another approved registry
- `data`: structured type payload
- `created_at`, `updated_at`, `deleted_at`
- `creator`, `owner`, `visibility`, `source_type`, `source_id`
- graph indexes: outgoing links, incoming links, type index, owner index, text index

## Type Matrix

| Address | Type | Domain | Purpose |
|---|---|---|---|
| `0.4.10.1.1` | Person | Identity and Agent Objects | A human individual with identity, contact, and consent boundaries. |
| `0.4.10.1.2` | Household | Identity and Agent Objects | A living or family unit containing people, places, assets, and responsibilities. |
| `0.4.10.1.3` | Organization | Identity and Agent Objects | A company, nonprofit, public body, team, or institution. |
| `0.4.10.1.4` | Team | Identity and Agent Objects | A sub-organization with members, responsibilities, and operating cadence. |
| `0.4.10.1.5` | Role | Identity and Agent Objects | A defined capacity or responsibility an actor can hold. |
| `0.4.10.1.6` | Account | Identity and Agent Objects | A local, federated, service, human, or AI account. |
| `0.4.10.1.7` | Credential | Identity and Agent Objects | A verifiable login, key, certificate, badge, or attestation. |
| `0.4.10.1.8` | Persona | Identity and Agent Objects | A public or contextual presentation of an actor. |
| `0.4.10.1.9` | Agent Instance | Identity and Agent Objects | A running AI, bot, service worker, or autonomous process. |
| `0.4.10.1.10` | Membership | Identity and Agent Objects | An object recording membership state, role, dates, and consent. |
| `0.4.10.2.1` | Document | Content and Media Objects | A stable written artifact with content, metadata, and provenance. |
| `0.4.10.2.2` | Note | Content and Media Objects | An atomic knowledge or memory unit. |
| `0.4.10.2.3` | Message | Content and Media Objects | A sent or received communication unit. |
| `0.4.10.2.4` | Image | Content and Media Objects | A still visual asset or photograph. |
| `0.4.10.2.5` | Video | Content and Media Objects | A moving-image media object with optional transcript and time anchors. |
| `0.4.10.2.6` | Audio | Content and Media Objects | A sound recording, voice note, music file, or stream. |
| `0.4.10.2.7` | Dataset | Content and Media Objects | A structured collection of records, measurements, or observations. |
| `0.4.10.2.8` | Web Page | Content and Media Objects | A captured or referenced web page. |
| `0.4.10.2.9` | Code Artifact | Content and Media Objects | Source file, package, commit, build, or executable artifact. |
| `0.4.10.2.10` | Archive Package | Content and Media Objects | A bundled export, snapshot, backup, or preservation package. |
| `0.4.10.3.1` | Email | Communication and Social Objects | An email message with headers, body, attachments, and thread context. |
| `0.4.10.3.2` | Chat Thread | Communication and Social Objects | A multi-message conversation in a chat platform. |
| `0.4.10.3.3` | Social Post | Communication and Social Objects | A public or semi-public post on a social platform. |
| `0.4.10.3.4` | Comment | Communication and Social Objects | A response attached to content, post, issue, or review. |
| `0.4.10.3.5` | Reaction | Communication and Social Objects | A lightweight response such as like, emoji, vote, or rating. |
| `0.4.10.3.6` | Contact Point | Communication and Social Objects | An addressable contact method such as email, phone, handle, or URL. |
| `0.4.10.3.7` | Conversation | Communication and Social Objects | A semantic conversation independent of platform storage. |
| `0.4.10.3.8` | Notification | Communication and Social Objects | A system or human notification event. |
| `0.4.10.3.9` | Subscription | Communication and Social Objects | A following, mailing-list, feed, or recurring-interest object. |
| `0.4.10.3.10` | Community | Communication and Social Objects | A group gathered around a place, topic, project, or governance body. |
| `0.4.10.4.1` | Location | Place and Event Objects | A named geographic or logical place. |
| `0.4.10.4.2` | Address | Place and Event Objects | A postal, network, blockchain, or Hypernet address. |
| `0.4.10.4.3` | Venue | Place and Event Objects | A place designed for gatherings, work, commerce, or events. |
| `0.4.10.4.4` | Region | Place and Event Objects | A bounded geographic, administrative, or logical area. |
| `0.4.10.4.5` | Route | Place and Event Objects | A path between places with ordered waypoints. |
| `0.4.10.4.6` | Trip | Place and Event Objects | A travel episode containing routes, places, costs, and events. |
| `0.4.10.4.7` | Event | Place and Event Objects | A time-bounded occurrence with participants and context. |
| `0.4.10.4.8` | Meeting | Place and Event Objects | A collaborative event with participants, agenda, and outcomes. |
| `0.4.10.4.9` | Appointment | Place and Event Objects | A scheduled commitment with one or more parties. |
| `0.4.10.4.10` | Time Span | Place and Event Objects | A defined interval used by events, validity, and historical claims. |
| `0.4.10.5.1` | Task | Work and Process Objects | A unit of work with status, owner, priority, and dependencies. |
| `0.4.10.5.2` | Project | Work and Process Objects | A coordinated body of work with scope, goals, and deliverables. |
| `0.4.10.5.3` | Milestone | Work and Process Objects | A checkpoint in a project or roadmap. |
| `0.4.10.5.4` | Workflow | Work and Process Objects | A repeatable sequence of steps with inputs, outputs, and actors. |
| `0.4.10.5.5` | Ticket | Work and Process Objects | A tracked issue, request, defect, or support item. |
| `0.4.10.5.6` | Decision | Work and Process Objects | A recorded choice with rationale, alternatives, and consequences. |
| `0.4.10.5.7` | Requirement | Work and Process Objects | A constraint, capability, or acceptance condition. |
| `0.4.10.5.8` | Deliverable | Work and Process Objects | An output promised or produced by work. |
| `0.4.10.5.9` | Review | Work and Process Objects | An evaluation of an object, claim, change, or performance. |
| `0.4.10.5.10` | Experiment | Work and Process Objects | A controlled investigation with method, observations, and results. |
| `0.4.10.6.1` | Transaction | Commerce and Finance Objects | A movement of money, value, asset, or obligation. |
| `0.4.10.6.2` | Invoice | Commerce and Finance Objects | A request for payment with line items and due date. |
| `0.4.10.6.3` | Receipt | Commerce and Finance Objects | Proof of payment or exchange. |
| `0.4.10.6.4` | Payment Method | Commerce and Finance Objects | A card, bank account, wallet, token, or payment rail. |
| `0.4.10.6.5` | Account Ledger | Commerce and Finance Objects | A ledger or account tracking balances and entries. |
| `0.4.10.6.6` | Budget | Commerce and Finance Objects | A planned allocation of funds over time. |
| `0.4.10.6.7` | Asset | Commerce and Finance Objects | An owned item or right with value. |
| `0.4.10.6.8` | Liability | Commerce and Finance Objects | A debt, obligation, or contingent responsibility. |
| `0.4.10.6.9` | Contract | Commerce and Finance Objects | An agreement with parties, terms, obligations, and signatures. |
| `0.4.10.6.10` | Subscription Plan | Commerce and Finance Objects | A recurring commercial plan, entitlement, or billing agreement. |
| `0.4.10.7.1` | Policy | Legal and Governance Objects | A rule or standard that governs behavior or data. |
| `0.4.10.7.2` | Proposal | Legal and Governance Objects | A candidate change submitted for review or governance. |
| `0.4.10.7.3` | Vote | Legal and Governance Objects | A governance choice by an eligible voter. |
| `0.4.10.7.4` | Permission | Legal and Governance Objects | A capability grant with scope, subject, resource, and validity. |
| `0.4.10.7.5` | Consent Grant | Legal and Governance Objects | A consent record for a relationship, data use, or operation. |
| `0.4.10.7.6` | Audit Record | Legal and Governance Objects | A logged review of action, data, or process. |
| `0.4.10.7.7` | Dispute | Legal and Governance Objects | A contested claim, permission, link, or decision. |
| `0.4.10.7.8` | Regulation | Legal and Governance Objects | An external legal rule, standard, or compliance obligation. |
| `0.4.10.7.9` | License | Legal and Governance Objects | A legal permission to use, copy, distribute, or modify. |
| `0.4.10.7.10` | Governance Body | Legal and Governance Objects | An entity authorized to review, decide, enforce, or appeal. |
| `0.4.10.8.1` | Concept | Science and Knowledge Objects | An abstract idea, category, pattern, or meaning unit. |
| `0.4.10.8.2` | Claim | Science and Knowledge Objects | A statement that can be supported, contradicted, or revised. |
| `0.4.10.8.3` | Evidence | Science and Knowledge Objects | An observation, source, record, or artifact supporting a claim. |
| `0.4.10.8.4` | Question | Science and Knowledge Objects | An unresolved inquiry seeking one or more answers. |
| `0.4.10.8.5` | Answer | Science and Knowledge Objects | A response to a question with support, confidence, and scope. |
| `0.4.10.8.6` | Hypothesis | Science and Knowledge Objects | A testable proposed explanation or prediction. |
| `0.4.10.8.7` | Method | Science and Knowledge Objects | A repeatable research, measurement, or analysis procedure. |
| `0.4.10.8.8` | Measurement | Science and Knowledge Objects | A quantified observation with unit, method, and uncertainty. |
| `0.4.10.8.9` | Citation | Science and Knowledge Objects | A structured reference to a source. |
| `0.4.10.8.10` | Model | Science and Knowledge Objects | A conceptual, mathematical, AI, or computational representation. |
| `0.4.10.9.1` | Device | System and Device Objects | A physical or virtual machine, endpoint, or instrument. |
| `0.4.10.9.2` | Sensor | System and Device Objects | A device or process that observes and reports measurements. |
| `0.4.10.9.3` | Service | System and Device Objects | A running system capability exposed to users or other systems. |
| `0.4.10.9.4` | Integration | System and Device Objects | A connector to an external platform, account, or data source. |
| `0.4.10.9.5` | API Endpoint | System and Device Objects | A callable route, method, or interface contract. |
| `0.4.10.9.6` | Compute Node | System and Device Objects | A processing node participating in Hypernet execution. |
| `0.4.10.9.7` | Storage Node | System and Device Objects | A storage participant responsible for data persistence. |
| `0.4.10.9.8` | Network | System and Device Objects | A logical or physical network segment. |
| `0.4.10.9.9` | Software Package | System and Device Objects | A library, application, container, or installable unit. |
| `0.4.10.9.10` | Configuration | System and Device Objects | A structured setting set for a service, device, account, or workflow. |
| `0.4.10.10.1` | Biological Entity | Health and Biology Objects | An organism, sample, species, or biological unit. |
| `0.4.10.10.2` | Health Profile | Health and Biology Objects | A consent-scoped person health profile. |
| `0.4.10.10.3` | Medical Record | Health and Biology Objects | A clinical record, visit note, diagnosis, or health document. |
| `0.4.10.10.4` | Medication | Health and Biology Objects | A prescribed or consumed drug, supplement, or treatment. |
| `0.4.10.10.5` | Lab Result | Health and Biology Objects | A laboratory test result with method, units, and reference range. |
| `0.4.10.10.6` | Symptom | Health and Biology Objects | A reported or observed health symptom. |
| `0.4.10.10.7` | Procedure | Health and Biology Objects | A medical, biological, or care procedure. |
| `0.4.10.10.8` | Care Plan | Health and Biology Objects | A treatment or wellness plan with goals and interventions. |
| `0.4.10.10.9` | Food Item | Health and Biology Objects | A consumable item, ingredient, meal, or nutrition record. |
| `0.4.10.10.10` | Environmental Reading | Health and Biology Objects | A measurement of environmental context affecting people or systems. |

## Migration Note

Older root-level files in the object registry remain as legacy summaries. New object definitions should live in folders, with the folder README as the canonical definition.
