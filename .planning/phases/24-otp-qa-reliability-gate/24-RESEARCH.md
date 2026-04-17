# Phase 24: OTP QA Reliability Gate - Research

**Date:** 2026-04-17  
**Discovery Level:** Level 0 (existing patterns only)  
**Status:** Applied

## Why Level 0

Phase 24 did not require a new library, architecture choice, or external integration. The remaining work was gap-closing test coverage on top of the OTP behavior established in Phases 20 through 23.

## Findings

### Current coverage was already strong in three areas

- `tests/test_otp_security.py` already covered core OTP verification outcomes such as valid, invalid, expired, and locked submissions.
- `tests/test_otp_email_delivery.py` already covered provider contract behavior for test mode and fail-closed email delivery.
- `tests/test_otp_auth_integration.py` already covered register/verify happy paths and major resend/session guardrails from earlier phases.

### The Phase 24 gaps were narrow and specific

- No dedicated helper-level test file existed for resend cooldown logic and resend window-cap enforcement.
- No explicit resend integration test proved the auth flow rolls back cleanly when `send_otp_email()` fails during `/verify-otp/resend`.
- No explicit integration test proved that two concurrent verify submissions cannot both succeed against the same pending challenge.

### Existing implementation already exposed the right seams

- `utils/otp_security.py` provides `get_resend_otp_policy`, `prepare_resend_otp_challenge`, and `activate_replacement_otp_challenge`, which are stable seams for helper-level coverage.
- `routes/auth.py` already routes resend and verify through persisted `OtpChallenge` rows and session-backed pending state, which supports deterministic integration tests with two clients.

## Applied Approach

1. Add a focused resend-policy unit file instead of enlarging `tests/test_otp_security.py` further.
2. Extend `tests/test_otp_auth_integration.py` with resend failure rollback and concurrent verify single-success coverage.
3. Validate with focused commands first, then run the broader OTP regression gate.

## Risks Left Intentionally Out of Scope

- `datetime.utcnow()` deprecation warnings remain throughout the codebase and tests.
- Flask-Limiter continues to emit expected in-memory backend warnings in tests.
- Live Resend dashboard verification still depends on setting `RESEND_FROM_EMAIL` in the runtime environment.
