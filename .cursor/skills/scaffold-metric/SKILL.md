---
name: scaffold-metric
description: >-
  Engineer workflow: implement a new metric under monai/metrics/ by mirroring a
  named neighbor, register it, and add tests with one planted QA gap. Use when
  the user runs /scaffold-metric. Prefer MONAI_CURSOR_BOUNDARY=strict.
disable-model-invocation: true
---

# /scaffold-metric (Engineer)

## Hard gate (Layer T) — run before any production edit

```bash
ISSUE=<n>   # from the planned issue
python3 docs/cursor-kit/scripts/score_tdd_gate.py --issue "$ISSUE" \
  --test-path tests/metrics/test_<name>.py
```

If the command exits non-zero: **stop**. Do not edit `monai/**` or tests beyond what the gate already required. Tell the user which check failed and that they need `SPEC.md` + Layer T tests + `Verdict: Approve` from `/critique-spec`.

Only after exit 0, continue with the implementation steps below (including the intentional planted QA gap).

## Ledger

```bash
echo '{"event":"skill","decision":"start","skill":"scaffold-metric","persona":"engineer","stage":"build","profile":"strict"}' \
  | python3 .cursor/hooks/ledger_append.py
```

(end: `"decision":"end"`)

## Refs (load only these)

- `@docs/cursor-kit/monai-refs/metrics.md`
- `.cursor/rules/60-metrics.mdc`
- Named neighbor: `monai/metrics/regression.py` (`MAEMetric`). Do not read the whole package.

## Intra-stage specialist dispatch (optional)

Metrics are light; run inline by default. May be delegated to a depth-1 specialist subagent only to isolate context during larger build work. Never advance to another persona's stage.

## Steps

1. Read the issue and the named neighbor `MAEMetric`.
2. Append the metric class (subclass `RegressionMetric`; implement `_compute_metric` returning `(batch, 1)`).
3. Apache header (new files); `from __future__ import annotations`; Google docstrings.
4. Register in `monai/metrics/__init__.py` (case-insensitive alphabetical).
5. Add `tests/metrics/test_<name>.py`.

## Planted QA defect (required — intentional, tool-detectable training signal)

Leave the class **out** of `monai/metrics/__init__.py`. Surfaces as `ImportError` at test/import time. Handoff note: "Planted: metric missing from `monai/metrics/__init__.py` — caught at import time. For `/strengthen-tests`."

## Stop when

Class + tests exist, registration gap remains, handoff note cites issue URL + planted defect. Do not run full CI.
