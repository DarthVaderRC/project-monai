# Losses: add a loss (progressive-disclosure)

**Load-first (80% of the job):** to add a loss, copy the closest neighbor in `monai/losses/`, subclass `_Loss` (or an existing loss), implement `forward(input, target) -> Tensor`, and register the class name in `monai/losses/__init__.py` (case-insensitive alphabetical; no per-file `__all__`).

Named neighbor for the pack: **`DiceLoss`** in `monai/losses/dice.py`. Reference implementation shipped by this kit: **`LogCoshDiceLoss`** (same file) — a `DiceLoss` subclass whose `forward` wraps the result in `log(cosh(...))`.

## Minimal subclass pattern (verbatim from the shipped example)

```python
class LogCoshDiceLoss(DiceLoss):
    """Log-Cosh smoothed Dice loss (inherits all DiceLoss args)."""

    def forward(self, input: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        dice: torch.Tensor = super().forward(input=input, target=target)
        return torch.log(torch.cosh(dice))
```

## On-demand depth (open only if needed)

- Building a loss from scratch (not subclassing an existing one): read `DiceLoss.__init__` for the `reduction` + flag-validation pattern and `_Loss` base usage.
- Reduction semantics and shapes: `DiceLoss.forward` docstring in `monai/losses/dice.py`.
- Registration exact location: the `from .dice import (...)` block in `monai/losses/__init__.py`.

## Deprecated-API guard

Run `bash docs/cursor-kit/scripts/check-deprecations.sh <touched files>`; do not introduce APIs from `deprecations.md`.
