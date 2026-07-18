#!/usr/bin/env python3
"""afterFileEdit: record agent file edits to the usage ledger (accounting only).

`afterFileEdit` accepts no output fields, so this hook only logs path + edit
count. The user-facing style/test nudge lives in `post_edit_nudge.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from policy import append_ledger, emit, read_stdin_json, rel_path  # noqa: E402


def main() -> int:
    try:
        payload = read_stdin_json()
        file_path = payload.get("file_path") or ""
        rel = rel_path(file_path) if file_path else ""
        edits = payload.get("edits") or []
        interesting = rel.startswith("monai/transforms/") or rel.startswith("tests/transforms/")
        append_ledger(
            "afterFileEdit",
            "transform_edit" if interesting else "edit",
            path=rel or file_path,
            edit_count=len(edits) if isinstance(edits, list) else None,
        )
        emit({})
        return 0
    except Exception as exc:  # noqa: BLE001 — fail open
        print(f"nudge_style_test hook error: {exc}", file=sys.stderr)
        emit({})
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
