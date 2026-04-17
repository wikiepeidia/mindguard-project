---
phase: 23
slug: otp-abuse-guardrails
status: completed
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-17
---

# Phase 23 — Validation Strategy

> Per-phase validation contract for OTP abuse guardrails.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + unittest |
| **Config file** | none |
| **Quick run command** | `python -m pytest tests/antispam/test_otp_guardrails.py tests/test_otp_auth_integration.py -k "otp or rate_limit or resend or verify" -q` |
| **Full suite command** | `python -m pytest tests/antispam/test_otp_guardrails.py -q && python -m pytest tests/test_otp_auth_integration.py -k "otp or rate_limit or resend or verify" -q && python -m pytest tests/test_csrf_and_routes.py -k "verify_otp or resend" -q` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/antispam/test_otp_guardrails.py tests/test_otp_auth_integration.py -k "otp or rate_limit or resend or verify"`
- **After every plan wave:** Run `python -m pytest tests/antispam/test_otp_guardrails.py tests/test_otp_auth_integration.py tests/test_csrf_and_routes.py -k "otp or resend or verify_otp"`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 23-01-01 | 01 | 1 | OTPREL-02 | T-23-01 / T-23-02 | OTP abuse telemetry persists active cooldown state without raw-email leakage | unit | `python -m py_compile config.py services/otp_abuse_guard.py` | ✅ | green |
| 23-01-02 | 01 | 1 | OTPREL-01, OTPREL-02 | T-23-03 | Verify and resend POST routes enforce limiter and sync active telemetry cooldown with the pending challenge | route | `python -m py_compile routes/auth.py services/otp_abuse_guard.py config.py` | ✅ | green |
| 23-02-01 | 02 | 2 | OTPREL-02 | T-23-02 | OTP abuse service tests prove cooldown activation and challenge lock sync | unit | `python -m pytest tests/antispam/test_otp_guardrails.py -q` | ✅ | green |
| 23-02-02 | 02 | 2 | OTPREL-01, OTPREL-02 | T-23-03 / T-23-04 | Route tests prove verify/resend rate limits fire while normal OTP flow still succeeds | integration | `python -m pytest tests/test_otp_auth_integration.py -k "otp or rate_limit or resend or verify" -q && python -m pytest tests/test_csrf_and_routes.py -k "verify_otp or resend" -q` | ✅ | green |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

None. `OtpAuthAbuseGuardrailTests::test_verify_get_uses_anti_spam_cooldown_to_disable_resend` asserts the wait-state response directly, so this phase no longer needs a separate manual gate.

---

## Validation Sign-Off

- [x] All tasks have automated verification commands
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 60s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** executed 2026-04-17

## Executed Evidence

- `python -m py_compile config.py services/otp_abuse_guard.py`
- `python -m py_compile routes/auth.py services/otp_abuse_guard.py config.py`
- `python -m pytest tests/antispam/test_otp_guardrails.py tests/test_otp_auth_integration.py -k "otp or rate_limit or resend or verify" -q` -> 30 passed
- `python -m pytest tests/antispam/test_otp_guardrails.py -q` -> 3 passed
- `python -m pytest tests/test_otp_auth_integration.py -k "otp or rate_limit or resend or verify" -q` -> 27 passed
- `python -m pytest tests/test_csrf_and_routes.py -k "verify_otp or resend" -q` -> 5 passed
- `python -m pytest tests/antispam/test_decision_service.py tests/antispam/test_monitor_mode.py tests/antispam/test_signal_scoring.py tests/antispam/test_soft_enforce.py tests/antispam/test_user_feedback.py tests/antispam/test_otp_guardrails.py -q` -> 12 passed
- `python -m pytest tests/test_otp_security.py -q` -> 19 passed

## Residual Notes

- Existing `datetime.utcnow()` deprecation warnings remain in the codebase and tests.
- Flask-Limiter test apps still use in-memory storage during unit/integration runs, which is expected for the local test harness.

Result: PASSED
