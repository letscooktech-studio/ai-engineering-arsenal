"""OutcomeLab command line."""
import argparse
import json
import shutil
import sys
from pathlib import Path

from .__main__ import main as legacy_demo
from .http_verify import verify
from .runner import CONTRACTS


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(3, "OutcomeLab: invalid command or arguments\n")


def main(argv=None):
    parser = Parser(prog="outcomelab", description="Verify business state on a disposable local service.")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("catalog", "doctor", "demo", "verify-http"):
        command = commands.add_parser(name)
        command.add_argument("--json", action="store_true")
        if name == "doctor":
            command.add_argument("--project", required=True, type=Path)
        if name == "verify-http":
            command.add_argument("--contract", required=True, type=Path)
            command.add_argument("--base-url", required=True)
            command.add_argument("--allow-local-writes", action="store_true")
    args = parser.parse_args(argv)
    code = 0
    if args.command == "demo":
        return legacy_demo(["--json"] if args.json else [])
    if args.command == "catalog":
        result = {"schema_version": 1, "contracts": [
            dict(spec, adapters=["synthetic-sqlite", "localhost-http"],
                 source=f"examples/http/{key}.json",
                 limitations="Sequential disposable fixture; no production or provider coverage")
            for key, spec in sorted(CONTRACTS.items())]}
    elif args.command == "doctor":
        if not args.project.is_dir():
            result, code = {"verdict": "INVALID", "error_class": "project_directory_unavailable"}, 3
        else:
            markers = ("pyproject.toml", "requirements.txt", "package.json", "build.gradle",
                       "build.gradle.kts", "pubspec.yaml", "src-tauri/tauri.conf.json")
            result = {"manifests": [name for name in markers if (args.project / name).is_file()],
                      "executables": {name: shutil.which(name) is not None
                                      for name in ("python", "node", "npm", "flutter", "xcodebuild", "cargo")},
                      "verdict": "UNVERIFIED", "scope": "File and executable presence only"}
    else:
        if args.allow_local_writes:
            print("Local POSTs may mutate service state. Use a disposable database.", file=sys.stderr)
        result, code = verify(args.contract, args.base_url, args.allow_local_writes)
    if args.json or args.command != "verify-http":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"{result['verdict']} ({result['executed_assertions']} assertions, "
              f"{result['skipped_assertions']} skipped)")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
