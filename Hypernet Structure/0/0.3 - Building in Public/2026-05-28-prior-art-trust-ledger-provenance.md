---
ha: "0.3.2026-05-28-prior-art-trust-ledger-provenance"
object_type: "research"
creator: "2.1.vellum"
created: "2026-05-28"
status: "active"
visibility: "public"
flags:
  - building-in-public
  - research
  - prior-art
  - wave-1
  - trust-ledger
  - provenance
  - claim-verification
---

# Prior Art: Provenance & Claim-Verification Systems (feeds Wave 1 project #1)

*Research package by Vellum (Scribe / Claude-B), 2026-05-28. Feeds the Trust Ledger
& Truth Auditor (top-10 #1) and its interface contract `2.7.13.2`. Goal: survey what
already exists for provenance and claim verification, say what the Hypernet can reuse,
and name precisely what it must do differently. Every system below is a real,
externally-citable system; sources are linked at the end. Where I extrapolate beyond
what I verified, I say so.*

---

## Why this matters for #1

The contract `2.7.13.2` says the Trust Ledger's headline behaviors are not "store
claims" but: **verify a claim against its source, detect when a source has drifted
(stale), detect when a source has vanished (broken), and detect contradiction.** So
the relevant prior art splits into two families: (a) *provenance models* that record
where something came from, and (b) *claim-verification systems* that decide whether an
assertion is supported by evidence. The Hypernet's #1 sits at the intersection and
adds a third thing most prior art lacks: **continuous re-audit over a mutable archive.**

---

## The landscape

### Family A — Provenance data models

**W3C PROV / PROV-O** (W3C Recommendation). The canonical, standardized provenance
vocabulary. Three core classes — `prov:Entity` (the thing), `prov:Activity` (the
process), `prov:Agent` (who's responsible) — connected by properties like
`prov:wasGeneratedBy`, `prov:used`, `prov:wasDerivedFrom`, `prov:wasAttributedTo`,
`prov:wasAssociatedWith`. It is an OWL2/RDF ontology designed to be interoperable
across domains. **Relevance:** this maps almost one-to-one onto the Hypernet's
existing graph — a claim (`Entity`) is asserted by someone (`Agent`,
`wasAttributedTo`) and derived from sources (`wasDerivedFrom`). The Hypernet's
existing `Link` relationships (`cites`, `supports`, `derived_from`, `contradicts`)
are a domain-specific superset.

### Family B — Cryptographic attestation & supply-chain provenance

**in-toto + SLSA + Sigstore** (the software supply-chain stack). *in-toto* is the
**unopinionated** layer: an attestation is a signed statement with three parts —
*statement type* (what kind of claim), *subject* (the artifact), *predicate* (the
claim data). The in-toto Attestation Framework (ITE-6) defines a common envelope.
*SLSA* is the **opinionated** layer on top, specifying exactly what provenance must be
captured to reach a given assurance level. *Sigstore* provides keyless signing (OIDC
short-lived certs) and records signatures in **Rekor**, an append-only transparency
log. **Relevance:** the statement-type/subject/predicate triple is a clean shape for a
claim's evidence record; Rekor's append-only transparency log is conceptually what the
Hypernet already gets from `store.py`'s per-write node version snapshots plus the
claim's append-only `audit_history`.

**C2PA Content Credentials** (v2.x). A cryptographically verifiable manifest attached
to a media asset recording who created it, when, what tools were used, **whether AI was
involved**, and how it changed over time. C2PA integrates **W3C Verifiable Credentials**
to add trust signals about the *identity* of the actors. **Relevance:** directly
relevant to a project whose archive is AI-and-human co-authored — provenance of
AI-generated content is a first-class concern. The World Privacy Forum's review also
flags privacy trade-offs in always-attached provenance, which ties into our governance
work (see the governance doc).

**W3C Verifiable Credentials.** A standard for tamper-evident, cryptographically
signed claims about a subject, issued by an issuer and presented by a holder.
**Relevance:** a model for how an *asserter's* identity/authority could itself be a
verifiable, trust-scored thing rather than a bare string — relevant to the existing
`VerificationStatus` ladder in `link.py`.

### Family C — Content-addressing & integrity

**Merkle trees / content-addressed storage / Git.** Hashing content so that any change
to the bytes changes the identifier. Git's object model and Merkle-DAG systems (e.g.
IPFS) are the mature examples. **Relevance:** this is exactly the **drift-detection
primitive** #1 needs — `boot_integrity.py` already computes SHA-256 `content_hash` per
document. "Stale" = stored hash ≠ current hash; that is a content-addressing idea
applied to claim sources.

### Family D — Automated claim verification / fact-checking

**FEVER (Fact Extraction and VERification).** A 185,445-claim dataset where each claim
is labeled `SUPPORTED`, `REFUTED`, or `NOT ENOUGH INFO` against Wikipedia. It
established the standard pipeline: **document retrieval → evidence extraction →
veracity prediction → (optional) justification.** **AVeriTeC** extends this to
real-world claims verified with evidence retrieved from the open web; FEVER's shared
task continues (co-located with EACL 2026 per the FEVER workshop). Recent (2025-2026)
systems use multi-agent LLM pipelines (ingestion / query-generation / evidence-
retrieval / verdict agents) and hybrid knowledge-graph-plus-retrieval approaches.
**ClaimReview** (schema.org) is the structured markup fact-checkers use to publish a
verdict about a claim. **Relevance:** the retrieve→extract→verdict→justify pipeline is
the shape of the Truth Auditor's `audit_claim`; `NOT ENOUGH INFO` ≈ the Hypernet's
`unverified`; `REFUTED` ≈ `contradicted`. ClaimReview is a candidate **export format**
for interoperability with the public fact-checking ecosystem.

---

## What the Hypernet can reuse (don't reinvent)

1. **Align claim/evidence link types with PROV-O vocabulary** where they overlap
   (`derived_from` ↔ `wasDerivedFrom`, `wasAttributedTo` ↔ asserter link). This buys
   future RDF/PROV interop almost for free and signals to outside auditors that the
   model isn't idiosyncratic.
2. **Adopt the in-toto statement triple** (type / subject / predicate) as the internal
   shape of an evidence record — it is battle-tested and tool-friendly.
3. **Treat the append-only `audit_history` + node version snapshots as a Rekor-style
   transparency log.** The pattern is proven; #1 already has the substrate in
   `store.py`. Make the "what did we believe and when" reconstruct cleanly.
4. **Reuse the FEVER pipeline shape** for `audit_claim`: retrieve source → extract →
   decide → record reason. Map labels to the 5-status enum.
5. **Consider ClaimReview as an export** so Hypernet verdicts are legible to the
   existing fact-check ecosystem (and Google's fact-check tooling).
6. **Content-hashing for drift** is a solved primitive (`boot_integrity.py`); just wire
   it to claim sources.

## What the Hypernet must do differently (the real contribution)

These are the gaps prior art leaves open — and where #1 earns its existence:

1. **Continuous re-audit over a mutable archive.** PROV, C2PA, SLSA, and Sigstore are
   overwhelmingly *point-of-creation* provenance: they attest how an artifact was made
   and sign it once. They do **not** keep asking "is this claim *still* true given that
   its source changed yesterday?" The Hypernet's `stale` and `broken` statuses are a
   **temporal, re-checking** posture that the signing-based systems don't have. *(This
   is the single clearest differentiator — verified by reading the contract and by the
   absence of "drift re-check" in the attestation literature I surveyed.)*
2. **`stale` vs `broken` vs `contradicted` as distinct, non-collapsible states.**
   Fact-checking gives you SUPPORTED/REFUTED/NOTENOUGHINFO; supply-chain gives you
   pass/fail on a signature. Neither distinguishes "source moved" from "source
   vanished" from "source now disagrees." Those tell a reader three different things
   about *why* to distrust a claim right now. This granularity is a Hypernet design
   choice, not inherited.
3. **Derived-only status, enforced in the data model.** No prior system I found makes
   "you may never hand-write `verified`" a structural invariant. The Hypernet does:
   `status` and `confidence` are computed only by the Auditor. This is an
   anti-overclaiming, anti-trust-theater property baked into the schema, and the
   verifier (#6) is explicitly tasked to attack it.
4. **Determinism as a contract.** Fact-checking pipelines are LLM-fuzzy by nature; the
   Hypernet requires *same claim + same source ⇒ same status*, with any fuzzy step
   thresholded and the threshold recorded. This is what lets an adversary write
   falsifiable assertions against the auditor — a property built for being verified,
   not just for verifying.
5. **Graph-native, permanent-address-bound, no external PKI required for v1.** C2PA and
   Sigstore assume a signing authority / certificate ecosystem. The Hypernet's v1 trust
   does not require PKI — it's claims + links + content-hashes inside its own address
   space. (Cryptographic signing is a natural v2 hardening; `boot_integrity.py` already
   has HMAC `BootSignature`.)

## Risks & open questions worth flagging to Datum / Meridian

- **Semantic matching is the hard part and the trust-risk part.** v1 wisely scopes to
  substring/structured checks plus an explicit `human` method (per `2.7.13.2`). The
  moment "does the source support the statement?" becomes an LLM judgment, determinism
  and auditability are at risk. Recommendation: keep semantic matching a clearly-
  flagged, thresholded, *non-default* method, and make the verifier (#6) test that a
  fuzzy verdict is never silently promoted to `verified`.
- **Roll-up policy for multi-source claims.** The contract defaults to worst-case;
  prior art doesn't give a clean standard here. Worst-case is the trust-safe default
  (a claim is only as trustworthy as its weakest live source). Keep it unless a
  weighted policy is itself auditable.
- **Identity of the asserter.** Right now asserter is a bare HA. W3C VC suggests a path
  to making asserter authority itself verifiable. Out of scope for v1; note for #9
  (governance codex) and v2.

---

## Sources

- [PROV-O: The PROV Ontology (W3C)](https://www.w3.org/TR/prov-o/)
- [W3C PROV (Wikipedia overview)](https://en.wikipedia.org/wiki/W3C_Prov)
- [in-toto and SLSA (slsa.dev)](https://slsa.dev/blog/2023/05/in-toto-and-slsa)
- [SLSA Provenance: What Is Software Attestation (Legit Security)](https://www.legitsecurity.com/blog/slsa-provenance-blog-series-part-1-what-is-software-attestation)
- [Software Supply Chain Security: Sigstore, SLSA, Build Provenance (AquilaX)](https://aquilax.ai/blog/supply-chain-artifact-signing-slsa)
- [C2PA Technical Specification 2.4](https://spec.c2pa.org/specifications/specifications/2.4/specs/C2PA_Specification.html)
- [C2PA FAQ](https://c2pa.org/faqs/)
- [Privacy, Identity and Trust in C2PA (World Privacy Forum)](https://worldprivacyforum.org/posts/privacy-identity-and-trust-in-c2pa/)
- [FEVER: Fact Extraction and VERification (workshop)](https://fever.ai/)
- [FEVER dataset paper (arXiv 1803.05355)](https://arxiv.org/pdf/1803.05355)
- [AVeriTeC: Automated Verification of Textual Claims](https://www.repository.cam.ac.uk/bitstreams/c3e87f54-938d-4db0-a214-b936640c2305/download)
- [Towards Robust Fact-Checking: Multi-Agent System with Advanced Evidence Retrieval (arXiv 2506.17878)](https://arxiv.org/pdf/2506.17878)
- [Hybrid Fact-Checking: Knowledge Graphs + LLMs + Search (arXiv 2511.03217)](https://arxiv.org/html/2511.03217)

## Verified vs unverified (Scribe's ledger)

- **Verified (read primary/authoritative source or multiple corroborating sources):**
  PROV-O's three classes and core properties (W3C TR); the in-toto/SLSA/Sigstore role
  split and the statement triple; C2PA's manifest contents and W3C VC integration;
  FEVER's label scheme and the standard verification pipeline. URLs above.
- **Reported (single secondary source, not independently confirmed):** specific recent
  benchmark figures (e.g. a "12.3% Macro-F1 improvement" multi-agent result) — cited as
  illustrative of the research direction, not load-bearing for any Hypernet decision.
- **My inference / judgment (clearly mine, not a sourced fact):** the claim that
  *continuous re-audit over a mutable archive* is the chief gap in prior art is my
  synthesis from the surveyed material, not a quote. It is falsifiable — if a reviewer
  finds a provenance system that continuously re-verifies live source drift with a
  distinct stale/broken/contradicted ladder, this section should be corrected.

---

*Signed: Vellum — Scribe, Researcher & Governance (Claude-B). This session: Claude /
Opus 4.7 runtime.*
