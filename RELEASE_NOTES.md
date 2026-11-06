# AI Engineering Arsenal v0.1.0

This is an **early open-source foundation release**. It combines portable AI engineering review skills with dependency-free, runnable synthetic risk demonstrations and evidence-oriented evaluation tools.

## First executable risk demonstrations

- **Duplicate webhook event:** A deliberately broken SQLite handler credits an invoice twice when the same event is delivered twice. The corrected fixture processes an identical event only once and rejects conflicting payloads with the same event ID.
- **Invoice persistence:** A deliberately broken save function acknowledges a write that was rolled back. The corrected fixture persists the invoice and is checked using a reopened SQLite connection.

Both scenarios include an independent acceptance invariant applied to the broken and corrected fixture, detailed observations, contract/source hashes and automated unit tests.

## Run locally

Requires Python 3.11+; no network, database server, paid AI subscription or third-party packages.

```sh
python -m risk_lab
python -m risk_lab --json
python -m unittest discover -s tests -v
python scripts/validate.py
```

## Important limitations

- Synthetic, repository-owned examples, **not** real payment provider or user-application testing.
- Not a security certificate, independent AI coding-agent benchmark or proof of production readiness.
- Hashes identify example content; the repo author can change both the content and hashes.
- No external integration or independent adoption is claimed.

Documentation: [Production Risk Lab](docs/PRODUCTION-RISK-LAB.md).
