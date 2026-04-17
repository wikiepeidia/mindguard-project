---
phase: 26-auth-flow-smtp-cutover
plan: 01
subsystem: otp-auth
tags: [otp, smtp, auth, regression]

requires:
  - phase: 25-smtp-provider-core-config
    provides: SMTP provider boundary and normalized delivery categories reused by auth routes
provides:
  - Structured operator diagnostics for SMTP delivery failures in auth routes
  - SMTP-path register/resend integration coverage at the real provider boundary
affects: [26-02, 27-01, 27-02]

tech-stack:
  added: []
  patterns: [Route-level provider diagnostics, SMTP-path integration tests via patched Flask-Mail transport]

key-files:
  created: []
  modified: [routes/auth.py, tests/test_otp_auth_integration.py]

key-decisions:
  - "Auth routes remain transport-agnostic and continue to call send_otp_email instead of embedding SMTP logic."
  - "SMTP route coverage patches services.otp_email_delivery.mail.send so tests hit the actual provider-selection branch."
  - "Operator diagnostics log provider, provider_hint, category, and missing config keys without exposing secrets."

patterns-established:
  - "When a new OTP provider is introduced, route tests should target the provider boundary instead of mocking the route wrapper."
  - "Auth delivery failures should preserve user-facing fail-closed UX while adding structured logs for operators."

requirements-completed: [SMTPC-01, SMTPC-02, SMTPC-03, SMTPQ-02]

duration: 30min
completed: 2026-04-17
---

# Phase 26 Plan 01 Summary

Completed the SMTP auth-flow cutover at the register and resend entrypoints.

## Accomplishments

- Added structured OTP delivery failure logs in `routes/auth.py` so operators can distinguish SMTP misconfiguration from transient runtime failures.
- Kept register/resend fail-closed behavior intact while preserving the existing user-facing flash flow.
- Expanded `tests/test_otp_auth_integration.py` with SMTP-path register/resend success and failure cases by patching the Flask-Mail transport directly.
- Proved the resend/session challenge contract remains intact on SMTP timeout and misconfiguration branches.

## Task Commits

No git commit was created in this workspace session.

## Verification

- `python -m pytest tests/test_otp_auth_integration.py -q`
- `python -m pytest tests/test_otp_email_delivery.py tests/test_otp_auth_integration.py -q`

## Self-Check: PASSED
