# Phase 22: Resend & Verify Session Stability - Context

**Gathered:** 2026-04-15  
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 22 focuses only on stabilizing the resend and verify session contract for the current OTP flow.

Scope included in this phase:

- Let the user request a new OTP from the verify screen without repeating the full registration form.
- Keep the verify page state stable across refresh while the challenge is still pending.
- Redirect safely back to registration when the pending OTP session/challenge is missing or expired.
- Add API-level tests for resend and verify behavior, with emphasis on route/session correctness.

Scope excluded from this phase:

- Provider failover or outage retry queue behavior.
- Route-level abuse throttling and telemetry.
- Full OTP QA matrix and concurrent edge-case stress.

</domain>

<decisions>
## Implementation Decisions

### Resend Flow Contract

- **D-01:** Add a dedicated resend endpoint for the verify flow, and keep the user inside the OTP flow instead of sending them back through the full registration form.
- **D-02:** Resend should issue a fresh OTP challenge and invalidate the previous active challenge for the same registration session.
- **D-03:** The verify page should present a simple resend affordance with a visible wait state/cooldown message, but the UI stays intentionally minimal rather than introducing a new OTP interaction pattern.

### Session Contract

- **D-04:** Treat `pending_registration` and `pending_otp_challenge_id` as the active session contract for the verify flow.
- **D-05:** On refresh, the verify page should continue to work as long as the pending session and challenge remain valid; if either is missing or expired, redirect the user safely back to registration with a clear Vietnamese message.
- **D-06:** After resend success, update the pending challenge reference in session so the next verify submission uses the newest challenge.

### Testing Priority

- **D-07:** Phase 22 should prioritize API/route-level tests for resend and verify behavior, because the user explicitly asked to “really test the api”.
- **D-08:** Tests must cover resend success, resend denied when session state is missing, refresh-safe verify behavior, and safe redirect when pending state is gone or expired.
- **D-09:** Keep tests deterministic by mocking OTP delivery and challenge issuance boundaries; do not rely on real provider calls for this phase.

### the agent's Discretion

- Whether resend uses the same verify page POST or a separate POST endpoint behind the same page is up to the planner, as long as the contract remains simple and testable.
- Exact cooldown wording and button-disabled copy can be chosen by the planner, but the user-visible behavior must be obvious.
- Any later outage/failover/abuse controls stay deferred to the next phases.

</decisions>

<canonical_refs>

## Canonical References

### Phase Scope and Requirements

- `.planning/ROADMAP.md` — Phase 22 goal, success criteria, and plan boundary.
- `.planning/REQUIREMENTS.md` — OTPRES-01, OTPRES-02, OTPSES-01 traceability.
- `.planning/PROJECT.md` — Milestone constraints and current OTP reliability focus.

### Current OTP Implementation

- `routes/auth.py` — Register and verify flow, current session keys, and insertion point for resend handling.
- `templates/verify_otp.html` — Current verify page text and OTP input contract.
- `utils/otp_security.py` — Challenge issuance and verification lifecycle rules.
- `tests/test_otp_auth_integration.py` — Existing route/session integration coverage and good place to extend API tests.
- `tests/test_csrf_and_routes.py` — Existing OTP route baseline and CSRF expectations.

### Prior Phase Context

- `.planning/phases/21-production-otp-email-delivery/21-CONTEXT.md` — Provider and delivery decisions already locked.
- `.planning/phases/21-production-otp-email-delivery/21-VALIDATION.md` — Requirement-to-test mapping for the delivery phase.

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- The current register flow already stores `pending_registration`, `pending_otp_challenge_id`, and `pending_verification_email` in session.
- `verify_otp()` already redirects safely when pending state is missing, so Phase 22 should tighten and normalize that contract instead of inventing a new one.
- OTP challenge issuance already lives in `utils.otp_security.issue_otp_challenge()`, which can be reused when resend creates a new challenge.

### Established Patterns

- Auth flow messages are already in Vietnamese and use `flash()` plus redirects.
- Existing tests use Flask test client, session transactions, and explicit database setup, so API-level regression tests fit the codebase pattern.
- OTP logic is already challenge-based rather than session-only, which makes refresh stability a session-contract problem rather than a new storage design problem.

### Integration Points

- Resend should hook into the verify page and update the session challenge reference after a successful resend.
- Missing or expired session state should return the user to `/register` with a safe, user-facing message.
- The main verification path should remain centered on `/verify-otp` so the planner can keep the feature easy to test.

</code_context>

<specifics>
## Specific Ideas

- The resend affordance should feel like part of the same verify flow, not a separate recovery screen.
- The API test emphasis should include both happy-path resend and the failure path when the pending session has already expired or been cleared.
- Keep the user-facing copy short and concrete in Vietnamese: what happened, what to do next, and what will happen if they refresh.

</specifics>

<deferred>
## Deferred Ideas

- Route-level abuse throttling and telemetry for `/verify-otp` and resend.
- Outage continuity retry queue and provider failover.
- Full OTP QA gate with concurrency and provider-failure matrix.

These belong to later phases in the roadmap and should not be pulled into Phase 22.

</deferred>

---

*Phase: 22-resend-verify-session-stability*
*Context gathered: 2026-04-15*
