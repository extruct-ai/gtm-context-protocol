# GTM Context Protocol

A file-based GTM context you embed in a project and drive with agents (Claude Code, workflows, scripts). Connect this folder to your tools — CRM, sequencer, meeting recorder, enrichment — and agents orchestrate research, enrichment, copy preparation, and signal monitoring on top of it. The goal is a structure you invite your future agents into, so they don't reinvent the wheel every session.

## What you can do with it

- **Keep account context fresh** — agents pull CRM history, meetings, and emails into one living `context.md` per company.
- **Monitor buying signals** — define the signals that matter once; agents detect and log occurrences per company on a schedule.
- **Run campaigns with researched personalization** — enroll companies into a campaign; the hypothesis, voice, and cadence live right next to the list.
- **Sync state back to your CRM** — your GTM context is the working copy; sync workflows push updates back. *(roadmap)*

## Prerequisites

- [Claude Code](https://claude.com/claude-code) — or any agent that can read files and call MCP tools
- MCP connections to your GTM stack: at minimum your CRM (Attio, HubSpot, Pipedrive); ideally also your meeting recorder (Granola, Gong), sequencer (Instantly, Apollo), and enrichment provider (Extruct, Clay)
- Nothing else — no database, no server. Everything is files and git.

## Quickstart

1. Clone and open:
   ```bash
   git clone https://github.com/extruct-ai/gtm-context-protocol.git
   cd gtm-context-protocol && claude
   ```
2. Connect your tools as MCP servers (`claude mcp add ...` or your claude.ai connectors).
3. Say **"set up my GTM context"** — the agent checks your connections, interviews you about product, personas, and signals, and fills `knowledge-base/`.
4. Say **"add {company} and research it"** — the agent creates the company folder, pulls your CRM history, and writes its context and signals.
5. Open `companies/{company}/context/context.md` — that's your first artifact.

The setup routine and context rules live in [`CLAUDE.md`](CLAUDE.md), which Claude Code loads automatically — any agent landing in this folder already knows how to behave.

## Layout

```text
.
├── orchestration/
│   ├── workflows/          # one YAML per workflow — triggers, scope, steps
│   ├── prompts/            # reusable agent instructions
│   └── scripts/            # deterministic code ops
│
├── knowledge-base/              # what you sell, to whom, and what to watch for
│   ├── knowledge-base.yaml
│   ├── definition.md
│   ├── signals/sample-signal/   # signal.yaml + definition.md
│   ├── product/  personas/  use-cases/
│   └── case-studies/  objections/  competitors/
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

The `sample-*` assets are empty, pre-wired templates: to create an asset, copy one, rename it, and update the IDs in its manifest — or just ask the agent, which does exactly that.

## How everything stays connected

Every company, campaign, and signal is a folder with one YAML "record card" — think CRM object, but in a file. The card tells agents which files belong to the asset, what it's linked to, and which workflows touch it. Assets reference each other by stable ID (`company.acme`, `campaign.pe-rollups-eu`), never by file path, so renaming folders never breaks a workflow — and there's no central registry to go stale. You'll rarely edit these cards by hand; agents maintain them.

Full spec — manifest shape, ID conventions, workflow references, signal occurrences: [`PROTOCOL.md`](PROTOCOL.md).
