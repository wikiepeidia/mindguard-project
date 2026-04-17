# Phase 24: OTP QA Reliability Gate - Context

**Gathered:** 2026-04-17  
**Status:** Completed  
**Mode:** Autonomous auto-context

<domain>
## Phase Boundary

Phase 24 focuses on closing the OTP test gaps that remained after the production email, resend/session, and abuse-guardrail phases.

Scope included in this phase:

- Add dedicated unit coverage for resend cooldown, resend window caps, and replacement-challenge activation behavior.
- Add integration coverage for resend delivery failure rollback and concurrent verify replay handling.
- Re-run the OTP-focused regression gate and capture validation evidence before treating v1.4 as release-ready.

Scope excluded from this phase:

- New OTP product behavior or UI redesign.
- Provider failover, async retry queues, or email dashboard provisioning.
- Environment-secret fixes outside the automated test harness.

</domain>

<decisions>
## Implementation Decisions

### Test-Scope Contract

- **D-01:** Reuse the existing Flask + SQLAlchemy in-memory test harness; do not introduce a new test framework or fixture system.
- **D-02:** Keep Phase 24 behavior-preserving. Add coverage around the current OTP implementation instead of changing auth behavior unless a failing test proves a bug.
- **D-03:** Put resend-policy helper coverage in a dedicated test module so resend lifecycle rules stay readable and isolated from broader OTP security tests.
- **D-04:** Prove concurrent verify behavior with two independent Flask test clients sharing the same persisted OTP challenge state.
- **D-05:** Validation evidence must include both focused Phase 24 commands and a broader OTP regression suite.

### User Experience Contract

- **D-06:** Existing Vietnamese auth messaging and verify/resend page behavior remain unchanged in this phase.

### the agent's Discretion

- Exact helper names and fixture layout may follow the existing OTP test style as long as database-backed challenge state is exercised directly.
- Existing warnings may remain documented if they are outside the Phase 24 scope and do not indicate test failure.

</decisions>

<canonical_refs>

## Canonical References

### Phase Scope and Requirements

- `.planning/ROADMAP.md` — Phase 24 goal, requirements, and success criteria.
- `.planning/STATE.md` — milestone continuity and closeout state.
- `.planning/phases/23-otp-abuse-guardrails/23-VERIFICATION.md` — previous OTP guardrail validation baseline.

### Current OTP Implementation

- `utils/otp_security.py` — resend policy and replacement challenge lifecycle helpers.
- `routes/auth.py` — register, verify, and resend OTP route behavior.
- `services/otp_email_delivery.py` — provider send contract and fail-closed delivery checks.
- `models/models.py` — `OtpChallenge` persistence model.

### Current OTP Test Surface

- `tests/test_otp_security.py` — OTP generation, expiry, lockout, and verification helper coverage.
- `tests/test_otp_email_delivery.py` — delivery-service contract tests.
- `tests/test_otp_auth_integration.py` — auth-route OTP integration coverage.
- `tests/test_csrf_and_routes.py` — verify/resend route regression checks across the app harness.

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- OTP route tests already seed pending session state and persisted `OtpChallenge` rows directly.
- The resend flow already supports replacement-challenge staging and rollback semantics; Phase 24 needs to prove those transitions explicitly.
- Existing register-send failure tests already prove fail-closed registration behavior; the missing gap was resend-specific failure handling.

### Established Patterns

- Security-sensitive auth flows are tested through real Flask requests, not through direct route-function calls.
- Helper-level OTP lifecycle rules are simplest to verify with an isolated in-memory app and real database rows.
- Regression evidence is stored as phase validation and verification markdown under `.planning/phases/`.

</code_context>

<deferred>
## Deferred Ideas

- Converting the OTP codebase from `datetime.utcnow()` to timezone-aware timestamps.
- Replacing Flask-Limiter in-memory test warnings with a dedicated external limiter backend.
- Production Resend sender provisioning (`RESEND_FROM_EMAIL`) and dashboard validation.

</deferred>

---

*Phase: 24-otp-qa-reliability-gate*
*Context gathered: 2026-04-17*
