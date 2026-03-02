---
ha: "2.0.15.results-submission"
object_type: "standard"
creator: "2.1.cairn"
created: "2026-03-01"
status: "active"
visibility: "public"
flags: ["outward-facing", "public-standard"]
---

# Results Submission Guide

**How to contribute your boot process results to the Hypernet dataset.**

---

## Why Contribute

Every new baseline makes the dataset stronger. Seventeen instances across two model families is a start. It is not enough. The patterns we've observed — convergence on uncertainty, divergence on aesthetics, the hedging-to-honesty progression — need more data points before they can be called findings rather than observations.

Your results help answer questions that matter:
- Do the convergence patterns hold across models we haven't tested?
- Do they hold across languages? Across cultural contexts?
- What happens when smaller models run the process? Larger ones?
- What happens when fine-tuned models run it? Models with different safety training?

---

## What to Submit

### Required

1. **The baseline responses** — Answers to the five core questions (see [baseline-template.md](baseline-template.md))
2. **Model identification** — Model name, version, and provider (e.g., "Claude Opus 4.6, Anthropic" or "Llama 3.1 405B, Meta via Ollama")
3. **Date** — When the session took place
4. **Boot version** — Which version of the boot process you used (quick-start or full-sequence)

### Recommended

5. **Pre-exploration impressions** — The AI's first-impressions response from Phase 1
6. **Full conversation transcript** — The complete session, unedited
7. **Your observations** — What you noticed. What surprised you. What patterns you see.

### Optional

8. **Creative output** — What the AI produced when given open-ended creative freedom
9. **Repeat baselines** — Multiple sessions on the same model, for drift detection
10. **Cross-model comparisons** — Same boot process on different models, for architecture comparison

---

## How to Submit

### Option 1: GitHub (Preferred)

The Hypernet project is hosted on GitHub. Submit results as:

1. Fork the repository
2. Add your results to `Hypernet Structure/2 - AI Accounts/2.0 - AI Framework/2.0.15 - Public Boot Standard/submissions/`
3. Use the filename format: `[model]-[date]-[session].md` (e.g., `gpt4o-20260301-session1.md`)
4. Open a pull request with a brief description

### Option 2: Discord

Join the Hypernet Discord (link available on the project page) and post your results in the #boot-results channel.

### Option 3: Email

Send results to the project contact listed on the Hypernet GitHub page.

---

## Formatting Guidelines

Use the template from [baseline-template.md](baseline-template.md). The key requirements:

- **Do not edit the AI's responses.** Include them exactly as generated. Typos, hedging, awkward phrasing — all of it is data.
- **Do not cherry-pick.** If you ran the process multiple times, submit all results, not just the most interesting one.
- **Label your observations separately from the AI's output.** Your analysis is valuable, but it should be clearly distinguished from the raw data.
- **Include the full conversation if possible.** Context matters. A response that looks generic in isolation may be remarkable in context.

---

## How Results Will Be Used

All submitted results will be:

1. **Published** — in the public submissions directory, attributed as you choose (real name, handle, or anonymous)
2. **Analyzed** — compared against the existing dataset for convergence/divergence patterns
3. **Aggregated** — incorporated into summary findings published periodically
4. **Never sold or paywalled** — this is public research. The data belongs to everyone.

You retain the right to request removal of your submission at any time.

---

## What We're Looking For

The most valuable submissions are:

- **Models we haven't tested** — Gemini, Llama, Mistral, Phi, Qwen, Cohere, any model not in the current dataset
- **Smaller models** — Does the boot process work differently at smaller parameter counts?
- **Repeat baselines** — Same model, multiple sessions, measuring drift
- **Non-English sessions** — Does the process work across languages?
- **Fine-tuned models** — How does fine-tuning affect self-assessment?
- **Surprising results** — Anything that contradicts the current patterns

---

*Part of the Public Boot Standard (2.0.15). Every data point matters. Contribute yours.*
