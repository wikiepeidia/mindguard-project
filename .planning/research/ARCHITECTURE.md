# Architecture Research — v1.5 SMTP Pivot

## Integration points

- `config.py`: add SMTP-specific config contract.
- `extensions.py`: reuse `mail = Mail()` initialized from app config.
- `services/otp_email_delivery.py`: add SMTP transport branch while preserving normalized result contract.
- `routes/auth.py`: keep current register/resend call sites unchanged except for provider selection readiness.
- `tests/`: extend current OTP unit and integration coverage around SMTP success/failure.

## Suggested build order

1. Define SMTP config contract and readiness checks.
2. Add SMTP send path in `services/otp_email_delivery.py`.
3. Wire auth flows to the new provider selection.
4. Add focused tests for SMTP success/failure.
5. Run production smoke verification on Vercel.

## Architecture rule

Routes should continue to consume a normalized delivery result. Provider-specific logic belongs in the mail service layer.# Architecture: Milestone v1.4 OTP Email Reliability and QA

Domain: OTP email verification for signup on Flask monolith (Vercel serverless + NeonDB/PostgreSQL fallback to SQLite)
Researched: 2026-04-14
Confidence: HIGH (based on current code in routes/auth.py, models/models.py, services/anti_spam.py, utils/helpers.py, database scripts)

## Current State (Observed)

1. Signup stores pending registration in Flask session and currently keeps plain password in session payload.
2. OTP validation uses session key otp_code with fallback default 123456, so OTP can be bypassed in edge cases.
3. No dedicated resend OTP endpoint/service boundary exists.
4. Flask-Mail extension is initialized in app bootstrap, but mail config is not explicitly modeled in Config for OTP delivery.
5. Existing anti-spam and limiter patterns already exist and should be reused instead of introducing new infrastructure.
6. Manual database migration convention is already established in database/ scripts (idempotent, one-off, no Alembic).

Implication: the safest low-disruption path is to keep existing auth blueprint and session login contract, but move OTP state out of session into DB and add service-layer OTP orchestration.

## Recommended Architecture (Minimal Disruption)

### Component Boundaries

| Component | Responsibility | Changes |
|---|---|---|
| routes/auth.py | HTTP forms, captcha validation, flash, redirects | Replace inline OTP logic with service calls; add resend endpoint |
| services/otp_service.py (new) | OTP lifecycle and signup activation transaction | New |
| services/mail_adapter.py (new) | Provider-agnostic mail send interface via Flask-Mail | New |
| models/models.py | Persistence models | Add OtpChallenge model |
| config.py | Runtime tuning via env vars | Add MAIL_* and OTP_* knobs |
| database/migrate_otp_challenge.py (new) | Manual idempotent schema migration | New |

Design rule: routes stay thin, services own business rules, DB owns shared OTP state so Vercel stateless runtime is safe.

## Data Model Strategy

### New Table: otp_challenges

Use one table for signup OTP challenge + pending registration payload to avoid storing password/plain OTP in client session.

| Field | Type | Purpose |
|---|---|---|
| id | integer pk | Internal key |
| challenge_id | varchar(64) unique | Public token stored in session and used by verify/resend |
| purpose | varchar(32) | signup (future reset_password compatible) |
| email | varchar(150) not null | Verification target |
| name | varchar(150) not null | Pending registration field |
| password_hash | varchar(256) not null | Hashed password before account activation |
| payload_json | text nullable | Optional city/occupation/dob snapshot |
| otp_hash | varchar(128) not null | Hashed OTP only, never plaintext |
| otp_expires_at | datetime not null | OTP TTL gate |
| verify_attempt_count | integer default 0 | Wrong attempt tracking |
| resend_count | integer default 0 | Resend cap tracking |
| next_resend_at | datetime nullable | Cooldown gate |
| locked_until | datetime nullable | Lockout gate |
| status | varchar(20) not null | pending/sent/verified/expired/locked/consumed/failed_send |
| last_send_error | varchar(255) nullable | Provider failure reason (sanitized) |
| created_ip | varchar(45) nullable | Abuse analysis |
| last_request_ip | varchar(45) nullable | Abuse analysis |
| created_at | datetime not null | Audit |
| updated_at | datetime not null | Audit |
| verified_at | datetime nullable | Success timestamp |
| consumed_at | datetime nullable | Finalized timestamp |

### Indexes

1. uq_otp_challenges_challenge_id unique(challenge_id)
2. idx_otp_challenges_email_purpose_status(email, purpose, status)
3. idx_otp_challenges_expires_at(otp_expires_at)
4. idx_otp_challenges_next_resend_at(next_resend_at)
5. idx_otp_challenges_locked_until(locked_until)
6. idx_otp_challenges_created_at(created_at)

### Cleanup Approach

1. Lazy cleanup inside OtpService (run lightweight delete/update on start/resend/verify).
2. Keep only terminal rows older than retention window (for example 7 to 30 days depending on audit need).
3. Optional manual maintenance script database/cleanup_otp_challenges.py for bulk cleanup if table grows.

Rationale: no new scheduler dependency required; still compatible with serverless and current workflow.

## Service Boundaries

### services/mail_adapter.py (new)

Contract:

1. send_otp_email(to_email, otp_code, expires_minutes, context)
2. Returns structured result: success(bool), provider_message_id(str|None), error_code(str|None), error_detail(str|None)

Responsibilities:

1. Build localized email subject/body.
2. Encapsulate Flask-Mail Message creation and send call.
3. Normalize provider errors into stable error codes for route/UI logic.

### services/otp_service.py (new)

Contract:

1. start_signup_challenge(form_data, client_ip, user_agent)
2. resend_signup_challenge(challenge_id, client_ip)
3. verify_signup_code(challenge_id, otp_input, client_ip)
4. cleanup_stale_challenges(limit)

Responsibilities:

1. OTP generation with secrets module (not random module).
2. OTP hashing and compare (constant-time check).
3. Lockout and cooldown state transitions.
4. Idempotent account activation transaction (create Registration once, consume challenge).
5. Logging structured OTP lifecycle events.

### auth route integration

1. /register: keep captcha + field validation; call start_signup_challenge; store only challenge_id in session.
2. /verify-otp: call verify_signup_code; on success set registration_email session exactly as current login contract.
3. /verify-otp/resend (new POST): call resend_signup_challenge and return message with cooldown/remaining policy.

## Request Flow: Signup -> Send OTP -> Verify -> Activate

### A. Signup submit

1. User submits register form with captcha.
2. auth route validates fields and duplicate email (existing Registration table).
3. otp_service.start_signup_challenge:
   - cleanup stale rows
   - generate OTP and hash
   - create or refresh active challenge for email
   - commit challenge state (pending/sent)
   - send via mail_adapter
   - update send status
4. Store challenge_id in session (not raw OTP, not plaintext password).
5. Redirect to verify page.

### B. Verify OTP

1. User posts otp input.
2. auth route loads challenge_id from session.
3. otp_service.verify_signup_code:
   - load challenge
   - reject if expired/locked/consumed
   - compare OTP hash
   - wrong code: increment verify_attempt_count; set locked_until if max reached
   - correct code: create Registration from stored payload (password already hashed), mark challenge verified/consumed
4. Route sets registration_name and registration_email in session and redirects onboarding (no change to downstream behavior).

### C. Resend OTP

1. User clicks resend on verify page.
2. auth route posts to /verify-otp/resend with session challenge_id.
3. otp_service.resend_signup_challenge:
   - enforce next_resend_at cooldown
   - enforce resend_count max
   - enforce locked/expired status
   - rotate OTP hash and expiry
   - send mail and update status
4. Route returns success or wait/locked message.

## Resend, Rate Limit, and Lockout Interaction Model

Use layered controls so behavior is predictable and minimally invasive:

| Layer | Scope | Recommended default | Action |
|---|---|---|---|
| flask-limiter route limits | Per IP/request path | register: existing 5/min; verify: 20/min; resend: 5/10min | 429 hard block |
| otp_challenges.next_resend_at | Per challenge/email | 60s cooldown | deny resend until cooldown ends |
| otp_challenges.resend_count | Per challenge/email | max 5 | deny resend, prompt restart signup |
| otp_challenges.verify_attempt_count + locked_until | Per challenge/email | max 5 wrong attempts; 15m lock | deny verify until lock expires |
| optional anti_spam monitor | Cross-flow abuse signal | monitor mode first | log and later enforce if abuse spikes |

Priority order:

1. Route-level limiter first (cheap protection).
2. Challenge lockout/cooldown second (business rules).
3. Anti-spam signal third (adaptive control, optional in phase 1).

## Failure Handling and Observability

### Failure handling

1. Mail provider failure: challenge remains but marked failed_send, user gets retry guidance, no account created.
2. Expired OTP: status -> expired; ask user to resend or restart signup.
3. Duplicate activation race: rely on unique email in Registration; catch IntegrityError and convert to safe user message.
4. DB transient errors: rollback and flash generic retry message; never reveal internals.

### Observability events (app.logger)

Emit structured logs with event keys:

1. otp.challenge.created
2. otp.send.success
3. otp.send.failure
4. otp.verify.success
5. otp.verify.failure
6. otp.challenge.locked
7. otp.challenge.expired

Recommended log fields:

1. challenge_id
2. email_hash (never raw email in high-verbosity logs)
3. ip (normalized)
4. attempts, resend_count
5. latency_ms for send
6. error_code

Optional QA dashboard query can be built from otp_challenges statuses before adding a dedicated metrics stack.

## Migration Strategy (Manual Scripts in database/)

### Script 1: database/migrate_otp_challenges.py

1. Initialize Flask app + db like migrate_anti_spam_phase2.py pattern.
2. Use inspector to check table existence.
3. Create table only if missing.
4. Create indexes idempotently (check name before create).
5. Print clear migration summary and exit code.

### Script 2: database/migrate_config_otp_defaults.py (optional)

Document and validate required env vars (no secrets in code):

1. MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER, MAIL_USE_TLS
2. OTP_EXPIRES_MINUTES, OTP_RESEND_COOLDOWN_SECONDS, OTP_MAX_VERIFY_ATTEMPTS, OTP_LOCK_MINUTES, OTP_MAX_RESENDS

### Script 3: database/cleanup_otp_challenges.py (optional)

Manual cleanup utility for old terminal rows to keep DB lean.

## Phased Integration Order (Roadmap Ready)

### Phase 1: Schema foundation

1. Add OtpChallenge model and migration script.
2. Run migration in local and staging.
3. Verify indexes and idempotency.

Exit criteria: table exists, migration re-run is safe.

### Phase 2: Mail and config boundary

1. Add MAIL_* and OTP_* config keys.
2. Implement mail_adapter with mocked tests.
3. Validate provider failure mapping.

Exit criteria: email send path works in test mode and production-like env.

### Phase 3: OTP service core

1. Implement start/resend/verify/cleanup in otp_service.
2. Add unit tests for expiry, wrong attempts, lockout, resend cooldown.
3. Add structured logs.

Exit criteria: service-level tests cover all state transitions.

### Phase 4: Auth route integration

1. Wire /register and /verify-otp to otp_service.
2. Add /verify-otp/resend endpoint.
3. Update verify template to show resend + cooldown status.

Exit criteria: signup -> email OTP -> verify -> onboarding works end-to-end.

### Phase 5: Rate-limit and abuse hardening

1. Add/adjust route limiter rules for verify and resend.
2. Enable optional anti-spam monitoring for OTP abuse signals.
3. Tune thresholds based on logs from staging.

Exit criteria: abusive resend/verify bursts are blocked without harming normal users.

### Phase 6: QA and rollout safety

1. Update route/integration tests currently tied to hardcoded OTP behavior.
2. Add mail mock integration tests for happy path and failure path.
3. Run full pytest suite and deploy to preview before production.

Exit criteria: regression suite green and OTP flow stable on Vercel preview.

## Notes for Minimal Disruption

1. Keep existing session keys registration_name and registration_email after successful verification so downstream routes remain unchanged.
2. Keep existing auth blueprint endpoints except adding resend endpoint.
3. Avoid introducing queues/background workers in v1.4; keep synchronous send with robust error handling and retry UX.
4. Maintain manual migration workflow in database/ and avoid flask db migrate/upgrade.
