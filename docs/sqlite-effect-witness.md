# Verify a backend effect with a read-only SQLite witness

OutcomeLab can verify how many rows a v2 workflow created for its generated run ID in an approved disposable SQLite database. This check is separate from the target service's HTTP readback.

## Reproduce an API that hides duplicate effects

With OutcomeLab installed, start the reference backend:

```sh
python -m risk_lab.demo_http --variant broken --mask-ledger --show-witness-path --port 8765
```

The server prints the absolute path to its temporary ledger database. Copy that path and substitute it for `ABSOLUTE_DB_PATH` in a second terminal:

```sh
outcomelab verify-http --contract examples/http/v2/webhook-idempotency.json --base-url http://127.0.0.1:8765 --allow-local-writes --sqlite-witness "ABSOLUTE_DB_PATH" ledger invoice_id 1 --allow-disposable-witness --json
```

Both webhook requests return 200. Every HTTP assertion passes because the masked GET reports one credit. The witness reads the actual run-scoped ledger and returns FAIL. Restart with `--variant fixed`, copy the new database path, and use the same contract. Both observation authorities pass. Stop the reference server to dispose of its temporary database.

## Apply to your own backend

- Approve the exact canonical local file, ordinary table, and visible text key column. The service must write the v2 `{run_id}` into that column. The witness checks zero matching rows before sending HTTP, then checks the requested count after HTTP observations pass.
- Pass the database definition through the CLI. The contract cannot request a database or supply SQL. The runner opens the file in read-only URI mode and counts exact text-key matches in a bounded read snapshot. Views, WAL databases, active sidecars, noncanonical paths, and files above 64 MiB are refused. A missing, locked, or replaced witness yields UNVERIFIED.
- Use a trusted local disk and disposable test data. Do not put a production or remote-mounted file behind the approved path. The runner cannot establish filesystem ownership or protect against an adversary controlling the application or filesystem. Keep the test API and database under the operator's control.
- Receipts include the witness authority, definition hash, and baseline/readback outcomes. They omit paths, SQL rows, and credentials. A failed HTTP check can skip the final witness because failure is already established. An interrupted mutation can have committed; reconcile state and let the operator manage cleanup.

## Verify the persisted integer amount

Add `--sqlite-sum amount_cents 750` to the witness command to require an exact sum of the selected column as well as the count. Use integer minor units for money. The column must be visible in the approved table. NULL, text, and real values make the sum unverified. The runner reads the bounded count and values from the same snapshot. Receipts report the comparison outcome and include the sum definition in the hash, without printing values.

To reproduce one persisted row with the wrong amount, start the demo with `--variant fixed --wrong-ledger-amount --show-witness-path --port 8765`. Use the printed path and the same v2 webhook contract with both witness flags. HTTP and count pass, but the integer sum fails. Restart without `--wrong-ledger-amount` to verify the corrected variant.

For a single expected row the sum checks that row's integer value. A sum across multiple rows does not establish each row's amount, ownership, or status. Non-SQLite data, cross-service consistency, and production behavior need separate evidence.

The witness requires SQLite 3.37 or newer for table inspection. References checked November 6, 2026. [SQLite URI modes](https://www.sqlite.org/uri.html) · [SQLite table inspection](https://www.sqlite.org/pragma.html#pragma_table_list) · [HTTP semantics](https://www.rfc-editor.org/rfc/rfc9110.html)
