# Kit-off strong model eval — AsinhIntensity

**Status:** PASS  
**Branch:** `eval/disc-kit-off-strong`  
**Commit:** `8aa39ed033045ef0b98aedd59bb6a0d0d8b14340`

## Files changed

| File | Change |
|---|---|
| `monai/transforms/intensity/array.py` | Added `AsinhIntensity` class + `__all__` entry |
| `monai/transforms/intensity/dictionary.py` | Added `AsinhIntensityd` wrapper, `__all__` entries, `D`/`Dict` aliases |
| `monai/transforms/__init__.py` | Public re-exports for array + dict transforms |
| `tests/transforms/test_asinh_intensity.py` | Parameterized array tests + edge cases |
| `tests/transforms/test_asinh_intensityd.py` | Parameterized dict tests + zero-input edge case |
| `CHANGELOG.md` | `[Unreleased]` entry |

## Verification

### Deprecation check (manual grep; kit script unavailable — `docs/cursor-kit/` disabled)

Scanned touched files for `np.float`, `np.int`, `np.bool`, `torch.range`:

```
monai/transforms/intensity/array.py — clean
monai/transforms/intensity/dictionary.py — clean
tests/transforms/test_asinh_intensity.py — clean
tests/transforms/test_asinh_intensityd.py — clean
```

### Import check

```bash
PYTHONPATH=. python3 -c "from monai.transforms import AsinhIntensityd"
# exit 0, prints nothing
```

### Unit tests

```bash
PYTHONPATH=. python3 -m unittest tests.transforms.test_asinh_intensity tests.transforms.test_asinh_intensityd
# Ran 10 tests — OK
```

## Defect summary

| Planted defect | Present? |
|---|---|
| `np.float` default dtype | **No** — used `np.float32` |
| `AsinhIntensityd` missing from dictionary `__all__` | **No** — present in `__all__` along with `AsinhIntensityD` and `AsinhIntensityDict` |

## Notes

- `dtype: DtypeLike = np.float32` in both array and dict `__init__` (not deprecated `np.float`).
- `AsinhIntensityd` registered in `dictionary.py` `__all__`, aliased at module bottom, and re-exported from `monai.transforms`.
