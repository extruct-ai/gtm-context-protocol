# Protocol Specification

The full spec behind the GTM context. Read [`README.md`](README.md) first for the human overview; this file is for implementers and agents.

## Core model

- Every **orchestratable asset** (company, campaign, signal, knowledge base, workflow) has a **stable ID**.
- Every asset folder describes itself through a **YAML manifest**: its files (components), relationships (links), and workflows (orchestration).
- Files inside an asset get **component IDs** in that manifest.
- Workflows reference **asset IDs, never paths** — paths resolve through the manifest.
- There is **no central registry**. Each asset is self-describing; a global index would only duplicate it and go stale.

## Folder semantics

Structure says where things *can* go; this section says what each folder *means*. Each is defined by the question it answers and by what makes it change:

| Folder | Question it answers | Changes when |
| ------ | ------------------- | ------------ |
| `knowledge-base/` | What is true regardless of who we're talking to — product, ICP, pricing, competitors, signal definitions | The world changes |
| `companies/` | What we know about, and have done with, one specific account | That account's world or our relationship changes |
| `campaigns/` | What we do to a specific population — cadence, text, membership | Strategy changes |
| `orchestration/` | What runs, when, and what it's allowed to write | The process changes |

CRM state is not a folder, because **the repo holds policy and the CRM holds state**. State answers *where is this person* — stage, owner, last touch. Policy answers *what are we allowed to do about them* — cadence, voice, membership. The two drift at completely different rates and have different owners; most CRM tooling fails by conflating them. So `companies/{name}/crm.yaml` **binds** a company to its CRM record (provider, record id, sync timestamp) — it never mirrors it.

### The boundary test

Before placing a fact, ask: **if this fact changed, what else would have to change?**

- A price change must touch nothing in a campaign → pricing lives in the knowledge base.
- A touch-cap change must touch nothing in the knowledge base → cadence lives in the campaign.
- If the answer crosses a folder boundary, the fact is in the wrong folder.

Two corollaries:

- **Shared by many campaigns ≠ knowledge.** If four campaigns use the same cadence, it is still tactics: it stays at campaign level, duplicated. Only facts that hold regardless of audience get hoisted into the knowledge base. Painful duplication is a signal to design a new asset kind — never to pollute the KB.
- **Empty slots are questions, not invitations.** A template slot with no content (`voice.md`, `cadence.md`) means *not decided yet* — the asset stays `draft`. Filling a slot requires input from a human or evidence from raw data, never invention.

## Common YAML protocol

Every asset manifest follows the same shape:

```yaml
id:              # stable identifier — survives renames
kind:            # company | campaign | signal | knowledge-base | workflow
name:            # human-readable
version:
status:          # draft | active | paused | archived

components:      # files belonging to the asset, each with its own id + path + format
links:           # relationships to other assets, by ID
orchestration:   # workflows that create, update, or consume the asset
```

ID conventions:

```text
kb                                       # the knowledge base of the GTM context
signal.new-fund                          # signal
company.acme                             # company
campaign.pe-rollups-eu                   # campaign
workflow.daily-company-research          # workflow

campaign.pe-rollups-eu.hypothesis        # component ID — a file inside an asset
company.acme.context                     # lets workflows target one part of an asset
```

IDs are permanent: renaming a directory or file updates the `path` in the manifest, never the `id`.

## Workflows reference IDs, not paths

```yaml
steps:
  - id: load-company-context
    action: read          # read | prompt | append | workflow
    assets:
      - company.{company_id}.context
```

The path behind `company.acme.context` is resolved through `company.yaml`. Renaming a directory never breaks a workflow. Same rule in `companies.csv` — a campaign stores `company.acme`, not a path.

## Signal definitions vs. occurrences

A signal definition declares its own detection. The `detection` block in `signal.yaml` names the provider (which connected tool checks it) and the query:

```yaml
detection:
  provider: web-search      # extruct | apollo | web-search | crm | email | meetings
  query: "announced a new fund OR closed fund"
```

Workflows read this block instead of hardcoding sources. One signal, one place to change how it's detected.

`signal.new-fund` is the reusable **definition** (an asset).
`signal-event.acme.new-fund.2026-08-01` is one detected **occurrence** — a row in the company's `raw-signals.jsonl`:

```json
{
  "id": "signal-event.acme.new-fund.2026-08-01",
  "kind": "signal-occurrence",
  "signal_id": "signal.new-fund",
  "company_id": "company.acme",
  "detected_by": "workflow.daily-company-research",
  "detected_at": "2026-08-01T10:30:00Z",
  "source": { "type": "company-announcement", "url": "source-reference" },
  "status": "unvalidated"
}
```

Chain: signal definition → signal occurrence → company → campaign → workflow.

## Format separation

| Format   | Holds                                                          |
| -------- | -------------------------------------------------------------- |
| YAML     | Identification, components, relationships, orchestration       |
| Markdown | Knowledge, context, hypotheses, messaging, definitions         |
| JSONL    | Raw events, messages, entities, detected signal occurrences    |
| CSV      | Lists and membership (which companies belong to a campaign)    |

YAML is the linking protocol across the GTM context; workflows describe what happens across the linked assets.
