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

import unittest

import numpy as np
from parameterized import parameterized

from monai.transforms import RobustScaleIntensity
from tests.test_utils import TEST_NDARRAYS, assert_allclose

# Dense, deterministic image with a well-defined (non-zero) interquartile range.
IMG = np.arange(64, dtype=np.float32).reshape(1, 8, 8)


def _expected(img: np.ndarray, lower: float, upper: float) -> np.ndarray:
    median = np.percentile(img, 50.0)
    scale = np.percentile(img, upper) - np.percentile(img, lower)
    return ((img - median) / scale).astype(np.float32)


class TestRobustScaleIntensity(unittest.TestCase):
    @parameterized.expand([[p] for p in TEST_NDARRAYS])
    def test_default_iqr(self, p):
        result = RobustScaleIntensity()(p(IMG))
        assert_allclose(result, p(_expected(IMG, 25.0, 75.0)), type_test="tensor", rtol=1e-4, atol=1e-4)

    @parameterized.expand([[p] for p in TEST_NDARRAYS])
    def test_custom_percentiles(self, p):
        result = RobustScaleIntensity(lower=10.0, upper=90.0)(p(IMG))
        assert_allclose(result, p(_expected(IMG, 10.0, 90.0)), type_test="tensor", rtol=1e-4, atol=1e-4)

    @parameterized.expand([[p] for p in TEST_NDARRAYS])
    def test_constant_volume(self, p):
        """Zero inter-percentile range must not produce NaN/Inf (median-subtracted output)."""
        const = np.full((1, 4, 4), 5.0, dtype=np.float32)
        result = RobustScaleIntensity()(p(const))
        assert_allclose(result, p(np.zeros_like(const)), type_test="tensor", rtol=1e-6, atol=1e-6)

    @parameterized.expand([[p] for p in TEST_NDARRAYS])
    def test_channel_wise(self, p):
        data = np.stack([IMG[0], IMG[0] * 2.0, IMG[0] * 3.0]).astype(np.float32)  # (3, 8, 8)
        result = RobustScaleIntensity(channel_wise=True)(p(data))
        for i, c in enumerate(data):
            assert_allclose(result[i], p(_expected(c, 25.0, 75.0)), type_test="tensor", rtol=1e-4, atol=1e-4)

    def test_invalid_percentiles(self):
        with self.assertRaises(ValueError):
            RobustScaleIntensity(lower=80.0, upper=20.0)


if __name__ == "__main__":
    unittest.main()
