# Phase 25: SMTP Provider Core & Config - Context

**Gathered:** 2026-04-17  
**Status:** Ready for planning and execution  
**Mode:** Autonomous single-phase execution

<domain>
## Phase Boundary

Implement the generic SMTP provider core for OTP delivery so MindGuard can send OTP mail on Vercel without depending on Resend custom-domain verification.

This phase is limited to provider/core concerns:

- config contract for SMTP host, port, auth, TLS/SSL, and sender
- provider selection through `EMAIL_PROVIDER`
- SMTP send adapter inside `services/otp_email_delivery.py`
- normalized provider outcomes and fail-closed behavior
- unit coverage for SMTP config validation and delivery result mapping

This phase does not expand route UX, readiness UI, or production smoke steps. Those stay in Phases 26 and 27.

</domain>

<decisions>
## Decisions

### Locked Decisions

- **D-01:** Replace the blocked Resend-only path with a generic `smtp` provider that works on Vercel without a custom sending domain.
- **D-02:** Reuse the existing Flask-Mail extension and keep transport selection behind `services/otp_email_delivery.py`; auth routes should stay transport-agnostic.
- **D-03:** Keep `EMAIL_PROVIDER` as the provider selector and add an env-driven SMTP contract: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_USE_TLS`, `SMTP_USE_SSL`, `SMTP_FROM_EMAIL`.
- **D-04:** Fail closed when SMTP sender or credentials are wrong. Delivery failure must not silently advance OTP state.
- **D-05:** Environment variables remain the production source of truth; local JSON fallback may exist only as a secondary local-development convenience.

### the agent's Discretion

- Exact exception-to-category mapping for SMTP transport failures, as long as `misconfigured`, `timeout`, `provider_rejected`, and `network_error` remain distinguishable.
- Whether to expose the SMTP contract through provider-neutral keys only or also derive Flask-Mail `MAIL_*` keys for compatibility.

</decisions>

<code_context>
## Existing Code Insights

- `services/otp_email_delivery.py` currently supports only `resend_api` and already owns normalized delivery results.
- `extensions.py` and `app.py` already initialize `mail = Mail()` and `mail.init_app(app)`.
- `config.py` currently defines only Resend OTP mail config and readiness helpers.
- `routes/auth.py` already fails closed when `send_otp_email()` returns `ok=False`, so provider-level failure handling must preserve that contract.
- `tests/test_otp_email_delivery.py` is the focused unit suite for delivery-provider behavior.

</code_context>

<specifics>
## Specific Ideas

- Derive Flask-Mail `MAIL_*` settings from the new `SMTP_*` keys so the extension can stay the transport implementation.
- Treat `SMTP_USE_TLS` and `SMTP_USE_SSL` both set to true as misconfiguration.
- Keep the SMTP path injectable in tests via the existing `transport` parameter instead of needing a live SMTP server.

</specifics>

<deferred>
## Deferred Ideas

- Multi-provider failover or automatic fallback from Resend to SMTP.
- Route-level SMTP regression expansion.
- Production mailbox smoke and operator runbook work.

</deferred>
