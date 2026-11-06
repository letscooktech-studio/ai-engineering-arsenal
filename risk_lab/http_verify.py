"""Validate a bounded contract before making direct loopback requests."""
import http.client
import json
import os
import re
import socket
import sqlite3
import subprocess
import sys
import platform
from datetime import datetime, timezone
from uuid import uuid4
from threading import Event, Timer

from . import __version__
from .contracts import SCALARS, at_pointer, decode, expand, load_contract, matches, require, resolve, ID

from . import sqlite_witness

LIMIT = 256 * 1024
AUTH_ENV = "OUTCOMELAB_BEARER_TOKEN"


def request(port, step, token=None):
    # Direct HTTPConnection has no proxy configuration or redirect handling.
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
    try:
        peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.sock = peer
        peer.settimeout(2)
        peer.connect(("127.0.0.1", port))
        expired = Event()

        def interrupt():
            expired.set()
            try:
                peer.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

        deadline = Timer(3, interrupt)
        deadline.start()
        try:
            payload = json.dumps(step["json"]) if "json" in step else None
            headers = {"Content-Type": "application/json"} if payload is not None else {}
            if token is not None:
                headers["Authorization"] = f"Bearer {token}"
            connection.auto_open = False
            connection.request(step["method"], step["path"], payload, headers)
            with connection.getresponse() as response:
                lengths = response.headers.get_all("Content-Length", [])
                encodings = response.headers.get_all("Transfer-Encoding", [])
                require(len(lengths) <= 1 and len(encodings) <= 1 and not (lengths and encodings))
                if lengths:
                    require(re.fullmatch(r"[0-9]{1,10}", lengths[0]) and int(lengths[0]) <= LIMIT)
                if encodings:
                    require(response.chunked and step.get("strict_framing") is not True)
                raw = response.read(LIMIT + 1)
                if expired.is_set() or len(raw) > LIMIT or response.length not in (0, None):
                    raise ValueError("response size or framing")
                require(not (step.get("strict_framing") and raw and not lengths))
                return response.status, response.headers.get_content_type(), raw
        finally:
            deadline.cancel()
            deadline.join()
    finally:
        connection.close()


def git(*args):
    try:
        return subprocess.run(["git", "-c", "core.fsmonitor=false", *args], capture_output=True, check=True,
                              text=True, timeout=2,
                              env={key: value for key, value in os.environ.items() if key != AUTH_ENV}).stdout.strip()
    except (OSError, subprocess.SubprocessError, UnicodeError):
        return None


def verify(path, base_url, allow_writes, use_bearer=False, witness_arguments=None, allow_witness=False, sum_arguments=None):
    now = lambda: datetime.now(timezone.utc).isoformat()
    run_id = uuid4().hex
    receipt = dict(schema_version=1, contract_id=None, contract_sha256=None, run_id=run_id,
                   cli_version=__version__, environment=platform.system(),
                   observation_authority="target-http-api", contract_approval="operator-declared",
                   contract_schema_version=None, step_results=[],
                   attempted_steps=0, skipped_steps=None, git_head=None, working_tree_dirty=None,
                   started_at=now(), target_class="local-loopback", runtime_version=sys.version.split()[0],
                   provenance="local-user-run", assertion_results=[], executed_steps=0, error_class=None,
                   limitations=["One local contract; target code and state are not attested.",
                                "Contract hash identifies bytes, not approval or tamper resistance.",
                                "Optional v1 Git metadata describes the CLI working directory."])
    checks = receipt["assertion_results"]
    total = None
    witness = None
    amount = None
    try:
        contract, digest, total = load_contract(path)
        receipt.update(contract_id=contract["id"], contract_sha256=digest,
                       contract_schema_version=contract["schema_version"])
        steps = contract["steps"]
        receipt["skipped_steps"] = len(steps)
        target = re.fullmatch(r"http://127\.0\.0\.1:([1-9][0-9]{3,4})", base_url)
        require(target and 1024 <= int(target[1]) <= 65535)
        token = os.environ.get(AUTH_ENV) if use_bearer else None
        require(not use_bearer or matches(r"[A-Za-z0-9._~+/-]{1,2048}={0,2}", token))
        require(bool(witness_arguments) == allow_witness)
        require(not sum_arguments or witness_arguments)
        if witness_arguments:
            require(contract["schema_version"] == 2)
            witness = sqlite_witness.definition(witness_arguments)
            if sum_arguments:
                amount = sqlite_witness.sum_definition(sum_arguments)
            receipt["sqlite_witness"] = dict(authority="read-only-local-sqlite",
                                             definition_sha256=sqlite_witness.fingerprint(witness, amount),
                                             baseline="SKIPPED", readback="SKIPPED")
            if amount:
                receipt["sqlite_witness"]["integer_sum"] = "SKIPPED"
        require(allow_writes or all(step["method"] == "GET" for step in contract["steps"]))
    except (OSError, ValueError, RecursionError):
        verdict, code = "INVALID", 3
        receipt["error_class"] = "input_or_write_permission"
    else:
        verdict, code = "PASS", 0
        variables = {"run_id": run_id}
        documents = {}
        stateful = contract["schema_version"] == 2
        if not stateful:
            status = git("--no-optional-locks", "status", "--porcelain")
            receipt.update(git_head=git("rev-parse", "--verify", "HEAD"),
                           working_tree_dirty=None if status is None else bool(status))
        effect_unknown = False
        write_in_flight = False
        checking_witness = witness is not None
        try:
            if witness:
                witness_identity, observed = sqlite_witness.count_rows(witness, run_id, amount=amount)
                count = observed[0] if amount else observed
                receipt["sqlite_witness"]["baseline"] = "PASS" if count == 0 else "FAIL"
                require(count == 0)
            checking_witness = False
            for index, step in enumerate(steps):
                phase = "baseline" if stateful and index == 0 else "action" if step["method"] == "POST" else "readback"
                outgoing = expand(step, variables) if stateful else step
                receipt["attempted_steps"] += 1
                write_in_flight = step["method"] == "POST"
                status, media, raw = request(int(target[1]), dict(outgoing, strict_framing=stateful), token)
                effect_unknown |= write_in_flight and (300 <= status < 400 or status in (408, 429) or status >= 500)
                write_in_flight = False
                receipt["executed_steps"] += 1
                receipt["step_results"].append(dict(step=step["id"], phase=phase,
                                                    expected_status=step["expect_status"], observed_status=status))
                if 300 <= status < 400:
                    raise ValueError("redirect")
                if status != step["expect_status"]:
                    if stateful and (phase == "baseline" or status in (401, 403, 408, 429) or status >= 500):
                        raise ValueError("baseline or service unavailable")
                    receipt["status_mismatch"] = dict(step=step["id"], expected=step["expect_status"], observed=status)
                    verdict, code = "FAIL", 1
                    break
                if "assert_json" not in step and "capture" not in step:
                    continue
                require(media == "application/json")
                document = decode(raw)
                if "assert_json" in step:
                    documents[step["id"]] = document
                for check in step.get("assert_json", []):
                    observed = at_pointer(document, check["pointer"])
                    if "length" in check:
                        require(type(observed) is list)
                        observed, expected, comparison = len(observed), check["length"], "list length"
                    elif "from" in check:
                        before = at_pointer(documents[check["from"]], check["pointer"])
                        if "delta" in check:
                            require(type(before) is int and type(observed) is int)
                            observed, expected, comparison = observed - before, check["delta"], "integer delta"
                        else:
                            require(type(before) in SCALARS and type(observed) in SCALARS)
                            expected, comparison = before, "unchanged scalar"
                    else:
                        expected = resolve(check["equals"], variables) if stateful else check["equals"]
                        comparison = "exact equality"
                    match = type(observed) is type(expected) and observed == expected
                    checks.append(dict(step=step["id"], pointer=check["pointer"], phase=phase,
                                       status="PASS" if match else "FAIL", comparison=comparison))
                    if not match:
                        if phase == "baseline":
                            raise ValueError("baseline isolation unavailable")
                        verdict, code = "FAIL", 1
                if "capture" in step:
                    capture = step["capture"]
                    captured = at_pointer(document, capture["pointer"])
                    require(matches(ID, captured) and captured != token)
                    variables[capture["name"]] = captured
            if witness and code == 0:
                checking_witness = True
                _, observed = sqlite_witness.count_rows(witness, run_id, witness_identity, amount=amount)
                count = observed[0] if amount else observed
                receipt["sqlite_witness"]["readback"] = "PASS" if count == witness[-1] else "FAIL"
                if count != witness[-1]:
                    verdict, code = "FAIL", 1
                elif amount:
                    if observed[1] is None:
                        raise ValueError("integer witness unavailable")
                    matched = observed[1] == amount[1]
                    receipt["sqlite_witness"]["integer_sum"] = "PASS" if matched else "FAIL"
                    if not matched:
                        verdict, code = "FAIL", 1
            receipt["skipped_steps"] = len(steps) - receipt["attempted_steps"]
        except (OSError, http.client.HTTPException, sqlite3.Error, ValueError, RecursionError):
            if verdict != "FAIL":
                verdict, code = "UNVERIFIED", 2
            receipt["error_class"] = "witness_unavailable" if checking_witness else "incomplete_observation"
            if checking_witness:
                phase = "baseline" if receipt["attempted_steps"] == 0 else "readback"
                if receipt["sqlite_witness"][phase] == "SKIPPED":
                    receipt["sqlite_witness"][phase] = "UNVERIFIED"
                if amount and phase == "readback":
                    receipt["sqlite_witness"]["integer_sum"] = "UNVERIFIED"
        receipt["effect_unknown"] = effect_unknown or write_in_flight
        receipt["cleanup"] = "operator-managed"
        if receipt["error_class"]:
            receipt["skipped_steps"] = len(steps) - receipt["attempted_steps"]
    receipt.update(verdict=verdict, finished_at=now(), executed_assertions=len(checks),
                   skipped_assertions=None if total is None else total - len(checks))
    return receipt, code
