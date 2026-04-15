---
phase: 21-production-otp-email-delivery
plan: 02
subsystem: auth
tags: [otp, auth, resend, fail-closed]

requires:
  - phase: 21-production-otp-email-delivery
    provides: Resend config contract and delivery service
provides:
  - Register flow integration with send_otp_email
  - Fail-closed handling on delivery failures
  - Clear verify-page user guidance for production OTP flow

affects: [21-03, 22]

tech-stack:
  added: []
  patterns: [Fail-closed registration gate, service-driven email delivery]

key-files:
  created: []
  modified: [routes/auth.py, templates/verify_otp.html, services/otp_email_delivery.py]

key-decisions:
  - "Register flow only proceeds to verify page when send_otp_email returns ok=true."
  - "On delivery failure, issued challenge is invalidated and pending registration session is cleared."
  - "Testing mode uses deterministic delivery behavior to keep route tests network-free."

patterns-established:
  - "Auth route delegates provider behavior to service and maps normalized categories to UX-safe messages."

requirements-completed: [OTPMAIL-01, OTPMAIL-02]

duration: 20min
completed: 2026-04-15
---

# Phase 21 Plan 02 Summary

Integrated Resend delivery into registration and enforced fail-closed account activation behavior.

## Accomplishments

- Updated register flow in routes/auth.py to call send_otp_email immediately after challenge issuance.
- Added fail-closed branch:
  - invalidates challenge on send failure,
  - clears pending registration session state,
  - redirects back to register with clear Vietnamese retry guidance.
- Updated verify template copy to clarify what users should do when email is delayed.
- Added deterministic TESTING behavior in delivery service to avoid external network dependency during route tests.

## Task Commit

- Combined implementation commit: `e5099d8`

## Verification

- `python -m py_compile routes/auth.py services/otp_email_delivery.py`
- `python -m pytest tests/test_otp_auth_integration.py -k "register"`

## Self-Check: PASSED
