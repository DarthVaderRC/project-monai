# Metrics: add a metric (progressive-disclosure)

**Load-first (80% of the job):** to add a regression metric, subclass `RegressionMetric`, implement `_compute_metric(y_pred, y) -> Tensor` returning shape `(batch, 1)`, and register in `monai/metrics/__init__.py` (case-insensitive alphabetical; no per-file `__all__`). Reduction across the batch is automatic via `aggregate()`.

Named neighbor: **`MAEMetric`** in `monai/metrics/regression.py`. Reference implementation shipped by this kit: **`MedianAbsoluteErrorMetric`** (same file).

## Minimal subclass pattern (verbatim from the shipped example)

```python
class MedianAbsoluteErrorMetric(RegressionMetric):
    """Median absolute error (batch reduction handled by aggregate())."""

    def __init__(self, reduction=MetricReduction.MEAN, get_not_nans: bool = False) -> None:
        super().__init__(reduction=reduction, get_not_nans=get_not_nans)

    def _compute_metric(self, y_pred: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        flt = partial(torch.flatten, start_dim=1)
        return torch.quantile(flt(torch.abs(y - y_pred)), 0.5, dim=-1, keepdim=True)
```

## On-demand depth (open only if needed)

- Base contract (`_compute_tensor`, `aggregate`, `_check_shape`): read `RegressionMetric` in `monai/metrics/regression.py`.
- Mean-style reduction helper: `compute_mean_error_metrics` in the same file (uses `torch.mean`; do NOT reuse for median).
- Non-regression metrics: subclass `CumulativeIterationMetric` (`monai/metrics/metric.py`).

## Test pattern

The regression metric test file (`tests/metrics/test_compute_regression_metrics.py`) does NOT use `parameterized`; it loops shapes and compares against a numpy reference. New standalone metric tests may use `parameterized` (see `tests/metrics/test_median_absolute_error.py`). Lifecycle: `m = Metric(...); m(y_pred, y); m.aggregate()`.
