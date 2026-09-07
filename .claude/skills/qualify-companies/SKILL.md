---
name: qualify-companies
description: Score accounts against the qualification framework. Use when the user says "qualify my companies" or asks for MEDDIC/MEDDPICC/BANT scoring.
---

Follow the rules in `CLAUDE.md` and the spec in `PROTOCOL.md`.

1. Check which framework is named in `knowledge-base/definition.md`. If none, ask the user (MEDDIC, MEDDPICC, BANT, custom) and record it there — never pick one silently.
2. For each company in scope: score the account into `framework.md` from `context/raw/` and CRM history, every score tagged `[VERIFIED:]`/`[INFERRED:]`. A criterion the data can't answer stays empty — a gap is a finding.
3. Refresh `engagement.md` (the derived digest) alongside.
4. Report back: strongest accounts first, and the criteria most often unknown — that list is discovery homework.
