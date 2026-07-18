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

from monai.transforms import RobustScaleIntensity, RobustScaleIntensityd
from tests.test_utils import TEST_NDARRAYS, assert_allclose


class TestRobustScaleIntensityd(unittest.TestCase):
    @parameterized.expand([[p] for p in TEST_NDARRAYS])
    def test_iqr_scale(self, p):
        key = "img"
        data = p(np.arange(16, dtype=np.float32).reshape(1, 4, 4))
        result = RobustScaleIntensityd(keys=[key], lower=25.0, upper=75.0)({key: data})
        expected = RobustScaleIntensity(lower=25.0, upper=75.0)(data)
        assert_allclose(result[key], expected, type_test="tensor", rtol=1e-5, atol=1e-5)

    @parameterized.expand([[p] for p in TEST_NDARRAYS])
    def test_matches_array(self, p):
        key = "img"
        data = p(np.arange(16, dtype=np.float32).reshape(1, 4, 4))
        out_d = RobustScaleIntensityd(keys=[key])({key: data})[key]
        out_a = RobustScaleIntensity()(data)
        assert_allclose(out_d, out_a, type_test="tensor", rtol=1e-5, atol=1e-5)

    @parameterized.expand([[p] for p in TEST_NDARRAYS])
    def test_channel_wise(self, p):
        key = "img"
        ch0 = np.arange(16, dtype=np.float32).reshape(4, 4)
        ch1 = np.arange(16, 32, dtype=np.float32).reshape(4, 4)
        data = p(np.stack([ch0, ch1], axis=0))
        result = RobustScaleIntensityd(keys=[key], channel_wise=True)({key: data})
        expected = RobustScaleIntensity(channel_wise=True)(data)
        assert_allclose(result[key], expected, type_test="tensor", rtol=1e-5, atol=1e-5)

    @parameterized.expand([[p] for p in TEST_NDARRAYS])
    def test_constant_volume(self, p):
        key = "img"
        data = p(np.ones((1, 4, 4), dtype=np.float32) * 7.0)
        result = RobustScaleIntensityd(keys=[key])({key: data})
        expected = RobustScaleIntensity()(data)
        assert_allclose(result[key], expected, type_test="tensor", rtol=1e-5, atol=1e-5)


if __name__ == "__main__":
    unittest.main()
