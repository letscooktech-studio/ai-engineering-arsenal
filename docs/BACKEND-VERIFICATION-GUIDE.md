# Backend developer guide

Use OutcomeLab when a successful request can leave the wrong business state. Start with one operation, one disposable test environment, and one failure that an operator can reproduce.

## 1. Write the acceptance rule

Record these details before editing the implementation or contract:

| Item | Webhook example |
| --- | --- |
| Logical operation | Credit an invoice for one delivery ID |
| Isolation | Disposable database and a fresh run ID |
| Baseline | Zero credits and zero ledger rows for this run |
| Approved actions | Send the same delivery twice, then send a conflicting amount |
| Required outcome | One row and 750 credited cents after both deliveries |
| Forbidden effect | A duplicate credit or any change after rejecting the conflicting delivery |
| Observation authority | API GET for the reported amount. Optional read-only SQLite for the persisted row count. |

For an invoice save, check absence before creation and the identity and amount on readback. For an inventory rejection, read stock after the first reservation and again after the rejection. A `409` alone cannot show whether stock changed.

## 2. Match the risk to an observer

| Claim | Evidence to collect | Current OutcomeLab support |
| --- | --- | --- |
| The API exposes the expected state | GET the same run-scoped resource before and after the action | V2 HTTP contract |
| The database contains exactly one effect | Count rows keyed to the run ID | Optional read-only SQLite witness on an approved rollback-journal file |
| The persisted integer amount is correct | Check the integer sum, with a count of one for a single row | Optional SQLite witness with `--sqlite-sum COLUMN EXPECTED` |
| The persisted owner or status is correct | Inspect typed fields through an operator-approved database read | Use your existing database test harness. |
| A rejected operation leaves related records unchanged | Compare each relevant record before and after rejection | Use HTTP assertions for fields exposed by the service. Use a transaction test for backing-store effects across tables. |
| A race, worker delay, or redelivery is safe | Exercise a deterministic interleaving or controlled worker and observe the final state | Use a dedicated integration harness and report that evidence separately. |

Missing evidence stays `UNVERIFIED`. A valid contract or a successful bundled demo cannot establish a claim about your service.

## 3. Run an example, then adapt it

In an active Python 3.11+ virtual environment, from the OutcomeLab checkout:

```sh
python -m pip install -e .
outcomelab catalog
outcomelab validate --contract examples/http/v2/webhook-idempotency.json
```

Follow the [broken and corrected HTTP walkthrough](START-HERE.md) or the [deceptive API and SQLite walkthrough](sqlite-effect-witness.md). Then copy the closest contract into your application's test directory. Map its paths, approved payload, and assertions to your disposable service. V2 uses a `{run_id}` path segment for baseline and final GET and binds that ID into an approved action. If your API cannot provide that isolation through its test routes, use your own test harness for the claim.

Start your service with the normal test command and wait for readiness. Disable outbound production integrations, use synthetic test credentials, and verify the service is listening on the intended loopback port. In the following example, `tests/contracts/webhook.json` is the copy you adapted and approved:

```sh
outcomelab validate --contract tests/contracts/webhook.json
outcomelab verify-http --contract tests/contracts/webhook.json --base-url http://127.0.0.1:8765 --allow-local-writes --json
```

For bearer authentication, supply a short-lived test token through `OUTCOMELAB_BEARER_TOKEN` and add `--bearer-token`. For backing-store row counts, approve the file, table, key, and count separately and follow the [witness guide](sqlite-effect-witness.md).

## 4. Diagnose, repair, and verify again

1. Keep the receipt from the failing run. Locate the contradicted assertion, phase, and observer. With `effect_unknown: true`, reconcile the potentially committed effect before any new mutation.
2. Fix the implementation in a separate change. Re-run with the same contract bytes and observer definition. Compare contract hashes and use a fresh run ID.
3. Record the broken and corrected verdicts, what each observer established, and any skipped checks. Keep credentials, private identifiers, and raw response bodies out of reports.
4. Add the approved contract to [your CI test lifecycle](api-regression-testing-in-ci.md). Preserve the exit status and tear down the disposable environment through your application's tooling.

For AI-assisted work, use the [agent verification guide](AGENT-VERIFICATION-GUIDE.md). See the [contract reference](PRODUCTION-RISK-LAB.md) for supported methods, limits, and exit codes.
