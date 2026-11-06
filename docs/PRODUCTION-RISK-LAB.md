# OutcomeLab verification

Use the [quickstart](START-HERE.md) for an executable HTTP example. See the [source registry](SOURCE-REGISTRY.md) for platform references and tool boundaries. The legacy SQLite CLI is available separately.

## HTTP contract v1

The JSON object has `schema_version: 1`, `id`, optional `description`, and `steps`. Each step has a unique `id`, `method`, `path`, and integer `expect_status`. POST requires a static JSON object in `json`. GET can have an `assert_json` array and the final step must be a GET with assertions. The runner supports exact typed scalar equality (`equals`) and list length (`length`). Pointers are slash-separated object keys using ASCII letters, digits, underscores and hyphens. Version 1 supports integer JSON numbers.

Use a literal `http://127.0.0.1:PORT` with port 1024–65535. Paths allow slash-separated ASCII letters, digits, underscores and hyphens. The runner sends requests directly to loopback and refuses redirects. V1 manifests cannot set headers, execute code, or expand variables. Limits include 64 KiB contracts, 16 KiB POST payloads, 256 KiB response bodies, 10 steps, 20 assertions, and up to five seconds per request.

| Exit | Result | Meaning |
| --- | --- | --- |
| 0 | PASS | All required observations matched |
| 1 | FAIL | A status or observed business value contradicted the contract |
| 2 | UNVERIFIED | The runner could not complete an observation |
| 3 | INVALID | The contract, target or permission was invalid |

## HTTP contract v2

Start with the [stateful examples](../examples/http/v2/). The [unknown binding example](../examples/http/v2/invalid/unknown-resource.json) fails offline validation. V2 retains v1 field names and adds the following rules:

| Part | Rule |
| --- | --- |
| Baseline | First step is a GET whose path includes a whole `{run_id}` segment. Expect 404 for absence, or 200 with assertions establishing initial state. A mismatch stops the run as UNVERIFIED before any mutation. |
| Action | At least one POST must expect 2xx and use `{run_id}` in a path segment or top-level body value. Include one or more actions between the baseline and the last GET. |
| Readback | Last step is a GET using the same path template as the baseline, expects 200, and has JSON assertions. A 200 baseline requires at least one nonzero integer delta from it on the final step. |
| Binding | `{run_id}` expands to a new 32-character UUID4 hex value. A step expecting 2xx can declare one `"capture": {"name": "created", "pointer": "/id"}`. Names are unique and case-sensitive. Captured values must be strings matching `[A-Za-z0-9_-]{1,64}`. Captures become available on later steps. |
| Placement | Use `{name}` as a whole path segment, whole top-level POST JSON value, or whole string in an `equals` assertion. Path segments and body values are checked again after expansion. Nested JSON is literal. There is no expression evaluation or environment interpolation. |
| Relative assertions | `{"pointer": "/amount_cents", "from": "before", "delta": 750}` checks exact integer subtraction. `{"pointer": "/state", "from": "once", "unchanged": true}` compares typed scalars. The source must be an earlier 200 GET with assertions on the identical path template. Missing or mistyped observations are UNVERIFIED. |

IDs are 1–64 ASCII letters, digits, underscores or hyphens. V2 pointers consist of up to eight slash-separated ID-shaped keys. JSON has a nesting limit of 32 and accepts integer numbers only. V2 requires Content-Length for nonempty response bodies and rejects transfer encodings. Ambiguous framing and redirects are rejected. There are at most 10 attempts of up to 5 seconds each, with no POST retry. A timed-out write may already have changed state.

### HTTP response integrity

OutcomeLab rejects parser-reported header defects, malformed field names, folded values, and disallowed control characters. It accepts an absent Content-Encoding or one case-insensitive identity value. Gzip, other encodings, and repeated or stacked codings yield UNVERIFIED when the response is needed for a verdict. The runner does not decompress bodies. The receipt identifies these cases as `malformed_response_headers` or `unsupported_content_encoding` without including response fields. A rejected POST response may follow a committed write. Check `effect_unknown` before taking another action.

### Local authentication and evidence

Pass `--bearer-token` to read `OUTCOMELAB_BEARER_TOKEN` from the process environment. It supplies only the Authorization bearer header. Empty, oversized, or invalid values, including line breaks, are rejected before contacting the target. Use a short-lived credential for the disposable service. Local HTTP is plaintext and the receiving server controls its own logging. See [RFC 6750](https://www.rfc-editor.org/rfc/rfc6750).

Receipts label all observations `target-http-api` and approval `operator-declared`. They include a run ID, contract hash and version, CLI and runtime versions, phase/status records, and assertion outcomes without raw bodies or comparison values. An attempted step may have changed state even when no complete response was observed. V2 does not invoke Git. Optional legacy v1 Git metadata describes the CLI working directory. The receipt cannot attest the service source, build, or database contents.

### Optional SQLite witness and uncertain writes

See the [SQLite witness guide](sqlite-effect-witness.md) for operator consent, file scope, and the deceptive-API demonstration. When enabled, a successful HTTP run requires the final witness to match too. A definitive failed assertion takes precedence over a later incomplete observation, and the receipt keeps the incomplete diagnostic. A baseline mismatch blocks writes and yields UNVERIFIED. An interrupted POST may have committed. The receipt flags `effect_unknown` when delivery or the mutation result is uncertain.

### Threat model

Review the manifest and expected state before execution. POST can leave changes behind even if a later check fails. The verifier uses no proxy, follows no redirects and emits comparison outcomes rather than response payloads or assertion values. Use dummy names in contracts because the receipt includes contract and step IDs and pointers. A contract hash identifies the exact bytes, and legacy Git fields refer to the CLI checkout. A local service can proxy requests elsewhere or return misleading state. Local results cover the declared observations under the supplied environment and input only.

## Legacy SQLite demonstrations

## Quick start

Requirements: Python 3.11+; no database server or external package.

From the repository root:

```sh
python -m risk_lab
python -m risk_lab --json
python -m risk_lab --scenario webhook-idempotency
python -m unittest discover -s tests -v
python scripts/validate.py
```

Expected demonstration status for both scenarios: `DEMONSTRATED (broken=FAIL, fixed=PASS)`. A successful process exit means **only** that these intentionally selected synthetic negative controls behaved as defined. It is not evidence of the security or correctness of a real payment system.

## Two scenarios and their observable invariants

| Scenario | Broken reference | Corrected reference | Acceptance oracle |
| --- | --- | --- | --- |
| `webhook-idempotency` | Applying the same synthetic event twice inserts two ledger entries and credits the invoice twice | Event ID is registered in the same SQLite transaction as the invoice credit/ledger insert; conflicting payloads are rejected | Reopen SQLite DB: one ledger effect, exactly 750 cents credited, second identical delivery labeled `duplicate` |
| `invoice-persistence` | Returns success but rolls back the database transaction | Commits the new row | Open a new DB connection: exact invoice ID, customer and amount remain stored |

Synthetic SQLite fixtures are in [`risk_lab/fixtures.py`](../risk_lab/fixtures.py). The **same acceptance invariant** runs for broken and corrected variants in [`risk_lab/runner.py`](../risk_lab/runner.py). Actual measured state, negative-control status, reference-source digest, and contract digest are included in JSON output.

The runner creates isolated temporary SQLite databases, executes only the built-in repo-owned fixtures from an explicit allowlist, and deletes temporary files on completion. It makes **no network calls**, reads no user application files, and imports no arbitrary modules from supplied paths. It does not need or consume Codex, Claude, or other API credits.

## Meaning of statuses

- `DEMONSTRATED`: broken fixture produced a failing outcome and corrected fixture passed the same oracle.
- `REGRESSION`: the expected negative-versus-positive behavior was not demonstrated despite completed checks.
- `UNVERIFIED`: a check was unavailable, produced an unexpected exception, or could not reach a valid observable outcome.

For independent real-product verification, the oracle must be approved outside the candidate agent's editable worktree, and a trusted runner must execute it against the exact candidate revision. The built-in contract and source hashes are **identifiers**, not tamper-resistant proofs; both may be updated by a repository author. The example does not independently establish requirements coverage.

## Non-goals and safety limitations

- The webhook fixture is not production-grade. No cryptographic webhook signature verification, provider authentication, event ordering, settlement reconciliation, multi-process contention, retries, network failure, currency conversion, or database portability is tested.
- The persistence fixture reopens a DB connection; it does not restart a full application or test a UI.
- This is not an independent measurement of how well Codex or Claude performs; no model baseline or agent run is bundled.
- The package is intended for a trusted repository checkout, not a sandbox for executing arbitrary untrusted third-party test code.

## Contribute a scenario

A contribution should contain a real user-visible invariant, a minimal reproducible broken example, a corrected example, shared tests, bounded/isolated execution, and explicit failure modes. Require the broken implementation to **fail** the acceptance oracle. Require the corrected implementation to **pass** it. Tests must prove both controls are actually exercised; no unconditional PASS and no treating a skipped check as success. Link to primary external evidence where the failure is based on a reported incident, but sanitize all credentials/customer data.

Open an issue using [the reproducible scenario proposal template](../.github/ISSUE_TEMPLATE/reproducible-scenario.yml) before introducing a broad new runtime or integration.
