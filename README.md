# OutcomeLab

![LetsCookTech Open Source Team banner](assets/letscooktech-open-source-team-banner.png)

OutcomeLab checks whether your local HTTP API did what you expected. For example, it sends the same webhook twice, then reads the ledger to check that the payment was credited only once.

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
outcomelab verify-http --contract examples/http/webhook-idempotency.json --base-url http://127.0.0.1:8765 --allow-local-writes
```

The broken service returns HTTP 200 for both deliveries, but the ledger shows two credits. OutcomeLab prints `FAIL (2 assertions, 0 skipped)`. Restart the service with `--variant fixed` and run the same command. It prints `PASS (2 assertions, 0 skipped)`.

## Check your own API

Copy an [example contract](examples/http/) and set the routes, test payloads, and expected state for your service. Run against a disposable database. The runner accepts literal IPv4 loopback targets and requires `--allow-local-writes` for POST requests. Add `--json` to get a receipt with the contract hash, verdict, and assertion outcomes.

- [Walkthrough for webhook idempotency and invoice persistence](docs/START-HERE.md)
- [Contract format, exit codes, and safety rules](docs/PRODUCTION-RISK-LAB.md)
- [Production Risk Lab agent skill](skills/production-risk-lab/SKILL.md)

A passing result covers the observations in the supplied contract. The bundled examples use fictional inputs and temporary databases.

## Engineering resources

| Resource | Contents |
| --- | --- |
| [Skills](skills/) | Portable playbooks for security, architecture, and engineering reviews |
| [Compatibility](docs/COMPATIBILITY.md) | How to use the playbooks in different agent clients |
| [Case studies](case-studies/) | Illustrative walkthroughs of the review process |
| [Benchmarks](benchmarks/) and [evaluation tooling](docs/RUNNABLE-EVALUATIONS.md) | Rubrics, comparison fixtures, and reproducibility guidance |
| [Contributing](CONTRIBUTING.md) and [skill standard](docs/SKILL-STANDARD.md) | How to contribute a contract, fix, or playbook |

Maintained by the LetsCookTech Open Source Team. [Releases](https://github.com/letscooktech-studio/outcomelab/releases) · [Report an issue](https://github.com/letscooktech-studio/outcomelab/issues) · [MIT license](LICENSE)
