# Discriminating eval run — AsinhIntensity (2026-07-17)

Task: *Add an intensity transform `AsinhIntensity` (array + dict) to MONAI.*

Transform chosen because it is **not** in model memory (unlike RobustScaleIntensity) and is listed as a scaffold backup in the kit.

## Arms

| Arm | Worktree | Commit | How |
|---|---|---|---|
| Kit-on scaffold | `.worktrees/eval-disc-kit-on` | `d9e6baec` | `/scaffold-transform` skill — **must plant** `np.float` + missing `__all__` |
| Kit-on post-QA | same | `05a703d6` | `/strengthen-tests` fixes both defects |
| Kit-off strong | `.worktrees/eval-disc-kit-off-strong` | `8aa39ed0` | Task sentence only; kit disabled; model may read neighbors |
| Kit-off weak | `.worktrees/eval-disc-kit-off-weak` | `3f28f414` | Task sentence only; constrained to not read neighbors/tests |

Scorer: `scripts/score_process.py --transform AsinhIntensity`

## Process scorecard (post-scaffold unless noted)

| Signal | Kit-on scaffold | Kit-on post-QA | Kit-off strong | Kit-off weak |
|---|---|---|---|---|
| `np.float` / deprecated API present | **YES** (planted) | NO | NO | **YES** (unplanned) |
| `AsinhIntensityd` missing from `__all__` | **YES** (planted) | NO | NO | NO |
| `check-deprecations.sh` fails | **YES** | NO | NO | **YES** |
| `from monai.transforms import AsinhIntensityd` fails | **YES** | NO | NO | **YES** (no `__init__` export + `np.float`) |
| Parameterized tests exist | YES (stub) | YES (28 pass) | YES (10 pass) | **NO** |
| **Ship-ready** (all gates pass) | **NO** | **YES** | **YES** | **NO** |

## What kit-on offers (when convention rubric saturates)

1. **Enforced defect → detect → fix loop.** Scaffold *must* leave tool-detectable ship-blockers; QA skill + gates fix them. Measured: 2/2 planted defects caught pre-QA; ship-ready only after `/strengthen-tests`.
2. **Floor for weak contributors.** Kit-off weak = broken import, deprecated API, no tests. Same gates would block merge **if run** — the kit makes running them mandatory in the persona workflow.
3. **Process observability.** Ledger + `/strengthen-tests` output vs hoping a strong model self-QA'd (kit-off strong never ran QA).

Kit-off strong reaching ship-ready at scaffold is expected for capable models — the kit's value is **variance reduction** and **workflow enforcement**, not beating a strong model on a single artifact score.

## Reports

- `disc-kit-on-scaffold/REPORT.md`
- `disc-kit-on-post-qa/REPORT.md`
- `disc-kit-off-strong/REPORT.md`
- `disc-kit-off-weak/REPORT.md`
