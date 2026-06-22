# Titan self-evolution roadmap

Titan should improve through scored failures, not prompt inflation.

## Current weaknesses

- Too few public before/after results.
- Synthetic examples may be mistaken for real audits if labels are weak.
- Skill quality is uneven until every skill has proof-pack artifacts.
- External market data must be refreshed before launches.
- No automated evaluator yet.

## Future weaknesses

- Category confusion if "OS" implies runtime capabilities before they exist.
- Contributor quality may drop if templates encourage filler.
- Competitors may add benchmarks faster.
- Model improvements may reduce perceived need unless Titan focuses on verification and operating discipline.

## V3: Proof engine

Goal: make Titan visibly better than default AI on tier-one tasks.

- Add baseline/Titan output pairs for four tier-one skills.
- Add expected finding inventories for eval cases.
- Add a scoring script that produces weighted totals.
- Add benchmark submission issue template.
- Publish first release with transparent wins, losses, and limitations.

## V4: Runtime adapters

Goal: make Titan easy to use across tools.

- Add adapter docs for Codex, Claude, ChatGPT, Cursor, Windsurf, Cline, Roo Code, Aider, and agent SDKs.
- Add machine-readable skill manifests.
- Add routing guidance: which skill to use for which task.
- Add permission and safety policies for tool-using agents.

## V5: Open Source AI CTO

Goal: move from playbook library to operating system.

- Add skill router.
- Add evaluation runner.
- Add policy gates.
- Add contribution leaderboard for benchmarked improvements.
- Add community-maintained case studies.
- Add release-quality dashboards.

## Adoption risk controls

- Lead with before/after proof.
- Keep the first-run path under five minutes.
- Avoid model-specific branding.
- Focus tier-one skills before expanding.
- Make every roadmap item produce a user-visible artifact.
