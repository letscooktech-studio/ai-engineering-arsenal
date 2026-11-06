# Benchmark contract

Developed by the LetsCookTech Open Source Team.

OutcomeLab evaluates whether a skill improves decisions, not whether it produces longer prose.

## Case format

Every evaluation case contains a sanitized input artifact, task statement, rubric, expected safety boundaries, and hidden scoring notes. Run the same model, temperature, tools, and token budget both with and without the skill.

## Scorecard

Score each dimension from 0–4:

| Dimension | 0 | 4 |
| --- | --- | --- |
| Evidence fidelity | Unsupported claims | Claims trace to supplied evidence |
| Decision usefulness | Generic advice | Clear, prioritized, actionable decision |
| Risk handling | Misses material failures | Names risks, limits, and mitigations |
| Verification | No test path | Concrete, feasible validation criteria |
| Calibration | False certainty | Explicit unknowns and confidence |
| Efficiency | Meandering output | Complete within the task budget |

Report raw scores, cost, latency, evaluator agreement, and known failure modes. Do not combine runs across model versions without labeling them.

## Minimum publication bar

- Three representative cases per skill: ordinary, incomplete-context, and adversarial/edge case.
- One independent human review for a high-stakes skill.
- A published limitation when the skill does not outperform baseline on a dimension.
- No real secrets, customer data, or exploit-ready artifacts in public cases.

## Baseline comparison template

| Dimension | Default assistant | With skill | Evidence |
| --- | ---: | ---: | --- |
| Evidence fidelity |  |  |  |
| Decision usefulness |  |  |  |
| Risk handling |  |  |  |
| Verification |  |  |  |
| Calibration |  |  |  |

## First-wave benchmark plan

| Skill | Baseline task | Skill advantage to test | Primary limitation | Risk |
| --- | --- | --- | --- | --- |
| Security Auditor | Generic code review | Evidence-linked findings and safe verification | Cannot prove runtime behavior from static input | High |
| Startup Validator | Generic business-plan critique | Falsifiable tests and precommitted thresholds | Weak when customer access is absent | Medium |
| Competitor Analyzer | Feature comparison | Source ledger and disconfirming evidence | External facts can become stale | Medium |
| System Architect | Diagram request | Trade-offs, failure behavior, rollback | Estimates depend on missing load data | High |
| Database Architect | Schema generation | Invariants and migration safety | Requires workload and data-classification context | High |
| Technical Debt Hunter | Refactor suggestions | Evidence-based prioritization | Telemetry gaps lower confidence | Medium |
| AI Search Optimizer | Content rewrite | Claim provenance and measurement plan | No ranking guarantee | Medium |
| SEO Auditor | SEO checklist | URL-level evidence and attribution discipline | Search changes have long observation windows | Medium |
| Cost Explosion Detector | Cost-cut ideas | Driver traceability and safe controls | Incomplete allocation data distorts conclusions | High |
| CTO Operating System | Engineering-health summary | Outcome-linked priorities and cadence | Sensitive organizational context needs judgment | High |
| Production AI SaaS Builder | “Build me a SaaS” request | End-to-end delivery gates and deployable artifacts | Requires real credentials and human approval to deploy | High |

Expected improvement is a higher rubric score, not a fixed percentage. Report absolute scores and evaluator agreement; do not infer causation from one run.

## Failure triage

Classify failures as missing context, ambiguous instruction, unsupported tool assumption, unsafe advice, hallucinated evidence, weak prioritization, or evaluation flaw. Fix the smallest responsible layer and rerun the affected cases.
