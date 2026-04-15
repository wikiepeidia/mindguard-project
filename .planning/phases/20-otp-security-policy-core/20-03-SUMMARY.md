---
phase: 20-otp-security-policy-core
plan: 03
subsystem: auth
tags: [otp, test, validation, lifecycle]

requires:
  - phase: 20-otp-security-policy-core
    provides: OTP challenge schema and auth route integration
provides:
  - OTP security policy unit tests for challenge lifecycle (generation, hash, expiry, lockout, validation)
  - Updated route-level tests to reflect challenge-based OTP integration
  - Validation metrics reflecting actual manual execution outcomes

affects: [21, 22, 23, 24]

tech-stack:
  added: []
  patterns: [Automated testing over complex policy states, Mock-based config overrides]

key-files:
  created: [tests/test_otp_security_policy.py]
  modified: [tests/test_csrf_and_routes.py, .planning/phases/20-otp-security-policy-core/20-VALIDATION.md]

key-decisions:
  - "Decoupled tests for `utils.otp_security` into policies and structural coverage to prevent tight coupling and test database-reliant logic precisely using isolated mock DB interactions."
  - "Refactored route-level tests in `tests/test_csrf_and_routes.py` without mutating legacy code, but just fixing the assertions around DB state reflection."
  - "Utilized mocked Dictionary config in test setup explicitly overriding Flask constraints for faster testing."

patterns-established:
  - "Policy-driven test categorization directly matching Requirements mapping IDs."

requirements-completed: [OTPSEC-01, OTPSEC-02, OTPSEC-03, OTPPOL-01, OTPPOL-02, OTPPOL-03]

duration: 15min
completed: 2026-04-15
---

# Phase 20 Plan 03: Establish Policy Tests and Align Validation Summary

**Created and aligned automated tests for all Phase 20 OTP security requirements, followed by updating core validation evidence map to pass.**

## Performance

- **Duration:** 15 min
- **Started:** 2026-04-15T11:00:00Z
- **Completed:** 2026-04-15T11:15:00Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- Created `tests/test_otp_security_policy.py` containing individual scenarios handling Generation bounds, DB persistence verification against plaintext disclosure, Challenge Expiration, Max attempt Lockout triggering, and Challenge Re-issuance validity logic. Tests now utilize proper Mock dict overrides.
- Updated `tests/test_csrf_and_routes.py` to ensure route success explicitly tests for state transitions inside the mock database objects (`challenge.status = 'used'`).
- Filled out `20-VALIDATION.md` map setting its coverage checks against live CLI commands mapping cleanly to the `green` output of pytest. `nyquist_compliant` enabled.

## Task Commits

1. **Task 1: Add OTP security policy test suite** - `82a6309` (test)
2. **Task 2: Update existing auth route tests** - `b759925` (test)
3. **Task 3: Refresh validation map** - `f9ac67b` (docs)

## Files Created/Modified
- `tests/test_otp_security_policy.py` (Created) - Holds specific `otppol` and `otpsec` checks
- `tests/test_csrf_and_routes.py` (Modified) - Updated assertions
- `.planning/phases/20-otp-security-policy-core/20-VALIDATION.md` (Modified) - Matrix filled

## Decisions Made
- Chose to patch `app.app_context` logic locally inside test's `setUp` to dodge DB object unbounding alongside mock setups. Then shifted directly to mock dictionaries over objects to fulfill constraints inside helpers.
- Adjusted query string references inside `20-VALIDATION.md` to reflect properly constructed test names internally (`single_use` replaced `replay`).

## Deviations from Plan

### Auto-fixed Issues
**1. [Rule 1 - Bug] Fixed Flask Context Mismatch in Mocks**
- **Found during:** Task 1 Execution
- **Issue:** Attempting to patch Alchemy models led to `RuntimeError: Working outside of application context.`  
- **Fix:** Switched `setUp` logic to leverage initialized app context directly.

**2. [Rule 1 - Bug] Fixed Mock iteration Error inside _cfg_get**
- **Found during:** Task 1 Execution
- **Issue:** `TypeError: unsupported type for timedelta seconds component: MagicMock`
- **Fix:** Replaced mock Config payload with explicit hardcoded dictionary `mock_config`.

## Issues Encountered
- Missing `test_otp_security_policy.py` bypass handling for ignored scopes in `.gitignore` was overridden with `git add -f`.

## Known Stubs
- `test_csrf_and_routes.py` continues referring to a placeholder Send OTP behavior which is normal as this requires Phase 21 resolution.

## Next Phase Readiness
- Phase 20 is complete.
- We have fully decoupled the baseline logic and policies while backing them fully with tests.
- Ready to jump right into Phase 21 (Production OTP Email Delivery).

## Self-Check: PASSED
- `tests/test_otp_security_policy.py` exists
- Commits `82a6309`, `b759925` and `f9ac67b` exist.
