# Stack Research — v1.5 SMTP Pivot

## Existing stack to reuse

- `Flask-Mail` is already installed and initialized in `extensions.py`.
- `services/otp_email_delivery.py` already centralizes OTP delivery status normalization.
- `config.py` already owns provider/env configuration for OTP delivery.

## Recommended stack additions

- Use `Flask-Mail` as the SMTP transport layer.
- Add provider-neutral env keys for SMTP host, port, username, password, TLS/SSL, and default sender.
- Keep `EMAIL_PROVIDER` as the transport selector, but add `smtp` as the production path.

## Gmail App Password compatibility notes

- Gmail app passwords require Google 2-Step Verification.
- Gmail app passwords are mailbox credentials, not OAuth tokens.
- This path does not require owning a sending domain, so it works with the current Vercel-only setup.

## Do not add

- Another mail library unless `Flask-Mail` proves technically insufficient.
- Domain-dependent API providers as the new primary path for this milestone.# Technology Stack — Milestone v1.4 OTP Email Reliability & QA

**Project:** MindGuard v2  
**Researched:** 2026-04-14  
**Scope:** Production OTP email for Flask + SQLAlchemy + NeonDB PostgreSQL + Vercel serverless

## Current codebase findings (impacting OTP production-readiness)

- `routes/auth.py` currently flashes OTP demo and verifies against `session.get('otp_code', '123456')`; hardcoded fallback means bypass risk.
- OTP state is stored in Flask session, not in DB; this is weak for replay prevention, auditability, and concurrent verify/resend control.
- `extensions.py` + `app.py` already initialize `Flask-Mail` (`mail = Mail()`, `mail.init_app(app)`), so SMTP path exists technically.
- `config.py` has no mail provider configs yet (`MAIL_*`, `RESEND_API_KEY`, etc. are absent).
- `models/models.py` has no OTP challenge table.
- Existing tests in `tests/test_csrf_and_routes.py` still assert OTP `123456`, so test suite currently reinforces non-production behavior.

## Stack additions/changes needed now (for this exact environment)

### 1) Add OTP persistence and verification layer in PostgreSQL (NeonDB)

Create a new model (and manual migration script in `database/`, per project rule) named for example `EmailOtpChallenge`:

| Field | Type | Purpose |
|---|---|---|
| id | UUID/BigInt PK | Challenge identity |
| email | String (indexed) | Recipient |
| purpose | Enum/String | `register`, later extend `reset_password` |
| otp_hash | String | Hashed OTP only (never plaintext) |
| otp_salt | String | Per-challenge salt |
| expires_at | DateTime (indexed) | TTL |
| consumed_at | DateTime nullable | One-time use marker |
| attempts_used | Integer | Failed verify count |
| max_attempts | Integer | Lock threshold |
| resend_count | Integer | Abuse control |
| cooldown_until | DateTime nullable | Resend cooldown |
| last_sent_at | DateTime | Observability |
| provider | String | `resend`, `ses`, `smtp_gworkspace`, etc. |
| provider_message_id | String | Delivery tracing |
| created_at | DateTime | Audit |
| updated_at | DateTime | Audit |

Recommended indexes/constraints:

- Unique active challenge per `(email, purpose)` where `consumed_at IS NULL` and `expires_at > now()`.
- Index on `(email, purpose, expires_at)` for fast verify and cleanup.

### 2) Add provider abstraction (do not hardwire route to one vendor)

Create service boundary:

- `services/otp_service.py`: issue, resend, verify OTP, enforce limits.
- `services/email_sender.py`: provider-agnostic send interface.
- `services/email_providers/resend_api.py` (primary).
- `services/email_providers/smtp.py` (fallback/dev/staging compatibility with existing Flask-Mail).

This keeps v1.4 shippable while preserving easy migration to SES/SendGrid/Postmark later.

### 3) Add config surface in `config.py`

Minimum env/config keys:

- `EMAIL_PROVIDER` (`resend_api`, `smtp`, `ses_api`, ...)
- `DEFAULT_FROM_EMAIL`
- `OTP_TTL_SECONDS` (default 300)
- `OTP_MAX_ATTEMPTS` (default 5)
- `OTP_RESEND_COOLDOWN_SECONDS` (default 60)
- `OTP_MAX_RESENDS_PER_WINDOW` (default 3)
- `OTP_RESEND_WINDOW_SECONDS` (default 900)
- `OTP_HASH_PEPPER` (secret)
- `EMAIL_SEND_TIMEOUT_SECONDS` (default 5)
- Provider-specific:
  - `RESEND_API_KEY`
  - or SMTP keys (`MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME`, `MAIL_PASSWORD`)
  - optional future SES keys/role

### 4) Update tests to match production behavior

Current tests are OTP-demo oriented. Add:

- Unit tests for OTP issue/verify/resend and expiry.
- Route tests for:
  - success path
  - wrong OTP increments attempts
  - expired OTP rejected
  - max attempts lockout
  - resend cooldown and resend cap
  - one-time consume behavior
- Provider integration tests with mocked HTTP send (Resend API) and mocked SMTP fallback.
- Race test: two concurrent verifies, only one succeeds.

## Security requirements (non-negotiable)

| Control | v1.4 requirement |
|---|---|
| OTP generation | `secrets`-based cryptographic randomness, 6-digit numeric OTP |
| Storage | Store hash only (`HMAC-SHA256` or equivalent with per-challenge salt + server pepper) |
| TTL | 5 minutes default |
| Attempts | Max 5 verify attempts/challenge |
| Resend | 60s cooldown, max 3 resends per 15 minutes |
| One-time use | Set `consumed_at` atomically on successful verify |
| Replay prevention | Reject if `consumed_at` set or `expires_at < now()` |
| Race prevention | Verify inside DB transaction (`SELECT ... FOR UPDATE` or atomic conditional update) |
| Session trust | Do not store authoritative OTP in session/cookie |
| Logging | Never log OTP plaintext; log only challenge id/provider message id |
| Response messages | Keep generic to reduce account enumeration |
| Transport | TLS required provider-side (SMTP TLS or HTTPS API) |

Implementation note for this codebase:

- Flask session is signed, not suitable as OTP source-of-truth. Move OTP truth to NeonDB immediately.
- Existing `Flask-Limiter` should also be applied to `/verify-otp` and future `/resend-otp`.

## Option 1: Gmail SMTP / Google Workspace SMTP

### Practical fit

Good for very early stage or internal environments, but weak as long-term production OTP backbone.

### Key limits and constraints from Google docs

- Gmail SMTP (`smtp.gmail.com`) sending limit: 2,000 messages/day.
- Google Workspace SMTP relay (`smtp-relay.gmail.com`): up to 10,000 recipients/day per user.
- Google can suspend sending up to 24 hours after limit breach.
- Less secure app/password-only patterns are deprecated; OAuth-first direction and stricter policies after 2025.
- App Password requires 2-Step Verification and is explicitly not recommended by Google as a primary long-term pattern.
- Deliverability to Gmail now strongly depends on SPF/DKIM/DMARC and sender behavior policies.

### Verdict for MindGuard v1.4

- Can be fallback or temporary bridge.
- Should not be primary target architecture for growth scenarios.

## Option 2: Transactional email providers

### Comparison for OTP-focused workloads

| Provider | Entry pricing snapshot (2026-04) | Throughput controls / limits | Deliverability posture | Complexity | MindGuard fit |
|---|---|---|---|---|---|
| Resend | Free: 3,000/mo + 100/day; Pro: $20/50k; Pro 100k: $35; Scale starts $90/100k | API + SMTP; batch up to 100/call; idempotency key (24h) | Strong DX for transactional, fast integration | Low | Best default for v1.4 |
| SendGrid | Free trial 100/day for 60 days; Essentials from $19.95; Pro from $89.95 | Endpoint-specific API rate limits; headers + `429` handling | Mature ecosystem, strong enterprise path | Medium | Good growth fallback |
| Postmark | Free dev tier 100/mo; paid starts $15; overage by plan | Batch endpoint supports up to 500 messages/call | Transactional-first reputation, strong inbox focus | Low/Medium | Excellent deliverability-first alternative |
| Mailgun | Free 100/day; Basic $15/10k; Foundation $35/50k; Scale $90/100k | Has API rate limits (not publicly fixed in one number), SMTP+HTTP | Mature, feature-rich; good at scale | Medium | Good if team needs advanced controls |
| AWS SES | $0.10/1,000 outbound (+ data), free tier message credits in first year | Explicit per-account quotas: `Max24HourSend`, `MaxSendRate`, sandbox vs production access | Great at high scale if configured well | Medium/High (AWS ops) | Cost leader at large volume |

### SES-specific note (important)

- Account can be sandbox or production in each region (`ProductionAccessEnabled`).
- In sandbox: only verified identities can receive.
- Quotas are account-specific and queryable via CLI/API (`get-account`, `get-send-quota`), including per-second and 24h limits.

## Option 3: Temporary/disposable email services

Examples reviewed: Mailinator, Ethereal, Mailtrap Email Sandbox.

### Should they be used?

- Dev/QA/Staging: Yes, for test workflow automation and safe capture of OTP emails.
- Production user verification: No.

### Why not for production OTP

- Ethereal is explicitly a fake SMTP service where emails are never delivered to real recipients.
- Disposable/public inbox models are not trustworthy identity channels.
- They do not represent real deliverability behavior for Gmail/Outlook/Yahoo inboxes.
- Security/compliance risk for real user verification data.

### Practical note for this codebase

Current registration already forces `@gmail.com`, so disposable-domain abuse is partly reduced by design. Still, disposable services remain test-only tools.

## Recommended provider strategy by stage and scale

| Stage | Expected scale | Recommended provider | Transport | Reason |
|---|---|---|---|---|
| Local dev | 0 real users | Mailtrap or Ethereal | SMTP sandbox | Fast debugging without real sends |
| Staging/UAT | Internal QA + controlled testers | Same provider as prod (Resend) + optional Mailinator inbox assertions | HTTP API primary | Detect template/flow issues before prod |
| Production now (v1.4) | ~50 CCU, low-to-moderate OTP volume | Resend Pro | HTTP API | Best reliability/effort ratio on Vercel serverless |
| Growth | 100k to 1M+ OTP/month | Keep abstraction; evaluate SES or SendGrid/Postmark based on KPI | HTTP API | Control cost vs deliverability/support |
| Very high scale | >1M OTP/month | SES (cost focus) or SendGrid/Postmark enterprise (managed deliverability focus) | HTTP/API | Long-term optimization |

## Cost, throughput, deliverability tradeoffs (practical)

- Gmail/Workspace SMTP:
  - Cost: often appears “free” under Workspace subscription.
  - Throughput: hard daily limits; suspension risk after spikes.
  - Deliverability: acceptable for low volume, but weaker control for app-transactional growth.

- Resend/Postmark:
  - Cost: higher than SES at large volume.
  - Throughput: sufficient for startup/SMB transactional OTP.
  - Deliverability: generally stronger out-of-box for transactional flows and easier operationally.

- SendGrid/Mailgun:
  - Cost: mid/high depending features and volume.
  - Throughput: enterprise-ready with mature event/rate-limit handling.
  - Deliverability: strong when properly configured; more knobs and operational surface.

- SES:
  - Cost: typically lowest at scale.
  - Throughput: explicit account quotas and strong scaling path.
  - Deliverability: excellent potential, but requires stronger AWS operational maturity and reputation management discipline.

## Vercel/serverless compatibility constraints and implications

| Constraint | Implication for OTP stack |
|---|---|
| Stateless function instances | OTP state must be in NeonDB, not session |
| Function time budget and external I/O | Use short outbound timeout (3-5s), fail fast, retry once with jitter |
| Read-only deployment filesystem (except temp areas) | No local durable queue/file-based mail retry |
| High concurrency possible | Make verify consume operation atomic to prevent double-use |
| External network call per request | Prefer provider HTTP APIs for predictable behavior over per-request SMTP handshakes |

Recommended send behavior on Vercel:

- Synchronous send in register/resend route with strict timeout and clear error handling.
- Store challenge before send; on send failure, mark status and allow controlled retry.
- Use idempotency key for provider API to avoid duplicates on retries.

## What NOT to add now (v1.4 scope protection)

1. SMS OTP or authenticator-app MFA.
2. Multi-provider active-active routing orchestration.
3. Dedicated IP purchase/warmup pipeline at current scale.
4. Full async job stack (Celery/RQ + Redis) unless real timeout evidence appears in production metrics.
5. Complex anti-fraud device fingerprint stack beyond current OTP + rate-limit + CAPTCHA baseline.
6. Large auth refactor outside register/verify/resend OTP path.
7. New deployment platform changes (stay with Vercel + NeonDB as required).

## Recommended default for v1.4

Concrete recommendation for this repository and milestone:

1. Primary email provider: Resend via HTTP API.
2. Plan choice: Pro (start at $20/50k), reassess when OTP volume exceeds current bracket.
3. Keep Flask-Mail SMTP adapter only as fallback/dev path, not primary production route.
4. OTP policy:
   - 6-digit cryptographic OTP
   - TTL 5 minutes
   - Max 5 verify attempts
   - Resend cooldown 60 seconds
   - Max 3 resends per 15 minutes
5. Persist OTP challenge in NeonDB with hashed OTP and atomic consume logic.
6. Remove all hardcoded `123456` behavior and update tests to production semantics.
7. Enforce provider authentication + domain setup before go-live:
   - SPF
   - DKIM
   - DMARC
   - TLS transport
8. Add provider abstraction now so SES/SendGrid/Postmark can be switched later without route-level rewrites.

This gives the fastest safe path to production OTP on current Flask + Vercel architecture while preserving scale-up flexibility.

## Sources

- <https://knowledge.workspace.google.com/admin/gmail/gmail-sending-limits-in-google-workspace>
- <https://knowledge.workspace.google.com/admin/gmail/send-email-from-a-printer-scanner-or-app>
- <https://support.google.com/accounts/answer/185833>
- <https://support.google.com/mail/answer/81126>
- <https://resend.com/pricing>
- <https://resend.com/pricing.md>
- <https://resend.com/docs/api-reference/emails/send-email>
- <https://resend.com/docs/api-reference/emails/send-batch-emails>
- <https://resend.com/docs/send-with-smtp>
- <https://sendgrid.com/pricing/>
- <https://www.twilio.com/docs/sendgrid/api-reference/how-to-use-the-sendgrid-v3-api/rate-limits>
- <https://postmarkapp.com/pricing>
- <https://postmarkapp.com/developer/user-guide/send-email-with-api>
- <https://www.mailgun.com/pricing/>
- <https://documentation.mailgun.com/docs/mailgun/user-manual/sending-messages/send-http>
- <https://aws.amazon.com/ses/pricing/>
- <https://docs.aws.amazon.com/cli/latest/reference/ses/get-send-quota.html>
- <https://docs.aws.amazon.com/cli/latest/reference/sesv2/get-account.html>
- <https://docs.aws.amazon.com/cli/latest/reference/sesv2/put-account-details.html>
- <https://mailtrap.io/email-sandbox/>
- <https://ethereal.email/>
- <https://mailinator.com/>

Confidence notes:

- HIGH: Google limits/policies, Vercel limits, Resend pricing/API, SendGrid rate-limit behavior, Postmark/Mailgun published pricing pages.
- MEDIUM: Relative deliverability ranking across providers (depends on sender reputation and setup quality).
- MEDIUM: SES starter quota examples (actual quota is account/region-specific and must be queried per account).
