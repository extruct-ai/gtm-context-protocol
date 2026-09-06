---
name: add-company
description: Onboard and research one company. Use when the user says "add {company} and research it" — a net-new target not in the CRM, or a deep one-off.
---

Follow the rules in `CLAUDE.md` and the spec in `PROTOCOL.md`.

1. Copy `companies/sample-company` → `companies/{company-slug}`; update the `id` in `company.yaml`; fill `identity` (domain, `crm_id` from the CRM if it exists there) and the `crm:` binding.
2. Pull available history via MCP — CRM record and activity, meetings, emails — into `context/raw/*.jsonl` (every record with `source` + `source_id`).
3. Write `context/context.md`: the current state of the relationship, grounded in that raw data.
4. Research the company against the knowledge-base signals; append hits to `research/raw-signals.jsonl`, record the keep/drop calls in `research/distillation.md`, and summarize the survivors in `research/signals.md`.
5. Set status to `active`.
