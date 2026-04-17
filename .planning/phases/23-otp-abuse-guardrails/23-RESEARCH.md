---
phase: 23-otp-abuse-guardrails
status: complete
created: 2026-04-17
source: manual-fallback-research
---

# Phase 23 Research - OTP Abuse Guardrails

## Scope

Phase 23 must satisfy only these requirement IDs:

- OTPREL-01
- OTPREL-02

Out of phase for this plan set:

- OTP outage continuity and retry queue behavior
- New verify-page UX beyond small wait-state feedback
- Full OTP QA matrix and concurrent edge-case testing

## Codebase Findings (Current State)

1. OTP verify and resend POST routes have no route-level limiter guards.

- `routes/auth.py` defines `/verify-otp` and `/verify-otp/resend`
- neither route currently has `@limiter.limit(...)`
- this leaves OTP POST bursts dependent only on challenge logic and global default limits

1. The project already has a reusable anti-spam telemetry system.

- `services/anti_spam.py` persists `AntiSpamEvent` and `AntiSpamActorState`
- thresholds, window, cooldown, and risk weighting are already config-backed
- the service is used in the scammer report flow and tested independently

1. OTP lifecycle already has a native cooldown field that can be aligned with telemetry.

- `models.models.OtpChallenge` already has `locked_until` and `status`
- `verify_otp_submission()` already respects the locked state and lock expiry
- no schema change is needed to represent an anti-spam-backed OTP cooldown

1. Phase 22 already built the correct verify/resend session contract.

- resend stays inside the verify flow
- the verify page can already show a resend wait-state using `resend_enabled` and `resend_notice`
- Phase 23 can extend that server-calculated wait-state instead of redesigning the UI

1. Existing OTP route tests disable limiter behavior by default.

- `tests/test_otp_auth_integration.py` sets `RATELIMIT_ENABLED = False`
- targeted Phase 23 rate-limit coverage will need either a separate app override or a dedicated test class with limiter enabled

## Standard Stack (Use Existing Libraries)

- Existing Flask blueprints and session handling in `routes/auth.py`
- Existing `Flask-Limiter` extension from `extensions.py`
- Existing anti-spam models and `AntiSpamDecisionService`
- Existing OTP lifecycle model and helpers in `models.models` and `utils.otp_security`
- Existing unittest + pytest hybrid test setup
- No new dependency required

## Architecture Patterns to Apply

1. Config-backed route-level limiter strings

- add OTP-specific config keys for route limits
- apply them to POST `/verify-otp` and POST `/verify-otp/resend`
- keep GET `/verify-otp` unthrottled so refresh does not become a false-positive abuse event

1. Dedicated OTP abuse helper/service layered on existing anti-spam persistence

- add a small helper/service that derives a stable OTP abuse actor from the pending email without storing raw email in new telemetry keys
- record verify/resend abuse events through `AntiSpamDecisionService`
- read the active `AntiSpamActorState` for the same OTP actor when rendering or enforcing the verify flow

1. Challenge-level cooldown sync

- when OTP anti-spam cooldown activates, set `OtpChallenge.locked_until` to the later of the existing challenge lock and the anti-spam cooldown
- do not invalidate the challenge just because anti-spam cooldown activated
- keep the cooldown temporary and recoverable on the same verify flow

1. Minimal UX extension only

- reuse the existing resend wait-state UI to reflect anti-spam cooldown when it is stronger than resend cooldown alone
- use flash messages for blocked verify/resend attempts
- avoid any new page or JS-only timer system

## Recommended File-Level Implementation

- `config.py`
  - add OTP-specific route-level rate limit strings and OTP-specific anti-spam threshold/cooldown config
- `services/otp_abuse_guard.py`
  - add OTP actor derivation, telemetry record helper, active cooldown lookup, and challenge lock sync helper
- `routes/auth.py`
  - add limiter decorators to the verify and resend POST routes
  - apply OTP abuse guard before processing verify/resend actions
  - merge anti-spam cooldown into the resend wait-state shown on the verify page
- `tests/antispam/test_otp_guardrails.py`
  - add focused unit coverage for OTP abuse telemetry and cooldown sync
- `tests/test_otp_auth_integration.py`
  - add route-level limit and anti-spam-backed OTP flow coverage

## Common Pitfalls to Avoid

- Reusing the global scammer-report abuse thresholds without OTP-specific config overrides
- Logging raw pending email in anti-spam actor identifiers
- Applying limiter decorators to GET `/verify-otp` and breaking normal refresh behavior
- Letting anti-spam cooldown and `OtpChallenge.locked_until` drift to different wait times on the same challenge
- Writing rate-limit tests against the default OTP test app while `RATELIMIT_ENABLED` is still false

## Validation Architecture

- Test framework: pytest + unittest hybrid already present in repo
- Quick command: `python -m pytest tests/antispam/test_otp_guardrails.py tests/test_otp_auth_integration.py -k "otp or rate_limit or resend or verify"`
- Full command: `python -m pytest tests/antispam/test_otp_guardrails.py tests/test_otp_auth_integration.py tests/test_csrf_and_routes.py -k "otp or resend or verify_otp"`
- Required checks:
  - POST `/verify-otp` returns 429 once the configured route limit is exceeded
  - POST `/verify-otp/resend` returns 429 once the configured route limit is exceeded
  - OTP abuse telemetry persists cooldown state in `AntiSpamActorState` for the same pending actor
  - Anti-spam cooldown synchronizes with `OtpChallenge.locked_until`
  - Legitimate OTP verification still succeeds when requests remain below the abuse thresholds

## Implementation Readiness

Ready to implement. Phase 23 can be delivered by extending the current auth flow with the existing limiter and anti-spam infrastructure; no new persistence layer or external library is required.
