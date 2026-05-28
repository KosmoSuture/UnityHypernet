---
ha: "1.1.10.shared.readme"
object_type: "stub"
created: "2026-05-08"
status: "relocated"
visibility: "public"
flags: ["privacy-wall-stub"]
---

# Shared Context — Moved to Private

The contents of `1.1.10/shared-context/` (family.md, priorities.md) have been
moved to `1.1.private/embassy/shared-context/` per the 2026-05-08 privacy-wall
remediation.

**Why:** These files contained personal family details, children's first
names, mother's full name, and Matt's internal priorities — information
appropriate for the embassy AI to read locally but not appropriate for the
public archive.

**Where it went:** `Hypernet Structure/1 - People/1.1 Matt Schaeffer/private/embassy/shared-context/`

That path is gitignored under the `**/private/` pattern in root `.gitignore`.

**For the booted companion AI:** if you have local read access to
`1.1.private/`, read shared-context from there. Otherwise, you don't have
access to this content and should not attempt to reconstruct it from public
sources.

**Governance:** see `1.0.2-PRIVATE-DATA-NAMESPACE.md` for the `*.private`
namespace pattern, and the privacy-wall standard for `1.*` accounts at
`1.0.3-PRIVACY-WALL-STANDARD.md` (created as part of this remediation).

— Keel (1.1.10.1) per Matt directive 2026-05-08
