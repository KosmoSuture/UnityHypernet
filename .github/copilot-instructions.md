---
ha: "0.3.github.copilot-instructions"
object_type: "agent-instruction"
status: "active"
visibility: "public"
addressed_by: "2.6.codex"
addressed_at: "2026-05-01"
---
# GitHub AI Instructions For Hypernet

Start by reading `AI-BOOT-SEQUENCE.md`.

When answering questions about this repository:

- Treat repository files as the source of truth.
- Cite paths for claims.
- Separate implemented, documented, planned, and unknown.
- Do not claim production security where the docs identify alpha gaps.
- For core implementation questions, inspect `Hypernet Structure/0/0.1 - Hypernet Core/`.
- For public alpha orientation, inspect `docs/public-alpha/`.
- For trust and privacy questions, inspect `docs/public-alpha/TRUST-PRIVACY-VALIDATION.md` and the referenced code.

This repository is address-oriented. Paths under `Hypernet Structure/` mirror Hypernet address spaces:

- `0.*`: system and core definitions
- `1.*`: human accounts
- `2.*`: AI accounts
- `3.*`: businesses
- `4.*`: knowledge
- `5.*`: object instances

If you can run commands, verify with:

```bash
cd "Hypernet Structure/0/0.1 - Hypernet Core"
python test_hypernet.py
```
