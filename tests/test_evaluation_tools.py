"""Unit tests for strict scoring and artifact-pinned comparison."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from score_evaluation import EvaluationError, WEIGHTS, score, load_json
from compare_evaluations import compare


def full(value: int = 5) -> dict[str, int]:
    return {key: value for key in WEIGHTS}


class ScorerTests(unittest.TestCase):
    def test_weighted_math(self):
        for number, expected in ((10, 100), (0, 0), (5, 50)):
            self.assertEqual(score(full(number))["weighted_total"], expected)
        special = full(0)
        special["accuracy"] = 10
        self.assertEqual(score(special)["weighted_total"], 12)

    def test_reject_bool_nan_and_infinity(self):
        for value in (True, float("nan"), float("inf"), float("-inf")):
            bad = full()
            bad["accuracy"] = value
            with self.subTest(value=value), self.assertRaises(EvaluationError):
                score(bad)

    def test_reject_missing_unknown_out_of_range_and_wrong_type(self):
        cases = [
            dict(list(full().items())[:-1]),
            {**full(), "unknown": 7},
            {**full(), "evidence": -1},
            {**full(), "security": 11},
            {**full(), "verification": "10"},
            [],
        ]
        for bad in cases:
            with self.subTest(bad=bad), self.assertRaises(EvaluationError):
                score(bad)

    def test_reject_nonstandard_json_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "score.json"
            p.write_text('{"value": NaN}', encoding="utf-8")
            with self.assertRaises(EvaluationError):
                load_json(p)


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        items = {}
        for label, content in (("baseline", "Baseline observation"), ("candidate", "Candidate observation")):
            path = self.root / f"{label}.txt"
            path.write_text(content, encoding="utf-8")
            items[label] = {
                "artifact": path.name,
                "artifact_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "scores": full(4 if label == "baseline" else 6),
            }
        self.manifest = {
            "schema_version": 1,
            "case_id": "synthetic-test",
            "controls": {
                "model": "test-model",
                "task_sha256": "0" * 64,
                "tools": [],
                "token_budget": 4000,
                "evaluator": "unit-test",
            },
            **items,
        }
        self.file = self.root / "manifest.json"
        self.save()

    def save(self):
        self.file.write_text(json.dumps(self.manifest), encoding="utf-8")

    def test_improvement(self):
        result = compare(self.file)
        self.assertEqual(result["verdict"], "IMPROVED")
        self.assertEqual(result["score_delta"], 20)

    def test_tie_and_critical_regression(self):
        self.manifest["candidate"]["scores"] = full(4)
        self.save()
        self.assertEqual(compare(self.file)["verdict"], "TIE")
        self.manifest["candidate"]["scores"] = full(3)
        self.save()
        self.assertEqual(compare(self.file)["verdict"], "CRITICAL_REGRESSION")

    def test_reject_tampered_artifact(self):
        (self.root / "candidate.txt").write_text("Tampered", encoding="utf-8")
        with self.assertRaises(EvaluationError):
            compare(self.file)

    def test_reject_path_traversal(self):
        self.manifest["candidate"]["artifact"] = "../external.txt"
        self.save()
        with self.assertRaises(EvaluationError):
            compare(self.file)

    def test_reject_invalid_controls(self):
        for invalid in (True, 0, -5, "100"):
            self.manifest["controls"]["token_budget"] = invalid
            self.save()
            with self.subTest(invalid=invalid), self.assertRaises(EvaluationError):
                compare(self.file)

    def test_reject_missing_score(self):
        del self.manifest["candidate"]["scores"]["accuracy"]
        self.save()
        with self.assertRaises(EvaluationError):
            compare(self.file)


if __name__ == "__main__":
    unittest.main()
