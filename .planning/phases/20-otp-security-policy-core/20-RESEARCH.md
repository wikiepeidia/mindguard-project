---
phase: 20-otp-security-policy-core
status: complete
created: 2026-04-15
source: manual-fallback-research
---

# Phase 20 Research - OTP Security Policy Core

## Scope

Phase 20 must satisfy only these requirement IDs:

- OTPSEC-01, OTPSEC-02, OTPSEC-03
- OTPPOL-01, OTPPOL-02, OTPPOL-03

Out of phase (do not implement here):

- OTPMAIL-* (real provider delivery)
- OTPRES-*/OTPSES-* (resend/session UX stabilization)
- OTPREL-*, OTPQA-*

## Codebase Findings (Current State)

1. OTP is hardcoded in auth flow:

- routes/auth.py register route flashes demo OTP 123456
- routes/auth.py verify route uses session.get('otp_code', '123456')

1. OTP is not persisted server-side:

- No OTP challenge table exists in models/models.py
- OTP validation currently relies on session data only

1. No OTP lifecycle controls:

- No TTL
- No attempt counter
- No lockout window
- No explicit single-use enforcement in durable storage

1. View still exposes demo OTP text:

- templates/verify_otp.html shows '(Ma demo: 123456)'

1. Existing test baseline encodes hardcoded behavior:

- tests/test_csrf_and_routes.py sets sess['otp_code'] = '123456' and posts that value

## Standard Stack (Use Existing Libraries)

- Python stdlib security primitives:
  - secrets for random OTP generation
  - hashlib + hmac for constant-time comparison and PBKDF2/HMAC hashing
  - datetime/timedelta for TTL and lockout windows
- Existing Flask + SQLAlchemy stack
- Existing werkzeug.security for password hash remains unchanged for user password
- No new package dependency required

## Architecture Patterns to Apply

1. Introduce server-side OTP challenge entity

- New model (for example: OtpChallenge) stores only hashed OTP metadata
- Session stores challenge reference (challenge_id), never raw OTP

1. OTP hash strategy (salt + pepper)

- Per-challenge random salt
- Global pepper from Config (OTP_PEPPER)
- Stored fields: otp_hash, otp_salt, pepper_version
- Compare using constant-time check

1. State machine for replay safety

- Challenge statuses: active, used, expired, locked, superseded
- New issue invalidates prior active challenge(s) for same email/purpose
- Successful verify sets used_at and status=used

1. Lockout policy (challenge level)

- Increment attempts_used on invalid OTP
- If attempts_used reaches max_attempts, set locked_until
- Reject verify when now < locked_until

1. Expiry policy

- expires_at = issued_at + OTP_TTL_SECONDS (default 300)
- Expired challenge rejected and marked expired

## Data Model Recommendation

Add model in models/models.py:

- id (PK)
- email (indexed)
- purpose (default register_verify)
- otp_hash (non-null)
- otp_salt (non-null)
- pepper_version (default v1)
- attempts_used (default 0)
- max_attempts (default from config)
- issued_at
- expires_at
- locked_until (nullable)
- used_at (nullable)
- invalidated_at (nullable)
- invalidation_reason (nullable)
- status (active/used/expired/locked/superseded)

## Migration Strategy (Project Convention)

Use manual migration script only:

- database/migrate_otp_challenges.py
- Use app.app_context() + db.create_all() pattern used by existing migration scripts
- Do not use flask db migrate/upgrade

## Route Integration Strategy

Update routes/auth.py:

1. register()

- After pending_registration set, call otp issue function
- Issue returns challenge_id + plaintext OTP (for email send path later)
- Store challenge_id in session['pending_otp_challenge_id']
- Remove any hardcoded OTP fallback paths

1. verify_otp()

- Read pending_registration and pending_otp_challenge_id
- Validate challenge lifecycle: exists, active, not expired, not locked, not used
- Verify submitted OTP against stored hash
- On success: mark challenge used, create Registration, clear pending session keys
- On failure: increment attempts and enforce lockout if threshold reached

1. Error messages

- Keep user-facing messages in Vietnamese
- Never include OTP value in flash/log output

## Security Notes and Pitfalls

- Do not write OTP into logs, flash, template, or DB plaintext
- Use generic invalid OTP messaging to avoid side-channel leaks
- Keep challenge tied to pending session context to prevent cross-account verification
- Ensure OTP compare is constant-time
- Mark challenge terminal state on success/final expiry to prevent replay

## Common Pitfalls to Avoid

- Leaving session fallback value '123456' in verify path
- Comparing hashes with normal == instead of hmac.compare_digest
- Forgetting to invalidate older active challenges when issuing new one
- Failing to clear pending session keys after success
- Storing naive datetime inconsistently between issue/verify functions

## Validation Architecture

- Test framework: unittest/pytest hybrid already present
- Quick command: python -m pytest tests/test_csrf_and_routes.py -k otp
- Full command: python -m pytest tests/test_csrf_and_routes.py tests/test_otp_security_policy.py
- Required checks:
  - No hardcoded 123456 in auth/template OTP flow
  - OTP verify success path works with hashed challenge
  - Expired challenge rejected
  - Wrong attempts trigger lockout
  - Used challenge cannot be reused
  - Re-issued challenge invalidates previous active challenge

## Implementation Readiness

Ready to plan. No external dependency research is required for Phase 20 because required mechanisms are achievable with current stack and stdlib.
