---
name: prep-for-ci
description: >-
  DevOps workflow: map and run local MONAI style/test commands equivalent to CI,
  confirm DCO-ready commits, optionally open a draft PR to the fork only. Use
  when the user runs /prep-for-ci.
disable-model-invocation: true
---

# /prep-for-ci (DevOps)

## Ledger

```bash
echo '{"event":"skill","decision":"start","skill":"prep-for-ci","persona":"DevOps","stage":"ci"}' \
  | python3 .cursor/hooks/ledger_append.py
```

(end: `"decision":"end"`)

## Profile

- Finish local checks under current profile (often `strict`).
- Switch to **`everyday`** before any `gh` draft PR (strict blocks `gh`).

## Local → CI map

| Local | Maps toward |
|---|---|
| `./runtests.sh --ruff` | Style jobs in `.github/workflows/` (e.g. pythonapp / cicd) |
| `./runtests.sh --autofix` / `--codeformat` | Full lint + types |
| `./runtests.sh --quick --unittests` | Unit test workflows (`cicd_tests.yml`, etc.) |
| `.pre-commit-config.yaml` | Same tool family as CI |

Prefer smallest subset covering touched files.

## Steps

1. Confirm branch and dirty state: `git status -sb`.
2. Run at least: `./runtests.sh --ruff` and scoped transform tests for the new module.
3. DCO: recent commits must include `Signed-off-by:` (`git log -1 --format=%B`). Advise `git commit -s` if missing (do not rewrite published history unless user asks).
4. Note boundary profile + that `.cursor/usage/ledger.jsonl` may have stage entries (Cursor-estimated economics — not a billing product).
5. Optional: draft PR **to fork** `dev` (not upstream):

```bash
gh pr create -R DarthVaderRC/project-monai --base dev --draft --title "..." --body "..."
```

Or speak a PR body without creating if user declines.

## Output

Checklist:

- [ ] Style / ruff
- [ ] Scoped unit tests
- [ ] DCO
- [ ] CI mapping explained
- [ ] Draft PR URL (optional) — fork only

## Stop when

Checklist is complete. Hand off to `/review`.
