---
name: sync-companies
description: Sync the book of business from connected sources into company folders. Use when the user says "sync my companies" or "sync my CRM".
---

Follow the rules in `CLAUDE.md` and the spec in `PROTOCOL.md`.

The primary flow: sync the user's book of business from their connected sources — CRM, email, meeting recorder, sequencer.

1. Pull the account list from the CRM MCP. If it's large, confirm scope with the user first (all accounts, active deals only, a segment).
2. For each account not yet in `companies/`: create the folder from `sample-company`, update the `id`, fill `identity` (domain, `crm_id`) and the `crm:` binding (provider, record id).
3. Pull per-company history — CRM activity, meetings, emails, contacts — into `context/raw/*.jsonl`. Every raw record carries `source` and `source_id`; dedupe on that pair. Contacts become entries under `org-chart/people/`, deduped on email (else LinkedIn URL), with the key in the file's frontmatter.
4. Write or refresh `context/context.md` and the `engagement.md` digest for each company; advance the per-source cursors in the `sync:` block of `company.yaml`.
5. Re-runs are incremental: start from each source's `sync:` cursor, append new raw records (never rewrite), refresh `context.md` only where something changed.
