# Titan skill standard

Every published Titan skill is an operating procedure, not a persona. Its `SKILL.md` must contain a precise trigger description, a minimum intake, workflow, output contract, quality gates, and improvement loop. The following controls apply to every skill, including where a concise skill does not repeat them verbatim.

## Evidence and reasoning

Separate supplied facts, verified external evidence, assumptions, estimates, hypotheses, and decisions. Prefer primary evidence. Attach a source location and retrieval date to external claims. If the evidence is insufficient to decide, say so and name the smallest next observation that would change the decision.

## Verification and failure detection

Turn every material recommendation into an observable check: test, measurement, review, rehearsal, or rollback criterion. Detect missing scope, unavailable critical artifacts, stale evidence, contradictory inputs, unsupported tool assumptions, and claims not grounded in supplied material. Mark the output incomplete rather than filling gaps with confident prose.

## Risk and safety

Respect authorization, privacy, security, contractual, and operational boundaries. Do not expose secrets, impersonate users, make irreversible production changes, or provide unauthorized harmful instructions. Escalate a high-stakes recommendation to an appropriate human owner when confidence or authority is insufficient.

## Evaluation and benchmark

Run the same task with and without the skill using equivalent model, tools, temperature, and token budget. Score evidence fidelity, decision usefulness, risk handling, verification, calibration, and efficiency using [EVALUATION-STANDARD.md](EVALUATION-STANDARD.md) and [BENCHMARK-LAB.md](BENCHMARK-LAB.md). Publish limitations and failure modes along with any claimed improvement.

## Success and maintenance

Define task-local success before acting: a validated decision, a passed test, a measured outcome, or a safe stop. Record owners and review dates for decisions that matter. Improve the skill from scored failures; avoid expanding it with untested advice.
