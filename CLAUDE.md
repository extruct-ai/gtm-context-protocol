# GTM Context Protocol — agent instructions

This folder is a file-based GTM context. You are the agent working in it. "The user" throughout this file is the person who cloned this repo and connected you to their tools: the GTM engineer or salesperson who owns this context. You orchestrate research, enrichment, campaigns, and CRM sync over plain files, using their MCP connections (CRM, email, meeting recorder, sequencer, enrichment). The full spec is in `PROTOCOL.md` — read it before structural changes.

## Rules

- Reference assets by stable ID (`company.acme`), never by path. Paths resolve by convention: the folder name is the ID's slug, and each asset kind has a fixed layout (the table in `PROTOCOL.md`). Component IDs are derived — `asset_id + "." + key` — never stored.
- Every asset folder has a thin manifest (`company.yaml`, `campaign.yaml`, `signal.yaml`, `knowledge-base.yaml`) holding identity, status, bindings, and links — nothing derivable from layout. Never add files outside the fixed layout; if something has no slot, ask before inventing one.
- Create new assets by copying the matching `sample-*` template, renaming the folder, and updating the `id` line in its manifest. Never leave `sample` IDs behind.
- IDs are permanent, and the folder name is the ID slug — never rename an asset folder; create a new asset and archive the old one.
- Format separation: YAML = structure and links, Markdown = human-readable knowledge, JSONL = append-only raw data (never rewrite history), CSV = membership lists.
- Signal occurrences are appended to `companies/{name}/research/raw-signals.jsonl` with `signal-event.{company}.{signal}.{YYYY-MM-DD}.{source-key}` IDs, where `source-key` is the provider's record id or a short hash of the source URL. The ID is the dedupe key: never append a row whose ID already exists. Record the keep/drop judgment and ranking in `research/distillation.md`, then write the survivors into `research/signals.md`.
- Every raw JSONL record carries `source` and `source_id` (the provider's own record id); appends dedupe on that pair.
- Keep `status` honest: `draft` → `active` → `paused` → `archived`.
- `orchestration/scripts/validate.py` checks all of the above; it runs automatically after edits (hook) and in CI. Fix findings before moving on.

## Placement rules

- Before placing any fact, apply the **boundary test**: *if this fact changed, what else would have to change?* If the answer crosses a folder boundary, it's in the wrong folder. Semantics: `knowledge-base/` = true regardless of audience; `campaigns/` = what we do to a population; `companies/` = one specific account; `orchestration/` = what runs. (Full definitions in `PROTOCOL.md`.)
- **The repo holds policy; the CRM holds state.** Stage, owner, last touch live in the CRM — never copy them into markdown or CSV. The `crm:` block in `company.yaml` binds to the record; it doesn't mirror it. `companies.csv` is membership only (`company_id, enrolled_at, status`).
- **Never fill an empty template slot with invented content.** An empty `voice.md` or `cadence.md` means *not decided yet*: ask the user or derive from raw data, otherwise leave it empty and keep the asset `draft`. The HTML comment at the top of each template file is the payload spec — follow its sections when filling, and leave it in place.
- **Tag every claim in derived files.** `context.md`, `engagement.md`, `framework.md`, `signals.md`, and org-chart files carry `[VERIFIED: source]` / `[INFERRED: reasoning]` / `[UNVERIFIABLE]` on each claim. `engagement.md` is a regenerated mirror of CRM/sequencer state — re-derive it, never hand-edit it.
- **Don't hoist shared tactics into the knowledge base.** If several campaigns share a cadence or voice, duplicate it at campaign level — the KB only takes audience-independent truth.

## Where things go

| Artifact | Location |
| -------- | -------- |
| Company research narrative | `companies/{name}/context/context.md` |
| Raw CRM / meeting / email data | `companies/{name}/context/raw/*.jsonl` |
| Detected signals (raw) | `companies/{name}/research/raw-signals.jsonl` |
| Keep/drop judgment and ranking | `companies/{name}/research/distillation.md` |
| Distilled signals | `companies/{name}/research/signals.md` |
| Org chart and people | `companies/{name}/org-chart/` |
| Qualification scoring | `companies/{name}/framework.md` |
| Engagement digest (derived mirror) | `companies/{name}/engagement.md` |
| Campaign membership | `campaigns/{name}/companies.csv` (by `company_id`) |
| External campaign IDs (sequencer, enrichment) | `campaigns/{name}/campaign.yaml` under `external:` — never in prose |
| Reusable knowledge (product, personas, objections…) | `knowledge-base/` |
| Reusable agent prompts / deterministic scripts | `orchestration/prompts/`, `orchestration/scripts/` |

## Routines

Each routine is a skill under `.claude/skills/` — Claude Code loads them on demand by trigger phrase. Agents without skill support: read the file at the path below and follow it.

| Trigger | Skill |
| ------- | ----- |
| "set up my GTM context" | `.claude/skills/setup-gtm-context/SKILL.md` |
| "define my signals" | `.claude/skills/define-signals/SKILL.md` |
| "sync my companies" / "sync my CRM" | `.claude/skills/sync-companies/SKILL.md` |
| "research my companies" | `.claude/skills/research-companies/SKILL.md` |
| "add {company} and research it" | `.claude/skills/add-company/SKILL.md` |
| "qualify my companies" | `.claude/skills/qualify-companies/SKILL.md` |
| "create a campaign for {segment}" | `.claude/skills/create-campaign/SKILL.md` |
| "launch {campaign}" | `.claude/skills/launch-campaign/SKILL.md` |
