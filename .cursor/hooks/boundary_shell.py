#!/usr/bin/env python3
"""beforeShellExecution: gate risky shell commands by boundary profile.

In `strict`, denies out-of-allowlist / dangerous commands; in `everyday`, allows
with warnings. Audits `gh` usage to the ledger when allowed.
Missing pack.config in strict → deny naming `.cursor/pack.config.json`.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from policy import (  # noqa: E402
    append_ledger,
    deny_message,
    emit,
    load_pack_config,
    missing_config_deny_msg,
    profile,
    project_root,
    read_stdin_json,
    shell_decision,
)


def main() -> int:
    try:
        payload = read_stdin_json()
        command = payload.get("command") or ""
        root = project_root()
        cfg = load_pack_config(root)
        mode = profile(cfg)
        permission, user_message, agent_message = shell_decision(command, mode, cfg)
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
        root = project_root()
        cfg = load_pack_config(root)
        mode = profile(cfg)
        msg = f"boundary_shell hook error: {exc}"
        print(msg, file=sys.stderr)
        if mode == "strict":
            deny = deny_message(cfg, root) if cfg else missing_config_deny_msg(root)
            emit({"permission": "deny", "user_message": deny, "agent_message": msg})
        else:
            emit({"permission": "allow"})
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
