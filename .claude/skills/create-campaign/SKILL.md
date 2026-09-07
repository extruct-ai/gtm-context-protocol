---
name: create-campaign
description: Design a campaign for a segment. Use when the user says "create a campaign for {segment}".
---

Follow the rules in `CLAUDE.md` and the spec in `PROTOCOL.md`.

1. Copy `campaigns/sample-campaign` → `campaigns/{campaign-slug}`; update the `id`.
2. Write `hypothesis.md` (why this segment, why now), `voice.md`, `cadence.md` with the user, then draft `text.md` in that voice for the user to approve.
3. Enroll companies by adding rows to `companies.csv` — `company_id, enrolled_at, status`, never paths and never execution state. Companies not yet in `companies/` get onboarded first (add-company / sync-companies).
4. Link the relevant signals in `campaign.yaml` (`links.signals`); name the knowledge-base pieces the campaign leans on in `knowledge.md`.
