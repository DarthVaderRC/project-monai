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

"""Tests for RobustScaleIntensityd (issue #1)."""

from __future__ import annotations

import unittest

import numpy as np
import torch
from parameterized import parameterized

from monai.transforms import RobustScaleIntensityD, RobustScaleIntensityd, RobustScaleIntensityDict
from tests.test_utils import TEST_NDARRAYS, assert_allclose

IMG = np.arange(64, dtype=np.float32).reshape(1, 8, 8)


def _expected(img: np.ndarray, lower: float, upper: float) -> np.ndarray:
    median = np.percentile(img, 50.0)
    scale = np.percentile(img, upper) - np.percentile(img, lower)
    return ((img - median) / scale).astype(np.float32)


class TestRobustScaleIntensityd(unittest.TestCase):
    def test_aliases(self):
        """D / Dict aliases must resolve to the map transform (registration smoke)."""
        self.assertIs(RobustScaleIntensityD, RobustScaleIntensityd)
        self.assertIs(RobustScaleIntensityDict, RobustScaleIntensityd)

    @parameterized.expand([[p] for p in TEST_NDARRAYS])
    def test_default_iqr(self, p):
        """Happy path on keyed dict entry; median/IQR scale matches array formula."""
        key = "img"
        result = RobustScaleIntensityd(keys=[key])({key: p(IMG)})[key]
        assert_allclose(result, p(_expected(IMG, 25.0, 75.0)), type_test="tensor", rtol=1e-4, atol=1e-4)

    @parameterized.expand([[p] for p in TEST_NDARRAYS])
    def test_preserves_non_target_keys(self, p):
        """Only targeted keys are scaled; sibling keys are preserved."""
        label = np.zeros((1, 8, 8), dtype=np.uint8)
        data = {"img": p(IMG), "label": p(label)}
        result = RobustScaleIntensityd(keys=["img"])(data)
        assert_allclose(result["img"], p(_expected(IMG, 25.0, 75.0)), type_test="tensor", rtol=1e-4, atol=1e-4)
        assert_allclose(result["label"], data["label"], type_test=False)

    @parameterized.expand([[p] for p in TEST_NDARRAYS])
    def test_channel_wise(self, p):
        key = "img"
        data = np.stack([IMG[0], IMG[0] * 2.0]).astype(np.float32)
        result = RobustScaleIntensityd(keys=[key], channel_wise=True)({key: p(data)})[key]
        for i, c in enumerate(data):
            assert_allclose(result[i], p(_expected(c, 25.0, 75.0)), type_test="tensor", rtol=1e-4, atol=1e-4)

    @parameterized.expand([[p] for p in TEST_NDARRAYS])
    def test_constant_volume(self, p):
        key = "img"
        const = np.full((1, 4, 4), 7.0, dtype=np.float32)
        result = RobustScaleIntensityd(keys=[key])({key: p(const)})[key]
        assert_allclose(result, p(np.zeros_like(const)), type_test="tensor", rtol=1e-6, atol=1e-6)
        self.assertTrue(np.isfinite(np.asarray(result)).all())

    @parameterized.expand([[p] for p in TEST_NDARRAYS])
    def test_dtype(self, p):
        key = "img"
        result = RobustScaleIntensityd(keys=[key], dtype=np.float64)({key: p(IMG)})[key]
        if isinstance(result, torch.Tensor):
            self.assertEqual(result.dtype, torch.float64)
        else:
            self.assertEqual(result.dtype, np.float64)

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
