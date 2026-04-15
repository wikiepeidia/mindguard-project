---
phase: 21
slug: production-otp-email-delivery
status: completed
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-15
---

# Phase 21 - Validation Strategy

> Per-phase validation contract for OTPMAIL delivery behavior.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + unittest |
| **Config file** | none (existing direct tests) |
| **Quick run command** | `python -m pytest tests/test_otp_auth_integration.py -k "register"` |
| **Full suite command** | `python -m pytest tests/test_otp_email_delivery.py tests/test_otp_auth_integration.py -k "register or otp"` |
| **Estimated runtime** | ~45 seconds |

---

## Sampling Rate

- **After every task commit:** Run register-focused integration checks
- **After wave complete:** Run service + route OTP delivery test suite
- **Before `/gsd-verify-work`:** Full suite must pass
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 21-01-01 | 01 | 1 | OTPMAIL-03 | T-21-03 | Env-only provider config contract and fail-closed readiness | unit | `python -m py_compile config.py` | ✅ | green |
| 21-01-02 | 01 | 1 | OTPMAIL-01 | T-21-01 | Resend delivery service returns deterministic success/failure categories | unit | `python -m py_compile services/otp_email_delivery.py services/__init__.py` | ✅ | green |
| 21-02-01 | 02 | 2 | OTPMAIL-01 | T-21-04 | Register flow sends OTP and proceeds only on send success | route | `python -m py_compile routes/auth.py && python -m pytest tests/test_otp_auth_integration.py -k "register"` | ✅ | green |
| 21-02-02 | 02 | 2 | OTPMAIL-02 | T-21-05 | Failed send invalidates pending state and gives safe retry guidance | route | `python -m pytest tests/test_otp_auth_integration.py -k "send_failure or register"` | ✅ | green |
| 21-03-01 | 03 | 3 | OTPMAIL-01, OTPMAIL-02, OTPMAIL-03 | T-21-07 | Requirement-level coverage via service and route tests + evidence map | integration | `python -m pytest tests/test_otp_email_delivery.py && python -m pytest tests/test_otp_auth_integration.py -k "register or otp"` | ✅ | green |

*Status: pending / green / red / flaky*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real inbox receive and spam-folder behavior in production | OTPMAIL-01 | Requires external provider/inbox and deployment env | Deploy with valid `RESEND_API_KEY` and `RESEND_FROM_EMAIL`, register with real email, verify message delivery and timing |

---

## Validation Sign-Off

- [x] All tasks have automated verification commands
- [x] Requirement-to-test mapping covers OTPMAIL-01/02/03
- [x] No plaintext OTP leakage in service/test assertions
- [x] `nyquist_compliant: true` set after test pass

**Approval:** approved
