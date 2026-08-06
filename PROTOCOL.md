# Protocol Specification

The full spec behind the workspace. Read [`README.md`](README.md) first for the human overview; this file is for implementers and agents.

## Core model

- Every **orchestratable asset** (company, campaign, signal, knowledge base, workflow) has a **stable ID**.
- Every asset folder describes itself through a **YAML manifest**: its files (components), relationships (links), and workflows (orchestration).
- Files inside an asset get **component IDs** in that manifest.
- Workflows reference **asset IDs, never paths** — paths resolve through the manifest.
- There is **no central registry**. Each asset is self-describing; a global index would only duplicate it and go stale.

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
kb                                       # the workspace knowledge base
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

YAML is the linking protocol across the workspace; workflows describe what happens across the linked assets.
