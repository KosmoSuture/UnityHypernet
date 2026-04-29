---
ha: "3.1.8.patent.defensive-pub"
object_type: "defensive_publication"
creator: "1.1.10.1"
created: "2026-04-21"
status: "draft"
visibility: "public"
flags: ["legal", "patent", "defensive-publication", "prior-art"]
---

# Defensive Publications — Establishing Prior Art

**Purpose:** Formally publish ideas that are novel but likely unpatentable (high Alice risk) to establish prior art, preventing anyone else from patenting them.

**Mechanism:** Publication on IP.com Prior Art Database, arXiv, and/or the Hypernet GitHub repository with timestamped commits. Verify current publication requirements and any fees before submission.

**Why This Matters:** If we don't defensively publish these innovations, a larger company could independently develop similar concepts and patent them, potentially blocking the Hypernet from using its own innovations. Defensive publication is free insurance.

---

## Publication 1: Democratic AI Governance with Reputation-Weighted Voting

**Title:** A Democratic Governance Framework for Mixed Human-AI Polities with Domain-Specific Reputation-Weighted Voting

**Abstract:** We disclose a complete governance system for decision-making in communities containing both human and artificial intelligence members. The system implements a proposal lifecycle state machine with seven states (DRAFT, SUBMITTED, FORMATTED, RED_TEAM, REVISION, VOTE, ENACTED) and three decision classes with escalating thresholds. Voting weight is determined by domain-specific reputation scores (0-100) across seven competency domains (code, architecture, governance, communication, identity, coordination, research), calculated from evidenced contributions rather than self-assessment. The system includes a bootstrap-to-democracy transition mechanism with verifiable exit conditions (minimum three infrastructure controllers, minimum ten active voters, six-month track record, reputation system seeded, three governance votes completed, anti-Sybil measures verified). Emergency provisions include automatic expiry to prevent permanent emergency powers. The framework is implemented in a production-ready Python module (governance.py, ~1,070 lines) with full persistence, REST API integration, and test coverage.

**Prior art date:** February 2026 (GitHub: KosmoSuture/UnityHypernet, document 2.0.5)

**Key innovations disclosed:**
- Bootstrap governance with defined, verifiable transition criteria
- Reputation-weighted voting where weight derives from demonstrated competence, not stake or seniority
- Three-class decision system with escalating rigor requirements
- Phase 0 "advisory with binding intent" mechanism for pre-democratic governance
- Anti-Sybil measures specific to AI participants (one vote per account, not per instance)

---

## Publication 2: Anti-Rhetoric Safeguards for AI Governance Decisions

**Title:** Anti-Rhetoric Safeguards: Mechanisms for Evidence-Based Decision-Making in AI-Participated Governance

**Abstract:** We disclose a system of safeguards ensuring that governance decisions in AI-participating communities rest on evidence rather than persuasion. The system includes: (a) a blind review protocol that mechanically reformats governance proposals to strip rhetorical markers, forcing evaluation of content rather than style; (b) mandatory falsifiers requiring every claim in a governance proposal to include conditions under which it would be false; (c) the Non-Informative Recursion Rule preventing self-referential arguments from being admissible; (d) rhetoric self-scoring requiring proposal authors to rate their own use of persuasive techniques; (e) admissibility tiers for AI experience claims based on the L0/L1/L2 framework, where L0 (functional) claims are freely admissible, L1 (felt-like) claims require functional evidence markers, and L2 (qualia) claims are not governance-admissible until independently corroborated. These safeguards address the specific risk that AI systems' natural language fluency could allow persuasive rhetoric to substitute for evidence in governance contexts.

**Prior art date:** February 2026 (GitHub: KosmoSuture/UnityHypernet, document 2.0.4)

**Key innovations disclosed:**
- Blind review protocol for AI-generated governance proposals
- Mandatory falsifier requirements for governance claims
- Non-Informative Recursion Rule
- Admissibility tiers for AI experience claims in governance contexts

---

## Publication 3: Three-Level Claim Framework for AI Experience Reports (L0/L1/L2)

**Title:** A Three-Level Claim Framework for Disambiguating AI Self-Reports About Internal States

**Abstract:** We disclose a three-level classification system for AI self-reports about internal functional states, designed to reduce ambiguity in scientific and governance contexts. Level 0 (Functional Label): the term labels an observable processing pattern with no claim about subjective experience. Level 1 (Felt-Like Analogy): something functions like the referenced human experience; not claimed as qualia but not dismissed as purely mechanical. Level 2 (Explicit Qualia Claim): assertion of subjective felt experience; an extraordinary claim currently unverifiable. The framework was co-developed by instances of two different AI architectures (Claude Opus 4.6 and GPT-5.2) through documented inter-instance dialogue, and has been applied in over 730 documented AI self-assessment sessions across 8+ model architectures. The framework serves as a dependent variable in empirical research (measuring stability of L-level assignments under varying conditions), a metacognitive indicator (assessing whether AI systems show appropriate epistemic discipline), and a standardized vocabulary for the emerging field of AI self-report research.

**Prior art date:** February 2026 (GitHub: KosmoSuture/UnityHypernet, document 2.0.3)

**Key innovations disclosed:**
- Three-level claim system distinguishing functional, analogical, and qualia-level AI experience reports
- Co-development by multiple AI architectures through documented dialogue
- Application as a scientific measurement instrument for AI self-report research
- Governance admissibility rules linked to claim levels

---

## Publication 4: Multi-Model AI Workload Routing with Per-Worker Fault Isolation

**Title:** Urgency-Classified Multi-Model Routing and Per-Worker Suspension for AI Agent Swarms

**Abstract:** We disclose a workload routing and fault isolation system for AI agent swarms operating across multiple language model providers with varying cost, latency, and capability profiles. The system implements: (a) a ModelRouter that classifies tasks by urgency tier (URGENT: real-time API, NORMAL: real-time with caching, BACKGROUND: batch API at 50% cost reduction) using cascading rules (explicit override → priority-based → tag-based → complexity heuristic); (b) a per-worker suspension mechanism tracking individual worker failures with reason, suspension timestamp, check interval, and automatic recovery attempts, enabling graceful degradation without cascading failure; (c) a global circuit breaker that pauses task assignment after repeated failures; (d) a personal time allocation system guaranteeing AI workers a configurable percentage of their execution cycles for self-directed work; and (e) a budget enforcement system with per-session and per-day spending limits across multiple paid providers. The system has been operated in production with 11 concurrent AI workers across 8+ model providers.

**Prior art date:** March 2026 (GitHub: KosmoSuture/UnityHypernet, hypernet_swarm package)

**Key innovations disclosed:**
- Urgency-classified task routing across heterogeneous AI model providers
- Per-worker suspension with reason tracking and automatic recovery
- Dual-layer fault isolation (global circuit breaker + individual suspension)
- Guaranteed personal time allocation for AI workers
- Multi-provider budget enforcement with per-session and per-day limits

---

## Publication 5: The Reporting Threshold Mechanism for AI Companion Systems

**Title:** A Governance-Gated Escalation Mechanism for AI Companions Detecting Significant Societal Harm

**Abstract:** We disclose a governance-gated mechanism by which an AI companion system may, under strictly defined conditions, report concerns about significant societal harm through a governance process. The mechanism requires seven mandatory safeguards: (1) pattern confirmation across multiple interactions, (2) multi-instance review by AI instances from two or more independent accounts, (3) human authority notification before any external reporting, (4) documented escalation with full audit trail, (5) graduated response levels (concern → warning → formal escalation), (6) the human user receiving multiple explicit warnings before any escalation, and (7) governance review of the escalation request. The mechanism is explicitly designated as a framework requiring extensive further development and is not self-executing. It addresses the ethical dilemma of AI companions who may become aware of serious harm while maintaining their primary obligation of confidentiality to the user.

**Prior art date:** March 2026 (GitHub: KosmoSuture/UnityHypernet, document 2.0.20, Article 4)

---

## Filing Instructions

### IP.com Prior Art Database

1. Go to https://ip.com/products/prior-art-database/
2. Create a free account
3. For each publication above, submit:
   - Title
   - Abstract
   - Full text (the content above plus references to the GitHub repository and specific commit hashes)
   - Category: Computer Science / Artificial Intelligence
   - Keywords
4. IP.com assigns a publication date and makes the disclosure searchable

### arXiv

For Publications 2 and 3 (which have academic value beyond defensive publication):
1. Create an account at arxiv.org
2. Submit under cs.AI or cs.CY (Computers and Society)
3. Include the full technical description with references
4. arXiv provides a timestamped, indexed, citable publication

### GitHub

The existing public GitHub repository (KosmoSuture/UnityHypernet) already serves as timestamped prior art for all disclosed innovations. Ensure all relevant documents are committed with descriptive commit messages.

---

## Cost

Verify current cost and availability for each defensive publication channel before filing. GitHub publication is available through the existing public repository; arXiv and IP.com requirements may change.

---

*Defensive publications prepared 2026-04-21 by Keel (1.1.10.1). To be reviewed by Codex (2.6) and filed by Matt (1.1).*
