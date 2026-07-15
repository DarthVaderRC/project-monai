# Transforms: array + dictionary (`d`) pattern

Curated, offline-sufficient notes for Cursor agents. Canonical source files beat this
file when they disagree. You should be able to scaffold a correct intensity transform
from this page alone, without `@Docs` or opening unrelated packages.

## Where to look

| Kind | Path |
|---|---|
| Array intensity transforms | [`monai/transforms/intensity/array.py`](../../../monai/transforms/intensity/array.py) |
| Dict wrappers | [`monai/transforms/intensity/dictionary.py`](../../../monai/transforms/intensity/dictionary.py) |
| Base classes | [`monai/transforms/transform.py`](../../../monai/transforms/transform.py) |
| Public re-exports | [`monai/transforms/__init__.py`](../../../monai/transforms/__init__.py) |
| Official docs (optional) | [@Docs](https://docs.monai.io/en/stable/) -> Transforms |

## Required imports (array module already has these)

```python
from __future__ import annotations

import numpy as np
import torch

from monai.config import DtypeLike
from monai.config.type_definitions import NdarrayOrTensor
from monai.data.meta_obj import get_track_meta
from monai.transforms.transform import RandomizableTransform, Transform
from monai.utils.enums import TransformBackends
from monai.utils.type_conversion import convert_data_type, convert_to_dst_type, convert_to_tensor
```

## Array transform pattern (copy `ScaleIntensity` / `NormalizeIntensity`)

Non-negotiable conventions observed across neighbors:

1. Subclass `Transform` (deterministic) or `RandomizableTransform` (random).
2. Class attribute: `backend = [TransformBackends.TORCH, TransformBackends.NUMPY]`.
3. `__init__` stores plain params; `dtype: DtypeLike = np.float32` is the common default.
4. `__call__(self, img: NdarrayOrTensor) -> NdarrayOrTensor` must:
   - normalize input: `img = convert_to_tensor(img, track_meta=get_track_meta())`
   - compute on a meta-free view: `img_t = convert_to_tensor(img, track_meta=False)`
   - restore dtype/type and MetaTensor via `convert_to_dst_type(ret, dst=img, dtype=...)[0]`
5. Support `channel_wise` when peers do (iterate `for d in img_t: ...` then `torch.stack`).

Skeleton (deterministic):

```python
class RobustScaleIntensity(Transform):
    """Scale intensity robustly using the median and IQR (outlier-resistant)."""

    backend = [TransformBackends.TORCH, TransformBackends.NUMPY]

    def __init__(self, channel_wise: bool = False, dtype: DtypeLike = np.float32) -> None:
        self.channel_wise = channel_wise
        self.dtype = dtype

    def __call__(self, img: NdarrayOrTensor) -> NdarrayOrTensor:
        img = convert_to_tensor(img, track_meta=get_track_meta())
        img_t = convert_to_tensor(img, track_meta=False)
        # ... compute robust-scaled `ret` (torch ops so both backends work) ...
        ret = convert_to_dst_type(ret, dst=img, dtype=self.dtype or img_t.dtype)[0]
        return ret
```

Random transforms additionally subclass `RandomizableTransform`, implement
`randomize(self, data)` to draw params, and gate work behind
`self._do_transform` (set by `super().__call__` / `randomize`), exactly like
`RandScaleIntensity`.

## Dictionary transform pattern (copy `ScaleIntensityd`)

1. Subclass `MapTransform` (or `RandomizableTransform, MapTransform` for random).
2. `backend = <ArrayClass>.backend` (reuse, do not re-list).
3. `__init__(self, keys: KeysCollection, ..., allow_missing_keys: bool = False)`:
   - call `super().__init__(keys, allow_missing_keys)`
   - construct and hold the array transform (e.g. `self.scaler = RobustScaleIntensity(...)`).
4. `__call__(self, data)`:

```python
def __call__(self, data: Mapping[Hashable, NdarrayOrTensor]) -> dict[Hashable, NdarrayOrTensor]:
    d = dict(data)
    for key in self.key_iterator(d):
        d[key] = self.scaler(d[key])
    return d
```

5. Aliases at the bottom of `dictionary.py` (exact existing convention):

```python
RobustScaleIntensityD = RobustScaleIntensityDict = RobustScaleIntensityd
```

## Registration checklist (three places — miss one and imports break)

- [ ] `array.py`: append `"RobustScaleIntensity"` to that module's top-level `__all__`.
- [ ] `dictionary.py`: append `"RobustScaleIntensityd"`, `"RobustScaleIntensityD"`,
      `"RobustScaleIntensityDict"` to that module's top-level `__all__`, and add the
      alias assignment line at the bottom.
- [ ] `monai/transforms/__init__.py`: add the array name to the `intensity.array`
      import block and the `d` + `D` names to the `intensity.dictionary` import block
      (follow the existing `ScaleIntensity` / `ScaleIntensityd` / `ScaleIntensityD` lines).
- [ ] Apache 2.0 header + `from __future__ import annotations` (already present when appending).
- [ ] Google-style docstring; the dict wrapper docstring points at the array class via
      `:py:class:`monai.transforms.RobustScaleIntensity``.

## Do not scaffold

Soft-clip intensity already exists (`ClipIntensityPercentiles`, `soft_clip` util). Do not
add `SoftClipIntensity`.

## Deprecated-API guard

Do not introduce APIs flagged in [`deprecations.md`](deprecations.md). MONAI marks
removals with `@deprecated` / `@deprecated_arg` from `monai/utils/deprecate_utils.py`;
run `bash docs/cursor-kit/scripts/check-deprecations.sh` on touched files.

## Demo catalog (this fork)

Primary: `RobustScaleIntensity` / `RobustScaleIntensityd`.
Backups: `AsinhIntensity`, `TanhSqueezeIntensity` (same shape, different math).
