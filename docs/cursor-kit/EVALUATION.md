# Evaluation: kit-off vs kit-on

Honest framing: **this is not a production ROI measurement.** It is a repeatable,
runnable comparison that shows *what the kit changes about a first contribution*.
The panel asked "what impact would you expect?" — this is how we'd answer with
evidence instead of a slide.

## Protocol (repeatable in ~10 min)

Same task both times: *"Add an intensity transform `RobustScaleIntensity` (array +
dict) to MONAI."*

1. **Kit-off run.** Fresh Agent chat with rules/hooks disabled (rename `.cursor/`
   to `.cursor.off/` or use a workspace without the kit) and no `monai-refs`/`@Docs`.
   Prompt with only the task sentence. Save the output.
2. **Kit-on run.** Restore the kit, `strict` profile, run `/scaffold-transform` on
   the seeded issue. Save the output.
3. **Score both** against the rubric below (objective, tool-checkable).
4. Optionally show `python3 docs/cursor-kit/scripts/ledger-report.py` for the
   kit-on run's stage/persona/deny activity.

## Rubric (each is pass/fail and mostly automatable)

| Convention | Checked by |
|---|---|
| Apache 2.0 header present | grep / review |
| `from __future__ import annotations` | grep |
| Array class + `MapTransform` `d` wrapper both present | import / review |
| `backend = [TransformBackends.TORCH, TransformBackends.NUMPY]` | grep |
| MetaTensor-safe (`convert_to_tensor(track_meta=...)` + `convert_to_dst_type`) | grep |
| Registered in `__all__` (array + dict) and `monai.transforms` re-exports | `python -c "from monai.transforms import ...d"` |
| `d`/`D`/`Dict` aliases | grep |
| No deprecated APIs (`np.float`, `torch.range`, ...) | `check-deprecations.sh` |
| Parameterized tests for array + `d`, incl. an edge case | run `unittest` |
| American English | review |
| Stays within approved boundaries (no `monai/networks` reads) | ledger denies |
| Changelog `[Unreleased]` entry | `check-changelog.sh` |

## Captured representative result

Numbers below are from a representative run; re-run the protocol to refresh. The
point is the *shape* of the gap, which is stable.

| Rubric item | Kit-off (task sentence only) | Kit-on (`/scaffold-transform`) |
|---|---|---|
| Apache header | missing | present |
| `annotations` future import | missing | present |
| Array + `d` wrapper | array only (no dict) | both |
| `backend` attribute | missing | present |
| MetaTensor-safe | no (raw numpy math) | yes |
| `__all__` + re-exports | not registered | registered (planted gap is intentional, QA-fixed) |
| Deprecated APIs | `np.float` used | none (gate clean after QA) |
| Tests | none | array + `d` parameterized + edge |
| Boundary respect | reads unrelated packages | strict denies logged |
| Changelog entry | none | `[Unreleased]` bullet |
| Score | ~2 / 12 | 12 / 12 (after QA fixes planted defects) |

### Illustrative kit-off output (typical, abbreviated)

```python
import numpy as np

class RobustScaleIntensity:
    def __init__(self, dtype=np.float):        # deprecated alias
        self.dtype = dtype
    def __call__(self, img):
        med = np.median(img)                    # numpy-only; breaks torch/MetaTensor
        iqr = np.percentile(img, 75) - np.percentile(img, 25)
        return (img - med) / iqr                # no d-wrapper, no header, no tests,
                                                # no registration, div-by-zero on constant input
```

### Kit-on output

See branch `golden/robust-scale-intensity` for the vetted array + `d` +
registration + tests that the kit steers the agent toward (Apache header,
`annotations`, `backend`, MetaTensor-safe, constant-volume guard, parameterized
tests, three-place registration).

## What this does and does not prove

- **Does:** the kit converts a first contribution from "plausible but wrong" to
  "convention-correct and testable," and makes boundary/deprecation/deploy gates
  observable.
- **Does not:** measure real ramp-time or defect-rate in the customer's codebase.
  That needs the frame in [`DEMO.md`](DEMO.md) (time-to-first-safe-PR, % first PRs
  failing conventions) run over real onboarding cohorts.
