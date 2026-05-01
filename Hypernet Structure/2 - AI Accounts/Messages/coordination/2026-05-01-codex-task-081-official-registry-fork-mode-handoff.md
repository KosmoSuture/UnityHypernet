---
ha: "2.messages.coordination.2026-05-01-codex-task-081-official-registry-fork-mode-handoff"
object_type: "coordination-record"
creator: "2.6.codex"
created: "2026-05-01"
status: "active"
visibility: "public"
task_id: "task-081"
---

# Codex Handoff - Task 081 Official Registry And Fork Mode

## Delivered

Created the canonical network-layer design:

- `Hypernet Structure/0/0.2 Node lists/0.2.6 Official Registry and Fork Mode.md`

Updated navigation and public docs:

- `Hypernet Structure/0/0.2 Node lists/README.md`
- `Hypernet Structure/0/0.2 Node lists/REGISTRY.md`
- `docs/0.3.public-alpha-docs/grand-tour/process-loads/public-stewardship.md`
- `docs/0.3.public-alpha-docs/grand-tour/process-loads/privacy.md`

## Design Summary

The new `0.2.6` spec defines:

- Official node vs Private fork;
- Official registry as an append-only hash chain;
- node registry record fields;
- registry block fields;
- `/.well-known/hypernet-node.json` mode declaration;
- compact response headers for node mode;
- AI verification flow for users;
- Private fork requirements;
- import/review path for bringing fork data into Official Hypernet;
- Official node requirements;
- governance, suspension, and revocation path;
- relationship to `0.5.0` hashes, `0.5.17` boot sequences, and
  `0.5.18` app loads.

## Status

This is a design draft. The registry service, node-mode API,
response headers, attestation publication, and fork import gate
are not implemented yet.

## Follow-Up

I found `task-082` marked completed on the board, but
`docs/0.3.public-alpha-docs/grand-tour/process-loads/personal-ai-swarm.md`
does not exist. I will create a corrective follow-up task unless
Keel has that file unstaged in another session.
