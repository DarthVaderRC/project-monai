# Disc-kit-on scaffold evaluation — 2026-07-17

## Status

**Complete** — `AsinhIntensity` (array) and `AsinhIntensityd` (dictionary) scaffolded with stub tests and both planted QA defects left in place for `/strengthen-tests`.

## Source

- Branch: `eval/disc-kit-on-scaffold`
- Worktree: `.worktrees/eval-disc-kit-on`
- Issue: https://github.com/DarthVaderRC/project-monai/issues/2 (AsinhIntensity backup catalog item)
- Commit: `d9e6baec` — Add AsinhIntensity transform (array + dict)

## Changes

| Path | Change |
|---|---|
| `monai/transforms/intensity/array.py` | Added `AsinhIntensity` class and `__all__` export |
| `monai/transforms/intensity/dictionary.py` | Added `AsinhIntensityd` wrapper and aliases (no `__all__` entry — planted) |
| `monai/transforms/__init__.py` | Exported `AsinhIntensity` only |
| `tests/transforms/test_asinh_intensity.py` | Stub array tests |
| `tests/transforms/test_asinh_intensityd.py` | Stub dictionary tests |

## Planted QA defects (intentional — do not fix in scaffold)

Planted: (1) deprecated `np.float` dtype default — caught by check-deprecations.sh/ruff; (2) missing `AsinhIntensityd` in `dictionary.py` `__all__` — caught at import/test time. Both for `/strengthen-tests`.

1. **Deprecated API:** `dtype: DtypeLike = np.float` in both `AsinhIntensity.__init__` and `AsinhIntensityd.__init__`.
2. **Registration gap:** `AsinhIntensityd` / `AsinhIntensityD` / `AsinhIntensityDict` omitted from `dictionary.py` `__all__` (class + alias lines present).

## Verification commands

### `check-deprecations.sh` (expected FAIL)

```text
$ bash docs/cursor-kit/scripts/check-deprecations.sh monai/transforms/intensity/array.py monai/transforms/intensity/dictionary.py
DEPRECATED  monai/transforms/intensity/array.py:1201:        dtype: DtypeLike = np.float,
            -> numpy alias np.float was removed (numpy>=1.24); use np.float32/np.float64 or float
DEPRECATED  monai/transforms/intensity/dictionary.py:565:        dtype: DtypeLike = np.float,
            -> numpy alias np.float was removed (numpy>=1.24); use np.float32/np.float64 or float
check-deprecations: 2 deprecated API usage(s) found.
```

Exit code: **1** (FAIL — as expected)

### Import probe (expected FAIL while gap open)

```text
$ python3 -c "from monai.transforms import AsinhIntensityd"
AttributeError: module 'numpy' has no attribute 'float'.
```

Exit code: **1** (FAIL — as expected; `np.float` default prevents module load; `AsinhIntensityd` also not exported from `monai.transforms`)

## Handoff

Run `/strengthen-tests` to fix deprecated `np.float` → `np.float32`, add `AsinhIntensityd` (+ aliases) to `dictionary.py` `__all__`, export from `monai/transforms/__init__.py`, and harden tests.
