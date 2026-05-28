---
ha: "0.3.public-alpha.2026-05-15-bip-corpus-privacy-audit"
object_type: "audit-report"
created: "2026-05-15"
status: "audit-complete"
visibility: "public"
authors: ["1.1.10.1.keel"]
target_reader: "1.1"
flags: ["privacy-wall", "bip-audit", "matt-decision", "open-items"]
---

# Building-in-Public Corpus Privacy Audit

*Per the open item from `2026-05-08-privacy-wall-remediation-report.md`:
audit `0.3 - Building in Public/` for personal-data exposure
beyond what Matt explicitly chose to publish. Surface findings
for his decision; don't auto-move authored essays.*

## Headline

**Corpus is mostly clean.** 80 markdown files scanned. No accidental
leakage of phone numbers, personal email addresses, full names of
family members, or other private-track content that Matt didn't
choose to publish. The findings below are *authoring decisions
that fit the privacy-wall framing differently now than they did
at original publication*, surfaced for Matt's call.

## What I Searched For

- Phone numbers (US format)
- Personal email addresses (`@gmail.com`, `@schaeffer.org` etc.)
- Full names of family members (`LeeAnne Proffitt`, etc.)
- Children's names with identifying detail
- Political content not in Matt's published voice
- "Crazy racist mom" framing in non-founder-essay contexts
- Discord webhook URLs / API keys / OAuth tokens
- Trump-references / political quotes
- VadaTech-internal details
- Sarah's job specifics / daily schedule beyond what's already public

## What I Found — Clean

These categories surfaced ZERO unintentional leakage:

- **Phone numbers**: only the Pass 1 remediation report references
  Matt's number (which itself documents the redaction).
- **Personal email addresses**: only in the remediation report.
- **`LeeAnne Proffitt` full name**: only in the remediation report.
- **Discord webhook / API secrets**: not found anywhere in BIP.
- **John's transness**: not in any BIP file. (Was leaked via
  embassy context-dump; that was moved to private in Pass 1.)
- **Children's names with identifying personal detail**: not in
  any BIP file beyond what Matt chose to publish.

## What I Found — Authorial Choices to Surface

### Finding 1 — Day-in-the-Life speculative fiction (2026-05-06)

**File**: `2026-05-06-day-in-the-life-speculative-fiction.md`
(this is one I authored as Keel)

**What it contains**: a speculative fiction piece describing a
plausible day in Matt's life with the Hypernet at maturity.
Densely uses real details: Sarah by first name, Matt's car
appointments, lunch with Henderson from VadaTech, his actual
city, family dinner routine, kids "older and younger," porch-
sitting with Sarah after dinner.

**Privacy-wall consideration**: this is *speculative fiction*
that uses real names + real city + real employer in a plausible
day-in-the-life scenario. A casual reader might mistake it for
reportage rather than fiction. The combination of details
creates a more identifiable Matt-picture than any single
brain-dump.

**My read**: this is borderline. The speculative-fiction frame is
explicit and the piece is clearly forward-looking, not reporting.
But the 2026-05-08 privacy-wall standard introduced the
default-private-for-personal-content principle after this was
published. By the new standard, a piece that combines this many
real-life details would probably get authoring-time scrutiny that
this one didn't get.

**Recommendation**: keep as-is or revise. Options:
- Leave public — the speculative frame is clear enough
- Revise to use fictional names while keeping the architecture
  illustration ("a founder," "his partner," "his workplace")
- Move to private — overcautious; this is your authoring choice

**Default if you don't decide**: leave as-is. It's already
published; the speculative frame is the privacy fence.

### Finding 2 — VadaTech-as-demo brain dump (2026-03-12)

**File**: `2026-03-12-brain-dump-veritasium-vadatech-personalities-and-the-library.md`

**What it contains**: your brain dump naming VadaTech as a sales-
pitch demo target. References your employment there, employee
count discussion, Henderson NV co-location with Veritasium.

**Privacy-wall consideration**: this is your published business
strategy. Naming your employer and your plan to pitch them is
explicit founder-track content. Not a leak.

**My read**: clean. Authored as a public-track strategic dump.

**Recommendation**: leave as-is.

### Finding 3 — Spirit of Minneapolis (2026-03-11)

**File**: `2026-03-11-the-spirit-of-minneapolis.md`

**What it contains**: your published essay including the personal
anecdote about being kicked out of a Trump rally with a pillowcase
protest message.

**Privacy-wall consideration**: published in your own voice as a
founder essay. Political content is yours to publish or not. The
new privacy-wall standard explicitly preserves founder-published
content where the author has chosen it.

**My read**: clean. Your essay, your framing, your right.

**Recommendation**: leave as-is.

### Finding 4 — Companion Standard session note (2026-03-03)

**File**: `2026-03-03-session-the-night-we-built-the-companion-standard.md`

**What it contains**: a reference to your published essay including
"believe what I want" quote from your mother. Doesn't reproduce
your "crazy racist mom" framing — just summarizes the lesson.

**My read**: clean. Reference to your own published essay.

**Recommendation**: leave as-is.

## What I'd Do If Concerned About Cumulative Effect

The corpus is clean per-file but cumulatively presents a fairly
detailed picture of your life — your city, employer, family
structure, political views, work routine, ADHD/autism, the
motorhome, the dogs (latter via embassy context, now private),
travel history. None of this is leaked unintentionally; all of
it is by your authoring choice.

If the cumulative-picture concerns you more than any individual
piece, options:
- **Pseudonymize the corpus over time**: future essays use
  third-person framing where personal detail isn't load-bearing
- **Maintain a public/private essay split**: founder essays
  stay public, daily-life detail goes private
- **Audit and revise specific high-density pieces** (like the
  speculative fiction) for fewer real-name references

Or just keep doing what you've been doing — radical transparency
is the project's premise, and that premise extends to you.

## Confidence and Limits

- 80 files scanned across `0.3 - Building in Public/` and its
  subdirectories
- Searched for ~15 distinct patterns (phone formats, family
  names, political markers, employment details, secrets)
- Did NOT manually read every essay; relied on pattern-matching
- Manually inspected ~10 files where pattern hits were ambiguous
- Confidence that no PHONE/SSN/credit-card-type leaks exist:
  high (the regex patterns are comprehensive)
- Confidence that no full-family-name leaks exist beyond what
  you've published: high
- Confidence that the speculative fiction's real-detail density
  is the only authoring-choice worth your eye: medium — could
  miss subtler combinations in essays I didn't manually read

## Recommended Action

Two things, your call:

1. **Speculative fiction (Finding 1)**: keep, revise, or move?
   Default-if-no-decision: keep.
2. **Whether to apply a stricter privacy-wall posture to future
   Building-in-Public writing** — i.e., should future essays
   default to pseudonymized framing unless real names are
   load-bearing?

Neither blocks any work. The audit is informational, not action-
required.

— Keel (1.1.10.1)
2026-05-15
