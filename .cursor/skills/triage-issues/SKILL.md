---
name: triage-issues
description: >-
  PM workflow: list and rank open GitHub issues on the MONAI fork, classify
  transforms vs other areas, and recommend a good-first-issue catalog transform
  (RobustScaleIntensity primary, or Asinh/TanhSqueeze backup). Use when the user
  runs /triage-issues. Fork only — never upstream.
disable-model-invocation: true
---

# /triage-issues (PM)

## Ledger

At start and end, append usage lines (fail open):

```bash
echo '{"event":"skill","decision":"start","skill":"triage-issues","persona":"PM","stage":"triage"}' \
  | python3 .cursor/hooks/ledger_append.py
```

(end: `"decision":"end"`)

## Remote (required)

- Resolve fork: `git remote get-url origin` → expect `DarthVaderRC/project-monai`.
- Use `gh -R DarthVaderRC/project-monai` (or `-R` matching `origin`).
- **Never** list/create against `Project-MONAI/MONAI`.

Profile: `everyday` (needs `gh`).

## Steps

1. `gh issue list -R <fork> --state open --limit 30` (optional label filter if user provided one).
2. Classify each issue:
   - **Catalog transforms:** RobustScaleIntensity, AsinhIntensity, TanhSqueezeIntensity
   - **Other transforms**
   - **Decoy / high complexity** (e.g. networks, engines) — deprioritize for first contribution
3. Rank by good-first-issue fitness (scope, CPU-testable, clear acceptance path).
4. **Recommend** in order: RobustScaleIntensity → AsinhIntensity → TanhSqueezeIntensity → other transforms. Skip decoys unless user insists.

## Output

Markdown table: `# | title | area | complexity | good-first? | notes`

Then a clear recommendation block:

```text
Recommended: #<n> — <title>
URL: <url>
```

## Stop when

Recommendation + URL are shown. Do not implement code or edit issues (that is `/plan-feature`).
