# OutcomeLab: product thesis

Developed by the LetsCookTech Open Source Team.

## Mission

Become the default open-source layer for repeatable AI-assisted engineering decisions. The unit of value is not a prompt; it is an operating procedure that produces a useful artifact a human can verify.

## Market view

AI configuration formats—skills, projects, rules, modes, assistants, MCP integrations, and agent frameworks—address a common need: portable task context and reliable procedures. Most repositories optimize for collection size or novelty. OutcomeLab optimizes for evidence, evaluation, safety, and upkeep.

### Ecosystem snapshot (2026-06-22)

The figures below are public GitHub discovery snapshots, not growth rates or quality scores. See [RESEARCH.md](RESEARCH.md) for method and limitations.

| Repository | Category | Stars | Strategic lesson |
| --- | --- | ---: | --- |
| [f/prompts.chat](https://github.com/f/prompts.chat) | Prompt collection | 164,067 | Breadth and a contribution flywheel attract attention. |
| [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) | MCP directory | 89,577 | Fast-moving ecosystems need discovery and maintenance. |
| [ComposioHQ/awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) | Skill directory | 65,479 | Skills have demand; a single-vendor brand narrows durability. |
| [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | Agent tooling directory | 47,003 | Curated integration points drive repeat visits. |
| [PatrickJS/awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) | Editor-rule collection | 40,055 | Concrete copy-paste artifacts are highly shareable. |

GitHub search does not provide reliable historical stars for all projects. Do not make a growth-rate claim until a versioned time series exists.

## Gap and opportunity ranking

| Opportunity | Score /100 | Rationale |
| --- | ---: | --- |
| Security and release-risk reviews | 91 | High consequence, repeatable artifacts, clear verification. |
| Architecture and technical-debt decisions | 89 | Persistent pain; benefits from explicit trade-offs. |
| Cost and AI-spend controls | 86 | Clear unit economics and measurable guardrails. |
| CTO operating reviews | 84 | Connects engineering signals to executive decisions. |
| Startup validation and competitive intelligence | 80 | Broad demand; evidence discipline is scarce. |
| Search and SEO operations | 74 | Valuable, but attribution is difficult and platforms change. |

Score = demand (25%) + repeat use (20%) + decision consequence (20%) + evidence availability (15%) + shareability (10%) + execution feasibility (10%). These are prioritization hypotheses to test with users, not market facts.

## Moat and repository design

The defensible asset is a public corpus of difficult, consented evaluation cases, scored outputs, and improvement history—not the text of an individual prompt. Keep source skills in plain Markdown, adapters thin, and platform-specific policy outside the skill. Every merge should strengthen the corpus or the operating standard.

Naming uses lower-case hyphenated folders. Version the repository semantically; version any behavior-changing skill explicitly in its changelog or release notes. Require an owner, review cadence, and an evaluation case before a skill is promoted beyond experimental status. Deprecate stale procedures visibly instead of silently letting them drift.

## Compatibility

The durable compatibility contract is a task-specific Markdown file that works in any agent context. Native adapters are convenience layers, not canonical formats. See [COMPATIBILITY.md](COMPATIBILITY.md).

## Self-critique and risk register

| Failure mode | Why it matters | Mitigation |
| --- | --- | --- |
| Generic-content sprawl | Catalog size can erase trust | Require a decision problem, owner, and scored case. |
| Weak benchmark claims | A polished demo can mislead | Publish cases, controls, budgets, limitations, and raw scores. |
| Model or vendor churn | Surface-specific formats age quickly | Keep Markdown source and test adapters separately. |
| Unsafe high-stakes advice | Security and production mistakes have real cost | Scope limits, safe fixtures, human review, and explicit authorization. |
| Maintainer burnout | Curation is work, not a one-time launch | Small catalog, clear ownership, review cadence, deprecation. |
| Growth without retention | Stars do not prove usefulness | Measure reruns, case submissions, and decisions changed. |
| Monetization pressure | Sponsorship can distort the corpus | Disclose conflicts; keep evaluation criteria public and independent. |

## Twelve-month roadmap

### Q1 — prove usefulness

Publish the first ten skills, compatibility guidance, CI validation, and three sanitized cases for high-risk workflows. Seek twenty useful external issue reports or PRs, not a vanity metric.

### Q2 — earn trust

Publish versioned baseline-vs-skill results, recruit domain maintainers, and add tested adapters for the highest-demand agent surfaces.

### Q3 — compound the corpus

Release an evaluation runner, establish a privacy policy for submitted cases, and publish case studies that show an engineering decision changed.

### Q4 — scale responsibly

Create a maintainer council, enforce semantic release/deprecation policy, and repeat narrowly targeted community launches based on demonstrated value.
