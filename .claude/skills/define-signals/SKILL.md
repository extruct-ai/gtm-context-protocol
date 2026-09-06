---
name: define-signals
description: Define buying-intent signals as reusable assets. Use when the user says "define my signals" or describes events that mean buying intent.
---

Follow the rules in `CLAUDE.md` and the spec in `PROTOCOL.md`.

1. Ask the user which events mean buying intent for them (funding, hiring, leadership change, tech adoption, expansion). One signal = one observable event.
2. For each signal, ask which tool detects it. Don't recite a fixed menu — check what the user actually has connected and propose from that. Categories worth covering: enrichment, search and scraping, intent and hiring data, CRM activity, email, meeting transcripts. Write the tool's name and its query into the `detection` block of the signal's `signal.yaml`. `provider` is a free string naming the connected integration (`apollo`, `exa`, `predictleads`, `crustdata`, `attio`, `gong`) — there is no fixed set, and each category has dozens of viable sources. This is the point of a signal definition: detection lives in the signal, in one place, never inside a workflow.
3. Copy `knowledge-base/signals/sample-signal` into a new signal asset, update its `id`, and write `definition.md`: what the signal means, what evidence counts.
4. Set each signal's status to `active`. Never create signals the user didn't confirm.
