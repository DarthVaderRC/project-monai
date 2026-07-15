#!/usr/bin/env python3
"""sessionStart: inject MONAI_CURSOR_BOUNDARY from .cursor/boundary-profile."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from policy import PROFILE_ENV, append_ledger, emit, profile  # noqa: E402


def main() -> int:
    try:
        mode = profile()
        append_ledger("sessionStart", "ok", profile_injected=mode)
        context = (
            f"MONAI Cursor kit active. Boundary profile: {mode} "
            f"(strict = deny reads/shell outside transforms + kit paths; "
            f"everyday = warn only). Flip via `.cursor/boundary-profile`. "
            f"Skills: /triage-issues /plan-feature /scaffold-transform "
            f"/strengthen-tests /prep-for-ci /review."
        )
        emit({"env": {PROFILE_ENV: mode}, "additional_context": context})
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"session_start hook error: {exc}", file=sys.stderr)
        emit({})
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
