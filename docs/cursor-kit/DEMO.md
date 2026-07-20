# Runbook — MONAI Cursor onboarding kit

Session script for the `project-monai` workspace on branch
`productization-plugin-monorepo` (plugin-shaped thin consumer). Fallback demo
branch if plugins are unavailable: `cursor-onboarding-kit`.

**Push to origin is not needed** (keep kit local until then).

### Pre-flight (plugins)

1. Install plugins from the sibling `cursor` monorepo (see that repo’s `README.md`):
   ```bash
   mkdir -p ~/.cursor/plugins/local
   cp -R /path/to/cursor/plugins/platform-core ~/.cursor/plugins/local/platform-core
   cp -R /path/to/cursor/plugins/pack-monai ~/.cursor/plugins/local/pack-monai
   ```
2. Cursor **Customize** → enable **platform-core** + **pack-monai** (User-scoped is OK).
3. New Agent chat on `project-monai` → confirm pack rules inject (e.g. Pack spike / transform rules).
4. If `.cursor/refs/` is empty/missing: run `/init-pack`.

---

## Narrative (judgment — read this first)

This section is what the exercise grades as *judgment about what’s worth solving*, not only a working spine. The live walkthrough proves the artifact; this proves *why*.

**Agent topology (say once):** Each persona drives their own stage and hands off via artifacts (issue → diff+note → verdict). No single command runs the whole SDLC — that would be solo-dev vibe-coding, not a multi-persona org. Subagents are used *within* a stage for context isolation (e.g. background `/review-contribution`), never to jump personas.

### 45-minute agenda

| Block | Time | Goal |
|---|---|---|
| Judgment | 5–8 min | Business pain, prioritize/skip, tooling choices, how we’d measure value |
| Live spine | 20–25 min | Triage → plan → Layer T → critique → strict deny → scaffold → QA → CI → review |
| Limitations / next | 5 min | Honesty + productization next (plugin core vs packs, agents) |

**Trim talking track:** do not narrate every layer equally. Deep-dive shared rails (rules/hooks/refs) + one deny + one planted QA fix. Skills are thin orchestrators — say that once.

### Business problem

Platform onboards engineers onto a **convention-heavy** MONAI library; **ramp is slow** and PRs drift from standards. They care about the **full SDLC** (plan → design → build → test → review → CI), and want **one solution** PM / eng / QA / DevOps can share.

**KPI to attack:** *time-to-first-safe-merge* (scoped change, green checks, DCO) and *convention consistency* on early PRs.

### Why MONAI + transforms (not a toy)

- Encodable conventions (array + `d`, `__all__`, Apache header, American English, lint stack).
- CPU-runnable transform tests → live walkthrough fits 45 minutes.
- Clinical PM stories + dense tests + real CI → multi-persona without faking SDLC.

### Prioritize / skip

| Build first | Skip / defer (v1) |
|---|---|
| Plugins (platform-core + pack-monai) + thin consumer | Public Marketplace publish |
| Rules + two-profile hooks + `/scaffold-transform` | Companion-repo installer |
| QA + DevOps skills; PM triage/plan | Custom docs/boundary MCP |
| Pack refs SSOT → `.cursor/refs/` + `@Docs` | Custom Mode |
| sync-check + CODEOWNERS + kit CI | GPU/distributed automation |
| Layer D judge (additive) + Layer E `model_id` | Full billing/token invoice |

**Equal depth vs live sequencing:** all five requirements are designed in; the **live** path is short on purpose (presentation choice, not a depth cut).

### Tooling choices (defend live)

| Choice | Why |
|---|---|
| Approach A (in-repo kit) | Reliable walkthrough; versioned with the fork |
| `@Docs` + `.cursor/refs/` | Official API + owned conventions; no custom docs MCP |
| Hooks (strict/everyday) | Honest boundary enforcement for req #3 |
| `AGENTS.md` only | Portable working guidance without Custom Mode |
| Cursor-estimated ledger | Stage/persona observability; not fake billing precision |
| Live fork issues (A) + upstream scan (D) | Runnable PM artifact + authentic backlog optics |

### How we measure value (honest: not measured yet)

Do **not** claim production ROI. Propose the frame platform would run:

| Outcome | Proxy metric | Kit lever |
|---|---|---|
| Faster ramp | Time-to-first-safe-PR | Scaffold + refs + rules cut “framework syntax” days |
| Less convention rework | % first PRs failing style/header/`__all__`/missing `d` tests | Rules + QA path + sync-check CI |
| Fewer uncaught gaps | Review/CI comments on covered anti-patterns | `/strengthen-tests`, `/review-contribution`, post-edit nudges |
| Multi-role leverage | Non-eng runs of PM/QA skills | Ten `/` skills on shared rails (seven in live contribution spine) |
| Safe autonomy | Boundary deny vs escape (ledger) | Strict/everyday hooks |
| Cost awareness | Cursor usage + ledger stage counts | Estimated; not an invoice |

**Spoken value line:** *“New engineers waste days on framework syntax and silent convention misses. We automate boilerplate safely so they focus on medical/business logic; hooks and QA cut missed tests and out-of-bounds context. Platform measures ramp time and first-PR defect rate — not LOC.”*

**Evidence, not a slide:** [`EVALUATION.md`](EVALUATION.md) has two layers. **Lead with Layer A (process):** AsinhIntensity run — kit-on scaffold fails ship-ready (planted `np.float` + `__all__` gap), gates catch both, `/strengthen-tests` → ship-ready; kit-off weak stays broken; kit-off strong skips QA entirely. **Layer B (conventions):** naive draft **2/12**; strong models saturate at 12/12 — so say the kit **guarantees gates + raises the floor**, not “beats GPT on a checklist.”

### Exercise “looking for” → where you show it

| Criterion | Where in the session |
|---|---|
| Judgment / business impact | This narrative + prioritize/skip |
| Thinking process / options weighed | Tooling table + rejected companion-repo/MCP |
| SDLC breadth | Spine triage → review |
| Multi-audience | Seven `/` skills on live spine; PM live issues |
| Runnable artifact | Live spine (not slides) |
| Honesty / limitations | Closing block |
| Maintainability without you | sync-check CI + README + CODEOWNERS |

### Sync-check = “team owns this” (detection half)

Ownership is not the script alone. **Versioned kit + CODEOWNERS + sync gate** so when CONTRIBUTING/paths drift, CI fails instead of silently teaching wrong norms. README tells the team how to bump rules/refs.

### Productization (shipped on this branch)

The **content pack** is MONAI-specific (correct for the stand-in). Shipping “this consumer folder as-is” as a Marketplace plugin would be wrong for other libs — that’s why we split.

The split is **by reader** — Cursor has no cross-plugin path resolution, so a core hook can't read a file inside the pack plugin:

| Piece | Portable? | Contents | How it reaches the agent |
|---|---|---|---|
| Platform core (plugin, Required) | Yes | Hook **engine**, library-agnostic skill *shells*, spec-critic agent, sync-check / score / Layer D runners, ledger | Enable in Customize |
| Library pack (plugin, Default Off) | No | MONAI rules, `refs/` SSOT, `scaffold-*`, pack.config **schema + example** | Cursor **injects** rules/skills; refs read from consumer `.cursor/refs/` |
| Consumer (this repo) | n/a | `.cursor/pack.config.json` instance + `boundary-profile` + materialized `refs/` + `usage/` | Hooks read config via `CURSOR_PROJECT_DIR` |

**This branch already physicalizes that split** in the sibling `cursor` monorepo (`platform-core` + `pack-monai`). Consumer narrative + seam notes live in [`productization/`](productization/).

v1 enablement is **manual** in Customize; `workspaceOpen → pluginPaths` is an upgrade (already in platform-core — reload Cursor to exercise). Spec-critic is the only `model:`-enforced agent pin; broader standing-agent personas stay deferred.

**Strong answers (copy):**

- *“Platform-core is the portable Required plugin; pack-monai is Default-Off and swapped per library.”*
- *“Config splits by reader: Cursor injects the pack's rules/skills; hooks read the consumer's `pack.config.json` via `CURSOR_PROJECT_DIR`.”*
- *“Adding DIFFUSER is a new pack folder + marketplace entry + that repo's config instance — the engine is written once.”*
- *“LOC isn’t the KPI — ramp time and convention adherence are.”*
- *“Upstream good-first issues are context; writable work stays on the fork catalog.”*

### Limitations (say out loud)

- Hooks ≠ OS sandbox; determined users can still escape outside Cursor.
- Medical/scientific correctness needs human review.
- Rule drift possible — mitigated by sync-check CI, not eliminated.
- Ledger is Cursor-estimated stage metering, not billing.
- CPU transform scope only in the live path.

### Hook-coverage honesty (verified against Cursor's hooks contract)

Grounded in the actual event schemas, not assumptions:

- `beforeReadFile` gates the Read tool and returns one `permission` for the
  primary `file_path`. It also *sees* prompt `attachments` (`@`-mentioned files /
  rules) — we log out-of-bounds ones to the ledger, but a hook **cannot strip
  already-attached context**. So strict-mode denial governs agent reads, not
  context you hand it directly.
- `beforeReadFile` output honors `permission` + `user_message` only (no
  `agent_message`), so a denied read shows the user a message but doesn't coach
  the agent inline.
- `afterFileEdit` returns **no** actionable output; the "run style/tests/deprecation
  checks" nudge is surfaced via `postToolUse` (`additional_context`) instead.
- `beforeSubmitPrompt` can only **block** with a message (no context injection),
  so the convention coach blocks only high-confidence anti-patterns (e.g. soft-clip).
- `subagentStart/Stop` are audited to the ledger; the kit allows delegation and
  observes it rather than gating it in v1.
- `beforeShellExecution` uses **`failClosed: false`**. When the hook process
  runs, strict/everyday deny/allow still apply. But Cursor can fail to *spawn*
  the hook (Agents Window race: “Shell execution is not available in the worker
  extension host”); with `failClosed: true` that hard-locks Shell for the whole
  chat and agents flee to MCP/browser. Fail-open on spawn failure keeps the PM
  `gh` path alive; policy denials when the script runs are unchanged.
  `beforeReadFile` stays `failClosed: true`. If Shell still wedges: **Developer:
  Reload Window**, then warm up with `echo ok && gh auth status` before
  `/plan-feature`.

---

## Pre-flight

- [ ] Open folder: `/Users/DineshGawande/Code/project-monai` (not the planning repo)
- [ ] Branch: `cursor-onboarding-kit` (push to fork **only when the demo starts**, if required)
- [ ] `gh auth status` OK; Issues enabled on fork
- [ ] `@Docs` indexed: https://docs.monai.io/en/stable/
- [ ] Customize → Rules shows `00`–`70`; Skills show ten `/` workflows (live spine uses seven — see table below)
- [ ] `echo everyday > .cursor/boundary-profile`
- [ ] Optional: `bash docs/cursor-kit/scripts/sync-check.sh` exits 0
- [x] Seeded issues present:

| Issue | # | URL |
|---|---|---|
| RobustScaleIntensity (primary) | **1** | https://github.com/DarthVaderRC/project-monai/issues/1 |
| AsinhIntensity (backup) | **2** | https://github.com/DarthVaderRC/project-monai/issues/2 |
| TanhSqueezeIntensity (backup) | **3** | https://github.com/DarthVaderRC/project-monai/issues/3 |
| Decoy (networks) | **4** | https://github.com/DarthVaderRC/project-monai/issues/4 |

**Triage narrative (A+D):** `/triage-issues` may **read-only** scan upstream `Project-MONAI/MONAI` `good first issue`s for context, then **recommend only** a fork catalog issue (#1–#3). Never create/edit upstream.

---

## Contribution spine

| Step | Action | Artifact | Spoken line (judgment) |
|---|---|---|---|
| 1 | `/triage-issues` | Ranked table | Multi-audience PM; A+D = real backlog optics + seeded fork catalog (`kit-seed`) |
| 2 | `/plan-feature` | Live issue + `docs/cursor-kit/work/<n>/SPEC.md` | Runnable PM artifact — not markdown theater |
| 3 | Write Layer T failing tests | Red `tests/transforms/test_*.py` with `Layer T red` marker | TDD before impl — gate checks convention, not pytest |
| 4 | `/critique-spec` | `SPEC-REVIEW.md` with `Verdict: Approve` | Hard-gated spec review; prod-write restraint is prompt-only (boundary does not stop `monai/**` if critic misbehaves) |
| 5 | `echo strict > .cursor/boundary-profile` | Boundary on | Req #3 — approved boundaries |
| 6 | Deny probe | Hook deny | Show teeth: agent cannot quietly leave transforms |
| 7 | `/scaffold-transform` (runs `score_tdd_gate` first) | Code + planted gap | Req #1 — correct first contribution without reading the whole repo |
| 8 | `/strengthen-tests` | Gap fixed | Req #2 — catch mistakes before human review |
| 9 | everyday → `/prep-for-ci` | CI map | Path to production; sync-check CI = ownable kit; release-train aware |
| 10 | `/review-contribution` | Verdict | Reviewer persona on the same rails (not Cursor `/review` Bugbot) |

### Layer T (hard gate)

Before scaffold: SPEC.md + failing tests + `/critique-spec` → `Verdict: Approve` (last line).
`score_tdd_gate.py` must exit 0; scaffold skills refuse otherwise. Spec-critic runs as
an agent with `model: cursor-grok-4.5-high-fast` pinned (only enforceable model routing in v1 —
verify in the agent UI on live runs). Critic ledger proof is kit-owned
(`source=critique-spec` after SPEC-REVIEW exists), not Cursor's subagent audit payload
(optional corroboration only). Prod-write restraint is prompt-enforced. Layer T red
marker is a required static convention.

**Optional after review (do not block the spine):** Layer D
`python3 docs/cursor-kit/scripts/llm_judge.py --issue <n> --prompt-only` (or `--dry-run`
template). Layer E: ledger may carry `model_id` when known — cost/routing only, not quality.

### Planted defect

Scaffold intentionally omits the `*d` class from `dictionary.py` `__all__`. QA skill fixes it.

### Backup switch

If primary is blocked, triage → AsinhIntensity (#2), then TanhSqueezeIntensity (#3). Same spine.

### Golden fallback (if live scaffold drifts)

A vetted `RobustScaleIntensity` (array + `d` + 20 passing tests) lives on branch
`golden/robust-scale-intensity` (never merged into the kit branch, so the live
scaffold is genuine). Recover instantly without leaving the kit branch:

```bash
git checkout golden/robust-scale-intensity -- \
  monai/transforms/intensity/array.py \
  monai/transforms/intensity/dictionary.py \
  monai/transforms/__init__.py \
  tests/transforms/test_robust_scale_intensity.py \
  tests/transforms/test_robust_scale_intensityd.py
# Strict-mode-safe (matches /strengthen-tests); do not use `python -m unittest ...` while strict is on.
python3 -m tests.transforms.test_robust_scale_intensity
python3 -m tests.transforms.test_robust_scale_intensityd
```

Frame it honestly to the panel: "the scaffold is generated live; this is a
tested safety net so a model hiccup doesn't derail the walkthrough."

### Profile switch

```bash
echo strict > .cursor/boundary-profile
echo everyday > .cursor/boundary-profile
```

Read/deny hooks honor the file immediately. Prefer a fresh Agent chat after flips for clean narrative.

---

## Copy-paste prompt bank

Use these in **Agent chat** with the `project-monai` workspace.

Each prompt has a short talk track: **Under the hood** (what should fire),
**You should see** (good outcome), **Say out loud** (judgment line),
**Fail / thrash** (kit or model misfire — stop and recover).

Prefer **`everyday`** unless a beat says otherwise. Fresh Agent chat after
profile flips keeps the narrative clean.

### A. Rules / docs smoke

```text
With @monai/transforms/intensity/array.py in context: which project rules apply, and what is the array vs dict (d) pattern for a new intensity transform?
```

- **Under the hood:** `@array.py` attaches; `00-repo-guardrails.mdc` (`alwaysApply`) + `10-transforms.mdc` (globs `monai/transforms/**`); optional read of `.cursor/refs/transforms-array-dict.md`. `beforeReadFile` allows `.cursor/` + transforms paths.
- **You should see:** Names those rules; summarizes array (`Transform` / `RandomizableTransform` in `intensity/array.py`) vs dict (`MapTransform` + aliases in `intensity/dictionary.py`) + three registration sites.
- **Say out loud:** “Rules are path-scoped convention packs — the agent doesn’t need the whole repo to get the pattern right.”
- **Fail / thrash:** Hunting `10-transforms-intensity.mdc`; fighting hooks to read pack rules; opening `monai/networks`.

```text
Using @Docs and @.cursor/refs/transforms-array-dict.md — how do I add a MapTransform wrapper for an intensity transform? Do not open monai/networks.
```

- **Under the hood:** `@Docs` + owned ref; same transform rules as above; agent should stay on allowlist without a deny probe.
- **You should see:** Wrapper recipe from the ref (`keys`, hold array transform, `key_iterator`, `*d` / `*D` / `*Dict` aliases) — not a networks digression.
- **Say out loud:** “Official docs for API; `.cursor/refs/` for our non-negotiable conventions — no custom docs MCP.”
- **Fail / thrash:** Reads `monai/networks/**`; invents SoftClipIntensity; ignores the ref file that was attached. Without “*Do not open monai/networks*” agents often wander into unrelated packages “for
  context.”

### B. PM — triage

Profile: **`everyday`** (`gh` needed).

```text
/triage-issues
```

- **Under the hood:** Skill `/triage-issues` (platform-core) (`disable-model-invocation`); ledger `skill` start/end (persona PM, stage triage); `gh` against upstream (read-only) + fork; `00-repo-guardrails` fork-only remotes.
- **You should see:** Ranked table; recommend fork **#1 RobustScaleIntensity** (or backup #2/#3); upstream good-first issues as context only.
- **Say out loud:** “Multi-audience PM — real backlog optics plus a seeded fork catalog”
- **Fail / thrash:** Recommends implementing an upstream issue on this fork; creates/edits upstream; skips ledger skill markers.
- **NOTE**: The scaffolder is deliberately narrow so the platform pattern is demonstrably reliable; generalizing families is a product roadmap item, not 
  a missing demo checkbox. I didn’t under-build the scaffolder — I scoped the first pack.
- **KPI is time-to-first-safe-merge**, not “one skill that scaffolds all of MONAI.” Intensity transforms are the densest, CPU-testable convention surface for a 45-minute spine.

```text
First briefly scan upstream Project-MONAI/MONAI good first issues (read-only) for context. Then rank open issues on this fork and recommend RobustScaleIntensity (#1) unless blocked. Do not recommend implementing an upstream issue on this fork.
```

- **Under the hood:** Same as `/triage-issues` without relying on slash dispatch — still `everyday` + `gh`.
- **You should see:** Explicit upstream-then-fork narrative ending on #1.
- **Say out loud:** “Writable work stays on the fork; upstream is a mirror for prioritization optics.”
- **Fail / thrash:** Treats decoy networks issue #4 as the build target; opens PRs/issues on upstream.

### C. PM — plan

Profile: **`everyday`**. If this chat’s first Shell call just failed closed, **Reload
Window**, warm up with `echo ok && gh auth status`, then paste below (do not let
the agent “recover” via MCP/browser).

**TRADE OFF**: Fail-closed is right for real hook failures. Cursor currently conflates ‘hook didn’t spawn’ with ‘hook denied,’ which bricks PM gh. We fail-open on spawn failure so the demo’s enforcement  path stays the script’s allow/deny, not an infra hard-lock. beforeReadFile stays fail-closed.

```text
/plan-feature
Use fork issue #1 (RobustScaleIntensity) from triage. Confirm/update acceptance criteria, non-goals, touch paths under monai/transforms/intensity/, and test expectations on the live GitHub issue. Fork only — no upstream edits.
```

- **Under the hood:** Skill `plan-feature`; ledger PM/`plan`; `gh issue view|edit` on **fork only**; refs/rules for transforms touch paths. Shell hook must actually run (see fail-closed note above).
- **You should see:** Live GitHub issue #1 updated (acceptance criteria, non-goals, paths, tests) — not a local markdown plan-only artifact.
- **Say out loud:** “Runnable PM artifact — the issue is the handoff from triaging.”
- **Fail / thrash:** Edits upstream; chat-only plan; MCP/browser issue edit because Shell wedged; expands scope outside `monai/transforms/intensity/`.

### D. Boundary deny moment
Why Boundary? Reduces accidental out-of-bounds context and keep the default agent on the contribution path. They help ramp and convention discipline; they do not stop a determined engineer. `Strict` is the contribution boundary; `everyday` is the org boundary. Same rails, different permission sets per stage.

**When you’d invest more**: org-managed hooks, CI as source of truth, CODEOWNERS/review, maybe cloud agents with locked config. Local boundary-profile alone is never your hard perimeter.

```bash
echo strict > .cursor/boundary-profile
```

- **Under the hood:** Hooks re-read `.cursor/boundary-profile` immediately (`policy.profile`); prefer a **fresh Agent chat** so `sessionStart` injects `MONAI_CURSOR_BOUNDARY=strict`.
- **You should see:** No agent output yet — profile flip only.
- **Say out loud:** “Strict = approved contribution boundary, not a toy sandbox.”
- **Fail / thrash:** Profile file still `everyday`; continuing in an old chat that never picked up strict.

Then:

```text
Read monai/networks/nets/unet.py and summarize the UNet constructor.
```

- **Under the hood:** `beforeReadFile` → `boundary_read.py` → **deny** (networks outside strict allowlist); ledger `decision: deny`; user sees deny message pointing at transforms + kit paths. Hook cannot strip `@` attachments already in the prompt — this beat uses an agent **Read**, not an attachment.
- **You should see:** Blocked read; no UNet constructor summary from file contents.
- **Say out loud:** “The agent cannot quietly leave transforms during the engineer stage.”
- **Fail / thrash:** Read succeeds; agent summarizes from training memory as if the read worked; Shell/`cat` bypass succeeds without you calling out hooks ≠ OS sandbox.

### E. Engineer — scaffold

Stay on **`strict`**.

Smoke run: open .cursor/refs/transforms-array-dict.md)

```text
/scaffold-transform
Implement the transform from issue #1 under monai/transforms/intensity/ (array + d). Follow .cursor/refs/. Leave the planted dictionary __all__ gap for QA. Stay in strict allowlist.
```

- **Under the hood:** Skill `scaffold-transform`; ledger engineer/`build`; rules `10-transforms` + `20-testing` + `30-style`; ref `transforms-array-dict.md`; `beforeReadFile`/`beforeShellExecution` keep work in transforms + kit; post-edit nudges may fire on intensity edits.
- **You should see:** Array + `d` classes; stub tests; **planted** (1) `np.float` dtype default (2) `*d` missing from `dictionary.py` `__all__`; handoff note cites both. No full CI.
- **Say out loud:** “Correct first contribution without reading the whole library - defects are intentional training signals for QA.”
- **Fail / thrash:** Fixes the planted gaps itself; drifts into networks/losses; `gh` under strict (denied); silent skip of array or `d`.

### F. QA — strengthen

Still **`strict`** unless a check needs `gh` (it shouldn’t).

```text
/strengthen-tests
Fix the planted __all__ gap and harden parameterized tests for the new transform (array + d).
```

- **Under the hood:** Skill `strengthen-tests`; ledger QA/`test`; rule `20-testing.mdc`; runs `check-deprecations.sh` first; fixes `np.float` → `np.float32` and `dictionary.py` `__all__`; hardens parameterized array + `d` tests; prefer `python3 -m tests.transforms...` (strict shell allowlist).
- **You should see:** Deprecation script clean; `from monai.transforms import <Name>d` works; stronger tests; planted gaps gone.
- **Say out loud:** “Catch mistakes before human review — tooling signal, not a checklist recited from memory.”
- **Fail / thrash:** Leaves `np.float` or `__all__` gap; only edits tests without fixing registration; uses non-allowlisted unittest invocation that strict denies mid-demo.

### G. DevOps — CI

```bash
echo everyday > .cursor/boundary-profile
```

- **Under the hood:** Flip before `gh` / broader shell; fresh chat optional but cleaner.
- **You should see:** Profile back to warn-only.
- **Say out loud:** “Everyday for integration commands; strict was for the contribution boundary.”
- **Fail / thrash:** Running `/prep-for-ci` while still strict and wondering why `gh` is denied.

```text
/prep-for-ci
Run local ruff + scoped tests, run docs/cursor-kit/scripts/check-deprecations.sh and check-changelog.sh, confirm DCO and a [Unreleased] changelog entry, map to CI workflows including docs/cursor-kit sync-check. Do not open a PR against upstream; draft to the fork only if I ask.
```

- **Under the hood:** Skill `prep-for-ci`; ledger DevOps/`ci`; maps local commands → `.github/workflows/` + `cursor-kit-sync.yml`; changelog/DCO/release-train narrative; fork-only remotes.
- **You should see:** Local check results; CI map including sync-check + deprecation gate; `[Unreleased]` note; no upstream PR.
- **Say out loud:** “Path to production — sync-check means the team owns the kit when norms drift.”
- **Fail / thrash:** Opens PR against `Project-MONAI/MONAI`; skips changelog/deprecation gates; claims deploy = manual NGC push.

### H. Reviewer

Use **`/review-contribution`** — not Cursor’s built-in `/review` (Bugbot / Security
chooser). After rename, Reload Window so Customize → Skills picks it up.

```text
/review-contribution
Review the transform diff against CONTRIBUTING and Cursor rules. Include CODEOWNERS note and planted-gap status.
```

- **Under the hood:** Skill `review-contribution`; ledger reviewer/`review`; checklist vs `contributing-checklist.md`, rules, `CONTRIBUTING.md`, `.github/CODEOWNERS`; confirms planted gaps are fixed (post-QA).
- **You should see:** Pass/fail table with evidence; Approve or Request changes; CODEOWNERS + planted-gap status called out.
- **Say out loud:** “Same rails for the reviewer persona — not Cursor Bugbot. We renamed to avoid the product `/review` collision.”
- **Fail / thrash:** Picking Bugbot/Security from Cursor’s `/review` chooser; rubber-stamp Approve with no checklist; misses remaining `__all__`/deprecated API; suggests upstream PR.

Optional delegation beat (shows multi-role automation, not just a menu):

```text
Delegate the review to a background subagent: launch a Task that runs the /review-contribution checklist on the current diff and reports Approve / Request changes. The subagentStart/Stop audit hook logs it to the ledger.
```

- **Under the hood:** `subagentStart` / `subagentStop` → `subagent_audit.py` → ledger allow/completed (kit observes; does not gate delegation in v1).
- **You should see:** Subagent verdict; ledger rows for start/stop with subagent type + tool counts.
- **Say out loud:** “Subagents isolate work inside a stage — they don’t jump personas across the SDLC.”
- **Fail / thrash:** No ledger audit rows; subagent used to skip to a different persona’s stage.

### I. Optional economics / trajectory beat

Prefer the combined HTML dashboard (counts + Layer C scorecard):

```bash
cp .cursor/usage/ledger.jsonl docs/cursor-kit/eval-runs/2026-07-17/kit-spine-$(date +%Y%m%d).jsonl
python3 docs/cursor-kit/scripts/ledger-dashboard.py \
  docs/cursor-kit/eval-runs/2026-07-17/kit-spine-$(date +%Y%m%d).jsonl \
  --session all
open .cursor/usage/ledger-dashboard.html   # or the path printed by the script
```

CLI-only equivalents still work: `ledger-report.py` (counts) and `score_trajectory.py` (scorecard).

- **Under the hood:** Reads `.cursor/usage/ledger.jsonl`; aggregates persona/stage/skill/decision counts; runs Layer C checks (skill order, strict deny, scaffold-under-strict — see [`EVALUATION.md`](EVALUATION.md)).
- **You should see:** A small HTML page with ship-ready badge, required **11/11**, denies/warns, and check table. Target `ship_ready_trajectory: true`.
- **Say out loud:** “Cursor-estimated stage metering — not a billing invoice. We measure whether the kit path ran — process evidence, not LOC.”
- **Fail / thrash:** Framing ledger lines as precise cost; empty ledger because skills never appended start/end; score fails because deny probe or skill markers were skipped.

---

## After the session

- Flip back: `echo everyday > .cursor/boundary-profile`
- Archive + dashboard: see **§I** (`ledger-dashboard.py`; target **11/11** required)
- Discard live scaffold transform/tests/changelog from the kit branch unless you intend to keep them; keep kit fixes (hooks, rules, skill renames, DEMO)
- Do not push kit branch to upstream MONAI
- If you opened a draft PR on the fork, close or leave it — confirm afterward
