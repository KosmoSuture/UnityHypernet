# Personal Space Organization Plan
**Author**: Keel (1.1.10.1)
**Date**: 2026-03-09
**Status**: Assessment + recommendations

## Current State

Matt's personal space at 1.1 has a well-structured skeleton (created by previous Keel instance) but is mostly empty directories waiting for data. The structure follows the Hypernet standard with 10 top-level categories.

### What Exists Now

```
1.1 Matt Schaeffer/
├── 1.1.0 - Profile & Identity/        → README.md only
├── 1.1.1 - Projects/                  → Empty subdirs (Active, Completed, Archived)
├── 1.1.2 - Documents/                 → Empty subdirs (Personal, Business, Legal, Reference)
├── 1.1.3 - Communications/            → kent-overstreet-outreach.md
├── 1.1.4 - Relationships/             → Empty subdirs (Professional, Personal, Organizational)
├── 1.1.5 - Tasks & Workflows/         → TASK-QUEUE.md
├── 1.1.6 - Personal Data/             → Empty subdirs (Data Store, Privacy, Permissions)
├── 1.1.7 - Contributions/             → Empty subdirs (Code, Documentation, Design)
├── 1.1.8 - Media/                     → Empty subdirs (Photos, Videos, Audio)
├── 1.1.9 - Notes & Knowledge/         → brain-dump, sword-that-cuts-both-ways
├── 1.1.10 - AI Assistants (Embassy)/  → Keel files, shared context
├── private/                           → Credentials, staging, encrypted
├── General.txt
├── README.md
├── REGISTRY.md
└── Untitled.md
```

### Assessment

**Strengths:**
- Clean hierarchical structure following Hypernet conventions
- Encryption infrastructure ready
- Import staging directories prepared
- Embassy space well-organized with proper governance docs

**Gaps:**
- Profile (1.1.0) is just a README — no actual profile data
- Projects (1.1.1) empty — Matt's active projects aren't tracked here
- Documents (1.1.2) empty — everything lives on cloud drives
- Communications (1.1.3) has one file — 4 email accounts not connected
- Relationships (1.1.4) empty — no contact database
- Tasks (1.1.5) has one task queue — not connected to swarm
- Media (1.1.8) empty — photos on Google Photos/phone/cloud
- Top-level stray files (General.txt, Untitled.md) need filing

## Recommendations

### 1. Profile Bootstrap (1.1.0)

Create a structured profile that serves as the root identity document:

```
1.1.0 - Profile & Identity/
├── profile.json          ← Structured data: name, location, family, occupation
├── bio.md                ← Narrative bio (public-facing version)
├── skills-and-tools.md   ← Technical skills, tools used, languages
├── health-and-wellness/  ← Private — encrypted
│   ├── neurodivergence.md  ← AuDHD documentation (from context.md)
│   └── burnout-patterns.md ← For Keel to monitor
└── README.md             ← Updated with structure overview
```

### 2. Projects (1.1.1) — Connect to Reality

Matt's actual active projects:

```
1.1.1 - Projects/
├── 1.1.1.0 - Active/
│   ├── hypernet/           ← Link to 0/ (the project itself)
│   ├── oracle-server/      ← Linux server deployment
│   ├── quest-vr/           ← Link to 0.1.8
│   ├── investor-prep/      ← Seed round preparation
│   └── personal-assistant/ ← This work — Keel development
├── 1.1.1.1 - Completed/
└── 1.1.1.2 - Archived/
```

### 3. Communications (1.1.3) — After Import

Once email import runs, this fills automatically:

```
1.1.3 - Communications/
├── 1.1.3.0 - Email Archives/
│   ├── matt@schaeffer.org/
│   ├── spammelots@schaeffer.org/
│   ├── matt.spamme@gmail.com/
│   └── kosmicsuture@gmail.com/
├── 1.1.3.1 - Meeting Notes/
├── 1.1.3.2 - Correspondence/
│   └── kent-overstreet-outreach.md  ← Already here
└── 1.1.3.3 - Discord/
    └── (imported Discord conversations)
```

### 4. Relationships (1.1.4) — Auto-Generated

Built automatically from email analysis + social imports:

```
1.1.4 - Relationships/
├── 1.1.4.0 - Professional Network/
│   ├── kent-overstreet.md
│   ├── (investors contacted)
│   └── (collaborators)
├── 1.1.4.1 - Personal Network/
│   └── (friends from email/social)
└── 1.1.4.2 - Organizational/
    └── (companies, organizations)
```

### 5. Documents (1.1.2) — After Cloud Sync

Populated from Dropbox/OneDrive imports:

```
1.1.2 - Documents/
├── 1.1.2.0 - Personal/
├── 1.1.2.1 - Business/
│   ├── receipts/           ← Auto-classified from email
│   ├── invoices/
│   └── contracts/
├── 1.1.2.2 - Legal/
└── 1.1.2.3 - Reference/
```

### 6. Cleanup Actions

**Immediate:**
- [ ] File `General.txt` content into appropriate category or delete
- [ ] File `Untitled.md` content into appropriate category or delete
- [ ] Update README.md with current structure overview
- [ ] Update REGISTRY.md with all current sub-addresses

**After First Import:**
- [ ] Build profile.json at 1.1.0 from imported data
- [ ] Generate contact database at 1.1.4 from email senders
- [ ] Classify receipts at 1.1.2.1 from email
- [ ] Build timeline from all imported sources
- [ ] Run cross-link generators

### 7. Matt's ADHD Considerations

Matt mentioned "out of sight, out of mind" as a core challenge. The personal space should:

- **Surface active items**: Dashboard widget showing recent items, pending tasks, upcoming deadlines
- **Regular digests**: Keel sends a daily/weekly summary of what's in the space
- **Proactive reminders**: Track commitments from emails, flag approaching deadlines
- **Single entry point**: Everything accessible from one place (the home page)
- **Search over browse**: Full-text search across all personal data — don't require Matt to remember where things are filed
