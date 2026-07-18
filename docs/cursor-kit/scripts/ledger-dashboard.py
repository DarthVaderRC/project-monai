#!/usr/bin/env python3
"""ledger-dashboard.py — counts + trajectory score as an HTML dashboard.

Combines ledger-report aggregations with score_trajectory Layer C checks.
Token economics remain Cursor-estimated; this is observability, not billing.

Plain baseline (for compare): ledger-dashboard-plain.py → ledger-dashboard-plain.html

Usage:
  python3 docs/cursor-kit/scripts/ledger-dashboard.py
  python3 docs/cursor-kit/scripts/ledger-dashboard.py path/to/ledger.jsonl
  python3 docs/cursor-kit/scripts/ledger-dashboard.py --out /tmp/kit-dashboard.html
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


def _bar_section(title: str, counter: Counter, key_header: str, delay: float) -> str:
    if not counter:
        return (
            f"<section class='panel' style='--d:{delay}s'>"
            f"<h2>{html.escape(title)}</h2><p class='empty'>(none)</p></section>"
        )
    peak = max(counter.values()) or 1
    rows = []
    for i, (k, v) in enumerate(counter.most_common()):
        pct = max(4, round(100 * v / peak))
        rows.append(
            "<div class='bar-row' "
            f"style='--i:{i}'>"
            f"<div class='bar-label' title='{html.escape(key_header)}'>{html.escape(str(k))}</div>"
            f"<div class='bar-track'><div class='bar-fill' style='--w:{pct}%'></div></div>"
            f"<div class='bar-n'>{v}</div>"
            "</div>"
        )
    return (
        f"<section class='panel' style='--d:{delay}s'>"
        f"<h2>{html.escape(title)}</h2>"
        f"<div class='bars'>{''.join(rows)}</div></section>"
    )


def _spine(skills: list[str], expected: list[str]) -> str:
    items = []
    started = set(skills)
    for i, name in enumerate(expected):
        state = "done" if name in started else "miss"
        items.append(
            f"<li class='spine-item {state}' style='--i:{i}'>"
            f"<span class='spine-dot'></span>"
            f"<span class='spine-name'>/{html.escape(name)}</span>"
            f"<span class='spine-flag'>{'ran' if state == 'done' else 'missing'}</span>"
            "</li>"
        )
    return "<ol class='spine'>" + "".join(items) + "</ol>"


def _render_html(*, ledger: Path, agg: dict, report: dict) -> str:
    score = report["score"]
    ship = score["ship_ready_trajectory"]
    badge = "pass" if ship else "fail"
    ship_label = "Ship-ready trajectory" if ship else "Trajectory incomplete"
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    skills = list(report.get("skills_started") or [])
    skills_human = ", ".join(skills) or "(none)"
    expected = [
        "triage-issues",
        "plan-feature",
        "scaffold-transform",
        "strengthen-tests",
        "prep-for-ci",
        "review-contribution",
    ]
    req_pct = round(100 * score["required_pass"] / max(1, score["required_total"]))

    check_rows = []
    for i, c in enumerate(report["checks"]):
        mark = "PASS" if c["passed"] else "FAIL"
        kind = "required" if c["required"] else "optional"
        check_rows.append(
            f"<tr class='check {'ok' if c['passed'] else 'bad'}' style='--i:{i}'>"
            f"<td><span class='pill {('ok' if c['passed'] else 'bad')}'>{mark}</span></td>"
            f"<td class='kind'>{kind}</td>"
            f"<td>{html.escape(c['label'])}</td>"
            f"<td class='detail'>{html.escape(c['detail'])}</td>"
            "</tr>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>MONAI Cursor kit — ledger dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,500;6..72,650&display=swap" rel="stylesheet"/>
<style>
  :root {{
    --ink: #12202a;
    --muted: #5a6b76;
    --line: #d7e0e6;
    --ok: #0f7a4a;
    --ok-soft: #d8f3e6;
    --bad: #a12828;
    --bad-soft: #f8e0e0;
    --accent: #0b6e6a;
    --accent-2: #c45c26;
    --bg: #f3f6f4;
    --card: rgba(255,255,255,0.82);
    --shadow: 0 1px 0 rgba(18,32,42,0.04);
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    color: var(--ink);
    font: 15px/1.5 "Instrument Sans", "Segoe UI", sans-serif;
    background-color: var(--bg);
    background-image:
      linear-gradient(180deg, rgba(11,110,106,0.08), transparent 28%),
      radial-gradient(900px 480px at 90% -10%, rgba(196,92,38,0.12), transparent 50%),
      linear-gradient(rgba(18,32,42,0.035) 1px, transparent 1px),
      linear-gradient(90deg, rgba(18,32,42,0.035) 1px, transparent 1px);
    background-size: auto, auto, 28px 28px, 28px 28px;
    min-height: 100vh;
  }}
  main {{ max-width: 980px; margin: 0 auto; padding: 2.25rem 1.25rem 3.5rem; }}
  .mast {{
    display: flex; flex-wrap: wrap; justify-content: space-between; gap: 1rem;
    align-items: end; margin-bottom: 1.5rem;
    animation: rise 0.55s ease both;
  }}
  .brand {{
    font-family: "Newsreader", Georgia, serif;
    font-size: clamp(1.8rem, 3vw, 2.35rem);
    font-weight: 650;
    letter-spacing: -0.03em;
    line-height: 1.05;
    margin: 0;
  }}
  .brand span {{ color: var(--accent); }}
  .meta {{ color: var(--muted); font-size: 0.9rem; max-width: 36rem; }}
  .meta code {{
    font-size: 0.82em;
    background: rgba(255,255,255,0.7);
    border: 1px solid var(--line);
    padding: 0.05rem 0.35rem;
  }}
  .hero {{
    display: grid; gap: 1rem;
    grid-template-columns: 1.35fr 1fr;
    margin-bottom: 1.25rem;
  }}
  @media (max-width: 800px) {{ .hero {{ grid-template-columns: 1fr; }} }}
  .card {{
    background: var(--card);
    border: 1px solid var(--line);
    box-shadow: var(--shadow);
    backdrop-filter: blur(8px);
    padding: 1.15rem 1.25rem 1.25rem;
    animation: rise 0.6s ease both;
    animation-delay: var(--d, 0s);
  }}
  .badge {{
    display: inline-flex; align-items: center; gap: 0.4rem;
    padding: 0.28rem 0.65rem;
    font-size: 0.78rem; font-weight: 700;
    letter-spacing: 0.04em; text-transform: uppercase;
  }}
  .badge.pass {{ background: var(--ok-soft); color: var(--ok); }}
  .badge.fail {{ background: var(--bad-soft); color: var(--bad); }}
  .badge::before {{
    content: ""; width: 0.45rem; height: 0.45rem; border-radius: 1px;
    background: currentColor;
  }}
  .score-ring-wrap {{
    display: grid; grid-template-columns: auto 1fr; gap: 1rem; align-items: center;
    margin-top: 1rem;
  }}
  .ring {{
    --p: {req_pct};
    width: 92px; height: 92px; border-radius: 50%;
    background:
      conic-gradient(var(--accent) calc(var(--p) * 1%), #dfe7ea 0);
    display: grid; place-items: center;
    animation: spin-in 0.9s ease both;
  }}
  .ring > span {{
    width: 68px; height: 68px; border-radius: 50%;
    background: #fff; display: grid; place-items: center;
    font-weight: 700; font-size: 1.05rem;
  }}
  .stats {{ display: flex; flex-wrap: wrap; gap: 1.1rem; }}
  .stat strong {{
    display: block; font-size: 1.55rem; letter-spacing: -0.03em;
    font-variant-numeric: tabular-nums;
  }}
  .stat span {{ color: var(--muted); font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em; }}
  .panel {{
    background: var(--card);
    border: 1px solid var(--line);
    box-shadow: var(--shadow);
    padding: 1rem 1.15rem 1.15rem;
    margin-bottom: 1rem;
    animation: rise 0.55s ease both;
    animation-delay: var(--d, 0s);
  }}
  h2 {{
    font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.08em;
    color: var(--muted); margin: 0 0 0.85rem; font-weight: 600;
  }}
  .spine {{
    list-style: none; margin: 0; padding: 0;
    display: grid; gap: 0.45rem;
  }}
  .spine-item {{
    display: grid; grid-template-columns: auto 1fr auto; gap: 0.7rem;
    align-items: center; padding: 0.45rem 0.55rem;
    border: 1px solid transparent;
    animation: rise 0.45s ease both;
    animation-delay: calc(0.05s * var(--i));
  }}
  .spine-item.done {{ background: rgba(15,122,74,0.06); border-color: rgba(15,122,74,0.15); }}
  .spine-item.miss {{ background: rgba(161,40,40,0.05); border-color: rgba(161,40,40,0.12); }}
  .spine-dot {{
    width: 0.65rem; height: 0.65rem; border-radius: 1px;
    background: var(--muted);
  }}
  .spine-item.done .spine-dot {{ background: var(--ok); }}
  .spine-item.miss .spine-dot {{ background: var(--bad); }}
  .spine-name {{ font-weight: 600; font-variant-numeric: tabular-nums; }}
  .spine-flag {{ font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ text-align: left; padding: 0.5rem 0.55rem; border-bottom: 1px solid var(--line); vertical-align: top; }}
  th {{ color: var(--muted); font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }}
  tr.check {{ animation: rise 0.4s ease both; animation-delay: calc(0.03s * var(--i)); }}
  .pill {{
    display: inline-block; min-width: 3.2rem; text-align: center;
    padding: 0.12rem 0.4rem; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.04em;
  }}
  .pill.ok {{ background: var(--ok-soft); color: var(--ok); }}
  .pill.bad {{ background: var(--bad-soft); color: var(--bad); }}
  td.kind {{ color: var(--muted); font-size: 0.85rem; }}
  td.detail {{ color: var(--muted); font-size: 0.88rem; }}
  .bars {{ display: grid; gap: 0.45rem; }}
  .bar-row {{
    display: grid; grid-template-columns: minmax(7rem, 12rem) 1fr 2.2rem;
    gap: 0.65rem; align-items: center;
    animation: rise 0.4s ease both; animation-delay: calc(0.03s * var(--i));
  }}
  .bar-label {{
    font-size: 0.88rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }}
  .bar-track {{
    height: 0.55rem; background: #e4ecef; overflow: hidden;
  }}
  .bar-fill {{
    height: 100%; width: 0;
    background: linear-gradient(90deg, var(--accent), #1f8f88);
    animation: grow 0.7s ease forwards;
    animation-delay: calc(0.04s * var(--i) + 0.15s);
  }}
  .bar-n {{
    text-align: right; font-variant-numeric: tabular-nums; font-weight: 600; color: var(--muted);
  }}
  .empty {{ color: var(--muted); }}
  @keyframes rise {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to {{ opacity: 1; transform: none; }}
  }}
  @keyframes grow {{
    from {{ width: 0; }}
    to {{ width: var(--w); }}
  }}
  @keyframes spin-in {{
    from {{ filter: saturate(0.6); transform: scale(0.92); opacity: 0; }}
    to {{ filter: none; transform: none; opacity: 1; }}
  }}
  @media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{
      animation: none !important; transition: none !important;
    }}
  }}
</style>
</head>
<body>
<main>
  <header class="mast">
    <div>
      <p class="brand">MONAI kit <span>ledger</span></p>
      <p class="meta">Generated {html.escape(generated)} · {html.escape(str(ledger.name))} · session metering, not a billing invoice</p>
    </div>
    <span class="badge {badge}">{ship_label}</span>
  </header>

  <div class="hero">
    <div class="card" style="--d:0.05s">
      <h2>Layer C scorecard</h2>
      <div class="score-ring-wrap">
        <div class="ring" aria-label="Required score {score['required_pass']} of {score['required_total']}">
          <span>{score['required_pass']}/{score['required_total']}</span>
        </div>
        <div class="stats">
          <div class="stat"><strong>{score['optional_pass']}/{score['optional_total']}</strong><span>optional</span></div>
          <div class="stat"><strong>{agg['total']}</strong><span>events</span></div>
          <div class="stat"><strong>{len(skills)}</strong><span>skills</span></div>
        </div>
      </div>
      <p class="meta" style="margin:1rem 0 0">Started: {html.escape(skills_human)}</p>
    </div>
    <div class="card" style="--d:0.12s">
      <h2>Boundary signal</h2>
      <div class="stats" style="margin-top:0.35rem">
        <div class="stat"><strong>{agg['denies']}</strong><span>denies</span></div>
        <div class="stat"><strong>{agg['warns']}</strong><span>warns</span></div>
        <div class="stat"><strong>{agg['oob']}</strong><span>oob attach</span></div>
      </div>
      <p class="meta" style="margin:1rem 0 0">Strict deny + warn counts from hook decisions in this ledger slice.</p>
    </div>
  </div>

  <section class="panel" style="--d:0.18s">
    <h2>Contribution spine</h2>
    {_spine(skills, expected)}
  </section>

  <section class="panel" style="--d:0.22s">
    <h2>Trajectory checks</h2>
    <table>
      <thead><tr><th>result</th><th>kind</th><th>check</th><th>detail</th></tr></thead>
      <tbody>{''.join(check_rows)}</tbody>
    </table>
  </section>

  <section class="panel" style="--d:0.24s">
    <h2>How to read these counts</h2>
    <p class="meta" style="margin:0">
      Bars count <strong>ledger event lines</strong>, not unique people or unique skill runs.
      Persona / stage / skill tallies come almost only from <code>event=skill</code>
      lines (<code>start</code> + <code>end</code>). A clean run is usually <strong>2 per skill</strong>
      (one start, one end). Higher means retries or missing end markers.
    </p>
  </section>

  {_bar_section("By persona — skill events tagged with persona", agg["by_persona"], "persona", 0.26)}
  {_bar_section("By SDLC stage — skill events tagged with stage", agg["by_stage"], "stage", 0.3)}
  {_bar_section("By skill — skill start/end events (≈2 per complete run)", agg["by_skill"], "skill", 0.34)}
  {_bar_section("By event source — all hook/skill event types", agg["by_event"], "event", 0.38)}
  {_bar_section("By decision — allow/deny/warn/start/end/…", agg["by_decision"], "decision", 0.42)}
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
        help="HTML output path (default: .cursor/usage/ledger-dashboard.html)",
    )
    ap.add_argument("--session", choices=("latest", "all"), default="all")
    ap.add_argument("--open", action="store_true", help="Print file:// URL only (does not launch a browser)")
    args = ap.parse_args()

    root = _root()
    ledger = (args.ledger or root / ".cursor" / "usage" / "ledger.jsonl").resolve()
    out = (args.out or root / ".cursor" / "usage" / "ledger-dashboard.html").resolve()

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
