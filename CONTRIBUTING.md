# Contributing

Developed by the LetsCookTech Open Source Team.

Open an issue before a large skill so the problem, user, evidence sources, and evaluation case are clear. Keep pull requests narrow.

## A skill must

1. Solve a recurring, decision-relevant problem.
2. Have a hyphen-case folder and valid `SKILL.md` frontmatter.
3. Specify intake, workflow, output contract, quality gates, and improvement loop; comply with the [skill standard](docs/SKILL-STANDARD.md).
4. Separate verified facts from assumptions and define safe limits.
5. Include or link an evaluation case before it is promoted beyond experimental status.

Do not contribute generic personas, model-specific marketing, copied proprietary material, unverifiable claims, or instructions that enable unauthorized harm.

Run the bundled skill validator against any changed skill before submitting it.

## Production Risk Lab scenarios

Before adding a scenario, explain a concrete user-facing invariant and share a sanitized negative reproduction. Use the [scenario issue template](.github/ISSUE_TEMPLATE/reproducible-scenario.yml). Keep broken and corrected fixtures and a shared, falsifiable test oracle. Run `python -m risk_lab`, `python -m unittest discover -s tests -v`, and `python scripts/validate.py`. We welcome failure reports and tests that show where the current framework is misleading.
