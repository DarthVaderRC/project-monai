#!/usr/bin/env python3
"""afterFileEdit nudge: remind style + scoped tests for transforms/tests edits."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from policy import append_ledger, emit, read_stdin_json, rel_path  # noqa: E402

NUDGE = (
    "Cursor-kit nudge: after editing transforms/tests, run "
    "`./runtests.sh --ruff` and a scoped module test "
    "(e.g. `python -m tests.transforms.test_<name>`)."
)


def main() -> int:
    try:
        payload = read_stdin_json()
        file_path = payload.get("file_path") or ""
        rel = rel_path(file_path) if file_path else ""
        interesting = rel.startswith("monai/transforms/") or rel.startswith("tests/transforms/")
        append_ledger("afterFileEdit", "nudge" if interesting else "ok", path=rel or file_path)
        if interesting:
            emit(
                {
                    "user_message": NUDGE,
                    "agent_message": NUDGE,
                    "additional_context": NUDGE,
                }
            )
        else:
            emit({})
        return 0
    except Exception as exc:  # noqa: BLE001 — fail open
        print(f"nudge_style_test hook error: {exc}", file=sys.stderr)
        emit({})
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
