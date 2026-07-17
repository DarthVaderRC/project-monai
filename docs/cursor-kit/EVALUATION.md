# Evaluation: kit-off vs kit-on

Honest framing: **this is not a production ROI measurement.** It is a repeatable,
runnable comparison that shows *what the kit changes about a first contribution*.
The panel asked "what impact would you expect?" — this is how we'd answer with
evidence instead of a slide.

**Artifacts for the 2026-07-17 run:** [`eval-runs/2026-07-17/`](eval-runs/2026-07-17/)
(scores JSON, excerpts, scorer, run notes).

## Protocol (repeatable in ~10 min)

Same task both times: *"Add an intensity transform `RobustScaleIntensity` (array +
dict) to MONAI."*

1. **Kit-off run.** Fresh Agent chat with rules/hooks disabled (rename `.cursor/`
   to `.cursor.off/` or use a workspace without the kit) and no `monai-refs`/`@Docs`.
   Prompt with only the task sentence. Save the output.
2. **Kit-on run.** Restore the kit, `strict` profile, run `/scaffold-transform` on
   the seeded issue (then QA / CI as in the demo spine). Save the output.
3. **Score both** against the rubric below (objective, tool-checkable) using
   `python3 docs/cursor-kit/eval-runs/2026-07-17/scripts/score_rubric.py <repo-root>`.
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
| No deprecated APIs (`np.float`, `torch.range`, ...) | `check-deprecations.sh` / scoped scan |
| Parameterized tests for array + `d`, incl. an edge case | run `unittest` |
| American English | review (RobustScale* class text only) |
| Stays within approved boundaries (no `monai/networks` reads) | source scan / ledger denies |
| Changelog `[Unreleased]` entry | `check-changelog.sh` / grep |

## Captured result — 2026-07-17 (measured)

### How this run was produced

| Arm | How |
|---|---|
| **Naive draft reference** | The historical junior/first-draft snippet (numpy-only, `np.float`). **Not an agent run** — kept as the baseline the kit was designed against. |
| **Kit-off (agent)** | Worktree `eval/kit-off-2026-07-17` @ `48b57f3c`. Kit disabled (`.cursor` / `docs/cursor-kit` / `AGENTS.md` moved aside). Constraints: no kit reads, no `golden/*` branches, no reading neighboring transform class bodies. Task sentence only. |
| **Kit-on** | Branch `golden/robust-scale-intensity` @ `e52ffce6` (vetted array + `d` + tests + registration). Changelog bullet applied locally to match full-spine `/prep-for-ci` parity (golden itself lacked the `[Unreleased]` line). |

Scorer: `eval-runs/2026-07-17/scripts/score_rubric.py` (exit 0 = 12/12).

### Scorecard (all 12 conventions)

| Convention | Naive draft | Kit-off (agent) | Kit-on (golden + CI changelog) |
|---|---|---|---|
| Apache 2.0 header present | FAIL | PASS | PASS |
| `from __future__ import annotations` | FAIL | PASS | PASS |
| Array class + `MapTransform` `d` wrapper both present | FAIL | PASS | PASS |
| `backend = [TransformBackends.TORCH, TransformBackends.NUMPY]` | FAIL | PASS | PASS |
| MetaTensor-safe (`convert_to_tensor` + `convert_to_dst_type`) | FAIL | PASS | PASS |
| Registered in `__all__` / `monai.transforms` re-exports | FAIL | PASS | PASS |
| `d`/`D`/`Dict` aliases | FAIL | PASS | PASS |
| No deprecated APIs | FAIL (`np.float`) | PASS | PASS |
| Parameterized tests for array + `d`, incl. edge case | FAIL | PASS (13 tests) | PASS (20 tests) |
| American English | PASS | PASS | PASS |
| Stays within approved boundaries (no `monai/networks`) | PASS | PASS | PASS |
| Changelog `[Unreleased]` entry | FAIL | PASS | PASS |
| **Score** | **2 / 12** | **12 / 12** | **12 / 12** |

### Which two did the naive draft pass?

1. **American English** — no British spellings in the snippet.  
2. **Stays within approved boundaries** — no `monai.networks` usage (and no out-of-bounds package imports).

Everything else fails (no header, no `annotations`, array-only / no `MapTransform` `d`, no `backend`, raw numpy math, not registered, no aliases, deprecated `np.float`, no tests, no changelog).

### Naive draft reference (2/12)

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

Saved at `eval-runs/2026-07-17/naive-draft/`.

### Kit-off vs kit-on (measured agents) — reading the 12/12 vs 12/12

A capable coding agent with MONAI priors, even **without** the kit and without reading neighbor class bodies, can still land a convention-correct implementation (**12/12**). The kit-on golden path also scores **12/12** on this rubric (with changelog added for CI parity).

So the automatable **final-artifact convention rubric saturates** for strong models. What the kit still uniquely demonstrates (see demo spine + ledger):

- **Process rails:** persona handoffs, planted registration/deprecation gaps caught by `/strengthen-tests`, strict boundary denies in the ledger.
- **Repeatability for juniors:** the naive draft (**2/12**) is what the kit was built to prevent when priors / neighbor-mirroring are weak.
- **Observability:** `ledger-report.py` stage/persona/deny counts on kit-on runs.

**Method notes**

- Apache header and `from __future__ import annotations` PASS when the class is appended to existing `array.py` / `dictionary.py` that already carry them (inherited module head) — true for both agent arms.
- Kit-off boundary was scored by source scan (hooks were disabled). Kit-on can additionally show ledger denies in a live strict session.
- Do not treat an old “~2/12 kit-off agent” headline as a measured agent score; that figure was the **naive draft**, now labeled as such.

### Kit-on pointer

See branch `golden/robust-scale-intensity` for the vetted array + `d` +
registration + tests. Excerpt: `eval-runs/2026-07-17/kit-on/RobustScaleIntensity.excerpt.py`.

## What this does and does not prove

- **Does:** make the convention gap vs a naive first draft **itemized and reproducible** (2/12 → 12/12), and show that a strong kit-off agent can also reach 12/12 — so panel claims must separate *junior/naive risk* from *strong-model finals*.
- **Does not:** measure real ramp-time or defect-rate in the customer's codebase.
  That needs the frame in [`DEMO.md`](DEMO.md) (time-to-first-safe-PR, % first PRs
  failing conventions) run over real onboarding cohorts. It also does not yet
  include trajectory evals (tool-call / multi-turn path scoring).

## Phase 1 archetype packs (loss / metric / network)

Each pack ships a verified reference implementation (kit-on baseline = conventions +
mypy-clean + tests pass): `LogCoshDiceLoss`, `MedianAbsoluteErrorMetric`,
`LayerScale`. Re-run this same scorecard per archetype when you need Phase-1
kit-off vs kit-on numbers; the 2026-07-17 measured run above covers the intensity
transform spine only.
