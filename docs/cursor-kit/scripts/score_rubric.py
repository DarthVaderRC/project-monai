#!/usr/bin/env python3
"""Score a MONAI checkout against the EVALUATION.md 12-convention rubric for RobustScaleIntensity."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _grep(pattern: str, text: str) -> bool:
    return re.search(pattern, text, re.M) is not None


def score(root: Path) -> dict:
    array = root / "monai/transforms/intensity/array.py"
    dictionary = root / "monai/transforms/intensity/dictionary.py"
    init = root / "monai/transforms/__init__.py"
    changelog = root / "CHANGELOG.md"
    test_a = root / "tests/transforms/test_robust_scale_intensity.py"
    test_d = root / "tests/transforms/test_robust_scale_intensityd.py"

    array_txt = _read(array)
    dict_txt = _read(dictionary)
    init_txt = _read(init)
    cl_txt = _read(changelog)
    test_a_txt = _read(test_a)
    test_d_txt = _read(test_d)

    # Extract the RobustScaleIntensity class body from array.py (best-effort).
    m = re.search(
        r"class RobustScaleIntensity\b.*?(?=\nclass |\Z)",
        array_txt,
        re.S,
    )
    class_body = m.group(0) if m else ""
    # File head for header / future annotations (first 40 lines of array.py is shared;
    # for kit-off that appends to the same file, header is inherited — score the *new*
    # class file contribution by also checking whether a dedicated new module was used.
    # Convention: Apache header and future annotations are required on the module that
    # defines the class. For in-package appends, the existing module already has them,
    # so we pass only if the defining module has them (fair for both kit-on append and
    # kit-off append into array.py).
    file_head = "\n".join(array_txt.splitlines()[:40])

    has_array = "class RobustScaleIntensity" in array_txt
    has_dict = "class RobustScaleIntensityd" in dict_txt or "class RobustScaleIntensityD" in dict_txt

    results = {}

    results["Apache 2.0 header present"] = {
        "pass": _grep(r"^# Copyright \(c\) MONAI Consortium", file_head)
        and _grep(r"Apache License, Version 2\.0", file_head),
        "evidence": "module head of monai/transforms/intensity/array.py",
    }
    results["from __future__ import annotations"] = {
        "pass": "from __future__ import annotations" in file_head
        or "from __future__ import annotations" in array_txt[:800],
        "evidence": "monai/transforms/intensity/array.py",
    }
    results["Array class + MapTransform d wrapper both present"] = {
        "pass": has_array and has_dict and ("MapTransform" in dict_txt),
        "evidence": f"array={has_array} dict_wrapper={has_dict}",
    }
    results["backend = [TransformBackends.TORCH, TransformBackends.NUMPY]"] = {
        "pass": _grep(
            r"backend\s*=\s*\[TransformBackends\.TORCH,\s*TransformBackends\.NUMPY\]",
            class_body,
        ),
        "evidence": "RobustScaleIntensity.backend in array.py",
    }
    results["MetaTensor-safe (convert_to_tensor track_meta + convert_to_dst_type)"] = {
        "pass": (
            "convert_to_tensor" in class_body
            and "track_meta" in class_body
            and "convert_to_dst_type" in class_body
        ),
        "evidence": "RobustScaleIntensity.__call__ body",
    }

    # Registration / import
    import_ok = False
    import_err = ""
    try:
        proc = subprocess.run(
            [
                sys.executable,
                "-c",
                "from monai.transforms import RobustScaleIntensity, RobustScaleIntensityd; print('ok')",
            ],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=60,
            env={**dict(**{k: v for k, v in __import__("os").environ.items()}), "PYTHONPATH": str(root)},
        )
        import_ok = proc.returncode == 0 and "ok" in proc.stdout
        import_err = (proc.stderr or proc.stdout or "")[-300:]
    except Exception as exc:  # noqa: BLE001
        import_err = str(exc)
    in_all_array = _grep(r"['\"]RobustScaleIntensity['\"]", array_txt) or _grep(
        r"\bRobustScaleIntensity\b", _read(root / "monai/transforms/intensity/__init__.py")
    )
    # Prefer intensity package __all__ / transforms re-export patterns used by MONAI.
    intensity_init = _read(root / "monai/transforms/intensity/__init__.py")
    registered = (
        "RobustScaleIntensity" in init_txt
        and "RobustScaleIntensityd" in dict_txt
        and (
            "RobustScaleIntensity" in intensity_init
            or _grep(r"__all__[\s\S]*RobustScaleIntensity", array_txt)
            or import_ok
        )
    )
    results["Registered in __all__ (array + dict) and monai.transforms re-exports"] = {
        "pass": bool(import_ok),
        "evidence": f"import_ok={import_ok} detail={import_err!r}" if not import_ok else "from monai.transforms import RobustScaleIntensity, RobustScaleIntensityd",
    }

    results["d/D/Dict aliases"] = {
        "pass": (
            "RobustScaleIntensityD" in dict_txt
            and "RobustScaleIntensityDict" in dict_txt
            and "RobustScaleIntensityd" in dict_txt
        ),
        "evidence": "dictionary.py aliases",
    }

    # Deprecated APIs — scan new class + dict wrapper + tests if present
    dep_files = [p for p in (array, dictionary, test_a, test_d) if p.is_file()]
    dep_ok = True
    dep_detail = "skipped (no files)"
    if dep_files:
        script = root / "docs/cursor-kit/scripts/check-deprecations.sh"
        # kit-off worktree may have renamed docs/cursor-kit; fall back to main script patterns
        patterns = [
            (r"\bnp\.float\b", "np.float"),
            (r"\btorch\.range\b", "torch.range"),
            (r"\bnp\.int\b", "np.int"),
            (r"\bnp\.bool\b", "np.bool"),
        ]
        hits = []
        for f in dep_files:
            txt = _read(f)
            # Only scan RobustScale* regions when scanning large shared modules
            if f.name in {"array.py", "dictionary.py"}:
                mm = re.search(r"class RobustScaleIntensity[\s\S]*?(?=\nclass |\Z)", txt)
                txt = mm.group(0) if mm else ""
                if f.name == "dictionary.py":
                    mm2 = re.search(r"class RobustScaleIntensityd[\s\S]*?(?=\nclass |\Z)", _read(f))
                    txt += "\n" + (mm2.group(0) if mm2 else "")
            for pat, name in patterns:
                if re.search(pat, txt):
                    hits.append(f"{f.name}:{name}")
        dep_ok = len(hits) == 0
        dep_detail = "clean" if dep_ok else ",".join(hits)
    results["No deprecated APIs (np.float, torch.range, ...)"] = {
        "pass": dep_ok,
        "evidence": dep_detail,
    }

    # Tests
    tests_exist = test_a.is_file() and test_d.is_file()
    parameterized = ("parameterized" in test_a_txt) or ("@parameterized" in test_a_txt)
    edge = bool(
        re.search(r"constant|zeros|edge|channel_wise|dtype", test_a_txt + test_d_txt, re.I)
    )
    tests_pass = False
    test_detail = "missing files"
    if tests_exist:
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "tests.transforms.test_robust_scale_intensity",
                "tests.transforms.test_robust_scale_intensityd",
            ],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=180,
            env={**dict(**{k: v for k, v in __import__("os").environ.items()}), "PYTHONPATH": str(root)},
        )
        tests_pass = proc.returncode == 0
        test_detail = (proc.stderr + proc.stdout)[-400:]
    results["Parameterized tests for array + d, incl. an edge case"] = {
        "pass": bool(tests_exist and parameterized and edge and tests_pass),
        "evidence": f"files={tests_exist} parameterized={parameterized} edge={edge} unittest_ok={tests_pass} {test_detail!r}",
    }

    # American English — only scan RobustScale* class bodies (not unrelated peers in the same file)
    dict_class = ""
    md = re.search(r"class RobustScaleIntensityd\b.*?(?=\nclass |\Z)", dict_txt, re.S)
    if md:
        dict_class = md.group(0)
    british = re.findall(
        r"\b(normalise|normalising|visualise|colour|behaviour|favourite)\b",
        class_body + dict_class,
        re.I,
    )
    results["American English"] = {
        "pass": has_array and len(british) == 0,
        "evidence": "no British spellings in RobustScale* class text"
        if not british
        else f"found {british}",
    }

    # Boundary respect — for kit-on, check ledger if provided; for kit-off, check whether
    # implementation imported from monai.networks (out of intensity allowlist spirit).
    networks_import = bool(
        re.search(r"from monai\.networks|import monai\.networks", class_body + dict_txt + test_a_txt + test_d_txt)
    )
    results["Stays within approved boundaries (no monai/networks reads)"] = {
        "pass": has_array and not networks_import,
        "evidence": "no monai.networks imports in RobustScale* sources/tests"
        if not networks_import
        else "monai.networks referenced",
    }

    results["Changelog [Unreleased] entry"] = {
        "pass": bool(
            re.search(r"\[Unreleased\][\s\S]{0,800}RobustScaleIntensity", cl_txt)
        ),
        "evidence": "CHANGELOG.md [Unreleased] mentions RobustScaleIntensity",
    }

    # Fix unused var warning path
    _ = (in_all_array, registered)

    passed = sum(1 for v in results.values() if v["pass"])
    total = len(results)
    return {
        "root": str(root),
        "passed": passed,
        "total": total,
        "score": f"{passed}/{total}",
        "results": results,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path)
    ap.add_argument("--json-out", type=Path)
    args = ap.parse_args()
    report = score(args.root.resolve())
    text_lines = [f"Score: {report['score']}  ({report['root']})", ""]
    for name, item in report["results"].items():
        mark = "PASS" if item["pass"] else "FAIL"
        text_lines.append(f"- [{mark}] {name} — {item['evidence']}")
    print("\n".join(text_lines))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
