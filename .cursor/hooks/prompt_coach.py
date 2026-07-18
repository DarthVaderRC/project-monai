#!/usr/bin/env python3
"""beforeSubmitPrompt: block high-confidence anti-pattern prompts before send.

Can only allow or block (`{continue, user_message}`) — cannot inject context.
Blocks known "already exists" asks (e.g. SoftClipIntensity) with a pointer;
otherwise lets the prompt through.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from policy import append_ledger, emit, read_stdin_json  # noqa: E402

# (regex, guidance) — only high-confidence "already exists / don't do this" cases.
_ANTIPATTERNS: list[tuple[re.Pattern, str]] = [
    (
        re.compile(r"soft[\s_-]?clip", re.IGNORECASE),
        "Soft-clip intensity already exists in MONAI: use `ClipIntensityPercentiles` "
        "(with `sharpness_factor`) or the `soft_clip` util. Please rephrase around the "
        "existing API instead of adding `SoftClipIntensity`.",
    ),
]


def main() -> int:
    try:
        payload = read_stdin_json()
        prompt = payload.get("prompt") or ""
        for pattern, guidance in _ANTIPATTERNS:
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
