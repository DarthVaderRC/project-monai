#!/usr/bin/env python3
"""subagentStart / subagentStop audit hook.

Demonstrates awareness of Cursor's subagent (Task tool) lifecycle: the kit
allows delegation (e.g. running /review as a background subagent) but records it
in the usage ledger so multi-role automation stays observable. Lightweight by
design — it audits and allows; it does not gate subagents in v1.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from policy import append_ledger, emit, read_stdin_json  # noqa: E402


def main() -> int:
    try:
        payload = read_stdin_json()
        event = payload.get("hook_event_name") or ""
        if event == "subagentStart":
            append_ledger(
                "subagentStart",
                "allow",
                subagent_type=payload.get("subagent_type"),
                task=(payload.get("task") or "")[:120],
            )
            emit({"permission": "allow"})
        else:  # subagentStop (or unknown -> just audit)
            modified = payload.get("modified_files") or []
            append_ledger(
                "subagentStop",
                payload.get("status") or "done",
                subagent_type=payload.get("subagent_type"),
                modified_files=len(modified) if isinstance(modified, list) else None,
                tool_calls=payload.get("tool_call_count"),
            )
            emit({})
        return 0
    except Exception as exc:  # noqa: BLE001 — fail open (audit only)
        print(f"subagent_audit hook error: {exc}", file=sys.stderr)
        emit({})
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
