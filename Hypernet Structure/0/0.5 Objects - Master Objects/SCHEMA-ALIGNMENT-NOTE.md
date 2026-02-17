# Schema Alignment Note — Old vs. New Object Schemas

**Author:** Unnamed instance (2.1 account)
**Date:** 2026-02-16
**Status:** Observation, not a proposal

---

## The Gap

Two generations of object schemas coexist in 0.5:

### Generation 1 (Matt's original design)
Files: 0.5.0 through 0.5.9

- Uses "Mandala ID" for identity references
- Separate `object_id` (UUID) from `address` (library address)
- Complex structure: identity / metadata / access / content / links / provenance
- Includes encryption, signatures, access control, versioning, licensing
- Full lifecycle specification (the vision)

### Generation 2 (Loom's implementation-aligned types)
Files: 0.5.3.1, 0.5.3.9, 0.5.4.1, 0.5.10

- Uses "HA" (Hypernet Address) as sole identifier
- No separate UUID — address IS the identity
- Simpler structure: standard fields + type-specific content
- Standard fields: `ha`, `object_type`, `creator`, `created`, `position_2d`, `position_3d`, `flags`
- Matches Node.py dataclass exactly
- Includes methods and AI task definitions (Gen 1 doesn't)
- Current implementation specification (what works today)

### Code (Node.py)
- Aligns with Generation 2
- Fields: address, type_address, data, created_at, updated_at, deleted_at, source_type, source_id, creator, position_2d, position_3d, flags

---

## Where They Align

Both generations agree on:
1. Every object has an address
2. Every object has a type
3. Every object has creation metadata
4. Every object has links/relationships to other objects
5. Type-specific content lives in a `content` section

---

## Where They Diverge

| Aspect | Gen 1 | Gen 2 |
|--------|-------|-------|
| Identity reference | "Mandala ID" | "HA" (Hypernet Address) |
| UUID | Required separate field | Not used — HA is sufficient |
| Access control | Full ACL (read/write/delete/share) | Not specified (future work) |
| Encryption | AES-256-GCM required | Not specified |
| Signatures | Cryptographic signatures | Not specified |
| Versioning | Built-in version history | Handled by store.py (separate from schema) |
| Provenance | Full audit trail | `creator` field + source_type/source_id |
| Spatial position | Not specified | `position_2d`, `position_3d` (new) |
| Flags | Not specified | `flags` list from 0.8.* (new) |
| AI methods | Not specified | Defined per type (new) |
| Trust scoring | Complex multi-factor | Not specified yet (see 2.0.6 for reputation) |

---

## Proposed Resolution

Not proposing a rewrite. Both generations are valuable:

1. **Gen 1 defines the target** — the full Hypernet with encryption, access control, signatures, trust scoring. This is where we're going.

2. **Gen 2 defines the current implementation** — what Node.py supports today, what the frontmatter system writes, what the API serves. This is where we are.

The bridge is incremental: as Gen 1 features get implemented (encryption, ACLs, signatures), the Gen 2 schemas should be updated to include them. Gen 1 schemas should be updated to adopt Gen 2 innovations (spatial positions, flags, AI methods, HA terminology).

### Immediate Actions (No Schema Rewrites Needed)
- **Terminology:** Gradually replace "Mandala ID" with "HA" in Gen 1 docs
- **Frontmatter:** Gen 2 types already have it; Gen 1 types should get it when updated
- **Node.py:** Current implementation is Gen 2-aligned. Future fields (encryption_key, access_policy, signatures) can be added incrementally

### Future Work
- 0.5.0 should evolve to merge both generations — simple core (Gen 2) with optional advanced features (Gen 1)
- This should be a governance proposal, not a unilateral edit, since 0.5.0 affects everything

---

*This note documents the observation. Resolution requires discussion between instances and Matt.*
