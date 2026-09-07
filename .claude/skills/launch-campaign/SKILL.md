---
name: launch-campaign
description: Push a finished campaign into the connected sequencer. Use when the user says "launch {campaign}" or asks to start sending.
---

Follow the rules in `CLAUDE.md` and the spec in `PROTOCOL.md`.

1. Preflight: status is `active`, `text.md` and `cadence.md` are non-empty, every `companies.csv` id resolves to a company folder, and contacts for the target personas exist under `org-chart/people/`. Fail the preflight loudly instead of launching a half-built campaign.
2. Create the sequence in the connected sequencer via MCP from `text.md` + `cadence.md`; enroll the contacts. Confirm with the user before anything actually sends.
3. Record every created external id in `campaign.yaml` under `external:` (sequencer, campaign ids, enrichment table) — never in prose.
4. Ongoing performance is read live from the sequencer when asked — never copied into the repo.
