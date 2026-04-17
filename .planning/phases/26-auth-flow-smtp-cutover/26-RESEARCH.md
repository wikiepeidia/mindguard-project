# Phase 26: Auth Flow SMTP Cutover - Research

**Date:** 2026-04-17  
**Discovery Level:** Level 0  
**Status:** Applied

## Why Level 0

Phase 26 does not introduce a new dependency or a new provider. It wires the SMTP path from Phase 25 into the existing auth routes and adds route-level regression evidence plus operator guidance.

## Findings

### Auth routes were already mostly ready for the cutover

- `/register` and `/verify-otp/resend` already delegate all mail delivery to `send_otp_email()`.
- Route logic already preserves or invalidates OTP challenge/session state based on normalized delivery outcomes.

### The missing proof was SMTP-specific route coverage

- Existing auth integration tests patch `routes.auth.send_otp_email`, which proves route behavior but not the actual SMTP branch selected by config.
- The Phase 26 gap is to run those routes with `EMAIL_PROVIDER=smtp` and patch the underlying Flask-Mail transport instead.

### Operator guidance was missing in the repo

- `TODO.mD` was empty.
- The user explicitly asked for free SMTP setup guidance, so the repo needed a concrete Gmail App Password runbook with env vars and a failure-category matrix.

## Applied Approach

1. Add structured route logging for OTP delivery failures, keyed by flow name and provider category.
2. Add SMTP-path auth integration tests by patching `services.otp_email_delivery.mail.send` directly.
3. Capture the free Gmail App Password setup and failure-category guidance in `TODO.mD`.

## Risks Left Intentionally Out of Scope

- Live production SMTP verification on Vercel.
- Final release evidence and screenshots.
- Large-volume deliverability tuning.
