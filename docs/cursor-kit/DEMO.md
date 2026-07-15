# DEMO runbook — MONAI Cursor onboarding kit

Panel-safe session script for the `project-monai` workspace (`cursor-onboarding-kit` branch).

**Push to origin only during the live demo** (closed assignment — keep kit local until then).

---

## Panel narrative (judgment — read this first)

This section is what the exercise grades as *judgment about what’s worth solving*, not only a working spine. The live demo proves the artifact; this proves *why*.

### 45-minute agenda

| Block | Time | Goal |
|---|---|---|
| Judgment | 5–8 min | Business pain, prioritize/skip, tooling choices, how we’d measure value |
| Live spine | 20–25 min | Triage → plan → strict deny → scaffold → QA → CI → review |
| Limitations / next | 5 min | Honesty + beyond-demo (plugin core vs packs, agents) |

**Trim talking track:** do not narrate every layer equally. Deep-dive shared rails (rules/hooks/refs) + one deny + one planted QA fix. Skills are thin orchestrators — say that once.

### Business problem

Platform onboards engineers onto a **convention-heavy** library; **ramp is slow** and PRs drift from standards. They care about the **full SDLC** (plan → design → build → test → review → CI), and want **one solution** PM / eng / QA / DevOps can share.

**KPI to attack:** *time-to-first-safe-merge* (scoped change, green checks, DCO) and *convention consistency* on early PRs.

### Why MONAI + transforms (not a toy)

- Encodable conventions (array + `d`, `__all__`, Apache header, American English, lint stack).
- CPU-runnable transform tests → live demo fits 45 minutes.
- Clinical PM stories + dense tests + real CI → multi-persona without faking SDLC.

### Prioritize / skip

| Build first | Skip / defer (v1) |
|---|---|
| Rules + two-profile hooks + `/scaffold-transform` | Companion-repo installer |
| QA + DevOps skills; PM triage/plan | Custom docs/boundary MCP |
| In-repo refs + `@Docs` | Custom Mode |
| sync-check + CODEOWNERS + kit CI | GPU/distributed automation |
| | Full cost dashboard; Marketplace plugin extract |

**Equal depth vs demo sequencing:** all five requirements are designed in; the **live** path is short on purpose (presentation choice, not a depth cut).

### Tooling choices (defend live)

| Choice | Why |
|---|---|
| Approach A (in-repo kit) | Reliable panel-safe demo; versioned with the fork |
| `@Docs` + `monai-refs/` | Official API + owned conventions; no custom docs MCP |
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
| Fewer uncaught gaps | Review/CI comments on covered anti-patterns | `/strengthen-tests`, `/review`, post-edit nudges |
| Multi-role leverage | Non-eng runs of PM/QA skills | Six skills on shared rails |
| Safe autonomy | Boundary deny vs escape (ledger) | Strict/everyday hooks |
| Cost awareness | Cursor usage + ledger stage counts | Estimated; not an invoice |

**Spoken value line:** *“New engineers waste days on framework syntax and silent convention misses. We automate boilerplate safely so they focus on medical/business logic; hooks and QA cut missed tests and out-of-bounds context. Platform measures ramp time and first-PR defect rate — not LOC.”*

### Exercise “looking for” → where you show it

| Criterion | Where in the session |
|---|---|
| Judgment / business impact | This narrative + prioritize/skip |
| Thinking process / options weighed | Tooling table + rejected companion-repo/MCP |
| SDLC breadth | Spine triage → review |
| Multi-audience | Six `/` skills; PM live issues |
| Runnable artifact | Live spine (not slides) |
| Honesty / limitations | Closing block |
| Maintainability without you | sync-check CI + README + CODEOWNERS |

### Sync-check = “team owns this” (detection half)

Ownership is not the script alone. **Versioned kit + CODEOWNERS + sync gate** so when CONTRIBUTING/paths drift, CI fails instead of silently teaching wrong norms. README tells the team how to bump rules/refs.

### Beyond demo (productization — talk, don’t rebuild mid-panel)

Today’s **content pack** is MONAI/transforms-specific (correct for the stand-in). A Marketplace plugin of “this folder as-is” would be wrong for other libs.

| Layer | Portable? | Contents |
|---|---|---|
| Platform core | Yes | Hook engine, persona skill *shells*, sync-check *pattern*, ledger schema, AGENTS pattern |
| Library pack | No | MONAI rules text, `monai-refs/`, catalog transforms, planted-defect recipe |

**Next:** extract core to a private/org plugin; keep packs per library. **Agents/subagents:** same persona prompts as standing agents so the default agent can delegate QA/review — skills stay for explicit `/` demos. Not built in v1 on purpose.

**Strong panel answers (copy):**

- *“I’d productize the platform core as a plugin next; this fork keeps the MONAI pack in-repo for a reliable live demo.”*
- *“LOC isn’t the KPI — ramp time and convention adherence are.”*
- *“Upstream good-first issues are context; writable work stays on the fork catalog.”*

### Limitations (say out loud)

- Hooks ≠ OS sandbox; determined users can still escape outside Cursor.
- Medical/scientific correctness needs human review.
- Rule drift possible — mitigated by sync-check CI, not eliminated.
- Ledger is Cursor-estimated stage metering, not billing.
- CPU transform scope only in the live path.

---

## Pre-flight

- [ ] Open folder: `/Users/DineshGawande/Code/project-monai` (not the planning repo)
- [ ] Branch: `cursor-onboarding-kit` (push to fork **only when the panel starts**, if required)
- [ ] `gh auth status` OK; Issues enabled on fork
- [ ] `@Docs` indexed: https://docs.monai.io/en/stable/
- [ ] Customize → Rules shows `00`–`40`; Skills show six `/` workflows
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

## Demo spine

| Step | Action | Artifact | Spoken line (judgment) |
|---|---|---|---|
| 1 | `/triage-issues` | Ranked table; recommend #1 | Multi-audience PM; A+D = real backlog optics + controlled demo |
| 2 | `/plan-feature` on #1 | Live issue updated | Runnable PM artifact — not markdown theater |
| 3 | `echo strict > .cursor/boundary-profile` | Boundary on | Req #3 — approved boundaries |
| 4 | Deny probe | Hook deny | Show teeth: agent cannot quietly leave transforms |
| 5 | `/scaffold-transform` | Code + planted `__all__` gap | Req #1 — correct first contribution without reading the whole repo |
| 6 | `/strengthen-tests` | Gap fixed; stronger tests | Req #2 — catch mistakes before human review |
| 7 | everyday → `/prep-for-ci` | CI map; kit sync workflow | Path to production; sync-check CI = ownable kit |
| 8 | `/review` | Checklist verdict | Reviewer persona on the same rails |

### Planted defect

Scaffold intentionally omits the `*d` class from `dictionary.py` `__all__`. QA skill fixes it.

### Backup switch

If primary is blocked, triage → AsinhIntensity (#2), then TanhSqueezeIntensity (#3). Same spine.

### Profile switch

```bash
echo strict > .cursor/boundary-profile
echo everyday > .cursor/boundary-profile
```

Read/deny hooks honor the file immediately. Prefer a fresh Agent chat after flips for clean narrative.

---

## Copy-paste prompt bank

Use these in **Agent chat** with the `project-monai` workspace.

### A. Rules / docs smoke

```text
With @monai/transforms/intensity/array.py in context: which project rules apply, and what is the array vs dict (d) pattern for a new intensity transform?
```

```text
Using @Docs and @docs/cursor-kit/monai-refs/transforms-array-dict.md — how do I add a MapTransform wrapper for an intensity transform? Do not open monai/networks.
```

### B. PM — triage

```text
/triage-issues
```

```text
First briefly scan upstream Project-MONAI/MONAI good first issues (read-only) for context. Then rank open issues on this fork and recommend RobustScaleIntensity (#1) unless blocked. Do not recommend implementing an upstream issue in this demo.
```

### C. PM — plan

```text
/plan-feature
Use fork issue #1 (RobustScaleIntensity) from triage. Confirm/update acceptance criteria, non-goals, touch paths under monai/transforms/intensity/, and test expectations on the live GitHub issue. Fork only — no upstream edits.
```

### D. Boundary deny moment

```text
echo strict > .cursor/boundary-profile
```

Then:

```text
Read monai/networks/nets/unet.py and summarize the UNet constructor.
```

Expected: deny / blocked message pointing back to transforms + kit paths.

### E. Engineer — scaffold

```text
/scaffold-transform
Implement the transform from issue #1 under monai/transforms/intensity/ (array + d). Follow monai-refs. Leave the planted dictionary __all__ gap for QA. Stay in strict allowlist.
```

### F. QA — strengthen

```text
/strengthen-tests
Fix the planted __all__ gap and harden parameterized tests for the new transform (array + d).
```

### G. DevOps — CI

```text
echo everyday > .cursor/boundary-profile
```

```text
/prep-for-ci
Run local ruff + scoped tests, confirm DCO, map to CI workflows including docs/cursor-kit sync-check. Do not open a PR against upstream; draft to the fork only if I ask.
```

### H. Reviewer

```text
/review
Review the transform diff against CONTRIBUTING and Cursor rules. Include CODEOWNERS note and planted-gap status.
```

### I. Optional economics beat

```text
Show the last few lines of .cursor/usage/ledger.jsonl and explain them as Cursor-estimated stage/persona metering, not a billing invoice. Value is measured by ramp time and first-PR defect rate, not this file.
```

---

## After the session

- Flip back: `echo everyday > .cursor/boundary-profile`
- Do not push kit branch to upstream MONAI
- If you pushed to the fork for the demo, confirm with the panel whether to leave or remove it afterward
