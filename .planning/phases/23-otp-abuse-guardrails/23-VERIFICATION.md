---
status: passed
phase: 23-otp-abuse-guardrails
verified: 2026-04-17
---

# Phase 23: OTP Abuse Guardrails — Verification

## Success Criteria

### SC-1: Verify and resend bursts are blocked by route-level limits ✓ PASS

- `tests/test_otp_auth_integration.py::OtpAuthAbuseGuardrailTests::test_verify_post_rate_limit_returns_429`
  - Confirms POST `/verify-otp` returns 429 once the configured low test threshold is exceeded.
- `tests/test_otp_auth_integration.py::OtpAuthAbuseGuardrailTests::test_resend_post_rate_limit_returns_429`
  - Confirms POST `/verify-otp/resend` returns 429 after repeated bursts while the first two requests still pass.

### SC-2: Anti-spam telemetry and challenge cooldown stay aligned ✓ PASS

- `tests/antispam/test_otp_guardrails.py::TestOtpGuardrails::test_repeated_otp_abuse_events_trigger_cooldown`
  - Confirms repeated OTP abuse events persist a cooldown for the hashed OTP actor.
- `tests/antispam/test_otp_guardrails.py::TestOtpGuardrails::test_get_active_otp_cooldown_ignores_expired_state`
  - Confirms expired cooldown state is ignored.
- `tests/antispam/test_otp_guardrails.py::TestOtpGuardrails::test_sync_otp_challenge_cooldown_preserves_later_lock`
  - Confirms cooldown synchronization never shortens an existing later challenge lock.
- `tests/test_otp_auth_integration.py::OtpAuthAbuseGuardrailTests::test_verify_invalid_attempts_sync_anti_spam_cooldown_to_challenge`
  - Confirms verify abuse escalates into synchronized challenge lock state.
- `tests/test_otp_auth_integration.py::OtpAuthAbuseGuardrailTests::test_verify_get_uses_anti_spam_cooldown_to_disable_resend`
  - Confirms GET `/verify-otp` renders the abuse cooldown wait-state consistently.

### SC-3: Legitimate OTP users still succeed below the abuse thresholds ✓ PASS

- `tests/test_otp_auth_integration.py::OtpAuthAbuseGuardrailTests::test_verify_normal_success_still_passes_under_guardrails`
  - Confirms normal OTP verification still succeeds when request rate stays below the guardrail thresholds.
- `tests/test_csrf_and_routes.py::TestCSRFProtection::test_verify_otp_resend_with_csrf_allowed`
  - Confirms valid resend requests still reach the flow under the updated route contract.
- `tests/test_csrf_and_routes.py::TestAuthFlows::test_verify_otp_success`
  - Confirms the broader verify path still works with the Phase 23 auth changes in place.

## Regression Gates ✓ PASS

Executed commands:

```text
python -m pytest tests/antispam/test_otp_guardrails.py tests/test_otp_auth_integration.py -k "otp or rate_limit or resend or verify" -q
python -m pytest tests/antispam/test_otp_guardrails.py -q
python -m pytest tests/test_otp_auth_integration.py -k "otp or rate_limit or resend or verify" -q
python -m pytest tests/test_csrf_and_routes.py -k "verify_otp or resend" -q
python -m pytest tests/antispam/test_decision_service.py tests/antispam/test_monitor_mode.py tests/antispam/test_signal_scoring.py tests/antispam/test_soft_enforce.py tests/antispam/test_user_feedback.py tests/antispam/test_otp_guardrails.py -q
python -m pytest tests/test_otp_security.py -q
```

Results:

- Focused Phase 23 slice: `30 passed`
- Phase 23 validation commands: `3 passed`, `27 passed`, `5 passed`
- Broader anti-spam regression slice: `12 passed`
- OTP security regression slice: `19 passed`

## Residual Notes

- Existing `datetime.utcnow()` deprecation warnings remain in the OTP and anti-spam code paths.
- Flask-Limiter emits expected in-memory-storage warnings in tests because the harness does not configure an external storage backend.

## Result: PASSED (3/3 success criteria met)
