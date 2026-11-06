# Release plan — first runnable AI Engineering Arsenal release

## Preconditions (must be verified)

- [ ] All CI jobs pass on `main` for Linux and Windows with Python 3.11 and 3.12.
- [ ] `python -m risk_lab` observes FAIL on both intentionally broken fixtures and PASS on the corrected fixtures.
- [ ] `python scripts/validate.py` succeeds.
- [ ] README quick start was tested by a person outside the original authoring environment.
- [ ] Security/privacy boundaries and limitations are visible to adopters.
- [ ] Git tag and release notes accurately match the exact verified revision.

## Suggested first GitHub Release

Tag: `v0.1.0` (only if tag is not already in use)
Title: `AI Engineering Arsenal v0.1.0 — First executable risk scenarios`
Description: `First public runnable negative-control scenarios for duplicate webhook processing and invoice persistence, with a portable agent skill, machine-readable evidence and Linux/Windows CI. Both scenarios are synthetic demonstrations, not production security assessments or measured AI model benchmarks.`

Release only through a maintainer-authorized workflow after reviewing the corresponding commit. Never claim external adoption in the release notes.

## After release

Invite outside developers to reproduce the cases and report disagreements. Track separately: verified demo reproductions, actual third-party integrations, real accepted contributions, and GitHub repository traffic. Do not interpret stars or artificial engagements as verified software usage.
