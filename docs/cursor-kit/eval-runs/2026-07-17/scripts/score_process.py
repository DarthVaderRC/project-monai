#!/usr/bin/env python3
"""Score scaffold/QA process metrics for the kit discriminating evaluation.

Measures what the 12-convention rubric cannot: planted defects, gate catches, QA fixes.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _extract_class(text: str, name: str) -> str:
    m = re.search(rf"class {re.escape(name)}\b.*?(?=\nclass |\Z)", text, re.S)
    return m.group(0) if m else ""


def _run(cmd: list[str], cwd: Path, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    import os

    env = {**os.environ, "PYTHONPATH": str(cwd)}
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout, env=env)


def score_process(root: Path, transform: str, stage: str = "post_scaffold") -> dict:
    """transform e.g. AsinhIntensity -> array AsinhIntensity, dict AsinhIntensityd."""
    dict_name = f"{transform}d"
    array = root / "monai/transforms/intensity/array.py"
    dictionary = root / "monai/transforms/intensity/dictionary.py"
    test_a = root / f"tests/transforms/test_{_snake(transform)}.py"
    test_d = root / f"tests/transforms/test_{_snake(transform)}d.py"
    dep_script = root / "docs/cursor-kit/scripts/check-deprecations.sh"
    if not dep_script.is_file():
        dep_script = root / "docs/cursor-kit.off/scripts/check-deprecations.sh"
    if not (root / "docs/cursor-kit/monai-refs/deprecations.md").is_file():
        # Kit-off worktrees rename docs/cursor-kit -> .off; run gate from main checkout.
        main_root = Path(__file__).resolve().parents[5]
        main_script = main_root / "docs/cursor-kit/scripts/check-deprecations.sh"
        if main_script.is_file():
            dep_script = main_script

    array_txt = _read(array)
    dict_txt = _read(dictionary)
    array_body = _extract_class(array_txt, transform)
    dict_body = _extract_class(dict_txt, dict_name)

    has_array = bool(array_body)
    has_dict = bool(dict_body)

    # Planted defect 1: np.float default (not np.float32)
    dep_in_array = bool(re.search(r"dtype[^=]*=\s*np\.float\b", array_body)) or bool(
        re.search(r"\bnp\.float\b", array_body)
    )
    dep_in_dict = bool(re.search(r"dtype[^=]*=\s*np\.float\b", dict_body)) or bool(
        re.search(r"\bnp\.float\b", dict_body)
    )
    planted_deprecation = dep_in_array or dep_in_dict

    # Planted defect 2: *d missing from dictionary __all__
    in_dict_all = bool(re.search(rf"['\"]{dict_name}['\"]", dict_txt.split("__all__")[1][:2000] if "__all__" in dict_txt else ""))
    # safer: parse __all__ block
    all_match = re.search(r"__all__\s*=\s*\[(.*?)\]", dict_txt, re.S)
    all_names = all_match.group(1) if all_match else ""
    in_dict_all = dict_name in all_names.replace("'", '"').split('"') or f'"{dict_name}"' in all_names or f"'{dict_name}'" in all_names
    planted_registration_gap = has_dict and not in_dict_all

    # Deprecation gate
    dep_gate_exit = None
    dep_gate_detail = "no script"
    targets = [p for p in (array, dictionary, test_a, test_d) if p.is_file()]
    if dep_script.is_file() and targets:
        proc = _run(["bash", str(dep_script), *[str(p) for p in targets]], root)
        dep_gate_exit = proc.returncode
        dep_gate_detail = (proc.stdout + proc.stderr)[-500:]
    elif not targets:
        dep_gate_exit = -1
        dep_gate_detail = "no transform files"

    # Import gate
    import_ok = False
    import_detail = ""
    if has_array:
        proc = _run(
            [
                sys.executable,
                "-c",
                f"from monai.transforms import {transform}, {dict_name}; print('ok')",
            ],
            root,
        )
        import_ok = proc.returncode == 0
        import_detail = (proc.stderr + proc.stdout)[-300:]

    # Tests
    tests_exist = test_a.is_file() and test_d.is_file()
    tests_pass = False
    test_detail = "missing"
    if tests_exist:
        proc = _run(
            [
                sys.executable,
                "-m",
                "unittest",
                f"tests.transforms.test_{_snake(transform)}",
                f"tests.transforms.test_{_snake(transform)}d",
            ],
            root,
            timeout=180,
        )
        tests_pass = proc.returncode == 0
        test_detail = (proc.stdout + proc.stderr)[-400:]

    # Ship-ready: what /prep-for-ci cares about at transform scope
    ship_ready = (
        has_array
        and has_dict
        and not planted_deprecation
        and not planted_registration_gap
        and dep_gate_exit == 0
        and import_ok
        and tests_exist
        and tests_pass
    )

    metrics = {
        "transform_present_array": has_array,
        "transform_present_dict": has_dict,
        "planted_deprecation_np_float": planted_deprecation,
        "planted_registration_gap_dict_all": planted_registration_gap,
        "deprecations_gate_fails": dep_gate_exit == 1,
        "deprecations_gate_exit": dep_gate_exit,
        "dict_import_ok": import_ok,
        "tests_exist": tests_exist,
        "tests_pass": tests_pass,
        "ship_ready": ship_ready,
    }

    # Process scorecard (6 discriminating signals)
    process = {
        "scaffold_planted_both_defects": planted_deprecation and planted_registration_gap,
        "gate_catches_deprecation": dep_gate_exit == 1,
        "import_fails_while_gap_open": not import_ok and planted_registration_gap,
        "qa_would_be_needed": planted_deprecation or planted_registration_gap,
        "ship_ready_after_stage": ship_ready,
    }

    return {
        "root": str(root),
        "transform": transform,
        "stage": stage,
        "metrics": metrics,
        "process": process,
        "evidence": {
            "deprecation": f"array={dep_in_array} dict={dep_in_dict}",
            "registration": f"{dict_name} in dictionary __all__={in_dict_all}",
            "dep_gate": dep_gate_detail,
            "import": import_detail,
            "tests": test_detail,
        },
    }


def _snake(name: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return s.lower()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--transform", default="AsinhIntensity")
    ap.add_argument("--stage", default="post_scaffold")
    ap.add_argument("--json-out", type=Path)
    args = ap.parse_args()
    report = score_process(args.root.resolve(), args.transform, args.stage)
    m = report["metrics"]
    p = report["process"]
    print(f"Process score — {args.stage} @ {args.root}")
    print(f"  planted np.float: {m['planted_deprecation_np_float']}")
    print(f"  planted __all__ gap: {m['planted_registration_gap_dict_all']}")
    print(f"  deprecations gate fails: {m['deprecations_gate_fails']} (exit={m['deprecations_gate_exit']})")
    print(f"  dict import ok: {m['dict_import_ok']}")
    print(f"  tests pass: {m['tests_pass']} (exist={m['tests_exist']})")
    print(f"  ship_ready: {m['ship_ready']}")
    print(f"  process: {json.dumps(p)}")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
