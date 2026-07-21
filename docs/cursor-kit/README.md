# Cursor kit for MONAI (this fork)

Onboarding kit that encodes MONAI contribution norms into Cursor **plugins**
(**platform-core** + **pack-monai**), consumer **`.cursor/`** (config + materialized
refs + usage), **AGENTS.md**, and DEMO/EVAL narrative under `docs/cursor-kit/`.

The contribution spine stays on intensity transforms; Phase 1 adds full-stack packs
for **losses**, **metrics**, and **network blocks**.

## Quick map

| Layer | Path |
|---|---|
| Agent guide | [`AGENTS.md`](../../AGENTS.md) |
| Consumer config | [`.cursor/pack.config.json`](../../.cursor/pack.config.json) + [`boundary-profile`](../../.cursor/boundary-profile) |
| Materialized refs | [`.cursor/refs/`](../../.cursor/refs/) — runtime copy; pack SSOT is `plugins/pack-monai/refs/` |
| Usage ledger | [`.cursor/usage/`](../../.cursor/usage/) |
| Rules / scaffold skills | **pack-monai** plugin (injected when enabled) |
| Hooks / persona shells / spec-critic | **platform-core** plugin |
| Runbook + narrative | [`DEMO.md`](DEMO.md) |
| Kit-off vs kit-on evaluation | [`EVALUATION.md`](EVALUATION.md) |
| Sync check | [`scripts/sync-check.sh`](scripts/sync-check.sh) (wrapper → platform-core) |
| Layer A/B/C scorers | [`scripts/score_process.py`](scripts/score_process.py), [`score_rubric.py`](scripts/score_rubric.py), [`score_trajectory.py`](scripts/score_trajectory.py) (C → platform-core) |
| Layer D judge | [`scripts/llm_judge.py`](scripts/llm_judge.py) (wrapper → platform-core; additive) |
| Eval fixtures (dated) | [`eval-runs/`](eval-runs/) — ledgers/JSON only; scorers live under `scripts/` |
| Kit CI | [`.github/workflows/cursor-kit-sync.yml`](../../.github/workflows/cursor-kit-sync.yml) |
| Productization | [`productization/`](productization/) |

## `@Docs` setup (one-time)

1. Cursor Settings → **Indexing & Docs**
2. Add **https://docs.monai.io/en/stable/**
3. In Agent chat, use `@Docs` for official API questions; use `.cursor/refs/` for fork conventions

## Bootstrap

```bash
# After enabling platform-core + pack-monai:
 /init-pack
# or:
bash ~/.cursor/plugins/local/pack-monai/scripts/materialize_refs.sh "$(pwd)"
```

Edit refs in the **pack** repo, then re-run `/init-pack`. Do not treat `.cursor/refs/` as SSOT.

## Boundary profiles

Hooks (platform-core) read **`.cursor/boundary-profile` first**, then the env named by
`pack.config.json` `profile_env`, then default `everyday`.

```bash
echo everyday > .cursor/boundary-profile   # warn-only; gh allowed
echo strict > .cursor/boundary-profile     # deny out-of-allowlist reads/shell
```

## Sync check

[`scripts/sync-check.sh`](scripts/sync-check.sh) is a **thin wrapper** around the
platform-core runner. It checks thin-consumer inventory, `.cursor/refs/` existence,
and **byte drift** vs pack SSOT when available (`CURSOR_ONBOARDING_PACK_REFS` or
sibling/`~/.cursor/plugins/local/pack-monai/refs`).

**CI note:** pure-consumer CI often lacks the pack SSOT checkout — existence checks
still run; drift can go uncaught unless CI fetches pack refs or sets
`CURSOR_ONBOARDING_PACK_REFS`. See [`productization/PRODUCTIZATION.md`](productization/PRODUCTIZATION.md).

```bash
bash docs/cursor-kit/scripts/sync-check.sh
```

## Ownership

Platform ownership for kit paths is recorded in `.github/CODEOWNERS` (`.cursor/`, `AGENTS.md`, `docs/cursor-kit/`).

**Panel narrative** lives in [`DEMO.md`](DEMO.md).

### Core vs pack

| Owner | Manages | Does not manage |
|---|---|---|
| **Platform / DX team** | **Core:** hook engine, persona skill shells, `/init-pack`, sync-check runner, ledger, AGENTS template | Library conventions, neighbor classes, catalog examples |
| **Library / domain team** | **Pack:** rules, refs SSOT, `/scaffold-*`, pack.config schema+example, check-deprecations/changelog | Hook machinery, persona stage order |
| **Consumer workspace** | `pack.config.json` instance, `boundary-profile`, materialized `.cursor/refs/`, `usage/` | Duplicate rules/skills/hooks as SSOT |

**Source of truth:** [`productization/manifest.json`](productization/manifest.json) and [`productization/PRODUCTIZATION.md`](productization/PRODUCTIZATION.md).

## Usage ledger

`.cursor/usage/ledger.jsonl` is local metering (gitignored).

```bash
python3 docs/cursor-kit/scripts/ledger-dashboard.py
open .cursor/usage/ledger-dashboard.html   # macOS
python3 docs/cursor-kit/scripts/ledger-report.py
```
