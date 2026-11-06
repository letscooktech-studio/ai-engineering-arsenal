# OutcomeLab — Local HTTP API Regression Testing

![LetsCookTech Open Source Team banner](assets/letscooktech-open-source-team-banner.png)

OutcomeLab is an open-source CLI for stateful HTTP API testing. It checks webhook idempotency, invoice persistence, and inventory reservation behavior against a disposable local service or CI test environment. For example, it sends the same webhook twice, then reads the ledger to check that the payment was credited only once.

## Quickstart

Use Python 3.11 or newer. From the repository root, in an active virtual environment:

```sh
python -m pip install -e .
outcomelab catalog
outcomelab demo
```

The demo runs two bundled SQLite examples. To try the verifier over HTTP, start the disposable reference service in one terminal:

```sh
python -m risk_lab.demo_http --variant broken --port 8765
```

In a second terminal with the same environment active, run:

```sh
outcomelab verify-http --contract examples/http/v2/webhook-idempotency.json --base-url http://127.0.0.1:8765 --allow-local-writes
```

The broken service returns HTTP 200 for both deliveries, but the ledger shows two credits. OutcomeLab prints `FAIL (7 assertions, 0 skipped)`. Restart the service with `--variant fixed` and run the same command. It prints `PASS (7 assertions, 0 skipped)`.

## Check the backing store

The optional SQLite witness can catch a duplicate ledger row even when the API reports one credit and every HTTP assertion passes. It counts only rows for the current run in an explicitly approved disposable database. An optional integer sum also detects a wrong amount when the row count is correct. See the [deceptive-API walkthrough](docs/sqlite-effect-witness.md) and the [evidence matrix](docs/CLAIMS-MATRIX.md).

## Check your own API

Copy a [stateful example contract](examples/http/v2/) and set the routes, test payloads, and expected state for your service. Check it offline with `outcomelab validate --contract PATH`, then run against a disposable database. The runner accepts literal IPv4 loopback targets and requires `--allow-local-writes` for POST requests. Add `--json` to get a receipt with the contract hash, verdict, and assertion outcomes.

- [Backend developer guide](docs/BACKEND-VERIFICATION-GUIDE.md)
- [Agent verification guide and reusable prompt](docs/AGENT-VERIFICATION-GUIDE.md)
- [Walkthrough for webhook idempotency and invoice persistence](docs/START-HERE.md)
- [Run API regression tests in CI](docs/api-regression-testing-in-ci.md)
- [Contract format, exit codes, and safety rules](docs/PRODUCTION-RISK-LAB.md)
- [Production Risk Lab agent skill](skills/production-risk-lab/SKILL.md)

A passing result covers the observations in the supplied contract. The bundled examples use fictional inputs and temporary databases. [Reproduce the checks independently](https://github.com/letscooktech-studio/outcomelab/issues/3) or [propose a scenario](https://github.com/letscooktech-studio/outcomelab/issues/4).

## Engineering resources

| Resource | Contents |
| --- | --- |
| [Skills](skills/) | Portable playbooks for security, architecture, and engineering reviews |
| [Compatibility](docs/COMPATIBILITY.md) | How to use the playbooks in different agent clients |
| [Case studies](case-studies/) | Illustrative walkthroughs of the review process |
| [Benchmarks](benchmarks/) and [evaluation tooling](docs/RUNNABLE-EVALUATIONS.md) | Rubrics, comparison fixtures, and reproducibility guidance |
| [Contributing](CONTRIBUTING.md) and [skill standard](docs/SKILL-STANDARD.md) | How to contribute a contract, fix, or playbook |

Maintained by the LetsCookTech Open Source Team. [Releases](https://github.com/letscooktech-studio/outcomelab/releases) · [Report an issue](https://github.com/letscooktech-studio/outcomelab/issues) · [MIT license](LICENSE)
