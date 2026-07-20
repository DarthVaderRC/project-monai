# Contributing checklist (curated)

Short checklist derived from [`CONTRIBUTING.md`](../../../CONTRIBUTING.md). When in doubt, follow that file.

## Before coding

- [ ] Discuss via issue when unsure; check for duplicates / “belongs in PyTorch vs MONAI?”
- [ ] Prefer medical-application-specific features for MONAI

## Code quality

- [ ] **American English** (`normalize`, `visualize`, `color`)
- [ ] Apache 2.0 MONAI Consortium header on every source file
- [ ] `from __future__ import annotations` where peers use it
- [ ] Append to file-level `__all__` and public package exports
- [ ] Style: black, isort, ruff; types: mypy / pytype as required by CI

```bash
python -m pip install -U -r requirements-dev.txt
./runtests.sh --ruff          # quick
./runtests.sh --autofix       # auto-fix style
./runtests.sh --codeformat    # full lint + types
```

Config sources: `pyproject.toml`, `setup.cfg`, `.pre-commit-config.yaml`.

## Tests & docs

- [ ] Unit tests with `parameterized` where appropriate (see `monai-refs/testing.md`)
- [ ] Update docs / examples if public API changes (`CONTRIBUTING.md` — Building the documentation)

## Commits & PRs (this fork)

- [ ] Every commit has `Signed-off-by:` (DCO)
- [ ] Open draft PRs against the **fork** only — not upstream `Project-MONAI/MONAI`
- [ ] Use `gh -R DarthVaderRC/project-monai` (or `origin`) for issues/PRs

## Ownership

Review routing: [`.github/CODEOWNERS`](../../../.github/CODEOWNERS). Kit paths (`.cursor/`, `AGENTS.md`, `docs/cursor-kit/`) are platform-owned once CODEOWNERS is extended.
