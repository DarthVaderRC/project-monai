---
name: critique-spec
description: >-
  Dispatch the spec-critic agent to review SPEC.md + Layer T failing tests and
  write SPEC-REVIEW.md with Verdict: Approve or Request changes. Hard gate before
  /scaffold-*. Use when the user runs /critique-spec.
disable-model-invocation: true
---

# /critique-spec (PM / plan stage)

## Ledger

```bash
echo '{"event":"skill","decision":"start","skill":"critique-spec","persona":"PM","stage":"plan"}' \
  | python3 .cursor/hooks/ledger_append.py
```

(end: `"decision":"end"`)

## Profile

`everyday` (same as other PM skills). **Note:** everyday does not confine the critic to `docs/cursor-kit/work/**`; prod-write restraint is prompt-only in v1.

## Input

- Issue number (default `1` for RobustScaleIntensity demo)
- Confirm `docs/cursor-kit/work/<issue>/SPEC.md` exists
- Confirm Layer T test file exists (default `tests/transforms/test_robust_scale_intensity.py`) with a red marker

## Steps

1. Preflight (deterministic):

```bash
ISSUE=<n>
test -f docs/cursor-kit/work/$ISSUE/SPEC.md || { echo "missing SPEC.md"; exit 1; }
test -f tests/transforms/test_robust_scale_intensity.py || { echo "missing Layer T tests"; exit 1; }
```

2. Dispatch the **spec-critic** subagent (depth-1) via the Task tool / custom agent `spec-critic`. Prompt it with the issue number, SPEC path, and test path. The agent's `model:` frontmatter supplies the HIGH tier — do not override downward. Confirm in the UI that the launched agent shows **`cursor-grok-4.5-high-fast`** (or the verified slug from Step 0).

3. Wait for `docs/cursor-kit/work/<issue>/SPEC-REVIEW.md`. Confirm the file exists and the **last non-empty line** is `Verdict: Approve` or `Verdict: Request changes`.

4. **Append the kit-owned critic marker only after SPEC-REVIEW is confirmed on disk** (required for `score_tdd_gate` + Layer C). Choice: post-write, not pre-dispatch — marker attests “critic review artifact produced this run,” not merely “skill started.” Substance proof remains the review file + Approve line; marker is the delegation/completion signal the gate can trust without Cursor’s audit payload.

```bash
echo '{"event":"subagentStart","decision":"allow","subagent_type":"spec-critic","source":"critique-spec","task":"critique SPEC"}' \
  | python3 .cursor/hooks/ledger_append.py
```

Note: Cursor’s `subagent_audit` hook may also write a separate `subagentStart` row (no `source=critique-spec`). That is expected dual-row; gate/Layer C required checks filter on `source` so they do not double-count. Sanity-check ledger dashboard / reports after Task 7 so charts don’t look like two critic runs.

5. Show the verdict line. If `Request changes`, stop and hand back to `/plan-feature` (revise SPEC/tests; re-run `/critique-spec`). Do **not** run `/scaffold-*`.

6. Verify gate (should pass once Approve + marker + SPEC + red tests exist):

```bash
python3 docs/cursor-kit/scripts/score_tdd_gate.py --issue <n>
```

## Output

Path to `SPEC-REVIEW.md` + the `Verdict:` line + confirmation that ledger contains `source=critique-spec`.

## Stop when

Verdict file exists. End ledger. Do not implement production code.
