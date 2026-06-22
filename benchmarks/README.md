# Benchmarks

This directory is where Titan earns claims. A case study shows how a playbook behaves; a benchmark compares it with a baseline under controlled conditions. Do not treat an illustrative case study as performance evidence.

## Run protocol

For each case, run the same model/version, tools, system context, temperature, token budget, input artifact, and output budget twice: once with a minimal direct task (baseline), then with the Titan skill. Preserve raw outputs. Have an independent evaluator score them blind against the task rubric.

Publish the run date, provider/model, all controls, raw scores, evaluator agreement, cost, latency, limitations, and negative results. Do not pool different models or change the task between runs.

## Required result table

| Dimension | Baseline | Titan | Notes |
| --- | ---: | ---: | --- |
| Evidence fidelity |  |  |  |
| Decision usefulness |  |  |  |
| Risk handling |  |  |  |
| Verification |  |  |  |
| Calibration |  |  |  |
| Efficiency |  |  |  |

No cells may be filled until the underlying output and evaluator notes are committed or linked. See [docs/BENCHMARKS.md](../docs/BENCHMARKS.md) for the shared scoring contract.

