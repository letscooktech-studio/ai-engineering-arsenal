"""Command line entry point: python -m risk_lab [--json] [--scenario NAME]."""
from __future__ import annotations

import argparse
import json
from .runner import CONTRACTS, run_all, run_scenario


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run controlled synthetic production-risk scenarios")
    parser.add_argument("--scenario", choices=sorted(CONTRACTS), help="Run one scenario rather than all")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable results")
    args = parser.parse_args(argv)
    results = [run_scenario(args.scenario)] if args.scenario else run_all()
    if args.json:
        print(json.dumps({"schema_version": 1, "results": [result.as_json() for result in results]}, indent=2, sort_keys=True))
    else:
        for item in results:
            print(f"{item.scenario_id}: {item.verdict} (broken={item.negative_control.status}, fixed={item.corrected.status})")
    return 0 if all(item.verdict == "DEMONSTRATED" for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
