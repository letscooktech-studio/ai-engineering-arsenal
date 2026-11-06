# Start with OutcomeLab

Use Python 3.11 or newer. In a virtual environment, run from the checkout:

```sh
python -m pip install -e .
outcomelab catalog
outcomelab validate --contract examples/http/v2/webhook-idempotency.json
outcomelab doctor --project .
outcomelab demo
```

Installation uses setuptools as its build backend. Runtime uses the Python standard library. The demo command labels both bundled SQLite negative controls `DEMONSTRATED`.

## Run the same contract against two real HTTP endpoints

In terminal 1, start a disposable reference service:

```sh
python -m risk_lab.demo_http --variant broken --port 8765
```

In terminal 2, from the checkout, run:

```sh
outcomelab verify-http --contract examples/http/v2/webhook-idempotency.json --base-url http://127.0.0.1:8765 --allow-local-writes
```

Expected stdout is `FAIL (7 assertions, 0 skipped)`. The two identical deliveries returned 200, but readback shows two ledger entries and 1500 credited cents. The conflicting payload is separately rejected. Stop the server with Ctrl+C. Start it again with `--variant fixed` and repeat the exact verification command. Expected stdout is `PASS (7 assertions, 0 skipped)`. The new database records one row and 750 cents.

V2 allocates a new identity per run, so you can repeat the contract against the same disposable service. To check invoice persistence, use `examples/http/v2/invoice-persistence.json`. Broken acknowledges the write but returns 404 on a fresh-connection GET. Fixed returns the persisted invoice. That check covers a fresh SQLite connection.

## Check inventory after a rejected reservation

Run the same command with `examples/http/v2/inventory-rejection.json`. The first reservation reduces available stock from five to two. Both variants reject a second reservation with HTTP 409. Broken still subtracts three units, so the final readback fails. Fixed leaves two units available.

## Bring your own service

1. Start your authorized API against a disposable database with external integrations disabled. Copy the invoice example to a new file and map its GET and POST routes to your test service.
2. Keep `{run_id}` in the resource path and creation payload. Confirm GET reports absence before the write, then assert the exact ID and amount returned by GET afterward. Have the operator review those expectations.
3. Run `outcomelab validate --contract your-contract.json`. This reads the contract without running requests or subprocesses.
4. Run `outcomelab verify-http --contract your-contract.json --base-url http://127.0.0.1:8765 --allow-local-writes --json`. For an authenticated test API, inject a local test token into `OUTCOMELAB_BEARER_TOKEN` and add `--bearer-token`.
5. Compare the baseline and readback outcomes in the receipt. Discard or reset the disposable database through your service's own tooling. OutcomeLab does not clean up your application state.

See the [contract and safety rules](PRODUCTION-RISK-LAB.md), [contributing guide](../CONTRIBUTING.md), and [issue tracker](https://github.com/letscooktech-studio/outcomelab/issues).

See [API regression testing in CI](api-regression-testing-in-ci.md) for integrating a disposable service into your application's test pipeline.
