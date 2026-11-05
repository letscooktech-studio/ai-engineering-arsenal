#!/usr/bin/env python3
"""Strict, dependency-free scoring of independently assigned Arsenal rubric scores.

The script validates arithmetic and input shape. It does NOT establish that the
human evaluator was unbiased or that an AI response was factually correct.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys
from typing import Any

WEIGHTS = {
    "accuracy": 12,
    "evidence": 12,
    "verification": 12,
    "actionability": 10,
    "security": 10,
    "scalability": 8,
    "maintainability": 8,
    "completeness": 8,
    "risk_awareness": 8,
    "business_impact": 6,
    "user_value": 6,
}
CRITICAL_DIMENSIONS = ("accuracy", "evidence", "verification", "security")


class EvaluationError(ValueError):
    """Malformed or untrustworthy evaluation input."""


def reject_nonstandard_constant(value: str) -> None:
    raise EvaluationError(f"Non-finite JSON value is forbidden: {value}")


def no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise EvaluationError(f"Duplicate JSON field is forbidden: {key}")
        obj[key] = value
    return obj


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_nonstandard_constant, object_pairs_hook=no_duplicate_keys)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"Cannot load JSON file {path}: {exc}") from exc


def validate_scores(scores: Any) -> dict[str, float]:
    if not isinstance(scores, dict):
        raise EvaluationError("Scores must be a JSON object")
    missing = sorted(set(WEIGHTS) - set(scores))
    extra = sorted(set(scores) - set(WEIGHTS))
    if missing or extra:
        raise EvaluationError(f"Score dimensions mismatch: missing={missing}; unknown={extra}")
    clean: dict[str, float] = {}
    for key in WEIGHTS:
        value = scores[key]
        if type(value) not in (int, float) or not math.isfinite(value) or not 0 <= value <= 10:
            raise EvaluationError(f"{key}: expected finite number from 0 to 10 (booleans forbidden)")
        clean[key] = float(value)
    return clean


def score(scores: Any) -> dict[str, Any]:
    valid = validate_scores(scores)
    total = sum(valid[key] * weight for key, weight in WEIGHTS.items()) / 10
    return {"weighted_total": round(total, 2), "max_score": 100, "scores": valid}


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("Usage: python scripts/score_evaluation.py scores.json", file=sys.stderr)
        return 2
    try:
        result = score(load_json(Path(args[0])))
    except EvaluationError as exc:
        print(f"Invalid evaluation: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
