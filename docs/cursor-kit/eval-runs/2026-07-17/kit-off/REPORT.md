# Kit-off evaluation run — 2026-07-17

## Status

**Complete** — `RobustScaleIntensity` (array) and `RobustScaleIntensityd` (dictionary) implemented, tested, and committed.

## Commit

- **SHA:** `48b57f3c`
- **Branch:** `eval/kit-off-2026-07-17`
- **Message:** Add RobustScaleIntensity transform (array + dict)

## Files changed

| File | Change |
|------|--------|
| `monai/transforms/intensity/array.py` | Added `RobustScaleIntensity` class and `__all__` export |
| `monai/transforms/intensity/dictionary.py` | Added `RobustScaleIntensityd` wrapper, aliases, and `__all__` exports |
| `monai/transforms/__init__.py` | Re-exported array and dict transforms |
| `CHANGELOG.md` | `[Unreleased]` entry for new transform |
| `tests/transforms/test_robust_scale_intensity.py` | Array transform tests (8 cases) |
| `tests/transforms/test_robust_scale_intensityd.py` | Dictionary transform tests (5 cases) |

## Attestation

Did not read kit, golden branches, or neighboring transform implementations.

## Test result

13/13 tests passed.

## Rubric score (2026-07-17)

**12/12** — see `scores.json` (scorer exit 0).
