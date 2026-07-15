#!/usr/bin/env python3
"""ledger-report.py — turn the raw usage ledger into a small dashboard.

Aggregates `.cursor/usage/ledger.jsonl` (append-only stage/persona metering
written by skills + hooks) into per-persona, per-stage, and decision tables.
Token economics are Cursor-estimated; this is stage/persona observability, not a
billing invoice.

Usage:
  python3 docs/cursor-kit/scripts/ledger-report.py [path-to-ledger.jsonl]
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


def _root() -> Path:
    return Path(__file__).resolve().parents[3]


def _fmt_table(title: str, counter: Counter, key_header: str) -> str:
    if not counter:
        return f"{title}\n  (none)\n"
    width = max(len(str(k)) for k in counter) + 2
    width = max(width, len(key_header) + 2)
    lines = [title, f"  {key_header.ljust(width)}count"]
    for key, count in counter.most_common():
        lines.append(f"  {str(key).ljust(width)}{count}")
    return "\n".join(lines) + "\n"


def main() -> int:
    ledger = Path(sys.argv[1]) if len(sys.argv) > 1 else _root() / ".cursor" / "usage" / "ledger.jsonl"
    if not ledger.is_file():
        print(f"No ledger at {ledger} (nothing to report yet).")
        return 0

    total = 0
    malformed = 0
    by_event: Counter = Counter()
    by_decision: Counter = Counter()
    by_persona: Counter = Counter()
    by_stage: Counter = Counter()
    by_skill: Counter = Counter()

    with ledger.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                malformed += 1
                continue
            total += 1
            by_event[rec.get("event", "?")] += 1
            by_decision[rec.get("decision", "?")] += 1
            if rec.get("persona"):
                by_persona[rec["persona"]] += 1
            if rec.get("stage"):
                by_stage[rec["stage"]] += 1
            if rec.get("skill"):
                by_skill[rec["skill"]] += 1

    denies = sum(v for k, v in by_decision.items() if "deny" in str(k))
    warns = sum(v for k, v in by_decision.items() if "warn" in str(k))
    oob = by_decision.get("attachment_out_of_bounds", 0)

    print("=" * 52)
    print("MONAI Cursor kit — usage ledger report")
    print(f"ledger: {ledger}")
    print("=" * 52)
    print(f"events: {total}   boundary denies: {denies}   warns: {warns}   out-of-bounds attachments: {oob}")
    if malformed:
        print(f"(skipped {malformed} malformed line(s))")
    print()
    print(_fmt_table("By persona (skill activity):", by_persona, "persona"))
    print(_fmt_table("By SDLC stage:", by_stage, "stage"))
    print(_fmt_table("By skill:", by_skill, "skill"))
    print(_fmt_table("By event source:", by_event, "event"))
    print(_fmt_table("By decision:", by_decision, "decision"))
    print("Note: token economics are Cursor-estimated; value is measured by ramp")
    print("time and first-PR defect rate, not by this file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
