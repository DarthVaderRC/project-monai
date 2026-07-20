#!/usr/bin/env python3
"""Thin wrapper — canonical script lives in platform-core/scripts/."""
from __future__ import annotations

import os
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WRAPPER_DIR = Path(__file__).resolve().parent
os.environ.setdefault("CURSOR_PROJECT_DIR", str(ROOT))

core = os.environ.get("CURSOR_PLATFORM_CORE", "").strip()
candidates = []
if core:
    candidates.append(Path(core))
candidates.extend(
    [
        ROOT.parent / "cursor" / "plugins" / "platform-core",
        Path.home() / ".cursor" / "plugins" / "local" / "platform-core",
    ]
)
target = None
for c in candidates:
    script = c / "scripts" / Path(__file__).name
    if script.is_file():
        target = script
        break
if target is None:
    sys.stderr.write(
        "ERROR: platform-core not found; set CURSOR_PLATFORM_CORE or fetch plugins "
        "(see PRODUCTIZATION.md CI note)\n"
    )
    raise SystemExit(1)

scripts_dir = str(target.parent)
sys.path = [scripts_dir] + [
    p for p in sys.path if Path(p).resolve() != WRAPPER_DIR.resolve()
]
sys.argv[0] = str(target)
runpy.run_path(str(target), run_name="__main__")
