#!/usr/bin/env python3
"""ledger-dashboard-plain.py — baseline (pre-fancy) HTML dashboard for compare.

Frozen copy of the first minimal dashboard. Preferred generator is
`ledger-dashboard.py` (richer UI). Default output for this script should be
passed explicitly, e.g.:

  python3 docs/cursor-kit/scripts/ledger-dashboard-plain.py \\
    docs/cursor-kit/eval-runs/2026-07-17/kit-spine-20260719.jsonl \\
    --out .cursor/usage/ledger-dashboard-plain.html
"""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def _root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_score_module():
    path = _root() / "docs/cursor-kit/eval-runs/2026-07-17/scripts/score_trajectory.py"
    spec = importlib.util.spec_from_file_location("score_trajectory", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load scorer at {path}")
    mod = importlib.util.module_from_spec(spec)
    # dataclasses needs the module registered before exec_module.
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _aggregate(records: list[dict]) -> dict:
    by_event: Counter = Counter()
    by_decision: Counter = Counter()
    by_persona: Counter = Counter()
    by_stage: Counter = Counter()
    by_skill: Counter = Counter()
    for rec in records:
        by_event[str(rec.get("event", "?"))] += 1
        by_decision[str(rec.get("decision", "?"))] += 1
        if rec.get("persona"):
            by_persona[str(rec["persona"])] += 1
        if rec.get("stage"):
            by_stage[str(rec["stage"])] += 1
        if rec.get("skill"):
            by_skill[str(rec["skill"])] += 1
    denies = sum(v for k, v in by_decision.items() if "deny" in k)
    warns = sum(v for k, v in by_decision.items() if "warn" in k)
    oob = by_decision.get("attachment_out_of_bounds", 0)
    return {
        "total": len(records),
        "denies": denies,
        "warns": warns,
        "oob": oob,
        "by_persona": by_persona,
        "by_stage": by_stage,
        "by_skill": by_skill,
        "by_event": by_event,
        "by_decision": by_decision,
    }


def _table(title: str, counter: Counter, key_header: str) -> str:
    if not counter:
        return f"<section><h2>{html.escape(title)}</h2><p class='empty'>(none)</p></section>"
    rows = "".join(
        f"<tr><td>{html.escape(str(k))}</td><td class='n'>{v}</td></tr>"
        for k, v in counter.most_common()
    )
    return (
        f"<section><h2>{html.escape(title)}</h2>"
        f"<table><thead><tr><th>{html.escape(key_header)}</th><th>count</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></section>"
    )


def _render_html(*, ledger: Path, agg: dict, report: dict) -> str:
    score = report["score"]
    ship = score["ship_ready_trajectory"]
    badge = "pass" if ship else "fail"
    ship_label = "ship-ready" if ship else "not ship-ready"
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    skills = ", ".join(report.get("skills_started") or []) or "(none)"

    check_rows = "".join(
        "<tr>"
        f"<td class='{'ok' if c['passed'] else 'bad'}'>{'PASS' if c['passed'] else 'FAIL'}</td>"
        f"<td>{'required' if c['required'] else 'optional'}</td>"
        f"<td>{html.escape(c['label'])}</td>"
        f"<td class='detail'>{html.escape(c['detail'])}</td>"
        "</tr>"
        for c in report["checks"]
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>MONAI Cursor kit — ledger dashboard</title>
<style>
  :root {{
    --ink: #1a1a1a;
    --muted: #5c5c5c;
    --line: #e6e6e6;
    --ok: #1f6b3a;
    --bad: #8b1e1e;
    --bg: #fafaf8;
    --card: #ffffff;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font: 15px/1.45 "IBM Plex Sans", "Source Sans 3", "Segoe UI", sans-serif;
    color: var(--ink);
    background:
      radial-gradient(900px 400px at 10% -10%, #efece3 0%, transparent 55%),
      var(--bg);
  }}
  main {{ max-width: 880px; margin: 0 auto; padding: 2rem 1.25rem 3rem; }}
  h1 {{ font-size: 1.45rem; font-weight: 650; margin: 0 0 0.35rem; letter-spacing: -0.02em; }}
  h2 {{ font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); margin: 1.75rem 0 0.6rem; }}
  .meta {{ color: var(--muted); font-size: 0.9rem; }}
  .hero {{
    display: grid;
    gap: 0.75rem;
    grid-template-columns: 1fr;
    margin-top: 1.25rem;
  }}
  @media (min-width: 640px) {{
    .hero {{ grid-template-columns: 1.2fr 1fr; }}
  }}
  .card {{
    background: var(--card);
    border: 1px solid var(--line);
    padding: 1rem 1.1rem;
  }}
  .badge {{
    display: inline-block;
    padding: 0.2rem 0.55rem;
    font-size: 0.8rem;
    font-weight: 650;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }}
  .badge.pass {{ background: #e5f3ea; color: var(--ok); }}
  .badge.fail {{ background: #f8e6e6; color: var(--bad); }}
  .stats {{ display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 0.75rem; }}
  .stat strong {{ display: block; font-size: 1.35rem; }}
  .stat span {{ color: var(--muted); font-size: 0.8rem; }}
  table {{ width: 100%; border-collapse: collapse; background: var(--card); border: 1px solid var(--line); }}
  th, td {{ text-align: left; padding: 0.45rem 0.65rem; border-bottom: 1px solid var(--line); vertical-align: top; }}
  th {{ color: var(--muted); font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }}
  td.n {{ text-align: right; font-variant-numeric: tabular-nums; }}
  td.ok {{ color: var(--ok); font-weight: 650; }}
  td.bad {{ color: var(--bad); font-weight: 650; }}
  td.detail {{ color: var(--muted); font-size: 0.9rem; }}
  .empty {{ color: var(--muted); }}
  footer {{ margin-top: 2rem; color: var(--muted); font-size: 0.85rem; }}
</style>
</head>
<body>
<main>
  <h1>MONAI Cursor kit — ledger dashboard</h1>
  <p class="meta">Generated {html.escape(generated)} · ledger <code>{html.escape(str(ledger))}</code></p>

  <div class="hero">
    <div class="card">
      <span class="badge {badge}">{ship_label}</span>
      <div class="stats">
        <div class="stat"><strong>{score['required_pass']}/{score['required_total']}</strong><span>required</span></div>
        <div class="stat"><strong>{score['optional_pass']}/{score['optional_total']}</strong><span>optional</span></div>
        <div class="stat"><strong>{agg['total']}</strong><span>events</span></div>
      </div>
      <p class="meta" style="margin:0.85rem 0 0">Skills started: {html.escape(skills)}</p>
    </div>
    <div class="card">
      <div class="stats">
        <div class="stat"><strong>{agg['denies']}</strong><span>boundary denies</span></div>
        <div class="stat"><strong>{agg['warns']}</strong><span>warns</span></div>
        <div class="stat"><strong>{agg['oob']}</strong><span>out-of-bounds attachments</span></div>
      </div>
      <p class="meta" style="margin:0.85rem 0 0">Stage/persona metering — not a billing invoice.</p>
    </div>
  </div>

  <section>
    <h2>Trajectory checks (Layer C)</h2>
    <table>
      <thead><tr><th>result</th><th>kind</th><th>check</th><th>detail</th></tr></thead>
      <tbody>{check_rows}</tbody>
    </table>
  </section>

  {_table("By persona", agg["by_persona"], "persona")}
  {_table("By SDLC stage", agg["by_stage"], "stage")}
  {_table("By skill", agg["by_skill"], "skill")}
  {_table("By event source", agg["by_event"], "event")}
  {_table("By decision", agg["by_decision"], "decision")}

  <footer>
    Value is measured by ramp time and first-PR defect rate, not by this file.
    CLI equivalents: <code>ledger-report.py</code>, <code>score_trajectory.py</code>.
  </footer>
</main>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Write ledger counts + trajectory score as HTML.")
    ap.add_argument("ledger", nargs="?", type=Path, help="Path to ledger.jsonl")
    ap.add_argument(
        "--out",
        type=Path,
        help="HTML output path (default: .cursor/usage/ledger-dashboard-plain.html)",
    )
    ap.add_argument("--session", choices=("latest", "all"), default="all")
    ap.add_argument("--open", action="store_true", help="Print file:// URL only (does not launch a browser)")
    args = ap.parse_args()

    root = _root()
    ledger = (args.ledger or root / ".cursor" / "usage" / "ledger.jsonl").resolve()
    out = (args.out or root / ".cursor" / "usage" / "ledger-dashboard-plain.html").resolve()

    scorer = _load_score_module()
    records = scorer.load_ledger(ledger)
    if not records:
        print(f"No ledger records at {ledger}", file=sys.stderr)
        return 1

    scoped = scorer.filter_session(records, session=args.session, since_ts=None)
    report = scorer.score_trajectory(scoped)
    report["ledger"] = str(ledger)
    report["session"] = args.session
    agg = _aggregate(scoped)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_render_html(ledger=ledger, agg=agg, report=report), encoding="utf-8")

    score = report["score"]
    print(f"Wrote {out}")
    print(
        f"ship_ready_trajectory={score['ship_ready_trajectory']}  "
        f"required={score['required_pass']}/{score['required_total']}  "
        f"events={agg['total']}"
    )
    if args.open:
        print(out.as_uri())

    # Also emit a small JSON sidecar for tooling.
    sidecar = out.with_suffix(".json")
    sidecar.write_text(
        json.dumps(
            {
                "ledger": str(ledger),
                "html": str(out),
                "score": score,
                "skills_started": report.get("skills_started"),
                "counts": {
                    "total": agg["total"],
                    "denies": agg["denies"],
                    "warns": agg["warns"],
                    "oob": agg["oob"],
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return 0 if score["ship_ready_trajectory"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
