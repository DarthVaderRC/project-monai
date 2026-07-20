#!/usr/bin/env python3
"""sessionStart: inject boundary profile env + kit context into the Agent session.

Reads `.cursor/boundary-profile` (or `MONAI_CURSOR_BOUNDARY`), sets
`MONAI_CURSOR_BOUNDARY` on the session env, and injects a short reminder of the
active profile plus available slash skills.
"""

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
            f"Skills: /triage-issues /plan-feature /critique-spec "
            f"/scaffold-transform /scaffold-loss /scaffold-metric /scaffold-network "
            f"/strengthen-tests /prep-for-ci /review-contribution."
        )
        emit({"env": {PROFILE_ENV: mode}, "additional_context": context})
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"session_start hook error: {exc}", file=sys.stderr)
        emit({})
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
