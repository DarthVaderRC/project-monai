#!/usr/bin/env python3
"""beforeReadFile boundary hook."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure sibling import works when Cursor invokes this script by path.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from policy import (  # noqa: E402
    DENY_MSG,
    WARN_MSG,
    append_ledger,
    emit,
    path_allowed,
    profile,
    read_stdin_json,
    rel_path,
)


def main() -> int:
    try:
        payload = read_stdin_json()
        file_path = payload.get("file_path") or ""
        mode = profile()
        rel = rel_path(file_path) if file_path else ""
        allowed = path_allowed(rel, mode) if rel else False

        if allowed:
            emit({"permission": "allow"})
            return 0

        if mode == "strict":
            append_ledger("beforeReadFile", "deny", path=rel or file_path)
            emit(
                {
                    "permission": "deny",
                    "user_message": DENY_MSG,
                    "agent_message": DENY_MSG,
                }
            )
            return 0

        append_ledger("beforeReadFile", "warn", path=rel or file_path)
        emit(
            {
                "permission": "allow",
                "user_message": WARN_MSG,
                "agent_message": WARN_MSG,
            }
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        mode = profile()
        msg = f"boundary_read hook error: {exc}"
        print(msg, file=sys.stderr)
        if mode == "strict":
            emit({"permission": "deny", "user_message": DENY_MSG, "agent_message": msg})
        else:
            emit({"permission": "allow"})
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
