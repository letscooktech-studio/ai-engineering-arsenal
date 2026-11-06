# OutcomeLab changelog

## 0.2.0rc1 — release candidate

- Added v2 contracts with run-scoped identities, preconditions, captured identifiers, and before/after comparisons.
- Added offline validation and opt-in environment-supplied bearer authentication for disposable loopback services.
- Added redacted phase evidence and repeatable HTTP examples for webhook idempotency and invoice persistence.
- Kept v1 contracts, legacy demos, and both installed CLI names compatible.

### Existing 0.2.0 development baseline

- Added an installable CLI that verifies a developer-approved business-state contract against a disposable local HTTP service.
- Added executable broken and corrected webhook and invoice services with SQLite readback.
- Added a catalog, read-only project doctor and redacted JSON receipts.
- Preserved the legacy `python -m risk_lab` demonstrations and the published 0.1.0 tag.
