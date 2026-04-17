---
status: passed
phase: 24-otp-qa-reliability-gate
validated: 2026-04-17
---

# Phase 24: OTP QA Reliability Gate - Validation

## Commands Executed

```text
python -m pytest tests/test_otp_resend_policy.py -q
python -m pytest tests/test_otp_auth_integration.py -k "resend or concurrent" -q
python -m pytest tests/test_otp_email_delivery.py tests/test_otp_security.py tests/test_otp_resend_policy.py tests/test_otp_auth_integration.py tests/test_csrf_and_routes.py -q
```

## Results

- `python -m pytest tests/test_otp_resend_policy.py -q`
  - Result: `4 passed, 4 warnings in 0.70s`
- `python -m pytest tests/test_otp_auth_integration.py -k "resend or concurrent" -q`
  - Result: `9 passed, 20 deselected, 43 warnings in 1.35s`
- `python -m pytest tests/test_otp_email_delivery.py tests/test_otp_security.py tests/test_otp_resend_policy.py tests/test_otp_auth_integration.py tests/test_csrf_and_routes.py -q`
  - Result: `132 passed, 289 warnings in 24.84s`

## Coverage Added In This Phase

- `tests/test_otp_resend_policy.py`
  - Covers resend cooldown allow/block behavior.
  - Covers resend window-cap denial behavior.
  - Covers replacement challenge staging and activation semantics.
- `tests/test_otp_auth_integration.py`
  - Covers resend delivery failure rollback.
  - Covers concurrent verify single-success behavior.

## Residual Notes

- OTP and auth tests still emit `datetime.utcnow()` deprecation warnings from the current application code and test fixtures.
- Flask-Limiter still emits expected in-memory storage warnings inside the test harness.
- These warnings did not cause failures and were not expanded in scope for Phase 24.
