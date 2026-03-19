# Codebase Concerns

**Analysis Date:** 2026-03-19

## Tech Debt

**Monolithic authentication flow (`routes/auth.py`):**
- Issue: Login, registration, CAPTCHA, OTP verification, profile update, and onboarding live in one large module with duplicated CAPTCHA and session logic.
- Files: `routes/auth.py`
- Impact: Small changes can cause regressions in unrelated auth flows and increase bug-fix lead time.
- Fix approach: Split into focused service functions/modules (`captcha_service`, `otp_service`, `auth_service`) and keep routes thin.

**Route-layer business logic mixed with persistence (`routes/scammer.py`, `routes/main.py`, `routes/chatbot.py`):**
- Issue: Route handlers perform data validation, file handling, business rules, and DB writes directly.
- Files: `routes/scammer.py`, `routes/main.py`, `routes/chatbot.py`
- Impact: Hard to unit test and fragile to change because HTTP and domain logic are tightly coupled.
- Fix approach: Introduce service layer for report ingestion, risk scoring, and chatbot session lifecycle.

**Legacy/incomplete code fragments retained in production files (`routes/admin.py`, `routes/main.py`):**
- Issue: Files include in-code instructions/comments indicating copy-paste and partial replacement workflow.
- Files: `routes/admin.py`, `routes/main.py`
- Impact: Raises maintainability risk and confusion about source of truth.
- Fix approach: Remove scaffolding comments, enforce lint checks, and keep only executable production code.

## Known Bugs

**`datetime` used but not imported in admin approval path:**
- Symptoms: Approving a report can raise `NameError: name 'datetime' is not defined`.
- Files: `routes/admin.py`
- Trigger: POST to `/admin/approve-report/<id>` when leaderboard row exists.
- Workaround: None in runtime; requires code fix (`from datetime import datetime`).

**Test suite references missing AI functions:**
- Symptoms: AI quiz test script imports functions that do not exist.
- Files: `tests/test_ai_quiz.py`, `utils/ai_agent.py`
- Trigger: Run `python tests/test_ai_quiz.py`.
- Workaround: Update test to current API or restore removed functions.

**Potential broken API exposure due missing blueprint registration:**
- Symptoms: `/api/v1/*` endpoints are defined but not reachable in app registration.
- Files: `routes/api.py`, `app.py`
- Trigger: Access `/api/v1/check` or `/api/v1/stats`.
- Workaround: Register `api_bp` in `app.py`.

## Security Considerations

**Hardcoded secrets and credentials in code/config:**
- Risk: Session forgery and credential leakage if source is exposed; weak key rotation posture.
- Files: `config.py`
- Current mitigation: Optional environment-variable override exists.
- Recommendations: Remove all hardcoded defaults for `SECRET_KEY`, admin credentials, and encryption key; fail-fast at startup if secrets are absent.

**Hardcoded OTP value and no expiration policy:**
- Risk: Account takeover and fake-registration abuse.
- Files: `routes/auth.py`
- Current mitigation: CAPTCHA gate before registration.
- Recommendations: Generate cryptographically random OTP, store hashed OTP + expiry + attempt counter server-side, and throttle retries.

**Sensitive registration data stored in client session cookie (including plaintext password):**
- Risk: Data exposure via client-side session artifacts and browser compromise.
- Files: `routes/auth.py`
- Current mitigation: Flask signs session cookie but does not encrypt by default.
- Recommendations: Never store plaintext password in session; use temporary server-side store keyed by nonce.

**Upload path accepts files without strict type/content/size enforcement:**
- Risk: Malware upload, disk exhaustion, or unsafe file hosting.
- Files: `routes/scammer.py`
- Current mitigation: Filename sanitization via `secure_filename`.
- Recommendations: Enforce MIME/extension allowlist, max content length, antivirus scanning, and non-public storage with signed retrieval.

**No explicit CSRF protection for state-changing POST endpoints:**
- Risk: Cross-site request forgery on profile updates, follow/unfollow, report submission, and admin actions.
- Files: `routes/auth.py`, `routes/scammer.py`, `routes/admin.py`, `routes/chatbot.py`
- Current mitigation: CAPTCHA exists only for selected forms.
- Recommendations: Enable CSRF tokens globally (Flask-WTF or equivalent) and validate on all mutating endpoints.

## Performance Bottlenecks

**Search endpoints execute unbounded `contains` scans:**
- Problem: Query cost grows with dataset size; no index-friendly search strategy.
- Files: `routes/main.py`, `routes/api.py`
- Cause: `contains` on multiple text columns with `.all()` materialization.
- Improvement path: Add indexed normalized columns, use pagination and capped results, consider FTS (SQLite FTS5) for text search.

**Large result materialization and per-row processing in dashboard/report screens:**
- Problem: Admin and homepage logic can load and process many records in memory.
- Files: `routes/admin.py`, `routes/main.py`
- Cause: `.all()` plus per-item JSON parsing and transformation in Python loops.
- Improvement path: Paginate aggressively, project only required columns, and precompute derived fields.

**Synchronous external HTTP calls on request path:**
- Problem: User-facing latency increases and threads block when Cloudflare/OpenRouter is slow.
- Files: `routes/auth.py`, `routes/scammer.py`, `utils/chatbot.py`
- Cause: Inline network calls with fixed timeouts and no circuit-breaker/backoff.
- Improvement path: Add resilient retry policy, background jobs for non-critical tasks, and short-circuit fallback cache.

## Fragile Areas

**Session-centric authorization and identity assumptions:**
- Files: `utils/helpers.py`, `routes/auth.py`, `routes/chatbot.py`, `routes/scammer.py`, `routes/admin.py`
- Why fragile: Session keys (`registration_email`, `is_admin`, captcha answers) are used directly across routes without typed auth context.
- Safe modification: Introduce centralized auth/session adapter and route decorators with explicit invariants.
- Test coverage: Missing focused tests for session tampering and privilege escalation paths.

**Mixed encrypted/plain identifier model in scammer flows:**
- Files: `models/models.py`, `routes/scammer.py`, `routes/main.py`, `routes/api.py`
- Why fragile: Both encrypted identifiers and raw identifiers are used in storage and search, increasing inconsistency risk.
- Safe modification: Define one canonical identifier strategy (hashed lookup + separately protected display field).
- Test coverage: No contract tests verifying report deduplication/search consistency.

**Admin critical actions have minimal guardrails:**
- Files: `routes/admin.py`
- Why fragile: Direct record mutation and deletion with simple session boolean checks.
- Safe modification: Add role checks in data layer, audit logs, CSRF, and confirmation constraints.
- Test coverage: No admin authorization regression tests.

## Scaling Limits

**SQLite single-file database for multi-user write-heavy flows:**
- Current capacity: Suitable for low-concurrency local deployment.
- Limit: Write contention and lock contention under burst report/chat traffic.
- Scaling path: Move to PostgreSQL/MySQL with managed backups and connection pooling.

**File evidence storage on local disk under static path:**
- Current capacity: Works for small volumes.
- Limit: Disk growth, backup complexity, and static hosting exposure.
- Scaling path: Move evidence to object storage (S3-compatible) with lifecycle policies.

## Dependencies at Risk

**Missing explicit production WSGI server dependency:**
- Risk: App may run via Flask development server in non-dev contexts.
- Impact: Poor concurrency and weaker operational controls.
- Migration plan: Add `gunicorn`/`waitress` deployment profile and separate dev/prod entrypoints.

**No explicit test tooling dependency in main requirements:**
- Risk: Inconsistent test execution environment across contributors/CI.
- Impact: Silent regressions and low confidence releases.
- Migration plan: Add pinned test stack (`pytest` or keep `unittest` + runner scripts) in dedicated dev requirements.

## Missing Critical Features

**No centralized rate limiting for public and auth-sensitive endpoints:**
- Problem: Brute-force and abuse risk for login, register, report, and chatbot APIs.
- Blocks: Reliable abuse prevention at scale.

**No structured audit logging for admin/security-sensitive actions:**
- Problem: Weak incident investigation and compliance posture.
- Blocks: Forensics and accountability for content moderation/user management.

**No background task queue for slow or non-blocking work:**
- Problem: Long-running I/O remains on request thread.
- Blocks: Predictable latency and horizontal scaling.

## Test Coverage Gaps

**Authentication and authorization security paths are under-tested:**
- What's not tested: CSRF, OTP expiry/retry limits, session tampering, admin privilege boundaries.
- Files: `routes/auth.py`, `routes/admin.py`, `utils/helpers.py`
- Risk: Security regressions can ship undetected.
- Priority: High

**Scammer report upload and moderation paths are under-tested:**
- What's not tested: File validation, deduplication rules, concurrent report updates, approval/rejection side effects.
- Files: `routes/scammer.py`, `routes/admin.py`
- Risk: Data integrity and moderation defects.
- Priority: High

**Search/API performance and correctness not covered by repeatable tests:**
- What's not tested: Query limits, response time boundaries, false positives, large dataset behavior.
- Files: `routes/main.py`, `routes/api.py`
- Risk: Production slowdowns and noisy results.
- Priority: Medium

**AI integration tests are mostly ad-hoc scripts dependent on live external services:**
- What's not tested: Deterministic fallback behavior, timeout handling, failure-mode contract.
- Files: `tests/ai_chat_eval.py`, `tests/test_openrouter_limits.py`, `utils/chatbot.py`
- Risk: Flaky validation and blind spots in resilience behavior.
- Priority: Medium

---

*Concerns audit: 2026-03-19*
