# 2026-07-17 campaign fixtures

Ledgers, fixtures, and run notes for the July 17 eval.

Scorers moved out of this dated tree — use
[`../../scripts/`](../../scripts/) (see [`../README.md`](../README.md)).

Re-score examples:

```bash
python3 docs/cursor-kit/scripts/score_process.py . --transform AsinhIntensity --stage post_scaffold
python3 docs/cursor-kit/scripts/score_rubric.py .
python3 docs/cursor-kit/scripts/score_trajectory.py docs/cursor-kit/eval-runs/2026-07-17/kit-spine-20260719.jsonl --session all
```
