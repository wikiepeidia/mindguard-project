# Architecture Integration Strategy

**Domain:** Cybersecurity education + anti-scam reporting platform (Flask monolith)
**Researched:** 2026-03-19
**Research mode:** Ecosystem + brownfield integration
**Overall confidence:** HIGH

## Executive Recommendation

Integrate new capabilities as **additive slices** around existing blueprints, not by rewriting the request handlers. The current structure (single Flask app, blueprint boundaries, SQLAlchemy models, helper utilities) is already suitable for incremental hardening.

To minimize regression risk:
1. Introduce anti-spam through a dedicated policy/service layer that wraps current report submission flow.
2. Add persistence for anti-spam telemetry in new tables and nullable columns only; do not mutate existing semantics first.
3. Modernize UI through shared design tokens and page-by-page migration, preserving route names, template names, and form payload contracts.
4. Roll out in observe -> enforce phases (log-only first, then soft blocks, then strict limits).

## Current Architecture Constraints (from codebase)

- Composition root is `app.py` with blueprint registration for `main`, `scammer`, `chatbot`, `quiz`, `auth`, `admin`.
- Critical report path is `routes/scammer.py::report_scammer()` and currently mixes validation, CAPTCHA checks, file upload, encryption, and DB writes in one function.
- Identity context is session-based (`session['registration_email']`, `session['is_admin']`, `session['reporter_id']`).
- Existing anti-abuse is CAPTCHA-only (Cloudflare + math fallback) and does not include rate limits or behavior scoring.
- UI is server-rendered Jinja + static CSS/JS and can be modernized without API re-platforming.

Implication: architecture should add thin integration seams around existing functions before any deeper refactor.

## Target Integration Architecture

### Component Boundaries

| Component | Responsibility | Communicates With | Change Type |
|-----------|----------------|-------------------|-------------|
| Flask App Assembly (`app.py`) | Register extensions/blueprints and global middleware hooks | Blueprints, extensions | Small update |
| Routes (`routes/*.py`) | Request parsing, response rendering, orchestration | Services, models, utils | Minimal edits |
| Anti-Spam Service (`services/anti_spam_service.py`) | Risk evaluation, decision (allow/challenge/block), reason codes | Policy engine, telemetry repo, config | New |
| Policy Engine (`utils/anti_spam_rules.py`) | Deterministic rules: velocity, IP/cookie reputation, duplicate fingerprinting | Request metadata + historical counters | New |
| Telemetry Repository (`services/abuse_repository.py`) | Query/write anti-spam events and counters | New abuse tables + existing report tables | New |
| Privacy Utility (`utils/privacy.py`) | Canonical masking and hashing for display + storage-safe logs | Routes, templates, helpers | New (or merge into helpers) |
| UI Design System (`static/css/tokens.css`, shared partials) | Color/type/spacing/motion tokens for modernized light UI | All page-level CSS files, base template | New + incremental adoption |

### Data Model Additions (manual migration scripts)

Use additive schema changes only (manual scripts in `database/`):

1. `abuse_events`
- `id`, `created_at`
- `event_type` (report_submit, login_attempt, register_attempt)
- `ip_hash`
- `cookie_id`
- `fingerprint_hash`
- `route_name`
- `decision` (allow, challenge, block)
- `risk_score`, `reason_codes` (json/text)

2. `abuse_counters`
- `id`, `window_start`, `window_end`
- `scope_type` (ip, cookie, fingerprint, ip_cookie)
- `scope_key_hash`
- `event_type`
- `count`

3. Optional additive columns on `scammer_reports`
- `submit_ip_hash` nullable
- `submit_cookie_id` nullable
- `spam_risk_score` nullable
- `spam_flags` nullable text/json

All new fields default nullable to avoid write-path breakage.

## Integration Patterns to Use

### Pattern 1: Route-Guard Wrapper (recommended)

**What:** Keep existing route logic, but add one guard call at top of POST handlers.

**How:**
1. Build normalized request context (`ip`, `cookie_id`, `user/session`, `payload fingerprint`).
2. Call `anti_spam_service.evaluate(context)`.
3. Branch by decision:
- `allow`: continue current flow unchanged.
- `challenge`: force CAPTCHA regeneration and continue only after success.
- `block`: return graceful error and log event.
4. Write telemetry event for all outcomes.

**Why low risk:** Existing validation/business logic remains intact; anti-spam is additive and removable by feature flag.

### Pattern 2: Observe-Then-Enforce Rollout

**What:** Deploy policy in shadow mode first.

**Stages:**
1. `monitor`: evaluate + log only, never block.
2. `soft_enforce`: block only clearly abusive thresholds.
3. `strict_enforce`: full threshold policy.

**Why low risk:** Prevents accidental user lockout from incorrect thresholds.

### Pattern 3: Feature-Flagged UI Contract Preservation

**What:** Introduce a design token layer while preserving existing template variables and route endpoints.

**How:**
1. Add token stylesheet and shared UI partials in `templates/partials/`.
2. Migrate page CSS incrementally (`report_scammer`, `quiz`, `index`) without changing endpoint contracts.
3. Keep form field names backward-compatible during migration.

**Why low risk:** Frontend appearance can evolve independently from backend behavior.

## End-to-End Data Flow (target)

### Flow A: Report Submission with Anti-Spam

1. Browser submits `POST /scammer/report`.
2. Route extracts anti-spam context (IP, cookie id, payload fingerprint, route metadata).
3. `AntiSpamService.evaluate()` executes:
- velocity checks (per IP, per cookie, per fingerprint windows)
- duplicate-content checks
- recent block/challenge history checks
4. Decision returned:
- allow -> existing CAPTCHA + report persistence path
- challenge -> force CAPTCHA path and retry
- block -> flash message + redirect, no report write
5. Telemetry is stored in `abuse_events` and counters updated.
6. Existing `ScammerReport` and leaderboard updates proceed only on allow/challenge pass.

### Flow B: Login/Register Hardening (same pattern)

1. `POST /login` or `POST /register` calls anti-spam evaluation before credential/account checks.
2. High-risk actors receive challenge/block based on stage.
3. Telemetry retained for correlation with report abuse.

### Flow C: Privacy-Safe Display

1. Routes pass canonical masked values from `utils/privacy.py`.
2. Templates render masked phone/account identifiers consistently.
3. Raw sensitive values are never logged in anti-spam telemetry.

## Build Order for Roadmap Sequencing

1. **Phase 1: Instrumentation Foundation (no user-facing behavior changes)**
- Add anti-spam tables and migration scripts.
- Add service/policy modules and logging hooks in report/login/register routes in monitor mode.
- Add config flags: `ANTI_SPAM_MODE`, threshold defaults.

2. **Phase 2: Report Flow Enforcement (soft)**
- Enable `challenge` then limited `block` in `routes/scammer.py`.
- Add admin diagnostics panel for abuse events.
- Validate false-positive rate before expansion.

3. **Phase 3: Auth Flow Enforcement**
- Reuse same service on login/register endpoints.
- Add per-route threshold profiles.

4. **Phase 4: UI Design System Foundation**
- Add tokenized CSS layer and base layout modernization (light-first).
- No behavior changes; visual regression checks only.

5. **Phase 5: Page-by-Page UX Modernization**
- Modernize report page and quiz one-question-per-page flow.
- Preserve existing form contract and route names.

6. **Phase 6: Tightening + Cleanup**
- Remove dead CSS/JS after migration.
- Promote strict anti-spam mode if metrics are healthy.

## Regression Control Plan

- Keep all existing route URLs and HTTP methods unchanged.
- Keep existing form field names while introducing new UI components.
- Use additive DB migrations only; no destructive schema edits in same milestone.
- Gate anti-spam decisions behind environment/config flags.
- Add route-level smoke tests for:
  - `GET/POST /scammer/report`
  - `GET/POST /login`
  - `GET/POST /register`
  - leaderboard and profile rendering
- Add golden-path snapshots for modernized templates (desktop + mobile breakpoints).

## Anti-Patterns to Avoid

1. **Big-bang rewrite of `routes/scammer.py`**
- High chance of breaking report creation, evidence upload, and leaderboard sync.

2. **Hard blocking from day one**
- Causes false-positive lockouts without baseline telemetry.

3. **Mixing anti-spam logic directly into templates/JS**
- Security decisions must remain server-side and auditable.

4. **Replacing session identity model during same milestone**
- Separate concern; increases blast radius.

## Scalability Path

| Concern | Current (SQLite, low scale) | Mid Scale | High Scale |
|---------|-----------------------------|-----------|------------|
| Rate counters | SQLite counters acceptable | Move counters to Redis | Redis + async analytics pipeline |
| Rule evaluation | Inline synchronous | Cached thresholds + precomputed windows | Dedicated abuse service/process |
| UI delivery | Static files from Flask | Add CDN/cache headers | Split static hosting + edge cache |

## Confidence and Risk Notes

- **HIGH confidence:** Blueprint-centric additive integration, feature-flag rollout, and monitor-then-enforce strategy fit current architecture.
- **MEDIUM confidence:** Exact abuse thresholds; must be tuned from real traffic.
- **MEDIUM confidence:** Need final decision on using custom counters vs Flask-Limiter directly for all routes.

## Sources

### Codebase evidence (HIGH)
- `app.py`
- `routes/scammer.py`
- `routes/auth.py`
- `routes/main.py`
- `models/models.py`
- `.planning/PROJECT.md`
- `.planning/codebase/ARCHITECTURE.md`
- `.planning/codebase/STRUCTURE.md`

### External references (MEDIUM)
- Flask blueprints (official): https://flask.palletsprojects.com/en/stable/blueprints/
- Flask sessions and request lifecycle (official): https://flask.palletsprojects.com/en/stable/quickstart/#sessions
- Flask-Limiter docs (v4.1.1 page header observed): https://flask-limiter.readthedocs.io/en/stable/
