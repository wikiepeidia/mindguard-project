---
phase: 20-otp-security-policy-core
plan: 02
subsystem: auth
tags: [otp, auth, security, lifecycle]

requires:
  - phase: 20-otp-security-policy-core
    provides: OTP challenge schema + crypto helper foundation (20-01)
provides:
  - Secure register/verify OTP lifecycle integration
  - OTP verify UI without hardcoded/demo OTP disclosure
affects: [20-03, 21, 22, 23, 24]

tech-stack:
  added: []
  patterns: [Challenge-based OTP issuance, Policy evaluation on verification]

key-files:
  created: []
  modified:
    - routes/auth.py
    - templates/verify_otp.html

key-decisions:
  - "Moved from simple session string comparison to full database-backed OtpChallenge entity verification"
  - "Re-issuing OTP will automatically invalidate prior active ones"
  - "User feedback no longer leaks OTP values on template or flash messages"

patterns-established:
  - "Issue OTP challenge at registration submit and store only challenge ID and email in session"
  - "Check challenge status (expired, locked, already_used, invalidated) during verify submission and process accordingly"

requirements-completed: [OTPSEC-03, OTPPOL-01, OTPPOL-02, OTPPOL-03]

duration: 15min
completed: 2026-04-15
---

# Phase 20 Plan 02: Integrate OTP lifecycle controls into auth routes Summary

**Integrate OTP lifecycle controls into the auth register and verify routes, enforcing TTL, attempt lockout, single-use, and challenge invalidation.**

## Performance

- **Duration:** 15 min
- **Started:** 2026-04-15T03:52:00Z
- **Completed:** 2026-04-15T04:05:00Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments

- `routes/auth.py` register flow now uses `issue_otp_challenge` and does not leak demo OTP in flash messages or sessions.
- `verify_otp` in `routes/auth.py` loads `pending_otp_challenge_id` and runs the `verify_otp_submission` policy evaluation. Invalid states (expired, already_used, locked, invalidated) reset session limits or reject securely.
- Removed demo `123456` OTP values from `templates/verify_otp.html`. The view now shows the registered email securely.

## Task Commits

The tasks were executed and committed:

1. `b1e639d` feat(20-02): replace register hardcoded OTP with challenge-based issuance
2. `9c950a6` feat(20-02): remove OTP demo disclosure from verify template
3. `572869c` test(20-02): add failing tests for OTP auth route integration

## Files Created/Modified

- `routes/auth.py`
- `templates/verify_otp.html`

## Decisions Made

- Replaced the simple session OTP code logic with full DB challenge entity.
- Handled state transitions and flashed proper messages to end users without resetting session unnecessarily on rate limits, while fully clearing it on expiries/used occurrences.

## Deviations from Plan

- None - plan executed exactly as written.

## Known Stubs

- Send OTP via Email is stubbed out via a `TODO: Send plaintext_code via email` inside `routes/auth.py` (Phase 21).

## Next Phase Readiness

- Auth routes are decoupled from hardcoded logic and rely fully on `OtpChallenge`.
- Next plan (20-03) will cover integration of these into Password Reset APIs if needed, or progressing towards Phase 21.

## Self-Check: PASSED

- `routes/auth.py` is present and verified.
- `templates/verify_otp.html` is present and verified.
- Commits are verified in `git log`.
