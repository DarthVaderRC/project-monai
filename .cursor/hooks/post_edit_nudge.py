#!/usr/bin/env python3
"""postToolUse nudge: surface style + scoped-test reminder after transform edits.

`afterFileEdit` cannot return context to the agent, but `postToolUse` supports
`additional_context`. This hook fires after any tool, filters to file-editing
tools that touched `monai/transforms/**` or `tests/transforms/**`, and injects a
short reminder to run the CI-equivalent checks. Reads (no write payload) and
non-transform edits are ignored.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from policy import append_ledger, emit, read_stdin_json  # noqa: E402

NUDGE = (
    "Cursor-kit nudge: you edited a transforms/tests file. Before handing off, run "
    "`./runtests.sh --ruff` and a scoped module test "
    "(e.g. `python -m tests.transforms.test_<name>`), and "
    "`bash docs/cursor-kit/scripts/check-deprecations.sh` for deprecated APIs."
)

# Keys whose presence signals an edit/write (vs a read) tool call.
_WRITE_KEYS = {"edits", "new_string", "contents", "code", "file_text", "new_str", "patch"}

_TRANSFORM_PATH = re.compile(r"(monai/transforms/|tests/transforms/)[A-Za-z0-9_./-]+\.py")


def _looks_like_edit(tool_input: dict) -> bool:
    return any(k in tool_input for k in _WRITE_KEYS)


def main() -> int:
    try:
        payload = read_stdin_json()
        tool_input = payload.get("tool_input")
        if not isinstance(tool_input, dict):
            emit({})
            return 0
        blob = " ".join(str(v) for v in tool_input.values())
        if _looks_like_edit(tool_input) and _TRANSFORM_PATH.search(blob):
            append_ledger("postToolUse", "nudge", tool=payload.get("tool_name"))
            emit({"additional_context": NUDGE})
        else:
            emit({})
        return 0
    except Exception as exc:  # noqa: BLE001 — fail open
        print(f"post_edit_nudge hook error: {exc}", file=sys.stderr)
        emit({})
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
