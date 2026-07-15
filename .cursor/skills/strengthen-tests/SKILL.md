---
name: strengthen-tests
description: >-
  QA workflow: harden parameterized tests for a scaffolded intensity transform,
  ensure array + d coverage, and fix the planted dictionary __all__ registration
  gap. Use when the user runs /strengthen-tests.
disable-model-invocation: true
---

# /strengthen-tests (QA)

## Ledger

```bash
echo '{"event":"skill","decision":"start","skill":"strengthen-tests","persona":"QA","stage":"test"}' \
  | python3 .cursor/hooks/ledger_append.py
```

(end: `"decision":"end"`)

## Refs

- `@docs/cursor-kit/monai-refs/testing.md`
- `.cursor/rules/20-testing.mdc`
- Peers: `tests/transforms/test_scale_intensity.py`, `test_scale_intensityd.py`

## Steps

1. Identify paths from `/scaffold-transform` (or user-provided).
2. **Run the deprecated-API detector first** (this is the real signal, not a checklist):

```bash
bash docs/cursor-kit/scripts/check-deprecations.sh
```

   Fix every hit — the planted `np.float` dtype default must become `np.float32`
   in both the array and `d` classes. Re-run until clean (exit 0).
3. **Fix the registration gap:** ensure the `*d` class name is present in
   `monai/transforms/intensity/dictionary.py` `__all__` (and aliases exported if peers do).
   Confirm by importing: `python -c "from monai.transforms import <Name>d"`.
4. Scan for weak tests / missing `d` coverage / obvious anti-patterns.
5. Strengthen with `parameterized` cases (happy path + edge: constant volume, dtype, or channel-wise).
6. Run scoped tests only, e.g.:

```bash
python -m tests.transforms.test_<name>
python -m tests.transforms.test_<name>d
# or ./runtests.sh --quick --unittests if already in a good env
```

Stay under transforms/tests allowlist when `strict` is on.

## Output

- List of test improvements
- Confirmation `check-deprecations.sh` is clean (deprecated `np.float` fixed)
- Confirmation planted `__all__` gap is fixed (import succeeds)
- Pass/fail of scoped test commands

## Stop when

Planted gap fixed and scoped tests pass (or failures clearly reported). Do not open PRs (`/prep-for-ci`).
