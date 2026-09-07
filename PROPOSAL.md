# Proposal: setup improvements (v0.5)

Date: 2026-09-04. Scope: this repo only — the template, its docs, and its agent surface. Method: full read of every file plus verification of each open item from [`REVIEW.md`](REVIEW.md) against the current tree.

## Premise

`REVIEW.md` was merged (PR #1) but none of its recommendations were implemented: the manifests are still fat, `crm.yaml` still carries `fields: {}`, `companies.csv` still holds an execution state machine, and every internal inconsistency it lists is still present. This proposal turns the decisions already made there into concrete changes, resolves the doctrine questions the review left open, and adds what a fresh audit found on top — mostly gaps in the routines and in agent operability.

Four parts, ordered by decreasing certainty: Part 1 is mechanical (decisions already made, just unexecuted), Part 2 resolves doctrine, Part 3 closes routine gaps, Part 4 upgrades the agent surface. Each part is one PR.

---

## Part 1 — Execute the review: thin manifests, honest doctrine

### 1.1 Derive component IDs; thin every manifest

Component IDs become derivable, never stored: `component_id = asset_id + "." + key`, with the key↔path mapping defined once in `PROTOCOL.md` per asset kind. The casing mismatch that currently blocks this (`use_cases` → `kb.use-cases`) is fixed by making keys kebab-case, matching ID grammar.

A manifest keeps only what layout cannot express — identity, status, external bindings, links:

```yaml
# companies/sample-company/company.yaml — entire file
id: company.sample-company
kind: company
name:
status: draft            # draft | active | paused | archived

identity:
  domain:
  crm_id:

crm:                     # binding, never a mirror (absorbs crm.yaml — see 1.2)
  provider:              # attio | hubspot | pipedrive | ...
  record_id:

sync:                    # per-source incremental cursors (see 3.3)
  crm:      { last_synced_at: }
  email:    { last_synced_at: }
  meetings: { last_synced_at: }
```

Gone: the ~15-entry `components:` block (paths are convention: `context/context.md`, `research/signals.md`, … exactly as laid out today), the `orchestration:` block (see 1.5), `links.campaigns` (see 1.6), and `version:` on every manifest (no bump rule, no consumer; git versions files — REVIEW §3.6).

Creating a company from the template drops from ~15 ID edits across two files to editing **one line**.

### 1.2 Fold `crm.yaml` into `company.yaml`; delete `fields: {}`

`crm.yaml` today is three pointer fields, an open-ended `fields: {}` mirror (a second source of truth waiting to diverge — REVIEW §2.1), and a header whose `kind: crm-state` violates the protocol's own kind enum. Deleting `fields:` leaves too little to justify a file: the binding moves into `company.yaml` as the `crm:` block above, and `crm.yaml` is removed from the template. The doctrine line stays and gets stronger — the binding is now three fields inside the record card, structurally incapable of mirroring anything.

*Alternative if a separate file is preferred (e.g. so CRM tooling can rewrite it without touching the manifest): keep `crm.yaml` but strip it to the pointer plus `sync:` cursors, no `id`/`kind`/`version` header. The default recommendation is the fold.*

### 1.3 `companies.csv` becomes membership, nothing else

Current header: `company_id,status,priority,owner,enrolled_at,current_step,last_action_at,next_action_at,exit_reason` — a per-company campaign state machine plus an ownership field, in the repo, directly against the repo's own "the CRM holds state" rule (REVIEW §3.5).

New header:

```csv
company_id,enrolled_at,status
```

`status` is enrollment policy only (`enrolled | paused | exited`). Step, timing, and outcomes live in the sequencer and the CRM; `owner` lives in the CRM. The agent reads them from there when it needs them.

### 1.4 Fix signal-occurrence ID collisions — and get dedupe for free

`signal-event.{company}.{signal}.{date}` collides when a signal fires twice for one company in one day. New form:

```text
signal-event.{company}.{signal}.{YYYY-MM-DD}.{source-key}
```

where `source-key` is the provider's record id when it has one, else a short hash of the source URL. This does double duty: the ID **is** the dedupe key, so "append only what's new" becomes a pure ID comparison against the existing JSONL — no separate dedupe bookkeeping.

### 1.5 One shape for orchestration: the workflow owns the edge

The `orchestration:` block currently has four different shapes across four manifests, all empty. It is also a reverse link: workflows already name the assets they touch in their `scope`. Per the store-each-edge-once rule (REVIEW §3.4), asset manifests drop `orchestration:` entirely; "which workflows touch this asset" is derived by grepping `orchestration/workflows/*.yaml` — which a validator (4.2) can do mechanically.

`PROTOCOL.md`'s "every asset follows the same shape" claim is amended honestly: the common shape is `id / kind / name / status`; `components`, `links`, `orchestration` are no longer part of it.

### 1.6 Links: one owner per edge

- Company↔campaign is stored twice (YAML on one side, CSV rows on the other). The CSV is the owner; `links.campaigns` leaves `company.yaml`.
- Campaign↔signal stays on the campaign (`links.signals`) — the consumer owns the edge; `links.campaigns` leaves `signal.yaml`.
- Signal↔KB is implicit (signals live inside the KB); `links.knowledge_base` leaves `signal.yaml`, which also retires the `knowledge_base` vs `knowledge_bases` key inconsistency.

---

## Part 2 — Doctrine resolutions

### 2.1 `engagement.md` is a mirror, and says so

As documented ("who has been touched, how often, on which channel, with what response"), `engagement.md` re-accumulates instrumented event streams — the exact class REVIEW §2.2 says files must mirror, never own. Respecify it: a **derived, disposable digest** regenerated from `context/raw/` plus live CRM/sequencer reads, where every claim names its source. Adopt the attribution tags proven in production (REVIEW §2.3):

```markdown
- 4 touches in the last 30 days, last reply 2026-08-21 [VERIFIED: instantly campaign 1063a49e]
- Champion appears disengaged since the June re-org [INFERRED: no reply to 3 threads]
```

The same tag rule applies to `context.md` and `framework.md`. This goes into `PROTOCOL.md` as protocol text, not advice.

### 2.2 Payload skeletons — specify shape without inventing content

The "never fill an empty slot" rule is right, but zero-byte templates mean every agent run invents its own payload shape. Resolution that honors the rule: each template markdown file gets a **commented skeleton** — section headings and one-line guidance inside HTML comments, invisible when rendered, zero invented content:

```markdown
<!-- framework.md — scored against the framework named in knowledge-base/definition.md.
Empty = no framework chosen yet; ask, don't invent.
One section per framework letter. Every score cites evidence with [VERIFIED:]/[INFERRED:] tags. -->
```

Files covered: `context.md`, `engagement.md`, `framework.md`, `orgchart.md`, `people/sample-person.md`, `distillation.md`, `signals.md`, signal `definition.md`, and the five campaign files (`hypothesis.md`, `voice.md`, `text.md`, `cadence.md`, `knowledge.md`). This ports REVIEW §2.3's payload-template discipline in the lightest form the template can carry.

### 2.3 Drop `context/raw/graph.json`

It appears in the manifest and README ("the account graph") but no routine writes it, no schema defines it, nothing reads it. Dead slots teach agents that slots may be ignored. Remove it from the template and the docs; reintroduce when something produces it.

---

## Part 3 — Close the routine gaps in `CLAUDE.md`

### 3.1 Nothing ever fills `framework.md` or `engagement.md`

The README sells qualification scoring and engagement depth (How-it-works §3, §5), but no routine writes either file and the "Where things go" table omits both. Add a routine:

> **Qualifying accounts — "qualify my companies"**
> 1. Framework named in `knowledge-base/definition.md`? If not, ask (MEDDIC, MEDDPICC, BANT, custom) and record it there. Never pick one silently.
> 2. Per company: score from `context/raw/` + CRM history into `framework.md`, every score tagged `[VERIFIED:]`/`[INFERRED:]`; unknowable criteria stay empty — a gap is a finding.
> 3. Refresh `engagement.md` as the derived digest (2.1).
> 4. Report: strongest accounts, and the criteria most often unknown — that list is discovery homework.

And extend the sync routine's step 4 to refresh `engagement.md` alongside `context.md`. Both files enter the "Where things go" table.

### 3.2 Campaign execution: a routine and an `external:` block

Campaign creation stops at `companies.csv`; nothing launches. Add:

> **Launching — "launch {campaign}"**
> 1. Preflight: status `active`, `text.md`/`cadence.md` non-empty, every `companies.csv` id resolves, contacts for target personas exist in `org-chart/people/`.
> 2. Create the sequence in the connected sequencer via MCP from `text.md` + `cadence.md`; enroll contacts.
> 3. Record every created external id in `campaign.yaml` under `external:` — never in prose.
> 4. Ongoing performance is read from the sequencer live, not copied into the repo.

```yaml
# campaign.yaml gains:
external:
  sequencer:                # e.g. instantly
  sequencer_campaign_ids: []
  enrichment_table:         # e.g. an Extruct table id
```

This is REVIEW §6's sketch, landed in the template — and it fixes the documented production failure of external UUIDs living in prose.

### 3.3 Incremental sync gets real cursors and a dedupe rule

"Skip companies with no new data" currently has no mechanism. Two additions:

- The `sync:` block in `company.yaml` (1.1) holds one cursor per source — CRM, email, meetings — because they advance independently.
- Protocol rule: **every raw JSONL record carries `source_id`** (the provider's own record id). Appending dedupes on `(source, source_id)`. Signal occurrences already get this via the 1.4 ID form.

### 3.4 Small routine fixes

- Campaign creation routine mentions `text.md` and `knowledge.md` (currently implicit).
- Sync routine states the contact dedupe key for `org-chart/people/` files: email, else LinkedIn URL — filename slug derived from it, recorded in the person file's frontmatter. (Full people-as-entities modeling — REVIEW §2.4 — stays out of scope for the template; the dedupe key is the minimum that prevents duplicate person files.)

---

## Part 4 — Agent operability: prose becomes machinery

### 4.1 Routines become skills

The seven routines are already trigger-phrase-shaped. Move each from `CLAUDE.md` prose into `.claude/skills/{name}/SKILL.md`:

```text
.claude/skills/
  setup-gtm-context/   sync-companies/   define-signals/
  research-companies/  add-company/      qualify-companies/
  create-campaign/     launch-campaign/
```

`CLAUDE.md` keeps what must always be loaded — the rules, the boundary test, the placement table — and shrinks by more than half. Skills load on demand, version independently, and travel to other harnesses that support the format. For agents without skill support, `CLAUDE.md` keeps a one-line index pointing at the skill files, so the instructions remain reachable as plain markdown.

### 4.2 Ship the validator — the repo's first real script

`orchestration/scripts/validate.py` (stdlib-only, no dependencies), checking:

- ID grammar and uniqueness across all manifests
- no `sample` IDs outside `sample-*` folders
- expected layout present per asset kind (the convention 1.1 relies on)
- link resolution: every `links:` entry and every `companies.csv` id resolves to an existing asset
- status enum; JSONL parses; occurrence IDs match the 1.4 form; raw records carry `source_id`

Wired twice: a `PostToolUse` hook on Write/Edit in `.claude/settings.json` (warn, don't block), and a ~10-line GitHub Actions workflow (block on PR). REVIEW §2.5's finding stands: conventions without enforcement don't hold, and "never leave sample IDs behind" is currently enforced by hope.

### 4.3 `.claude/settings.json`

Checked in with the hook config plus a minimal permission allowlist (`python3 orchestration/scripts/*`, read-only git), so a fresh clone — including web sessions — gets validation and prompts-free basics without manual setup.

---

## Sequencing

*Status: approved 2026-09-06; all four parts implemented as sequential commits on this branch (PR #2), one commit per part, in the order below.*

| PR | Contents | Risk |
| -- | -------- | ---- |
| 1 | Part 1 + 2.3: thin manifests, fold `crm.yaml`, trim `companies.csv`, occurrence IDs, drop `graph.json`; `PROTOCOL.md` + `README.md` updated to match | Low — decisions already made in REVIEW.md |
| 2 | Part 2.1–2.2: engagement respec, attribution tags, payload skeletons | Low |
| 3 | Part 3: new routines, `external:` block, sync cursors, dedupe rules | Medium — new surface, review the routine text |
| 4 | Part 4: skills split, validator, hook, CI | Medium — validate against a scratch clone before merge |

Each PR leaves the repo consistent on its own; nothing depends on a later PR.

## Open questions

1. **`crm.yaml`: fold or keep?** Proposal folds it (1.2); keep it as a stripped pointer file only if external tooling needs to rewrite it independently of the manifest.
2. **Skeletons: inline comments or `_templates/`?** Proposal says inline (2.2) — one file to read per slot. A `_templates/` directory is the production pattern and better if skeletons grow past ~20 lines.
3. **Workflow YAML: keep as doctrine or cut?** REVIEW §5 says defer the engine but keep the format as written cadence doctrine. Proposal keeps `orchestration/workflows/` as-is and touches it only for the shared-header cleanup (1.5).

## Explicitly out of scope

- A workflow runner (REVIEW §5 — revisit when one exists).
- People as warehouse-keyed first-class entities (REVIEW §2.4) — beyond the dedupe key in 3.4, this needs the production warehouse and doesn't belong in the template.
- Any warehouse/ETL machinery — the template stays all-files; the boundary-of-record table in REVIEW §6 remains the guide for when a deployment outgrows that.
