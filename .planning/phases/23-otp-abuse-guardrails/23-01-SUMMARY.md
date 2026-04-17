---
phase: 23-otp-abuse-guardrails
plan: 01
subsystem: auth
tags: [otp, auth, anti-spam, rate-limit]

requires:
  - phase: 22-resend-verify-session-stability
    provides: Stable resend/session OTP flow and verify-page wait-state handling
provides:
  - Config-backed OTP verify/resend limiter contract
  - OTP abuse helper service over existing anti-spam telemetry
  - Auth-route cooldown enforcement aligned with OTP challenge state
affects: [23-02, 24]

tech-stack:
  added: []
  patterns: [Config-backed Flask-Limiter rules, hashed OTP actor IDs, anti-spam cooldown sync]

key-files:
  created: [services/otp_abuse_guard.py]
  modified: [config.py, routes/auth.py]

key-decisions:
  - "OTP abuse telemetry reuses AntiSpamEvent and AntiSpamActorState instead of adding a new schema or migration."
  - "Pending email is converted into a hashed OTP actor identifier so cooldown telemetry does not introduce a raw-email key."
  - "Anti-spam cooldown is synchronized back onto OtpChallenge.locked_until so verify and resend observe the same guardrail state."

patterns-established:
  - "Route-level limiter strings for OTP endpoints should remain config-backed for testability and tuning."
  - "Cooldown decisions should derive from active anti-spam event history, not stale cached window counters."

requirements-completed: [OTPREL-01, OTPREL-02]

duration: 15min
completed: 2026-04-17
---

# Phase 23 Plan 01 Summary

Implemented the Phase 23 OTP abuse guardrail foundation in the auth flow.

## Accomplishments

- Added OTP-specific config keys in `config.py` for verify/resend rate limits and anti-spam cooldown thresholds.
- Created `services/otp_abuse_guard.py` to derive a hashed OTP actor id, read active cooldown state, record OTP abuse events, merge resend wait-state policy, and synchronize challenge locks.
- Updated `routes/auth.py` so POST `/verify-otp` and POST `/verify-otp/resend` use explicit route-level limiter rules, persist OTP abuse telemetry, and keep challenge lock state aligned with anti-spam cooldowns.

## Task Commits

No git commit was created in this workspace session.

## Verification

- `python -m py_compile config.py services/otp_abuse_guard.py`
- `python -m py_compile routes/auth.py services/otp_abuse_guard.py config.py`

## Self-Check: PASSED
