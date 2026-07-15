---
name: triage-issues
description: >-
  PM workflow: optionally scan upstream MONAI good-first issues (read-only), then
  rank open issues on this fork and recommend a catalog intensity transform
  (RobustScaleIntensity primary, or Asinh/TanhSqueeze backup). Use when the user
  runs /triage-issues. Writable work stays on the fork only.
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

## Remotes

| Role | Repo | Allowed actions |
|---|---|---|
| **Upstream (context only)** | `Project-MONAI/MONAI` | **Read-only** `gh issue list` / `view` |
| **Fork (demo backlog)** | `DarthVaderRC/project-monai` (`origin`) | List + **recommend**; never create/edit here in this skill |

- Resolve fork via `git remote get-url origin`.
- **Never** `gh issue create|edit|comment|close` or open PRs against upstream.
- Writable follow-ups (`/plan-feature`) use the **fork** only.

Profile: `everyday` (needs `gh`).

## Steps (hybrid A+D)

### Pass D — upstream scan (optional but preferred in demo)

```bash
gh issue list -R Project-MONAI/MONAI --label "good first issue" --state open --limit 5
```

Summarize 1–3 real community issues in a short “Upstream context” note (titles + why they may/may not fit a 45‑minute first contribution). **Do not recommend upstream issues for implementation in this demo.**

### Pass A — fork backlog (authoritative)

1. `gh issue list -R DarthVaderRC/project-monai --state open --limit 30` (optional label filter).
2. Classify each fork issue:
   - **Catalog transforms:** RobustScaleIntensity, AsinhIntensity, TanhSqueezeIntensity
   - **Other transforms**
   - **Decoy / high complexity** (e.g. networks) — deprioritize
3. Rank by good-first-issue fitness (scope, CPU-testable, clear acceptance path).
4. **Recommend** fork issues only, in order: RobustScaleIntensity → AsinhIntensity → TanhSqueezeIntensity. Skip decoys unless the user insists.

## Output

1. Brief **Upstream context** table (optional Pass D).
2. Fork ranking table: `# | title | area | complexity | good-first? | notes`
3. Recommendation block (**fork URL only**):

```text
Recommended: #<n> — <title>
URL: https://github.com/DarthVaderRC/project-monai/issues/<n>
```

## Stop when

Fork recommendation + URL are shown. Do not implement code or edit issues (that is `/plan-feature`).
