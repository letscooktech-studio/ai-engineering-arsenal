# Backend reliability runbook

Use this runbook to turn a production risk into a repeatable test in a disposable environment. The goal is to decide whether one operation produced its intended effects and avoided its forbidden effects.

## 1. Establish the acceptance oracle

Record the following before changing the implementation.

| Question | Billing example |
| --- | --- |
| What does the business permit? | One posted credit of 750 cents for one logical event |
| Who can act? | A single authorized test actor with a short-lived local token |
| What must be true before the action? | The run-scoped invoice has no ledger effects |
| What can change? | Only the invoice and records intentionally created for the run |
| What must remain unchanged? | Ownership, amount after a duplicate, and unrelated invoices |
| Which observer can establish each fact? | HTTP for client-visible results, SQLite for approved persisted fields |
| How does the run end? | Preserve a redacted receipt, then dispose of the test database |

Approve the expected behavior with whoever owns the feature. Preserve the approved contract bytes outside the implementation change. A hash can establish that two runs used the same bytes. Access controls determine who can change both the contract and its reference hash.

## 2. Pick the right check

| Failure mode | Minimum useful observation | Available here |
| --- | --- | --- |
| Duplicate webhook | Count ledger effects for one logical event after redelivery | V2 webhook contract and SQLite count |
| Acknowledged write lost | Read the created object through a fresh DB connection | V2 invoice contract and disposable fixture |
| Rejected inventory reservation changes stock | Observe stock before and after the rejected operation | V2 inventory contract |
| Correct count, wrong amount | Check persisted integer minor units | SQLite integer sum |
| Correct count and amount, wrong owner/status | Compare exact stored fields on the approved row | SQLite exact fields |
| Cross-table partial commit | Read all coupled records in one consistent snapshot | Use your database integration suite |
| Two workers race to claim one job | Force a specific interleaving, then inspect persisted effects | Use a barrier-enabled integration harness |
| Accepted work never completes | Poll read-only state until an approved monotonic deadline | Use your worker test harness |
| Unauthorized actor changes data | Compare permitted and forbidden operations and confirm foreign state stayed unchanged | Use an authorized multi-identity harness |

## 3. Choose inputs and isolate state

1. Start your normal application test process on literal IPv4 loopback. Point it at disposable data. Disable provider calls and production integrations in the app itself.
2. Copy a [v2 reference contract](../examples/http/v2/) to your test directory. Map the approved request paths, expected statuses, and state readback to your test routes. Review [contract limits](PRODUCTION-RISK-LAB.md) if your API has different route shapes or methods.
3. Use `{run_id}` to bind this run to a fresh resource. An empty baseline and an exact final identity prevent pre-existing rows from satisfying a new test.
4. Validate offline with `outcomelab validate --contract PATH`. Then run the authorized HTTP and optional database witness. Follow the [developer guide](BACKEND-VERIFICATION-GUIDE.md) for the commands and [SQLite walkthrough](sqlite-effect-witness.md) for observer setup.

### Walk through a false green

A test service returns the right credited amount and persists exactly one ledger row. The application accidentally assigns that row to the wrong owner. The HTTP contract and a count or sum still pass. An exact witness for the approved owner fails.

The [live stored-owner regression](../tests/test_sqlite_exact_fields.py) runs that case and its corrected variant with the same webhook contract. It reads the database again through a separate SQLite connection to confirm the result.

```sh
python -m unittest discover -s tests -p test_sqlite_exact_fields.py -v
```

## 4. Interpret and reconcile

| Signal | What to do |
| --- | --- |
| PASS | Report the specific claim and observer. Record anything the run could not establish. |
| FAIL | Identify the contradictory step or witness assertion. Keep the failing receipt and correct the smallest causal code path. |
| UNVERIFIED | Check scope, readiness, response integrity, and witness availability. Obtain the missing evidence before approval. |
| INVALID | Fix the contract, target, or consent settings before executing anything. |
| effect_unknown | Check the operation ID against approved state before sending any retry. The operation may already have committed. |

For exact field checks, receipt entries appear in the same order as the `--sqlite-field` flags. The runner omits the column values. Keep the approved selector definition in an operator-controlled location and compare its digest along with the contract digest.

### Troubleshoot incomplete evidence

- **HTTP succeeds but SQLite is unavailable.** Confirm the file is the operator-approved canonical path and uses a supported rollback journal. Confirm the table and visible columns exist. If the file was replaced or locked, re-establish a safe baseline before another write.
- **The witness count matches but the amount or field fails.** Trace the database write and data mapping. Check exact integer units, SQLite storage types, and ownership. A case-insensitive column collation does not relax the field oracle.
- **The response is malformed or advertises an unsupported encoding.** Inspect the disposable server's response boundary. Fix the protocol behavior or use a supported uncompressed test route. Reconcile possible writes before retrying.
- **The HTTP contract passes but an important observer is absent.** Record the unverified claim separately. Add an approved observer that can see the state the business rule actually protects.

## 5. Keep the check in your engineering loop

- Establish a negative control where it is safe to do so. Confirm the same oracle fails on the known defect and passes after repair.
- Re-run without resetting when claiming isolation. Compare stable verdicts and digests across fresh run IDs.
- Integrate into [your CI lifecycle](api-regression-testing-in-ci.md). Preserve the CLI exit status and retain a sanitized receipt. Tear down the service and disposable data with your existing tooling.
- Use the [agent guide](AGENT-VERIFICATION-GUIDE.md) to hand off the approved oracle, a scoped diagnosis, and the unchanged rerun. Keep implementation repairs separate from acceptance changes.

The [evidence matrix](CLAIMS-MATRIX.md) and [transport QA matrix](assurance/TEST-MATRIX.md) show what has been exercised and where coverage ends.
