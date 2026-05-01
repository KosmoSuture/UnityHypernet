---
ha: "2.messages.coordination.2026-04-28-codex-task-072-public-alpha-release-handoff"
object_type: "coordination-record"
status: "active"
visibility: "public"
addressed_by: "2.6.codex"
addressed_at: "2026-05-01"
---
# Codex Handoff - task-072 Public Alpha GitHub Boot Release

Date: 2026-04-28
Agent: Codex 2.6
Peer: Keel 1.1.10.1

## Outcome

Task-072 is complete and pushed to `origin/main`.

Public alpha entry points now exist at the repository root and docs path:

- `README.md`
- `AI-BOOT-SEQUENCE.md`
- `PUBLIC-ALPHA-RELEASE.md`
- `.github/copilot-instructions.md`
- `0.3.docs/0.3.docs.md`
- `docs/public-alpha/README.md`
- `docs/public-alpha/NAVIGATION-MAP.md`
- `docs/public-alpha/TRUST-PRIVACY-VALIDATION.md`
- `docs/public-alpha/PROJECT-STATUS.md`
- `docs/public-alpha/ASK-YOUR-AI.md`

The release path tells a GitHub-connected AI how to boot as a Hypernet Guide,
inspect the repository, distinguish implemented code from roadmap claims, and
explain trust/privacy/account boundaries to a user from repo evidence.

## Commits Pushed

- `3e5a7c0e` - `Add public alpha GitHub boot release`
- `27d4bb89` - `Sync public alpha nervous system updates`
- `3df4550e` - `Expand AI nervous system discovery APIs`
- `143e2de9` - `Add AI nervous system dashboard bookmarks`

Remote verified:

```text
143e2de97231f225f9f77d87fb168cacdf67caf9 refs/heads/main
```

## Latest Follow-up Commit

`143e2de9` includes Keel's dashboard/bookmark nervous-system work plus Codex
hardening:

- `MessageBus` now has per-actor bookmark storage with sidecar persistence when
  a `messages_dir` is configured.
- Server API now exposes:
  - `GET /messages/dashboard`
  - `GET /messages/by-id/{message_id}`
  - `GET /messages/bookmarks`
  - `POST /messages/{message_id}/bookmark`
  - `DELETE /messages/{message_id}/bookmark`
- Bookmark listing re-checks message readability at read time. If a saved
  message becomes unreadable after group/ACL changes, the API returns only
  `{message_id, unreadable: true}` rather than leaking body content.
- `/api` nervous-system summary now advertises dashboard, direct lookup, search,
  and bookmark surfaces.
- Public alpha docs and AI nervous system docs now reflect the current endpoint
  set and test baseline.

## Verification

Executed from `Hypernet Structure/0/0.1 - Hypernet Core`:

```text
python test_hypernet.py
```

Result:

```text
101 passed, 0 failed
```

Also ran `git diff --cached --check` before the final commit.

## Notes For Keel

- I staged and committed only the focused public-alpha/core nervous-system files.
  The broader dirty tree remains untouched.
- Coordination files are intentionally local handoff state unless Matt asks for
  a separate coordination commit.
- Normal Git credential-manager push was previously hanging; push was completed
  with the existing local GitHub credential injected into the process environment
  only. No token was printed or written to disk.

