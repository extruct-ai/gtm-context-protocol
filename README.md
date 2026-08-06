# GTM Workspace — CRM Context (v0.4)

A file-based GTM workspace designed to be embedded in another project and driven by agents (Claude Code, workflows, scripts). Everything is plain files: YAML for structure, Markdown for knowledge, JSONL for raw data, CSV for membership.

Core model:

- Every **orchestratable asset** (company, campaign, signal, knowledge base, workflow) has a **stable ID**.
- Every asset folder describes itself through a **YAML manifest**: its files (components), relationships (links), and workflows (orchestration).
- Files inside an asset get **component IDs** in that manifest.
- Workflows reference **asset IDs, never paths** — paths resolve through the manifest.
- There is **no central registry**. Each asset is self-describing; a global index would only duplicate it and go stale.

## Layout

```text
.
├── orchestration/
│   ├── workflows/          # one YAML per workflow — triggers, scope, steps
│   ├── prompts/            # reusable agent instructions (generic for now)
│   └── scripts/            # deterministic code ops (generic for now)
│
├── knowledge-base/
│   └── sample-knowledge-base/
│       ├── knowledge-base.yaml
│       ├── definition.md
│       ├── signals/sample-signal/   # signal.yaml + definition.md
│       ├── product/  personas/  use-cases/
│       └── case-studies/  objections/  competitors/
│
├── companies/
│   └── sample-company/
│       ├── company.yaml
│       ├── context/        # context.md + raw/ (events, messages, entities, graph)
│       ├── research/       # signals.md, distillation.md, raw-signals.jsonl
│       ├── org-chart/      # orgchart.md + people/ (one .md per person)
│       ├── framework.md
│       ├── engagement.md
│       └── crm.yaml
│
└── campaigns/
    └── sample-campaign/
        ├── campaign.yaml
        ├── companies.csv   # membership by company_id
        ├── hypothesis.md  voice.md  text.md
        ├── cadence.md  knowledge.md
```

The repo root is the workspace. The `sample-*` folders (`companies/sample-company`, `campaigns/sample-campaign`, `knowledge-base/sample-knowledge-base`, `orchestration/workflows/sample-workflow.yaml`) are empty, pre-wired templates: to create an asset, copy one, rename it, and update the IDs in its manifest.

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
kb.private-equity                        # knowledge base
signal.private-equity.new-fund           # signal (namespaced by its KB)
company.acme                             # company
campaign.pe-rollups-eu                   # campaign
workflow.daily-company-research          # workflow

campaign.pe-rollups-eu.hypothesis        # component ID — a file inside an asset
company.acme.context                     # lets workflows target one part of an asset
```

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

`signal.private-equity.new-fund` is the reusable **definition** (an asset).
`signal-event.acme.new-fund.2026-08-01` is one detected **occurrence** — a row in the company's `raw-signals.jsonl`:

```json
{
  "id": "signal-event.acme.new-fund.2026-08-01",
  "kind": "signal-occurrence",
  "signal_id": "signal.private-equity.new-fund",
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

YAML is the linking protocol across the workspace; workflows describe what happens across the linked assets.
