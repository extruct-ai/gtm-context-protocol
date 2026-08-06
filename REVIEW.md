# Review: crm-context protocol (v0.4) vs. gtm-content current architecture

Date: 2026-08-06. Method: two parallel deep audits — one of this repo (every file, all 3 commits), one of the production repo (`revops/crm/`, `campaigns/`, `knowledge_base/`, `revops/db/`, `docs/account-workspace-architecture.md`) — synthesized below. All claims carry file:line evidence from one of the two repos.

## Verdict

The proposal is a linking protocol without payloads; the current repo is payloads without a linking protocol. They are almost perfectly complementary, and the merged system is better than either.

The proposal's five durable ideas split into two groups. A stable ID grammar, a thin machine-readable manifest per asset, and a status lifecycle each fix a pain the current repo demonstrably has. The signal definition/occurrence split and the per-company population loop (raw context accumulating → distilled views) are different: they are new capabilities. Signals have no current equivalent in any form — gtm-content has no signal definitions anywhere. The population loop is half-built as of early August: the pipeline-touch routine and account-event-sync skill now continuously populate *engagement state* (event logs, deal context, drafts) across 90+ accounts, but nothing yet accumulates *research-side* context — raw meeting notes, threads, entity observations, re-run research — which is the half the proposal's `context/raw/` + distillation design covers. Its central mistake is storing what should be derived: per-file component entries with hand-embedded IDs turn convention into a sync obligation with zero enforcement, and LLM agents doing file ops are exactly the population most likely to skip the bookkeeping. Meanwhile the current repo has already solved, in production, the hardest problems the proposal hasn't touched: system-of-record doctrine, the file/database boundary, payload templates with attribution discipline, and enforcement hooks.

Recommendation in one line: **adopt the IDs, thin the manifests, keep the warehouse canonical for instrumented events, build the population loop now (as skills and cron), and defer only the YAML workflow engine.**

---

## The two systems

**The proposal** (`crm-context`, v0.4): every orchestratable asset (company, campaign, signal, knowledge-base, workflow) is a self-describing folder with a YAML manifest carrying a stable ID, a component inventory, links to other assets, and workflow hooks (`README.md:5-11`). Workflows reference IDs, never paths; paths resolve through manifests (`README.md:80-88`). Formats are separated by mutation pattern: YAML = structure, Markdown = knowledge, JSONL = raw events, CSV = membership (`README.md:112-117`). Of 35 files, 19 content files are empty and 8 are `.gitkeep` — everything with content is protocol. The payloads (what goes *inside* `framework.md`, `context.md`, `engagement.md`) are entirely unspecified.

**The current repo** (`gtm-content`): an organically grown operational system. Its strongest asset is doctrine that is actually practiced — `revops/crm/README.md:22-28` assigns every fact class a system of record (Attio owns stage/value/owner, crm.db owns touches, files mirror and never own), and the account files carry it out line-by-line with `[VERIFIED: crm.db mart_outreach_timeline]` / `[INFERRED: …]` tags. Its weakest aspect is structural drift: four incompatible campaign folder generations, 13 loose data files (~8.2MB) at `campaigns/` root, byte-identical context files copied across campaigns, a forked account-workspace schema (`docs/account-workspace-architecture.md` 4-file vs `revops/crm/` 5-artifact), and campaign membership fragmented across CSVs, Extruct table UUIDs pasted in prose, Apollo/Instantly IDs, and a warehouse that only ever received 2 of ~24 campaigns.

---

## 1. What the proposal gets right — and the current pain each idea fixes

### 1.1 Stable ID grammar (`company.acme`, `campaign.x`, `signal.y`)
The current repo has no ID layer at the file level. Campaign membership truth is spread across four disjoint stores; external system IDs live as prose ("Extruct table 220fdc2a-… (2,612 companies; a duplicate 95610167… exists)" — `campaigns/revops-salesops-sub500/README.md:27-29`). The same account appears as `campaigns/kyb-b2b-fintech/accounts/finom/` and would appear as `revops/crm/finom/` with nothing tying them together. Wiki-links already collide across namespaces (`[[agentic-crm-stack]]` resolves to a content piece, not a KB node). A kind-prefixed stable ID that agrees with crm.db keys and Attio record IDs is the bridge the file layer is missing, and it is the single best import from the proposal.

### 1.2 A thin manifest per campaign, with a status lifecycle
Current campaign folders have no machine-readable descriptor at all. Consequence one: `campaigns/scripts/campaign_status.py` hardcodes one folder generation (`segments/**/emails.csv`), a fixed role set, and literal campaign names — it structurally cannot see 16 of 24 campaigns, including every campaign built since June. Consequence two: nothing distinguishes dead from dormant — `supplier-v2` untouched since April is indistinguishable from a paused effort. The proposal's `status: draft | active | paused | archived` (`README.md:58`) plus a manifest that shared scripts can glob solves both. This is what makes centralized tooling possible at all.

### 1.3 The signal definition/occurrence split — a new object type, and the KB is the right home for it
The most production-grade idea in the proposal (`README.md:90-108`): reusable definitions (`signal.new-fund`) separate from provenance-carrying detected occurrences (rows with `signal_id`, `company_id`, `detected_by`, `detected_at`, validation `status`). To be precise about the current state: gtm-content has **no signal definitions anywhere** — not in the knowledge base, not elsewhere. The closest artifacts are implicit triggers buried inside campaign hypothesis files, one-off detection runs (`crm_hiring_signals_*.csv` orphaned at `campaigns/` root), and dated why-now bullets inside individual dossiers. Every campaign re-derives its trigger from scratch, no detection is repeatable, and no occurrence carries provenance. This is not a formalization of existing practice — it is a new capability the current system simply lacks.

On placement — the proposal puts definitions in the knowledge base, and that is right, for a reason the proposal itself doesn't state: **a signal definition is a falsifiable pain hypothesis** ("a company hiring its first RevOps lead is in-market for CRM data work"), which is exactly the object class the KB lifecycle was built for. `emergent` when hypothesized, `validated` when detections convert across 2+ campaigns, `validated_by` recording where. Signals also complete the existing schema: the KB has plays (signal → action doctrine; 1 node today) but no representation of the atomic trigger a play fires on. Split the two halves cleanly: sales meaning and lifecycle live in the KB definition; detection mechanics (sources, queries, cadence) live as a section of it or beside the workflow that runs it.

### 1.4 Format separation as stated doctrine
The current repo does this by instinct and violates it at the edges: a mutating log file tracked in git (`revops/db/telegram_outbox.log`), an `.xlsx` in `revops/`, 8.2MB of CSV/JSONL at `campaigns/` root despite the `data → campaigns/{campaign}/data/` rule. The proposal's explicit format table (`README.md:112-117`) is worth adopting verbatim as a written rule, because "each format's failure modes match its content's mutation rate" is the correct organizing principle.

### 1.5 The campaign component set converges with what grew organically
The proposal's campaign anatomy — `hypothesis.md`, `voice.md`, `text.md`, `cadence.md`, `knowledge.md`, membership file — maps almost one-to-one onto what the newest real campaign grew by hand: kyb-b2b-fintech's `context/hypothesis_set.md`, `config/message-generation.md`, `emails/`, `sequence.md`, `context/*.md`. Independent convergence is strong evidence this is the right shape. Standardize it as the fifth and final campaign generation — this time with a manifest, so tooling holds it in place.

### 1.6 The KB taxonomy names the current graph's blind spots
The proposal's knowledge-base folders include `objections/`, `competitors/`, `use-cases/` (`README.md:26-27`). The current `knowledge_base/` has zero nodes in any of those categories — `market/` is empty, `emergent/` doesn't exist despite CLAUDE.md listing it. The taxonomy itself is a useful gap-list even before any node is written.

### 1.7 The population loop — half exists now; the research half is the gap
*(Corrected 2026-08-06 after merging main: an earlier draft of this section audited a stale checkout and called the account layer a one-shot batch. On main it isn't.)*

The company folder is designed as an accumulation → distillation pipeline: raw context flows in continuously (`context/raw/` events, messages, entities), distilled views are re-derived from it (`context.md`; `raw-signals.jsonl` → `signals.md` → `distillation.md`), and orchestration workflows name the cadence. gtm-content now has the **engagement half** of this loop in production: the pipeline-touch routine (scheduled, `revops/orchestration/routines/pipeline-touch/ROUTINE.md`) plus the account-event-sync skill merge activity from Attio/Gmail/Instantly/Granola into per-account `status_log.md`/`deal_context.md` and generate drafts across 90+ accounts, with `_reviews/` run records — a working, cadenced population mechanism that closely matches what the proposal's workflows sketch aspires to.

What still has no equivalent is the **research half**: nothing accumulates raw qualitative context per account (meeting notes, Slack/Telegram threads, entity observations have no inbox — `revops/slack/digest-*.md` was piling up homeless), and dossier research (`company_research.md`) is still one-shot with no re-run trigger or distillation step. The proposal's `context/raw/` + `research/` → distillation design is the blueprint for that missing half, and it can reuse the routine mechanics pipeline-touch already proved.

---

## 2. What the proposal must import from current practice

### 2.1 The system-of-record doctrine — fix `crm.yaml`
The proposal's `crm.yaml` carries `provider / record_id / last_synced_at` (fine — that's a pointer) plus an open-ended `fields: {}` (`crm.yaml:5-10`) — that's a writeable per-company mirror with no conflict policy, i.e., a second source of truth waiting to diverge. The production stance is the opposite and it works: "We mirror, we don't write back" (`revops/crm/README.md:22-28`), files display CRM state with the system of record named per fact class. The proposal should keep the pointer, delete `fields: {}`, and adopt the doctrine table as protocol text.

### 2.2 The database boundary — files are not a warehouse
The proposal is all-files because it has no database. The current repo already learned part of that lesson: entities and instrumented events live in a cloud-canonical SQLite warehouse (`crm.db` in GCS, hourly CI rewrite, read-only snapshot reads, writer-locked ETL writes, dbt-style raw→staging→marts — `revops/db/CRM_AGENT.md:17-19`, `DATABASE.md`) because cross-entity queries, joins, and dedup don't work over scattered files. But "raw" is not one class, and the boundary the protocol needs distinguishes two:

- **Instrumented event streams** — touches, sends, replies, content engagement, campaign membership. The warehouse is already their accumulator; per-company files should *mirror* these (as `status_log.md` mirrors `mart_outreach_timeline`), never re-accumulate them. Re-collecting this class per-folder recreates the fragmentation crm.db was built to end.
- **Unstructured, qualitative context** — meeting notes, Slack/Telegram threads, deep-research output, news, entity observations. This class has **no accumulator anywhere in the current repo** (which is why Slack digests sit homeless and `meetings/` sits empty), and the proposal's per-company `context/raw/` is the pragmatic store for it: agents append in place, distillation reads locally, portability holds. A later ETL can sweep it into the warehouse if cross-company querying ever demands it.

Signal occurrences straddle the line: the row schema and IDs (the proposal's design, kept as-is) matter more than the landing zone, but they should *end up* in a warehouse table — "all occurrences of `signal.new-fund` across companies" is a cross-company query by construction, and per-company JSONL alone answers it only by full scan. Landing per-company first with an ETL sweep (the `campaign_to_crm.py` precedent) is a fine implementation.

### 2.3 Payload templates and attribution discipline
The proposal specifies zero payload semantics — a reviewer cannot determine what `framework.md` is for. The current repo has the missing half: `revops/crm/_templates/` prescribes frontmatter and sections per artifact (buying-unit-by-layer map, why-now signals with Hiring/Leadership/News subsections, status-log line format embedded as a comment), `knowledge_base/node-template.md` embeds ~230 lines of per-node-type section schemas with placement rules ("customer names live in case-study nodes only"), and every claim carries `[VERIFIED: …] / [INFERRED: …] / [UNVERIFIABLE]`. Port the templates and the attribution rule into the protocol as the specification of each markdown component.

### 2.4 People as first-class entities
For a *CRM* workspace this is the proposal's largest modeling gap: people are empty markdown files under one company's `org-chart/people/`, with no IDs, no dedupe key, no ID-convention entry, and no way to represent a job change — a person is trapped inside a company folder. The current repo runs an entire campaign family on job changes (`campaigns/revops-job-change/`) and holds 9,232 deduped people in `mart_people`. People need stable IDs keyed to the warehouse (LinkedIn URL / email as natural keys), with company affiliation as a dated link, not a directory location.

### 2.5 The deposit loop and enforcement
The proposal has no validation of anything — no schema, no linter, `orchestration/scripts/` is a `.gitkeep`. The current repo demonstrates the only mechanism that keeps conventions alive: `knowledge_base/campaign-deposit-checklist.md` is enforced by a real PreToolUse hook on Instantly campaign creation, and the operational→KB citation counts (persona and win-case nodes cited 3-6× each by campaigns and content) show the loop actually deposits. Any manifest protocol ships with a validator (ID uniqueness, link resolution, component existence, status enum) wired into a hook or CI, or the manifests rot into exactly the stale index the README says it refuses to build (`README.md:11`).

### 2.6 Provenance as a pipeline table
The proposal's `orchestration:` blocks are empty category lists with four different shapes across four manifests. The current repo has a proven concrete pattern instead: revops-salesops-sub500's README documents the campaign as a step → script → output table with external IDs and dedup results. Until a workflow runner exists, that table *is* the orchestration record — and its known failure mode (steps run from scratchpad scripts that no longer exist) is an argument for committed scripts, not for a YAML engine.

---

## 3. Design flaws in the proposal to fix regardless of adoption

1. **Derive component IDs, don't store them.** Creating a company from the template requires updating ~15 embedded ID strings across two files; forget one and you get a silent duplicate `company.sample-company` with nothing to detect the collision. The rule `component_id = asset_id + "." + key` makes all of them derivable. Corollary: fix the key-vs-ID casing mismatch (`use_cases` → `kb.use-cases`) that makes derivation currently impossible.
2. **Convention over manifest for paths.** Every company has `context/context.md` at the same relative path — the components block restates a fixed layout and carries zero information beyond an obligation to stay in sync. Resolve `company.acme.context` by convention function, not manifest lookup; keep the manifest to what is *not* derivable: `id`, `kind`, `status`, `identity` (domain, crm_id), `links`, external IDs. This eliminates most of the maintenance burden while keeping ID addressing intact.
3. **Internal consistency debt** (all verified in the samples): the workflow manifest violates the "every asset follows the same shape" claim (no components/links/orchestration); `crm.yaml` is a component carrying an asset's identity with a `kind: crm-state` missing from the enum; the `orchestration:` block has four different shapes in four manifests; `knowledge_base` vs `knowledge_bases` link keys contradict the single-KB model; `signal-event.` ID prefix vs `kind: signal-occurrence` are two names for one concept; occurrence IDs collide when a signal fires twice for one company in one day.
4. **Link ownership.** Company↔campaign is stored as YAML on one side and CSV rows on the other, with no owner and no reverse-link rule. Store each edge once (membership in the warehouse; KB links on the operational asset) and derive the reverse.
5. **`companies.csv` scope creep.** The header (`current_step`, `next_action_at`, `exit_reason`) is a per-company campaign state machine, not "membership" — mutable execution state in a CSV invites concurrent-writer corruption. That state belongs in the warehouse (`mart_campaign_status` already exists for this).
6. **`version: 1` has no semantics** — no bump rule, no consumer, and git already versions files. Drop it until something reads it.
7. **The workflow engine is aspirational.** No resolver, runner, or prompt exists; the step vocabulary (`read | prompt | append | workflow`) has no conditionals, outputs, error handling, or parameter binding. Agents will bypass manifest resolution via path convention — which is fine if paths *are* the convention (see #2), and self-defeating if the manifests pretend otherwise.

---

## 4. What to change in gtm-content, based on the proposal

1. **Adopt the ID grammar repo-wide.** `company.{slug}` / `campaign.{slug}` / `signal.{slug}`, kind-prefixed, aligned with crm.db keys and Attio record IDs. Add to frontmatter of `revops/crm/{slug}/` artifacts and campaign manifests. Kind prefixes also resolve the existing wiki-link namespace collision between KB nodes and `content/pieces/` slugs.
2. **Add a thin `campaign.yaml` to every campaign folder** — id, status, dates, external IDs (Extruct table UUIDs, Instantly campaign UUIDs, Apollo list IDs, Linear issue), KB links. Migrate the UUIDs out of prose. Then rewrite `campaign_status.py` to discover campaigns by globbing manifests instead of hardcoding one generation's folder shape — that single change makes the status tooling cover all campaigns for good.
3. **Set `status:` on every campaign and archive the dead ones.** supplier-v2, suppliers-v1, linkedin-commenters v1-v3, and the April crm-enrichment family get `archived`; their loose root-level CSVs move into their `data/` folders or get deleted.
4. **Stand up signals as first-class — a new object type, not a migration:** definitions as `knowledge_base/gtm/signals/` nodes entering the standard lifecycle (`emergent` when hypothesized → `validated` when detections convert in 2+ campaigns); occurrences as a `signal_events` warehouse table using the proposal's row schema (`signal_id`, `company_id`, `detected_by`, `detected_at`, `source`, `status`), mirrored into per-account why-now sections under the existing mirror doctrine. The orphaned `crm_hiring_*` root files become the first ingested occurrences, and the existing hiring-signal campaign family becomes the first validation evidence.
5. **Heal the account-workspace fork.** Declare `revops/crm/` (5-artifact) canonical, update `docs/account-workspace-architecture.md` to match, and either migrate `campaigns/kyb-b2b-fintech/accounts/` or mark it a frozen instance. Add the stable company ID + Attio record ID + domain as structured frontmatter (boost-ai's `deal_context.md` already carries the Attio deal UUID — in prose).
6. **Standardize the fifth campaign generation** on the proposal's component set (hypothesis / voice / text / cadence / knowledge + data/ + reports/), documented once, held in place by the manifest and the status script.
7. **Ship the validator with the protocol, not after it.** One script: ID uniqueness, manifest↔directory sync, link resolution, status enum; wired as a hook (precedent: the deposit-checklist hook) or CI. The current repo's own history — data-placement rule vs. 8.2MB at root, centralized-scripts rule vs. 9 per-campaign `scripts/` dirs — shows conventions without enforcement don't hold.
8. **Build the research half of the population loop — the engagement half (pipeline-touch + account-event-sync) already runs.** Give every account folder a raw-context inbox and a refresh cadence: meeting notes (Granola) and Slack/Telegram digests route into per-account `context/raw/`; Deep Research re-runs on a trigger (signal fired, deal stage change) instead of once; distillation updates `company_research.md` in place, dated. Reuse the routine mechanics pipeline-touch proved — a scheduled ROUTINE.md wrapping a skill — and keep the proposal's workflow YAML as written cadence doctrine until a runner exists.

## 5. What not to adopt

- **The components block as path indirection** — thin the manifest instead (§3.1-3.2).
- **Per-company re-accumulation of instrumented event streams** (touches, sends, replies, membership) — the warehouse already owns those with joins, dedup, and CDC; mirror them into account files, don't re-collect them there. The rest of `context/raw/` — the unstructured qualitative class — stays, per §2.2.
- **`crm.yaml` `fields: {}`** — keep the pointer, keep mirror-don't-own.
- **The workflow YAML engine, for now** — current reality (committed scripts + skills + hooks + provenance tables in READMEs) delivers the same outcomes today. Revisit declarative workflows when a runner actually exists; the ID grammar loses nothing by waiting.

## 6. Sketch of the merged protocol

Thin manifest — everything else is convention:

```yaml
# campaigns/kyb-b2b-fintech/campaign.yaml
id: campaign.kyb-b2b-fintech
kind: campaign
status: active            # draft | active | paused | archived
created: 2026-06-25

external:
  extruct_table: f4fadaed-…
  instantly_campaigns: [1063a49e-…, 12308224-…]
  linear: EXT-…

links:
  knowledge: [industry-fintech-kyb, win-case-plata, win-case-finom-kyb, persona-revops]
# membership + per-company state: crm.db (raw_campaign_contacts / mart_campaign_status)
# components: by convention — hypothesis.md, voice.md, text.md, cadence.md, knowledge.md, data/, reports/
```

Boundary of record:

| Layer | Owns |
|---|---|
| External systems | What they already own: Attio deals, Instantly sends, Extruct tables, Apollo lists |
| crm.db (GCS, cloud-canonical) | Entities (people, companies), events (touches, signal occurrences), campaign membership and state |
| Markdown files + per-company `context/raw/` | Knowledge, strategy, dossiers, attributed *mirrors* of the above (`[VERIFIED:]`/`[INFERRED:]`), and unstructured raw context (meetings, threads, research output) |
| YAML manifests | Identity, status, external IDs, KB links — nothing derivable from layout |

The proposal's portability goal ("designed to be embedded in another project") survives intact: a thin-manifest workspace is *more* portable, because there are fewer strings to rewrite when instantiating it for a new client.
