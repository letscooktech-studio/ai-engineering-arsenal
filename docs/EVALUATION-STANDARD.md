# Titan Evaluation Standard

Titan outputs are scored on evidence, not style. The score should punish confident unsupported answers and reward calibrated, verifiable work.

## Scorecard

Each dimension is scored 0-10.

| Dimension | Weight | What earns a high score |
| --- | ---: | --- |
| Accuracy | 12 | Claims match the provided artifacts and current reliable sources. |
| Evidence | 12 | Important claims are grounded in cited files, data, logs, or sources. |
| Verification | 12 | Recommendations include tests, checks, measurements, or review gates. |
| Actionability | 10 | A user can execute the next steps without guessing. |
| Security | 10 | Trust boundaries, abuse paths, secrets, privacy, and permissions are handled. |
| Scalability | 8 | The answer considers growth, load, maintainability, and operational reality. |
| Maintainability | 8 | The proposed path is understandable, evolvable, and low-friction to operate. |
| Completeness | 8 | The output covers the task without padding or major omissions. |
| Risk awareness | 8 | Failure modes and assumptions are explicit. |
| Business impact | 6 | The answer connects technical work to cost, revenue, speed, or risk. |
| User value | 6 | The answer improves the user's real decision or outcome. |

Weighted total:

```text
sum(score * weight) / 10
```

Maximum score: 100.

## Confidence and uncertainty

Every evaluated output should include:

- confidence: high, medium, low;
- uncertainty drivers: missing artifacts, stale sources, unclear scope, untested assumptions;
- reviewer notes: why the score may be wrong;
- required follow-up: the smallest action that would increase confidence.

## Benchmark comparison rule

A Titan result only beats a default AI result when it improves the weighted total without creating unacceptable safety, accuracy, or maintenance regressions. Publish losses and ties. They are part of the improvement loop.
