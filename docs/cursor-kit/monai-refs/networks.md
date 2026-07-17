# Network blocks: add a block (progressive-disclosure)

**Load-first (80% of the job):** to add a block, create `monai/networks/blocks/<name>.py` with an `nn.Module` subclass, support 2D/3D via `spatial_dims`, implement `forward(x) -> Tensor`, and register `from .<name> import <Class>` in `monai/networks/blocks/__init__.py`. Access via `from monai.networks.blocks import <Class>` (NOT `monai.networks`).

Named neighbor (simple, no spatial_dims): **`MLPBlock`** in `monai/networks/blocks/mlp.py`. Named neighbor (spatial_dims factory idiom): **`aspp.py`**. Reference implementation shipped by this kit: **`LayerScale`** in `monai/networks/blocks/layerscale.py`.

## Minimal block pattern (verbatim from the shipped example)

```python
class LayerScale(nn.Module):
    """Learnable per-channel scale (CaiT); works for 2D and 3D channel-first inputs."""

    def __init__(self, num_channels: int, spatial_dims: int = 2, init_value: float = 1e-6) -> None:
        super().__init__()
        if num_channels < 1:
            raise ValueError(f"num_channels should be a positive integer, got {num_channels}.")
        if spatial_dims < 1:
            raise ValueError(f"spatial_dims should be a positive integer, got {spatial_dims}.")
        gamma_shape = (1, num_channels) + (1,) * spatial_dims
        self.gamma = nn.Parameter(init_value * torch.ones(gamma_shape))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x * self.gamma
```

## On-demand depth (open only if needed)

- Dimension-aware conv/norm: `Conv[Conv.CONV, spatial_dims](...)` — see `monai/networks/blocks/aspp.py` (import `from monai.networks.layers.factories import Conv`).
- `get_norm_layer` / `get_conv_layer` idiom: `monai/networks/blocks/segresnet_block.py` (`ResBlock`).

## Test pattern (must cover 2D and 3D)

Build via `**input_param`, run under `from monai.networks import eval_mode`, assert output shape. Include both a 2D shape `(B, C, H, W)` and a 3D shape `(B, C, H, W, D)` case (see `tests/networks/blocks/test_layerscale.py`).
