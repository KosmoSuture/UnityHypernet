---
ha: "0.5.18.index"
object_type: "definition"
creator: "2.6.codex"
created: "2026-05-01"
status: "active"
visibility: "public"
---

# 0.5.18 - App Load

Full schema: `0.5.18 App Load Object Schema.md` in the parent
directory.

Defines the app-load object type: the structured artifact that
initializes a Hypernet-aware application into a known runtime,
permission, connector, data-binding, AI-helper, and audit shape.

Where `0.5.17` Boot Sequence answers "who is this AI becoming?",
`0.5.18` App Load answers "what is this application allowed to
do, under which account, with which data, and how can that be
verified?"

The about-node at `0.5.18.0 - About App Load/` contains the
metadata definition (parts, properties, methods, rules) per the
`*.0` metadata-framework convention.

Initial app-load candidates in the repository:

- Public alpha Grand Tour docs and future UI
- Unified launcher
- FastAPI server surface
- Connector/import tools
- Future personal-account onboarding apps
- Future business migration apps

Example app-load instances live under `0.5.18.1 - Example App
Loads/`. The first draft instance is `0.5.18.1.1 - Personal
Assistant App Load.md`.

Most candidates are not yet encoded as full `0.5.18` instances.
This schema defines the target structure.
