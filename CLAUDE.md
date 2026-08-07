# GTM Context Protocol — agent instructions

This folder is a file-based GTM context. You orchestrate research, enrichment, campaigns, and CRM sync over plain files, using the user's MCP connections (CRM, meeting recorder, sequencer, enrichment). The full spec is in `PROTOCOL.md` — read it before structural changes.

## Rules

- Reference assets by stable ID (`company.acme`), never by path. Resolve paths through the asset's YAML manifest.
- Every asset folder has a manifest (`company.yaml`, `campaign.yaml`, `signal.yaml`, `knowledge-base.yaml`). When you add, move, or rename a file, update the manifest in the same change.
- Create new assets by copying the matching `sample-*` template, renaming it, and updating every `id` in the manifest. Never leave `sample` IDs behind.
- IDs are permanent. Renaming updates `path` in the manifest, never `id`.
- Format separation: YAML = structure and links, Markdown = human-readable knowledge, JSONL = append-only raw data (never rewrite history), CSV = membership lists.
- Signal occurrences are appended to `companies/{name}/research/raw-signals.jsonl` with `signal-event.{company}.{signal}.{date}` IDs; distill validated ones into `research/signals.md`.
- Keep `status` honest: `draft` → `active` → `paused` → `archived`.

## Placement rules

- Before placing any fact, apply the **boundary test**: *if this fact changed, what else would have to change?* If the answer crosses a folder boundary, it's in the wrong folder. Semantics: `knowledge-base/` = true regardless of audience; `campaigns/` = what we do to a population; `companies/` = one specific account; `orchestration/` = what runs. (Full definitions in `PROTOCOL.md`.)
- **The repo holds policy; the CRM holds state.** Stage, owner, last touch live in the CRM — never copy them into markdown. `crm.yaml` binds to the record; it doesn't mirror it.
- **Never fill an empty template slot with invented content.** An empty `voice.md` or `cadence.md` means *not decided yet*: ask the user or derive from raw data, otherwise leave it empty and keep the asset `draft`.
- **Don't hoist shared tactics into the knowledge base.** If several campaigns share a cadence or voice, duplicate it at campaign level — the KB only takes audience-independent truth.

## Where things go

| Artifact | Location |
| -------- | -------- |
| Company research narrative | `companies/{name}/context/context.md` |
| Raw CRM / meeting / email data | `companies/{name}/context/raw/*.jsonl` |
| Detected signals (raw) | `companies/{name}/research/raw-signals.jsonl` |
| Distilled signals | `companies/{name}/research/signals.md` |
| Org chart and people | `companies/{name}/org-chart/` |
| Campaign membership | `campaigns/{name}/companies.csv` (by `company_id`) |
| Reusable knowledge (product, personas, objections…) | `knowledge-base/` |
| Reusable agent prompts / deterministic scripts | `orchestration/prompts/`, `orchestration/scripts/` |

## Setup routine — "set up my GTM context"

1. Check MCP connections: CRM, meeting recorder, sequencer, enrichment. Report what's connected and what's missing (missing ones are fine — degrade gracefully).
2. Interview the user: what they sell, who buys it (personas), what signals indicate buying intent, common objections, main competitors.
3. Fill `knowledge-base/definition.md` and the subfolders (`product/`, `personas/`, `use-cases/`, `objections/`, `competitors/`) — one markdown file per item.
4. For each signal named, copy `knowledge-base/signals/sample-signal` into a new signal asset and write its `definition.md`.
5. Set `knowledge-base.yaml` status to `active`.

## Syncing companies — "sync my companies" / "sync my CRM"

The primary flow: reconstruct the user's book of business from their connected MCPs.

1. Pull the account list from the CRM MCP. If it's large, confirm scope with the user first (all accounts, active deals only, a segment).
2. For each account not yet in `companies/`: create the folder from `sample-company`, update all IDs, fill `identity` (domain, `crm_id`).
3. Pull per-company history — CRM activity, meetings, emails, contacts — into `context/raw/*.jsonl`; contacts become entries under `org-chart/people/`.
4. Write or refresh `context/context.md` for each company; record provider and sync timestamp in `crm.yaml`.
5. Re-runs are incremental: skip companies with no new data, append new raw records (never rewrite), refresh `context.md` only where something changed.

## Adding a single company — "add {company} and research it"

For a net-new target that isn't in the CRM yet, or a deep one-off.

1. Copy `companies/sample-company` → `companies/{company-slug}`; update all IDs in `company.yaml`; fill `identity` (domain, `crm_id` from the CRM if it exists there).
2. Pull available history via MCP — CRM record and activity, meetings, emails — into `context/raw/*.jsonl`.
3. Write `context/context.md`: the current state of the relationship, grounded in that raw data.
4. Research the company against the knowledge-base signals; append hits to `research/raw-signals.jsonl` and summarize in `research/signals.md`.
5. Set status to `active`.

## Creating a campaign — "create a campaign for {segment}"

1. Copy `campaigns/sample-campaign` → `campaigns/{campaign-slug}`; update all IDs.
2. Write `hypothesis.md` (why this segment, why now), `voice.md`, `cadence.md` with the user.
3. Enroll companies by adding rows to `companies.csv` — `company_id` only, never paths. Companies not yet in `companies/` get onboarded first (see above).
4. Link the campaign to the knowledge base and relevant signals in `campaign.yaml`.
