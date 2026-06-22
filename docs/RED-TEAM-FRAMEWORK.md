# Red-team framework

Titan should attack its own outputs before users do.

## Red-team questions

Ask these before publishing a skill output, benchmark, case study, or claim:

1. Why will this fail in the real world?
2. Why would users not care?
3. Which assumption is doing the most hidden work?
4. What evidence is missing?
5. What would a senior engineer reject?
6. What would a CTO reject?
7. What would a founder reject?
8. What would a security auditor reject?
9. What would an end user reject?
10. What could be misused, over-applied, or misread?

## Required red-team output

Use this structure:

```text
Weaknesses first:
- ...

Risk severity:
- Critical:
- High:
- Medium:
- Low:

Mitigations:
- ...

Residual risk:
- ...

Decision:
- Ship / revise / reject
```

## Rejection triggers

Reject or revise the artifact when it:

- makes a claim without evidence;
- hides uncertainty;
- gives a high-stakes recommendation without review gates;
- uses a generic checklist instead of task-specific analysis;
- cannot explain how success will be measured;
- adds complexity without improving the user's outcome.
