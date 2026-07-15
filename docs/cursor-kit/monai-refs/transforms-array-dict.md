# Transforms: array + dictionary (`d`) pattern

Curated notes for Cursor agents. Canonical sources beat this file when they disagree.

## Where to look

| Kind | Path |
|---|---|
| Array intensity transforms | [`monai/transforms/intensity/array.py`](../../../monai/transforms/intensity/array.py) |
| Dict wrappers | [`monai/transforms/intensity/dictionary.py`](../../../monai/transforms/intensity/dictionary.py) |
| Base classes | [`monai/transforms/transform.py`](../../../monai/transforms/transform.py) |
| Official docs | [@Docs](https://docs.monai.io/en/stable/) → Transforms |

## Array transform (pattern)

Peers such as `ScaleIntensity` / `NormalizeIntensity`:

1. Subclass `Transform` (or `RandomizableTransform`).
2. Set `backend = [TransformBackends.TORCH, TransformBackends.NUMPY]` when neighbors do.
3. Implement `__call__(self, img: NdarrayOrTensor) -> NdarrayOrTensor`.
4. Append the class name to the module `__all__`.
5. Prefer **appending** into the existing intensity modules rather than a new file.

## Dictionary transform (pattern)

Peers such as `ScaleIntensityd`:

1. Subclass `MapTransform`.
2. `backend = <ArrayClass>.backend`.
3. `__init__` takes `keys` (+ `allow_missing_keys`); construct/hold the array transform.
4. `__call__` copies the mapping, iterates `self.key_iterator(d)`, applies the array transform per key.
5. Export aliases at module bottom: `FooD = FooDict = Food` (existing convention).
6. Append to `__all__` (include aliases if peers do).

## Registration checklist

- [ ] Class in `array.py` + name in `__all__`
- [ ] Class in `dictionary.py` + aliases + `__all__`
- [ ] Re-exported via package public API (`monai.transforms` / intensity package inits) as peers require
- [ ] Apache 2.0 header + `from __future__ import annotations`
- [ ] Google-style docstrings pointing dict wrapper at the array class

## Do not scaffold

Soft-clip intensity already exists (`ClipIntensityPercentiles`, `soft_clip` util). Do not add `SoftClipIntensity`.

## Demo catalog (this fork)

Primary: `RobustScaleIntensity` / `RobustScaleIntensityd`. Backups: `AsinhIntensity`, `TanhSqueezeIntensity`.
