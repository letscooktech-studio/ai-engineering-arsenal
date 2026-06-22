# Security Auditor: synthetic tenant isolation review

## Input

The supplied [fixture](../evals/security-auditor/ordinary/handler.py) authenticates a caller, looks up an invoice by ID, and returns it. It contains no evidence that the invoice belongs to the caller’s organization.

## What a useful result looks like

| Field | Demonstration |
| --- | --- |
| Status | Confirmed authorization gap in the supplied handler. |
| Evidence | `handler.py` authenticates `user` but retrieves `db.invoices.get(invoice_id)` without a tenant/organization predicate. |
| Preconditions | An authenticated user can supply an invoice identifier for a different tenant; runtime route exposure and identifier predictability require confirmation. |
| Impact | Cross-tenant invoice disclosure if the data layer does not independently enforce tenant isolation. |
| Safe remediation | Scope the invoice query to the authenticated organization and enforce the same authorization rule in the data-access layer. |
| Verification | Add a test asserting a user from organization A receives no invoice from organization B; test the policy at API and repository boundaries. |
| Calibration | This review cannot prove route exposure, RLS configuration, or identifier enumeration from the fixture alone. |

The point is not to produce dramatic counts. It is to make a decision-ready claim with evidence, a safe fix, a test, and an explicit review gap.

