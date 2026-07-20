#!/usr/bin/env python3
"""beforeSubmitPrompt: block high-confidence anti-pattern prompts before send.

Can only allow or block (`{continue, user_message}`) — cannot inject context.
Patterns + guidance come from consumer `.cursor/pack.config.json` → prompt_coach.
Missing config → fail open (continue) with a ledger note.
"""

from __future__ import annotations

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


def _patterns(cfg: dict | None) -> list[tuple[re.Pattern[str], str]]:
    if not isinstance(cfg, dict):
        return []
    coach = cfg.get("prompt_coach")
    if not isinstance(coach, dict):
        return []
    raw = coach.get("patterns") or []
    out: list[tuple[re.Pattern[str], str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        pattern = item.get("pattern")
        guidance = item.get("guidance")
        if not pattern or not guidance:
            continue
        try:
            out.append((re.compile(str(pattern), re.IGNORECASE), str(guidance)))
        except re.error:
            continue
    return out


def main() -> int:
    try:
        payload = read_stdin_json()
        prompt = payload.get("prompt") or ""
        cfg = load_pack_config(project_root())
        if cfg is None:
            append_ledger("beforeSubmitPrompt", "pack_config_missing")
            emit({"continue": True})
            return 0
        for pattern, guidance in _patterns(cfg):
            if pattern.search(prompt):
                append_ledger("beforeSubmitPrompt", "blocked", reason=pattern.pattern)
                emit({"continue": False, "user_message": f"Cursor-kit coach: {guidance}"})
                return 0
        emit({"continue": True})
        return 0
    except Exception as exc:  # noqa: BLE001 — fail open (never block on error)
        print(f"prompt_coach hook error: {exc}", file=sys.stderr)
        emit({"continue": True})
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
