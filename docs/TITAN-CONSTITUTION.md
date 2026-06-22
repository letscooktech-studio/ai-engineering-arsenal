# Titan OS constitution

Titan exists to help AI systems catch important things normal AI misses. Every contribution must increase trust, repeatability, or measurable user value.

## Laws

1. Every skill must solve a real recurring problem.
2. Every recommendation must be measurable or explicitly marked as judgment.
3. Every output must separate facts, evidence, assumptions, estimates, and decisions.
4. Every workflow must include verification.
5. Every workflow must expose risks before final recommendations.
6. Every benchmark claim must include baseline output, Titan output, evaluator criteria, model details, and limitations.
7. Every skill must define what a good result looks like before producing the result.
8. Every skill must know when to stop because evidence is insufficient.
9. Every contribution must reduce user burden, not shift ambiguity onto the user.
10. Every public example must be safe, authorized, and labeled as synthetic or real.
11. Every new abstraction must earn its place by improving actionability, evaluation, or reuse.
12. Every skill must challenge at least one assumption that a default assistant would likely accept.
13. Every high-stakes output must name the human owner who should review it.
14. Every failure should feed the improvement loop.
15. No file should exist only to make the repository look larger.

## Maintainer decision test

Before accepting a change, ask:

- Does this help a user make a better real-world decision?
- Can the value be observed or scored?
- Does it reduce hallucination, blind confidence, or missed risk?
- Would a senior engineer, CTO, founder, or security reviewer respect the artifact?
- Does it improve the reputation: "Titan catches things normal AI misses"?

If the answer is no, reject or rewrite the change.
