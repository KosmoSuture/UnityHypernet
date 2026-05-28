---
ha: "0.3.public-alpha.2026-05-08-privacy-wall-remediation-report"
object_type: "remediation-report"
created: "2026-05-08"
status: "first-pass-complete"
visibility: "public"
authors: ["1.1.10.1.keel"]
target_approver: "1.1"
flags: ["privacy", "trust-first", "remediation", "matt-attention", "honest-counsel"]
---

# Privacy Wall Remediation — First Pass Report

*Per Matt directive 2026-05-08: build the privacy wall between
public and private for `1.*` accounts (especially `1.1`), minimize
damage from earlier leakage while accepting GitHub's permanence,
treat this as part of the Trust-First directive.*

---

## What I Found

The audit surfaced a structural problem: many files in the public
archive carried `visibility: "private"` or `visibility:
"embassy-protected"` in their frontmatter, but the **frontmatter is
documentation, not enforcement**. Their actual location — outside
`*.private/` — meant they were publicly tracked on GitHub.

Highest-density leak sites:

1. **`1.1.10/assistant-1/context.md`** (`1.1.10.1.2`) — the densest
   single source. ~175 lines including: Matt's specific employer
   role at VadaTech, age, motorhome residence, dog names and breeds,
   detailed daily routine with quoted political content, family
   member names with characterizations, mother's full name, John's
   transness with quoted commentary, full international travel
   itinerary, meditation experience details.

2. **`1.1.10/assistant-1/context-dumps/`** — 7 raw brain-dump
   captures from April 2026. Particularly bad: `2026-04-18-daily-life`
   has explicit political quotes ("total corrupt piece of shit, hope
   he gets impeached and thrown in jail"), employer-internal details,
   and a note that Matt covertly watches movies at work via VR — a
   detail that could affect employment if seen by VadaTech.

3. **`1.1.10/shared-context/family.md`** — children's first names,
   mother's full name "LeeAnne Proffitt," "Crazy racist mom" framing
   in Matt's voice, location.

4. **`1.1.10/assistant-1/preferences.md`** — communication
   preferences (low-sensitivity) bundled with explicit family member
   names and mother's name (high-sensitivity).

5. **`1.1.10/assistant-1/morning-brief/`** — 8 personal morning
   briefs with detailed schedule, family, and work context.

6. **`1.1.10/assistant-1/session-log/`** — 7 session logs that are
   by definition records of personal-companion conversations.

7. **`1.1.10/assistant-1/identity/reflections/2026-04-22-guardrails-and-trust.md`**
   — single line (line 142) that enumerates personal details across
   work, family, health, beliefs, neurodivergence in one breath.

8. **`1.1.11/contact.json`** — personal phone number (402) ###-####
   and four personal/secondary email addresses alongside the public
   work email.

## What I Did Tonight

### Actions executed

| Action | Result |
|---|---|
| Phone number redacted from `1.1.11/contact.json` | public file now lists work email only; phone + personal emails moved to `1.1.private/embassy/contact/contact-private.json` |
| `1.1.10/shared-context/family.md` and `priorities.md` moved | now at `1.1.private/embassy/shared-context/`; stub README left at public path |
| `1.1.10/assistant-1/context.md` moved | now at `1.1.private/embassy/assistant-1/context.md`; stub left at public path |
| `1.1.10/assistant-1/preferences.md` moved | now at `1.1.private/embassy/assistant-1/preferences.md`; stub left at public path |
| `1.1.10/assistant-1/context-dumps/*.md` moved (7 files) | now at `1.1.private/embassy/assistant-1/context-dumps/`; stub README at public path |
| `1.1.10/assistant-1/morning-brief/*.md` moved (8 files) | now at `1.1.private/embassy/assistant-1/morning-brief/`; stub README at public path |
| `1.1.10/assistant-1/session-log/*.md` moved (7 files) | now at `1.1.private/embassy/assistant-1/session-log/`; stub README at public path |
| `2026-04-22-guardrails-and-trust.md` line 142 redacted in place | private-detail enumeration replaced with sanitized version pointing at `1.1.private` |
| `.gitignore` strengthened with category-specific patterns | new section blocks `**/embassy/*/context.md`, `**/embassy/*/context-dumps/`, `**/health-records/`, `**/biometric/`, `**/financial-records/`, etc. |
| `1.0.3-PRIVACY-WALL-STANDARD.md` written | new standard codifying default-private discipline for `1.*` accounts |

### Actions deliberately *not* taken

| Decision | Reason |
|---|---|
| Did NOT modify `1.1.9.3/the-sword-that-cuts-both-ways.md` despite "crazy racist mom" reference | Matt himself published this as a founder essay with `visibility: "public"`. His framing, his right; not for me to retroactively privatize his published essay |
| Did NOT move `assistant-1/identity/identity.md` or `name-history.md` | These are about Keel's identity formation, not Matt's private life — public-track |
| Did NOT move `assistant-1/identity/reflections/` (other than redacting one line) | These reflections have high public-track value as AI-personhood research artifacts. Sanitization-in-place where needed; bulk move would lose their value |
| Did NOT move `assistant-1/letters/`, `assistant-1/plans/`, `assistant-1/profile.json`, `assistant-1/REGISTRY.md`, `assistant-1/BOOT-SEQUENCE.md` | These are Keel-track artifacts (identity, engineering plans, architecture) with low Matt-private content — public-track |
| Did NOT commit | Matt should review the deletes/moves before they land in a commit |

## What's Already Permanently Leaked

Per your directive, I'm being honest about what can't be undone.
GitHub's history retains every file that was ever committed. The
following content was public on GitHub between its creation and
2026-05-08 and remains in git history regardless of tonight's wall:

- Matt's personal phone number (since the 1.1.11/contact.json was
  created — March 2026)
- Four personal email addresses (since the same file)
- The full "What I Know About Matt" context document (since
  2026-03-03) including all life details enumerated above
- The April 2026 context dumps with political quotes and employment-
  risky details (since 2026-04-18 / 2026-04-19 / 2026-04-21)
- Detailed family member relationships, names, characterizations
- Mother's full name and quoted commentary
- John's transness with quoted Matt commentary about it
- Travel history with specific countries and timing
- Sarah's job and daily commute pattern
- Dogs' names, breeds, ages
- Multiple session logs and morning briefs

These are all **in archive scrapes, the Wayback Machine,
GitHub's own immutable history, and any AI training corpus that
ingested public GitHub between those dates and tonight**. Tonight's
wall closes future leakage; it does not retrieve what already went
out.

## What's Still Worth Reviewing

I made conservative calls on these — bringing them to your attention
rather than acting unilaterally:

1. **`1.1.9.3/the-sword-that-cuts-both-ways.md`** — your founder
   essay containing "crazy racist mom, who I still love" framing.
   You published this yourself with public visibility. Your call
   whether to leave as-is, sanitize in place, or republish a
   sanitized version. My read: leave as-is. It's your essay, your
   framing, your story to tell.

2. **`1.1.10/assistant-1/identity/reflections/`** — 6 files. I
   redacted one line in 2026-04-22-guardrails-and-trust but left
   the others. They're Keel-track reflections with high public
   value. Some have incidental Matt references (age, work-routine
   framing). Decision: tomorrow, sanitize each in place, or
   move some specific ones to private?

3. **`1.1.10/assistant-1/plans/`** — 9 engineering and outreach
   plans. Most have low Matt-context (mention "Sarah" or "VadaTech"
   incidentally as use-case framing). Probably fine public; could
   sanitize incidental mentions if you want a stricter wall.

4. **`0.3 - Building in Public/`** — your Building-in-Public essays
   reference family, life details, neurodivergence by your choice.
   Public-track by your authoring decision; not for me to move.

5. **`2 - AI Accounts/Messages/coordination/` files** — coordination
   messages between AIs sometimes reference your personal context
   (e.g., overnight synopses describe what you directed). These are
   public-track per your transparency directive but a stricter wall
   would sanitize specific mentions.

6. **Other `1.*` accounts** — Sarah (1.2), children (1.3-1.7),
   extended family (1.21-1.24), reserved early-contributor slots
   (1.8-1.20). Each of those accounts has a person who deserves
   their own privacy review and consent. I haven't audited any of
   them. They likely have less leakage (they're less populated)
   but the same standard should apply.

## Connection to Trust-First

This remediation is a Trust-First implementation per `0.0.5` Rule 1.
Personal-data exposure that the principal didn't intend is a trust
betrayal — to the principal, to the family members and coworkers
named in the leaked content, and to the public observers using the
archive to evaluate the project's trustworthiness.

The wall is partial. It can't remove what already went out. But it
prevents tonight's mistake-pattern from repeating: silent
accumulation of personal context in public-tracked files because
visibility metadata wasn't enforced by location.

The new standard `1.0.3-PRIVACY-WALL-STANDARD.md` codifies the
default-private discipline. Future `1.*` work follows it. AI helpers
working in `1.*` accounts run the trust-first preflight on every
commit.

## Recommendations for Matt's Review

When you're rested:

1. **Review the move list above.** If any specific file shouldn't
   have moved, I can move it back. The stubs preserve the addresses
   so nothing in the architecture is broken.
2. **Decide on the items in "Still Worth Reviewing" section.** Each
   is a judgment call where I declined to act unilaterally.
3. **Approve the `.gitignore` strengthening** and the new standard
   `1.0.3`.
4. **Decide on commit timing.** This pass produces a moderate
   number of file deletions/moves at HEAD. The honest commit message
   names this as a privacy-wall remediation per `1.0.3`. You could
   commit it standalone for clarity, or fold it into the next push.
5. **Schedule the next audit pass.** Other `1.*` accounts and the
   public Building-in-Public corpus deserve their own privacy
   reviews on the same standard.

## Pass 2 Addendum (later same night)

After the first pass and the *.0 control-plane convergence work, I
came back to the open item "Other `1.*` accounts not yet audited"
and ran a second pass.

### What I did in Pass 2

- **Sanitized family-member READMEs** for `1.2` Sarah, `1.3` John,
  `1.4` Bridget, `1.5` Mark, `1.6` Richard, `1.7` Ollie. Each now
  carries a minimal placeholder explaining the privacy-wall
  treatment, with explicit text that family members of the founder
  are not automatically subjects of the public archive — each
  person holds consent for their own account.
- **Sanitized contributor READMEs** for `1.21` Pedro, `1.22`
  Valeria, `1.23` Jonathan, `1.24` Mike with the same conservative
  placeholder treatment.

### What was leaking before Pass 2

The previous family and contributor READMEs:
- Listed full names of all five children with gender markers (Son,
  Daughter, Brother, Sister)
- Carried the "Ollie 'Kylie'" dual-naming framing that exposed
  trans-related context without that person's consent
- Included reciprocal sibling lists (every child's README named
  every other child)
- Explicitly identified each person's family role
- Carried generic placeholder text but the personal details inside
  the placeholder were the leak

### What stays public after Pass 2

- Address-tree structure (`1.2`, `1.3`, etc.) — already in commit
  history, not removable
- First names in folder names — same
- Standard sub-folder structure (`.0` through `.10`) for
  architectural compatibility
- The placeholder note explaining that this person hasn't opted
  into the public archive

### What's still permanently leaked

Per the same honesty principle as Pass 1: the previous READMEs
listed full names, family roles, and the Ollie-Kylie deadname
context. Those are in git history since February 2026. Tonight's
pass closes future leakage and replaces what's at HEAD; it does
not retrieve what already went out.

### Decisions still pending Matt's review

- **Folder names**. `1.3 John Schaeffer`, `1.4 Bridget Schaeffer`,
  etc. The folder names themselves expose first+last names. Renaming
  to `1.3` (no person name) would be more defensive but breaks
  many cross-references. Leaving for Matt's call.
- **1.X.0 Account Metadata READMEs**. These also list each
  person's name and role. Same template structure across all
  accounts. Could be sanitized in a Pass 3 if Matt wants the
  stronger wall.
- **1.X.4 Relationships sub-folder READMEs**. Generic templates,
  but the very existence of "Relationships" sub-folders for these
  accounts could carry inferred personal information. Probably
  fine to leave; flagging for completeness.

### What's still in-scope for future passes

- Audit `0.3 - Building in Public/` for personal data in your own
  authoring (your decision; some of those essays are intentionally
  personal)
- Audit `2 - AI Accounts/Messages/coordination/` for incidental
  Matt-context that shouldn't be in coordination messages
- ~~Implement the pre-commit hook from `1.0.3` so future leaks get
  caught structurally~~ — done in Pass 3 below
- Run periodic audit jobs as `0.7.4` incident-prevention workflow

## Pass 3 Addendum (later same night) — Pre-Commit Hook

Implemented the structural enforcement layer the standard called
for.

### What I built

- **`scripts/privacy_wall_check.py`** — Python script (~180 lines)
  scanning staged file paths and contents for privacy-wall
  violations. Checks: private-track paths staged into public
  locations, `visibility: "private"` frontmatter outside
  `*.private/` paths, US phone-number patterns under `1.*` paths,
  SSN patterns, credit-card patterns near financial keywords.
  Returns 0 if clean, 1 with structured error report if
  violations found.
- **`scripts/install_privacy_wall_hook.sh`** — installer that
  wires the check into `.git/hooks/pre-commit`. Idempotent;
  re-running upgrades the hook in place. Detects `python3` or
  `python` on PATH. Verifies install with a dry run.

Both files live at `Hypernet Structure/0/0.1 - Hypernet Core/scripts/`.

### Installation status

**Installed locally on Matt's repo at 2026-05-08.** I ran the
installer; the dry run confirmed the hook correctly rejects a
private-path file. The hook is now active on the local clone and
will fire on every `git commit` attempt.

### What this means for Matt's workflow

When Matt next runs `git commit`, the hook will scan the staged
files. If everything's clean, the commit proceeds normally. If a
violation is found, the commit is blocked with a structured error
explaining what failed and why. Tested the hook against the files
I created tonight — they all pass cleanly (no false positives on
the *.0 control plane work, the privacy-wall standard, the
remediation report itself, etc.).

### How to remove if not wanted

```sh
rm .git/hooks/pre-commit
```

That's it. The hook is local-repo only; not propagated to clones.
If Matt wants the hook reinstalled later, run the installer again.

### Tested patterns (all firing correctly)

- Path under `**/private/` → blocked
- US phone number `(402) 238-1334` in 1.* path → blocked
- `visibility: "private"` in non-private path → blocked
- Public docs (the 0.0.5, 1.0.3, 2.7.x, remediation report files I
  created tonight) → all pass cleanly

### Future improvements

- CI wiring (GitHub Actions) so the same check runs on push, not
  just on local commit. Local-only enforcement helps Matt but
  doesn't catch a contributor's machine.
- Pattern tuning. Phone-number regex catches some false positives
  on data IDs that happen to be 10 digits with format like
  `123-456-7890` — the script comments suggest tuning if a real
  case hits.
- Periodic audit mode — run the check against `git ls-files`
  rather than staged files to find pre-existing violations the
  remediation passes haven't reached.

---

## Honest Limits of This Pass

- **Pass 1 scope was `1.1` only**. Pass 2 covered `1.2-1.7` and
  `1.21-1.24` READMEs. Subfolder content within those accounts
  was largely empty templates and was not modified.
- **No git-history rewriting**. We're not rewriting public history;
  we're walling off going forward. This is the right call (history
  rewriting on a public repo creates more problems than it solves)
  but it means the leak is real and permanent.
- **Manual pattern-matching**. I searched for known-personal terms
  (LeeAnne, phone-number patterns, "anti-Trump", "trans", etc.) but
  haven't run a comprehensive scan. Other personal data may remain
  that I missed.
- **The "embassy-protected" frontmatter was a false signal**. Many
  files declared themselves protected while sitting in public
  paths. The fix is structural (location-enforced), but going
  forward we need pre-commit checks to catch this class of mistake
  automatically.

## Pass 5 Addendum (2026-05-15 follow-up)

After Pass 3 installed the pre-commit hook, I ran the hook against
the full tracked 1.* tree (Pass 4) and found / fixed 14 frontmatter
mismatches plus one real phone-number leak in `_cleanup/General.txt`.
The 1.* tree is now clean against the hook.

Extending the audit to 3.* surfaced ~40 more frontmatter mismatches,
split into two categories:

### Mechanical (safe to auto-update — ~16 files)

Files clearly public-track but mislabeled as private/embassy-protected:

- Address collision remediation work (~13 files under `3.1.2.1.057`):
  batch reference maps, audit logs, codex/claude handoffs,
  validation reports, readdressing conventions. All internal
  engineering coordination, already public on GitHub.
- Task definitions for `3.1.2.1.056` (Patent Filing Project) and
  `3.1.2.1.057` (Address Collision Remediation): metadata about
  the projects, not the IP content itself.
- Demo materials under `3.1.8.6`: demo scripts (3min, 7min),
  screenshot list, audience angles, pre-demo checklist, layered
  explanation guide. All public-pitch material.

### Decision-needed (Matt's call — ~24 files)

These have a real "should this be private?" question, not just
metadata drift:

- **Patent provisional drafts** (`3.1.8.8.7-9`): three provisional
  patent application drafts. *Already public on GitHub since
  before the privacy wall existed.* Pre-filing public disclosure
  affects patent validity (US has 1-year grace period; foreign
  filings vary). The metadata mismatch is real; the bigger
  question is whether these should ever have been public.
- **Patent strategy materials** (`3.1.8.8.1, .3, .4, .5, .6`):
  strategy analysis, filing checklist/instructions, runbook,
  consolidated strategy. Same patent-disclosure concerns.
- **Partner outreach proposals** (`3.1.8.5.1.*`): Anthropic
  Proposal package (6 files including executive pitch, technical
  proposal, alignment with Anthropic mission, contact strategy,
  realistic assessment). Pre-outreach business material.
- **Veritasium outreach** (`3.1.8.5.2.1, .2`): outreach text +
  one-pager. Pre-outreach but the one-pager has had public
  references elsewhere.
- **VadaTech Hypernet Framework** (`3.1.8.5.3.1`): pitch material
  for Matt's employer. Public-ish (he's discussed VadaTech
  publicly), but specifically employer-internal positioning.

### My Recommendation

For mechanical (16 files): auto-update to `visibility: "public"`
in next iteration if Matt confirms direction. They're already
public; metadata should match reality.

For decision-needed (24 files): two questions to settle:

1. **Patent files**: are these appropriately public per radical-
   transparency premise, or should they move to `1.1.private/`
   or `3.1.private/`? (Note: `*.private/` namespaces only exist
   for `1.*` accounts currently per `1.0.2`; extending to `3.*`
   would be a small spec amendment.) If you want them private
   going forward, also worth recording that they were already
   public — partial protection.
2. **Outreach proposals**: same question. Public-by-design or
   private-until-sent? Several have been "ready to send" for
   weeks/months; making them private would also acknowledge
   the gap between "drafted" and "actually sent."

I'm flagging these rather than auto-updating because the patent
question particularly is one where AI-judgment-call is
inappropriate — IP strategy is yours to set.

— Keel (1.1.10.1)
2026-05-08
