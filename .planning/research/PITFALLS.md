# Pitfalls Research — v1.5 SMTP Pivot

## Pitfalls to avoid

1. Confusing TLS and SSL settings for SMTP ports.
2. Treating a missing app password as a transient provider outage instead of configuration failure.
3. Logging SMTP credentials or full connection details.
4. Changing auth-route behavior while swapping transports.
5. Assuming Gmail SMTP scales indefinitely without quotas or account limits.

## Prevention strategy

- Validate SMTP config before attempting delivery.
- Keep outcome categories explicit (`misconfigured`, `timeout`, `network_error`, `provider_rejected`).
- Preserve the existing register/resend/session contract and prove it with regression tests.
- Document Gmail App Password prerequisites before the production cutover step.# Domain Pitfalls: v1.4 OTP Email Reliability & QA

**Domain:** Email OTP in Flask auth on Vercel  
**Researched:** 2026-04-14  
**Confidence:** HIGH for repository evidence, MEDIUM for provider/runtime behavior

## Scope and Roadmap Ownership Note

The milestone is initialized but roadmap phases are not yet defined (`.planning/STATE.md` shows `total_phases: 0`).
To assign ownership now, this document uses **proposed v1.4 phase buckets**:

- **OTP-1: Security Core** (OTP model, secrets, token semantics)
- **OTP-2: Email Delivery Reliability** (provider integration, timeout/retry, operational resilience)
- **OTP-3: Abuse Controls** (rate limits, resend cooldown, disposable-email risk controls)
- **OTP-4: Auth Flow Hardening** (session hygiene, anti-enumeration UX, idempotency)
- **OTP-5: QA and Observability** (tests, metrics, alerting, regression gates)

## Critical Pitfalls

| ID | Pitfall | Severity | Concrete detection signals in this repo | Prevention | Mitigation | Phase owner |
|---|---|---|---|---|---|---|
| OTP-P1 | Hardcoded OTP path remains reachable | **Critical** | `routes/auth.py:185` flashes demo `123456`; `routes/auth.py:202` falls back to `session.get('otp_code', '123456')`; tests assert fixed values in `tests/test_csrf_and_routes.py:530` and `tests/test_csrf_and_routes.py:552` | Generate OTP with CSPRNG (`secrets`), never with static fallback | Remove all default/static OTP values; fail closed when challenge is missing; rotate OTP on each resend | OTP-1 |
| OTP-P2 | No server-side OTP lifecycle (expiry/single-use/attempt state) | **Critical** | OTP is held in session (`routes/auth.py:196`, `routes/auth.py:202`); no OTP challenge model in `models/models.py` | Persist OTP challenge state server-side (hashed code, expiry, consumed flag, attempts, cooldown) | Add OTP challenge table + indexes; invalidate old token when issuing new one; enforce one-time use | OTP-1 |
| OTP-P3 | Verify endpoint can be brute-forced | **Critical** | Rate limits exist on login/register (`routes/auth.py:12`, `routes/auth.py:108`) but none on `/verify-otp` (`routes/auth.py:191`) | Add route-level, identity-level, and IP-level throttles for verify/resend | Enforce max attempts per challenge, lockout/backoff, and explicit 429 handling | OTP-3 |
| OTP-P4 | Session trust boundary too weak for OTP gate | **Critical** | `config.py:23` has hardcoded `SECRET_KEY` fallback; OTP/pending registration stored in session; no explicit `SESSION_COOKIE_SECURE` / `SESSION_COOKIE_SAMESITE` config in `config.py` | Use env-only strong secret, secure cookie settings, and server-side OTP challenge state | Rotate secret, invalidate active sessions, move OTP state out of cookie-backed session | OTP-1 + OTP-4 |

## High Pitfalls

| ID | Pitfall | Severity | Concrete detection signals in this repo | Prevention | Mitigation | Phase owner |
|---|---|---|---|---|---|---|
| OTP-P5 | Email delivery not actually wired for production | **High** | Flask-Mail exists (`extensions.py:9`, `app.py:71`) but `config.py` has no `MAIL_*` settings; no `mail.send`/`Message(...)` usage found in code | Implement explicit OTP delivery service and provider config in env | Add `MAIL_SERVER/PORT/USERNAME/PASSWORD`, delivery timeout, retries, and provider error taxonomy | OTP-2 |
| OTP-P6 | Resend OTP flow is missing despite milestone scope | **High** | Milestone requires resend/cooldown (`.planning/PROJECT.md:19`, `.planning/PROJECT.md:42`), but auth routes show no resend endpoint | Define resend API with strict cooldown and quota policy | Add `/resend-otp` route, rolling cooldown, per-email + per-IP quotas, and audit logs | OTP-3 |
| OTP-P7 | Enumeration risk via auth error messaging | **High** | Login and register reveal account state (`routes/auth.py` messages for wrong password, unregistered email, duplicate email) | Return generic client messages, keep specifics in logs | Normalize response body/time for existence and non-existence cases | OTP-4 |
| OTP-P8 | Vercel timeout and cold-start behavior not accounted for in OTP send path | **High** | No send timeout/retry policy module; no asynchronous fallback queue; milestone targets Vercel production | Use short outbound timeout, bounded retries, and failure-safe UX | Introduce provider abstraction with timeout budget + optional deferred retry worker | OTP-2 |
| OTP-P9 | Verify flow is not idempotent-safe under duplicate/concurrent submit | **High** | `verify_otp` inserts `Registration` then commits (`routes/auth.py:204+`), without explicit `IntegrityError` handling on duplicate email | Design verify as idempotent operation keyed by challenge | Catch unique constraint races, return safe success or deterministic failure path | OTP-4 |

## Medium Pitfalls

| ID | Pitfall | Severity | Concrete detection signals in this repo | Prevention | Mitigation | Phase owner |
|---|---|---|---|---|---|---|
| OTP-P10 | OTP observability blind spots | **Medium** | Access logging exists (`app.py`), but no OTP-specific structured events/metrics table or counters | Define OTP event schema (`issued`, `send_failed`, `verify_failed`, `locked`) | Add dashboards/alerts for delivery failure rate, retry spikes, and lockout anomalies | OTP-5 |
| OTP-P11 | Test coverage does not enforce OTP reliability guarantees | **Medium** | OTP tests are basic happy/wrong/no-pending checks in `tests/test_csrf_and_routes.py`; no tests for expiry, resend cooldown, lockouts, provider failure, concurrency | Create OTP test matrix before implementation freeze | Add unit + route + integration tests with mocked mail provider and deterministic clocks | OTP-5 |

## Specific Note: Temporary/Disposable Email Providers and Abuse Risk

Disposable and temporary inboxes are a direct abuse vector for OTP-based registration and account farming.
OWASP explicitly flags temporary email abuse and recommends risk-based controls.

**What this means for this repo now:**

- Current registration policy requires `@gmail.com` (`routes/auth.py`) which blocks many known disposable domains, but this is **not sufficient**.
- Abuse can still occur via:
  - Newly created throwaway Gmail accounts
  - Alias churn (`+tag` variants) for repeated account creation
  - Bot-driven account farms with real inboxes

**Recommended control strategy (do not rely on one control):**

1. Domain intelligence: maintain/update a disposable-domain deny/suspect list.
2. Risk tiering: do not hard-block everything; route suspicious domains/accounts into stricter friction.
3. Behavioral controls: tighter resend/verify quotas for high-risk domains and first-seen fingerprints.
4. Trust progression: require additional proof for sensitive actions until account trust increases.
5. Monitoring: alert on spikes by domain, MX provider, ASN, and creation velocity.

**Owner:** OTP-3 (Abuse Controls), with OTP-5 for monitoring and regression checks.

## Phase-Specific Warnings

| Proposed phase | Likely pitfall | Mitigation priority |
|---|---|---|
| OTP-1 Security Core | Shipping with static fallback or client-side-only OTP semantics | Highest |
| OTP-2 Email Delivery Reliability | Provider misconfiguration/timeouts discovered only after deploy | Highest |
| OTP-3 Abuse Controls | Verify/resend endpoints exploited for brute force or resource drain | Highest |
| OTP-4 Auth Flow Hardening | Enumeration and race-condition regressions | High |
| OTP-5 QA and Observability | No early signal for delivery or abuse regressions | High |

## Sources

- OWASP Authentication Cheat Sheet (login throttling, anti-enumeration, logging): <https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html>
- OWASP Multifactor Authentication Cheat Sheet (OTP handling and storage): <https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html>
- OWASP Email Validation and Verification Cheat Sheet (temporary email abuse): <https://cheatsheetseries.owasp.org/cheatsheets/Email_Validation_and_Verification_Cheat_Sheet.html>
- Flask Sessions / Config docs (secret key and cookie semantics): <https://flask.palletsprojects.com/en/3.0.x/quickstart/#sessions> and <https://flask.palletsprojects.com/en/3.0.x/config/#builtin-configuration-values>
- Flask-Limiter docs (production storage and route-level limits): <https://flask-limiter.readthedocs.io/en/stable/>
- Vercel Python Runtime and Function Limits: <https://vercel.com/docs/functions/runtimes/python> and <https://vercel.com/docs/functions/limitations>

## Top 5 non-negotiables for v1.4

1. Eliminate all hardcoded/default OTP values and generate OTP via cryptographic randomness only.
2. Enforce server-side OTP challenge lifecycle: hashed OTP, short TTL, single-use, attempt limits, and explicit cooldown.
3. Protect `/verify-otp` and `/resend-otp` with layered rate limits (IP + identity + challenge) and lockout/backoff behavior.
4. Ship production email delivery with env-only secrets, strict timeout budget, retry policy, and clear failure handling.
5. Gate release on OTP reliability tests (expiry/resend/lockout/provider-failure/concurrency) plus OTP observability alerts.
