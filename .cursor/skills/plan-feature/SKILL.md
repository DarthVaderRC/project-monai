---
name: plan-feature
description: >-
  PM workflow: create or update a live GitHub issue on the MONAI fork with
  acceptance criteria, non-goals, touch paths, and test expectations for a
  catalog intensity transform. Use when the user runs /plan-feature. Fork only.
disable-model-invocation: true
---

# /plan-feature (PM)

## Ledger

```bash
echo '{"event":"skill","decision":"start","skill":"plan-feature","persona":"PM","stage":"plan"}' \
  | python3 .cursor/hooks/ledger_append.py
```

(end: `"decision":"end"`)

## Remote (required)

- `gh -R DarthVaderRC/project-monai` (or `origin` fork only).
- Never target upstream `Project-MONAI/MONAI`.

Profile: `everyday`.

## Input

- Issue number/URL from `/triage-issues`, and/or a short clinical/product story.
- Default feature: **RobustScaleIntensity** (median/IQR robust scaling) unless triage recommended a backup.

## Steps

1. Fetch the issue: `gh issue view <n> -R <fork>`.
2. Draft body sections (edit existing or create if missing):

### Problem / clinical story
Why robust (or asinh / tanh-squeeze) intensity prep helps medical imaging pipelines.

### Acceptance criteria
- Array transform `Foo` + dict `Food` under `monai/transforms/intensity/`
- Registered in `__all__` and public exports per peers
- Parameterized tests for array + `d`
- American English; Apache header; style via `runtests.sh --ruff`

### Non-goals
- Soft-clip (already covered by `ClipIntensityPercentiles` / `soft_clip`)
- GPU-only / networks work
- Upstream MONAI PR from this fork

### Touch paths
- `monai/transforms/intensity/array.py`
- `monai/transforms/intensity/dictionary.py`
- `tests/transforms/test_<name>.py` + `test_<name>d.py`

### Test expectations
- Happy path + ≥1 edge (constant volume / channel-wise / dtype) with `parameterized`

3. Apply with `gh issue edit <n> -R <fork> --body ...` or `gh issue comment`, or `gh issue create` if creating new.
4. Prefer labels `good first issue` and `kit-seed` when creating catalog issues.

## Output

Live issue URL only (no local markdown substitute).

## Stop when

Issue URL is updated and shown. Hand off to `/scaffold-transform`.
