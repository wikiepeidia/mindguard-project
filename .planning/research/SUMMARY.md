# Milestone v1.4 OTP Research Summary

Date: 2026-04-14  
Scope: OTP email reliability, outage continuity fallback, and QA for current Flask monolith on Vercel + NeonDB.

## 1) Stack additions for v1.4

- Add server-side OTP persistence in PostgreSQL (NeonDB) via new `otp_challenges` table and manual migration script in `database/`.
- Add `services/otp_service.py` as OTP lifecycle boundary: issue, resend, verify, lockout, consume.
- Add `services/mail_adapter.py` (provider-agnostic) plus provider modules (Resend API primary, SMTP/API backup).
- Add outage continuity components: provider failover policy, DB-backed retry queue for pending registration resend, and auditable manual admin assist handoff.
- Extend `config.py` with `EMAIL_PROVIDER`, backup provider keys, `DEFAULT_FROM_EMAIL`, and OTP policy keys (`OTP_TTL_SECONDS`, `OTP_MAX_ATTEMPTS`, resend cooldown/caps).
- Keep Flask-Mail available for local fallback paths, but treat HTTP API provider as production path.
- Expand automated tests for OTP state transitions, failover behavior, outage recovery resend, and provider failure handling.

## 2) v1.4 table-stakes feature shortlist

- Remove all hardcoded OTP behavior (`123456`) and generate cryptographically random 6-digit OTP.
- Send real OTP emails in production, with clear error handling when provider send fails.
- Enforce OTP lifecycle policy: short TTL, max verify attempts, temporary lockout, and strict single-use.
- Add resend endpoint with cooldown + resend cap and user-visible countdown feedback.
- Normalize session contract from register -> verify so refresh/timeout behavior is deterministic.
- Add route-level protections for `/verify-otp` and resend endpoint (rate limit + abuse guardrails).
- Implement outage continuity path: automatic backup-provider failover, preserved pending registration in retry queue, and manual admin assist route for prolonged outage.
- Ship OTP reliability QA: happy path, wrong OTP, expired OTP, lockout, resend cooldown, provider failure, outage continuity, and concurrent verify.

## 3) Key architecture decisions

- OTP source of truth must move from Flask session to DB-backed challenge records.
- Auth routes stay thin; OTP business rules live in service layer.
- Verification must be atomic and idempotent to prevent replay/double activation under concurrency.
- Use provider abstraction now so later switch to SES/SendGrid/Postmark does not touch route logic.
- Keep request-path send synchronous with strict timeout budget; if send paths are down, preserve pending registration and enqueue DB-backed retry jobs (no Celery/Redis in v1.4).
- Emit structured OTP events (`challenge.created`, `send.success/failure`, `failover.used`, `retry.queued`, `verify.success/failure`, `locked`, `expired`) for operations and QA.

## 4) Top pitfalls and mitigations

| Pitfall | Why it is risky here | Mitigation for v1.4 |
|---|---|---|
| Hardcoded/default OTP path remains reachable | Enables bypass and invalidates verification trust | Remove fallback OTP values, fail closed if challenge missing, rotate OTP on resend |
| OTP lifecycle kept only in session | Stateless runtime and replay risks; weak auditability | Persist hashed OTP challenge in DB with expiry, attempts, consume marker |
| Missing verify/resend throttling | Brute-force and spam abuse on auth endpoints | Layer route limits + challenge-level cooldown/attempt lockout |
| Email provider outage leaves no user path | Registration dead-end during provider incidents | Add provider failover + retry queue + manual admin assist continuity path |
| Race conditions on verify | Duplicate/parallel submits can create inconsistent account state | Use transaction-safe consume logic and handle uniqueness races deterministically |

## 5) Recommended provider strategy (dev/staging/prod/growth)

| Stage | Provider choice | Transport | Practical intent |
|---|---|---|---|
| Dev | Mailtrap or Ethereal | SMTP sandbox | Safe debugging without real user delivery |
| Staging/UAT | Resend (same path as prod), optional inbox assertion tool | HTTP API primary | Catch template/policy regressions before release |
| Prod (v1.4) | Resend Pro + configured backup provider | HTTP API primary | Best speed-to-reliability fit with outage continuity fallback |
| Growth (100k-1M OTP/mo) | Keep abstraction; evaluate SES vs SendGrid/Postmark | HTTP/API | Rebalance cost, quotas, and deliverability support as volume grows |

Provider rule: keep SMTP adapter for fallback/dev only, not as primary production backbone.

## 6) What to defer out of v1.4

- SMS OTP, TOTP, or broader MFA expansion.
- Active-active multi-provider orchestration and advanced routing policies.
- Celery/Redis distributed queue stack (v1.4 uses DB-backed retry queue only).
- Dedicated IP warmup program and enterprise deliverability tuning.
- Full auth system refactor beyond register/verify/resend OTP flow.
- CI test stages that depend on real external inboxes and flaky provider quota behavior.

## Requirements input

Candidate requirement IDs:

- OTPSEC-01: Generate 6-digit OTP via cryptographic randomness and never use static fallback values.
- OTPSEC-02: Store OTP as hash+salt(+pepper), never plaintext in session, DB, logs, or UI.
- OTPPOL-01: Enforce OTP TTL (default 5 minutes) and reject expired challenges.
- OTPPOL-02: Enforce max verify attempts and temporary lockout after threshold.
- OTPPOL-03: Mark OTP consumed atomically and reject replay.
- OTPMAIL-01: Send OTP through provider adapter with timeout and normalized error mapping.
- OTPRES-01: Provide resend endpoint with cooldown and rolling resend cap.
- OTPSES-01: Persist and use challenge_id in session as the only client-side OTP reference.
- OTPOUT-01: Add automatic primary->backup provider failover during email outage.
- OTPOUT-02: Preserve pending registration in DB-backed retry queue and resend automatically on recovery.
- OTPOUT-03: Add manual admin assist completion path for prolonged outage.
- OTPREL-01: Add route-level and challenge-level throttling for verify/resend abuse control.
- OTPQA-01: Add automated tests for expiry, lockout, resend policy, provider failure, outage continuity, and concurrency.
