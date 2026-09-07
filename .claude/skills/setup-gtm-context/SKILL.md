---
name: setup-gtm-context
description: First-time setup of the GTM context. Use when the user says "set up my GTM context" or asks to initialize this repo against their tools.
---

Follow the rules in `CLAUDE.md` and the spec in `PROTOCOL.md`.

1. Check MCP connections: CRM, email, meeting recorder, sequencer, enrichment, search, intent data. List the tools each server actually exposes, not just the server names — that inventory is what signal detection and ETL get written against. Report what's connected and what's missing (missing ones are fine — degrade gracefully).
2. Interview the user: what they sell, who buys it (personas), common objections, main competitors.
3. Fill `knowledge-base/definition.md` and the subfolders (`product/`, `personas/`, `use-cases/`, `objections/`, `competitors/`) — one markdown file per item.
4. Set `knowledge-base.yaml` status to `active`.
5. Point the user to the next steps: "sync my companies", then "define my signals".
