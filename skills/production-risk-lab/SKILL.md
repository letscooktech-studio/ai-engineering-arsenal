---
name: production-risk-lab
description: Verify localhost HTTP business outcomes and run synthetic production-risk demonstrations and help design independently verifiable acceptance criteria. Use for reviewing duplicate webhook processing, invoice durability, repeatable failure reproducers, regression coverage, and production-readiness claims. Never claim real-app verification from synthetic fixtures.
---

# Production Risk Lab

You are operating an evidence-first engineering workflow. Follow the [OutcomeLab skill standard](../../docs/SKILL-STANDARD.md) and [risk-lab methodology](../../docs/PRODUCTION-RISK-LAB.md).

Use this skill when an engineer wants to understand **which production invariant needs a test, how to create a falsifiable negative control, and which evidence can actually justify completion**. The built-in scenarios are synthetic teaching demonstrations, not scans of arbitrary user repositories.

## Intake

Identify the project's platform, authorization, scope, invariant, current test framework, relevant environments, and trusted acceptance owner. Ask only for material missing information. Separate external facts, code evidence, inference, and assumptions. Never require a paid model, external API key, or internet to run included fixtures.

## Workflow

1. Inspect the actual code, test infrastructure, and relevant trust boundaries rather than assuming the stack.
2. State the user-visible outcome, forbidden failure, expected negative control, and who approved the test oracle.
3. Where platform/API details may have changed, look up current official documentation **only if the host has approved web tools**. Cite URL, revision/version, and retrieval date; otherwise mark external research unavailable.
4. Run `python -m risk_lab` from the OutcomeLab repository root for its **two bundled synthetic cases**. Use `--json` for machine-readable evidence. This command does not run the user's application.
5. Inspect both results: the deliberately broken example must FAIL and the corrected example must PASS under the same scenario invariant. Treat exceptions and unavailable checks as UNVERIFIED.
6. For a developer-owned localhost HTTP API, propose a contract from the real endpoints, obtain approval for the expected state, and check it offline with `outcomelab validate --contract PATH`. Run `outcomelab verify-http` against a disposable database. Use a v2 baseline and run-specific identity for state transitions. Require GET state readback and use `--allow-local-writes` only for approved POSTs. See the [quickstart](../../docs/START-HERE.md).
7. Treat receipts as observations from the target HTTP API. Request independent confirmation when test code and candidate implementation are both controlled by the coding agent; preserve results tied to a specific revision and environment.

## Output contract

Return an evidence ledger with: scope, tested implementation, executable command, observed invariant, negative control, corrected control, tool/version, source evidence, untested surfaces, reviewer, and verdict. Report exactly `DEMONSTRATED`, `REGRESSION`, or `UNVERIFIED` for built-in lab results. For external projects use `PASS`/`FAIL`/`UNVERIFIED` **per explicitly approved acceptance criterion**, never as a global production-ready badge.

## Quality gates

- Never substitute self-authored assertions for independently approved production requirements.
- A pass requires the intended check to run on the intended candidate revision with an observable result.
- No positive result when a test is skipped, exceptions occur, tools are unavailable, or evidence came from an unrelated target.
- Never execute untrusted project code, access live payment endpoints, or modify production data without explicit authorization and appropriate isolation.
- No claim that synthetic SQLite scenarios verify payment-webhook signature validation, race conditions, real financial settlements, a UI, or complete restart behavior.
- Run `python -m unittest discover -s tests -v` and `python scripts/validate.py` for contributions.

## Improvement loop

Use independently reproduced negative cases to refine the oracle and fixture. Preserve the broken version and record behavior changes. Prefer meaningful maintainers' scenarios over expanding the README or adding shallow skills. Publish observed failures and limitations as well as successes.

Copy this skill directory to `.agents/skills/production-risk-lab` for a Codex project, or to the user's `.agents/skills` directory for personal use. Other agents can load the portable SKILL.md using their client-specific setup. Invocation and tool permissions depend on the host.
