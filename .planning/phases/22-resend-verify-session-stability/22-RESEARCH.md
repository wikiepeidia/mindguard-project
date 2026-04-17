---
phase: 22-resend-verify-session-stability
status: complete
created: 2026-04-17
source: manual-fallback-research
---

# Phase 22 Research - Resend & Verify Session Stability

## Scope

Phase 22 must satisfy only these requirement IDs:

- OTPRES-01
- OTPRES-02
- OTPSES-01

Out of phase for this plan set:

- OTPOUT-* outage continuity and retry queue behavior
- OTPREL-* route-level abuse guardrails and telemetry coupling
- OTPQA-* broad OTP reliability matrix and concurrency stress coverage

## Codebase Findings (Current State)

1. Verify-page refresh is not yet session-aware on GET.

- routes/auth.py only validates `pending_registration` and `pending_otp_challenge_id` during POST `/verify-otp`
- GET `/verify-otp` always renders the template, even when pending state is gone or the referenced challenge is expired/invalid

2. There is no resend path from the verify flow.

- templates/verify_otp.html tells the user to go back to register if email is delayed
- routes/auth.py has no dedicated resend endpoint and no resend cooldown/cap policy

3. Existing challenge issuance is correct for replacement semantics, but not yet safe for resend failure handling.

- utils/otp_security.py `issue_otp_challenge()` invalidates prior active challenges immediately
- that behavior is fine for initial register and for successful resend replacement
- for resend, using it before delivery succeeds would strand the user if the new email fails to send and the old active challenge has already been invalidated

4. Phase 21 already established a reusable delivery contract.

- services/otp_email_delivery.py returns normalized `ok/category/message/provider_message_id`
- tests can patch `routes.auth.send_otp_email` and keep delivery deterministic with no real network dependency

5. Test coverage exists for register/verify basics, but not for resend/session stability.

- tests/test_otp_auth_integration.py covers register send success/failure and core verify lifecycle behavior
- tests/test_csrf_and_routes.py covers POST `/verify-otp` CSRF enforcement, but no resend endpoint exists yet

## Standard Stack (Use Existing Libraries)

- Existing Flask blueprints and server-side session handling in `routes/auth.py`
- Existing SQLAlchemy `OtpChallenge` model and `db.session`
- Existing OTP helper primitives in `utils/otp_security.py`
- Existing Phase 21 mail delivery service in `services/otp_email_delivery.py`
- Existing unittest + pytest hybrid test setup in `tests/`
- No new dependency required

## Architecture Patterns to Apply

1. Dedicated resend POST route bound to the current verify session

- add POST `/verify-otp/resend`
- require `pending_registration`, `pending_otp_challenge_id`, and `pending_verification_email`
- keep the user inside the verify flow rather than sending them back through `/register`

2. Success-gated replacement challenge swap

- resend must create a fresh OTP challenge only after resend policy allows it
- the current active challenge should remain usable until the replacement send succeeds
- once delivery succeeds, invalidate the previous active challenge, persist the new one, and update `session['pending_otp_challenge_id']`
- if resend delivery fails, keep the pending registration session intact and do not force the user to restart registration

3. Server-side resend policy driven by existing challenge timestamps

- add config-backed resend controls in `config.py`
- recommended defaults:
  - `OTP_RESEND_COOLDOWN_SECONDS = 60`
  - `OTP_RESEND_WINDOW_SECONDS = 900`
  - `OTP_RESEND_MAX_PER_WINDOW = 3`
- derive cooldown and per-window cap from `OtpChallenge.issued_at` history for the same `email` + `purpose='register'`
- do not rely on client-side countdown alone for enforcement

4. GET `/verify-otp` should validate pending state before rendering

- if `pending_registration` is missing: redirect to `/register` with Vietnamese guidance
- if referenced challenge is missing or expired: clear pending OTP session keys and redirect safely to `/register`
- if referenced challenge is active or locked-but-still-pending: render the verify page and keep the session stable on refresh

5. Minimal UI changes only

- keep the existing OTP input and verify submit path
- add a small resend form/button plus explicit Vietnamese wait-state message
- do not introduce a new OTP interaction pattern such as split inputs or JavaScript-only timers

## Recommended File-Level Implementation

- `config.py`
  - add resend-policy keys with env-backed defaults
- `utils/otp_security.py`
  - add resend eligibility helper(s) that calculate cooldown remaining and cap denial
  - add helper(s) for generating/persisting replacement challenges without invalidating the existing active challenge before resend success
- `routes/auth.py`
  - validate pending state on GET `/verify-otp`
  - add POST `/verify-otp/resend`
  - update session challenge id only after resend success
- `templates/verify_otp.html`
  - add minimal resend affordance and visible cooldown/cap status text

## Common Pitfalls to Avoid

- Reusing `issue_otp_challenge()` directly for resend before delivery succeeds
- Clearing `pending_registration` on resend failure and forcing the user back through the full register form
- Enforcing cooldown only in the template instead of on the server
- Forgetting CSRF protection on the new resend POST endpoint
- Redirecting on every non-active challenge state even when the flow should remain recoverable and resend-able

## Validation Architecture

- Test framework: pytest + unittest hybrid already present in repo
- Quick command: `python -m pytest tests/test_otp_auth_integration.py -k "resend or verify"`
- Full command: `python -m pytest tests/test_otp_auth_integration.py tests/test_csrf_and_routes.py -k "resend or verify_otp or register"`
- Required checks:
  - GET `/verify-otp` renders only when pending session + valid pending challenge still exist
  - missing session or expired challenge redirects safely to `/register`
  - POST `/verify-otp/resend` succeeds without re-submitting the register form
  - resend cooldown and cap deny replacement without changing the current pending challenge id
  - resend success invalidates the previous active challenge and updates `pending_otp_challenge_id`
  - resend POST remains CSRF-protected

## Implementation Readiness

Ready to plan. No external dependency research is required for Phase 22 because the phase can be delivered by extending the current Flask auth/session contract and reusing the existing OTP delivery service.