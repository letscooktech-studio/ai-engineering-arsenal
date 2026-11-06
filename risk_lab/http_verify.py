"""Validate a bounded contract before making direct loopback requests."""
import http.client
import json
import re
import socket
import subprocess
import sys
from datetime import datetime, timezone
from hashlib import sha256
from threading import Event, Timer

LIMIT = 256 * 1024
ID = r"[A-Za-z0-9_-]{1,64}"
PATH = r"/(?:[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*)?"
POINTER = r"(?:/[A-Za-z0-9_-]+){1,8}"


def require(condition):
    if not condition:
        raise ValueError("invalid contract or target")


def pairs(items):
    result = dict(items)
    require(len(result) == len(items))
    return result


def decode(raw):
    return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                      parse_constant=lambda _: require(False), parse_float=lambda _: require(False))


def matches(pattern, value):
    return isinstance(value, str) and re.fullmatch(pattern, value) is not None


def load_contract(path):
    with path.open("rb") as stream:
        raw = stream.read(65537)
    require(len(raw) <= 65536)
    contract = decode(raw)
    require(type(contract) is dict and set(contract) <= {"schema_version", "id", "description", "steps"})
    require(type(contract.get("schema_version")) is int and contract["schema_version"] == 1)
    require(matches(ID, contract.get("id")))
    require(isinstance(contract.get("description", ""), str))
    steps = contract.get("steps")
    require(type(steps) is list and 1 <= len(steps) <= 10)
    ids = set()
    count = 0
    for step in steps:
        require(type(step) is dict and set(step) <= {"id", "method", "path", "json", "expect_status", "assert_json"})
        require(matches(ID, step.get("id")) and step["id"] not in ids)
        ids.add(step["id"])
        require(matches(PATH, step.get("path")) and len(step["path"]) <= 512)
        require(step.get("method") in ("GET", "POST"))
        require(type(step.get("expect_status")) is int and 200 <= step["expect_status"] <= 599
                and not 300 <= step["expect_status"] < 400)
        if step["method"] == "POST":
            require(type(step.get("json")) is dict and "assert_json" not in step)
            require(len(json.dumps(step["json"])) <= 16384)
        else:
            require("json" not in step)
        if "assert_json" in step:
            checks = step["assert_json"]
            require(type(checks) is list and len(checks) > 0)
            count += len(checks)
            for check in checks:
                require(type(check) is dict and matches(POINTER, check.get("pointer")))
                require((set(check) == {"pointer", "equals"} and
                         type(check["equals"]) in (int, str, bool, type(None))) or
                        (set(check) == {"pointer", "length"} and
                         type(check["length"]) is int and check["length"] >= 0))
    require(1 <= count <= 20 and "assert_json" in steps[-1])
    return contract, sha256(raw).hexdigest(), count


def request(port, step):
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
            connection.auto_open = False
            connection.request(step["method"], step["path"], payload, headers)
            with connection.getresponse() as response:
                raw = response.read(LIMIT + 1)
                if expired.is_set() or len(raw) > LIMIT or response.length not in (0, None):
                    raise ValueError("response size or framing")
                return response.status, response.headers.get_content_type(), raw
        finally:
            deadline.cancel()
            deadline.join()
    finally:
        connection.close()


def git(*args):
    try:
        return subprocess.run(["git", *args], capture_output=True, check=True,
                              text=True, timeout=2).stdout.strip()
    except (OSError, subprocess.SubprocessError, UnicodeError):
        return None


def verify(path, base_url, allow_writes):
    now = lambda: datetime.now(timezone.utc).isoformat()
    receipt = dict(schema_version=1, contract_id=None, contract_sha256=None,
                   started_at=now(), target_class="local-loopback", runtime_version=sys.version.split()[0],
                   provenance="local-user-run", assertion_results=[], executed_steps=0, error_class=None,
                   limitations=["One local contract; target code and state are not attested.",
                                "Contract hash identifies bytes, not approval or tamper resistance.",
                                "Git metadata refers to the CLI working directory."])
    status = git("--no-optional-locks", "status", "--porcelain")
    receipt.update(git_head=git("rev-parse", "--verify", "HEAD"),
                   working_tree_dirty=None if status is None else bool(status))
    checks = receipt["assertion_results"]
    total = None
    try:
        contract, digest, total = load_contract(path)
        receipt.update(contract_id=contract["id"], contract_sha256=digest)
        target = re.fullmatch(r"http://127\.0\.0\.1:([1-9][0-9]{3,4})", base_url)
        require(target and 1024 <= int(target[1]) <= 65535)
        require(allow_writes or all(step["method"] == "GET" for step in contract["steps"]))
    except (OSError, ValueError, RecursionError):
        verdict, code = "INVALID", 3
        receipt["error_class"] = "input_or_write_permission"
    else:
        verdict, code = "PASS", 0
        try:
            for step in contract["steps"]:
                status, media, raw = request(int(target[1]), step)
                receipt["executed_steps"] += 1
                if 300 <= status < 400:
                    raise ValueError("redirect")
                if status != step["expect_status"]:
                    receipt["status_mismatch"] = dict(step=step["id"], expected=step["expect_status"], observed=status)
                    verdict, code = "FAIL", 1
                    break
                if "assert_json" not in step:
                    continue
                require(media == "application/json")
                document = decode(raw)
                for check in step["assert_json"]:
                    observed = document
                    for key in check["pointer"][1:].split("/"):
                        require(type(observed) is dict and key in observed)
                        observed = observed[key]
                    if "length" in check:
                        require(type(observed) is list)
                        observed = len(observed)
                        expected = check["length"]
                    else:
                        expected = check["equals"]
                    match = type(observed) is type(expected) and observed == expected
                    checks.append(dict(step=step["id"], pointer=check["pointer"],
                                       status="PASS" if match else "FAIL",
                                       comparison="list length" if "length" in check else "exact equality"))
                    if not match:
                        verdict, code = "FAIL", 1
        except (OSError, http.client.HTTPException, ValueError, RecursionError):
            if verdict != "FAIL":
                verdict, code = "UNVERIFIED", 2
            receipt["error_class"] = "incomplete_observation"
    receipt.update(verdict=verdict, finished_at=now(), executed_assertions=len(checks),
                   skipped_assertions=None if total is None else total - len(checks))
    return receipt, code
