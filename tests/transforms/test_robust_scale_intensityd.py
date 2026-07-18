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

from monai.transforms import RobustScaleIntensityd
from tests.test_utils import TEST_NDARRAYS, assert_allclose

IMG = np.arange(64, dtype=np.float32).reshape(1, 8, 8)


def _expected(img: np.ndarray, lower: float, upper: float) -> np.ndarray:
    median = np.percentile(img, 50.0)
    scale = np.percentile(img, upper) - np.percentile(img, lower)
    return ((img - median) / scale).astype(np.float32)


class TestRobustScaleIntensityd(unittest.TestCase):
    @parameterized.expand([[p] for p in TEST_NDARRAYS])
    def test_default_iqr(self, p):
        key = "img"
        result = RobustScaleIntensityd(keys=[key])({key: p(IMG)})[key]
        assert_allclose(result, p(_expected(IMG, 25.0, 75.0)), type_test="tensor", rtol=1e-4, atol=1e-4)

    @parameterized.expand([[p] for p in TEST_NDARRAYS])
    def test_allow_missing_keys(self, p):
        scaler = RobustScaleIntensityd(keys=["missing"], allow_missing_keys=True)
        data = {"img": p(IMG)}
        result = scaler(data)
        assert_allclose(result["img"], data["img"], type_test=False)

    def test_missing_key_raises(self):
        with self.assertRaises(KeyError):
            RobustScaleIntensityd(keys=["missing"])({"img": IMG})


if __name__ == "__main__":
    unittest.main()
