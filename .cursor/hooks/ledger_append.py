#!/usr/bin/env python3
"""Append a usage ledger line (for skills / manual metering).

Usage:
  echo '{"event":"skill","decision":"start","skill":"triage-issues","persona":"PM"}' \\
    | python3 .cursor/hooks/ledger_append.py

Or pass fields as CLI kwargs-like JSON on stdin only.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from policy import append_ledger, emit, read_stdin_json  # noqa: E402


def main() -> int:
    try:
        payload = read_stdin_json()
        event = str(payload.pop("event", "manual"))
        decision = str(payload.pop("decision", "info"))
        append_ledger(event, decision, **payload)
        emit({"ok": True})
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"ledger_append error: {exc}", file=sys.stderr)
        emit({"ok": False, "error": str(exc)})
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
