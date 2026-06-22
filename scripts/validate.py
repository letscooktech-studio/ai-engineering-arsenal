#!/usr/bin/env python3
"""Dependency-free structural checks for Titan OS skills and evaluation cases."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_SECTIONS = ("Workflow", "Output contract", "Quality gates")
REQUIRED_DOCS = (
    "OMEGA-AUDIT.md",
    "TITAN-CONSTITUTION.md",
    "OPERATING-MODEL.md",
    "EVALUATION-STANDARD.md",
    "RED-TEAM-FRAMEWORK.md",
    "MARKET-DOMINATION-RESEARCH.md",
    "BENCHMARK-LAB.md",
    "SELF-EVOLUTION.md",
)

def frontmatter(text: str, path: Path) -> list[str]:
    errors = []
    if not text.startswith("---\n"):
        return [f"{path}: missing YAML frontmatter"]
    end = text.find("\n---", 4)
    if end == -1:
        return [f"{path}: unterminated YAML frontmatter"]
    header = text[4:end]
    name = re.search(r"^name:\s*([a-z0-9-]+)\s*$", header, re.M)
    description = re.search(r"^description:\s*(.+)$", header, re.M)
    if not name or name.group(1) != path.parent.name:
        errors.append(f"{path}: name must match hyphen-case folder")
    if not description:
        errors.append(f"{path}: description is required")
    return errors

def main() -> int:
    errors = []
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8")
        errors += frontmatter(text, path)
        expected = REQUIRED_SECTIONS
        if path.parent.name == "production-ai-saas-builder":
            expected = ("Required intake", "Operating framework", "Output format", "Quality gates")
        for section in expected:
            if f"## {section}" not in text:
                errors.append(f"{path}: missing '{section}' section")
        if not (path.parent / "agents" / "openai.yaml").is_file():
            errors.append(f"{path}: missing agents/openai.yaml")
    for path in sorted((ROOT / "evals").glob("*/*/case.yaml")):
        text = path.read_text(encoding="utf-8")
        for field in ("skill:", "id:", "type:", "task:", "rubric:"):
            if field not in text:
                errors.append(f"{path}: missing {field}")
    for name in ("security-auditor", "startup-validator", "competitor-analyzer", "cto-operating-system"):
        for filename in ("evaluation-rubric.md", "failure-patterns.md"):
            path = ROOT / "benchmarks" / name / filename
            if not path.is_file():
                errors.append(f"{path}: missing tier-one credibility artifact")
    for filename in REQUIRED_DOCS:
        path = ROOT / "docs" / filename
        if not path.is_file():
            errors.append(f"{path}: missing Omega trust-system document")
    for filename in ("BENCHMARK.md", "RUBRIC.md", "CASE_STUDY.md", "FAILURE_PATTERNS.md", "EVALUATION.md", "EXAMPLES.md"):
        path = ROOT / "templates" / "skill-proof-pack" / filename
        if not path.is_file():
            errors.append(f"{path}: missing proof-pack template")
    if errors:
        print("Validation failed:", *errors, sep="\n- ")
        return 1
    print("Validated skills and evaluation manifests.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
