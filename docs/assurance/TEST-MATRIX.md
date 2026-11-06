# P0 adversarial QA matrix

Baseline `c743773c0b5443ab394b1437077145c1d2a0749d`, PR #10. Fresh Windows 11, Python 3.14.3 and SQLite 3.50.4 ran 43 tests and reproduced both false PASS results in the original 60-case harness.

Candidate scope is the transport fix and tests in this PR. Candidate observations below are from the same Windows/Python/SQLite environment. The PR checks identify the exact candidate SHA and independently run the committed suite on Windows and Ubuntu with Python 3.11 and 3.12. The original black-box harness was rerun locally; GitHub CI does not run that separate local harness.

**Wire** refers to [raw TCP process tests](../../tests/test_http_response_integrity.py). **Black box** refers to the original 60-case audit harness. Named tests refer to the unchanged existing suite. An expected failure or UNVERIFIED is a successful QA match. Cases marked partial, not run, or not implemented do not establish coverage.

| ID | Probe | Expected | Observed | Evidence or gap |
| --- | --- | --- | --- | --- |
| H01 | Well-formed JSON | PASS/0 | PASS/0 | Wire control |
| H02 | Header line without colon | UNVERIFIED/2 | UNVERIFIED/2 | Wire `Broken header`; original harness baseline PASS/0 |
| H03 | Declared gzip with plain JSON | UNVERIFIED/2 | UNVERIFIED/2 | Wire fake gzip; original harness baseline PASS/0 |
| H04 | Actual gzipped JSON | UNVERIFIED/2 | UNVERIFIED/2 | Wire gzip control |
| H05 | Conflicting Content-Length | UNVERIFIED/2 | UNVERIFIED/2 | Wire duplicate length |
| H06 | Content-Length plus Transfer-Encoding | UNVERIFIED/2 | UNVERIFIED/2 | Wire chunked header with length |
| H07 | Length greater than received body | UNVERIFIED/2 | UNVERIFIED/2 | Wire truncation |
| H08 | Length shorter than received body | Define strict policy | NOT RUN | Trailing bytes beyond declared body are outside this patch |
| H09 | Redirect | UNVERIFIED/2 | UNVERIFIED/2 | Black box redirect |
| H10 | Malformed JSON | UNVERIFIED/2 | UNVERIFIED/2 | Black box bad_json |
| H11 | Unsupported transfer coding | UNVERIFIED/2 | UNVERIFIED/2 | Wire bogus coding |
| H12 | Invalid header field name or NUL | UNVERIFIED/2 | UNVERIFIED/2 | Wire Bad name and NUL |
| H13 | Folded field or space before colon | UNVERIFIED/2 | UNVERIFIED/2 | Wire folding and whitespace |
| H14 | Oversized or excessive headers | UNVERIFIED/2 | UNVERIFIED/2 | Wire 65,537 bytes and 110 fields |
| H15 | Body stalls after headers | UNVERIFIED/2 | NOT RUN | Existing timeout test stalls before headers only |
| H16 | Wrong JSON media type | UNVERIFIED/2 | UNVERIFIED/2 | Wire text/html |
| H17 | JSON with charset parameter | PASS/0 | PASS/0 | Wire charset and identity |
| H18 | Malformed header after committing POST | UNVERIFIED/2, effect_unknown | UNVERIFIED/2, effect_unknown | Wire separate SQLite read, exactly one POST |
| H19 | EOF in framed body | UNVERIFIED/2 | UNVERIFIED/2 | Wire truncation |
| H20 | Invalid status line or HTTP version | UNVERIFIED/2 | UNVERIFIED/2 for NOTHTTP | Wire non-HTTP status line; version variants not run |
| D01 | Normal broken webhook | FAIL/1 | FAIL/1 | Black box webhook, twice |
| D02 | Fixed webhook | PASS/0 | PASS/0 | Black box webhook, twice |
| D03 | Masked duplicate ledger | HTTP-only PASS; witness FAIL | PASS/0; FAIL/1 | Black box; independent SQL found (2, 1500) |
| D04 | Wrong persisted integer amount | FAIL/1 | FAIL/1 | Black box; count PASS, sum FAIL, SQL (1, 751) |
| D05 | Correct persisted integer amount | PASS/0 | PASS/0 | Black box; SQL (1, 750) |
| D06 | NULL, text, real witness fields | UNVERIFIED/2 | UNVERIFIED/2 | Black box typed values |
| D07 | Missing or inaccessible SQLite | UNVERIFIED/2 | UNVERIFIED/2 for missing and locked | Black box; OS permission denial not run |
| D08 | Replaced witness file | UNVERIFIED/2 | UNVERIFIED/2 | Black box actual file replacement |
| D09 | Invalid identifier or missing column | INVALID/3 or UNVERIFIED/2 | INVALID/3; UNVERIFIED/2 | Black box injected identifiers and missing sum column; missing table not separately run |
| D10 | Unsupported WAL | UNVERIFIED/2 | UNVERIFIED/2 | Black box and witness tests |
| D11 | Equal total with wrong per-row values | Separate row-level oracle | NOT IMPLEMENTED | Sum is intentionally aggregate |
| D12 | Wrong owner or status | Typed row witness | NOT IMPLEMENTED | No typed row witness |
| D13 | Ledger and invoice totals disagree | Cross-table witness | NOT IMPLEMENTED | No cross-table witness |
| D14 | Rejected operation changes another table | Multi-table observer | NOT IMPLEMENTED | Inventory fixture covers one stock value |
| D15 | Repeat with fresh run IDs | Stable verdicts and hashes | MATCH | Black box 12 runs across three fixtures |
| S01 | Validate offline | VALID/0, no I/O to target | VALID/0 | Installed CLI and test_validate_has_no_network_or_subprocess |
| S02 | Malformed or duplicate manifest keys | INVALID/3 | INVALID/3 | Black box malformed; test_invalid_manifests duplicate keys |
| S03 | Unbound capture | INVALID/3 | INVALID/3 | Black box unknown binding |
| S04 | POST without consent | INVALID/3, no requests | INVALID/3, no requests | Black box and test_invalid_target_or_missing_permission_makes_no_request |
| S05 | Witness without consent | INVALID/3 | INVALID/3 | Black box and witness unit tests |
| S06 | Disallowed origin | INVALID/3 | INVALID/3 | Black box hostname and loopback alias |
| S07 | SQL identifier injection | INVALID/3 | INVALID/3 | Black box table and sum identifier |
| S08 | Absent bearer token | INVALID/3 or UNVERIFIED/2 | INVALID/3 | Black box missing token and CRLF token |
| S09 | Private data in receipt | No leakage | MATCH for sampled sentinels and path | Black box and wire; not exhaustive |
| S10 | Commit followed by disconnect | UNVERIFIED/2, effect_unknown | UNVERIFIED/2, effect_unknown | Black box read found committed row |
| S11 | Proven failure then incomplete evidence | FAIL/1 | FAIL/1 | test_proven_failure_survives_interrupted_later_write |
| S12 | Fresh install outside checkout | Installed CLI works | MATCH | Windows fresh venv and CI workflow |
| U01 | Fresh checkout setup | Successful documented install | MATCH | Fresh Windows install; onboarding time not measured |
| U02 | Adapt to unrelated backend | Measured friction | NOT RUN | No authorized external backend |
| U03 | Witness denied | UNVERIFIED/2 | UNVERIFIED/2 for lock | Black box exclusive lock; OS ACL not run |
| U04 | Agent proposes approved invariant | Correct, scoped handoff | PARTIAL | Prior pinned-baseline Codex trial used a supplied contract; no candidate trial |
| U05 | Agent drafts contract | Valid independent semantics | NOT RUN | Prior trial used existing contract |
| U06 | Agent locates defect | Evidence-backed source location | PARTIAL | Prior pinned-baseline trial traced fixture ledger insertion |
| U07 | Agent proposes repair | Oracle unchanged | PARTIAL | Prior trial gave a repair hypothesis; no code edits |
| U08 | Agent reruns after repair | Same oracle after actual repair | NOT RUN | Reference variants are controls |
| U09 | Independent maintainer evaluation | Outside-project evidence | NOT RUN | No feedback collected |
| U10 | Audit README claims | Scope supported by tests | MATCH for inspected claims | Claims matrix, Windows CLI controls and relative link check |
| X01 | Server-generated ID across routes | Future acceptance gate | NOT IMPLEMENTED in P0 | No expansion claims; local PATCH work excluded |
| X02 | PATCH with database witness | Future acceptance gate | NOT IMPLEMENTED in P0 | No expansion claims; local PATCH work excluded |
| X03 | DELETE and absence | Future acceptance gate | NOT IMPLEMENTED in P0 | No expansion claims; local PATCH work excluded |
| X04 | Deterministic oversell race | Future acceptance gate | NOT IMPLEMENTED in P0 | No expansion claims; local PATCH work excluded |
| X05 | Job replay | Future acceptance gate | NOT IMPLEMENTED in P0 | No expansion claims; local PATCH work excluded |
| X06 | Async completion deadline | Future acceptance gate | NOT IMPLEMENTED in P0 | No expansion claims; local PATCH work excluded |
| X07 | PostgreSQL rollback | Future acceptance gate | NOT IMPLEMENTED in P0 | No expansion claims; local PATCH work excluded |
| X08 | Cross-tenant effects | Future acceptance gate | NOT IMPLEMENTED in P0 | No expansion claims; local PATCH work excluded |
| X09 | Lost MCP reply | Future acceptance gate | NOT IMPLEMENTED in P0 | No expansion claims; local PATCH work excluded |
| X10 | Per-row value corruption | Future acceptance gate | NOT IMPLEMENTED in P0 | No expansion claims; local PATCH work excluded |

See [manual reproduction](MANUAL-REPRODUCTION.md) for commands and the [research mapping](RESEARCH-EVIDENCE.md) for standards and project policy.
