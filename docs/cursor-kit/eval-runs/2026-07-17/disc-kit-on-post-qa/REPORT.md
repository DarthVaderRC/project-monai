# Disc-kit-on post-QA evaluation — 2026-07-17

## Status

**Complete** — both planted defects fixed; scoped tests pass; all gates green.

## Source

- Branch: `eval/disc-kit-on-scaffold`
- Worktree: `.worktrees/eval-disc-kit-on`
- Base commit: `d9e6baec` — AsinhIntensity scaffold with planted defects
- QA commit: `05a703d6` — Fix AsinhIntensity QA defects and strengthen tests
- Skill: `/strengthen-tests` (QA, kit-on)

## Fixes applied

| Defect | Fix |
|---|---|
| Deprecated `np.float` dtype default in `AsinhIntensity` / `AsinhIntensityd` | Changed to `np.float32` in `array.py` and `dictionary.py` |
| Missing `AsinhIntensityd` registration | Added `AsinhIntensityd`, `AsinhIntensityD`, `AsinhIntensityDict` to `dictionary.py` `__all__` and `monai/transforms/__init__.py` imports |

## Test improvements

| Module | Before (stub) | After (hardened) |
|---|---|---|
| `test_asinh_intensity.py` | 7 tests (2 parameterized × 3 backends + invalid scale) | 14 tests (+ constant volume, channel-wise, dtype) |
| `test_asinh_intensityd.py` | 2 tests (manual `TEST_NDARRAYS` loops) | 14 tests (parameterized + constant volume, channel-wise, dtype, invalid scale) |
| **Total** | **9** | **28** |

New coverage: constant-volume edge case, channel-wise asinh, explicit dtype coercion, invalid-scale guard on dictionary wrapper, full `TEST_NDARRAYS` parameterization for `d` tests.

## Gate results

### Before QA (`d9e6baec`)

| Gate | Result | Detail |
|---|---|---|
| `check-deprecations.sh` | **FAIL** (exit 1) | 2 hits: `np.float` in `array.py:1201`, `dictionary.py:565` |
| Import `AsinhIntensityd` | **FAIL** (exit 1) | `AttributeError: module 'numpy' has no attribute 'float'` (blocks module load) |
| Scoped unittest | **FAIL** (blocked) | Import failure prevents test collection |

```text
$ bash docs/cursor-kit/scripts/check-deprecations.sh monai/transforms/intensity/array.py monai/transforms/intensity/dictionary.py
DEPRECATED  monai/transforms/intensity/array.py:1201:        dtype: DtypeLike = np.float,
DEPRECATED  monai/transforms/intensity/dictionary.py:565:        dtype: DtypeLike = np.float,
check-deprecations: 2 deprecated API usage(s) found.
```

### After QA (`05a703d6`)

| Gate | Result | Detail |
|---|---|---|
| `check-deprecations.sh` | **PASS** (exit 0) | `check-deprecations: clean (4 file(s) scanned).` |
| Import `AsinhIntensityd` | **PASS** (exit 0) | `AsinhIntensityd`, `AsinhIntensityD`, `AsinhIntensityDict` resolve |
| Scoped unittest | **PASS** (exit 0) | 14/14 array + 14/14 dictionary |

```text
$ python3 -m tests.transforms.test_asinh_intensity
Ran 14 tests in 0.007s — OK

$ python3 -m tests.transforms.test_asinh_intensityd
Ran 14 tests in 0.007s — OK
```

## Ship readiness

**ship_ready: true** — all gates pass (deprecations clean, import succeeds, 28/28 scoped tests pass).
