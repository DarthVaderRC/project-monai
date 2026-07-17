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

from monai.losses import DiceLoss, LogCoshDiceLoss

TEST_CASES = [
    [
        {"include_background": True, "sigmoid": True, "smooth_nr": 1e-6, "smooth_dr": 1e-6},
        {
            "input": torch.tensor([[[[1.0, -1.0], [-1.0, 1.0]]]]),
            "target": torch.tensor([[[[1.0, 0.0], [1.0, 1.0]]]]),
        },
    ],
    [
        {"include_background": True, "softmax": True, "reduction": "sum"},
        {
            "input": torch.tensor([[[1.0, 1.0], [2.0, 2.0]], [[1.0, 1.0], [2.0, 2.0]]]),
            "target": torch.tensor([[[1.0, 0.0], [0.0, 1.0]], [[0.0, 1.0], [1.0, 0.0]]]),
        },
    ],
]


class TestLogCoshDiceLoss(unittest.TestCase):
    @parameterized.expand(TEST_CASES)
    def test_equals_logcosh_of_dice(self, input_param, input_data):
        dice = DiceLoss(**input_param).forward(**input_data)
        result = LogCoshDiceLoss(**input_param).forward(**input_data)
        expected = torch.log(torch.cosh(dice))
        np.testing.assert_allclose(result.detach().cpu().numpy(), expected.detach().cpu().numpy(), rtol=1e-5)

    def test_output_is_finite_and_nonnegative(self):
        input_data = {
            "input": torch.tensor([[[[1.0, -1.0], [-1.0, 1.0]]]]),
            "target": torch.tensor([[[[1.0, 0.0], [1.0, 1.0]]]]),
        }
        result = LogCoshDiceLoss(sigmoid=True).forward(**input_data)
        self.assertTrue(torch.isfinite(result).all())
        self.assertGreaterEqual(result.item(), 0.0)


if __name__ == "__main__":
    unittest.main()
