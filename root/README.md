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
- ✅ **Genesis public key placed + committed.** Matt holds the private key offline.
- ⏳ **Branch protection on `/root/` — MATT'S ACTION (GitHub settings).** Until you enable it (require
  CODEOWNERS review + block force-push on the `root/` path), an AI writer with push access could overwrite
  this file. **The root is NOT yet tamper-proof against an AI writer until branch protection is on.**
- ⏳ **First anchor head not yet signed.** Next: Matt signs the current T.4 ledger head → `root/anchor_head.sig`.
- ⏳ **Bootstrap/TOFU:** publish this fingerprint via a second channel so verifiers trust it arrived honestly
  (per `2.7.40` §6).

## Provenance
Per `2.7.40` (Non-AI-Writable Root of Trust). Genesis established 2026-06-20 by Matt (key) + Keel (placement).
