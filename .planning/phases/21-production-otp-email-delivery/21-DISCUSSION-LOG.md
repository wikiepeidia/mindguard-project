# Phase 21: Production OTP Email Delivery - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md.

**Date:** 2026-04-15
**Phase:** 21-production-otp-email-delivery
**Areas discussed:** Provider path, failure UX, runtime secrets contract, OTP email content
**Mode:** Fast-continue (user requested to continue quickly)

---

## Provider path

| Option | Description | Selected |
|--------|-------------|----------|
| Google SMTP + App Password | Quickest production path with existing Flask-Mail wiring | ✓ |
| API provider (Resend/SendGrid) | Better long-term abstraction, but needs extra wiring now | |
| Keep demo/no real send | Violates Phase 21 goals | |

**User's choice:** Continue quickly with pragmatic default path.
**Notes:** Selected Google SMTP + App Password as phase baseline.

---

## Failure handling UX

| Option | Description | Selected |
|--------|-------------|----------|
| Fail closed + clear retry guidance | No account activation on send failure, user gets clear next step | ✓ |
| Silent pass-through | Risky and confusing for user | |
| Hard fail with technical details | Leaks internals, poor UX | |

**User's choice:** Continue with secure default.
**Notes:** Keep guidance user-friendly and non-technical.

---

## Runtime secrets contract

| Option | Description | Selected |
|--------|-------------|----------|
| Env-only MAIL_* credentials | Matches milestone constraints and production safety | ✓ |
| JSON fallback for production credentials | Increases secret risk and config drift | |
| Hardcoded fallback credentials | Disallowed | |

**User's choice:** Continue with secure default.
**Notes:** Enforce `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`.

---

## OTP email content contract

| Option | Description | Selected |
|--------|-------------|----------|
| Plain-text required + TTL + anti-phishing note | Fast to ship and sufficient for phase goal | ✓ |
| HTML-only complex template | More polish, not required for this phase | |
| Minimal OTP only (no guidance) | Lower user safety clarity | |

**User's choice:** Continue with practical default.
**Notes:** HTML can be optional if implementation remains simple.

---

## the agent's Discretion

- Subject line naming and detailed phrasing of OTP email.
- Service/module file placement for mail sender abstraction.
- Logging granularity that avoids plaintext OTP exposure.

## Deferred Ideas

- Multi-provider failover and outage queue handling.
- Resend cooldown UX and resend endpoint contract.
- OTP abuse guardrails and full OTP QA gate.
