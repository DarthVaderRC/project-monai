#!/usr/bin/env python3
"""Shared policy helpers for kit hooks: profiles, allowlists, ledger, emit.

Not a Cursor hook itself — imported by the scripts registered in hooks.json.
Owns path/shell decisions, profile resolution, and ledger append/JSON emit.

Allowlists and boundary copy come from the consumer `.cursor/pack.config.json`
instance (never hardcoded library prefixes here as the SSOT).
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_PROFILE = "everyday"
GENERIC_PROFILE_ENV = "CURSOR_ONBOARDING_BOUNDARY"
PACK_CONFIG_ENV = "CURSOR_ONBOARDING_PACK_CONFIG"
PACK_CONFIG_REL = ".cursor/pack.config.json"


def project_root() -> Path:
    env_root = os.environ.get("CURSOR_PROJECT_DIR") or os.environ.get("CLAUDE_PROJECT_DIR")
    if env_root:
        return Path(env_root).resolve()
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "AGENTS.md").exists() and (candidate / ".cursor").is_dir():
            return candidate
    return cwd


def pack_config_path(root: Path | None = None) -> Path:
    root = root or project_root()
    override = os.environ.get(PACK_CONFIG_ENV, "").strip()
    if override:
        return Path(override).resolve()
    return (root / PACK_CONFIG_REL).resolve()


def load_pack_config(root: Path | None = None) -> dict | None:
    """Load consumer pack.config.json. Returns None if missing/unreadable."""
    path = pack_config_path(root)
    try:
        if not path.is_file():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def missing_config_deny_msg(root: Path | None = None) -> str:
    root = root or project_root()
    missing = root / PACK_CONFIG_REL
    return (
        f"pack.config unresolved — missing {missing.as_posix()} "
        "(copy from pack example)"
    )


def profile(cfg: dict | None = None) -> str:
    """Resolve boundary profile.

    Preference order (session-friendly):
    1. `.cursor/boundary-profile` file contents (`strict`|`everyday`) — flip mid-session
    2. Env named by pack.config `profile_env` (or generic default)
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

    if cfg is None:
        cfg = load_pack_config(root)
    env_name = GENERIC_PROFILE_ENV
    if isinstance(cfg, dict):
        env_name = str(cfg.get("profile_env") or GENERIC_PROFILE_ENV)
    value = os.environ.get(env_name, DEFAULT_PROFILE).strip().lower()
    return value if value in {"strict", "everyday"} else DEFAULT_PROFILE


def rel_path(abs_path: str | Path, root: Path | None = None) -> str:
    root = root or project_root()
    path = Path(abs_path).resolve()
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def path_allowed(rel: str, mode: str, cfg: dict | None = None) -> bool:
    """Allowlist check using prefixes/files from pack.config for the given mode."""
    # Strip leading "./" only (not lstrip("./") — that also eats the "." in ".cursor/").
    while rel.startswith("./"):
        rel = rel[2:]
    if not rel or rel.startswith("/") or rel.startswith("../"):
        return False
    # Reject traversal even when prefixed by an allowlisted directory.
    if ".." in rel.split("/"):
        return False

    if cfg is None:
        cfg = load_pack_config()
    if not isinstance(cfg, dict):
        return False

    section = cfg.get(mode) if mode in {"strict", "everyday"} else None
    if not isinstance(section, dict):
        return False

    files = {str(f) for f in (section.get("files") or [])}
    prefixes = [str(p) for p in (section.get("prefixes") or [])]

    if rel in files:
        return True
    return any(rel == p.rstrip("/") or rel.startswith(p) for p in prefixes)


def deny_message(cfg: dict | None = None, root: Path | None = None) -> str:
    if cfg is None:
        cfg = load_pack_config(root)
    if not isinstance(cfg, dict):
        return missing_config_deny_msg(root)
    msg = cfg.get("deny_msg")
    return str(msg) if msg else missing_config_deny_msg(root)


def warn_message(cfg: dict | None = None) -> str:
    if cfg is None:
        cfg = load_pack_config()
    if isinstance(cfg, dict) and cfg.get("warn_msg"):
        return str(cfg["warn_msg"])
    return "Warning: outside everyday allowlist (pack.config)."


# Lazy module attrs so `from policy import DENY_MSG` still resolves at access time.
def __getattr__(name: str):  # noqa: ANN001
    if name == "DENY_MSG":
        return deny_message()
    if name == "WARN_MSG":
        return warn_message()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


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


def shell_decision(command: str, mode: str, cfg: dict | None = None) -> tuple[str, str | None, str | None]:
    """Return (permission, user_message, agent_message)."""
    if cfg is None:
        cfg = load_pack_config()
    deny = deny_message(cfg)
    warn = warn_message(cfg)
    cmd = command or ""

    if cfg is None:
        if mode == "strict":
            append_ledger("beforeShellExecution", "pack_config_missing", command=cmd)
            return "deny", deny, deny
        append_ledger("beforeShellExecution", "pack_config_missing", command=cmd)
        return "allow", warn + f" ({deny})", warn + f" ({deny})"

    if mode == "everyday":
        if _GH_SHELL.search(cmd) or _SAFE_SHELL.search(cmd):
            return "allow", None, None
        if _RISKY_NET.search(cmd):
            append_ledger("beforeShellExecution", "warn", command=cmd, reason="risky_network")
            return "allow", warn, warn
        # Allow everyday work broadly; warn only on clear out-of-tree probes
        if re.search(r"\b(monai/networks|/etc/|/Users/)\b", cmd) and not path_hint_ok(cmd, "everyday", cfg):
            append_ledger("beforeShellExecution", "warn", command=cmd, reason="outside_allowlist")
            return "allow", warn, warn
        return "allow", None, None

    # strict
    if _GH_SHELL.search(cmd):
        append_ledger("beforeShellExecution", "deny", command=cmd, reason="gh_in_strict")
        return "deny", deny + " (gh disabled in strict; switch to everyday.)", deny

    if _RISKY_NET.search(cmd):
        append_ledger("beforeShellExecution", "deny", command=cmd, reason="risky_network")
        return "deny", deny, deny

    if _DENIED_PATH_IN_CMD.search(cmd) and not _SAFE_SHELL.search(cmd):
        append_ledger("beforeShellExecution", "deny", command=cmd, reason="denied_path_in_cmd")
        return "deny", deny, deny

    if _SAFE_SHELL.search(cmd) or path_hint_ok(cmd, "strict", cfg):
        return "allow", None, None

    append_ledger("beforeShellExecution", "deny", command=cmd, reason="not_allowlisted")
    return "deny", deny, deny


def path_hint_ok(cmd: str, mode: str, cfg: dict | None = None) -> bool:
    """If command only mentions allowlisted relative paths, treat as ok."""
    mentions = re.findall(r"(?:^|[\s\"'=])((?:\.cursor|docs|monai|tests|AGENTS\.md)[^\s\"']*)", cmd)
    if not mentions:
        return False
    return all(path_allowed(m, mode, cfg) for m in mentions)
