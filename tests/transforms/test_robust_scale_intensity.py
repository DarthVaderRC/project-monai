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
import torch
from parameterized import parameterized

from monai.transforms import RobustScaleIntensity
from monai.transforms.utils_pytorch_numpy_unification import percentile
from tests.test_utils import TEST_NDARRAYS, assert_allclose


def _expected_robust_scale(data, lower=25.0, upper=75.0):
    median = percentile(data, 50.0)
    scale = percentile(data, upper) - percentile(data, lower)
    if scale == 0:
        return data - median
    return (data - median) / scale


class TestRobustScaleIntensity(unittest.TestCase):
    @parameterized.expand([[p] for p in TEST_NDARRAYS])
    def test_iqr_scale(self, p):
        data_np = np.arange(16, dtype=np.float32).reshape(1, 4, 4)
        scaler = RobustScaleIntensity(lower=25.0, upper=75.0)
        result = scaler(p(data_np))
        self.assertTrue(result.dtype in (np.float32, torch.float32))
        expected = p(_expected_robust_scale(data_np))
        assert_allclose(result, expected, type_test="tensor", rtol=1e-5, atol=1e-5)

    @parameterized.expand([[p] for p in TEST_NDARRAYS])
    def test_channel_wise(self, p):
        ch0 = np.arange(16, dtype=np.float32).reshape(4, 4)
        ch1 = np.arange(16, 32, dtype=np.float32).reshape(4, 4)
        data_np = np.stack([ch0, ch1], axis=0)
        scaler = RobustScaleIntensity(channel_wise=True)
        result = scaler(p(data_np))
        for i in range(data_np.shape[0]):
            expected = _expected_robust_scale(data_np[i])
            assert_allclose(result[i], p(expected), type_test="tensor", rtol=1e-5, atol=1e-5)

    @parameterized.expand([[p] for p in TEST_NDARRAYS])
    def test_constant_volume(self, p):
        """Zero IQR should return median-subtracted values (all zeros)."""
        scaler = RobustScaleIntensity()
        data = p(np.ones((1, 4, 4), dtype=np.float32) * 7.0)
        result = scaler(data)
        expected = p(np.zeros((1, 4, 4), dtype=np.float32))
        assert_allclose(result, expected, type_test="tensor", rtol=1e-5, atol=1e-5)

    def test_invalid_percentiles(self):
        with self.assertRaises(ValueError):
            RobustScaleIntensity(lower=75.0, upper=25.0)


if __name__ == "__main__":
    unittest.main()
