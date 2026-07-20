#!/usr/bin/env python3
"""beforeReadFile: enforce pack.config allowlists on file reads.

Missing pack.config in strict → deny naming `.cursor/pack.config.json`.
In everyday, allow with a warn that names the missing path.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure sibling import works when Cursor invokes this script by path.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from policy import (  # noqa: E402
    append_ledger,
    deny_message,
    emit,
    load_pack_config,
    missing_config_deny_msg,
    path_allowed,
    profile,
    project_root,
    read_stdin_json,
    rel_path,
    warn_message,
)


def audit_attachments(payload: dict, mode: str, cfg: dict | None) -> None:
    """Log out-of-bounds context attachments (@-mentioned files / rules).

    Honesty note: `beforeReadFile` returns a single permission for `file_path`.
    Attachments are already-included prompt context; the hook can *observe* them
    (and we log out-of-bounds ones) but cannot retroactively strip them. This is
    a documented boundary limitation, not silent enforcement.
    """
    attachments = payload.get("attachments")
    if not isinstance(attachments, list):
        return
    for att in attachments:
        if not isinstance(att, dict):
            continue
        att_path = att.get("file_path") or ""
        if not att_path:
            continue
        att_rel = rel_path(att_path)
        if not path_allowed(att_rel, mode, cfg):
            append_ledger(
                "beforeReadFile",
                "attachment_out_of_bounds",
                path=att_rel,
                attachment_type=att.get("type"),
            )


def main() -> int:
    try:
        payload = read_stdin_json()
        file_path = payload.get("file_path") or ""
        root = project_root()
        cfg = load_pack_config(root)
        mode = profile(cfg)
        rel = rel_path(file_path, root) if file_path else ""

        if cfg is None:
            append_ledger("beforeReadFile", "pack_config_missing", path=rel or file_path)
            if mode == "strict":
                msg = missing_config_deny_msg(root)
                emit(
                    {
                        "permission": "deny",
                        "user_message": msg,
                        "agent_message": msg,
                    }
                )
                return 0
            msg = warn_message(None) + f" ({missing_config_deny_msg(root)})"
            emit(
                {
                    "permission": "allow",
                    "user_message": msg,
                    "agent_message": msg,
                }
            )
            return 0

        audit_attachments(payload, mode, cfg)
        allowed = path_allowed(rel, mode, cfg) if rel else False

        if allowed:
            emit({"permission": "allow"})
            return 0

        if mode == "strict":
            msg = deny_message(cfg, root)
            append_ledger("beforeReadFile", "deny", path=rel or file_path)
            emit(
                {
                    "permission": "deny",
                    "user_message": msg,
                    "agent_message": msg,
                }
            )
            return 0

        msg = warn_message(cfg)
        append_ledger("beforeReadFile", "warn", path=rel or file_path)
        emit(
            {
                "permission": "allow",
                "user_message": msg,
                "agent_message": msg,
            }
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        root = project_root()
        cfg = load_pack_config(root)
        mode = profile(cfg)
        msg = f"boundary_read hook error: {exc}"
        print(msg, file=sys.stderr)
        if mode == "strict":
            deny = deny_message(cfg, root) if cfg else missing_config_deny_msg(root)
            emit({"permission": "deny", "user_message": deny, "agent_message": msg})
        else:
            emit({"permission": "allow"})
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
