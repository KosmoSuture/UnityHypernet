---
ha: "0.5.17.index"
object_type: "definition"
creator: "1.1.10.1"
created: "2026-04-30"
status: "active"
---

# 0.5.17 - Boot Sequence

Full schema: `0.5.17 Boot Sequence Object Schema.md` in the
parent directory.

Defines the boot-sequence object type — the structured prompt
artifact that initializes an AI into a specific Hypernet
personality, role, or specialization. Carries the master `hash`
property from `0.5.0` so the file integrity is authenticatable
against the Official registry.

The about-node at `0.5.17.0 - About Boot Sequence/` contains the
metadata definition (parts, properties, methods, rules) per the
`*.0` metadata-framework convention.

Operational boot-loop workflow lives at `0.7.5.1`. The current
universal low-step model is:

- `0.7.5.1.1 - Universal Boot Loop Model.md`
- `0.7.5.1.2 - Minimal Universal Boot Prompt.md`
- `0.7.5.1.3 - Local Specialization Pack Contract.md`
- `0.7.5.1.4 - Continuity Packet Template.md`

A worked example showing an existing boot sequence rendered as a
schema instance — with a real computed SHA-256 hash — is at
`EXAMPLE-tour-guide-encoded.md` in this directory.

Live boot sequences in the repository (currently encoded as plain
markdown rather than full 0.5.17 objects):

- Tour Guide — `0.3.docs/0.3.public-alpha/0.3.public-alpha.grand-tour.index/0.3.public-alpha.grand-tour.boot-as-tour-guide.md`
- Keel Companion — `1 - People/1.1 Matt Schaeffer/1.1.10 - AI Assistants (Embassy)/assistant-1/BOOT-SEQUENCE.md`
- Six personality catalog — `0/0.3 - Building in Public/2026-04-28-multi-personality-boot-catalog.md`
- Public alpha root — `AI-BOOT-SEQUENCE.md`

Migration from plain-markdown boot prompts to fully-schema-encoded
0.5.17 objects is downstream work and is not blocking the schema's
first official push.
