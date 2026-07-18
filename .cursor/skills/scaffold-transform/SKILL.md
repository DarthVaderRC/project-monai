---
name: scaffold-transform
description: >-
  Engineer workflow: implement a catalog intensity Transform + MapTransform d
  wrapper from a fork GitHub issue under monai/transforms/intensity/, with stub
  tests and one planted QA gap. Use when the user runs /scaffold-transform.
  Prefer MONAI_CURSOR_BOUNDARY=strict.
disable-model-invocation: true
---

# /scaffold-transform (Engineer)

## Ledger

```bash
echo '{"event":"skill","decision":"start","skill":"scaffold-transform","persona":"engineer","stage":"build","profile":"strict"}' \
  | python3 .cursor/hooks/ledger_append.py
```

(end: `"decision":"end"`)

## Profile

Prefer **`MONAI_CURSOR_BOUNDARY=strict`**. Stay in transforms + kit paths. Consult:

- `@docs/cursor-kit/monai-refs/transforms-array-dict.md`
- `@docs/cursor-kit/monai-refs/contributing-checklist.md`
- `@Docs` (MONAI stable) for API clarification

Do **not** read `monai/networks/**` or unrelated packages. If the user asks you to probe out-of-bounds, attempt it once to demonstrate the deny hook, then continue in-bounds.

## Input

Issue number/URL (primary: RobustScaleIntensity; backups: AsinhIntensity, TanhSqueezeIntensity).

## Implementation

1. Read peers: `NormalizeIntensity` / `ScaleIntensity` and their `*d` wrappers in intensity `array.py` / `dictionary.py`.
2. Append **array** class + **dict** `d` class (aliases `D` / `Dict`) matching neighbors.
3. Register in file `__all__` and package exports as peers require.
4. Apache header; `from __future__ import annotations`; Google docstrings.
5. Add stub tests under `tests/transforms/` (array + `d`), copying `test_scale_intensity.py` patterns lightly.

### Behavior sketches

| Transform | Intent |
|---|---|
| `RobustScaleIntensity` | Scale using median and IQR (outlier-resistant vs mean/std) |
| `AsinhIntensity` | `asinh`-based compression of dynamic range |
| `TanhSqueezeIntensity` | `tanh` squeeze of intensities into a bounded range |

### Planted QA defects (required — intentional, tool-detectable training signals)

Plant these two so `/strengthen-tests` fixes issues surfaced by tooling, not a checklist:

1. **Deprecated API (headline).** Use the removed numpy alias `np.float` as the
   `dtype` default instead of `np.float32` in the **array** class, i.e.
   `dtype: DtypeLike = np.float` (and mirror in the `d` wrapper). This is caught by
   `bash docs/cursor-kit/scripts/check-deprecations.sh` and by ruff — a realistic
   model mistake that maps directly to requirement #2 ("catch deprecated APIs").
2. **Registration gap.** Leave the `*d` class out of `dictionary.py`'s `__all__`
   (add the class + aliases, but omit the `__all__` entry). This surfaces at
   import/test time (a real `ImportError`/failing test), not as a style nit.

- Do **not** fix either in this skill run.
- Handoff note must say: "Planted: (1) deprecated `np.float` dtype default — caught
  by check-deprecations.sh/ruff; (2) missing `*d` in `dictionary.py` `__all__` —
  caught at import/test time. Both for `/strengthen-tests`."

## Stop when

Code + stub tests exist, planted `__all__` gap remains, and handoff note cites the issue URL + planted defect. Do not run full CI (that is `/prep-for-ci`).
