# GTM Context Protocol

The source of truth for your GTM work: what you sell, your signals, your companies, your campaigns. A system you connect your agents to. Plug in your tools over MCP (CRM, email, meeting recorder, sequencer, enrichment). Any agent then reads this context, works in it, and adds to it.

## What this is

A template repo. Clone it once and it becomes your GTM context: your data fills it, your agents maintain it. "Protocol" means the rules that make every agent file things the same way. You don't need to read those rules. Your agent does. They live in [`CLAUDE.md`](CLAUDE.md) and [`PROTOCOL.md`](PROTOCOL.md).

## What you tweak

Everything is yours after cloning. In practice:

- **You write:** knowledge base content (product, personas, objections), signal definitions (what to watch, which provider), campaign strategy (hypothesis, voice, cadence).
- **Agents write:** company folders (context, research, raw data), the YAML record cards, signal occurrences.
- **Keep intact:** the folder structure and the IDs. That is what agents navigate by.

## What you can do with it

- **Connect your book of business.** Plug in your CRM, email, meeting recorder, and sequencer. Every company becomes a folder here.
- **Keep account context fresh.** Agents distill CRM history, meetings, and emails into one `context.md` per company and keep it updated.
- **Define your buying signals.** Write down the signals that matter once. Each signal names the provider that detects it. The signal harness in `orchestration/` reviews every occurrence per company.
- **Run campaigns.** Enroll companies into a campaign. The hypothesis, voice, and cadence live next to the list.
- **Create workflows.** Describe recurring jobs in `orchestration/`: daily company research, signal checks, CRM sync. Agents run them on a schedule. *(roadmap)*

## Prerequisites

- MCP connections to your GTM stack: at minimum your CRM (Attio, HubSpot, Pipedrive); ideally also email (Gmail, Outlook), meeting recorder (Granola, Gong), sequencer (Instantly, Apollo), and enrichment (Extruct, Clay)
- Claude Code, Codex, Cursor

## Quickstart

1. Clone and open:
   ```bash
   git clone https://github.com/extruct-ai/gtm-context-protocol.git
   cd gtm-context-protocol && claude
   ```
2. Connect your tools as MCP servers (`claude mcp add ...` or your claude.ai connectors).
3. Say **"set up my GTM context"**. The agent checks your connections, interviews you about your product and personas, and fills `knowledge-base/`.
4. Say **"sync my companies"**. The agent pulls every account from your CRM into a company folder and writes its `context.md`.
5. Say **"define my signals"**. Tell the agent which events mean buying intent for you. Each one becomes a definition in `knowledge-base/signals/`.
6. Say **"research my companies"**. The agent checks every company against your signals and logs what it finds in `research/`.
7. Open `companies/`. Your book of business is now files: context, signals, and research per company.

One-off additions work too. **"add {company} and research it"** onboards a single company. Useful for net-new targets that aren't in your CRM yet.

The setup routine and context rules live in [`CLAUDE.md`](CLAUDE.md), which Claude Code loads automatically. Any agent you connect already knows how to behave.

## Layout

```text
.
├── orchestration/
│   ├── workflows/          # one YAML per workflow: triggers, scope, steps
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

The `sample-*` assets are empty, pre-wired templates. To create an asset, copy one, rename it, and update the IDs in its manifest. Or just ask the agent, which does exactly that.

## How everything stays connected

Every company, campaign, and signal is a folder with one YAML record card. Think CRM object, but in a file. The card tells agents which files belong to the asset, what it's linked to, and which workflows touch it. Assets reference each other by stable ID (`company.acme`, `campaign.pe-rollups-eu`), never by file path. Renaming folders never breaks a workflow. There is no central registry to go stale. You'll rarely edit these cards by hand; agents maintain them.

Full spec (manifest shape, ID conventions, workflow references, signal occurrences): [`PROTOCOL.md`](PROTOCOL.md).
