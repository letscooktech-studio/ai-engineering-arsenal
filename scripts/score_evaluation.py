#!/usr/bin/env python3
"""Score Titan Evaluation Standard dimensions from JSON input."""
from __future__ import annotations

import json
import sys

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


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: score_evaluation.py scores.json", file=sys.stderr)
        return 2

    with open(sys.argv[1], "r", encoding="utf-8") as handle:
        scores = json.load(handle)

    missing = [key for key in WEIGHTS if key not in scores]
    if missing:
        print(f"Missing scores: {', '.join(missing)}", file=sys.stderr)
        return 1

    invalid = {
        key: value
        for key, value in scores.items()
        if key in WEIGHTS and (not isinstance(value, (int, float)) or value < 0 or value > 10)
    }
    if invalid:
        print(f"Scores must be numbers from 0 to 10: {invalid}", file=sys.stderr)
        return 1

    weighted = sum(scores[key] * weight for key, weight in WEIGHTS.items()) / 10
    result = {
        "weighted_total": round(weighted, 2),
        "max_score": 100,
        "scores": {key: scores[key] for key in WEIGHTS},
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
