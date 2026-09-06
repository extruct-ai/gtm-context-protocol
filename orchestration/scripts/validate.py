#!/usr/bin/env python3
"""Validate the GTM context against PROTOCOL.md.

Checks manifests (header fields, ID grammar, slug/folder agreement, uniqueness,
leftover sample IDs), the per-kind layout, campaign membership CSVs, signal
links, and raw JSONL files (parseable, occurrence ID grammar, in-file dedupe).

Stdlib only. Exit 0 when clean; exit 2 with findings on stderr — the exit code
Claude Code hooks surface back to the agent, and nonzero fails CI.
"""

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
STATUSES = {"draft", "active", "paused", "archived"}
ENROLLMENT_STATUSES = {"enrolled", "paused", "exited"}
SLUG = r"[a-z0-9][a-z0-9-]*"
OCCURRENCE_ID = re.compile(
    rf"^signal-event\.{SLUG}\.{SLUG}\.\d{{4}}-\d{{2}}-\d{{2}}\.[A-Za-z0-9_-]+$"
)

COMPANY_LAYOUT = [
    "company.yaml",
    "context/context.md",
    "context/raw/events.jsonl",
    "context/raw/messages.jsonl",
    "context/raw/entities.jsonl",
    "research/raw-signals.jsonl",
    "research/distillation.md",
    "research/signals.md",
    "org-chart/orgchart.md",
    "framework.md",
    "engagement.md",
]
CAMPAIGN_LAYOUT = [
    "campaign.yaml",
    "companies.csv",
    "hypothesis.md",
    "voice.md",
    "text.md",
    "cadence.md",
    "knowledge.md",
]
LEGACY_FILES = ["crm.yaml", "context/raw/graph.json"]

findings = []


def flag(path, message):
    findings.append(f"{path.relative_to(ROOT)}: {message}")


def read_fields(path):
    """Extract top-level scalar fields from a thin manifest (no YAML lib in stdlib)."""
    fields = {}
    for line in path.read_text().splitlines():
        m = re.match(r"^([A-Za-z_-]+):\s*([^#]*?)\s*(?:#.*)?$", line)
        if m:
            fields.setdefault(m.group(1), m.group(2).strip())
    return fields


def read_link_signals(path):
    """Collect `links: -> signals:` entries: inline [] or dash list."""
    text = path.read_text()
    block = re.search(r"^links:\n((?:[ \t]+.*\n?)*)", text, re.M)
    if not block:
        return []
    m = re.search(r"signals:\s*\[([^\]]*)\]", block.group(1))
    if m:
        return [s.strip() for s in m.group(1).split(",") if s.strip()]
    m = re.search(r"signals:\s*\n((?:[ \t]+-[ \t]*\S.*\n?)*)", block.group(1))
    if m:
        return [ln.strip().lstrip("-").strip() for ln in m.group(1).splitlines() if ln.strip()]
    return []


def check_manifest(path, kind, expected_id):
    fields = read_fields(path)
    for key in ("id", "kind", "status"):
        if not fields.get(key):
            flag(path, f"missing `{key}`")
    got_id = fields.get("id", "")
    if got_id and got_id != expected_id:
        flag(path, f"id `{got_id}` does not match folder-derived `{expected_id}`")
    if fields.get("kind") and fields["kind"] != kind:
        flag(path, f"kind `{fields['kind']}`, expected `{kind}`")
    if fields.get("status") and fields["status"] not in STATUSES:
        flag(path, f"status `{fields['status']}` not in {sorted(STATUSES)}")
    if "sample" in got_id and "sample-" not in str(path):
        flag(path, f"leftover sample id `{got_id}` outside a sample-* template")
    if re.search(r"^version:", path.read_text(), re.M):
        flag(path, "carries `version:` — dropped from the protocol")
    return got_id


def check_layout(folder, layout):
    for rel in layout:
        if not (folder / rel).exists():
            flag(folder / rel, "missing from the fixed layout")
    for rel in LEGACY_FILES:
        if (folder / rel).exists():
            flag(folder / rel, "legacy file — its contents moved into company.yaml / were dropped")


def check_jsonl(path, occurrence_ids=False):
    if not path.exists():
        return
    seen = set()
    for n, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            flag(path, f"line {n}: not valid JSON")
            continue
        if occurrence_ids:
            rid = record.get("id", "")
            if not OCCURRENCE_ID.match(rid):
                flag(path, f"line {n}: occurrence id `{rid}` breaks the "
                           "signal-event.{company}.{signal}.{date}.{source-key} grammar")
            if rid in seen:
                flag(path, f"line {n}: duplicate occurrence id `{rid}`")
            seen.add(rid)


def check_membership(path, company_ids):
    if not path.exists():
        return
    with path.open() as f:
        rows = list(csv.reader(f))
    if not rows or rows[0] != ["company_id", "enrolled_at", "status"]:
        flag(path, "header must be exactly `company_id,enrolled_at,status`")
        return
    for n, row in enumerate(rows[1:], 2):
        if not row:
            continue
        cid = row[0].strip()
        if cid and cid not in company_ids:
            flag(path, f"row {n}: `{cid}` resolves to no company folder")
        if len(row) >= 3 and row[2].strip() and row[2].strip() not in ENROLLMENT_STATUSES:
            flag(path, f"row {n}: status `{row[2].strip()}` not in {sorted(ENROLLMENT_STATUSES)}")


def main():
    ids = {}

    def register(asset_id, path):
        if asset_id in ids:
            flag(path, f"duplicate id `{asset_id}` (also {ids[asset_id].relative_to(ROOT)})")
        elif asset_id:
            ids[asset_id] = path

    company_ids, signal_ids = set(), set()

    for folder in sorted((ROOT / "companies").glob("*/")):
        check_layout(folder, COMPANY_LAYOUT)
        manifest = folder / "company.yaml"
        if manifest.exists():
            register(check_manifest(manifest, "company", f"company.{folder.name}"), manifest)
        company_ids.add(f"company.{folder.name}")
        for raw in (folder / "context" / "raw").glob("*.jsonl"):
            check_jsonl(raw)
        check_jsonl(folder / "research" / "raw-signals.jsonl", occurrence_ids=True)

    for folder in sorted((ROOT / "knowledge-base" / "signals").glob("*/")):
        manifest = folder / "signal.yaml"
        if manifest.exists():
            register(check_manifest(manifest, "signal", f"signal.{folder.name}"), manifest)
        else:
            flag(manifest, "missing")
        signal_ids.add(f"signal.{folder.name}")

    kb = ROOT / "knowledge-base" / "knowledge-base.yaml"
    if kb.exists():
        register(check_manifest(kb, "knowledge-base", "kb"), kb)

    for folder in sorted((ROOT / "campaigns").glob("*/")):
        check_layout(folder, CAMPAIGN_LAYOUT)
        manifest = folder / "campaign.yaml"
        if manifest.exists():
            register(check_manifest(manifest, "campaign", f"campaign.{folder.name}"), manifest)
            for sid in read_link_signals(manifest):
                if sid not in signal_ids:
                    flag(manifest, f"links.signals `{sid}` resolves to no signal folder")
        check_membership(folder / "companies.csv", company_ids)

    for wf in sorted((ROOT / "orchestration" / "workflows").glob("*.yaml")):
        register(check_manifest(wf, "workflow", f"workflow.{wf.stem}"), wf)

    if findings:
        print(f"{len(findings)} finding(s):", file=sys.stderr)
        for f in findings:
            print(f"  - {f}", file=sys.stderr)
        return 2
    print("gtm-context: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
