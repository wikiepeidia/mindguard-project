# Phase 23: OTP Abuse Guardrails - Context

**Gathered:** 2026-04-17  
**Status:** Ready for planning  
**Mode:** Autonomous auto-context

<domain>
## Phase Boundary

Phase 23 focuses only on abuse guardrails for the existing OTP verify flow.

Scope included in this phase:

- Add route-level rate limiting to OTP verification and resend POST actions.
- Reuse the existing anti-spam telemetry system so OTP verify/resend attempts leave auditable cooldown evidence.
- Keep challenge-level lockout and resend cooldown aligned with anti-spam cooldown on the same pending OTP challenge.
- Add automated tests that prove normal users can still complete verification while abusive bursts are blocked.

Scope excluded from this phase:

- Provider outage failover or retry queue behavior.
- New OTP UI patterns beyond minimal wait-state feedback on the existing verify page.
- Broad milestone-wide OTP QA matrix and concurrency stress testing.

</domain>

<decisions>
## Implementation Decisions

### Abuse Guardrail Contract

- **D-01:** Protect only the POST actions for `/verify-otp` and `/verify-otp/resend` with route-level rate limits. Do not throttle the GET verify page.
- **D-02:** Reuse the existing `Flask-Limiter` extension and the existing anti-spam persistence models; do not introduce a new third-party dependency or a new database schema for OTP abuse control.
- **D-03:** Reuse `AntiSpamEvent` and `AntiSpamActorState` through a dedicated OTP abuse helper/service so OTP abuse telemetry is stored in the same system as the existing scammer-report anti-spam flow.
- **D-04:** When anti-spam cooldown activates for an OTP flow, sync that cooldown with the current `OtpChallenge.locked_until` so the challenge state and telemetry state do not drift.

### User Experience Contract

- **D-05:** Keep user-facing OTP abuse messaging in Vietnamese and minimal, using the existing flash/wait-state pattern rather than inventing a new screen.
- **D-06:** Do not add new OTP fields or a new verify page; Phase 23 should extend the current verify flow only.

### Testing Priority

- **D-07:** Tests must prove both route-level limiter blocking and anti-spam telemetry-backed cooldown behavior.
- **D-08:** Tests must also prove that legitimate, low-frequency OTP users still verify successfully.

### the agent's Discretion

- Exact limiter thresholds and cooldown values can be chosen during implementation, but they must be config-backed and conservative enough to stop bursts without harming the normal verify flow.
- The OTP abuse actor identity may be derived from a hashed pending email and request IP as long as raw email is not written into new telemetry fields.

</decisions>

<canonical_refs>

## Canonical References

### Phase Scope and Requirements

- `.planning/ROADMAP.md` — Phase 23 goal, success criteria, and scope.
- `.planning/REQUIREMENTS.md` — OTPREL-01 and OTPREL-02 requirement IDs. Note: traceability table is stale; use ROADMAP plus completed Phase 22 artifacts as the source of truth.
- `.planning/STATE.md` — Current milestone progress and continuity.

### Current OTP Implementation

- `routes/auth.py` — Current verify and resend routes.
- `services/anti_spam.py` — Existing anti-spam decision and cooldown persistence pattern.
- `models/models.py` — `AntiSpamEvent`, `AntiSpamActorState`, and `OtpChallenge` state fields.
- `extensions.py` — Shared `Flask-Limiter` extension.
- `config.py` — Current abuse and OTP configuration keys.

### Prior Phase Context

- `.planning/phases/20-otp-security-policy-core/20-03-SUMMARY.md` — OTP challenge lifecycle and testing patterns.
- `.planning/phases/21-production-otp-email-delivery/21-03-SUMMARY.md` — Delivery reliability contract and validation pattern.
- `.planning/phases/22-resend-verify-session-stability/22-02-SUMMARY.md` — Current verify/resend route behavior and regression strategy.

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- `Flask-Limiter` is already initialized globally and used on auth, admin, chatbot, and API routes.
- `AntiSpamDecisionService` already persists cooldown decisions in `AntiSpamEvent` and `AntiSpamActorState` with config-backed thresholds.
- `OtpChallenge.locked_until` and `status='locked'` already represent temporary challenge lockout in the OTP lifecycle.

### Established Patterns

- Security-sensitive auth feedback is delivered with Vietnamese `flash()` messages and redirects.
- OTP route tests already seed pending session state and `OtpChallenge` rows directly for deterministic integration coverage.
- Anti-spam tests use isolated in-memory apps and verify persisted cooldown state rather than mocking away the database.

### Integration Points

- Phase 23 should extend `routes/auth.py` and keep the verify/resend contract centered on the existing page.
- OTP abuse telemetry should flow through a helper/service layer rather than bloating route code.
- Phase 23 validation should combine anti-spam service tests with OTP route integration tests.

</code_context>

<specifics>
## Specific Ideas

- Prefer config-backed rate limit strings such as `OTP_VERIFY_RATE_LIMIT` and `OTP_RESEND_RATE_LIMIT` over hardcoded literals.
- Prefer OTP-specific anti-spam config keys rather than reusing the scammer-report thresholds exactly.
- Keep the resend button disable/wait-state wired through server-calculated values instead of client-only timers.

</specifics>

<deferred>
## Deferred Ideas

- Full outage continuity and retry queue handling.
- Multi-provider OTP failover behavior.
- Broad OTP concurrency, provider-failure, and release-gate QA matrix.

</deferred>

---

*Phase: 23-otp-abuse-guardrails*
*Context gathered: 2026-04-17*
