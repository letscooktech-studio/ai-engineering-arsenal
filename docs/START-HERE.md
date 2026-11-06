# Start with OutcomeLab

Use Python 3.11 or newer. In a virtual environment, run from the checkout:

```sh
python -m pip install -e .
outcomelab catalog
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
outcomelab verify-http --contract examples/http/webhook-idempotency.json --base-url http://127.0.0.1:8765 --allow-local-writes
```

Expected stdout is `FAIL (2 assertions, 0 skipped)`. Both POSTs returned 200, but the GET reads two ledger entries and 1500 credited cents. Stop the server with Ctrl+C. Start it again with `--variant fixed` and repeat the exact verification command. Expected stdout is `PASS (2 assertions, 0 skipped)`. The new database records one row and 750 cents.

Restart the disposable server for each run. To check invoice persistence, use `examples/http/invoice-persistence.json`. Broken acknowledges the write but returns 404 on a fresh-connection GET. Fixed returns the persisted invoice. That check covers a fresh SQLite connection.

## Bring your own service

Copy an example and set the endpoints, test payload and expected business state to match your authorized local dev API. Use a fresh test database and dummy identifiers. The write flag permits real state changes on the selected service. Even GET can mutate state if the service implements it that way. Use `--json` for a scoped receipt.

See the [contract and safety rules](PRODUCTION-RISK-LAB.md), [contributing guide](../CONTRIBUTING.md), and [issue tracker](https://github.com/letscooktech-studio/ai-engineering-arsenal/issues).
