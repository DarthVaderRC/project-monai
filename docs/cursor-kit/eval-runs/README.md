# Eval runs (fixtures only)

Dated ledgers, fixtures, and score JSON from measurement campaigns.

**Scorers do not live in this folder.** Use the live kit entrypoints under
[`../scripts/`](../scripts/):

| Layer | Entrypoint |
|---|---|
| A (process) | [`../scripts/score_process.py`](../scripts/score_process.py) |
| B (rubric) | [`../scripts/score_rubric.py`](../scripts/score_rubric.py) |
| C (trajectory) | [`../scripts/score_trajectory.py`](../scripts/score_trajectory.py) (wrapper → `platform-core`) |

Layer C canonical source: sibling monorepo
`cursor/plugins/platform-core/scripts/score_trajectory.py`
(also under `~/.cursor/plugins/local/platform-core/scripts/` after local install).

See [`../EVALUATION.md`](../EVALUATION.md) for how to re-score archived ledgers.
