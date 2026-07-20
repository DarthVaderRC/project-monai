#!/usr/bin/env python3
"""postToolUse: inject style + scoped-test reminder after matching file edits.

`afterFileEdit` cannot return context; this hook filters write tools that touched
paths matching pack.config `nudge.globs` and returns `additional_context`.
"""

from __future__ import annotations

import fnmatch
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from policy import (  # noqa: E402
    append_ledger,
    emit,
    load_pack_config,
    project_root,
    read_stdin_json,
)

DEFAULT_NUDGE = (
    "Cursor-kit nudge: you edited a transforms/tests file. Before handing off, run "
    "`./runtests.sh --ruff` and a scoped module test "
    "(e.g. `python -m tests.transforms.test_<name>`), and "
    "`bash docs/cursor-kit/scripts/check-deprecations.sh` for deprecated APIs."
)

# Keys whose presence signals an edit/write (vs a read) tool call.
_WRITE_KEYS = {"edits", "new_string", "contents", "code", "file_text", "new_str", "patch"}

# Repo-relative path candidates ending in .py (posix-ish).
_PATH_CANDIDATE = re.compile(
    r"(?:^|[\s\"'=])((?:\.?/?)?(?:monai|tests)/[A-Za-z0-9_./-]+\.py)",
    re.IGNORECASE,
)


def _looks_like_edit(tool_input: dict) -> bool:
    return any(k in tool_input for k in _WRITE_KEYS)


def _nudge_cfg(cfg: dict | None) -> tuple[list[str], str]:
    if not isinstance(cfg, dict):
        return [], DEFAULT_NUDGE
    nudge = cfg.get("nudge")
    if not isinstance(nudge, dict):
        return [], DEFAULT_NUDGE
    globs = [str(g) for g in (nudge.get("globs") or [])]
    message = str(nudge.get("message") or DEFAULT_NUDGE)
    return globs, message


def _path_matches(blob: str, globs: list[str]) -> bool:
    if not globs:
        return False
    candidates = [m.group(1).lstrip("./") for m in _PATH_CANDIDATE.finditer(blob)]
    # Also consider raw whitespace-separated tokens that look like paths.
    for token in blob.replace(",", " ").split():
        tok = token.strip("\"'").lstrip("./")
        if "/" in tok and tok.endswith(".py"):
            candidates.append(tok)
    for cand in candidates:
        for pat in globs:
            if fnmatch.fnmatch(cand, pat):
                return True
    return False


def main() -> int:
    try:
        payload = read_stdin_json()
        tool_input = payload.get("tool_input")
        if not isinstance(tool_input, dict):
            emit({})
            return 0
        cfg = load_pack_config(project_root())
        globs, nudge_msg = _nudge_cfg(cfg)
        if cfg is None:
            append_ledger("postToolUse", "pack_config_missing")
            emit({})
            return 0
        blob = " ".join(str(v) for v in tool_input.values())
        if _looks_like_edit(tool_input) and _path_matches(blob, globs):
            append_ledger("postToolUse", "nudge", tool=payload.get("tool_name"))
            emit({"additional_context": nudge_msg})
        else:
            emit({})
        return 0
    except Exception as exc:  # noqa: BLE001 — fail open
        print(f"post_edit_nudge hook error: {exc}", file=sys.stderr)
        emit({})
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
