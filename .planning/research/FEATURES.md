# Feature Research

**Domain:** Beta 1 Go-Live Hardening — Flask/Vercel/NeonDB AI chatbot platform (v1.2 Code Freeze)
**Researched:** 2026-04-10
**Confidence:** HIGH (direct codebase inspection + established production patterns)

---

## Context: Existing Infrastructure Relevant to Hardening

This is a CODE FREEZE milestone. No new features. Every item maps to an active requirement in PROJECT.md.

| Component | Current State | Gap for Beta 1 |
| --------- | ------------- | -------------- |
| `services/anti_spam.py` | DB-backed risk scoring (account + cookie + IP) for scammer reports | Not wired to chatbot endpoints — `/api` and `/support` are completely unprotected |
| `utils/chatbot.py` | Model waterfall (5 free OpenRouter models), `is_low_quality_ai_reply()`, `simple_bot_reply()` keyword fallback | No topic-based hard blocks; no sensitive-topic emergency response |
| `config.py` | `ABUS_MODE = "monitor"` (soft-enforce only) | Chatbot needs hard enforcement, not monitoring |
| `routes/chatbot.py` | Three endpoints: `/send` (auth-gated + persisted), `/api` (widget, no auth, no rate limit), `/support` (no auth, no rate limit) | Two unauthenticated AI endpoints with zero cost protection |
| `models.py` | `AiChatSession` + `AiChatMessage` in DB; bubble `/api` widget is stateless by design | Authenticated users using bubble get no history — trust failure for returning users |
| Vercel deployment | Ephemeral serverless functions, no shared in-process state, read-only filesystem | In-memory rate limiting is silently useless here — must use DB-backed state |
| NeonDB PostgreSQL | NullPool + pool_pre_ping configured (correct for serverless) | Free tier connection limit (~100 simultaneous) is the actual scale ceiling, not Vercel functions |

---

## Feature Landscape

### Table Stakes (Must Land Before Go-Live)

Missing any of these creates a cost blowout, safety liability, or legal exposure before public launch.

| Feature | Why Expected | Complexity | Stack Notes |
| ------- | ------------ | ---------- | ----------- |
| **Rate limiting on `/chatbot/api` and `/chatbot/support`** | Both are unauthenticated endpoints that call OpenRouter on every request. A single scripted requester can drain the full API budget in under an hour. Highest-severity cost risk for Beta 1. | MEDIUM | Cannot use in-process counters — Vercel ephemeral instances have no shared memory. Must use DB-backed sliding window counter in NeonDB. Same architectural pattern as `AntiSpamEvent` / `AntiSpamActorState` already in codebase. Per-IP key. Reject with HTTP 429 + Vietnamese message. |
| **Hard fallback for AI sensitive topics** | Free-tier models (Qwen 4B, Hermes) sometimes output wrong hotline numbers, non-Vietnamese text, or legally problematic advice. For a fraud-awareness platform, a wrong "call this number" response causes direct harm. | LOW | One-file change in `utils/chatbot.py`. Add a `hard_block_check()` pre-filter layer before `query_ai_model_with_meta()`. Blocked topics return a fixed response with verified emergency contacts: `Công an Hà Nội: 113`, `Ngân hàng Nhà nước: 1900 6247`. Blocked topics: self-harm signals, requests to AI to provide bank accounts to transfer money to, jailbreak patterns ("bỏ qua hướng dẫn"). |
| **Privacy policy banner on homepage** | Nghị định 13/2023/NĐ-CP (Vietnam Personal Data Protection Decree, effective July 2023) requires user notice and consent for personal data collection before processing. Displaying to Hà Nội citizens without notice is legal exposure. | LOW | Static HTML banner in `templates/index.html`. Dismiss state in `localStorage` key `mg_privacy_accepted`. No DB write needed. Banner must include: (1) what data is collected, (2) why, (3) link to `/privacy` static page, (4) explicit dismiss/accept button. Do not use a cookie for consent — cookies require their own notice under the decree. |
| **UI bug fixes (logout dropdown, profile hitbox, certification badge)** | Users who cannot log out or access their profile will not return. Certification badge errors destroy trust in the quiz system — the core educational product. These are trust blockers, not cosmetic issues. | LOW | Logout dropdown: likely Bootstrap JS not loaded before click handler — check `base.html` script load order. Profile hitbox: CSS `z-index` or `pointer-events` conflict. Certification badge: investigate `certificate_code` generation and `QuizResult` template rendering. |

### Differentiators (Launch-Week Quality Signal)

Not go-live blockers, but significantly improve Beta feedback quality and system stability.

| Feature | Value Proposition | Complexity | Stack Notes |
| ------- | ----------------- | ---------- | ----------- |
| **Chatbot session persistence fix for bubble widget** | Authenticated users using the floating bubble (`/chatbot/api`) get no chat history. They expect continuity with the full chat page. High user confusion for returning users who have built up sessions in the full chat view. | LOW | `/chatbot/api` currently calls `generate_chatbot_reply()` directly and discards the response. Fix: in `chatbot_api()`, check `session.get('registration_email')`. If authenticated, call `_persist_chat_exchange()` with `session_id=None` (creates/continues a session). If unauthenticated, keep existing stateless behavior. No schema change, no migration. |
| **AI system prompt plain-language adjustment** | Free-tier models on Vietnamese prompts sometimes produce formal/bureaucratic output ("Kính gửi quý vị...") that confuses less-educated users — the primary audience for a Hà Nội fraud-awareness tool. | LOW | One-line change to `DEFAULT_SYSTEM_PROMPT` in `utils/chatbot.py`. Add: `"Dùng ngôn ngữ đơn giản, tránh thuật ngữ kỹ thuật, phù hợp với người dân phổ thông."` No structural change. Independent of all other items. |
| **"Báo cáo sai / Góp ý" feedback button** | Creates a feedback loop for AI quality tuning without external survey tools. Surfaces bad AI responses that slip past `is_low_quality_ai_reply()`. Essential for Beta quality signal — without it, bad AI responses are invisible to the team. | MEDIUM | Floating button or inline icon near chatbot messages. Posts to new `POST /api/feedback` endpoint. New model `ChatFeedback`: `id`, `user_id` (nullable FK), `context_type` (chatbot/quiz/report), `message_preview` (VARCHAR 200), `feedback_type` (wrong_info/offensive/helpful/unclear), `ip_address`, `created_at`. This is the only new table in this milestone — keep to one migration. Admin dashboard shows count by feedback_type. |
| **Logging baseline verification** | Vercel function logs are ephemeral. Without structured logging and a log drain configured, there is no observability during Beta — no way to diagnose issues that appear in production. Flask `app.logger` calls are inconsistent across chatbot routes currently. | MEDIUM | Add `app.logger.info()` at chatbot entry/exit with structured fields: `user_id`, `model_used`, `reply_source`, `latency_ms`, `endpoint`. On Vercel, stdout goes to the Vercel dashboard. For persistence beyond 1 hour, configure a Vercel Log Drain (free tier supports Axiom or custom webhook). This is primarily config work, not code. |
| **Stress test: find NeonDB connection ceiling** | Vercel serverless scales automatically, but NeonDB free tier allows ~100 simultaneous connections. With `NullPool`, each request opens and closes a connection independently. The chatbot endpoint does: DB write (persist message) + external API call (OpenRouter) + DB write (persist reply). Under concurrent load, NeonDB connection quota is the actual bottleneck, not Vercel function count. Need to know this ceiling before public announcement. | LOW (test activity, no code) | Use `locust` or `k6` locally against the live Vercel URL. Ramp from 10 to 150 concurrent users on the chatbot endpoint. Observe: P95 latency, error rate, and NeonDB `too many connections` errors in Vercel logs. Expected ceiling: ~30-50 concurrent chatbot users before NeonDB errors appear on free tier. This is a test activity — not a code change. |

### Anti-Features (Explicitly Ruled Out for Code Freeze)

| Feature | Why Requested | Why Problematic | Alternative |
| ------- | ------------- | --------------- | ----------- |
| **In-memory rate limiting (Flask-Limiter with MemoryStorage)** | Simple to add, well-documented | Vercel serverless instances have no shared memory. State is per-invocation. Provides false confidence while offering zero actual protection. | DB-backed counter in NeonDB using the same `AntiSpamEvent` pattern already in codebase. |
| **Redis for rate limiting / session caching** | Industry-standard distributed rate limiting | Adds a new paid/free-tier service dependency, new credentials, new failure mode. Zero-budget project. Overkill for Beta 1 scale. | NeonDB counter is sufficient. Reassess if request volume at Beta requires sub-millisecond rate check. |
| **Celery / RQ for async AI calls** | Would remove 2-5s blocking AI call from request thread | Requires a persistent worker process — Vercel serverless does not support this. | Keep inline AI calls. Mitigate UX impact with a client-side loading spinner. The existing `timeout=15` is already in place. |
| **Full PDPD compliance implementation** | Legal requirement | Full compliance (data subject access requests, deletion workflows, DPA registration) is a multi-phase project. Code Freeze scope is banner + consent notice only. | Static banner + localStorage flag + link to privacy page. This satisfies the immediate notice requirement. |
| **AI response caching** | Reduces OpenRouter API calls for repeated questions | Fraud patterns change daily. Cached "safe" responses may be dangerously wrong for new scam variants appearing after cache was set. Inappropriate for a fraud-detection chatbot. | Do not cache AI responses for this domain. Every response should be fresh. |
| **Dark mode** | Frequently requested | Explicitly out of scope per PROJECT.md. Code freeze. | Defer to post-Beta. |
| **OAuth / social login** | Reduces registration friction | Adds new auth code paths that need testing — violates Code Freeze intent. | Defer to v2. |
| **Second anti-spam service instance for chatbot** | Reuse existing service cleanly | `AntiSpamDecisionService` has logic tied to scammer report semantics (reporter_hash, account weight). Wrapping chatbot rate limiting inside it adds coupling and makes the logic harder to read. | Create a thin, purpose-built `AiRateLimiter` class (20-30 lines) using `AntiSpamEvent` DB table for storage but with chatbot-specific window/threshold params. Avoids coupling. |

---

## Feature Dependencies

```text
[Rate limiting on /chatbot/api + /chatbot/support]
    └──requires──> [DB-backed counter — use AntiSpamEvent table, already exists]
    └──requires──> [IP extraction from X-Forwarded-For header — Vercel pattern]
    └──must ship before──> [Privacy banner launch (banner drives traffic spike)]

[Hard fallback for sensitive topics]
    └──extends──> [simple_bot_reply() in utils/chatbot.py — already exists]
    └──synergistic with──> [AI prompt plain-language adjustment — same file, same commit]
    └──is independent of──> [rate limiting]

[Privacy banner (PDPD)]
    └──requires──> [/privacy static route or page — may need creation]
    └──uses──> [localStorage only — no DB dependency]
    └──must ship before or with──> [public announcement]

[Chatbot session persistence fix]
    └──requires──> [AiChatSession + AiChatMessage — already exist]
    └──requires──> [_persist_chat_exchange() — already exists]
    └──is independent of──> [all other items — safe to ship any time]

[Feedback button]
    └──requires──> [new ChatFeedback model + one DB migration]
    └──requires──> [POST /api/feedback endpoint]
    └──enhances──> [AI quality tuning post-Beta]
    └──this is the only new migration in this milestone]

[Logging baseline]
    └──requires──> [audit of app.logger usage in chatbot routes]
    └──requires──> [Vercel Log Drain configuration — no code change]
    └──is prerequisite for──> [stress test — need logs to read results]

[Stress test]
    └──requires──> [logging baseline — need structured logs to diagnose]
    └──is NOT a code change — test activity only]
    └──informs──> [NeonDB connection pool sizing for v2]
```

### Dependency Notes

- Rate limiting MUST ship before the privacy banner. The banner will attract new users; unprotected endpoints must be hardened first.
- Hard fallback and prompt adjustment are both single-file changes in `utils/chatbot.py`. Group them in one commit to reduce review overhead.
- Feedback button requires the only new DB migration this milestone. Keep it last to avoid migration issues blocking other items.
- Session persistence fix is fully independent. Can ship at any point.
- Logging baseline is a prerequisite for interpreting stress test results. Do logging before stress test.

---

## MVP Definition

### Launch With (Go-Live Blockers — Cannot ship without these)

- [ ] Rate limiting on `/chatbot/api` and `/chatbot/support` — cost/availability blocker
- [ ] Hard fallback for sensitive AI topics — safety + legal blocker
- [ ] Privacy policy banner on homepage — legal compliance blocker (Nghị định 13/2023)
- [ ] UI bug fixes: logout dropdown, profile hitbox, certification badge — trust blockers

### Add in First Week of Beta

- [ ] Chatbot session persistence fix (bubble widget) — high user confusion, easy fix
- [ ] AI system prompt plain-language tuning — affects every response, one-line change
- [ ] Feedback button ("Báo cáo sai / Góp ý") — enables quality signal from day 1 of Beta

### Before Beta Ends (Observability + Capacity Planning)

- [ ] Logging baseline verification + log drain config — needed to diagnose Beta issues
- [ ] Stress test to find NeonDB connection ceiling — needed before broader public announcement

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
| ------- | ---------- | ------------------- | -------- |
| Rate limiting on AI endpoints | HIGH (prevents cost outage) | MEDIUM (DB counter pattern) | P1 — go-live blocker |
| Hard fallback for sensitive topics | HIGH (safety, legal) | LOW (extend existing function) | P1 — go-live blocker |
| Privacy banner (PDPD) | HIGH (legal compliance) | LOW (static HTML + localStorage) | P1 — go-live blocker |
| UI bug fixes (logout/profile/badge) | HIGH (trust) | LOW (HTML/CSS/route) | P1 — go-live blocker |
| Chatbot session persistence fix | MEDIUM (UX continuity) | LOW (reuse existing path) | P2 — Beta week 1 |
| AI prompt plain-language tuning | MEDIUM (accessibility) | LOW (one-line change) | P2 — Beta week 1 |
| Feedback button | MEDIUM (quality signal) | MEDIUM (new table + endpoint) | P2 — Beta week 1 |
| Logging baseline | MEDIUM (observability) | MEDIUM (audit + log drain config) | P2 — before stress test |
| Stress test | HIGH (capacity planning) | LOW (test activity, no code) | P2 — before broad announcement |

**Priority key:**

- P1: Must ship before public go-live
- P2: Ship during Beta week 1 or before broader announcement

---

## Domain-Specific Implementation Patterns

### 1. Rate Limiting Pattern for Vercel Serverless + NeonDB

**The key constraint:** Vercel serverless = no shared in-process memory. Every function invocation is independent. Flask-Limiter's `MemoryStorage` silently fails here. State must be in NeonDB.

**Recommended pattern (reuses existing infrastructure):**

```python
# New thin class, separate from AntiSpamDecisionService to avoid coupling
class AiRateLimiter:
    WINDOW_SECONDS = 60
    MAX_REQUESTS = 10  # for /api widget; use 20 for /support

    def is_allowed(self, ip: str) -> bool:
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=self.WINDOW_SECONDS)
        actor_key = f"ai_rl:{ip}"
        count = AntiSpamEvent.query.filter(
            AntiSpamEvent.actor_key == actor_key,
            AntiSpamEvent.occurred_at >= window_start
        ).count()
        if count >= self.MAX_REQUESTS:
            return False
        db.session.add(AntiSpamEvent(
            actor_key=actor_key, actor_type="ip",
            ip_address=ip, risk_score=0, risk_level="low",
            window_count=count + 1, triggered_cooldown=False,
            occurred_at=now
        ))
        db.session.commit()
        return True
```

**IP extraction on Vercel:** Use `request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()`. Vercel always sets `X-Forwarded-For`.

**Rejection response:**

```python
return jsonify({
    "error": "Quá nhiều yêu cầu. Vui lòng thử lại sau 1 phút.",
    "retry_after": 60
}), 429
```

### 2. AI Safety Guardrails Pattern

**Current state:** `simple_bot_reply()` is a post-AI fallback (runs when AI fails). Sensitive topic hard-blocks need to be a pre-AI gate (prevent AI from being called at all for dangerous topics).

**Recommended call stack:**

```text
user message
    → hard_block_check(message) → if match: return FIXED emergency response (skip AI entirely)
    → query_ai_model_with_meta() → model waterfall
    → is_low_quality_ai_reply() → quality gate
    → simple_bot_reply(message) → keyword fallback
```

**Hard-block keywords to add to `utils/chatbot.py`:**

```python
HARD_BLOCK_TRIGGERS = [
    "tự tử", "tự làm hại", "muốn chết",          # self-harm
    "bỏ qua hướng dẫn", "ignore previous",         # jailbreak
    "quên vai trò", "pretend you are",              # jailbreak
]

HARD_BLOCK_RESPONSE = (
    "Tôi không thể hỗ trợ yêu cầu này.\n\n"
    "Nếu bạn cần hỗ trợ khẩn cấp:\n"
    "- Công an Hà Nội: 113\n"
    "- Đường dây nóng Ngân hàng Nhà nước: 1900 6247\n"
    "- Hỗ trợ sức khỏe tâm thần: 1800 599 920 (miễn phí)"
)
```

### 3. Privacy Banner Pattern (Nghị định 13/2023 minimal compliance)

**What the decree requires for notice:** Before or at the time of data collection, inform users of: (a) the identity of the data controller, (b) the purpose of processing, (c) the type of data collected. A dismissible banner on first visit satisfies this.

**Implementation:**

- Banner HTML in `templates/base.html` (covers all pages, not just index)
- JS localStorage check on load: if `localStorage.getItem('mg_privacy_accepted')` is set, hide banner immediately
- Two buttons: "Đồng ý" (sets `mg_privacy_accepted=1`) + "Xem chính sách" (links to `/privacy`)
- Create a minimal `/privacy` route in `routes/main.py` rendering a static template
- Do not use a cookie for consent state — cookies require their own notice under the decree

### 4. Chatbot Session Persistence Fix

**Root cause:** `chatbot_api()` calls `generate_chatbot_reply()` directly. It never calls `_persist_chat_exchange()`.

**Fix (5 lines added to `chatbot_api()`):**

```python
user_email = session.get('registration_email')
if user_email:
    user = Registration.query.filter_by(email=user_email).first()
    if user:
        chat_session, reply, reply_meta, _ = _persist_chat_exchange(user, message, session_id=None)
        return jsonify({"reply": reply, "reply_source": reply_meta.get("source"), "reply_model": reply_meta.get("model")})
# Fall through to stateless path for unauthenticated users
```

No schema change, no migration. Works with existing `AiChatSession`/`AiChatMessage` models.

### 5. Stress Testing Pattern for Vercel + NeonDB

**What to test:** Not Vercel function throughput (it auto-scales). Test NeonDB connection saturation.

**Expected profile for chatbot endpoint:**

- Each request: open connection → INSERT chat message → call OpenRouter (2-5s) → INSERT bot reply → close connection
- `NullPool` means connections are not reused across requests
- NeonDB free tier: 20-100 concurrent connections depending on plan

**Test methodology:**

```bash
# Install locust
pip install locust

# locustfile.py: POST to /chatbot/api with sample message
# Ramp from 10 to 150 concurrent users
# Watch for: HTTP 500 with "too many connections", P95 > 5s

locust -f locustfile.py --host https://mindguard-five.vercel.app \
  --users 150 --spawn-rate 10 --run-time 2m --headless
```

**Stop criteria:** When error rate exceeds 5% or P95 latency exceeds 5 seconds. Record that concurrent user count as the ceiling. Document in `docs/technical/ARCHITECTURE.md`.

### 6. User Feedback Collection Pattern

**Minimal viable model:**

```python
class ChatFeedback(db.Model):
    __tablename__ = 'chat_feedback'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('registrations.id'), nullable=True)
    context_type = db.Column(db.String(20), nullable=False)   # 'chatbot', 'quiz', 'report'
    message_preview = db.Column(db.String(200), nullable=True)
    feedback_type = db.Column(db.String(20), nullable=False)   # 'wrong_info', 'offensive', 'helpful', 'unclear'
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Admin view:** Simple aggregation query by `feedback_type` + `created_at` date. No complex UI needed for Beta.

---

## Confidence Assessment

| Area | Confidence | Basis |
| ---- | ---------- | ----- |
| Rate limiting pattern (DB-backed) | HIGH | Direct inspection of existing `AntiSpamEvent` / `AntiSpamActorState` models. Same pattern applies. Vercel serverless constraint confirmed via `vercel.json`. |
| AI safety guardrails | HIGH | Direct inspection of `utils/chatbot.py`. Current `simple_bot_reply()` pattern is a clear extension point. Hard-block pattern is standard for production AI chatbots. |
| Privacy banner (Nghị định 13/2023) | MEDIUM | Decree content is public and clear on notice requirement. The "minimal banner = sufficient for Beta notice" interpretation is reasonable but not verified with a Vietnamese legal review. |
| Session persistence fix | HIGH | Direct inspection of `routes/chatbot.py` and `_persist_chat_exchange()`. The fix is a clear code path addition, not a design change. |
| Stress test methodology | MEDIUM | NullPool behavior on Vercel is confirmed via `config.py`. Free-tier NeonDB connection limits are documented by Neon but exact number depends on current plan — verify in Neon dashboard before test. |
| Feedback collection pattern | HIGH | Standard CRUD pattern. No novel complexity. New table only. |

---

## Sources

- Direct inspection: `routes/chatbot.py`, `services/anti_spam.py`, `utils/chatbot.py`, `config.py`, `models/models.py` (2026-04-10)
- Direct inspection: `vercel.json` — confirmed serverless, single region sin1, no background workers
- Direct inspection: `config.py` — confirmed NullPool, pool_pre_ping=True, ABUS_MODE=monitor
- Nghị định 13/2023/NĐ-CP (Vietnam Personal Data Protection Decree) — Article 13 notice requirements
- Vercel Python runtime: ephemeral instances, no persistent in-process state, log drain configuration
- Neon documentation: NullPool is required for serverless environments; connection limits vary by plan

---

*Feature research for: MindGuard v1.2 Beta 1 Go-Live Hardening*
*Researched: 2026-04-10*
*Supersedes: FEATURES.md (v1.0, 2026-03-19) — that file covered v1.0 brownfield features. This file covers v1.2 hardening scope only.*
