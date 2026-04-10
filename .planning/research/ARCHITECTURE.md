# Architecture Research

**Domain:** Beta 1 Go-Live hardening — rate limiting, AI safety, logging, stress testing, UI fixes on Flask monolith (Vercel serverless + NeonDB PostgreSQL)
**Researched:** 2026-04-10
**Confidence:** HIGH (codebase analysis as primary source, verified against Vercel/Flask constraints)

---

## Standard Architecture

### System Overview (Current — Post v1.1)

```
┌──────────────────────────────────────────────────────────────────┐
│                    Browser / HTTP Client                          │
└────────────────────────────┬─────────────────────────────────────┘
                             │ HTTPS
┌────────────────────────────▼─────────────────────────────────────┐
│               Vercel Edge (sin1 — Singapore)                      │
│               @vercel/python serverless function                  │
│               Read-only filesystem · Ephemeral instances          │
│               10s cold start limit · No shared memory             │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                     app.py (Flask entry point)                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                    Blueprint Layer (routes/)                 │  │
│  │  main · auth · quiz · scammer · chatbot · admin · library   │  │
│  │  api                                                         │  │
│  └───────────────────────────┬─────────────────────────────────┘  │
│  ┌────────────────────────────▼────────────────────────────────┐  │
│  │                    Services Layer (services/)                │  │
│  │  anti_spam.py · leaderboard_integrity.py                    │  │
│  │  sensitive_access_log.py                                     │  │
│  └───────────────────────────┬─────────────────────────────────┘  │
│  ┌────────────────────────────▼────────────────────────────────┐  │
│  │                    Utils Layer (utils/)                      │  │
│  │  chatbot.py · ai_agent.py · helpers.py                      │  │
│  │  encryption.py · privacy_policy.py · quiz_data.py           │  │
│  └───────────────────────────┬─────────────────────────────────┘  │
│  ┌────────────────────────────▼────────────────────────────────┐  │
│  │              Models Layer (models/models.py)                 │  │
│  │              SQLAlchemy ORM · 13 models                      │  │
│  └───────────────────────────┬─────────────────────────────────┘  │
└──────────────────────────────┬───────────────────────────────────┘
                               │ TCP + SSL (NullPool — no connection reuse)
┌──────────────────────────────▼───────────────────────────────────┐
│               NeonDB PgBouncer Pooler (ap-southeast-1)            │
│               → NeonDB PostgreSQL (persistent, shared)            │
└──────────────────────────────────────────────────────────────────┘

                               │ HTTPS (inline, request-blocking)
┌──────────────────────────────▼───────────────────────────────────┐
│               OpenRouter API (AI chatbot + quiz gen)              │
│               Model cascade: Mistral → Qwen → Llama              │
│               Timeout: 15s · No caching · Runs in request thread  │
└──────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Hardening Relevance |
|-----------|----------------|---------------------|
| `routes/chatbot.py` | Chat endpoints: `/send`, `/api`, `/support`, `/rename` | Rate limiting entry point — all 3 AI-calling endpoints |
| `utils/chatbot.py` | AI call logic, fallback, low-quality detection | AI safety fallback — modify system prompts + add hard fallback for sensitive topics |
| `services/anti_spam.py` | Multi-signal rate limiting (account/cookie/IP) | Extend to cover AI chatbot endpoints (currently only covers scammer reports) |
| `services/sensitive_access_log.py` | Audit trail for admin actions (DB-persisted) | Logging baseline — verify it actually fires and records correctly |
| `config.py` | All configuration including `ABUS_*` tuning params | Rate limit thresholds for chatbot, AI fallback behavior flags |
| `app.py` | Flask entry point, blueprint registration | Request logging middleware addition point |
| `templates/base.html` | Master layout inherited by all pages | Privacy banner injection point (homepage only), UI bug fixes |
| `models/models.py` | 13 SQLAlchemy models | Feedback model addition if feedback collection requires persistence |

---

## Recommended Project Structure (Modifications Only)

The v1.2 milestone is a CODE FREEZE. No new top-level directories. Changes are confined to:

```
mindguard_flask_v2/
├── utils/
│   └── chatbot.py              MODIFY — system prompt rewrite + hard sensitive-topic fallback
├── services/
│   └── anti_spam.py            MODIFY — extend evaluate_submission to accept endpoint_type param
│                               OR keep as-is and apply in routes/chatbot.py decorator
├── routes/
│   └── chatbot.py              MODIFY — add rate-limit decorator/check to /send + /api + /support
├── config.py                   MODIFY — add CHATBOT_RATE_* config vars, AI_SENSITIVE_FALLBACK flag
├── templates/
│   ├── base.html               INSPECT — nav dropdown fix (Đăng xuất), Profile hitbox
│   ├── index.html              MODIFY — add privacy policy banner
│   └── chatbot.html            MODIFY — fix bubble chat history persistence
├── models/
│   └── models.py               MAYBE MODIFY — add FeedbackReport model if feedback needs DB
└── app.py                      MAYBE MODIFY — add request_started/request_finished log hooks
```

No new directories. No new blueprint files. The hardening fits within the existing layer boundaries.

---

## Architectural Patterns

### Pattern 1: Decorator-Based Rate Limiting on Blueprint Routes

**What:** A per-route Python decorator that checks DB-persisted rate limit state before calling OpenRouter. Reuses `AntiSpamDecisionService` with a separate threshold config for chatbot vs scammer-report endpoints.

**When to use:** All three AI-calling endpoints: `/chatbot/send`, `/chatbot/api`, `/chatbot/support`.

**Trade-offs:**
- Pro: No new dependencies. Reuses existing `anti_spam.py` infrastructure (DB models, actor canonicalization, cooldown logic already in place).
- Pro: Vercel-compatible — state lives in NeonDB, not memory (ephemeral instances have no shared memory).
- Con: Every chatbot request incurs a DB read (AntiSpamActorState lookup). Acceptable because NeonDB latency is ~5-10ms vs 2-5s for OpenRouter — the DB check is negligible.
- Con: `ABUS_THRESHOLD_COUNT=3` (current default) is tuned for scammer report spam, not chatbot. Chatbot needs a separate threshold (e.g., 20 messages/10min).

**Example:**
```python
# routes/chatbot.py — add before the AI call
from services.anti_spam import AntiSpamDecisionService

_chatbot_limiter = AntiSpamDecisionService(
    window_minutes=10,
    threshold_count=20,   # Separate from report threshold (3)
    cooldown_minutes=5,
)

def chatbot_rate_limit_check(account_id=None, reporter_hash=None, ip=None):
    decision = _chatbot_limiter.evaluate_submission(
        account_id=account_id,
        reporter_hash=reporter_hash,
        ip_address=ip,
        signal_inputs={"account": 1 if account_id else 0, "cookie": 0, "ip": 1},
    )
    return decision.should_cooldown, decision
```

**Config additions to `config.py`:**
```python
CHATBOT_RATE_WINDOW_MINUTES = int(os.environ.get("CHATBOT_RATE_WINDOW", 10))
CHATBOT_RATE_THRESHOLD = int(os.environ.get("CHATBOT_RATE_THRESHOLD", 20))
CHATBOT_RATE_COOLDOWN_MINUTES = int(os.environ.get("CHATBOT_RATE_COOLDOWN", 5))
```

### Pattern 2: Hard Keyword Fallback in `utils/chatbot.py`

**What:** Before calling OpenRouter, or as a post-processing filter on the reply, check if the user message contains sensitive-topic keywords (self-harm, emergency, mental health crisis). If matched, return a pre-written hard-coded response with hotlines (Công an Hà Nội: 113, bank fraud: ngân hàng hotline) instead of or appended to the AI reply.

**When to use:** In `generate_chatbot_reply()` — both pre-AI (block the call) and post-AI (augment the reply).

**Trade-offs:**
- Pro: Zero latency — keyword matching is O(n) string ops, runs in microseconds.
- Pro: Deterministic — cannot be hallucinated away by the LLM.
- Pro: No new dependencies.
- Con: Keyword lists need maintenance as scam tactics evolve.
- Con: False positives possible (educational discussion of sensitive topics triggers hotline). Acceptable for Beta 1.

**The `simple_bot_reply()` in `utils/chatbot.py` already implements this pattern** for financial fraud. The extension is: add a new category for topics that should always surface specific hotlines, and append hotline info even when OpenRouter succeeds.

**Example addition to `utils/chatbot.py`:**
```python
HARD_FALLBACK_KEYWORDS = ("tự tử", "tự làm hại", "không muốn sống", "tuyệt vọng")
HARD_FALLBACK_RESPONSE = (
    "Tôi nhận thấy bạn đang trong tình huống khó khăn. Hãy liên hệ ngay:\n"
    "- Công an Hà Nội: 113\n"
    "- Đường dây hỗ trợ khẩn cấp: 1800 599 920 (miễn phí)\n"
    "Bạn không cần đối mặt một mình."
)

def generate_chatbot_reply(message, system_prompt=None):
    msg_lower = (message or "").lower()
    if any(kw in msg_lower for kw in HARD_FALLBACK_KEYWORDS):
        return HARD_FALLBACK_RESPONSE, {"source": "hard_fallback", "model": None}
    # ... rest of existing logic
```

### Pattern 3: Flask `app.logger` for Request Logging Baseline

**What:** Use Flask's built-in `app.logger` (which writes to stderr → Vercel's log stream) to emit structured log lines at request start/end. No new logging library needed.

**When to use:** In `app.py` using `@app.before_request` / `@app.after_request` hooks for request-level logging. In `routes/chatbot.py` for AI call outcome logging.

**Trade-offs:**
- Pro: `app.logger` already exists in Flask — zero new dependencies.
- Pro: Vercel captures stderr automatically — logs visible in Vercel dashboard under "Functions" → deployment logs.
- Con: Vercel serverless log retention is limited (last 24h on free tier, 7 days on Pro). For audit-grade logs, `SensitiveAccessLog` (DB-persisted) is the right tool — `app.logger` is for operational visibility only.
- Con: No structured JSON logging out of the box. For Beta 1, human-readable is sufficient.

**The critical distinction for this milestone:**
- `app.logger` → operational logs (request tracing, AI call outcomes, errors). Lives in Vercel logs. Ephemeral.
- `SensitiveAccessLog` (DB table) → audit logs (admin actions, PII access). Lives in NeonDB. Persistent.
- The "logging verification" task is about confirming BOTH paths work in production, not adding new logging infrastructure.

**Example `app.py` hook:**
```python
@app.before_request
def log_request_start():
    app.logger.info(f"REQ {request.method} {request.path} ip={request.headers.get('X-Forwarded-For', request.remote_addr)}")

@app.after_request
def log_request_end(response):
    app.logger.info(f"RES {response.status_code} {request.method} {request.path}")
    return response
```

### Pattern 4: Feedback as a DB Model + Simple Form

**What:** A `FeedbackReport` model in `models.py` and a POST endpoint in `routes/main.py` or a new `routes/feedback.py`. No external service. Stores: user email (optional), feedback type (bug/correction/suggestion), message, page URL, created_at.

**When to use:** For the "Báo cáo sai / Góp ý" button in Beta 1. Simple enough to avoid external tools (no Typeform, no Google Forms).

**Trade-offs:**
- Pro: Data stays in NeonDB. Admin can query directly from admin dashboard.
- Pro: No external dependency.
- Con: Requires a new model + migration script (manual, per project convention). Low effort.
- Con: No email notification to admin on new feedback. Admin must check dashboard. Acceptable for Beta 1.

**Vercel constraint respected:** POST to DB works fine. No filesystem writes needed.

---

## Data Flow

### Rate-Limited Chatbot Request Flow

```
User sends message to /chatbot/send
    ↓
Flask session check (login_required decorator)
    ↓
Extract actor signals: account_id from session, IP from X-Forwarded-For
    ↓
AntiSpamDecisionService.evaluate_submission() [DB read + write to anti_spam tables]
    ↓
decision.should_cooldown == True?
  YES → return 429 JSON {"error": "Bạn đang gửi quá nhiều tin nhắn...", "cooldown_until": "..."}
  NO  ↓
Keyword hard-fallback check (HARD_FALLBACK_KEYWORDS)
  MATCH → return hard-coded hotline response immediately (no OpenRouter call)
  NO MATCH ↓
utils.chatbot.query_ai_model_with_meta() → OpenRouter API (2-5s)
    ↓
is_low_quality_ai_reply()? → try next model in cascade
    ↓
AI reply or simple_bot_reply() fallback
    ↓
_persist_chat_exchange() → writes to AiChatMessage (DB)
    ↓
Return JSON response
```

### Logging Verification Flow

```
Request arrives
    ↓
@app.before_request → app.logger.info (stderr → Vercel logs)
    ↓
Route executes
    ↓
@app.after_request → app.logger.info with status code
    ↓
For admin actions: log_sensitive_access() → SensitiveAccessLog (NeonDB)
    ↓
Error? → app.logger.error + Flask default 500 handler
```

### Key Data Flows

1. **Rate limit state persistence:** `AntiSpamActorState` + `AntiSpamEvent` tables in NeonDB. Because Vercel instances are ephemeral (no shared memory), all rate limit state MUST be DB-persisted. The existing `anti_spam.py` already does this — it is Vercel-compatible by design.

2. **AI call outcome:** `reply_meta["source"]` (`"openrouter"` or `"fallback"` or `"hard_fallback"`) + `reply_meta["model"]` are already returned by every endpoint. These should be logged via `app.logger` for monitoring API budget drain.

3. **Feedback submission:** Form POST → `FeedbackReport` model → NeonDB. Admin reads from `/admin` dashboard via SQLAlchemy query.

---

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Beta 1 (100-1,000 CCU) | Current architecture sufficient. Rate limiting prevents OpenRouter budget exhaustion. NullPool + NeonDB PgBouncer handles concurrent connections. |
| 10,000 CCU | OpenRouter calls blocking request threads become bottleneck. Consider async AI calls or a job queue (Celery/RQ). NeonDB compute upgrade needed. |
| 100,000+ CCU | Vercel serverless auto-scales functions horizontally, but each new instance adds NeonDB connections. Migrate to connection pooler with explicit limits. Background AI processing mandatory. |

### Scaling Priorities for Beta 1

1. **First bottleneck: OpenRouter API budget.** Each chatbot call consumes free tier credits. Rate limiting (Pattern 1) is the primary mitigation. Hard fallback (Pattern 2) prevents unnecessary API calls for sensitive topics.
2. **Second bottleneck: NeonDB connection exhaustion.** Config already uses `NullPool` (creates connection per request, closes immediately). This is correct for Vercel. Do NOT change to a standard pool.
3. **Third bottleneck: Vercel cold starts.** 10s limit. Current `app.py` startup is fast (no seed, no heavy init). Flask initialization + DB connection ping is ~500ms. Safe.

---

## Anti-Patterns

### Anti-Pattern 1: In-Memory Rate Limiting

**What people do:** Use `flask-limiter` with the default in-memory storage backend.
**Why it's wrong:** Vercel spawns multiple ephemeral function instances. Each instance has its own memory. A user hitting 10 different instances effectively bypasses the limit — each instance sees 1 request.
**Do this instead:** Use DB-persisted state (NeonDB via existing `AntiSpamActorState` table). The rate limit state is shared across all Vercel instances because they all connect to the same NeonDB.

### Anti-Pattern 2: Writing Logs to the Filesystem

**What people do:** Configure Python `logging.FileHandler` to write to a log file.
**Why it's wrong:** Vercel's filesystem is read-only. `FileHandler` will raise `PermissionError` on any write attempt, breaking the log setup.
**Do this instead:** Write to stderr (`logging.StreamHandler(sys.stderr)`) — Vercel captures this automatically. Use `app.logger` which already defaults to stderr.

### Anti-Pattern 3: Adding `flask-limiter` as a New Dependency

**What people do:** Install `flask-limiter` to handle rate limiting.
**Why it's wrong:** Adds a new dependency during a CODE FREEZE milestone. `flask-limiter` requires a storage backend (Redis for production-grade distributed limiting) — adding Redis contradicts the "no stack changes" constraint. The existing `AntiSpamDecisionService` already has all the primitives needed.
**Do this instead:** Extend `AntiSpamDecisionService` with chatbot-specific config parameters. No new libraries.

### Anti-Pattern 4: Blocking the Request Thread for Stress Testing

**What people do:** Run `locust` or `wrk` against the production Vercel URL during live traffic.
**Why it's wrong:** Vercel serverless will scale out to handle load, but NeonDB free tier has max 104 connections. A stress test generating 50+ concurrent requests can exhaust DB connections, causing 500 errors for real users.
**Do this instead:** Stress test against a local dev server (`python app.py`) using `locust` locally, or use a separate Vercel preview deployment. Identify CCU threshold in a safe environment before going live.

### Anti-Pattern 5: Adding a Background Worker for AI Calls

**What people do:** Propose offloading OpenRouter calls to Celery/RQ to avoid blocking.
**Why it's wrong:** Correct for v2, but out of scope for Beta 1 CODE FREEZE. Celery requires Redis (new infrastructure) and changes the response model from synchronous to polling/websocket. This is a significant architectural change.
**Do this instead:** Keep inline synchronous AI calls for Beta 1. Rate limiting prevents the volume that would make latency a real user problem.

---

## Integration Points

### New vs Modified Components

| Component | Status | What Changes | Why |
|-----------|--------|-------------|-----|
| `utils/chatbot.py` | MODIFY | Add `HARD_FALLBACK_KEYWORDS` list, add pre-check in `generate_chatbot_reply()`, rewrite `DEFAULT_SYSTEM_PROMPT` for plain language | AI safety: hard fallback for sensitive topics; system prompt simplification for Vietnamese everyday users |
| `routes/chatbot.py` | MODIFY | Add rate limit check at top of `send_message()`, `chatbot_api()`, `support_chat()` | Rate limiting: protect OpenRouter budget |
| `config.py` | MODIFY | Add `CHATBOT_RATE_*` config vars (window, threshold, cooldown) | Config-driven rate limits, tunable via Vercel env vars without code deploy |
| `app.py` | MODIFY | Add `@app.before_request` / `@app.after_request` hooks for request logging | Logging baseline: operational visibility in Vercel dashboard |
| `templates/base.html` | MODIFY | Fix Đăng xuất dropdown z-index/pointer-events, fix Profile hitbox click area | UI bug fix: critical UX for Beta 1 |
| `templates/chatbot.html` | MODIFY | Fix bubble chat JS to persist session_id, send on subsequent requests | UI bug fix: chatbot history not saving between refreshes |
| `templates/index.html` | MODIFY | Add privacy policy banner component (cookie notice / data usage) | Compliance: required before public Beta 1 |
| `models/models.py` | MAYBE MODIFY | Add `FeedbackReport` model (5 columns) | Feedback collection: "Báo cáo sai / Góp ý" button |
| `routes/main.py` OR new `routes/feedback.py` | MAYBE ADD | POST endpoint for feedback submission | Feedback collection: form submission handler |
| `services/anti_spam.py` | NO CHANGE | Reused as-is with new instantiation params | Existing service already supports parameterized thresholds |
| `services/sensitive_access_log.py` | NO CHANGE | Already logs to NeonDB correctly — only needs verification | Logging baseline: confirm it fires, not rewrite it |

### External Services

| Service | Integration Pattern | Vercel Constraint | Notes |
|---------|---------------------|-------------------|-------|
| OpenRouter API | Inline `urllib.request` in request thread (blocking) | 10s Vercel timeout — OpenRouter timeout set to 15s, which EXCEEDS Vercel limit | The existing 15s timeout in `utils/chatbot.py` must be reduced to ≤8s to avoid Vercel killing the function before the AI response arrives |
| NeonDB PostgreSQL | NullPool per-request connection via SQLAlchemy | NullPool is correct for serverless — no connection kept between requests | `pool_pre_ping=True` already configured |
| Cloudflare Turnstile | Server-side token validation on form POST | Stateless HTTPS call — works on Vercel | Already integrated, no changes needed |

**Critical finding:** `utils/chatbot.py` line 98 sets `timeout=15` on the OpenRouter call. Vercel's default function execution timeout is 10 seconds for the Hobby plan. The AI call CAN time out the Vercel function before receiving a response. This is an existing bug that the hardening phase should fix: reduce timeout to 8 seconds (safe margin).

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `routes/chatbot.py` → `services/anti_spam.py` | Direct Python import, synchronous DB call | New in v1.2 — currently `anti_spam.py` is only called from `routes/scammer.py` |
| `routes/chatbot.py` → `utils/chatbot.py` | Direct Python import, `generate_chatbot_reply()` | Existing — no structural change, only prompt + fallback modifications |
| `app.py` → all routes (logging hooks) | Flask `before_request` / `after_request` signals | New in v1.2 — hooks fire for ALL blueprints, not just chatbot |
| Admin dashboard → `FeedbackReport` | SQLAlchemy query in `routes/admin.py` | New query if FeedbackReport model added |

---

## Build Order (Dependency-Aware)

The hardening tasks have the following dependencies:

```
Phase 1: Fix Critical UI Bugs (no backend deps — safe to start first)
  1a. Fix Đăng xuất dropdown in base.html (CSS/z-index)
  1b. Fix Profile hitbox in base.html (click area)
  1c. Fix chatbot bubble chat session persistence in chatbot.html JS
  1d. Fix/implement Certification badge in certificate.html
  → Unblocks: user-facing Beta 1 quality; can be tested immediately

Phase 2: AI Safety Hardening (depends on: understanding current chatbot.py)
  2a. Reduce OpenRouter timeout: chatbot.py line 98, 15s → 8s
  2b. Rewrite DEFAULT_SYSTEM_PROMPT for plain Vietnamese language
  2c. Add HARD_FALLBACK_KEYWORDS check to generate_chatbot_reply()
  2d. Add hotline constants (Công an: 113, bank support numbers)
  → Unblocks: rate limiting (rate limiting wraps the now-safe AI call)

Phase 3: Rate Limiting for AI Endpoints (depends on: Phase 2 complete)
  3a. Add CHATBOT_RATE_* config vars to config.py
  3b. Instantiate chatbot-specific AntiSpamDecisionService in routes/chatbot.py
  3c. Add rate limit check to /chatbot/send, /chatbot/api, /chatbot/support
  3d. Return 429 with Vietnamese-language cooldown message
  → Unblocks: stress testing (need rate limiting before hammering endpoints)

Phase 4: Logging Baseline Verification (parallel with Phase 2/3)
  4a. Add @app.before_request / @app.after_request hooks in app.py
  4b. Verify SensitiveAccessLog fires on admin actions (read existing logs in DB)
  4c. Deploy to Vercel, generate test traffic, confirm logs appear in Vercel dashboard
  4d. Document what IS logged vs what is NOT (gap analysis)
  → Unblocks: stress testing (need logging before observing stress test results)

Phase 5: Privacy Banner (no backend deps — parallel with others)
  5a. Add privacy policy banner HTML to templates/index.html
  5b. JS cookie to remember dismissal (localStorage — no DB write needed)
  → Completes: compliance requirement for Beta 1

Phase 6: Stress Testing (depends on: Phase 3 + Phase 4)
  6a. Run locust locally against python app.py (NOT against production)
  6b. Gradually increase CCU: 10 → 50 → 100 → 200
  6c. Identify NeonDB connection limit (expect errors around 90+ concurrent)
  6d. Identify OpenRouter rate limit response behavior
  6e. Document max safe CCU for Beta 1
  → Completes: operational readiness for Beta 1 go-live

Phase 7: Feedback Collection (no hard deps — can run parallel with Phase 4/5)
  7a. Add FeedbackReport model to models.py
  7b. Write manual migration script (CREATE TABLE feedback_reports ...)
  7c. Add POST /feedback endpoint (in routes/main.py or new routes/feedback.py)
  7d. Add "Báo cáo sai / Góp ý" button to relevant pages
  7e. Add feedback list view to admin dashboard
  → Completes: Beta 1 feedback loop
```

**Why this order:**
- Phase 1 (UI bugs) has zero backend dependencies — fastest to ship, immediately improves Beta 1 quality.
- Phase 2 (AI safety) must precede Phase 3 (rate limiting) because the timeout bug (15s > Vercel 10s limit) affects whether rate limiting even works correctly (a timed-out function never returns the 429).
- Phase 4 (logging) is parallel because it adds orthogonal hooks and doesn't change business logic.
- Phase 6 (stress test) is last because it validates the hardening work from Phases 2-4 under load.
- Phase 7 (feedback) is independent — no dependency on hardening tasks, can ship any time.

---

## Vercel Serverless Constraints Summary

All architectural decisions for v1.2 must respect these Vercel Hobby plan constraints:

| Constraint | Value | Implication for Hardening |
|------------|-------|--------------------------|
| Function execution timeout | 10 seconds | OpenRouter timeout MUST be ≤8s (currently 15s — bug) |
| Filesystem access | Read-only (except /tmp) | No log files. Use stderr (app.logger) + NeonDB for persistence |
| Memory per function | 1024 MB | Flask + SQLAlchemy fit comfortably. No concern. |
| Shared memory between instances | None | All state (rate limits, sessions) must be in NeonDB |
| Cold start overhead | ~500ms-2s for Python | No heavy init in app.py. Currently clean. |
| Concurrent executions | Auto-scales horizontally | Rate limiting MUST be DB-persisted (not in-memory) |
| Environment variables | Set in Vercel project settings | `CHATBOT_RATE_*` tuning params should go here, not hardcoded |

---

## Sources

- Codebase analysis (primary): `routes/chatbot.py`, `utils/chatbot.py`, `services/anti_spam.py`, `config.py`, `app.py`, `extensions.py`, `models/models.py`, `vercel.json` — HIGH confidence
- Previous research: `.planning/research/ARCHITECTURE.md` (v1.1 migration) — HIGH confidence (established NullPool + NeonDB patterns still apply)
- `.planning/PROJECT.md` (v1.2 milestone scope and constraints) — HIGH confidence

---
*Architecture research for: Beta 1 Go-Live hardening (v1.2) — Flask monolith on Vercel serverless*
*Researched: 2026-04-10*
