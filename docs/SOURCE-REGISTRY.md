# OutcomeLab source registry

References checked November 6, 2026. These sources describe platform behavior. They do not attest to OutcomeLab results.

| Source | Use |
| --- | --- |
| [OWASP Webhook Security](https://cheatsheetseries.owasp.org/cheatsheets/Webhook_Security_Cheat_Sheet.html) and [Stripe idempotency](https://stripe.com/blog/idempotency) | Duplicate delivery and downstream idempotent effects |
| [RFC 6750](https://www.rfc-editor.org/rfc/rfc6750) | Bearer header and credential handling. OutcomeLab limits plaintext to disposable loopback tests. |
| [OWASP API Security Top 10, 2023](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization/) | Object-level access checks for future authorization cases |
| [Stripe webhooks](https://docs.stripe.com/webhooks) and [Supabase platform webhooks](https://supabase.com/docs/guides/platform/webhooks) | Provider documentation for event delivery and duplicate handling |
| [Playwright best practices](https://playwright.dev/docs/best-practices) | Browser and user-visible behavior checks |
| [Android core app quality](https://developer.android.com/docs/quality-guidelines/core-app-quality) | Platform quality requirements for native checks |
| [Apple XCTest](https://developer.apple.com/documentation/xctest/) | Native test reference. The HTML page required JavaScript in this review. |
| [GitHub Actions security](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target) | Privileged PR trigger risks |
| [OpenAI skills](https://learn.chatgpt.com/docs/build-skills) | Skill structure and setup |

Record the official source URL, version or retrieval date, and the claim it supports. Record conflicting guidance or inaccessible sources. Treat current platform behavior as unverified when the relevant source cannot be checked.

## Tool boundaries

OutcomeLab runs a predeclared local HTTP state check. proofcheck covers PR evidence, [Schemathesis](https://schemathesis.readthedocs.io/en/stable/explanations/stateful/) covers schema-based and linked API testing, Keploy covers traffic capture and replay, [Pact](https://docs.pact.io/consumer) covers consumer/provider contracts, pgTAP covers PostgreSQL assertions, and Playwright covers browser behavior. Each can be used alongside an OutcomeLab check.
