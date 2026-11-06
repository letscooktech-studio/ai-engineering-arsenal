# OutcomeLab

OutcomeLab checks whether a local API produced the expected business result. Send the same webhook twice, then read the ledger to verify that only one credit was recorded.

Use Python 3.11+ and install in a virtual environment:

```sh
python -m pip install -e .
outcomelab catalog
```

Follow the [two-terminal quickstart](docs/START-HERE.md) to see a broken service fail and a corrected service pass the same contract. Then adapt the contract to your own disposable local API. The verifier connects only to literal IPv4 loopback and requires explicit opt-in for POSTs.

The reference services use temporary SQLite databases. A receipt records a local run for the supplied contract. The case studies and evaluation examples below are illustrative fixtures.

## Flagship production reviewers

These are the category-defining OutcomeLab skills. Start here if you want practical value instead of another prompt collection.

| Reviewer | What it catches | Best for |
| --- | --- | --- |
| [`nextjs-production-architecture-reviewer`](skills/nextjs-production-architecture-reviewer) | Next.js architecture, App Router, Server Actions, performance, SEO, AI-search, security, Vercel cost, Supabase integration, and deployment risks. | Next.js SaaS, AI platforms, ecommerce, dashboards, blogs, marketplaces, agency sites. |
| [`supabase-production-auditor`](skills/supabase-production-auditor) | RLS bypass, service-role misuse, weak auth, storage exposure, Realtime fan-out, database growth, cost, backups, and production-readiness gaps. | Supabase SaaS, AI apps, mobile apps, internal tools, marketplaces, learning platforms. |
| [`ai-agent-architecture-reviewer`](skills/ai-agent-architecture-reviewer) | Planning failures, memory risks, tool abuse, MCP risks, prompt injection, hallucination gaps, cost fan-out, observability, and reliability issues. | AI agents, copilots, workflow agents, browser agents, coding agents, research agents, multi-agent systems. |
| [`agentic-skill-pack-integrator`](skills/agentic-skill-pack-integrator) | Converts external skill packs into safe OutcomeLab-compatible operating frameworks. | Codex, Claude Code, Cursor, Windsurf, Cline, Roo Code, Aider, ChatGPT, Gemini, Antigravity-style agentic IDEs. |
| [`nvidia-accelerated-ai-systems-operator`](skills/nvidia-accelerated-ai-systems-operator) | Adds safety, validation, cost, and production-readiness review around NVIDIA/GPU accelerated AI workflows. | AI-Q, cuOpt, DALI, Dynamo, NemoClaw, Omniverse, physical AI, GPU infrastructure. |

Each flagship reviewer includes a benchmark rubric and comparison template under [`benchmarks/`](benchmarks) so future claims can be proven with baseline-vs-framework outputs.

## See the difference

| Without a playbook | With an OutcomeLab playbook |
| --- | --- |
| "Add authentication and validate inputs." | Maps assets and trust boundaries; reports evidence, preconditions, impact, remediation, regression tests, confidence, and review gaps. |
| "Use a queue and a database." | Compares designs, records assumptions and trade-offs, specifies timeouts/retries/rollback, and names the test that validates the decision. |
| "Build an AI SaaS." | Produces an acceptance contract plus tenancy, authorization, AI-evaluation, cost-cap, migration, observability, release, and rollback gates. |

Read a safe, concrete finding from the [synthetic tenant-review case study](case-studies/security-auditor-synthetic-tenant-review.md). It demonstrates an evidence-linked result; it does **not** claim a benchmark win.

## Start with these four

| Playbook | Use it when | Proof path |
| --- | --- | --- |
| [`security-auditor`](skills/security-auditor) | You need an authorized code, API, infra, or release-risk review. | [Case study](case-studies/security-auditor-synthetic-tenant-review.md) · [Rubric](benchmarks/security-auditor/evaluation-rubric.md) |
| [`startup-validator`](skills/startup-validator) | You need to test whether a product should exist before building it. | [Case study](case-studies/startup-validator-concierge-test.md) · [Rubric](benchmarks/startup-validator/evaluation-rubric.md) |
| [`competitor-analyzer`](skills/competitor-analyzer) | You need positioning based on evidence rather than a feature grid. | [Case study](case-studies/competitor-analyzer-market-map.md) · [Rubric](benchmarks/competitor-analyzer/evaluation-rubric.md) |
| [`cto-operating-system`](skills/cto-operating-system) | You need a focused operating plan from engineering signals. | [Case study](case-studies/cto-operating-system-quarterly-reset.md) · [Rubric](benchmarks/cto-operating-system/evaluation-rubric.md) |

## Use a playbook

Copy a skill folder into your agent's skills directory, or attach its `SKILL.md` to the task. Example:

```text
Use $security-auditor to review this authorized SaaS API. Scope: /api/invoices.
Evidence: repository files and deployment configuration attached.
Return only confirmed findings, review gaps, safe remediation, and verification tests.
```

Works as portable Markdown with Codex, Claude Code/Projects, ChatGPT, Gemini, Cursor, Windsurf, Cline, Roo Code, Aider, and agent SDKs. See [compatibility](docs/COMPATIBILITY.md).

## First wave

`nextjs-production-architecture-reviewer` · `supabase-production-auditor` · `ai-agent-architecture-reviewer` · `agentic-skill-pack-integrator` · `nvidia-accelerated-ai-systems-operator` · `security-auditor` · `startup-validator` · `competitor-analyzer` · `system-architect` · `database-architect` · `technical-debt-hunter` · `ai-search-optimizer` · `seo-auditor` · `cost-explosion-detector` · `cto-operating-system` · `production-ai-saas-builder`

## Searchable guides

These pages are written for GitHub, Google, and AI-search discoverability while staying useful to developers:

- [AI code review](docs/ai-code-review.md)
- [AI security audit](docs/ai-security-audit.md)
- [Architecture review AI](docs/architecture-review-ai.md)
- [Technical due diligence AI](docs/technical-due-diligence-ai.md)
- [AI CTO](docs/ai-cto.md)
- [Agentic skills for CLI and app clients](docs/agentic-skills-for-cli-and-apps.md)
- [Upstream skill pack imports](docs/upstream-skill-pack-imports.md)

## Evidence, not marketing

OutcomeLab does not claim that a playbook finds more issues, saves money, or outperforms a model until a reproducible result is published. Each benchmark holds model/version, tools, temperature, budget, inputs, rubric, baseline, playbook run, evaluator, and limitations constant. Read the [benchmark protocol](benchmarks/README.md).

## Trust system

OutcomeLab has a repository-level system for improving itself instead of only adding more skills:

| System | Purpose |
| --- | --- |
| [Repository audit](docs/REPOSITORY-AUDIT.md) | Finds weak assets, filler risk, missing proof, and deletion candidates. |
| [OutcomeLab constitution](docs/ARSENAL-CONSTITUTION.md) | Defines the laws every contribution must follow. |
| [AI CTO operating model](docs/OPERATING-MODEL.md) | Standardizes input, research, verification, risk review, decision, and quality review. |
| [Evaluation standard](docs/EVALUATION-STANDARD.md) | Scores outputs across accuracy, evidence, verification, actionability, security, and user value. |
| [Red-team framework](docs/RED-TEAM-FRAMEWORK.md) | Attacks outputs before users trust them. |
| [Benchmark lab](docs/BENCHMARK-LAB.md) | Defines the proof artifacts required before performance claims. |
| [Self-evolution roadmap](docs/SELF-EVOLUTION.md) | Moves the project toward a proof engine, runtime adapters, and Open Source AI CTO workflows. |

## FAQ

### Is this just a prompt repository?

No. A prompt repository optimizes for copyable text. OutcomeLab optimizes for evidence, verification, failure detection, benchmarks, and repeatable engineering decisions.

### Is this tied to one AI model?

No. The playbooks are Markdown-first and model-portable. They are designed for Claude, ChatGPT, Gemini, Codex, Cursor, Windsurf, Cline, Roo Code, Aider, OpenAI Agents, Anthropic agents, and future AI systems.

### Does it already prove benchmark superiority?

Not yet. The repository includes rubrics, synthetic case studies, and benchmark protocol. Public benchmark wins should only be claimed after raw baseline and framework outputs are published.


## Production Risk Lab — runnable demos

**New here?** [Try the 5-minute reproducibility guide](docs/START-HERE.md) or [report a platform-specific result](https://github.com/letscooktech-studio/outcomelab/issues/3).

The [Production Risk Lab](docs/PRODUCTION-RISK-LAB.md) adds two **executable, synthetic** negative-control scenarios: duplicate webhook events and invoice persistence. Each runs the same outcome check against intentionally broken and corrected SQLite implementations. They are teaching/evaluation fixtures, **not production software scans or model benchmarks**.

```sh
python -m risk_lab
python -m risk_lab --json
python -m unittest discover -s tests -v
```

The command runs locally with Python 3.11+ and no API keys or third-party packages. It reports `DEMONSTRATED` only when a broken fixture fails and a corrected fixture passes. It does not verify your own app. Read the [limitations](docs/PRODUCTION-RISK-LAB.md#non-goals-and-safety-limitations) before interpreting results. The [agent skill](skills/production-risk-lab/SKILL.md) helps developers reason about additional acceptance criteria.

## Contribute a useful playbook

A contribution needs a recurring decision problem, an evidence/verification contract, safety boundaries, and a sanitized evaluation case. Generic personas and untested prompt collections do not qualify. Start with [CONTRIBUTING.md](CONTRIBUTING.md).

## Repository map

| Path | Purpose |
| --- | --- |
| [`skills/`](skills) | Portable operating playbooks. |
| [`case-studies/`](case-studies) | Safe, concrete demonstrations of the output standard. |
| [`benchmarks/`](benchmarks) | Per-playbook rubrics and reproducibility protocol. |
| [`evals/`](evals) | Versioned task fixtures for baseline-versus-playbook runs. |
| [`docs/`](docs) | Product thesis, compatibility, launch, and publishing guidance. |
| [`templates/`](templates) | Proof-pack templates for graduating skills into trusted assets. |

## Status

[`v0.1.0`](https://github.com/letscooktech-studio/outcomelab/releases/tag/v0.1.0) is the first published foundation release. Case studies are synthetic demonstrations; public benchmark results are not yet published. That distinction is intentional.

Developed by the LetsCookTech Open Source Team.

## License

MIT. See [LICENSE](LICENSE).


## Executable rubric comparisons (experimental)

The repository now includes a dependency-free strict rubric scorer, artifact-hash checked baseline-versus-skill comparison, and automated regression tests. Run `python -m unittest discover -s tests -v` and read [Runnable paired evaluations](docs/RUNNABLE-EVALUATIONS.md) before interpreting results. The included example is **synthetic**, not a measured benchmark win.
