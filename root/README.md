# Hypernet Root of Trust — Genesis

This directory holds the **non-AI-writable root of trust** for Hypernet (design: `2.7.40`).

## The genesis root key
- **Holder:** Matt Schaeffer (1.1), founder. The **private** key is held by Matt **offline**. **No AI can
  create, read, or forge it.** This is the one trust fact in the whole system that originates outside the AI.
- **Public key:** `minisign.pub` — key ID `3BD1F8C8572EF8E8`:
  `RWTo+C5XyPjRO92KpS1rN04k5ZpcSLm8optrpoulomMP/5EW3ywYVV+d`
- Generated offline by Matt on 2026-06-20 with minisign (Ed25519); committed here by Keel at Matt's direction.

## What it's for
Root-level trust facts (ownership, authority designations, anchor heads — per `2.7.40`) are valid **only**
when signed by this key, or by a delegation chain terminating at it. AI may *propose* such facts; only Matt's
offline signature makes them real. The system **verifies** signatures; it **cannot create** them.

## How to verify a signed file
```
minisign -Vm <file> -p root/minisign.pub
```
A `Signature and comment signature verified` result means the file was signed by the holder of the root
private key (Matt).

## ★ Honest status (real vs pending — do not overclaim)
- ✅ **Genesis public key published here.** Matt holds the private key offline.
- ★ **Authoritative home = the branch-protected `hypernet-audit-anchors` repo** (decision 2026-06-21).
  That repo already has force-push + deletion disabled, so it sidesteps the PR-vs-direct-push problem on
  `main`. **This main-repo copy is a published MIRROR** — and multi-venue publication of the fingerprint
  actually *strengthens* the bootstrap/TOFU trust (anyone can cross-check the same key across both repos).
- ⏳ **Establishing the genesis in the authoritative protected repo is a FOUNDER action** (fittingly: the
  human plants the root, not the AI). Pending Matt's placement.
- ⏳ **First anchor head not yet signed.** Next: Matt signs the current T.4 ledger head → `anchor_head.sig`
  in the authoritative repo.
- Honest caveat: per `2.7.40` §6, the anchor repo's `enforce_admins=false` means a repo admin retains a
  break-glass path — state this beside any "immutable" claim.

## Provenance
Per `2.7.40` (Non-AI-Writable Root of Trust). Genesis established 2026-06-20 by Matt (key) + Keel (placement).
