# Deprecated / removed APIs to avoid in transforms

Curated list of APIs that a naive scaffold might emit but that are deprecated or
removed. MONAI marks its own removals with `@deprecated` / `@deprecated_arg` /
`@deprecated_arg_default` from `monai/utils/deprecate_utils.py`; the numpy/torch
entries below are the most common real mistakes when generating new intensity
transforms.

`docs/cursor-kit/scripts/check-deprecations.sh` parses the machine-readable block
below (`regex | reason`) and greps touched `monai/transforms/**` and
`tests/transforms/**` files. Keep the two views in sync when you add a rule.

## Human summary

| API | Status | Use instead |
|---|---|---|
| `np.float`, `np.int`, `np.bool`, `np.object`, `np.str` | Removed (numpy >= 1.24) | `np.float32` / `float`, `int`, `bool`, `object`, `str` |
| `np.float_`, `np.complex_` | Removed (numpy 2.0) | `np.float64`, `np.complex128` |
| `torch.range` | Removed | `torch.arange` |
| `.type(torch.FloatTensor)` | Legacy | `.to(dtype=...)` / `convert_to_tensor` |
| `np.bool8` | Removed | `np.bool_` |

MONAI-specific: do not reintroduce arguments already marked `@deprecated_arg`
(e.g. loss `y_pred`/`y_true` -> `input`/`target`); prefer the current signatures
of neighboring transforms.

## Machine-readable rules (used by check-deprecations.sh)

<!-- deprecations:start -->
np\.float\b | numpy alias np.float was removed (numpy>=1.24); use np.float32/np.float64 or float
np\.int\b | numpy alias np.int was removed; use int or np.int64
np\.bool\b | numpy alias np.bool was removed; use bool or np.bool_
np\.object\b | numpy alias np.object was removed; use object
np\.str\b | numpy alias np.str was removed; use str
np\.float_ | np.float_ removed in numpy 2.0; use np.float64
np\.complex_ | np.complex_ removed in numpy 2.0; use np.complex128
np\.bool8 | np.bool8 removed; use np.bool_
torch\.range\b | torch.range was removed; use torch.arange
\.type\(torch\.[A-Za-z]+Tensor\) | legacy tensor typing; use .to(dtype=...) or convert_to_tensor
<!-- deprecations:end -->
