# Testing (curated)

Canonical: [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) (Unit testing). Prefer **`parameterized`** cases; use helpers from `tests.test_utils` (`assert_allclose`, etc.). Keep default deps to torch/numpy when possible; optional deps → document and update `tests/min_tests.py` `exclude_cases`. Do not commit large binary fixtures.

## Layout by archetype

| Archetype | Directory | Pairing / coverage notes | Neighbor example |
|---|---|---|---|
| Transforms | `tests/transforms/` | Array + dict (`d`) files | [`test_scale_intensity.py`](../../../tests/transforms/test_scale_intensity.py) |
| Losses | `tests/losses/` | Mirror a peer loss test | [`test_logcosh_dice_loss.py`](../../../tests/losses/test_logcosh_dice_loss.py) |
| Metrics | `tests/metrics/` | Construct → call → `aggregate()` | [`test_median_absolute_error.py`](../../../tests/metrics/test_median_absolute_error.py) |
| Network blocks | `tests/networks/blocks/` | **2D and 3D** under `eval_mode` | [`test_layerscale.py`](../../../tests/networks/blocks/test_layerscale.py) |

Name files `test_<feature>.py`.

## Local commands

```bash
# quick unit subset
./runtests.sh --quick --unittests

# single module (after editable install)
python -m tests.transforms.test_scale_intensity
python -m tests.losses.test_logcosh_dice_loss
python -m tests.metrics.test_median_absolute_error
python -m tests.networks.blocks.test_layerscale
```

## Docs

Official notes: [@Docs](https://docs.monai.io/en/stable/) (index via Cursor — see `docs/cursor-kit/README.md`).
