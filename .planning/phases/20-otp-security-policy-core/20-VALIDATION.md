---
phase: 20
slug: otp-security-policy-core
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-15
---

# Phase 20 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest + unittest (existing hybrid) |
| **Config file** | none (existing direct tests) |
| **Quick run command** | `python -m pytest tests/test_csrf_and_routes.py -k otp` |
| **Full suite command** | `python -m pytest tests/test_csrf_and_routes.py tests/test_otp_security_policy.py` |
| **Estimated runtime** | ~35 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/test_csrf_and_routes.py -k otp`
- **After every plan wave:** Run `python -m pytest tests/test_csrf_and_routes.py tests/test_otp_security_policy.py`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 45 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 20-01-01 | 01 | 1 | OTPSEC-02 | T-20-01 | OTP persisted only as hash+salt+pepper metadata | unit | `python -m pytest tests/test_otp_security_policy.py -k hash` | ❌ W0 | pending |
| 20-01-02 | 01 | 1 | OTPSEC-01, OTPPOL-01 | T-20-02 | OTP random 6-digit + TTL enforced | unit | `python -m pytest tests/test_otp_security_policy.py -k "random or expiry"` | ❌ W0 | pending |
| 20-02-01 | 02 | 2 | OTPPOL-02 | T-20-03 | Wrong attempts increment + lockout enforced | route | `python -m pytest tests/test_csrf_and_routes.py -k "verify_otp and wrong"` | ✅ | pending |
| 20-02-02 | 02 | 2 | OTPPOL-03 | T-20-04 | Verify single-use and replay rejected | route | `python -m pytest tests/test_otp_security_policy.py -k replay` | ❌ W0 | pending |
| 20-03-01 | 03 | 3 | OTPSEC-03 | T-20-05 | New issue invalidates prior active challenge | unit | `python -m pytest tests/test_otp_security_policy.py -k invalidate` | ❌ W0 | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_otp_security_policy.py` - add OTP challenge lifecycle tests
- [ ] `tests/fixtures/otp_security.py` - reusable fixture builders for challenge states

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| No OTP demo hint visible on verify page | OTPSEC-01 | UI text assertion reliability across templates can be brittle with localization | Open `/verify-otp` after register and confirm page has no static OTP demo value |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependency
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 45s
- [ ] `nyquist_compliant: true` set in frontmatter after execution verification

**Approval:** pending
