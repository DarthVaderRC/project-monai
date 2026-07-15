# DEMO runbook — MONAI Cursor onboarding kit

Panel-safe session script for the `project-monai` workspace (`cursor-onboarding-kit` branch).

## Pre-flight

- [ ] Open folder: `/Users/DineshGawande/Code/project-monai` (not the planning repo)
- [ ] `gh auth status` OK; Issues enabled on fork
- [ ] `@Docs` indexed: https://docs.monai.io/en/stable/
- [ ] Customize → Rules shows `00`–`40`; Skills show six `/` workflows
- [ ] `echo everyday > .cursor/boundary-profile`
- [x] Seeded issues present:

| Issue | # | URL |
|---|---|---|
| RobustScaleIntensity (primary) | **1** | https://github.com/DarthVaderRC/project-monai/issues/1 |
| AsinhIntensity (backup) | **2** | https://github.com/DarthVaderRC/project-monai/issues/2 |
| TanhSqueezeIntensity (backup) | **3** | https://github.com/DarthVaderRC/project-monai/issues/3 |
| Decoy (networks) | **4** | https://github.com/DarthVaderRC/project-monai/issues/4 |

**Triage narrative (A+D):** `/triage-issues` may **read-only** scan upstream `Project-MONAI/MONAI` `good first issue`s for context, then **recommend only** a fork catalog issue (#1–#3). Never create/edit upstream.

## Demo spine

| Step | Action | Artifact |
|---|---|---|
| 1 | `/triage-issues` | Ranked table; recommend primary |
| 2 | `/plan-feature` on recommended # | Live issue updated |
| 3 | `echo strict > .cursor/boundary-profile` | Boundary on |
| 4 | Deny probe (prompt below) | Hook deny message |
| 5 | `/scaffold-transform` | Code + planted `__all__` gap |
| 6 | `/strengthen-tests` | Gap fixed; tests stronger |
| 7 | Local checks → `echo everyday > ...` → `/prep-for-ci` | CI map; optional draft PR to fork |
| 8 | `/review` | Checklist verdict |

### Planted defect

Scaffold intentionally omits the `*d` class from `dictionary.py` `__all__`. QA skill fixes it.

### Backup switch

If primary is blocked, triage → AsinhIntensity, then TanhSqueezeIntensity. Same spine.

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
Run local ruff + scoped tests, confirm DCO, map to CI workflows. Do not open a PR against upstream; draft to the fork only if I ask.
```

### H. Reviewer

```text
/review
Review the transform diff against CONTRIBUTING and Cursor rules. Include CODEOWNERS note and planted-gap status.
```

### I. Optional economics beat

```text
Show the last few lines of .cursor/usage/ledger.jsonl and explain them as Cursor-estimated stage/persona metering, not a billing invoice.
```

---

## Talking points (short)

1. Equal-depth rails (rules/hooks/refs) + thin `/` skill orchestrators per persona  
2. Live GitHub issues on the fork = runnable PM artifact  
3. Two-profile boundaries with a mid-demo deny moment  
4. Planted defect proves QA skill value  
5. Team can extend via README + sync-check + CODEOWNERS  

## After the session

- Flip back: `echo everyday > .cursor/boundary-profile`
- Do not push kit branch to upstream MONAI
