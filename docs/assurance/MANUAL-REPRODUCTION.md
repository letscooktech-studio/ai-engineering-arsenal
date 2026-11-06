# Reproduce the P0 transport checks

Use a clean checkout of the commit under review, Python 3.11 or newer, and authorized disposable loopback targets. The test fixture opens ephemeral local ports and creates its own SQLite database. No credentials are needed.

## Windows PowerShell

```powershell
python -m venv .venv
. ./.venv/Scripts/Activate.ps1
python -m pip install -e .
$env:OUTCOMELAB_TEST_CLI = (Get-Command outcomelab).Source
python scripts/validate.py
python -m unittest discover -s tests -p test_http_response_integrity.py -v
python -m unittest discover -s tests -v
python -m risk_lab --json
```

## Linux shell

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
export OUTCOMELAB_TEST_CLI="$(command -v outcomelab)"
python scripts/validate.py
python -m unittest discover -s tests -p test_http_response_integrity.py -v
python -m unittest discover -s tests -v
python -m risk_lab --json
```

The raw TCP fixture puts these exact ASCII byte sequences between the normal Content-Length line and the blank separator. The body is still plain JSON.

| Case | Extra wire bytes | Required receipt |
| --- | --- | --- |
| T-001 / H02 | `Broken header\r\n` | Exit 2, `UNVERIFIED`, `malformed_response_headers` |
| T-002 / H03 | `Content-Encoding: gzip\r\n` | Exit 2, `UNVERIFIED`, `unsupported_content_encoding` |

Each fault is placed on the final readback of the same six-step v2 webhook contract with SQLite count and sum requested. The test separately reads one persisted row totaling 750 cents and requires that the invalid HTTP response still prevents PASS. A second pair injects each fault immediately after a committed POST and checks `effect_unknown: true`, one physical POST, and preservation of both baseline assertions. Valid unencoded and explicit identity controls pass with the same contract.

For the real reference endpoints, follow the [three-scenario quickstart](../START-HERE.md) and [SQLite witness walkthrough](../sqlite-effect-witness.md). Preserve the contract hash across variants and keep raw bodies, private database paths, and tokens out of reports. A fault on a write response requires reconciliation before any retry.

## Follow-on review order

1. Typed row witnesses. Approve exact columns, ownership and status comparisons. Prove a wrong single row fails even when count and sum match.
2. REST contract adaptability. Review the separate query/PATCH work and prove an ordinary route and generated-ID workflow against a disposable application.
3. Transaction and concurrency fixtures. Add cross-table rollback evidence, then a deterministic barrier that proves the intended race interleaving.
4. Async and PostgreSQL. Add bounded read-only polling, worker redelivery controls, and a separately tested read-only adapter against disposable PostgreSQL.
5. Agent skills and adoption. Ship skills with executable controls only. Seek one independently maintained backend integration before broad usability claims.
