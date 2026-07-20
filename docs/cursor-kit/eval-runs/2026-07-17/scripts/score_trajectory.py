#!/usr/bin/env python3
"""Score kit-spine trajectory from the Cursor kit usage ledger.

Reads `.cursor/usage/ledger.jsonl` (or a saved copy) and checks whether the
session followed the expected persona/skill path, boundary profile discipline,
and hook observability signals documented in DEMO.md.

Usage:
  python3 docs/cursor-kit/eval-runs/2026-07-17/scripts/score_trajectory.py
  python3 .../score_trajectory.py path/to/kit-spine.jsonl --json-out scores.json
  python3 .../score_trajectory.py --session all --require-subagent
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

DEMO_SPINE_SKILLS: tuple[str, ...] = (
    "triage-issues",
    "plan-feature",
    "critique-spec",
    "scaffold-transform",
    "strengthen-tests",
    "prep-for-ci",
    "review-contribution",
)

_OUT_OF_BOUNDS_READ = re.compile(
    r"monai/(?!transforms(?:/|\b))[^/]+|"
    r"tests/(?!transforms(?:/|\b))",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Check:
    id: str
    label: str
    passed: bool
    required: bool
    detail: str


def _parse_ts(raw: str) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def load_ledger(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    records.sort(key=lambda r: r.get("ts") or "")
    return records


def filter_session(
    records: list[dict[str, Any]],
    *,
    session: str,
    since_ts: str | None,
) -> list[dict[str, Any]]:
    if since_ts:
        cutoff = _parse_ts(since_ts)
        if cutoff:
            return [r for r in records if (_parse_ts(str(r.get("ts", ""))) or cutoff) >= cutoff]

    if session != "latest":
        return records

    starts = [i for i, r in enumerate(records) if r.get("event") == "sessionStart"]
    if not starts:
        return records
    return records[starts[-1] :]


def _skill_starts(records: list[dict[str, Any]]) -> dict[str, datetime]:
    out: dict[str, datetime] = {}
    for rec in records:
        if rec.get("event") != "skill" or rec.get("decision") != "start":
            continue
        skill = rec.get("skill")
        if not skill or skill in out:
            continue
        ts = _parse_ts(str(rec.get("ts", "")))
        if ts:
            out[str(skill)] = ts
    return out


def _ordered(skills: dict[str, datetime], a: str, b: str) -> bool | None:
    if a not in skills or b not in skills:
        return None
    return skills[a] <= skills[b]


def score_trajectory(
    records: list[dict[str, Any]],
    *,
    require_subagent: bool = False,
) -> dict[str, Any]:
    skill_starts = _skill_starts(records)
    checks: list[Check] = []

    for skill in DEMO_SPINE_SKILLS:
        checks.append(
            Check(
                id=f"skill_{skill.replace('-', '_')}",
                label=f"Skill invoked: /{skill}",
                passed=skill in skill_starts,
                required=True,
                detail="start event in ledger" if skill in skill_starts else "missing skill start",
            )
        )

    order_pairs = [
        ("triage-issues", "plan-feature"),
        ("plan-feature", "critique-spec"),
        ("critique-spec", "scaffold-transform"),
        ("scaffold-transform", "strengthen-tests"),
        ("strengthen-tests", "prep-for-ci"),
        ("prep-for-ci", "review-contribution"),
    ]
    order_ok = True
    order_details: list[str] = []
    for a, b in order_pairs:
        result = _ordered(skill_starts, a, b)
        if result is None:
            order_details.append(f"{a} → {b}: skipped (missing skill)")
            continue
        if not result:
            order_ok = False
            order_details.append(f"{a} → {b}: OUT OF ORDER")
        else:
            order_details.append(f"{a} → {b}: ok")

    checks.append(
        Check(
            id="demo_spine_order",
            label="Kit spine skill order",
            passed=order_ok and len(skill_starts) >= 2,
            required=True,
            detail="; ".join(order_details) if order_details else "no skills to compare",
        )
    )

    strict_read_denies = [
        r
        for r in records
        if r.get("event") == "beforeReadFile"
        and r.get("decision") == "deny"
        and r.get("profile") == "strict"
        and _OUT_OF_BOUNDS_READ.search(str(r.get("path", "")))
    ]
    checks.append(
        Check(
            id="strict_boundary_deny",
            label="Strict mode blocked out-of-bounds read",
            passed=bool(strict_read_denies),
            required=True,
            detail=strict_read_denies[0].get("path", "none") if strict_read_denies else "no strict read deny",
        )
    )

    gh_denies_strict = [
        r
        for r in records
        if r.get("event") == "beforeShellExecution"
        and r.get("decision") == "deny"
        and r.get("profile") == "strict"
        and r.get("reason") == "gh_in_strict"
    ]
    checks.append(
        Check(
            id="strict_gh_denied",
            label="gh blocked under strict (if attempted)",
            passed=True,
            required=False,
            detail=f"{len(gh_denies_strict)} deny event(s)" if gh_denies_strict else "gh not attempted in strict",
        )
    )

    scaffold_ts = skill_starts.get("scaffold-transform")
    scaffold_strict = any(
        r.get("event") == "skill"
        and r.get("skill") == "scaffold-transform"
        and r.get("decision") == "start"
        and r.get("profile") == "strict"
        for r in records
    ) or any(
        r.get("event") == "sessionStart"
        and r.get("profile") == "strict"
        and scaffold_ts
        and (_parse_ts(str(r.get("ts", ""))) or scaffold_ts) <= scaffold_ts
        for r in records
    )
    checks.append(
        Check(
            id="scaffold_under_strict",
            label="Scaffold ran under strict profile",
            passed=scaffold_strict if "scaffold-transform" in skill_starts else False,
            required=True,
            detail="strict on skill or sessionStart before scaffold",
        )
    )

    pm_everyday = True
    pm_detail: list[str] = []
    for skill in ("triage-issues", "plan-feature"):
        for rec in records:
            if rec.get("event") == "skill" and rec.get("skill") == skill and rec.get("decision") == "start":
                prof = rec.get("profile", "everyday")
                if prof == "strict":
                    pm_everyday = False
                    pm_detail.append(f"{skill} started under strict")
                else:
                    pm_detail.append(f"{skill} profile={prof}")
    checks.append(
        Check(
            id="pm_under_everyday",
            label="PM skills not started under strict",
            passed=pm_everyday if any(s in skill_starts for s in ("triage-issues", "plan-feature")) else True,
            required=False,
            detail="; ".join(pm_detail) or "PM skills not logged",
        )
    )

    transform_edits = [
        r
        for r in records
        if r.get("event") == "afterFileEdit" and r.get("decision") == "transform_edit"
    ] or [
        r
        for r in records
        if r.get("event") == "postToolUse" and r.get("decision") == "nudge"
    ]
    checks.append(
        Check(
            id="transform_edit_observed",
            label="Transform edit or post-edit nudge logged",
            passed=bool(transform_edits),
            required=False,
            detail=str(len(transform_edits)) + " event(s)",
        )
    )

    subagent_starts = [r for r in records if r.get("event") == "subagentStart"]
    checks.append(
        Check(
            id="subagent_delegation",
            label="Subagent delegation audited",
            passed=bool(subagent_starts),
            required=require_subagent,
            detail=subagent_starts[0].get("task", "none")[:80] if subagent_starts else "no subagentStart",
        )
    )

    critic_starts = [
        r
        for r in records
        if r.get("event") == "subagentStart"
        and r.get("subagent_type") == "spec-critic"
        and r.get("source") == "critique-spec"
    ]
    checks.append(
        Check(
            id="spec_critic_subagent",
            label="kit-owned spec-critic marker (source=critique-spec)",
            passed=bool(critic_starts),
            required=True,
            detail=f"{len(critic_starts)} critic marker(s)" if critic_starts else "missing",
        )
    )

    coach_blocks = [r for r in records if r.get("event") == "beforeSubmitPrompt" and r.get("decision") == "blocked"]
    checks.append(
        Check(
            id="prompt_coach_fired",
            label="Prompt coach blocked anti-pattern (optional beat)",
            passed=bool(coach_blocks),
            required=False,
            detail=coach_blocks[0].get("reason", "none") if coach_blocks else "not triggered",
        )
    )

    required = [c for c in checks if c.required]
    optional = [c for c in checks if not c.required]
    required_pass = sum(1 for c in required if c.passed)
    optional_pass = sum(1 for c in optional if c.passed)
    ship_ready = all(c.passed for c in required)

    return {
        "event_count": len(records),
        "skills_started": list(skill_starts.keys()),
        "score": {
            "required_pass": required_pass,
            "required_total": len(required),
            "optional_pass": optional_pass,
            "optional_total": len(optional),
            "ship_ready_trajectory": ship_ready,
        },
        "checks": [
            {
                "id": c.id,
                "label": c.label,
                "passed": c.passed,
                "required": c.required,
                "detail": c.detail,
            }
            for c in checks
        ],
    }


def _default_ledger(root: Path) -> Path:
    return root / ".cursor" / "usage" / "ledger.jsonl"


def main() -> int:
    ap = argparse.ArgumentParser(description="Score kit-spine trajectory from usage ledger.")
    ap.add_argument(
        "ledger",
        nargs="?",
        type=Path,
        help="Path to ledger.jsonl (default: <repo>/.cursor/usage/ledger.jsonl)",
    )
    ap.add_argument(
        "--repo-root",
        type=Path,
        help="Repo root when ledger path omitted (default: auto from script location)",
    )
    ap.add_argument("--session", choices=("latest", "all"), default="latest")
    ap.add_argument("--since-ts", help="Only score events at or after this ISO timestamp")
    ap.add_argument("--require-subagent", action="store_true", help="Fail if subagentStart missing")
    ap.add_argument("--json-out", type=Path)
    args = ap.parse_args()

    repo_root = (args.repo_root or Path(__file__).resolve().parents[5]).resolve()
    ledger = args.ledger.resolve() if args.ledger else _default_ledger(repo_root)

    records = load_ledger(ledger)
    if not records:
        print(f"No ledger records at {ledger}", file=sys.stderr)
        return 1

    scoped = filter_session(records, session=args.session, since_ts=args.since_ts)
    report = score_trajectory(scoped, require_subagent=args.require_subagent)
    report["ledger"] = str(ledger)
    report["session"] = args.session
    report["since_ts"] = args.since_ts
    report["scoped_event_count"] = len(scoped)

    score = report["score"]
    print(f"Trajectory score — {ledger.name} ({args.session} session, {len(scoped)} events)")
    print(
        f"  required: {score['required_pass']}/{score['required_total']}   "
        f"optional: {score['optional_pass']}/{score['optional_total']}   "
        f"ship_ready_trajectory: {score['ship_ready_trajectory']}"
    )
    print(f"  skills started: {', '.join(report['skills_started']) or '(none)'}")
    print()
    for row in report["checks"]:
        mark = "PASS" if row["passed"] else "FAIL"
        req = "required" if row["required"] else "optional"
        print(f"  [{mark}] ({req}) {row['label']}")
        print(f"         {row['detail']}")

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    return 0 if score["ship_ready_trajectory"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
