---
phase: 25-smtp-provider-core-config
plan: 01
subsystem: otp-mail
tags: [otp, smtp, config]

requires:
  - phase: 24-otp-qa-reliability-gate
    provides: Stable OTP auth/session behavior preserved while the provider core changes underneath
provides:
  - SMTP config contract in Config
  - Flask-Mail-backed SMTP provider branch for OTP delivery
  - Updated technical architecture doc for provider-selected OTP transport
affects: [25-02, 26-01, 26-02]

tech-stack:
  added: []
  patterns: [Provider-neutral SMTP_* config with derived MAIL_* settings, normalized provider boundary in otp_email_delivery]

key-files:
  created: []
  modified: [config.py, services/otp_email_delivery.py, documents/docs/technical/ARCHITECTURE.md]

key-decisions:
  - "EMAIL_PROVIDER remains the selector, but smtp is now a supported production path beside resend_api."
  - "Flask-Mail is reused as the SMTP transport via derived MAIL_* config instead of introducing a new mail library."
  - "SMTP config validation rejects conflicting TLS and SSL flags before any send attempt."

patterns-established:
  - "Provider-specific config validation should happen inside the OTP delivery boundary before transport calls."
  - "Auth routes continue to depend only on normalized send results, not provider exceptions."

requirements-completed: [SMTPP-01, SMTPP-02, SMTPP-03, SMTPO-01]

duration: 35min
completed: 2026-04-17
---

# Phase 25 Plan 01 Summary

Implemented the SMTP provider core and config contract for the OTP mail pivot.

## Accomplishments

- Extended `config.py` with provider-neutral `SMTP_*` settings, derived Flask-Mail `MAIL_*` settings, and provider-aware readiness helpers.
- Added a Flask-Mail-backed SMTP send branch in `services/otp_email_delivery.py` while keeping the existing Resend branch intact.
- Normalized SMTP send outcomes into the existing `sent`, `misconfigured`, `provider_rejected`, `timeout`, and `network_error` contract.
- Updated `documents/docs/technical/ARCHITECTURE.md` so the OTP delivery layer is described as a config-selected provider boundary.

## Task Commits

No git commit was created in this workspace session.

## Verification

- `python -m pytest tests/test_otp_email_delivery.py -q`
- `python -m pytest tests/test_otp_auth_integration.py -q`

## Self-Check: PASSED