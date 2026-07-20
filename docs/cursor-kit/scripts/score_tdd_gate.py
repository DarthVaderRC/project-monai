#!/usr/bin/env python3
"""Layer T gate: SPEC + failing-test path + Approved SPEC-REVIEW + critic marker.

Paths come from consumer `.cursor/pack.config.json` → `tdd.artifact_paths`
when `schema_version` is present (Phase 3). Used by /scaffold-* as a hard
refuse gate and by Layer C.

Critic proof is kit-owned: /critique-spec appends a ledger row with
subagent_type=spec-critic and source=critique-spec. Do not rely on Cursor's
subagentStart payload populating subagent_type for custom agents.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

REQUIRED_SPEC_HEADINGS: tuple[str, ...] = (
    "## Problem",
    "## Acceptance criteria",
    "## Non-goals",
    "## Touch paths",
    "## Test expectations",
)

_VERDICT_LAST = frozenset({"Approve", "Request changes"})
PACK_CONFIG_ENV = "CURSOR_ONBOARDING_PACK_CONFIG"
PACK_CONFIG_REL = ".cursor/pack.config.json"


def load_pack_config(root: Path) -> dict | None:
    override = os.environ.get(PACK_CONFIG_ENV, "").strip()
    path = Path(override).resolve() if override else (root / PACK_CONFIG_REL).resolve()
    try:
        if not path.is_file():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def resolve_tdd_paths(root: Path, issue: str, cfg: dict | None) -> dict[str, Path]:
    """Resolve SPEC / REVIEW / test paths from pack.config tdd.artifact_paths.

    Requires schema_version + tdd.artifact_paths (Phase 3 — no hardcoded fallback).
    """
    if not isinstance(cfg, dict) or cfg.get("schema_version") is None:
        raise ValueError(
            f"pack.config missing or lacks schema_version — need {PACK_CONFIG_REL} "
            "(copy from pack example) with tdd.artifact_paths"
        )
    tdd = cfg.get("tdd")
    if not isinstance(tdd, dict):
        raise ValueError("pack.config missing tdd.artifact_paths")
    arts = tdd.get("artifact_paths")
    if not isinstance(arts, dict):
        raise ValueError("pack.config missing tdd.artifact_paths")
    for key in ("spec", "review", "test"):
        if not arts.get(key):
            raise ValueError(f"pack.config tdd.artifact_paths.{key} required")

    def _fmt(template: str) -> Path:
        return (root / str(template).format(issue=issue)).resolve()

    return {
        "spec": _fmt(str(arts["spec"])),
        "review": _fmt(str(arts["review"])),
        "test": _fmt(str(arts["test"])),
    }


def required_verdict_token(cfg: dict | None) -> str:
    if isinstance(cfg, dict):
        critic = cfg.get("spec_critic")
        if isinstance(critic, dict) and critic.get("required_verdict_token"):
            return str(critic["required_verdict_token"])
    return "Approve"


def verdict_of(text: str) -> str | None:
    """Machine verdict = last non-empty line must be exactly Verdict: <token>.

    Ignores prose that mentions 'Verdict:' earlier in the file.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return None
    last = lines[-1]
    if not last.startswith("Verdict:"):
        return None
    token = last[len("Verdict:") :].strip()
    if token not in _VERDICT_LAST:
        return None
    return token


def load_ledger(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def session_slice(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    starts = [i for i, r in enumerate(records) if r.get("event") == "sessionStart"]
    if not starts:
        return records
    return records[starts[-1] :]


def critic_marker_present(records: list[dict[str, Any]]) -> bool:
    """True when /critique-spec wrote its kit-owned ledger marker."""
    for rec in records:
        if rec.get("event") != "subagentStart":
            continue
        if rec.get("subagent_type") == "spec-critic" and rec.get("source") == "critique-spec":
            return True
    return False


def _check(id_: str, label: str, passed: bool, detail: str) -> dict[str, Any]:
    return {"id": id_, "label": label, "passed": passed, "required": True, "detail": detail}


def score_tdd_gate(
    root: Path,
    ledger_path: Path,
    *,
    issue: str,
    test_path: str | None = None,
) -> dict[str, Any]:
    cfg = load_pack_config(root)
    try:
        paths = resolve_tdd_paths(root, issue, cfg)
    except ValueError as exc:
        return {
            "ok": False,
            "checks": [
                _check(
                    "pack_config",
                    "pack.config tdd.artifact_paths resolvable",
                    False,
                    str(exc),
                )
            ],
            "exit_code": 1,
            "issue": issue,
        }

    # CLI --test-path still overrides the configured default when provided explicitly.
    if test_path:
        paths["test"] = (root / test_path).resolve()

    spec_path = paths["spec"]
    review_path = paths["review"]
    test_file = paths["test"]
    approve_token = required_verdict_token(cfg)
    checks: list[dict[str, Any]] = []

    spec_ok = spec_path.is_file()
    checks.append(_check("spec_exists", "SPEC.md exists", spec_ok, str(spec_path)))

    headings_ok = False
    if spec_ok:
        body = spec_path.read_text(encoding="utf-8")
        missing = [h for h in REQUIRED_SPEC_HEADINGS if h not in body]
        headings_ok = not missing
        checks.append(
            _check(
                "spec_sections",
                "SPEC has required H2 sections",
                headings_ok,
                "ok" if headings_ok else f"missing: {missing}",
            )
        )
    else:
        checks.append(_check("spec_sections", "SPEC has required H2 sections", False, "no SPEC"))

    test_ok = test_file.is_file()
    checks.append(_check("failing_test_exists", "Layer T test module exists", test_ok, str(test_file)))

    # Red check: **static heuristic / required convention**, not pytest execution.
    # Authors must include a marker token — a plain assertEqual that fails only at runtime
    # without one of these tokens will FAIL this gate. DEMO instructs the marker.
    # Tokens: "Layer T red" | raise AssertionError | self.fail( | @unittest.expectedFailure
    red_ok = False
    if test_ok:
        text = test_file.read_text(encoding="utf-8")
        red_ok = (
            "Layer T red" in text
            or "raise AssertionError" in text
            or "self.fail(" in text
            or "@unittest.expectedFailure" in text
        )
    checks.append(
        _check(
            "failing_test_red_marker",
            "Test file has Layer T red marker (pre-impl convention)",
            red_ok if test_ok else False,
            "marker present" if red_ok else "add 'Layer T red' or raise AssertionError stub (required convention)",
        )
    )

    review_ok = review_path.is_file()
    checks.append(_check("review_exists", "SPEC-REVIEW.md exists", review_ok, str(review_path)))

    verdict = verdict_of(review_path.read_text(encoding="utf-8")) if review_ok else None
    approved = verdict == approve_token
    checks.append(
        _check(
            "verdict_approve",
            f"Verdict: {approve_token} (last non-empty line)",
            approved,
            f"verdict={verdict!r}",
        )
    )

    records = session_slice(load_ledger(ledger_path))
    critic = critic_marker_present(records)
    checks.append(
        _check(
            "critic_subagent",
            "kit-owned spec-critic marker (source=critique-spec)",
            critic,
            "found" if critic else "missing ledger marker from /critique-spec",
        )
    )

    # Pre-scaffold hard gate: all checks required.
    ok = all(c["passed"] for c in checks)
    return {"ok": ok, "checks": checks, "exit_code": 0 if ok else 1, "issue": issue}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--issue", required=True, help="Workdir issue id, e.g. 1")
    p.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repo root (default: cwd)",
    )
    p.add_argument(
        "--test-path",
        default=None,
        help="Override relative path to Layer T test module (else pack.config tdd.artifact_paths.test)",
    )
    p.add_argument(
        "--ledger",
        type=Path,
        default=None,
        help="ledger.jsonl path",
    )
    p.add_argument("--json", action="store_true", help="Print full JSON result")
    args = p.parse_args(argv)
    root = (args.root or Path.cwd()).resolve()
    ledger = args.ledger or (root / ".cursor" / "usage" / "ledger.jsonl")
    result = score_tdd_gate(root, ledger, issue=args.issue, test_path=args.test_path)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for c in result["checks"]:
            mark = "PASS" if c["passed"] else "FAIL"
            print(f"[{mark}] {c['id']}: {c['detail']}")
        print("OK" if result["ok"] else "FAIL")
    return int(result["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
