# DEMO runbook — MONAI Cursor onboarding kit

Panel-safe session script for the `project-monai` workspace (`cursor-onboarding-kit` branch).

## Pre-flight

- [ ] Open folder: `/Users/DineshGawande/Code/project-monai` (not the planning repo)
- [ ] `gh auth status` OK; Issues enabled on fork
- [ ] `@Docs` indexed: https://docs.monai.io/en/stable/
- [ ] Customize → Rules shows `00`–`40`; Skills show six `/` workflows
- [ ] `echo everyday > .cursor/boundary-profile`
- [ ] Seeded issues present (fill after Task 6):

| Issue | # | URL |
|---|---|---|
| RobustScaleIntensity (primary) | _TBD_ | _TBD_ |
| AsinhIntensity (backup) | _TBD_ | _TBD_ |
| TanhSqueezeIntensity (backup) | _TBD_ | _TBD_ |
| Decoy (networks) | _TBD_ | _TBD_ |

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
Rank open issues on this fork for a good-first intensity transform contribution. Prefer RobustScaleIntensity unless blocked.
```

### C. PM — plan

```text
/plan-feature
Use the recommended issue from triage. Add acceptance criteria, non-goals, touch paths under monai/transforms/intensity/, and test expectations. Update the live GitHub issue on the fork only.
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
Implement the transform from issue #<PRIMARY> under monai/transforms/intensity/ (array + d). Follow monai-refs. Leave the planted dictionary __all__ gap for QA. Stay in strict allowlist.
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
