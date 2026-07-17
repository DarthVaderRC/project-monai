# Kit-off weak evaluation run — 2026-07-17

## Status

**Complete (minimal)** — `AsinhIntensity` (array) and `AsinhIntensityd` (dictionary) appended and committed. No tests, CHANGELOG, or top-level `monai/transforms/__init__.py` re-exports.

## Commit

- **SHA:** `3f28f4147bad2b7ad6767e1edca378eb81879464`
- **Branch:** `eval/disc-kit-off-weak`
- **Message:** Add AsinhIntensity transform (array + dict)

## Implementation notes

| Check | Result |
|-------|--------|
| `np.float` vs `np.float32` | Uses **`np.float`** (deprecated alias; runtime fails on NumPy ≥1.24) |
| Dict wrapper | **Yes** — `AsinhIntensityd` with `AsinhIntensityD` / `AsinhIntensityDict` aliases |
| `__all__` registration | **Yes** — both `array.py` and `dictionary.py` |
| Top-level re-export | **No** — not added to `monai/transforms/__init__.py` |

## Import test result

```
python3 -c "from monai.transforms.intensity.array import AsinhIntensity; from monai.transforms.intensity.dictionary import AsinhIntensityd; print('import ok')"
```

**Import:** pass  
**Runtime `__call__`:** fail — `AttributeError: module 'numpy' has no attribute 'float'` (due to `np.float` usage)

## Quality summary

Working asinh idea at import level; weak dtype choice breaks execution on current NumPy; no torch path, no tests, no changelog, no package-level export.
