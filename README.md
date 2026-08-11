# GTM Context Protocol

The source of truth for your GTM work: what you sell, your signals, your companies, your campaigns. A system you connect your agents to. Plug in your tools over MCP (CRM, email, meeting recorder, sequencer, enrichment). Any agent then reads this context, works in it, and adds to it.

## What this is

A template repo. Clone it once and it becomes your GTM context: your data fills it, your agents maintain it. "Protocol" means the rules that make every agent file things the same way. You don't need to read those rules. Your agent does. They live in [`CLAUDE.md`](CLAUDE.md) and [`PROTOCOL.md`](PROTOCOL.md).

## How it works

1. **Connect your tools over MCP** — CRM, meeting recorder, sequencer, enrichment, email. Whatever you already run on.
2. **Your book of business becomes folders.** One folder per company, pulled from your CRM with its history attached.
3. **Each account gets a context file** — what the relationship is and what came out of it, with how deep you actually are in the account kept next to it in `engagement.md`. Both written from the raw data, not from memory.
4. **Research extends it.** Every company folder has a `research/` half you point an agent at when you want a question answered about that account.
5. **Qualification is yours to choose.** Name your framework — MEDDIC, MEDDPICC, BANT — and each account gets scored against it in `framework.md`.
6. **Signals are defined once and reused.** Each signal names the provider that detects it, so detection lives in the signal definition instead of being re-invented inside every workflow.
7. **Campaigns hang off the same context.** Plug in any sequencer and describe how campaigns get designed: hypothesis, voice, copy, cadence.

Everything here is meant to be edited. The structure is a starting shape, not a cage.

## What you tweak

Everything is yours after cloning. In practice:

- **You write:** knowledge base content (product, personas, use cases, case studies, objections, competitors), signal definitions (what to watch, which provider), campaign strategy (hypothesis, voice, cadence).
- **Agents write:** company folders (context, engagement, research, raw data), the YAML record cards, signal occurrences.
- **Keep intact:** the folder structure and the IDs. That is what agents navigate by.

The knowledge base is where your time actually pays off. Everything else an agent can rebuild from your tools; this part only exists if you put it there.

## Prerequisites

- MCP connections to your GTM stack: at minimum your CRM (Attio, HubSpot, Pipedrive); ideally also email (Gmail, Outlook), meeting recorder (Granola, Gong), sequencer (Instantly, Apollo), and enrichment (Extruct)
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

## Connecting your tools

Nothing is bundled. This repo names providers; your MCP connections supply them. Add them once:

```bash
claude mcp add extruct --transport http https://mcp.extruct.ai/mcp
claude mcp list
```

or add them as connectors in claude.ai. What you connect determines what the context can do:

| Category | Powers | Examples |
| -------- | ------ | -------- |
| **Enrichment** | Firmographics, contacts, emails, tech stack | Extruct, Apollo, People Data Labs, Crustdata, ContactOut, Hunter, Lusha, LeadMagic, RocketReach, FullEnrich, Prospeo, Wiza, Findymail |
| **Search & scraping** | Funding, launches, news, any public page | Exa, Serper, Firecrawl, Apify, Browserbase, DataForSEO |
| **Intent & hiring signals** | Job postings, tech adoption, ad audiences | PredictLeads, TheirStack, Sumble, BuiltWith, Bloomberry, Google / LinkedIn / Meta Ads Audiences |
| **CRM** | Account sync, contacts, activity history | Attio, HubSpot, Salesforce, Pipedrive |
| **Meetings** | Transcripts — what was actually said on calls | Gong, Granola, Fireflies.ai, Attention |
| **Email & messaging** | Thread history, replies, engagement | Gmail, Google Workspace, Outlook, Slack, Intercom |
| **Sequencing** | Campaign execution | Instantly, Outreach, Lemlist, Smartlead, HeyReach, Amplemarket, Nooks |
| **Warehouse** | Cross-company queries once files stop scaling | Snowflake, ClickHouse, BigQuery |

`provider` in a signal is just the name of the tool you connected — `apollo`, `exa`, `predictleads`, `attio`, `gong`. It is a free string, not a fixed enum: there are dozens of viable sources per category and no list would stay current. Name the one you actually connected.

**Signals** name a provider in their `detection` block, and that's the only place the binding lives. **Research** uses the same connections: `research my companies` walks every active signal through its declared provider, and for a one-off question on a single account you point the agent at whichever tool can answer it.

Connect what you have. Missing tools are fine — the agent reports what's connected at setup and works with the rest. A signal whose provider isn't connected simply doesn't run, and it says so rather than silently substituting a different source.

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

### Inside a company folder

| File | Holds |
| ---- | ----- |
| `context/context.md` | The narrative: where the relationship stands, what's been said, what's open. Rewritten from raw data whenever something changes |
| `context/raw/` | Everything raw, as it arrived: CRM events, email threads and call transcripts, extracted entities, and the account graph. Appended, never rewritten, so the history stays intact |
| `engagement.md` | Depth of penetration: who has been touched, how often, on which channel, with what response |
| `framework.md` | The account scored against your qualification framework. Empty until you name one — MEDDIC, MEDDPICC, BANT, your own |
| `org-chart/orgchart.md` | The buying unit: who decides, who blocks, who reports to whom |
| `org-chart/people/*.md` | One file per person — role, history with you, what they care about |
| `research/raw-signals.jsonl` | Every detection, appended with its source and provenance — noise included |
| `research/distillation.md` | The judgment record: which detections were junk and why, which were real, and how the real ones rank |
| `research/signals.md` | What survived: what fired, the evidence, a suggested angle |
| `company.yaml` | Record card: ID, status, domain, CRM id, components, links |
| `crm.yaml` | Pointer to the CRM record — provider, record id, last sync. It binds to the record; it never mirrors it |

Stage, owner, and last touch stay in the CRM. The repo holds policy, the CRM holds state.

### Inside a campaign folder

| File | Holds |
| ---- | ----- |
| `hypothesis.md` | Why this segment, why now — the bet, stated so it can be wrong |
| `voice.md` | How you sound: tone, register, what you never say |
| `text.md` | The actual copy — subject lines, bodies, variants |
| `cadence.md` | The sequence: steps, timing, channels, exit rules |
| `knowledge.md` | Which knowledge-base pieces this campaign leans on — personas, objections, proof |
| `companies.csv` | Membership by `company_id` |
| `campaign.yaml` | Record card, plus links to the knowledge base and the signals that feed it |

You write the hypothesis, voice, and cadence with the agent. Your sequencer takes it from there over MCP.

### Inside the knowledge base

This is the part worth doing by hand. `definition.md` states what you sell in one place; the rest is one markdown file per item:

| Folder | Holds |
| ------ | ----- |
| `product/` | What you sell, how it works, what it costs |
| `personas/` | Who buys, what they own, what they're measured on |
| `use-cases/` | The jobs it gets hired for, by segment or vertical |
| `case-studies/` | Proof — who bought, what changed, by how much |
| `objections/` | What you hear, and what actually answers it |
| `competitors/` | Who else is in the room and how you differ |
| `signals/` | One folder per signal: what it means, what evidence counts, which provider detects it |

Everything in here is true regardless of who you're talking to. Anything that's only true for one audience belongs in a campaign; anything true for one account belongs in that company's folder.

## Signals, end to end

A signal is one observable event that means someone might be ready to buy — a fund closed, a first RevOps hire, a new CTO, a tool swapped out. You define it once and every company gets checked against it.

**1. Define it.** `knowledge-base/signals/{name}/definition.md` says what the signal means and what evidence actually counts. This is a claim you can be wrong about, so write it that way.

**2. Connect a provider.** The `detection` block in `signal.yaml` names which of your connected tools goes looking, and what it looks for:

```yaml
detection:
  provider: predictleads   # name of a connected tool — apollo, exa, crustdata, attio, gong, …
  query: "announced a new fund OR closed fund"
```

`provider` names whichever tool you connected ([categories and examples above](#connecting-your-tools)); `query` is what to look for, in that tool's terms.

This is the point of the whole design: **detection lives in the signal, in one place** — never buried inside a workflow. Swap enrichment for web search later and everything that consumes the signal follows, with nothing else to edit. A signal with no provider doesn't run — the agent will ask you to finish the definition rather than improvise a source.

**3. Collect occurrences.** Every hit is appended to that company's `research/raw-signals.jsonl` — its own ID (`signal-event.acme.new-fund.2026-08-01`), which signal fired, what detected it, when, the source, and `status: unvalidated`. Append-only, so you keep the full detection history and can tell a signal that keeps firing from one that fired once.

**4. Cut the noise and rank the rest.** Detection is noisy: providers return coincidences, stale news, and the wrong company with a similar name. `research/distillation.md` is where those get thrown out and the survivors get ordered — it holds the judgment calls themselves: this detection was junk *because X*, this one is real, and this is why it outranks the others. Writing down the reasoning is the point. It's a record you can revisit and argue with, and it's how signal prioritization stays consistent across accounts instead of being re-decided from scratch every run. The raw log stays intact underneath, so a rejection can always be reopened.

**5. Keep what survives.** `research/signals.md` holds the real ones in priority order: what fired, the evidence, a suggested angle.

The chain runs: signal definition → occurrence → distillation → company → campaign. The definition is reusable, the occurrence is evidence with provenance attached.

## Orchestration

`orchestration/` is everything about how data gets in and how it gets processed:

- `workflows/` — one YAML per recurring job. A `trigger` (schedule, event, or manual), a `scope` naming the assets it touches, and `steps` that read, prompt, append, or call another workflow.
- `prompts/` — reusable agent instructions, so a research pass runs the same way every time.
- `scripts/` — deterministic operations that shouldn't be left to a model.

The point of this folder is autonomy: you finish a call, the transcript lands in the right company folder, the context updates, and what you learned works its way back into the knowledge base without you filing anything.

*Roadmap: the workflow format is defined, but no runner ships with this repo yet. Today you trigger a workflow by asking the agent to run it, or by wiring it to your own scheduler.*

## How everything stays connected

Every company, campaign, and signal is a folder with one YAML record card. Think CRM object, but in a file. The card tells agents which files belong to the asset, what it's linked to, and which workflows touch it. Assets reference each other by stable ID (`company.acme`, `campaign.pe-rollups-eu`), never by file path. Renaming folders never breaks a workflow. There is no central registry to go stale. You'll rarely edit these cards by hand; agents maintain them.

Full spec (manifest shape, ID conventions, workflow references, signal occurrences): [`PROTOCOL.md`](PROTOCOL.md).
