---
name: review
description: >-
  Reviewer workflow: checklist self-review of a transform contribution against
  Cursor rules, CONTRIBUTING.md, CODEOWNERS routing, tests, and style. Use when
  the user runs /review.
disable-model-invocation: true
---

# /review (Reviewer)

## Ledger

```bash
echo '{"event":"skill","decision":"start","skill":"review","persona":"reviewer","stage":"review"}' \
  | python3 .cursor/hooks/ledger_append.py
```

(end: `"decision":"end"`)

## Refs

- `@docs/cursor-kit/monai-refs/contributing-checklist.md`
- `.cursor/rules/*.mdc`
- `CONTRIBUTING.md`
- `.github/CODEOWNERS`

## Steps

1. Review `git diff` / PR body for the transform change set.
2. Score each item pass/fail with evidence:

| Check | Pass? | Notes |
|---|---|---|
| American English | | |
| Apache header | | |
| Array + `d` pattern | | |
| `__all__` + public exports (incl. `*d`) | | |
| Parameterized tests array + `d` | | |
| Style (ruff/black/isort expectations) | | |
| DCO on commits | | |
| No deprecated APIs (`check-deprecations.sh` clean) | | |
| No SoftClipIntensity / redundant soft-clip | | |
| Fork-only remotes (no upstream PR) | | |
| CODEOWNERS routing noted | | |
| Planted gap resolved (registration in package `__init__.py` / transform `__all__`) | | |

3. List residual risks (coverage gaps, API naming, MetaTensor edge cases).
4. Final verdict: **Approve** / **Request changes** with top 3 actions if failing.

## Stop when

Verdict + checklist are published. Do not implement fixes unless the user explicitly asks (then prefer the owning skill).
