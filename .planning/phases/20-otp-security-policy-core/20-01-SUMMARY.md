---
phase: 20-otp-security-policy-core
plan: 01
subsystem: auth
tags: [otp, pbkdf2, hmac, secrets, cryptography, security]

# Dependency graph
requires:
  - phase: 19-verification-maintenance-setup
    provides: Verified codebase and docs baseline for v1.4 work
provides:
  - OtpChallenge ORM model with lifecycle and policy fields
  - OTP issue/hash/verify helper functions (utils/otp_security.py)
  - OTP security policy config keys (TTL, attempts, lockout, pepper)
  - Manual migration script for otp_challenges table
affects: [20-02, 20-03, 21, 22, 23, 24]

# Tech tracking
tech-stack:
  added: [hashlib.pbkdf2_hmac, hmac.compare_digest, secrets.randbelow]
  patterns: [hash-only OTP storage, constant-time comparison, pepper versioning]

key-files:
  created: [utils/otp_security.py, database/migrate_otp_challenges.py, tests/test_otp_security.py]
  modified: [config.py, .gitignore]

key-decisions:
  - "PBKDF2-HMAC-SHA256 with 100k iterations for OTP hashing -- balances security with serverless latency"
  - "Pepper versioned (v1) to support future rotation without invalidating active challenges"
  - "OtpChallenge model already existed in models.py from prior planning -- reused as-is"

patterns-established:
  - "Hash-only OTP storage: plaintext OTP returned from issue_otp_challenge for email sending but never persisted"
  - "Challenge lifecycle states: active -> used/expired/locked/invalidated with reason tracking"
  - "Config keys from env vars with safe defaults: OTP_TTL_SECONDS=300, OTP_MAX_ATTEMPTS=5, OTP_LOCKOUT_SECONDS=900"

requirements-completed: [OTPSEC-01, OTPSEC-02]

# Metrics
duration: 5min
completed: 2026-04-15
---

# Phase 20 Plan 01: OTP Challenge Schema + Crypto Helper Foundation Summary

**PBKDF2-hashed OTP challenge model with secrets-based generation, constant-time verification, and env-driven security policy config**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-15T03:45:25Z
- **Completed:** 2026-04-15T03:50:32Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Created utils/otp_security.py with cryptographically secure OTP generation (secrets.randbelow), PBKDF2-HMAC-SHA256 hashing, challenge issuance with supersession of prior active challenges, and constant-time verification (hmac.compare_digest)
- Added OTP security policy config keys to Config class (OTP_TTL_SECONDS, OTP_MAX_ATTEMPTS, OTP_LOCKOUT_SECONDS, OTP_PEPPER, OTP_PEPPER_VERSION) -- all sourced from environment variables
- Created idempotent migration script for otp_challenges table with indexes on email, status, expires_at, and composite email+status
- Full TDD cycle: 19 tests written and passing covering generation, hashing, verification lifecycle, config keys, and model fields

## Task Commits

Each task was committed atomically:

1. **Task 1 (RED): Failing OTP tests** - `32c992e` (test)
2. **Task 1 (GREEN): OTP security module + config keys** - `221238b` (feat)
3. **Task 2: Migration script for otp_challenges** - `82e6397` (feat)

## Files Created/Modified
- `utils/otp_security.py` - OTP generation, hashing, challenge issuance, and verification helpers
- `config.py` - Added OTP_TTL_SECONDS, OTP_MAX_ATTEMPTS, OTP_LOCKOUT_SECONDS, OTP_PEPPER, OTP_PEPPER_VERSION
- `database/migrate_otp_challenges.py` - Idempotent migration creating otp_challenges table and indexes
- `tests/test_otp_security.py` - 19 unit tests for OTP security foundation
- `.gitignore` - Added exception for tests/test_otp_security.py

## Decisions Made
- Used PBKDF2-HMAC-SHA256 with 100k iterations for OTP hashing -- provides strong brute-force resistance while staying within serverless timeout constraints
- Pepper is versioned (v1) to support future key rotation without invalidating in-flight challenges
- OtpChallenge model was already present in models.py from prior planning work -- reused without modification
- Migration uses SERIAL PRIMARY KEY (PostgreSQL-native) matching the NeonDB production stack

## Deviations from Plan

None - plan executed exactly as written. OtpChallenge model already existed from prior work, so no model creation was needed in Task 1.

## Issues Encountered
- `.gitignore` pattern `tests/*` blocked committing the test file -- added `!tests/test_otp_security.py` exception (Rule 3: blocking issue)

## User Setup Required

OTP_PEPPER environment variable should be set in production (Vercel) for pepper-based hashing. Without it, an empty string is used as pepper (safe for development but not production-grade).

## Known Stubs

None -- all functions are fully implemented with no placeholder logic.

## Next Phase Readiness
- OTP foundation types, helpers, and migration are ready for Plan 02 (register/verify lifecycle enforcement)
- routes/auth.py still uses hardcoded OTP `123456` -- Plan 02 will integrate the new OTP helpers
- No blockers for continuing to Plan 02

## Self-Check: PASSED

All 5 files verified present. All 3 commit hashes verified in git log.

---
*Phase: 20-otp-security-policy-core*
*Completed: 2026-04-15*
