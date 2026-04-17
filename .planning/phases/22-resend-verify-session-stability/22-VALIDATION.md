---
phase: 22
slug: resend-verify-session-stability
status: completed
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-17
---

# Phase 22 - Validation Strategy

> Per-phase validation contract for resend/session stability during OTP verification.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + unittest |
| **Config file** | none (existing direct tests) |
| **Quick run command** | `python -m pytest tests/test_otp_auth_integration.py -k "resend or verify"` |
| **Full suite command** | `python -m pytest tests/test_otp_auth_integration.py tests/test_csrf_and_routes.py -k "resend or verify_otp or register"` |
| **Estimated runtime** | ~45 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/test_otp_auth_integration.py -k "resend or verify"`
- **After every plan wave:** Run `python -m pytest tests/test_otp_auth_integration.py tests/test_csrf_and_routes.py -k "resend or verify_otp or register"`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 22-01-01 | 01 | 1 | OTPRES-02 | T-22-01 / T-22-02 | Resend cooldown and per-window cap are enforced server-side before replacement issuance | unit | `python -m py_compile config.py utils/otp_security.py` | ✅ | green |
| 22-01-02 | 01 | 1 | OTPRES-01, OTPSES-01 | T-22-03 | Verify GET validates pending state and resend success updates the active challenge id without leaving the flow | route | `python -m py_compile routes/auth.py && python -m pytest tests/test_otp_auth_integration.py -k "verify or otp"` | ✅ | green |
| 22-02-01 | 02 | 2 | OTPRES-01, OTPRES-02, OTPSES-01 | T-22-04 | Route/session regressions cover resend success, resend denial when pending session is missing, cooldown denial, and expired pending state | integration | `python -m pytest tests/test_otp_auth_integration.py -k "resend or verify"` | ✅ | green |
| 22-02-02 | 02 | 2 | OTPRES-01, OTPRES-02, OTPSES-01 | T-22-05 | New resend endpoint remains CSRF-protected and validation evidence maps every requirement to runnable commands | route/docs | `python -m pytest tests/test_csrf_and_routes.py -k "verify_otp or resend" && python -m pytest tests/test_otp_auth_integration.py -k "resend or verify"` | ✅ | green |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Verify page shows resend affordance and Vietnamese cooldown guidance clearly | OTPRES-01, OTPRES-02 | Copy and button presentation are easier to confirm visually than with route tests alone | Open `/verify-otp` with a seeded pending session, confirm the resend control is visible and the wait-state text is understandable in Vietnamese |

---

## Validation Sign-Off

- [x] All tasks have automated verification commands
- [x] Requirement-to-test mapping covers OTPRES-01, OTPRES-02, and OTPSES-01
- [x] No resend path bypasses CSRF or server-side cooldown enforcement
- [x] `nyquist_compliant: true` set in frontmatter after execution verification

**Approval:** approved 2026-04-17
