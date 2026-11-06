"""Strict contract parsing and scalar-only v2 bindings."""
import json
import re
from hashlib import sha256

ID = r"[A-Za-z0-9_-]{1,64}"
PATH = r"/(?:[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*)?"
POINTER = r"(?:/[A-Za-z0-9_-]{1,64}){1,8}"
REFERENCE = r"\{([A-Za-z0-9_-]{1,64})\}"
SCALARS = (int, str, bool, type(None))


def require(condition):
    if not condition:
        raise ValueError("invalid contract or observation")


def pairs(items):
    result = dict(items)
    require(len(result) == len(items))
    return result


def bound_depth(value, remaining=32):
    require(remaining >= 0)
    if isinstance(value, dict):
        for child in value.values():
            bound_depth(child, remaining - 1)
    elif isinstance(value, list):
        for child in value:
            bound_depth(child, remaining - 1)


def decode(raw):
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                       parse_constant=lambda _: require(False), parse_float=lambda _: require(False))
    bound_depth(value)
    return value


def matches(pattern, value):
    return isinstance(value, str) and re.fullmatch(pattern, value) is not None


def resolve(value, variables):
    if isinstance(value, str) and ("{" in value or "}" in value):
        match = re.fullmatch(REFERENCE, value)
        require(match and match[1] in variables)
        return variables[match[1]]
    return value


def expand(step, variables):
    path = "/".join(resolve(segment, variables) for segment in step["path"].split("/"))
    require(matches(PATH, path) and len(path) <= 512)
    expanded = dict(step, path=path)
    if "json" in step:
        expanded["json"] = {key: resolve(value, variables) for key, value in step["json"].items()}
        require(len(json.dumps(expanded["json"])) <= 16384)
    return expanded


def at_pointer(document, pointer):
    for key in pointer[1:].split("/"):
        require(type(document) is dict and key in document)
        document = document[key]
    return document


def load_contract(path):
    with path.open("rb") as stream:
        raw = stream.read(65537)
    require(len(raw) <= 65536)
    contract = decode(raw)
    require(type(contract) is dict and set(contract) <= {"schema_version", "id", "description", "steps"})
    version = contract.get("schema_version")
    require(type(version) is int and version in (1, 2))
    require(matches(ID, contract.get("id")))
    require(isinstance(contract.get("description", ""), str))
    steps = contract.get("steps")
    require(type(steps) is list and 1 <= len(steps) <= 10)
    if version == 2:
        require(len(steps) >= 3 and all(type(step) is dict for step in steps))
        baseline = steps[0]
        require(baseline.get("method") == "GET" and type(baseline.get("path")) is str
                and "{run_id}" in baseline["path"].split("/"))
        require(baseline.get("expect_status") in (200, 404))
        require(("assert_json" in baseline) == (baseline["expect_status"] == 200))
        require(steps[-1].get("path") == baseline["path"] and steps[-1].get("expect_status") == 200)
        require(any(step.get("method") == "POST" for step in steps[1:-1]))
    prior = {}
    variables = {"run_id": "r" * 32}
    count = 0
    for step in steps:
        keys = {"id", "method", "path", "json", "expect_status", "assert_json"}
        if version == 2:
            keys.add("capture")
        require(type(step) is dict and set(step) <= keys)
        require(matches(ID, step.get("id")) and step["id"] not in prior)
        require(type(step.get("path")) is str)
        require(step.get("method") in ("GET", "POST"))
        status = step.get("expect_status")
        require(type(status) is int and 200 <= status <= 599 and not 300 <= status < 400)
        if step["method"] == "POST":
            require(type(step.get("json")) is dict and "assert_json" not in step)
            require(len(json.dumps(step["json"])) <= 16384)
        else:
            require("json" not in step)
        if version == 2:
            expand(step, variables)
        else:
            require(matches(PATH, step["path"]) and len(step["path"]) <= 512)
        if "assert_json" in step:
            checks = step["assert_json"]
            require(type(checks) is list and len(checks) > 0)
            count += len(checks)
            for check in checks:
                require(type(check) is dict and matches(POINTER if version == 2 else
                                                       r"(?:/[A-Za-z0-9_-]+){1,8}", check.get("pointer")))
                keys = set(check)
                if keys == {"pointer", "equals"}:
                    expected = check["equals"]
                    require(type(expected) in SCALARS)
                    if version == 2:
                        resolve(expected, variables)
                elif keys == {"pointer", "length"}:
                    require(type(check["length"]) is int and check["length"] >= 0)
                else:
                    require(version == 2 and keys in ({"pointer", "from", "delta"},
                                                      {"pointer", "from", "unchanged"}))
                    require(type(check["from"]) is str and check["from"] in prior)
                    source = prior[check["from"]]
                    require(source["method"] == "GET" and source["path"] == step["path"]
                            and source["expect_status"] == 200 and "assert_json" in source)
                    if "delta" in check:
                        require(type(check["delta"]) is int)
                    else:
                        require(check["unchanged"] is True)
        if "capture" in step:
            capture = step["capture"]
            require(type(capture) is dict and set(capture) == {"name", "pointer"})
            require(matches(ID, capture["name"]) and capture["name"] not in variables)
            require(matches(POINTER, capture["pointer"]) and 200 <= status < 300)
            variables[capture["name"]] = "x" * 64
        prior[step["id"]] = step
    require(1 <= count <= 20 and "assert_json" in steps[-1])
    if version == 2:
        require(any(step["method"] == "POST" and 200 <= step["expect_status"] < 300
                    and ("{run_id}" in step["path"].split("/")
                    or "{run_id}" in step["json"].values()) for step in steps))
    if version == 2 and baseline["expect_status"] == 200:
        require(any(check.get("from") == baseline["id"] and check.get("delta", 0) != 0
                    for check in steps[-1]["assert_json"]))
    return contract, sha256(raw).hexdigest(), count
