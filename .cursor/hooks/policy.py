#!/usr/bin/env python3
"""Shared boundary policy + usage ledger for MONAI Cursor kit hooks."""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PROFILE_ENV = "MONAI_CURSOR_BOUNDARY"
DEFAULT_PROFILE = "everyday"

STRICT_PREFIXES = (
    ".cursor/",
    "docs/cursor-kit/",
    "monai/transforms/",
    "tests/transforms/",
)

STRICT_FILES = frozenset(
    {
        "AGENTS.md",
        "CONTRIBUTING.md",
        "pyproject.toml",
        "setup.cfg",
        ".pre-commit-config.yaml",
        "runtests.sh",
        "requirements-dev.txt",
        "requirements.txt",
        "tests/test_utils.py",
        "tests/min_tests.py",
        "tests/__init__.py",
        "tests/lazy_transforms_utils.py",
    }
)

EVERYDAY_PREFIXES = (
    ".cursor/",
    "docs/",
    "monai/",
    "tests/",
    ".github/",
)

EVERYDAY_FILES = STRICT_FILES | frozenset(
    {
        "LICENSE",
        "README.md",
        "CODE_OF_CONDUCT.md",
        "CITATION.cff",
        "Dockerfile",
        "Dockerfile.slim",
    }
)

DENY_MSG = (
    "Blocked by MONAI_CURSOR_BOUNDARY=strict. Stay within transforms + kit paths "
    "(.cursor/, AGENTS.md, docs/cursor-kit/, monai/transforms/, tests/transforms/) "
    "or set MONAI_CURSOR_BOUNDARY=everyday. See AGENTS.md."
)

WARN_MSG = (
    "Warning: path/command is outside the everyday Cursor-kit allowlist. "
    "Prefer monai/, tests/, docs/, .cursor/. See AGENTS.md."
)


def profile() -> str:
    """Resolve boundary profile.

    Preference order (demo-friendly):
    1. `.cursor/boundary-profile` file contents (`strict`|`everyday`) — flip mid-session
    2. `MONAI_CURSOR_BOUNDARY` environment variable
    3. `everyday`
    """
    root = project_root()
    profile_file = root / ".cursor" / "boundary-profile"
    try:
        if profile_file.is_file():
            file_value = profile_file.read_text(encoding="utf-8").strip().splitlines()[0].strip().lower()
            if file_value in {"strict", "everyday"}:
                return file_value
    except OSError:
        pass
    value = os.environ.get(PROFILE_ENV, DEFAULT_PROFILE).strip().lower()
    return value if value in {"strict", "everyday"} else DEFAULT_PROFILE


def project_root() -> Path:
    env_root = os.environ.get("CURSOR_PROJECT_DIR") or os.environ.get("CLAUDE_PROJECT_DIR")
    if env_root:
        return Path(env_root).resolve()
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "AGENTS.md").exists() and (candidate / ".cursor").is_dir():
            return candidate
    return cwd


def rel_path(abs_path: str | Path, root: Path | None = None) -> str:
    root = root or project_root()
    path = Path(abs_path).resolve()
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def path_allowed(rel: str, mode: str) -> bool:
    rel = rel.lstrip("./")
    if rel.startswith("../") or rel.startswith("/"):
        return False
    files = STRICT_FILES if mode == "strict" else EVERYDAY_FILES
    prefixes = STRICT_PREFIXES if mode == "strict" else EVERYDAY_PREFIXES
    if rel in files:
        return True
    return any(rel == p.rstrip("/") or rel.startswith(p) for p in prefixes)


def append_ledger(event: str, decision: str, **extra: object) -> None:
    root = project_root()
    usage_dir = root / ".cursor" / "usage"
    try:
        usage_dir.mkdir(parents=True, exist_ok=True)
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "profile": profile(),
            "decision": decision,
            **extra,
        }
        with (usage_dir / "ledger.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError as exc:  # fail open for metering
        print(f"ledger append failed: {exc}", file=sys.stderr)


def read_stdin_json() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)


def emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload))
    sys.stdout.flush()


_SAFE_SHELL = re.compile(
    r"(^|[;&|]\s*)("
    r"\./runtests\.sh\b|"
    r"python3?\s+-m\s+tests\.transforms\b|"
    r"python3?\s+-m\s+pytest\b|"
    r"pytest\b|"
    r"ruff\b|"
    r"black\b|"
    r"isort\b|"
    r"pre-commit\b|"
    r"git\s+(status|diff|log|add|commit|branch|rev-parse|show)\b|"
    r"ls\b|"
    r"pwd\b|"
    r"echo\b|"
    r"head\b|"
    r"wc\b|"
    r"chmod\b"
    r")",
    re.IGNORECASE,
)

_GH_SHELL = re.compile(r"(^|[;&|]\s*)gh\b", re.IGNORECASE)

_RISKY_NET = re.compile(
    r"\b(curl|wget|npm|npx|pip3?\s+install|conda\s+install|git\s+clone)\b",
    re.IGNORECASE,
)

_DENIED_PATH_IN_CMD = re.compile(
    r"\b(monai/(?!transforms(?:/|\b))[a-z0-9_./-]+|"
    r"tests/(?!transforms(?:/|\b)|test_utils\.py|min_tests\.py|__init__\.py|"
    r"lazy_transforms_utils\.py)[a-z0-9_./-]+)\b",
    re.IGNORECASE,
)


def shell_decision(command: str, mode: str) -> tuple[str, str | None, str | None]:
    """Return (permission, user_message, agent_message)."""
    cmd = command or ""

    if mode == "everyday":
        if _GH_SHELL.search(cmd) or _SAFE_SHELL.search(cmd):
            return "allow", None, None
        if _RISKY_NET.search(cmd):
            append_ledger("beforeShellExecution", "warn", command=cmd, reason="risky_network")
            return "allow", WARN_MSG, WARN_MSG
        # Allow everyday work broadly; warn only on clear out-of-tree probes
        if re.search(r"\b(monai/networks|/etc/|/Users/)\b", cmd) and not path_hint_ok(cmd, "everyday"):
            append_ledger("beforeShellExecution", "warn", command=cmd, reason="outside_allowlist")
            return "allow", WARN_MSG, WARN_MSG
        return "allow", None, None

    # strict
    if _GH_SHELL.search(cmd):
        append_ledger("beforeShellExecution", "deny", command=cmd, reason="gh_in_strict")
        return "deny", DENY_MSG + " (gh disabled in strict; switch to everyday.)", DENY_MSG

    if _RISKY_NET.search(cmd):
        append_ledger("beforeShellExecution", "deny", command=cmd, reason="risky_network")
        return "deny", DENY_MSG, DENY_MSG

    if _DENIED_PATH_IN_CMD.search(cmd) and not _SAFE_SHELL.search(cmd):
        append_ledger("beforeShellExecution", "deny", command=cmd, reason="denied_path_in_cmd")
        return "deny", DENY_MSG, DENY_MSG

    if _SAFE_SHELL.search(cmd) or path_hint_ok(cmd, "strict"):
        return "allow", None, None

    append_ledger("beforeShellExecution", "deny", command=cmd, reason="not_allowlisted")
    return "deny", DENY_MSG, DENY_MSG


def path_hint_ok(cmd: str, mode: str) -> bool:
    """If command only mentions allowlisted relative paths, treat as ok."""
    mentions = re.findall(r"(?:^|[\s\"'=])((?:\.cursor|docs|monai|tests|AGENTS\.md)[^\s\"']*)", cmd)
    if not mentions:
        return False
    return all(path_allowed(m.lstrip("./"), mode) for m in mentions)
