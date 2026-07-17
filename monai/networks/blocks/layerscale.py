# Copyright (c) MONAI Consortium
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import torch
import torch.nn as nn


class LayerScale(nn.Module):
    """
    Learnable per-channel scaling for channel-first tensors, based on: "Touvron et al.,
    Going deeper with Image Transformers <https://arxiv.org/abs/2103.17239>" (CaiT).

    Multiplies the input by a learnable per-channel vector ``gamma`` initialized to a small
    value, which lets a residual branch start close to the identity and stabilizes training of
    deep networks. Works for both 2D (``B, C, H, W``) and 3D (``B, C, H, W, D``) inputs.

    Args:
        num_channels: number of channels ``C`` of the input tensor.
        spatial_dims: number of spatial dimensions of the input (2 for images, 3 for volumes).
            Defaults to 2.
        init_value: initial value for every entry of ``gamma``. Defaults to 1e-6.
    """

    def __init__(self, num_channels: int, spatial_dims: int = 2, init_value: float = 1e-6) -> None:
        super().__init__()
        if num_channels < 1:
            raise ValueError(f"num_channels should be a positive integer, got {num_channels}.")
        if spatial_dims < 1:
            raise ValueError(f"spatial_dims should be a positive integer, got {spatial_dims}.")
        self.spatial_dims = spatial_dims
        gamma_shape = (1, num_channels) + (1,) * spatial_dims
        self.gamma = nn.Parameter(init_value * torch.ones(gamma_shape))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x * self.gamma
