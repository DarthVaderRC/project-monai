#!/usr/bin/env python3
"""beforeShellExecution: gate risky shell commands by boundary profile.

In `strict`, denies out-of-allowlist / dangerous commands; in `everyday`, allows
with warnings. Audits `gh` usage to the ledger when allowed.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from policy import append_ledger, emit, profile, read_stdin_json, shell_decision  # noqa: E402
from policy import DENY_MSG  # noqa: E402


def main() -> int:
    try:
        payload = read_stdin_json()
        command = payload.get("command") or ""
        mode = profile()
        permission, user_message, agent_message = shell_decision(command, mode)
        out: dict = {"permission": permission}
        if user_message:
            out["user_message"] = user_message
        if agent_message:
            out["agent_message"] = agent_message
        if permission == "allow" and user_message is None:
            # successful allow — optional audit for gh under everyday
            if "gh " in command or command.strip().startswith("gh"):
                append_ledger("beforeShellExecution", "allow", command=command, reason="gh")
        emit(out)
        return 0
    except Exception as exc:  # noqa: BLE001
        mode = profile()
        msg = f"boundary_shell hook error: {exc}"
        print(msg, file=sys.stderr)
        if mode == "strict":
            emit({"permission": "deny", "user_message": DENY_MSG, "agent_message": msg})
        else:
            emit({"permission": "allow"})
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
