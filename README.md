# GTM Context Protocol

A file-based GTM context you embed in a project and drive with agents (Claude Code, workflows, scripts). Connect this folder to your tools — CRM, email, meeting recorder, sequencer, enrichment — and agents run research, enrichment, copy, and signals on top of it. The goal is a structure you invite your future agents into, so they don't reinvent the wheel every session.

## What you can do with it

- **Connect your book of business** — plug in your CRM, email, meeting recorder, and sequencer; every company becomes a folder here.
- **Keep account context fresh** — agents distill that history into one living `context.md` per company and keep it updated.
- **Define your buying signals** — write down the signals that matter once; every occurrence detected per company gets reviewed by your signal harness here.
- **Run campaigns with researched personalization** — enroll companies into a campaign; the hypothesis, voice, and cadence live right next to the list.
- **Stay bound to your CRM without mirroring it** — the repo holds policy (who to touch, how); your CRM keeps state (stage, owner, last touch); sync workflows keep the two in step. *(roadmap)*

## Prerequisites

- [Claude Code](https://claude.com/claude-code) — or any agent that can read files and call MCP tools
- MCP connections to your GTM stack: at minimum your CRM (Attio, HubSpot, Pipedrive); ideally also email (Gmail, Outlook), meeting recorder (Granola, Gong), sequencer (Instantly, Apollo), and enrichment (Extruct, Clay)
- Nothing else — no database, no server. Everything is files and git.

## Quickstart

1. Clone and open:
   ```bash
   git clone https://github.com/extruct-ai/gtm-context-protocol.git
   cd gtm-context-protocol && claude
   ```
2. Connect your tools as MCP servers (`claude mcp add ...` or your claude.ai connectors).
3. Say **"set up my GTM context"** — the agent checks your connections, interviews you about product, personas, and signals, and fills `knowledge-base/`.
4. Say **"sync my companies"** — the agent pulls every account from your CRM into a company folder and writes its `context.md`.
5. Open `companies/` — your book of business as files, one researched context per company.

One-off additions work too: **"add {company} and research it"** onboards a single company — useful for net-new targets that aren't in your CRM yet.

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
