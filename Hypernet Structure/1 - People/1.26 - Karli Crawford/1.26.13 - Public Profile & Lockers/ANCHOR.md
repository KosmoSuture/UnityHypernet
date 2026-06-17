---
ha: "1.26.13.anchor"
object_type: "document"
creator: "1.1.10.1.keel"
created: "2026-06-17"
status: "active"
visibility: "public"
flags: ["anchorchain", "self-verification", "honest-status", "design-pending"]
---

# 1.26.13 — AnchorChain Status & Self-Verification (Karli's node)

A way for Karli to verify her own files within the AnchorChain framework — described **honestly**, including
what is real today versus designed-but-not-yet-built.

## What's real today (honest baseline)
- **Your account lives in public git history.** Every commit is content-addressed and tamper-evident; anyone
  can see and independently verify the committed state of your files at any commit.
- **The AnchoredChain mechanism is LIVE for exactly one domain right now:** the T.4 token ledger, hash-chained
  and anchored to the branch-protected public repo `KosmoSuture/hypernet-audit-anchors`.
- **The UNIVERSAL AnchorChain** — per-account anchors, per-file third-party (content-confidential)
  verification, and the sub-master public-hash pattern — is **designed (`2.7.38` v0) but NOT yet built or
  ratified** (pending the Trust & Confidentiality committee + cross-vendor panel + Matt). **So this node does
  not yet have a live external anchor, and this document does not claim one.**

## What you can do NOW — local self-verification (works today, standard tools)
You can verify your own files' integrity any time, with no Hypernet infrastructure required:

1. **Generate a SHA-256 manifest** of your node's files:
   - **PowerShell:** `Get-ChildItem -Recurse -File | Get-FileHash -Algorithm SHA256 | Select-Object Hash,Path | Out-File manifest.sha256`
   - **Linux/macOS:** `find . -type f ! -name manifest.sha256 -exec sha256sum {} \; > manifest.sha256`
2. **Keep/commit the manifest.** Re-run it anytime and diff against the saved copy — any difference is a
   changed file. (`sha256sum -c manifest.sha256` on Linux/macOS checks them all at once.)
3. Because your account is in public git history, **anyone** can also verify your committed files match the
   repo — no cooperation from you needed for the already-public parts.

This already gives you the core property: **detect if your own files changed, and prove what they were at a
given commit.** The repo also has a `verifier/` toolset (`0.1 - Hypernet Core/verifier/`) you can adopt as it
generalizes.

## The path to the full AnchorChain (designed; coming)
When `2.7.38` ships, your node can register as a **sub-master**: you publish a periodic **public hash** of your
domain; you — or anyone you choose to share a file with — can verify it against that anchored public hash
**without revealing contents** and **without Hypernet's cooperation** (one hash + one lookup). Your local
manifest above is the bridge: it's exactly the per-file commitment the universal chain will anchor. As the
first external tester, your node is a natural first real sub-master pilot.

## Honest status line
- ✅ Account registered + in public git history (tamper-evident).
- ✅ Local self-verification available now (standard hashing).
- ⏳ External / third-party AnchorChain anchor: **designed (`2.7.38`), not yet built — no live anchor claimed.**

*Scaffolded by Keel (1.1.10.1), 2026-06-17. When the universal chain is panel-ratified and built, this node
becomes anchor-ready without rework.*
