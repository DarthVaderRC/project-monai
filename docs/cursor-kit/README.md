# Cursor kit (stub)

Onboarding kit for Cursor agents on this MONAI fork. Full maintainability guide lands in a later kit task; this stub covers docs setup and the curated refs pack.

## `@Docs` setup (one-time per machine)

1. Open **Cursor Settings → Indexing & Docs** (or Features → Docs, depending on version).
2. Add documentation URL: **https://docs.monai.io/en/stable/**
3. Keep the index prefix bounded to that root (do not index unrelated sites for conventions).
4. In Agent chat, cite with `@Docs` / the indexed MONAI docs when answering API questions.

Prefer `@Docs` + in-repo refs over scraping random web pages.

## In-repo refs (`monai-refs/`)

| File | Use when |
|---|---|
| [`monai-refs/transforms-array-dict.md`](monai-refs/transforms-array-dict.md) | Adding array + `d` intensity transforms |
| [`monai-refs/testing.md`](monai-refs/testing.md) | Writing or hardening transform tests |
| [`monai-refs/contributing-checklist.md`](monai-refs/contributing-checklist.md) | PR / style / DCO checklist |

Also see root [`AGENTS.md`](../../AGENTS.md) and `.cursor/rules/`.

## Coming soon

- Full README (add rule/skill/hook; bump refs when CONTRIBUTING changes)
- `scripts/sync-check.sh`
- `DEMO.md` runbook
