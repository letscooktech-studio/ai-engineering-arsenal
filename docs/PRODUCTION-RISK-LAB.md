# Production Risk Lab — executable negative controls

This is an **early, standard-library-only demonstration system**. It provides repeatable examples of why an API response or a successful function return does not prove a business outcome. It does **not** inspect real services or automatically run third-party agents, mobile emulators, browsers, or payment infrastructure.

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
