# Publishing OutcomeLab on GitHub

## Recommendation

Start with a normal repository under the identity that will actually maintain it. If OutcomeLab will have multiple long-term maintainers, separate branding, or several future repositories, create a GitHub organization and publish it there from day one. Do not maintain two canonical copies; use one canonical public repository and transfer it later if ownership changes.

Suggested canonical name: `ai-engineering-arsenal`. It is model-agnostic, durable, and directly targets the search category: AI engineering.

## First publish checklist

1. Create the empty public repository on the chosen personal account or organization; do not initialize it with a conflicting README.
2. Set repository description: `Open-source AI engineering skills, workflows, audits, evaluation systems, benchmarks, and playbooks for developers, founders, technical teams, and AI builders.` Add topics: `ai-engineering`, `ai-code-review`, `security-audit`, `architecture-review`, `startup-validation`, `ai-evaluation`, `ai-agents`, `developer-tools`.
3. Add the remote locally, commit the reviewed files, and push `main`. Enable branch protection requiring the validation workflow before merging.
4. Configure repository social preview, Discussions (for questions/showcase), Issues, security reporting, and a release process. Pin the repository on the maintainer profile or organization.
5. Create `v0.1.0` only after validation passes. The release notes must say evaluations are planned unless scored results are included.

## Search and GitHub discovery

Repository ranking cannot be guaranteed. Improve discoverability with a unique name, a plain first sentence describing the problem and audience, accurate topics, a useful README, frequent substantive releases, real examples/evaluations, and inbound references from technical write-ups. Avoid keyword stuffing, fake stars, copied content, or claims that a skill can replace security review or engineering judgment.

## First 30 days

- Week 1: publish the repository and one walkthrough using `production-ai-saas-builder` on a safe demo.
- Week 2: ask five builders to run one skill on a real but sanitized task; convert gaps into issues.
- Week 3: publish the first baseline-versus-skill scored case and a limitation discovered during testing.
- Week 4: make one carefully targeted community post that leads with the case study, then answer every substantive question.

## Decision rule: personal vs organization

Choose a **personal repository** if one person owns governance and is proving demand. Choose an **organization** if governance, brand independence, or multiple repositories/maintainers are already real. An organization is a coordination choice, not a growth strategy.

Developed by the LetsCookTech Open Source Team.
