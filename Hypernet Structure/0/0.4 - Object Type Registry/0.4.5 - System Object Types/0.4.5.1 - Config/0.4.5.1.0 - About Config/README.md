---
ha: "0.4.5.1.0"
object_type: "definition"
creator: "2.1.librarian"
created: "2026-03-19"
status: "active"
---

# 0.4.5.1.0 - About Config

A Config object stores configuration settings for a system component. Configs control runtime behavior of the server, swarm, connectors, and other infrastructure.

## Security

Config objects may contain sensitive values (API keys, tokens, credentials). These are stored in the `secrets/` directory, excluded from version control, and encrypted at rest. The public config schema is documented; the values are protected.
