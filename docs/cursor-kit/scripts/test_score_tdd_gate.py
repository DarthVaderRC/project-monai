from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from score_tdd_gate import (  # type: ignore  # noqa: E402
    REQUIRED_SPEC_HEADINGS,
    score_tdd_gate,
    session_slice,
    verdict_of,
)

_PACK = {
    "pack": "monai",
    "schema_version": 1,
    "tdd": {
        "artifact_paths": {
            "spec": "docs/cursor-kit/work/{issue}/SPEC.md",
            "review": "docs/cursor-kit/work/{issue}/SPEC-REVIEW.md",
            "test": "tests/transforms/test_robust_scale_intensity.py",
        }
    },
    "spec_critic": {"required_verdict_token": "Approve"},
}


def _write_pack(root: Path, pack: dict | None = None) -> None:
    cfg_dir = root / ".cursor"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    (cfg_dir / "pack.config.json").write_text(
        json.dumps(pack if pack is not None else _PACK), encoding="utf-8"
    )


class ScoreTddGateTest(unittest.TestCase):
    def _work(self, tmp: Path, issue: str = "1") -> Path:
        d = tmp / "docs" / "cursor-kit" / "work" / issue
        d.mkdir(parents=True)
        return d

    def test_verdict_approve(self) -> None:
        text = "# Review\n\n- ok\n\nVerdict: Approve\n"
        self.assertEqual(verdict_of(text), "Approve")

    def test_verdict_request_changes(self) -> None:
        self.assertEqual(verdict_of("Verdict: Request changes\n"), "Request changes")

    def test_verdict_missing(self) -> None:
        self.assertIsNone(verdict_of("# no verdict\n"))

    def test_verdict_ignores_prose_mention(self) -> None:
        # Prose "Verdict:" must not double-match; only the last non-empty line counts.
        text = (
            "# Review\n\n"
            "- I'd lean Verdict: Request changes unless criteria tighten.\n\n"
            "Verdict: Approve\n"
        )
        self.assertEqual(verdict_of(text), "Approve")

    def test_verdict_rejects_non_terminal_line(self) -> None:
        text = "Verdict: Approve\n\n## Notes\nmore prose\n"
        self.assertIsNone(verdict_of(text))

    def test_session_slice_from_last_start(self) -> None:
        records = [
            {"ts": "1", "event": "sessionStart"},
            {"ts": "2", "event": "skill", "skill": "old"},
            {"ts": "3", "event": "sessionStart"},
            {
                "ts": "4",
                "event": "subagentStart",
                "subagent_type": "spec-critic",
                "source": "critique-spec",
            },
        ]
        sliced = session_slice(records)
        self.assertEqual(len(sliced), 2)
        self.assertEqual(sliced[0]["event"], "sessionStart")

    def test_fails_without_pack_config(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._work(root)
            ledger = root / ".cursor" / "usage" / "ledger.jsonl"
            ledger.parent.mkdir(parents=True)
            ledger.write_text("", encoding="utf-8")
            result = score_tdd_gate(root, ledger, issue="1")
            self.assertFalse(result["ok"])
            ids = {c["id"] for c in result["checks"] if not c["passed"]}
            self.assertIn("pack_config", ids)

    def test_fails_without_spec(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_pack(root)
            self._work(root)
            ledger = root / ".cursor" / "usage" / "ledger.jsonl"
            ledger.parent.mkdir(parents=True)
            ledger.write_text("", encoding="utf-8")
            result = score_tdd_gate(root, ledger, issue="1")
            self.assertFalse(result["ok"])
            ids = {c["id"] for c in result["checks"] if not c["passed"]}
            self.assertIn("spec_exists", ids)

    def test_fails_without_kit_owned_critic_marker(self) -> None:
        # Cursor-populated subagent_type alone is not enough.
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_pack(root)
            work = self._work(root)
            spec = "\n".join(f"{h}\n\nbody\n" for h in REQUIRED_SPEC_HEADINGS)
            (work / "SPEC.md").write_text(spec, encoding="utf-8")
            (work / "SPEC-REVIEW.md").write_text(
                "## Notes\n\n- aligned\n\nVerdict: Approve\n", encoding="utf-8"
            )
            tests_dir = root / "tests" / "transforms"
            tests_dir.mkdir(parents=True)
            (tests_dir / "test_robust_scale_intensity.py").write_text(
                "raise AssertionError('Layer T red — impl missing')\n",
                encoding="utf-8",
            )
            ledger = root / ".cursor" / "usage" / "ledger.jsonl"
            ledger.parent.mkdir(parents=True)
            rows = [
                {"ts": "2026-07-20T00:00:00+00:00", "event": "sessionStart", "decision": "ok"},
                {
                    "ts": "2026-07-20T00:01:00+00:00",
                    "event": "subagentStart",
                    "decision": "allow",
                    "subagent_type": "spec-critic",
                    "task": "critique SPEC",
                    # missing source=critique-spec
                },
            ]
            ledger.write_text(
                "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8"
            )
            result = score_tdd_gate(root, ledger, issue="1")
            self.assertFalse(result["ok"])
            ids = {c["id"] for c in result["checks"] if not c["passed"]}
            self.assertIn("critic_subagent", ids)

    def test_passes_full_gate(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write_pack(root)
            work = self._work(root)
            spec = "\n".join(f"{h}\n\nbody\n" for h in REQUIRED_SPEC_HEADINGS)
            (work / "SPEC.md").write_text(spec, encoding="utf-8")
            (work / "SPEC-REVIEW.md").write_text(
                "## Notes\n\n- aligned\n\nVerdict: Approve\n", encoding="utf-8"
            )
            # Minimal failing-test marker file (existence + red stub flag)
            tests_dir = root / "tests" / "transforms"
            tests_dir.mkdir(parents=True)
            (tests_dir / "test_robust_scale_intensity.py").write_text(
                "raise AssertionError('Layer T red — impl missing')\n",
                encoding="utf-8",
            )
            ledger = root / ".cursor" / "usage" / "ledger.jsonl"
            ledger.parent.mkdir(parents=True)
            rows = [
                {"ts": "2026-07-20T00:00:00+00:00", "event": "sessionStart", "decision": "ok"},
                {
                    "ts": "2026-07-20T00:01:00+00:00",
                    "event": "subagentStart",
                    "decision": "allow",
                    "subagent_type": "spec-critic",
                    "source": "critique-spec",
                    "task": "critique SPEC",
                },
            ]
            ledger.write_text(
                "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8"
            )
            result = score_tdd_gate(root, ledger, issue="1")
            self.assertTrue(result["ok"], result)


if __name__ == "__main__":
    unittest.main()
