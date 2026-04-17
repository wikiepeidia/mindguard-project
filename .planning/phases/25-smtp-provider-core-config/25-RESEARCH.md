# Phase 25: SMTP Provider Core & Config - Research

**Date:** 2026-04-17  
**Discovery Level:** Level 0 with quick source verification  
**Status:** Applied

## Why Level 0

Phase 25 reuses libraries and patterns already present in the repo:

- `Flask-Mail==0.9.1` is already installed.
- `extensions.py` already initializes `Mail()`.
- `services/otp_email_delivery.py` already normalizes provider outcomes.

No new dependency or external architecture choice was required.

## Findings

### Existing provider boundary is already in the right place

- `services/otp_email_delivery.py` is the single delivery seam used by auth routes.
- `routes/auth.py` already invalidates or preserves OTP state based on the normalized `send_otp_email()` result rather than provider-specific exceptions.

### SMTP config is missing in the current codebase

- `config.py` currently exposes only Resend OTP config.
- Flask-Mail is initialized, but no explicit SMTP contract exists for provider-host, auth, TLS/SSL, or sender readiness.

### Flask-Mail supports the needed transport shape

- The installed package initializes from `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_USE_TLS`, `MAIL_USE_SSL`, and `MAIL_DEFAULT_SENDER`.
- The library does not expose its own timeout config key in 0.9.1, so timeout remains a normalized runtime outcome rather than a dedicated Flask-Mail setting.

## Applied Approach

1. Add provider-neutral `SMTP_*` config keys and derive compatible `MAIL_*` settings from them.
2. Extend `otp_email_delivery_status()` to validate both `resend_api` and `smtp` providers.
3. Add an SMTP send branch that reuses Flask-Mail `Message` objects and normalizes SMTP exceptions into the existing result contract.
4. Expand `tests/test_otp_email_delivery.py` with SMTP readiness and outcome coverage.
5. Refresh the technical architecture doc so the provider boundary is documented.

## Risks Left Intentionally Out of Scope

- Operator-facing Gmail App Password checklists and readiness diagnostics stay in Phase 26.
- Production mailbox smoke on Vercel stays in Phase 27.
- Resend decommissioning is deferred until the SMTP path is proven and cut over.
