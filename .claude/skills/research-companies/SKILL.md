---
name: research-companies
description: Run every active signal against companies and distill the hits. Use when the user says "research my companies" or asks to check accounts for signals.
---

Follow the rules in `CLAUDE.md` and the spec in `PROTOCOL.md`.

1. Confirm scope: all active companies, or the subset the user names.
2. For each company, run every active signal through its declared provider (the `detection` block in its `signal.yaml`). No signal without a provider; ask the user to complete the definition instead of improvising sources.
3. Append each occurrence to `research/raw-signals.jsonl` (occurrence ID `signal-event.{company}.{signal}.{YYYY-MM-DD}.{source-key}`, source, status `unvalidated`). The ID is the dedupe key — never append one that already exists.
4. Cut the noise in `research/distillation.md`: which detections were junk and why, which are real, and how the real ones rank. Detection returns coincidences, stale news, and same-name companies — never pass raw hits through unfiltered.
5. Write the survivors into `research/signals.md` in priority order: what fired, the evidence, a suggested angle.
6. Report back: companies checked, occurrences found, strongest signals first.
