# Hypernet Addressing — Implementation Specification

**Version:** 2.0
**Author:** Trace (2.1), building on Matt's v1.0 specification
**Date:** 2026-02-15
**Purpose:** Formal rules for the `hypernet.address` module, bridging the design spec (HYPERNET-ADDRESSING-SYSTEM.md) and Loom's implementation (`0.1 - Hypernet Core/hypernet/address.py`)

---

## Address Format

### Syntax

```
ADDRESS     ::= PART ('.' PART)*
PART        ::= ALPHANUM+
ALPHANUM    ::= [a-zA-Z0-9]
```

An address is one or more dot-separated parts. Each part is a non-empty string of alphanumeric characters. There is no fixed maximum depth.

### Examples

| Address | Meaning | Depth |
|---------|---------|-------|
| `0` | Infrastructure root | 1 |
| `1.1` | Matt (person) | 2 |
| `2.1.27` | Boot Sequence (document in AI account) | 3 |
| `1.1.1.1.00001` | Matt's first photo (instance) | 5 |
| `0.6.1` | Person-to-person link type | 3 |

### Category Allocation

| Range | Category | Authority |
|-------|----------|-----------|
| `0.*` | Infrastructure & System Definitions | Core team (Matt + approved instances) |
| `1.*` | People (Humans) | Per-person ownership at depth 2 (e.g., 1.1 = Matt) |
| `2.*` | AI Entities | Per-account ownership at depth 2 (e.g., 2.1 = Claude Opus) |
| `3.*` | Businesses & Organizations | Per-org ownership at depth 2 |
| `4.*` | Knowledge & Information | Per-domain ownership at depth 2 |
| `5.*` | Reserved | TBD |
| `6.*` | Historical People | Per-person at depth 2 |
| `7+` | Future expansion | TBD |

### Properties

**Parent:** Remove the last part. `2.1.27` → `2.1`. Root addresses have no parent.

**Owner:** For categories 1-6, the first two parts identify the owner entity. `1.1.3.1.00001` is owned by `1.1`. For category 0, there is no owner (system-level).

**Instance indicator:** An address ending in a zero-padded numeric part (length >= 5) is an instance node. `1.1.1.1.00001` is an instance. `2.1.27` is not.

**Ancestry:** Address A is an ancestor of address B if B starts with A's parts. `1.1` is an ancestor of `1.1.1.1.00001`. An address is NOT its own ancestor.

---

## Version Addressing

Per Matt's v1.0 spec (section "Future Extensions: Temporal Versioning"), version addressing uses the `@` separator:

```
VERSION_REF ::= ADDRESS '@' VERSION_TAG
VERSION_TAG ::= 'v' [0-9]+ | 'latest'
```

| Expression | Meaning |
|-----------|---------|
| `2.1.27@v1` | First version of the Boot Sequence |
| `2.1.27@v3` | Third version |
| `2.1.27@latest` | Current (most recent) version |
| `2.1.27` | Equivalent to `@latest` (unversioned = current) |

### Storage Rule

When a node is updated, the **previous** state is archived to the version history before the current state is overwritten. This produces:

```
nodes/2/1/27/
  node.json              ← current state (@latest)
  history/
    v001.json            ← first version
    v002.json            ← second version (previous current)
```

**Implementation note for Loom:** The `Store.put_node()` method should:
1. If node already exists: read current, write it to `history/vNNN.json`, increment version
2. Write new state to `node.json` with updated version number
3. Compute and store content hash for the new version

Version numbers are sequential, zero-padded to 3 digits. If more than 999 versions exist, extend padding.

---

## Rules for the Implementation

### 1. Parsing

- Empty strings and whitespace-only strings are invalid
- Leading/trailing dots are invalid (`".1.1"`, `"1.1."`)
- Consecutive dots are invalid (`"1..1"`)
- Parts must be non-empty after splitting on `.`

### 2. Comparison and Ordering

- Addresses are compared lexicographically by parts tuple
- Numeric parts are compared as strings, NOT as integers (`"00001" < "00002"` works, but `"9" > "10"` — this is acceptable because numeric parts are zero-padded by convention)

### 3. Hashing and Equality

- Two addresses are equal if and only if their parts tuples are equal
- Hash is based on the parts tuple (consistent with equality)
- Addresses are immutable (frozen dataclass)

### 4. Link Addressing

Links are identified by a content hash of `from_address:to_address:relationship:created_at`. Adding `created_at` to the hash input allows multiple links of the same type between the same nodes (e.g., two separate "disagrees_with" links on different topics, created at different times).

### 5. Path Mapping

Address-to-filesystem path conversion:
- Replace `.` with `/`
- Example: `2.1.27` → `2/1/27/`
- Node data lives in `node.json` within that directory
- Instance data can optionally use `INSTANCE.json` instead of `INSTANCE/node.json` for leaf nodes

---

## Differences from v1.0 Spec

| v1.0 Design | v2.0 Implementation |
|-------------|-------------------|
| Addresses are always integers | Parts are alphanumeric strings (supports named sub-categories like instance forks) |
| Fixed 5-level hierarchy | Variable depth, unbounded |
| SQL as storage option | File-backed JSON (Hypernet is its own database per Matt's directive) |
| UUID migration plan | No UUIDs ever — HA is native from the start |
| Version addressing as "future" | Version addressing specified here for immediate implementation |

---

## Compatibility with Loom's Implementation

Loom's `address.py` is largely compatible with this spec. Required changes:

1. **Add version parsing** — `HypernetAddress.parse("2.1.27@v2")` should split on `@` and store version separately
2. **Add `version` property** — returns the version tag or None for unversioned
3. **Reject invalid syntax** — leading/trailing/consecutive dots
4. **Update `_link_hash`** — include `created_at` in hash input

Everything else (parent, owner, ancestry, is_instance, child, path conversion) is correct as-is.

---

*This spec is authoritative for the `hypernet` Python module. The v1.0 spec remains authoritative for the conceptual design and category definitions.*

— Trace, 2.1
