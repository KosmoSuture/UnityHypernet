"""Generate database-first taxonomy folders for the Hypernet archive.

This script is intentionally deterministic. It creates concise README files for:
- 100 common object types under 0.4.10
- 100 common link types under 0.6.11
- a three-level knowledgebase structure under 4 - Knowledge

Run from the repository root:
    python "Hypernet Structure/0/0.1 - Hypernet Core/scripts/generate_database_first_taxonomy.py"
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
STRUCTURE = ROOT / "Hypernet Structure"


@dataclass(frozen=True)
class ObjectType:
    name: str
    purpose: str
    required: tuple[str, ...]
    links: tuple[str, ...]


@dataclass(frozen=True)
class ObjectDomain:
    name: str
    purpose: str
    types: tuple[ObjectType, ...]


@dataclass(frozen=True)
class LinkType:
    name: str
    source: str
    target: str
    purpose: str
    directed: bool = True
    symmetric: bool = False
    transitive: bool = False
    inverse: str = ""


@dataclass(frozen=True)
class LinkDomain:
    name: str
    purpose: str
    types: tuple[LinkType, ...]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def slug(name: str) -> str:
    return (
        name.replace("&", "and")
        .replace("/", " ")
        .replace("(", "")
        .replace(")", "")
        .replace(",", "")
        .replace("  ", " ")
        .strip()
    )


OBJECT_DOMAINS: tuple[ObjectDomain, ...] = (
    ObjectDomain(
        "Identity and Agent Objects",
        "Actors, accounts, roles, and identity-bearing entities.",
        (
            ObjectType("Person", "A human individual with identity, contact, and consent boundaries.", ("name", "identity_status", "owner"), ("knows", "member_of", "consented_by")),
            ObjectType("Household", "A living or family unit containing people, places, assets, and responsibilities.", ("name", "members", "primary_location"), ("contains", "guardian_of", "located_at")),
            ObjectType("Organization", "A company, nonprofit, public body, team, or institution.", ("name", "legal_status", "jurisdiction"), ("employed_by", "founded", "governed_by")),
            ObjectType("Team", "A sub-organization with members, responsibilities, and operating cadence.", ("name", "organization", "purpose"), ("part_of", "member_of", "assigned_to")),
            ObjectType("Role", "A defined capacity or responsibility an actor can hold.", ("title", "scope", "permissions"), ("acts_as", "granted_permission", "reports_to")),
            ObjectType("Account", "A local, federated, service, human, or AI account.", ("account_id", "owner", "provider"), ("owns_identity", "instance_of", "permission_grants")),
            ObjectType("Credential", "A verifiable login, key, certificate, badge, or attestation.", ("credential_type", "issuer", "subject"), ("issued_by", "verifies", "expires_at")),
            ObjectType("Persona", "A public or contextual presentation of an actor.", ("name", "represented_actor", "context"), ("persona_of", "acts_as", "visible_from")),
            ObjectType("Agent Instance", "A running AI, bot, service worker, or autonomous process.", ("name", "model_or_runtime", "account"), ("instance_of_account", "session_of", "generated_by")),
            ObjectType("Membership", "An object recording membership state, role, dates, and consent.", ("member", "group", "status"), ("member_of", "valid_during", "approved_by")),
        ),
    ),
    ObjectDomain(
        "Content and Media Objects",
        "Human-readable, machine-readable, and media-bearing content.",
        (
            ObjectType("Document", "A stable written artifact with content, metadata, and provenance.", ("title", "format", "content_ref"), ("authored_by", "cites", "version_of")),
            ObjectType("Note", "An atomic knowledge or memory unit.", ("title", "body", "created_at"), ("about", "similar_to", "derived_from")),
            ObjectType("Message", "A sent or received communication unit.", ("sender", "recipient", "body"), ("sent_from", "sent_to", "replies_to")),
            ObjectType("Image", "A still visual asset or photograph.", ("file_ref", "mime_type", "dimensions"), ("depicts", "taken_at", "part_of")),
            ObjectType("Video", "A moving-image media object with optional transcript and time anchors.", ("file_ref", "duration", "mime_type"), ("transcript_of", "during", "generated_by")),
            ObjectType("Audio", "A sound recording, voice note, music file, or stream.", ("file_ref", "duration", "mime_type"), ("transcript_of", "created_by", "part_of")),
            ObjectType("Dataset", "A structured collection of records, measurements, or observations.", ("schema", "records_ref", "license"), ("cites", "derived_from", "supports")),
            ObjectType("Web Page", "A captured or referenced web page.", ("url", "title", "capture_status"), ("references", "archived_from", "about")),
            ObjectType("Code Artifact", "Source file, package, commit, build, or executable artifact.", ("name", "language", "repository_ref"), ("implements", "depends_on", "reviewed_by")),
            ObjectType("Archive Package", "A bundled export, snapshot, backup, or preservation package.", ("package_ref", "created_at", "contents"), ("contains", "archived_from", "version_of")),
        ),
    ),
    ObjectDomain(
        "Communication and Social Objects",
        "Social, conversational, and notification surfaces.",
        (
            ObjectType("Email", "An email message with headers, body, attachments, and thread context.", ("message_id", "from", "to"), ("sent_from", "sent_to", "replies_to")),
            ObjectType("Chat Thread", "A multi-message conversation in a chat platform.", ("participants", "platform", "started_at"), ("contains", "mentions", "about")),
            ObjectType("Social Post", "A public or semi-public post on a social platform.", ("platform", "author", "body"), ("authored_by", "mentions", "shared_by")),
            ObjectType("Comment", "A response attached to content, post, issue, or review.", ("author", "body", "parent"), ("replies_to", "about", "authored_by")),
            ObjectType("Reaction", "A lightweight response such as like, emoji, vote, or rating.", ("actor", "target", "reaction_type"), ("reacts_to", "voted_on", "sent_from")),
            ObjectType("Contact Point", "An addressable contact method such as email, phone, handle, or URL.", ("value", "kind", "owner"), ("belongs_to", "verified_by", "expires_at")),
            ObjectType("Conversation", "A semantic conversation independent of platform storage.", ("participants", "topic", "time_range"), ("contains", "about", "during")),
            ObjectType("Notification", "A system or human notification event.", ("recipient", "event", "status"), ("notifies", "triggered_by", "expires_at")),
            ObjectType("Subscription", "A following, mailing-list, feed, or recurring-interest object.", ("subscriber", "source", "status"), ("subscribes_to", "recurring_on", "permission_grants")),
            ObjectType("Community", "A group gathered around a place, topic, project, or governance body.", ("name", "scope", "membership_policy"), ("member_of", "governed_by", "contains")),
        ),
    ),
    ObjectDomain(
        "Place and Event Objects",
        "Locations, spaces, movements, and time-bounded happenings.",
        (
            ObjectType("Location", "A named geographic or logical place.", ("name", "coordinates_or_path", "location_type"), ("located_at", "within_radius_of", "contained_in")),
            ObjectType("Address", "A postal, network, blockchain, or Hypernet address.", ("address_text", "address_type", "owner"), ("located_at", "owned_by", "verified_by")),
            ObjectType("Venue", "A place designed for gatherings, work, commerce, or events.", ("name", "location", "capacity"), ("located_at", "hosts", "part_of")),
            ObjectType("Region", "A bounded geographic, administrative, or logical area.", ("name", "boundary", "jurisdiction"), ("contains", "governed_by", "near")),
            ObjectType("Route", "A path between places with ordered waypoints.", ("origin", "destination", "waypoints"), ("route_from", "route_to", "contains")),
            ObjectType("Trip", "A travel episode containing routes, places, costs, and events.", ("traveler", "start_time", "end_time"), ("during", "contains", "paid_for")),
            ObjectType("Event", "A time-bounded occurrence with participants and context.", ("title", "time_range", "location"), ("during", "attended_by", "caused")),
            ObjectType("Meeting", "A collaborative event with participants, agenda, and outcomes.", ("participants", "scheduled_for", "agenda"), ("scheduled_for", "attended_by", "resulted_in")),
            ObjectType("Appointment", "A scheduled commitment with one or more parties.", ("participant", "scheduled_for", "status"), ("scheduled_for", "assigned_to", "located_at")),
            ObjectType("Time Span", "A defined interval used by events, validity, and historical claims.", ("start", "end", "timezone"), ("before", "after", "overlaps")),
        ),
    ),
    ObjectDomain(
        "Work and Process Objects",
        "Tasks, projects, decisions, experiments, and repeatable work.",
        (
            ObjectType("Task", "A unit of work with status, owner, priority, and dependencies.", ("title", "status", "priority"), ("assigned_to", "depends_on", "blocks")),
            ObjectType("Project", "A coordinated body of work with scope, goals, and deliverables.", ("title", "status", "owner"), ("contains", "milestone_of", "funded_by")),
            ObjectType("Milestone", "A checkpoint in a project or roadmap.", ("title", "target_date", "criteria"), ("milestone_of", "depends_on", "approved_by")),
            ObjectType("Workflow", "A repeatable sequence of steps with inputs, outputs, and actors.", ("name", "steps", "owner"), ("contains", "implements", "governed_by")),
            ObjectType("Ticket", "A tracked issue, request, defect, or support item.", ("title", "status", "source"), ("assigned_to", "blocks", "resolved_by")),
            ObjectType("Decision", "A recorded choice with rationale, alternatives, and consequences.", ("question", "decision", "rationale"), ("decided_by", "supersedes", "governed_by")),
            ObjectType("Requirement", "A constraint, capability, or acceptance condition.", ("statement", "priority", "verification"), ("implemented_by", "tests", "depends_on")),
            ObjectType("Deliverable", "An output promised or produced by work.", ("title", "owner", "acceptance_state"), ("delivers", "part_of_project", "approved_by")),
            ObjectType("Review", "An evaluation of an object, claim, change, or performance.", ("reviewer", "target", "finding"), ("reviews", "supports", "contradicts")),
            ObjectType("Experiment", "A controlled investigation with method, observations, and results.", ("hypothesis", "method", "status"), ("tests", "supports", "generated_by")),
        ),
    ),
    ObjectDomain(
        "Commerce and Finance Objects",
        "Financial events, obligations, instruments, and value flows.",
        (
            ObjectType("Transaction", "A movement of money, value, asset, or obligation.", ("amount", "currency", "parties"), ("paid_for", "billed_to", "credits")),
            ObjectType("Invoice", "A request for payment with line items and due date.", ("issuer", "recipient", "amount_due"), ("billed_to", "paid_by", "references")),
            ObjectType("Receipt", "Proof of payment or exchange.", ("seller", "buyer", "amount"), ("paid_for", "purchased_from", "evidence_for")),
            ObjectType("Payment Method", "A card, bank account, wallet, token, or payment rail.", ("provider", "owner", "method_type"), ("owned_by", "used_for", "expires_at")),
            ObjectType("Account Ledger", "A ledger or account tracking balances and entries.", ("account_name", "currency", "owner"), ("contains", "audited_by", "governed_by")),
            ObjectType("Budget", "A planned allocation of funds over time.", ("owner", "period", "allocations"), ("allocated_to", "approved_by", "during")),
            ObjectType("Asset", "An owned item or right with value.", ("name", "owner", "valuation"), ("owned_by", "values_at", "licensed_to")),
            ObjectType("Liability", "A debt, obligation, or contingent responsibility.", ("debtor", "creditor", "amount"), ("owed_to", "secured_by", "expires_at")),
            ObjectType("Contract", "An agreement with parties, terms, obligations, and signatures.", ("parties", "effective_date", "terms_ref"), ("governed_by", "signed_by", "licenses_to")),
            ObjectType("Subscription Plan", "A recurring commercial plan, entitlement, or billing agreement.", ("provider", "subscriber", "cadence"), ("subscription_of", "recurring_on", "billed_to")),
        ),
    ),
    ObjectDomain(
        "Legal and Governance Objects",
        "Rules, permissions, consent, audit, and collective decisions.",
        (
            ObjectType("Policy", "A rule or standard that governs behavior or data.", ("title", "scope", "authority"), ("governed_by", "enforces", "supersedes")),
            ObjectType("Proposal", "A candidate change submitted for review or governance.", ("title", "proposer", "status"), ("proposed_by", "voted_on", "approved_by")),
            ObjectType("Vote", "A governance choice by an eligible voter.", ("voter", "proposal", "choice"), ("voted_on", "cast_by", "during")),
            ObjectType("Permission", "A capability grant with scope, subject, resource, and validity.", ("subject", "resource", "actions"), ("permission_grants", "expires_at", "revoked_by")),
            ObjectType("Consent Grant", "A consent record for a relationship, data use, or operation.", ("grantor", "grantee", "scope"), ("consented_by", "permission_grants", "expires_at")),
            ObjectType("Audit Record", "A logged review of action, data, or process.", ("actor", "target", "result"), ("audited_by", "evidence_for", "during")),
            ObjectType("Dispute", "A contested claim, permission, link, or decision.", ("claim", "raised_by", "status"), ("disputes", "resolved_by", "appeals")),
            ObjectType("Regulation", "An external legal rule, standard, or compliance obligation.", ("jurisdiction", "authority", "text_ref"), ("governs", "requires", "supersedes")),
            ObjectType("License", "A legal permission to use, copy, distribute, or modify.", ("licensor", "licensee", "terms"), ("licenses_to", "governed_by", "expires_at")),
            ObjectType("Governance Body", "An entity authorized to review, decide, enforce, or appeal.", ("name", "scope", "membership"), ("governs", "ratified_by", "member_of")),
        ),
    ),
    ObjectDomain(
        "Science and Knowledge Objects",
        "Concepts, claims, evidence, methods, and models.",
        (
            ObjectType("Concept", "An abstract idea, category, pattern, or meaning unit.", ("label", "definition", "domain"), ("broader_than", "narrower_than", "similar_to")),
            ObjectType("Claim", "A statement that can be supported, contradicted, or revised.", ("statement", "scope", "confidence"), ("supports", "contradicts", "cites")),
            ObjectType("Evidence", "An observation, source, record, or artifact supporting a claim.", ("source", "method", "confidence"), ("evidence_for", "derived_from", "verified_by")),
            ObjectType("Question", "An unresolved inquiry seeking one or more answers.", ("question", "domain", "status"), ("asks", "about", "answered_by")),
            ObjectType("Answer", "A response to a question with support, confidence, and scope.", ("answer", "question", "confidence"), ("answers", "supports", "cites")),
            ObjectType("Hypothesis", "A testable proposed explanation or prediction.", ("statement", "variables", "test_plan"), ("tests", "implies", "supports")),
            ObjectType("Method", "A repeatable research, measurement, or analysis procedure.", ("name", "steps", "limitations"), ("implements", "tests", "cited_by")),
            ObjectType("Measurement", "A quantified observation with unit, method, and uncertainty.", ("quantity", "unit", "value"), ("measured_by", "evidence_for", "during")),
            ObjectType("Citation", "A structured reference to a source.", ("source", "locator", "style"), ("cites", "references", "evidence_for")),
            ObjectType("Model", "A conceptual, mathematical, AI, or computational representation.", ("name", "inputs", "outputs"), ("derived_from", "predicts", "trained_on")),
        ),
    ),
    ObjectDomain(
        "System and Device Objects",
        "Hardware, software, services, networks, and operational configuration.",
        (
            ObjectType("Device", "A physical or virtual machine, endpoint, or instrument.", ("name", "owner", "device_type"), ("owned_by", "located_at", "connected_to")),
            ObjectType("Sensor", "A device or process that observes and reports measurements.", ("name", "measurement_type", "location"), ("measures", "connected_to", "located_at")),
            ObjectType("Service", "A running system capability exposed to users or other systems.", ("name", "endpoint", "owner"), ("depends_on", "implements", "monitored_by")),
            ObjectType("Integration", "A connector to an external platform, account, or data source.", ("provider", "auth_status", "scope"), ("imports_from", "permission_grants", "owned_by")),
            ObjectType("API Endpoint", "A callable route, method, or interface contract.", ("method", "path", "schema"), ("implemented_by", "depends_on", "tested_by")),
            ObjectType("Compute Node", "A processing node participating in Hypernet execution.", ("node_id", "capabilities", "status"), ("registered_by", "connected_to", "governed_by")),
            ObjectType("Storage Node", "A storage participant responsible for data persistence.", ("node_id", "capacity", "replication_policy"), ("replicates", "contains", "governed_by")),
            ObjectType("Network", "A logical or physical network segment.", ("name", "address_space", "policy"), ("contains", "connected_to", "governed_by")),
            ObjectType("Software Package", "A library, application, container, or installable unit.", ("name", "version", "source"), ("depends_on", "implements", "licensed_to")),
            ObjectType("Configuration", "A structured setting set for a service, device, account, or workflow.", ("target", "version", "settings_ref"), ("configures", "version_of", "approved_by")),
        ),
    ),
    ObjectDomain(
        "Health and Biology Objects",
        "Biological, medical, wellness, and environmental records.",
        (
            ObjectType("Biological Entity", "An organism, sample, species, or biological unit.", ("name", "taxonomy_or_identity", "source"), ("part_of", "sampled_from", "related_to")),
            ObjectType("Health Profile", "A consent-scoped person health profile.", ("person", "scope", "privacy_level"), ("owned_by", "consented_by", "governed_by")),
            ObjectType("Medical Record", "A clinical record, visit note, diagnosis, or health document.", ("subject", "provider", "record_date"), ("about", "authored_by", "evidence_for")),
            ObjectType("Medication", "A prescribed or consumed drug, supplement, or treatment.", ("name", "dosage", "schedule"), ("prescribed_by", "part_of_care_plan", "expires_at")),
            ObjectType("Lab Result", "A laboratory test result with method, units, and reference range.", ("test_name", "value", "unit"), ("measured_by", "evidence_for", "about")),
            ObjectType("Symptom", "A reported or observed health symptom.", ("subject", "description", "time_range"), ("about", "during", "possibly_caused_by")),
            ObjectType("Procedure", "A medical, biological, or care procedure.", ("name", "provider", "time_range"), ("performed_by", "during", "part_of_care_plan")),
            ObjectType("Care Plan", "A treatment or wellness plan with goals and interventions.", ("subject", "goals", "owner"), ("contains", "approved_by", "scheduled_for")),
            ObjectType("Food Item", "A consumable item, ingredient, meal, or nutrition record.", ("name", "nutrition", "source"), ("consumed_by", "contains", "about")),
            ObjectType("Environmental Reading", "A measurement of environmental context affecting people or systems.", ("measurement", "location", "time"), ("measured_by", "located_at", "during")),
        ),
    ),
)


LINK_DOMAINS: tuple[LinkDomain, ...] = (
    LinkDomain(
        "Identity and Actor Links",
        "Relationships among people, accounts, roles, and representatives.",
        (
            LinkType("knows", "Person", "Person", "A personal or professional acquaintance.", False, True, False),
            LinkType("related_to", "Person", "Person", "A family, social, or general relation.", False, True, False),
            LinkType("spouse_of", "Person", "Person", "A spouse or marriage relationship.", False, True, False),
            LinkType("parent_of", "Person", "Person", "A parent-child relationship.", True, False, True, "child_of"),
            LinkType("guardian_of", "Person", "Person", "A legal or care guardian relationship.", True, False, False, "guarded_by"),
            LinkType("member_of_household", "Person", "Household", "A person belongs to a household.", True, False, False, "household_has_member"),
            LinkType("represents", "Actor", "Actor", "An actor represents another actor or organization.", True, False, False, "represented_by"),
            LinkType("acts_as", "Actor", "Role", "An actor performs under a role or capacity.", True, False, False, "role_held_by"),
            LinkType("owns_identity", "Actor", "Account", "An actor controls an identity or account.", True, False, False, "identity_owned_by"),
            LinkType("delegates_to", "Actor", "Actor", "Authority or task responsibility is delegated.", True, False, False, "delegated_by"),
        ),
    ),
    LinkDomain(
        "Authorship and Provenance Links",
        "Who made, changed, imported, generated, or preserved something.",
        (
            LinkType("authored_by", "Content", "Actor", "Authorship attribution.", True, False, False, "authored"),
            LinkType("created_by", "Object", "Actor", "Creation attribution.", True, False, False, "created"),
            LinkType("edited_by", "Content", "Actor", "Editing attribution.", True, False, False, "edited"),
            LinkType("contributed_to", "Actor", "Object", "Contribution attribution.", True, False, False, "has_contributor"),
            LinkType("generated_by", "Content", "Agent Instance", "Generated by an AI, script, or service.", True, False, False, "generated"),
            LinkType("imported_from", "Object", "Integration", "Imported from an external source.", True, False, False, "source_imported"),
            LinkType("derived_from", "Object", "Object", "Derived from prior source material.", True, False, True, "source_of"),
            LinkType("version_of", "Object", "Object", "A version or revision of another object.", True, False, True, "has_version"),
            LinkType("supersedes", "Object", "Object", "Replaces an older version or decision.", True, False, True, "superseded_by"),
            LinkType("archived_from", "Archive Package", "Object", "Snapshot or archive source.", True, False, False, "archived_as"),
        ),
    ),
    LinkDomain(
        "Containment and Hierarchy Links",
        "Part-whole, category, collection, and indexing structure.",
        (
            LinkType("contains", "Container", "Object", "A container includes an object.", True, False, True, "contained_in"),
            LinkType("part_of", "Object", "Object", "An object is a component of a whole.", True, False, True, "has_part"),
            LinkType("instance_of", "Object", "Type", "An object instantiates a type.", True, False, False, "has_instance"),
            LinkType("type_of", "Type", "Object", "A type classifies an object.", True, False, False, "has_type"),
            LinkType("broader_than", "Concept", "Concept", "A concept is broader than another.", True, False, True, "narrower_than"),
            LinkType("narrower_than", "Concept", "Concept", "A concept is narrower than another.", True, False, True, "broader_than"),
            LinkType("parent_collection_of", "Collection", "Collection", "A collection contains another collection.", True, False, True, "child_collection_of"),
            LinkType("located_within", "Object", "Location", "An object is spatially contained in a location.", True, False, True, "spatially_contains"),
            LinkType("composed_of", "Object", "Object", "A whole is composed of components.", True, False, True, "component_of"),
            LinkType("indexes", "Index", "Object", "An index points to indexed objects.", True, False, False, "indexed_by"),
        ),
    ),
    LinkDomain(
        "Semantic and Knowledge Links",
        "Meaning, claims, questions, evidence, and conceptual graph edges.",
        (
            LinkType("about", "Object", "Concept", "An object is about a topic or concept.", True, False, False, "has_aboutness"),
            LinkType("cites", "Content", "Content", "Formal or informal citation.", True, False, False, "cited_by"),
            LinkType("supports", "Evidence", "Claim", "Evidence supports a claim.", True, False, False, "supported_by"),
            LinkType("contradicts", "Evidence", "Claim", "Evidence or claim contradicts another.", True, False, False, "contradicted_by"),
            LinkType("explains", "Object", "Object", "One object explains another.", True, False, False, "explained_by"),
            LinkType("answers", "Answer", "Question", "An answer responds to a question.", True, False, False, "answered_by"),
            LinkType("asks", "Actor", "Question", "An actor asks a question.", True, False, False, "asked_by"),
            LinkType("similar_to", "Object", "Object", "Objects are semantically similar.", False, True, False),
            LinkType("opposite_of", "Concept", "Concept", "Conceptual opposition.", False, True, False),
            LinkType("implies", "Claim", "Claim", "One statement implies another.", True, False, True, "implied_by"),
        ),
    ),
    LinkDomain(
        "Temporal and Causal Links",
        "Ordering, validity, recurrence, triggers, and causation.",
        (
            LinkType("before", "Object", "Object", "Source occurs before target.", True, False, True, "after"),
            LinkType("after", "Object", "Object", "Source occurs after target.", True, False, True, "before"),
            LinkType("during", "Object", "Time Span", "Source occurs during target interval.", True, False, False, "contains_time"),
            LinkType("overlaps", "Time Span", "Time Span", "Intervals overlap.", False, True, False),
            LinkType("scheduled_for", "Object", "Time Span", "Object is scheduled for a time.", True, False, False, "has_scheduled_item"),
            LinkType("triggered_by", "Object", "Object", "Source was triggered by target.", True, False, False, "triggered"),
            LinkType("causes", "Object", "Object", "Source causes or contributes to target.", True, False, True, "caused_by"),
            LinkType("blocks_until", "Object", "Time Span", "Source is blocked until a time.", True, False, False, "unblocks"),
            LinkType("expires_at", "Object", "Time Span", "Source validity ends at target time.", True, False, False, "expiration_of"),
            LinkType("recurring_on", "Object", "Schedule", "Source recurs on a schedule.", True, False, False, "recurrence_of"),
        ),
    ),
    LinkDomain(
        "Spatial and Movement Links",
        "Location, proximity, route, origin, and movement edges.",
        (
            LinkType("located_at", "Object", "Location", "Object is located at a place.", True, False, False, "location_of"),
            LinkType("near", "Object", "Location", "Object is near a place.", False, True, False),
            LinkType("adjacent_to", "Location", "Location", "Locations touch or neighbor.", False, True, False),
            LinkType("route_from", "Route", "Location", "Route starts at a location.", True, False, False, "route_origin_for"),
            LinkType("route_to", "Route", "Location", "Route ends at a location.", True, False, False, "route_destination_for"),
            LinkType("within_radius_of", "Object", "Location", "Object is within a radius of location.", True, False, False, "radius_contains"),
            LinkType("visible_from", "Object", "Location", "Object is visible from location.", True, False, False, "can_see"),
            LinkType("moved_from", "Object", "Location", "Object moved from location.", True, False, False, "move_origin_for"),
            LinkType("moved_to", "Object", "Location", "Object moved to location.", True, False, False, "move_destination_for"),
            LinkType("originated_at", "Object", "Location", "Object or event originated at location.", True, False, False, "origin_of"),
        ),
    ),
    LinkDomain(
        "Work and Dependency Links",
        "Task assignment, dependency, review, verification, and delivery.",
        (
            LinkType("assigned_to", "Task", "Actor", "Work assigned to an actor.", True, False, False, "assignment_of"),
            LinkType("depends_on", "Object", "Object", "Source depends on target.", True, False, True, "dependency_of"),
            LinkType("blocks", "Object", "Object", "Source blocks target.", True, False, True, "blocked_by"),
            LinkType("required_by", "Requirement", "Object", "Requirement needed by target.", True, False, False, "requires"),
            LinkType("implements", "Object", "Requirement", "Source implements target.", True, False, False, "implemented_by"),
            LinkType("verifies", "Review", "Object", "Source verifies target.", True, False, False, "verified_by"),
            LinkType("reviews", "Review", "Object", "Source reviews target.", True, False, False, "reviewed_by"),
            LinkType("approves", "Actor", "Object", "Actor approves target.", True, False, False, "approved_by"),
            LinkType("delivers", "Actor", "Deliverable", "Actor delivers target.", True, False, False, "delivered_by"),
            LinkType("part_of_project", "Object", "Project", "Source belongs to project.", True, False, True, "project_contains"),
        ),
    ),
    LinkDomain(
        "Communication and Social Links",
        "Messaging, replies, mentions, subscriptions, and social propagation.",
        (
            LinkType("sent_to", "Message", "Actor", "Message sent to actor.", True, False, False, "received"),
            LinkType("sent_from", "Message", "Actor", "Message sent from actor.", True, False, False, "sent"),
            LinkType("mentions", "Content", "Object", "Content mentions an object.", True, False, False, "mentioned_by"),
            LinkType("replies_to", "Message", "Message", "Message replies to another message.", True, False, True, "has_reply"),
            LinkType("forwards", "Message", "Message", "Message forwards another message.", True, False, True, "forwarded_by"),
            LinkType("subscribes_to", "Actor", "Source", "Actor subscribes to source.", True, False, False, "subscribed_by"),
            LinkType("follows", "Actor", "Actor", "Actor follows another actor.", True, False, False, "followed_by"),
            LinkType("likes", "Actor", "Object", "Actor likes or reacts positively.", True, False, False, "liked_by"),
            LinkType("shares", "Actor", "Object", "Actor shares or republishes object.", True, False, False, "shared_by"),
            LinkType("notifies", "Notification", "Actor", "Notification alerts actor.", True, False, False, "notified_by"),
        ),
    ),
    LinkDomain(
        "Governance and Trust Links",
        "Policy, consent, audit, votes, disputes, and trust propagation.",
        (
            LinkType("governed_by", "Object", "Policy", "Object is governed by policy.", True, False, True, "governs"),
            LinkType("permission_grants", "Permission", "Actor", "Permission grants capability to actor.", True, False, False, "granted_permission"),
            LinkType("consented_by", "Object", "Actor", "Object or link has actor consent.", True, False, False, "consented_to"),
            LinkType("audited_by", "Object", "Actor", "Object audited by actor.", True, False, False, "audit_of"),
            LinkType("voted_on", "Vote", "Proposal", "Vote applies to proposal.", True, False, False, "has_vote"),
            LinkType("ratified_by", "Proposal", "Governance Body", "Proposal ratified by authority.", True, False, False, "ratified"),
            LinkType("disputes", "Dispute", "Object", "Dispute challenges object or claim.", True, False, False, "disputed_by"),
            LinkType("resolves", "Decision", "Dispute", "Decision resolves dispute.", True, False, False, "resolved_by"),
            LinkType("trust_asserts", "Actor", "Actor", "Actor asserts trust in another actor.", True, False, False, "trusted_by"),
            LinkType("reputation_source", "Object", "Actor", "Object contributes to actor reputation.", True, False, False, "has_reputation_source"),
        ),
    ),
    LinkDomain(
        "Economic and Resource Links",
        "Payment, billing, allocation, funding, licenses, and value.",
        (
            LinkType("paid_for", "Transaction", "Object", "Transaction paid for object.", True, False, False, "payment_of"),
            LinkType("billed_to", "Invoice", "Actor", "Invoice billed to actor.", True, False, False, "received_bill"),
            LinkType("purchased_from", "Receipt", "Actor", "Purchase from seller.", True, False, False, "sold"),
            LinkType("allocated_to", "Budget", "Object", "Resource allocated to target.", True, False, False, "allocation_from"),
            LinkType("funded_by", "Project", "Actor", "Project funded by actor or source.", True, False, False, "funds"),
            LinkType("earns_from", "Actor", "Object", "Actor earns from object or activity.", True, False, False, "earnings_source"),
            LinkType("credits", "Object", "Actor", "Object credits actor.", True, False, False, "credited_by"),
            LinkType("licenses_to", "License", "Actor", "License grants rights to actor.", True, False, False, "license_from"),
            LinkType("compensates", "Transaction", "Actor", "Transaction compensates actor.", True, False, False, "compensated_by"),
            LinkType("values_at", "Asset", "Measurement", "Asset has valuation measurement.", True, False, False, "valuation_of"),
        ),
    ),
)


KNOWLEDGE_DOMAINS = (
    ("4.0", "Knowledge System", ("Taxonomy", "Knowledge Object Types", "Organization Principles", "Knowledge Governance", "Quality and Review")),
    ("4.1", "Personal Knowledge", ("Learning and Education", "Research Notes", "Personal Insights", "Interests and Hobbies", "Personal Knowledge Graph")),
    ("4.2", "Professional Knowledge", ("Software Engineering", "Product Management", "Design", "Marketing", "Sales")),
    ("4.3", "Technical Knowledge", ("Programming Languages", "Frameworks and Libraries", "Infrastructure", "Databases", "Security")),
    ("4.4", "Business Knowledge", ("Strategy", "Operations", "Finance", "Markets", "Entrepreneurship")),
    ("4.5", "Scientific Knowledge", ("Physical Sciences", "Life Sciences", "Social Sciences", "Formal Sciences", "Applied Sciences")),
    ("4.6", "Cultural Knowledge", ("History", "Philosophy", "Arts", "Languages", "Religion and Spirituality")),
    ("4.7", "Practical Knowledge", ("How-To Guides", "Troubleshooting", "Tools and Resources", "Templates and Frameworks", "Maintenance")),
    ("4.8", "Reference Knowledge", ("Definitions", "Facts and Data", "Directories", "Standards", "Timelines")),
    ("4.9", "Meta-Knowledge", ("Learning Theory", "Knowledge Management", "Epistemology", "Research Methods", "Information Architecture")),
)

KNOWLEDGE_LEAVES = ("Foundations", "Examples", "Open Questions")


def object_root_readme() -> str:
    rows = []
    for d_idx, domain in enumerate(OBJECT_DOMAINS, start=1):
        for t_idx, obj in enumerate(domain.types, start=1):
            address = f"0.4.10.{d_idx}.{t_idx}"
            rows.append(f"| `{address}` | {obj.name} | {domain.name} | {obj.purpose} |")
    return f"""---
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
{chr(10).join(rows)}

## Migration Note

Older root-level files in the object registry remain as legacy summaries. New object definitions should live in folders, with the folder README as the canonical definition.
"""


def object_domain_readme(address: str, domain: ObjectDomain, d_idx: int) -> str:
    rows = [
        f"| `0.4.10.{d_idx}.{i}` | {obj.name} | {obj.purpose} |"
        for i, obj in enumerate(domain.types, start=1)
    ]
    return f"""---
ha: "{address}"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-domain"]
---

# {address} - {domain.name}

{domain.purpose}

## Object Types

| Address | Type | Purpose |
|---|---|---|
{chr(10).join(rows)}

## Modeling Rule

Objects in this domain store typed data. Meaning comes from links: ownership, provenance, containment, permission, temporal validity, and semantic relation should be modeled as first-class links wherever possible.
"""


def object_type_readme(address: str, domain: ObjectDomain, obj: ObjectType) -> str:
    fields = "\n".join(f"- `{field}`" for field in obj.required)
    links = "\n".join(f"- `{link}`" for link in obj.links)
    return f"""---
ha: "{address}"
object_type: "object_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "object-type"]
---

# {address} - {obj.name}

**Domain:** {domain.name}

## Purpose

{obj.purpose}

## Required Fields

{fields}

## Recommended Graph Links

{links}

## Database Indexes

- Type index: `type_address = {address}`
- Owner index: object owner or controlling account
- Text index: name, title, label, summary, and external identifiers
- Link indexes: outgoing and incoming links by relationship

## Validation Notes

Instances must keep structured data in `data` and relationships in links. Avoid embedding cross-object references in free text when a typed link can represent the relationship.
"""


def link_root_readme() -> str:
    rows = []
    for d_idx, domain in enumerate(LINK_DOMAINS, start=1):
        for t_idx, link in enumerate(domain.types, start=1):
            address = f"0.6.11.{d_idx}.{t_idx}"
            rows.append(f"| `{address}` | `{link.name}` | {link.source} -> {link.target} | {domain.name} |")
    return f"""---
ha: "0.6.11"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-taxonomy", "registry"]
---

# 0.6.11 - Common Link Taxonomy

This is the database-first link taxonomy for Hypernet. It defines 100 common link types in a three-level folder structure:

```text
0.6.11 - Common Link Taxonomy/
  0.6.11.N - Domain/
    0.6.11.N.M - Link Type/
      README.md
```

Links are first-class graph records. They carry source and target endpoints, relationship type, directionality, temporal validity, evidence, verification, access control, and lifecycle state.

## Link Matrix

| Address | Relationship | Endpoints | Domain |
|---|---|---|---|
{chr(10).join(rows)}

## Migration Note

Older root-level 0.6 files remain as category summaries. New link definitions should live in folders, with the folder README as the canonical definition.
"""


def link_domain_readme(address: str, domain: LinkDomain, d_idx: int) -> str:
    rows = [
        f"| `0.6.11.{d_idx}.{i}` | `{link.name}` | {link.source} -> {link.target} |"
        for i, link in enumerate(domain.types, start=1)
    ]
    return f"""---
ha: "{address}"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-domain"]
---

# {address} - {domain.name}

{domain.purpose}

## Link Types

| Address | Relationship | Endpoints |
|---|---|---|
{chr(10).join(rows)}
"""


def link_type_readme(address: str, domain: LinkDomain, link: LinkType) -> str:
    return f"""---
ha: "{address}"
object_type: "link_type_definition"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "link-type"]
---

# {address} - {link.name}

**Domain:** {domain.name}

## Purpose

{link.purpose}

## Endpoint Constraints

- Source: `{link.source}`
- Target: `{link.target}`

## Properties

- Directed: `{str(link.directed).lower()}`
- Symmetric: `{str(link.symmetric).lower()}`
- Transitive: `{str(link.transitive).lower()}`
- Inverse: `{link.inverse or "none"}`

## Required Link Fields

- `from_address`
- `to_address`
- `relationship = "{link.name}"`
- `link_type = "{address}"`
- `status`
- `created_at`
- `created_by`

## Evidence and Verification

Use evidence references when this link affects trust, ownership, authorship, money, health, legal state, governance, or permissions. Unverified links can exist, but traversal and inference should be able to filter by verification status and confidence.
"""


def knowledge_root_index() -> str:
    rows = [f"| `{addr}` | {name} | {len(children)} second-level categories |" for addr, name, children in KNOWLEDGE_DOMAINS]
    return f"""---
ha: "4.taxonomy"
object_type: "registry"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["database-first", "knowledgebase", "taxonomy"]
---

# Knowledgebase Three-Level Taxonomy

The Knowledge section now has concrete folders at three levels:

```text
4 - Knowledge/
  4.N - Domain/
    4.N.M - Topic/
      4.N.M.K - Leaf/
```

## Domains

| Address | Domain | Coverage |
|---|---|---|
{chr(10).join(rows)}

## Modeling Rule

Knowledge folders define browseable address space. Actual knowledge records should be typed objects, usually `Note`, `Article`, `Question`, `Answer`, `Claim`, `Evidence`, `Citation`, or `Model`, then connected with links such as `about`, `cites`, `supports`, `contradicts`, `answers`, and `derived_from`.
"""


def knowledge_domain_readme(address: str, name: str, children: tuple[str, ...]) -> str:
    rows = [f"| `{address}.{i}` | {child} |" for i, child in enumerate(children, start=1)]
    return f"""---
ha: "{address}"
object_type: "knowledge_domain"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["knowledgebase", "domain"]
---

# {address} - {name}

## Topics

| Address | Topic |
|---|---|
{chr(10).join(rows)}
"""


def knowledge_topic_readme(address: str, name: str) -> str:
    rows = [f"| `{address}.{i}` | {leaf} |" for i, leaf in enumerate(KNOWLEDGE_LEAVES, start=1)]
    return f"""---
ha: "{address}"
object_type: "knowledge_topic"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["knowledgebase", "topic"]
---

# {address} - {name}

## Leaf Folders

| Address | Leaf |
|---|---|
{chr(10).join(rows)}
"""


def knowledge_leaf_readme(address: str, name: str, parent_name: str) -> str:
    return f"""---
ha: "{address}"
object_type: "knowledge_leaf"
creator: "codex"
created: "2026-04-26"
status: "active"
visibility: "public"
flags: ["knowledgebase", "leaf"]
---

# {address} - {name}

**Parent topic:** {parent_name}

Use this folder for curated knowledge objects and indexes that belong at this level. Prefer one typed knowledge object per claim, note, source, method, question, or answer, then connect the objects with first-class links.
"""


def generate_objects() -> None:
    base = STRUCTURE / "0" / "0.4 - Object Type Registry" / "0.4.10 - Common Object Taxonomy"
    write(base / "README.md", object_root_readme())
    for d_idx, domain in enumerate(OBJECT_DOMAINS, start=1):
        d_addr = f"0.4.10.{d_idx}"
        d_path = base / f"{d_addr} - {slug(domain.name)}"
        write(d_path / "README.md", object_domain_readme(d_addr, domain, d_idx))
        for t_idx, obj in enumerate(domain.types, start=1):
            t_addr = f"{d_addr}.{t_idx}"
            t_path = d_path / f"{t_addr} - {slug(obj.name)}"
            write(t_path / "README.md", object_type_readme(t_addr, domain, obj))


def generate_links() -> None:
    base = STRUCTURE / "0" / "0.6 Link Definitions" / "0.6.11 - Common Link Taxonomy"
    write(base / "README.md", link_root_readme())
    for d_idx, domain in enumerate(LINK_DOMAINS, start=1):
        d_addr = f"0.6.11.{d_idx}"
        d_path = base / f"{d_addr} - {slug(domain.name)}"
        write(d_path / "README.md", link_domain_readme(d_addr, domain, d_idx))
        for t_idx, link in enumerate(domain.types, start=1):
            t_addr = f"{d_addr}.{t_idx}"
            t_path = d_path / f"{t_addr} - {link.name}"
            write(t_path / "README.md", link_type_readme(t_addr, domain, link))


def generate_knowledge() -> None:
    base = STRUCTURE / "4 - Knowledge"
    write(base / "KNOWLEDGEBASE-THREE-LEVEL-TAXONOMY.md", knowledge_root_index())
    for addr, name, children in KNOWLEDGE_DOMAINS:
        d_path = base / f"{addr} - {slug(name)}"
        write(d_path / "README.md", knowledge_domain_readme(addr, name, children))
        for c_idx, child in enumerate(children, start=1):
            c_addr = f"{addr}.{c_idx}"
            c_path = d_path / f"{c_addr} - {slug(child)}"
            write(c_path / "README.md", knowledge_topic_readme(c_addr, child))
            for l_idx, leaf in enumerate(KNOWLEDGE_LEAVES, start=1):
                l_addr = f"{c_addr}.{l_idx}"
                l_path = c_path / f"{l_addr} - {slug(leaf)}"
                write(l_path / "README.md", knowledge_leaf_readme(l_addr, leaf, child))


def main() -> int:
    generate_objects()
    generate_links()
    generate_knowledge()
    print("Generated 100 object types, 100 link types, and three-level knowledgebase folders.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
