# Start here — reproduce the first Arsenal risk scenarios

**You can try the runnable demo without creating an account, installing a coding agent, entering API keys, or starting a database server.**

## 1. Run the actual release

Prerequisite: Python 3.11+ and Git.

```sh
git clone https://github.com/letscooktech-studio/ai-engineering-arsenal.git
cd ai-engineering-arsenal
git checkout v0.1.0
python -m risk_lab
```

Expected output:

```text
invoice-persistence: DEMONSTRATED (broken=FAIL, fixed=PASS)
webhook-idempotency: DEMONSTRATED (broken=FAIL, fixed=PASS)
```

On a clean checkout this typically runs without extra packages. If anything differs, **that's a useful bug report**.

## 2. Inspect what was actually checked

```sh
python -m risk_lab --json
python -m unittest discover -s tests -v
python scripts/validate.py
git rev-parse HEAD
```

`invoice-persistence` tests a rolled-back SQLite write against a committed write after reopening the DB connection. `webhook-idempotency` tests a duplicate event that incorrectly credits twice versus one recorded effect under a unique event key.

**Important:** This only proves two controlled synthetic fixtures behave as designed. It does *not* verify a real application, an actual payment provider, a browser workflow, or AI coding-agent superiority.

## 3. Use it with your coding agent

Review [the Production Risk Lab skill](../skills/production-risk-lab/SKILL.md) and copy its directory into the skills location supported by your current Codex, Claude Code or other compatible agent version. Agents can use the skill to formulate testable production-risk invariants and explain the executable examples.

The skill does **not** automatically install global hooks, run third-party project code, or grant a coding agent browser/web access.

## 4. Send genuinely useful feedback

- [Independent reproducibility issue](https://github.com/letscooktech-studio/ai-engineering-arsenal/issues/3) — platform, Python version, commands, observed result, unclear setup or failures.
- [Contributor scenario proposal](https://github.com/letscooktech-studio/ai-engineering-arsenal/issues/4) — a falsifiable new failure invariant and positive/negative controls.
- [Security policy](../SECURITY.md) — use private channels for secrets or vulnerability reports, never paste sensitive information into public issues.

Maintainers are especially interested in **counterexamples and limitations**, not only success reports. Stars are appreciated but aren't considered evidence that the tool works for external users.
