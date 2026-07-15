# Testing transforms (curated)

Canonical: [`CONTRIBUTING.md`](../../../CONTRIBUTING.md) (Unit testing) and existing tests under `tests/transforms/`.

## Layout & naming

- Transform tests live under `tests/transforms/` (and nested packages when present).
- Name files `test_<feature>.py`; pair array and dict coverage, e.g.:
  - [`tests/transforms/test_scale_intensity.py`](../../../tests/transforms/test_scale_intensity.py)
  - [`tests/transforms/test_scale_intensityd.py`](../../../tests/transforms/test_scale_intensityd.py)

## Patterns to copy

- Prefer **`parameterized`** for input variants (`TEST_NDARRAYS`, shapes, kwargs).
- Use shared helpers from `tests.test_utils` (`assert_allclose`, image test case bases).
- Keep default deps to torch/numpy when possible; optional deps → document and update `tests/min_tests.py` `exclude_cases` if needed.
- Do not commit large binary fixtures.

## Local commands

```bash
# quick unit subset
./runtests.sh --quick --unittests

# single module (after editable install)
python -m tests.transforms.test_scale_intensity
python -m tests.transforms.test_scale_intensityd
```

For new transforms, add matching `test_<name>.py` and `test_<name>d.py` (or equivalent) covering happy path + at least one edge (constant volume, dtype, or channel-wise) when peers do.

## Docs

Official testing/transform notes: [@Docs](https://docs.monai.io/en/stable/) (index via Cursor — see `docs/cursor-kit/README.md`).
