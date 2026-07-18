# Cursor kit for MONAI (this fork)

Onboarding kit that encodes MONAI contribution norms into Cursor **rules**, **skills**, **hooks**, **AGENTS.md**, and curated **docs**. The live demo spine stays on intensity transforms; Phase 1 adds full-stack packs for **losses**, **metrics**, and **network blocks** (rules + refs + `/scaffold-*` skills + worked examples).

## Quick map

| Layer | Path |
|---|---|
| Agent guide | [`AGENTS.md`](../../AGENTS.md) |
| Rules | [`.cursor/rules/`](../../.cursor/rules/) |
| Skills | [`.cursor/skills/`](../../.cursor/skills/) |
| Hooks | [`.cursor/hooks.json`](../../.cursor/hooks.json) + [`.cursor/hooks/`](../../.cursor/hooks/) |
| Boundary profile | [`.cursor/boundary-profile`](../../.cursor/boundary-profile) (`everyday` \| `strict`) |
| Refs | [`monai-refs/`](monai-refs/) |
| Demo runbook + **panel narrative** | [`DEMO.md`](DEMO.md) |
| Kit-off vs kit-on evaluation | [`EVALUATION.md`](EVALUATION.md) |
| Sync check | [`scripts/sync-check.sh`](scripts/sync-check.sh) |
| Kit CI | [`.github/workflows/cursor-kit-sync.yml`](../../.github/workflows/cursor-kit-sync.yml) |
| Productization skeleton | [`productization/`](productization/) — core-vs-pack manifest + extraction plan (no runtime effect) |

## `@Docs` setup (one-time)

1. Cursor Settings → **Indexing & Docs**
2. Add **https://docs.monai.io/en/stable/**
3. In Agent chat, use `@Docs` for official API questions; use `monai-refs/` for fork conventions

## Boundary profiles

Hooks read **`.cursor/boundary-profile` first** (flip mid-session without relaunching Cursor), then `MONAI_CURSOR_BOUNDARY`, then default `everyday`.

```bash
echo everyday > .cursor/boundary-profile   # warn-only; gh allowed
echo strict > .cursor/boundary-profile     # deny out-of-allowlist reads/shell
```

`sessionStart` also injects the profile into the session env. Start a **new Agent chat** after flipping if shell tools still show the old value; read/deny hooks re-read the file each time.

## Sync check

[`scripts/sync-check.sh`](scripts/sync-check.sh) is a **smoke alarm for kit path drift** — a fast check that every file the kit depends on still exists on disk.

### Why it matters

Rules and skills tell agents to read specific paths (`CONTRIBUTING.md`, `monai-refs/*.md`, neighbor modules in `Source of truth:` footers). If someone renames, moves, or deletes those files, the kit would still *point* at them but agents would get broken or outdated guidance — with no obvious failure until a bad contribution lands.

**Versioned kit + CODEOWNERS + sync-check CI** means the platform team owns maintainability: when paths drift, CI fails instead of silently teaching wrong norms. Panel narrative: [`DEMO.md`](DEMO.md) § “Sync-check = team owns this”.

### What it checks

1. **Rules cross-check** — reads `Source of truth:` lines in `.cursor/rules/*.mdc` and verifies each referenced path exists.
2. **Kit inventory** — verifies a fixed list of hooks, skills, docs, scripts, and the kit CI workflow file exist.

Each path prints `OK` or `MISS`. Summary line: `checked=N missing=M`. Exit **0** if all found, **1** if any missing.

### What it does not do

- Does **not** run tests, lint, or mypy
- Does **not** validate file contents
- Does **not** prove agents followed the rules — only that linked files are present

### When to run

```bash
bash docs/cursor-kit/scripts/sync-check.sh
```

- After adding or changing a rule’s `Source of truth:` paths
- After adding hooks, skills, refs, or kit docs (add new paths to the inventory in `sync-check.sh` if needed)
- Automatically in CI via [`.github/workflows/cursor-kit-sync.yml`](../../.github/workflows/cursor-kit-sync.yml) when kit-related paths change

## How to add a rule

1. Create `.cursor/rules/<nn>-<name>.mdc` with frontmatter (`alwaysApply` or `globs`).
2. Keep it short; end with `**Source of truth:** \`path\`, ...`
3. Run `docs/cursor-kit/scripts/sync-check.sh` (also enforced by `.github/workflows/cursor-kit-sync.yml` on kit path changes)

## How to add a skill

1. Create `.cursor/skills/<name>/SKILL.md`
2. Frontmatter: `name` (must match folder), `description`, `disable-model-invocation: true`
3. Instruct ledger append via `python3 .cursor/hooks/ledger_append.py`
4. Reload Cursor window; invoke with `/<name>` in the **project-monai** Agent chat

## How to add/change a hook

1. Add script under `.cursor/hooks/`
2. Register in `.cursor/hooks.json`
3. `chmod +x` if needed; prefer `python3` over `jq`
4. Dry-run with stdin JSON before relying on demo

## When CONTRIBUTING.md changes

1. Diff against `monai-refs/contributing-checklist.md` and Layer-1 rules
2. Update footers / checklist excerpts
3. Run `sync-check.sh`
4. Note the bump in the PR that touches the kit

## Ownership

Platform ownership for kit paths is recorded in `.github/CODEOWNERS` (`.cursor/`, `AGENTS.md`, `docs/cursor-kit/`).

**Panel narrative** (business judgment, value metrics, beyond-demo plugin/agents path) lives in [`DEMO.md`](DEMO.md) — start there for the interview, not only the live spine.

## Usage ledger

`.cursor/usage/ledger.jsonl` is local metering (gitignored). Treat token economics as **Cursor-estimated**, not a billing product.

Aggregate it into a dashboard (per-persona / per-stage / decision, boundary denies, out-of-bounds attachments):

```bash
python3 docs/cursor-kit/scripts/ledger-report.py
```
