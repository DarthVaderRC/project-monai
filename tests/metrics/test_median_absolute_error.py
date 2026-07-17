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

from monai.metrics import MedianAbsoluteErrorMetric

TEST_CASES = [
    [{"reduction": "mean"}, (2, 3), (2, 3)],
    [{"reduction": "mean"}, (4, 1, 8, 8), (4, 1, 8, 8)],
    [{"reduction": "mean"}, (2, 1, 4, 4, 4), (2, 1, 4, 4, 4)],
]


class TestMedianAbsoluteErrorMetric(unittest.TestCase):
    @parameterized.expand(TEST_CASES)
    def test_value(self, input_param, y_pred_shape, y_shape):
        torch.manual_seed(0)
        y_pred = torch.rand(y_pred_shape)
        y = torch.rand(y_shape)

        metric = MedianAbsoluteErrorMetric(**input_param)
        metric(y_pred, y)
        result = metric.aggregate()

        flat = np.abs(y.numpy() - y_pred.numpy()).reshape(y_shape[0], -1)
        expected = np.mean(np.median(flat, axis=1))
        np.testing.assert_allclose(result.cpu().numpy().item(), expected, rtol=1e-5)

    def test_zero_error(self):
        y = torch.ones(3, 1, 5, 5)
        metric = MedianAbsoluteErrorMetric(reduction="mean")
        metric(y, y)
        self.assertAlmostEqual(metric.aggregate().item(), 0.0, places=6)


if __name__ == "__main__":
    unittest.main()
