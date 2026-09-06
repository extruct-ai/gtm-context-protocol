# Protocol Specification

The full spec behind the GTM context. Read [`README.md`](README.md) first for the human overview; this file is for implementers and agents.

## Core model

- Every **orchestratable asset** (company, campaign, signal, knowledge base, workflow) has a **stable ID**.
- Every asset folder carries a **thin YAML manifest** holding only what layout cannot express: identity, status, external bindings, links.
- **Component IDs are derived, never stored**: `component_id = asset_id + "." + key`, where the keys and their paths are fixed by the layout table below. There is nothing to keep in sync and nothing to forget when creating an asset.
- Workflows reference **asset and component IDs, never paths** — paths resolve through the layout table.
- There is **no central registry**. IDs plus layout resolve everything; an index would only duplicate the tree and go stale.

## Folder semantics

Structure says where things *can* go; this section says what each folder *means*. Each is defined by the question it answers and by what makes it change:

| Folder | Question it answers | Changes when |
| ------ | ------------------- | ------------ |
| `knowledge-base/` | What is true regardless of who we're talking to — product, ICP, pricing, competitors, signal definitions | The world changes |
| `companies/` | What we know about, and have done with, one specific account | That account's world or our relationship changes |
| `campaigns/` | What we do to a specific population — cadence, text, membership | Strategy changes |
| `orchestration/` | What runs, when, and what it's allowed to write | The process changes |

CRM state is not a folder, because **the repo holds policy and the CRM holds state**. State answers *where is this person* — stage, owner, last touch. Policy answers *what are we allowed to do about them* — cadence, voice, membership. The two drift at completely different rates and have different owners; most CRM tooling fails by conflating them. So the `crm:` block in `company.yaml` **binds** a company to its CRM record (provider, record id) — it never mirrors it. There is no per-field CRM mirror anywhere in the repo, by design.

### The boundary test

Before placing a fact, ask: **if this fact changed, what else would have to change?**

- A price change must touch nothing in a campaign → pricing lives in the knowledge base.
- A touch-cap change must touch nothing in the knowledge base → cadence lives in the campaign.
- If the answer crosses a folder boundary, the fact is in the wrong folder.

Two corollaries:

- **Shared by many campaigns ≠ knowledge.** If four campaigns use the same cadence, it is still tactics: it stays at campaign level, duplicated. Only facts that hold regardless of audience get hoisted into the knowledge base. Painful duplication is a signal to design a new asset kind — never to pollute the KB.
- **Empty slots are questions, not invitations.** A template slot with no content (`voice.md`, `cadence.md`) means *not decided yet* — the asset stays `draft`. Filling a slot requires input from a human or evidence from raw data, never invention.

## Common YAML protocol

Every manifest shares one header:

```yaml
id:       # stable identifier — survives everything
kind:     # company | campaign | signal | knowledge-base | workflow
name:     # human-readable
status:   # draft | active | paused | archived
```

Beyond the header, each kind adds only what layout cannot express:

| Kind | Extra blocks |
| ---- | ------------ |
| `company` | `identity` (domain, crm_id), `crm` (provider, record_id — the binding), `sync` (per-source cursors) |
| `campaign` | `links.signals` (which signal definitions feed it) |
| `signal` | `detection` (provider, query) |
| `knowledge-base` | none |
| `workflow` | `trigger`, `scope`, `steps` |

Nothing else goes into a manifest. If a value is derivable from the layout, derive it; if it is state, it lives in the external system that owns it.

ID conventions:

```text
kb                                       # the knowledge base of the GTM context
signal.new-fund                          # signal
company.acme                             # company
campaign.pe-rollups-eu                   # campaign
workflow.daily-company-research          # workflow

campaign.pe-rollups-eu.hypothesis        # component ID — derived, never stored
company.acme.context                     # lets workflows target one part of an asset
```

IDs are permanent, and **the folder name is the ID's slug**: `company.acme` lives at `companies/acme/`. Renaming a folder would rename the asset, so folders don't get renamed — create a new asset and archive the old one instead.

## Layout is the contract

Component IDs resolve to paths through this table — the same relative layout in every asset of a kind:

**Company** (`companies/{slug}/`):

| Component key | Path |
| ------------- | ---- |
| `context` | `context/context.md` |
| `events` | `context/raw/events.jsonl` |
| `messages` | `context/raw/messages.jsonl` |
| `entities` | `context/raw/entities.jsonl` |
| `raw-signals` | `research/raw-signals.jsonl` |
| `distillation` | `research/distillation.md` |
| `signals` | `research/signals.md` |
| `org-chart` | `org-chart/orgchart.md` |
| `people` | `org-chart/people/` |
| `framework` | `framework.md` |
| `engagement` | `engagement.md` |

**Campaign** (`campaigns/{slug}/`):

| Component key | Path |
| ------------- | ---- |
| `companies` | `companies.csv` |
| `hypothesis` | `hypothesis.md` |
| `voice` | `voice.md` |
| `text` | `text.md` |
| `cadence` | `cadence.md` |
| `knowledge` | `knowledge.md` |

**Knowledge base** (`knowledge-base/`):

| Component key | Path |
| ------------- | ---- |
| `definition` | `definition.md` |
| `signals` | `signals/` |
| `product` | `product/` |
| `personas` | `personas/` |
| `use-cases` | `use-cases/` |
| `case-studies` | `case-studies/` |
| `objections` | `objections/` |
| `competitors` | `competitors/` |

So `company.acme.context` resolves to `companies/acme/context/context.md`, always. A workflow step:

```yaml
steps:
  - id: load-company-context
    action: read          # read | prompt | append | workflow
    assets:
      - company.{company_id}.context
```

needs no manifest lookup and can never dangle.

## Links: one owner per edge

Every relationship is stored exactly once; the reverse direction is derived, never written:

| Edge | Owner |
| ---- | ----- |
| company ↔ campaign | the campaign's `companies.csv` |
| campaign ↔ signal | the campaign's `links.signals` |
| signal ↔ knowledge base | implicit — signals live inside the KB |
| asset ↔ workflow | the workflow's `scope` |

"Which campaigns is acme in" is answered by scanning `campaigns/*/companies.csv` — cheap, and impossible to have two disagreeing answers.

## Signal definitions vs. occurrences

A signal definition declares its own detection. The `detection` block in `signal.yaml` names the provider (which connected tool checks it) and the query:

```yaml
detection:
  provider: predictleads    # name of a connected tool — apollo, exa, crustdata, attio, gong, …
  query: "announced a new fund OR closed fund"
```

`provider` is a free string naming whichever integration you connected, not a fixed enum — enrichment, search, intent, CRM, meetings and messaging each have dozens of viable sources, and pinning a closed list into the spec would only go stale.

Workflows read this block instead of hardcoding sources. One signal, one place to change how it's detected.

`signal.new-fund` is the reusable **definition** (an asset).
`signal-event.acme.new-fund.2026-08-01.pl-8842731` is one detected **occurrence** — a row in the company's `raw-signals.jsonl`:

```json
{
  "id": "signal-event.acme.new-fund.2026-08-01.pl-8842731",
  "kind": "signal-occurrence",
  "signal_id": "signal.new-fund",
  "company_id": "company.acme",
  "detected_by": "workflow.daily-company-research",
  "detected_at": "2026-08-01T10:30:00Z",
  "source": { "type": "company-announcement", "url": "source-reference", "source_id": "pl-8842731" },
  "status": "unvalidated"
}
```

The occurrence ID is `signal-event.{company}.{signal}.{YYYY-MM-DD}.{source-key}`, where `source-key` is the provider's record id when it has one, else a short hash of the source URL. Two consequences: the same signal firing twice in one day gets two distinct IDs, and **the ID is the dedupe key** — before appending, check whether the ID already exists in the file; appending only what's new is a pure ID comparison.

Chain: signal definition → signal occurrence → company → campaign → workflow.

## Derived files: attribution, and the mirror rule

Raw is immutable, derived is disposable — and a derived file must show its work. Every claim in a derived markdown file (`context.md`, `engagement.md`, `framework.md`, `signals.md`, org-chart files) carries an attribution tag:

- `[VERIFIED: source]` — grounded in a raw record or a live tool read; name the source.
- `[INFERRED: reasoning]` — a judgment call; name the reasoning.
- `[UNVERIFIABLE]` — stated but uncheckable; use sparingly.

`engagement.md` is the strictest case: it digests **instrumented state** (touches, sends, replies) that the CRM and sequencer own. It mirrors, it never owns — regenerate it from raw plus live reads; never hand-edit it, and never treat it as the source for a number the owning system can answer.

The empty template files carry their payload shape as HTML comments — section headings and guidance, invisible when rendered. The comments say what a filled file looks like; the empty-slot rule still holds: content comes from the user or from raw data, never from invention.

## Format separation

| Format   | Holds                                                          |
| -------- | -------------------------------------------------------------- |
| YAML     | Identification, status, bindings, links                        |
| Markdown | Knowledge, context, hypotheses, messaging, definitions         |
| JSONL    | Raw events, messages, entities, detected signal occurrences    |
| CSV      | Lists and membership (which companies belong to a campaign)    |

YAML is the linking protocol across the GTM context; workflows describe what happens across the linked assets. `companies.csv` carries membership only — `company_id, enrolled_at, status` where `status` is enrollment policy (`enrolled | paused | exited`). Step, timing, outcomes, and owner are state and live in the sequencer and the CRM.
