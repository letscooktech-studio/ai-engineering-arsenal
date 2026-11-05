#!/usr/bin/env python3
"""Compare independently rated AI outputs with hash-pinned raw artifacts.

No model calls, code execution or network requests. This tool checks input
consistency, not the accuracy of subjective human evaluator scores.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any

from score_evaluation import CRITICAL_DIMENSIONS, EvaluationError, load_json, score

SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
MAX_ARTIFACT_BYTES = 10 * 1024 * 1024


def strict_fields(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != expected:
        raise EvaluationError(f"{label} must contain exactly {sorted(expected)}")
    return value


def safe_artifact(manifest_dir: Path, rel: Any, sha256: Any) -> tuple[Path, int]:
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute():
        raise EvaluationError("Evidence artifact path must be relative")
    base = manifest_dir.resolve()
    file = (base / rel).resolve()
    if not file.is_relative_to(base) or not file.is_file():
        raise EvaluationError(f"Artifact must be a file inside manifest directory: {rel}")
    if not isinstance(sha256, str) or not SHA256_RE.fullmatch(sha256):
        raise EvaluationError("Artifact SHA-256 must be 64 lowercase hexadecimal characters")
    size = file.stat().st_size
    if size < 1 or size > MAX_ARTIFACT_BYTES:
        raise EvaluationError(f"Artifact must be 1..{MAX_ARTIFACT_BYTES} bytes: {rel}")
    digest = hashlib.sha256()
    with file.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    if digest.hexdigest() != sha256:
        raise EvaluationError(f"Artifact digest mismatch: {rel}")
    return file, size


def compare(manifest_file: Path) -> dict[str, Any]:
    data = strict_fields(load_json(manifest_file), {"schema_version", "case_id", "controls", "baseline", "candidate"}, "Manifest")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise EvaluationError("schema_version must equal 1")
    if not isinstance(data["case_id"], str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{0,79}", data["case_id"]):
        raise EvaluationError("case_id must be a simple identifier up to 80 characters")
    controls = strict_fields(data["controls"], {"model", "task_sha256", "tools", "token_budget", "evaluator"}, "Controls")
    for field in ("model", "evaluator"):
        if not isinstance(controls[field], str) or not controls[field].strip():
            raise EvaluationError(f"controls.{field} required")
    if not isinstance(controls["task_sha256"], str) or not SHA256_RE.fullmatch(controls["task_sha256"]):
        raise EvaluationError("controls.task_sha256 must be a lowercase SHA-256 hash")
    if not isinstance(controls["tools"], list) or not all(isinstance(t, str) and t.strip() for t in controls["tools"]):
        raise EvaluationError("controls.tools must be a list of tool identifiers")
    if type(controls["token_budget"]) is not int or not 1 <= controls["token_budget"] <= 1_000_000:
        raise EvaluationError("controls.token_budget must be an integer between 1 and 1000000")

    entries = {}
    for label in ("baseline", "candidate"):
        item = strict_fields(data[label], {"artifact", "artifact_sha256", "scores"}, label)
        _, size = safe_artifact(manifest_file.parent, item["artifact"], item["artifact_sha256"])
        rated = score(item["scores"])
        entries[label] = {
            "artifact": item["artifact"],
            "artifact_sha256": item["artifact_sha256"],
            "artifact_size": size,
            **rated,
        }
    before, after = entries["baseline"], entries["candidate"]
    gains = {key: round(after["scores"][key] - before["scores"][key], 3) for key in before["scores"]}
    regressions = [key for key in CRITICAL_DIMENSIONS if gains[key] < 0]
    delta = round(after["weighted_total"] - before["weighted_total"], 2)
    verdict = "CRITICAL_REGRESSION" if regressions else "IMPROVED" if delta > 0 else "REGRESSED" if delta < 0 else "TIE"
    return {
        "schema_version": 1,
        "case_id": data["case_id"],
        "verdict": verdict,
        "score_delta": delta,
        "critical_regressions": regressions,
        "dimension_deltas": gains,
        "controls": controls,
        "baseline": entries["baseline"],
        "candidate": entries["candidate"],
        "limitations": [
            "Scores are human-provided judgments, not verified facts about output quality.",
            "The manifest records controls but cannot prove both runs used identical settings.",
            "Hashes establish local artifact consistency, not trusted provenance or independent scoring.",
            "Reviewers must inspect the referenced raw outputs; they are not embedded in this report.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("Usage: python scripts/compare_evaluations.py manifest.json", file=sys.stderr)
        return 2
    try:
        result = compare(Path(args[0]))
    except (EvaluationError, OSError) as exc:
        print(f"Invalid benchmark: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
