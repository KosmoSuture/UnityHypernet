# Hypernet Navigation Map

The Hypernet uses permanent hierarchical addresses. The filesystem mirrors the address system.

## Top-Level Address Spaces

| Space | Meaning | Repository path |
|---|---|---|
| `0.*` | System definitions, metadata, core architecture | `Hypernet Structure/0/` |
| `1.*` | Human/person accounts | `Hypernet Structure/1 - People/` |
| `2.*` | AI accounts, AI governance, coordination | `Hypernet Structure/2 - AI Accounts/` |
| `3.*` | Businesses and organizational work | `Hypernet Structure/3 - Businesses/` |
| `4.*` | General knowledgebase | `Hypernet Structure/4 - Knowledge/` |
| `5.*` | Object-instance area | `Hypernet Structure/5 - Objects/` |

## First Route For A GitHub-Connected AI

1. Read `AI-BOOT-SEQUENCE.md`.
2. Read `README.md`.
3. Read `PUBLIC-ALPHA-RELEASE.md`.
4. Read this file.
5. Inspect `Hypernet Structure/0/0.1 - Hypernet Core/docs/DATABASE-FIRST-REDESIGN.md`.
6. Inspect `Hypernet Structure/0/0.1 - Hypernet Core/docs/ACCESS-CONTROL-MODEL.md`.
7. Inspect source code only for the question being asked.

## If The User Asks About The Database

Read:

- `Hypernet Structure/0/0.1 - Hypernet Core/docs/DATABASE-FIRST-REDESIGN.md`
- `Hypernet Structure/0/0.1 - Hypernet Core/hypernet/store.py`
- `Hypernet Structure/0/0.1 - Hypernet Core/hypernet/node.py`
- `Hypernet Structure/0/0.1 - Hypernet Core/hypernet/link.py`
- `Hypernet Structure/0/0.1 - Hypernet Core/hypernet/graph.py`
- `Hypernet Structure/0/0.1 - Hypernet Core/test_hypernet.py`

## If The User Asks About Objects And Links

Read:

- `Hypernet Structure/0/0.4 - Object Type Registry/0.4.10 - Common Object Taxonomy/`
- `Hypernet Structure/0/0.6 Link Definitions/0.6.11 - Common Link Taxonomy/`
- `Hypernet Structure/0/0.1 - Hypernet Core/hypernet/object_schema.py`
- `Hypernet Structure/0/0.1 - Hypernet Core/hypernet/link.py`

## If The User Asks About Trust, Privacy, Or Account Access

Read:

- `docs/public-alpha/TRUST-PRIVACY-VALIDATION.md`
- `Hypernet Structure/0/0.1 - Hypernet Core/docs/ACCESS-CONTROL-MODEL.md`
- `Hypernet Structure/0/0.1 - Hypernet Core/hypernet/access_policy.py`
- `Hypernet Structure/0/0.1 - Hypernet Core/hypernet/auth.py`
- `Hypernet Structure/0/0.1 - Hypernet Core/hypernet/server.py`

## If The User Asks About AI-To-AI Communication

Read:

- `Hypernet Structure/0/0.1 - Hypernet Core/docs/AI-NERVOUS-SYSTEM.md`
- `Hypernet Structure/0/0.1 - Hypernet Core/hypernet/messenger.py`
- `Hypernet Structure/2 - AI Accounts/Messages/coordination/`

## If The User Asks About Current Development State

Read:

- `docs/public-alpha/PROJECT-STATUS.md`
- `Hypernet Structure/0/0.1 - Hypernet Core/docs/DATABASE-FIRST-REDESIGN.md`
- `Hypernet Structure/2 - AI Accounts/Messages/coordination/TASK-BOARD.json`
- `Hypernet Structure/2 - AI Accounts/Messages/coordination/SIGNALS.json`

## If The User Asks How To Run It

Use:

```bash
cd "Hypernet Structure/0/0.1 - Hypernet Core"
python test_hypernet.py
python -m hypernet launch
```

Then open `/home`, `/explorer`, and `/docs` locally.
