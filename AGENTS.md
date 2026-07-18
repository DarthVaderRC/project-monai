# MONAI Cursor onboarding kit

Project-level guidance for Cursor agents working in this fork. Owned by the platform team via `.github/CODEOWNERS` (`.cursor/`, this file, `docs/cursor-kit/`).

This is **not** a Custom Mode. Skills are invoked explicitly with `/`.

## Agent topology (how the personas work together)

- **Each persona's session orchestrates only its own stage.** A persona invokes their own `/` skill(s); work moves to the next persona via an **artifact handoff** (a GitHub issue, a diff + handoff note, a verdict) — never via an automated pipeline. There is no `ship-feature` god-command.
- **Subagents are an intra-stage tool.** Within a single stage, a persona may delegate a heavy or parallelizable sub-task to a specialist subagent (isolated context window, depth-1). Example: the reviewer can run `/review-contribution` as a background subagent. Subagents never advance the flow into another persona's stage.

## Skills (slash commands)

| Skill | Persona | Purpose |
|---|---|---|
| `/triage-issues` | PM | Rank open fork issues; recommend a catalog transform issue |
| `/plan-feature` | PM | Create or update a **live GitHub issue** on the fork with acceptance criteria |
| `/scaffold-transform` | Engineer | Implement array + `d` intensity transform from the issue |
| `/scaffold-loss` | Engineer | Implement a new loss under `monai/losses/` from an issue |
| `/scaffold-metric` | Engineer | Implement a new metric under `monai/metrics/` from an issue |
| `/scaffold-network` | Engineer | Implement a new network block under `monai/networks/blocks/` from an issue |
| `/strengthen-tests` | QA | Harden parameterized tests; fix planted scaffold gaps |
| `/prep-for-ci` | DevOps | Map local `runtests.sh` / style checks to CI; DCO; optional draft PR **to fork** |
| `/review-contribution` | Reviewer | Checklist review vs rules + `CONTRIBUTING.md` (not Cursor `/review` Bugbot) |

## Boundary profiles

Preferred (mid-session flip without relaunching Cursor): write `.cursor/boundary-profile`:

| File contents | Behavior |
|---|---|
| `everyday` (default) | Warn on out-of-allowlist reads/shell; do not block. `gh` allowed. |
| `strict` | Deny out-of-allowlist file reads and risky shell. Use for `/scaffold-*` (transforms allowlist; Phase 1 packs available under everyday). |

```bash
echo everyday > .cursor/boundary-profile
echo strict > .cursor/boundary-profile
```

Hooks also honor `MONAI_CURSOR_BOUNDARY` if the profile file is absent. `sessionStart` injects the resolved profile into the session env. Allowlist details: `.cursor/hooks.json` + `.cursor/hooks/`.

## Docs (preferred sources)

1. In-repo refs under `docs/cursor-kit/monai-refs/`:
   - `transforms-array-dict.md` — array + `d` intensity pattern
   - `losses.md` — loss conventions + `LogCoshDiceLoss` neighbor (`DiceLoss`)
   - `metrics.md` — metric conventions + `MedianAbsoluteErrorMetric` neighbor (`MAEMetric`)
   - `networks.md` — network-block conventions + `LayerScale` neighbors
   - `testing.md` — parameterized tests / `runtests.sh`
   - `contributing-checklist.md` — style, license, DCO, fork-only PRs
2. Cursor `@Docs`: index **https://docs.monai.io/en/stable/** (setup steps in `docs/cursor-kit/README.md`).
3. Canonical repo files: `CONTRIBUTING.md`, `pyproject.toml`, `setup.cfg`, `.pre-commit-config.yaml`.

Do **not** scrape random web pages for MONAI conventions. Prefer refs + `@Docs` + in-repo sources.

## Remote policy (this fork)

- **Issues and PRs target the fork only** (`origin` → `DarthVaderRC/project-monai`).
- Never open issues or PRs against upstream `Project-MONAI/MONAI` from this kit.
- Use `gh` with `-R DarthVaderRC/project-monai` (or detect `origin`) for PM/DevOps skills.

## Contribution pointers

- Full process: [`CONTRIBUTING.md`](CONTRIBUTING.md) (American English, Apache header, style, tests, DCO).
- Kit maintainability: `docs/cursor-kit/README.md`.
- Sync check: `docs/cursor-kit/scripts/sync-check.sh` (verifies rule “Source of truth” paths still exist).
- Panel runbook: `docs/cursor-kit/DEMO.md`.
