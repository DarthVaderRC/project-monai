---
name: scaffold-loss
description: >-
  Engineer workflow: implement a new loss under monai/losses/ by mirroring a
  named neighbor, register it, and add parameterized tests with one planted QA
  gap. Use when the user runs /scaffold-loss. Prefer MONAI_CURSOR_BOUNDARY=strict.
disable-model-invocation: true
---

# /scaffold-loss (Engineer)

## Hard gate (Layer T) — run before any production edit

```bash
ISSUE=<n>   # from the planned issue
python3 docs/cursor-kit/scripts/score_tdd_gate.py --issue "$ISSUE" \
  --test-path tests/losses/test_<name>.py
```

If the command exits non-zero: **stop**. Do not edit `monai/**` or tests beyond what the gate already required. Tell the user which check failed and that they need `SPEC.md` + Layer T tests + `Verdict: Approve` from `/critique-spec`.

Only after exit 0, continue with the implementation steps below (including the intentional planted QA gap).

## Ledger

```bash
echo '{"event":"skill","decision":"start","skill":"scaffold-loss","persona":"engineer","stage":"build","profile":"strict"}' \
  | python3 .cursor/hooks/ledger_append.py
```

(end: `"decision":"end"`)

## Refs (load only these)

- `@docs/cursor-kit/monai-refs/losses.md`
- `.cursor/rules/50-losses.mdc`
- Named neighbor: `monai/losses/dice.py` (`DiceLoss`). Do not read the whole `monai/losses/` package.

## Intra-stage specialist dispatch (optional)

Losses are light; run inline by default. Only if combining with other build work, the Engineer may delegate this skill body to a depth-1 specialist subagent to isolate context. Never advance to another persona's stage.

## Steps

1. Read the issue and the named neighbor `DiceLoss`.
2. Append the loss class in the appropriate `monai/losses/*.py` file (subclass `_Loss` or an existing loss).
3. Apache header (new files); `from __future__ import annotations`; Google docstrings.
4. Register the class name in `monai/losses/__init__.py` (case-insensitive alphabetical).
5. Add `tests/losses/test_<name>.py` with `parameterized` cases.

## Planted QA defect (required — intentional, tool-detectable training signal)

Leave the class **out** of `monai/losses/__init__.py` (implement + test everything else). This surfaces as an `ImportError` at test/import time — a real ship-blocker for `/strengthen-tests` to fix. Handoff note must say: "Planted: loss missing from `monai/losses/__init__.py` — caught at import time. For `/strengthen-tests`."

## Stop when

Class + tests exist, registration gap remains, handoff note cites issue URL + planted defect. Do not run full CI.
