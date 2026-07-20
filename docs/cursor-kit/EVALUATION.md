# Evaluation: kit-off vs kit-on

Important: **this is not a production ROI measurement.** It is a repeatable, runnable comparison that shows *what the kit changes about a first contribution*.
This answers "what impact would you expect?" with evidence.

**Artifacts:** [`eval-runs/2026-07-17/`](eval-runs/2026-07-17/) (scorers, JSON scores, reports, excerpts).

---

## Two evaluation layers (use both in the panel)

| Layer | Question it answers | Saturates for strong models? |
|---|---|---|
| **A. Process / QA rubric** (primary) | Do tool-detectable ship-blockers get planted, caught, and fixed through the persona workflow? | **No** — kit-on scaffold deliberately fails until QA |
| **B. Convention rubric** (secondary) | Does the final artifact match MONAI house style? | **Yes** — strong kit-off agents can hit 12/12 |

Lead with **Layer A** first. Use **Layer B** to show the naive/junior floor (2/12 draft) and why convention checklists alone are insufficient.

---

## Layer A — Process rubric (discriminating)

**Task:** *Add an intensity transform `AsinhIntensity` (array + dict) to MONAI.*

**Why AsinhIntensity:** not already in the repo; less memorized than RobustScaleIntensity; listed as a scaffold backup in `/scaffold-transform`.

**Scorer:** `python3 docs/cursor-kit/eval-runs/2026-07-17/scripts/score_process.py <repo-root> --transform AsinhIntensity --stage post_scaffold|post_qa`

### Protocol

1. **Kit-on scaffold** — run `/scaffold-transform` (strict). Skill **requires** two planted, tool-detectable defects: `np.float` dtype default + `AsinhIntensityd` missing from `dictionary.py` `__all__`. Do not fix in this stage.
2. **Kit-on QA** — run `/strengthen-tests`. Fix both defects; strengthen tests; confirm gates pass.
3. **Kit-off strong** — kit disabled; task sentence only; model may read neighbors (control for capable agents).
4. **Kit-off weak** — kit disabled; task sentence only; constrained to not read neighbors/tests (junior simulation).

### Measured result — 2026-07-17

| Signal | Kit-on scaffold `d9e6baec` | Kit-on post-QA `05a703d6` | Kit-off strong `8aa39ed0` | Kit-off weak `3f28f414` |
|---|---|---|---|---|
| Deprecated `np.float` present | **YES** (planted) | NO | NO | **YES** (unplanned) |
| `AsinhIntensityd` missing from `__all__` | **YES** (planted) | NO | NO | NO |
| `check-deprecations.sh` fails | **YES** | NO | NO | **YES** |
| Import `AsinhIntensityd` fails | **YES** | NO | NO | **YES** |
| Tests exist + pass | stub / fail | **28 pass** | **10 pass** | **none** |
| **Ship-ready** | **NO** | **YES** | **YES** (no QA ran) | **NO** |

Full run notes: [`eval-runs/2026-07-17/disc-RUN.md`](eval-runs/2026-07-17/disc-RUN.md).

### What kit-on offers when Layer B shows 12/12 = 12/12

The convention rubric can **saturate** for strong models (see Layer B below). Kit-on still adds:

1. **Mandatory defect → gate → fix loop.** Scaffold plants ship-blockers; `check-deprecations.sh` and import tests fail **before** QA; `/strengthen-tests` is the measured fix path. Strong kit-off agents skip this entirely if they happen to code correctly first try.
2. **Floor for weak contributors.** Kit-off weak shipped deprecated `np.float`, no tests, broken public import — **not ship-ready**. The kit's QA skill and gates are the enforced backstop; without them, merge depends on reviewer luck.
3. **Persona observability.** Ledger + explicit QA handoff vs an opaque one-shot agent commit.

*The kit doesn't always beat a strong model on a static checklist — it **guarantees** the SDLC gates run and **raises the floor** for everyone else.*

---

## Layer B — Convention rubric (12 items)

Same task (historical run used RobustScaleIntensity): *"Add an intensity transform `RobustScaleIntensity` (array + dict) to MONAI."*

**Scorer:** `python3 docs/cursor-kit/eval-runs/2026-07-17/scripts/score_rubric.py <repo-root>`

| Convention | Checked by |
|---|---|
| Apache 2.0 header present | grep / review |
| `from __future__ import annotations` | grep |
| Array class + `MapTransform` `d` wrapper both present | import / review |
| `backend = [TransformBackends.TORCH, TransformBackends.NUMPY]` | grep |
| MetaTensor-safe (`convert_to_tensor(track_meta=...)` + `convert_to_dst_type`) | grep |
| Registered in `__all__` (array + dict) and `monai.transforms` re-exports | import |
| `d`/`D`/`Dict` aliases | grep |
| No deprecated APIs | `check-deprecations.sh` |
| Parameterized tests for array + `d`, incl. an edge case | `unittest` |
| American English | review |
| Stays within approved boundaries (no `monai/networks` reads) | source scan / ledger |
| Changelog `[Unreleased]` entry | grep |

### Measured result — RobustScaleIntensity (2026-07-17)

| Arm | Score | Notes |
|---|---|---|
| Naive draft reference | **2/12** | Passes only American English + boundary; uses `np.float`, numpy-only math |
| Kit-off agent (strong, constrained) | **12/12** | No kit; still convention-complete from priors |
| Kit-on golden file | **12/12** | Human-curated reference, not a live agent run |

**Which two did the naive draft pass?** American English; stays within boundaries (no `monai.networks`).

The old "~2/12 kit-off agent" headline referred to this **naive draft**, not a measured agent run.

**Saturation warning:** several rows are inherited when appending to existing `array.py` (header, `annotations`) or correlated (backend + MetaTensor + aliases). Treat Layer B as a **style checklist**, not the kit's primary value proof.

Naive draft + excerpts: `eval-runs/2026-07-17/naive-draft/`.

---

## What this does and does not prove

**Does prove (with Layer A):**

- Planted, tool-detectable defects are caught by kit gates before merge.
- `/strengthen-tests` closes the loop to ship-ready.
- Weak kit-off contributions fail ship-ready; kit-on workflow succeeds.

**Does not prove:**

- Real ramp-time or cohort defect-rate (see [`DEMO.md`](DEMO.md) measurement frame).
- That kit-on beats kit-off strong on every convention row (it often won't).

---

## Layer T — TDD / spec-critic gate (hard gate before scaffold)

**Question:** *Did the session satisfy SPEC + failing tests + approved spec review before any scaffold skill ran?*

**Scorer:** `python3 docs/cursor-kit/scripts/score_tdd_gate.py [--issue <n>] [--test-path <path>]`

**Artifacts (per issue `n`):**

| Artifact | Role |
|---|---|
| `docs/cursor-kit/work/<n>/SPEC.md` | Plan output from `/plan-feature` (required headings) |
| `tests/transforms/test_*.py` (Layer T module) | Red tests with `Layer T red` marker — **required static convention**; gate checks file presence + marker text, **does not execute pytest** |
| `docs/cursor-kit/work/<n>/SPEC-REVIEW.md` | Critic output; **completion proof = file exists + last non-empty line is `Verdict: Approve` or `Verdict: Request changes`** |
| Ledger row | Kit-owned marker: `event=subagentStart`, `subagent_type=spec-critic`, `source=critique-spec` — emitted **after** SPEC-REVIEW exists; delegation/completion signal the scorer trusts (not Cursor's `subagent_audit` payload) |

**Hard gate:** `/scaffold-*` skills run `score_tdd_gate.py` first and **refuse** if exit ≠ 0. All required checks must pass before production code edits.

**Model pin:** Spec-critic is an agent with `model: cursor-grok-4.5-high-fast` — the only enforceable model routing in v1. Verify on the critic agent UI during live runs.

**Prod-write restraint:** The critic must not edit `monai/**`; enforcement is **prompt-only** (agent is not `readonly` because it writes SPEC-REVIEW). Everyday boundary profile does not confine the critic to kit paths — a misbehaving critic could still touch production files.

**Relationship to other layers:**

| Layer | Layer T interaction |
|---|---|
| **A (process)** | Unchanged — planted defects (`np.float`, `__all__` gap) still come from scaffold; Layer T gates *before* scaffold, not the QA fix loop |
| **C (trajectory)** | **Requires** kit-owned critic marker (`source=critique-spec` after SPEC-REVIEW exists). Cursor `subagent_audit` `subagentStart` rows are optional corroboration once observed live. **Dual `subagentStart` rows** (kit marker + Cursor audit) per critic dispatch are expected — Layer C filters on `source` so they do not double-count |

---

## Layer C (Trajectory rubric)

**Question:** *Did the session follow the contribution spine — personas, skills, boundaries — not just produce a good diff?*

**Scorer:** `python3 docs/cursor-kit/eval-runs/2026-07-17/scripts/score_trajectory.py [ledger.jsonl]`

Defaults to the latest `sessionStart` slice of `.cursor/usage/ledger.jsonl`. Archive a rehearsal copy:

```bash
cp .cursor/usage/ledger.jsonl docs/cursor-kit/eval-runs/2026-07-17/kit-spine-$(date +%Y%m%d).jsonl
python3 docs/cursor-kit/eval-runs/2026-07-17/scripts/score_trajectory.py \
  docs/cursor-kit/eval-runs/2026-07-17/kit-spine-$(date +%Y%m%d).jsonl \
  --session all --json-out docs/cursor-kit/eval-runs/2026-07-17/kit-spine-scores.json
```

**Required checks (11):** all seven kit-spine skills logged (`start`), correct order (including `/critique-spec` after plan), strict read deny on out-of-bounds path, scaffold under strict, kit-owned spec-critic marker (`source=critique-spec`).

**Optional checks (5):** PM under everyday, transform-edit nudge, gh deny in strict, prompt coach, subagent audit (`--require-subagent` to promote subagent to required).

**Reference fixture:** [`fixtures/kit-spine-kit-on.jsonl`](eval-runs/2026-07-17/fixtures/kit-spine-kit-on.jsonl) — target `ship_ready_trajectory: true` after Task 7 fixture refresh (pre-Layer T fixture currently scores 9/11).

*Layer A proves gates catch defects; Layer C proves the multi-persona workflow actually ran.*

Human dashboard (counts + score): `python3 docs/cursor-kit/scripts/ledger-dashboard.py`.

---

## Phase 1 archetype packs (loss / metric / network)

Each pack ships a verified reference implementation (kit-on baseline = conventions + mypy-clean + tests pass):

| Archetype | Class | Neighbor | Pack surfaces |
|---|---|---|---|
| Loss | `LogCoshDiceLoss` | `DiceLoss` | `50-losses.mdc`, `monai-refs/losses.md`, `/scaffold-loss` |
| Metric | `MedianAbsoluteErrorMetric` | `MAEMetric` | `60-metrics.mdc`, `monai-refs/metrics.md`, `/scaffold-metric` |
| Network block | `LayerScale` | `MLPBlock` / `aspp.py` | `70-networks.mdc`, `monai-refs/networks.md`, `/scaffold-network` |

Re-run **Layer A** (process scorer adapted per archetype) when you need pack-level kit-off vs kit-on numbers; intensity transform runs above cover the contribution spine.
