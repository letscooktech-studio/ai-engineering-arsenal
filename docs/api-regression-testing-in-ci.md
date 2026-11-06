# Run local API regression tests in CI with OutcomeLab

OutcomeLab tests an HTTP contract against a service on the same machine or in the same network namespace. It can check a Node.js, Python, Go, Java, or .NET API that exposes the required routes. Your API's language and database can differ from the bundled Python and SQLite examples. The runner needs Python 3.11 or newer.

## Choose a business invariant

| API | Before | Action | Verify by GET |
| --- | --- | --- | --- |
| Billing | Read the run-scoped ledger | Deliver the same event twice | Exactly one credit was recorded |
| Invoicing | Confirm a new invoice is absent | Create the invoice | The invoice and amount are visible |
| Commerce | Read available stock | Reserve stock, then request more than is available | The rejected reservation left stock unchanged |

The [inventory contract](../examples/http/v2/inventory-rejection.json) checks a common failure that status-only tests miss. Both reference variants return HTTP 409 for the rejected reservation. Broken subtracts stock anyway. Fixed preserves the previous quantity.

## Bring your application to the runner

1. Copy a v2 [example contract](../examples/http/v2/) into your application repository. Replace the fixture routes and expectations with your approved business invariant. Keep the same run-specific resource in the baseline and final read.
2. In CI, start your application with its normal test command and a disposable database. Wait for the app's readiness probe. If it runs in a container, publish its test port on `127.0.0.1` only or run OutcomeLab in the same network namespace. Disable outbound production integrations in the application configuration.
3. Install OutcomeLab from a reviewed commit or release. Validate the contract before starting any verification requests.
4. Run the approved contract, preserve the exit status, and tear down the service and database using your existing test lifecycle.

With the installed CLI and a ready test API:

```sh
outcomelab validate --contract tests/contracts/reservation.json
outcomelab verify-http --contract tests/contracts/reservation.json --base-url http://127.0.0.1:8765 --allow-local-writes --json > outcome.json
```

An authenticated test API can use a short-lived local token from `OUTCOMELAB_BEARER_TOKEN` with `--bearer-token`. Keep privileged credentials out of untrusted pull-request workflows. Inspect receipt identifiers before publishing artifacts. Treat exits 1, 2, and 3 as unsuccessful checks, and preserve the distinction between a contradicted expectation, missing evidence, and invalid configuration.

See the repository's [tested Windows and Linux workflow](../.github/workflows/validate.yml) and the [contract reference](PRODUCTION-RISK-LAB.md). These checks exercise sequential HTTP behavior. Race conditions and independently verified database state require separate tests.
