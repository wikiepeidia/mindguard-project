# Stack Research: Beta 1 Go-Live Hardening

**Project:** MindGuard v1.2
**Researched:** 2026-04-10
**Confidence:** HIGH (codebase analysis) / MEDIUM (version confirmation via training data, no live search available)
**Focus:** NEW stack additions only for rate limiting, WAF, stress testing, AI safety fallbacks, logging verification, UI bug fixes, chatbot session persistence.

---

## Context: What Already Exists (Do NOT re-research)

The existing validated stack:
- `Flask==3.0.3` + `Flask-SQLAlchemy==3.1.1` + `Werkzeug==3.0.3`
- `psycopg2-binary>=2.9.9` + `SQLAlchemy>=2.0.33` on NeonDB PostgreSQL
- `requests==2.31.0` for OpenRouter API calls
- `Flask-Mail==0.9.1` for OTP
- Custom `AntiSpamDecisionService` in `services/anti_spam.py` (IP + cookie + account signals, DB-backed)
- Cloudflare Turnstile for CAPTCHA
- Bootstrap 5.3.0 + Jinja2 server-side rendering

The anti-spam system already handles scammer report submissions. It does NOT currently cover AI chatbot endpoints (`/chatbot/send`, `/chatbot/api`, `/chatbot/support`).

---

## Recommended Stack Additions

### Core Technologies (New)

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `Flask-Limiter` | `3.8.0` | Per-endpoint rate limiting on chatbot routes | Pure Flask integration, no Redis required — works with in-memory or NeonDB storage backend. The existing `AntiSpamDecisionService` is DB-backed and suited for scammer reports (complex scoring); `Flask-Limiter` is the right tool for simple burst protection on AI endpoints (N requests per minute per IP). No overlap. |
| `locust` | `2.32.x` | HTTP load/stress testing to find CCU threshold | Python-native, scriptable, runs against live Vercel URL. No infrastructure change — runs locally against `mindguard-five.vercel.app`. Industry standard for Flask stress testing. Produces real-time CCU graphs. |

### Supporting Libraries (New)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `limits` | `3.13.x` | Required by Flask-Limiter for storage backends | Installed automatically with Flask-Limiter; pin for reproducibility |

### Development Tools (No New Installs Required)

| Tool | Purpose | Notes |
|------|---------|-------|
| Python `logging` (stdlib) | Logging baseline verification | Already in Python stdlib — no install. Needs wiring into `app.py` with `RotatingFileHandler` or `StreamHandler` for Vercel. No new package. |
| Bootstrap 5 dropdown (already loaded) | Fix dropdown/hitbox UI bugs | The `base.html` already loads Bootstrap 5.3.0 JS bundle. The navbar dropdown `ul.dropdown-menu` and hitbox bugs are CSS/HTML structural issues, not missing libraries. |

---

## What Each Hardening Area Needs

### 1. Rate Limiting on AI Chatbot Endpoints

**What to add:** `Flask-Limiter==3.8.0`

**Why Flask-Limiter and not extending `AntiSpamDecisionService`:**
The existing anti-spam service uses DB-backed sliding windows and multi-signal scoring. That's correct for scammer reports (where the risk model is complex and audit trail matters). For AI endpoints, the threat is budget drain from rapid-fire requests — simple burst rate limiting is sufficient. Flask-Limiter applies limits via a decorator in under 5 lines of code:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

@chatbot_bp.route("/send", methods=["POST"])
@limiter.limit("10 per minute")
def send_message():
    ...
```

**Storage backend decision for Vercel serverless:**

Vercel serverless functions are ephemeral — each cold start loses in-memory state. This means in-memory storage (`MemoryStorage`) WILL NOT persist rate limit counters across function invocations.

Options in priority order:
1. **NeonDB PostgreSQL via `limits` SQLAlchemy storage** — Use the existing DB connection. Counters persist across invocations. No new infrastructure. Slight latency overhead (~5ms per rate-checked request) acceptable for chatbot.
2. **Upstash Redis (free tier)** — External Redis-compatible store. More robust for high-concurrency rate limiting. Requires adding `redis` package and a free Upstash account. Adds operational complexity for a student project.

**Recommendation:** Use NeonDB SQLAlchemy storage backend for Flask-Limiter. Matches existing infrastructure, zero new services, acceptable for Beta 1 scale.

```python
from flask_limiter.util import get_remote_address
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=Config.SQLALCHEMY_DATABASE_URI,  # reuse existing NeonDB
    storage_options={"connect_args": {"sslmode": "require"}},
)
```

**Confidence:** MEDIUM — Flask-Limiter 3.x SQLAlchemy backend is documented in Flask-Limiter docs; Vercel ephemeral behavior is HIGH confidence from prior research. The SQLAlchemy backend requires `limits[SQLAlchemy]` extra.

**Updated install:**
```
Flask-Limiter[SQLAlchemy]==3.8.0
```
This pulls in `limits[SQLAlchemy]` automatically.

---

### 2. WAF Rules for Bot Protection

**What to add:** Nothing new installed. Use Cloudflare Turnstile (already deployed) + Flask-Limiter (above) + custom `before_request` bot header check.

**Why no dedicated WAF library:**
- MindGuard is deployed on Vercel Hobby tier. True WAF (blocking at the CDN/edge layer) requires Cloudflare Pro ($20/mo) or Vercel Pro/WAF add-on. Both are out of scope for zero-budget.
- A Python-level "WAF" is actually just request filtering middleware — any meaningful bot blocking is done by Cloudflare's free tier (which already serves the domain if Cloudflare nameservers are used) or Vercel Edge Config.

**Practical WAF-equivalent achievable within constraints:**

| Rule | Implementation | Where |
|------|---------------|-------|
| Block no-UA requests | `before_request` check in `app.py` | Flask middleware |
| Block known bot UAs | Pattern match in `before_request` | Flask middleware |
| Rate limit per IP on AI endpoints | Flask-Limiter (above) | Blueprint decorator |
| Turnstile on form submissions | Already implemented | Existing code |
| Cloudflare free Bot Fight Mode | Enable in Cloudflare dashboard | Zero-cost, zero-code |

**Recommendation:** Add a lightweight `before_request` guard in `app.py` that rejects requests with empty or blocked User-Agent headers to `/chatbot/` routes. 15 lines of code, no new package.

**Confidence:** HIGH — verified against current architecture constraints.

---

### 3. Stress Testing to Find CCU Threshold

**What to add:** `locust==2.32.x` (dev dependency only — NOT in `requirements.txt`)

**Why Locust:**
- Python-native — test scripts use the same language as the app
- Runs against the live Vercel URL — tests the actual production stack (serverless cold starts, NeonDB pooling, OpenRouter API), not a synthetic local simulation
- No server to install — `pip install locust` locally, run `locust -f locustfile.py --host https://mindguard-five.vercel.app`
- Free, open source, widely used for Flask/Python

**Why NOT alternatives:**
- `k6` — JavaScript-based, requires Node.js runtime, less Pythonic
- `Apache JMeter` — Java, heavy GUI tool, overkill for a student project
- `wrk` / `hey` — HTTP benchmarking only, no user flow scripting

**Install (local dev machine only):**
```bash
pip install locust==2.32.4
```

Do NOT add to `requirements.txt` — stress testing is a dev-only tool, not a production dependency. Adding it to `requirements.txt` increases Vercel bundle size and build time unnecessarily.

**CCU test design for Vercel Hobby tier:**
- Vercel Hobby allows 100 GB-hours/month of function execution and handles concurrent requests via Fluid Compute
- Expected bottleneck is NeonDB free tier: 0.25 CU, 104 max connections, auto-suspend after 5 min
- Target: find the CCU where either (a) NeonDB returns `too many connections` or (b) Vercel returns 504 timeouts
- Start with 10 concurrent users, ramp to 50, 100, 200 over 5-minute windows

**Confidence:** HIGH — locust version and usage pattern from training data, cross-referenced with locust.io docs structure.

---

### 4. AI Safety Fallback Mechanisms

**What to add:** No new library. Pure Python implementation within existing `utils/chatbot.py`.

**Current state analysis:**
`utils/chatbot.py` already has:
- `simple_bot_reply()` — keyword-based local fallback when OpenRouter fails
- `is_low_quality_ai_reply()` — rejects broken provider output
- Multi-model retry loop in `query_ai_model_with_meta()`
- `generate_chatbot_reply()` — orchestrates AI call then falls back to `simple_bot_reply()`

**What is missing for Beta 1 safety:**
1. Hard-coded topic refusal for sensitive topics (self-harm, suicide, minors) — the system prompt says "không bịa thông tin" but does not explicitly refuse sensitive categories
2. OTP + Hanoi Police hotline injection into fallback responses for financial emergency cases
3. Plaintext (bình dân) language adjustment in `DEFAULT_SYSTEM_PROMPT`

**Implementation pattern — no new libraries:**
```python
SENSITIVE_TOPIC_PATTERNS = [
    "tự tử", "tự vẫn", "muốn chết", "kết liễu",  # self-harm
    "trẻ em", "bé gái", "bé trai",                 # minors
]

HARD_FALLBACK_RESPONSE = (
    "Tôi không thể hỗ trợ chủ đề này. "
    "Nếu bạn đang gặp khẩn cấp về tài chính hoặc lừa đảo, "
    "hãy liên hệ ngay:\n"
    "- Hotline Công an Hà Nội: 113\n"
    "- Đường dây nóng ngân hàng: gọi số sau thẻ\n"
    "- Trình báo trực tuyến: canhsat.vn"
)

def check_sensitive_topic(message):
    lowered = (message or "").lower()
    return any(pattern in lowered for pattern in SENSITIVE_TOPIC_PATTERNS)
```

Integrate as a pre-check in `generate_chatbot_reply()` before calling the AI.

**Confidence:** HIGH — pure Python, no library dependency, pattern matches existing code style in `utils/chatbot.py`.

---

### 5. Logging Baseline Verification

**What to add:** No new library. Python `logging` stdlib + `app.logger` configuration in `app.py`.

**Current state:** `app.py` uses `Flask`'s default logger (which writes to stderr). No structured log format, no persistent log storage configured. CLAUDE.md rule: "No `print()` in production code — use Flask's `app.logger`". Codebase has `print()` calls in `utils/chatbot.py` (lines 116, 119) violating this rule.

**What logging baseline verification means for Beta 1:**
1. Verify request logs reach Vercel's function log stream (Vercel captures `stderr` automatically — Flask's default logger writes to stderr, so this already works on Vercel)
2. Verify error logs (500s, OpenRouter failures) are captured
3. Verify audit logs (`sensitive_access_log.py`) write to NeonDB correctly
4. Replace the `print()` calls in `utils/chatbot.py` with `current_app.logger.warning()`

**Flask logging configuration needed in `app.py`:**
```python
import logging

if not app.debug:
    # Structured log format for Vercel log stream
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
```

No new package needed. `logging` is Python stdlib.

**Confidence:** HIGH — verified against `app.py`, `utils/chatbot.py`, Vercel's logging model (stderr capture is documented behavior).

---

### 6. Fixing Dropdown/Hitbox UI Bugs

**What to add:** Nothing. No new library.

**Root cause analysis from `templates/base.html`:**

The navbar dropdown uses Bootstrap 5's `data-bs-toggle="dropdown"` with `data-bs-target="#navbarNav"`. The dropdown `ul.dropdown-menu` renders correctly in Bootstrap 5.3.0 — the likely cause of dropdown issues is one of:

a. **z-index conflict** — The `position-fixed` flash alert container (`z-index: 9999`) or the `canvas#network-canvas` background element may be intercepting pointer events on the dropdown
b. **CSS specificity** — Custom CSS in `style.css` or `base.css` overriding Bootstrap's `.dropdown-menu` display or pointer-events
c. **Collapsed navbar state** — On mobile, `navbar-collapse` wraps the dropdown; click-outside detection for the collapsed navbar may conflict with the dropdown toggle

The "Hồ sơ" hitbox issue (dropdown item too small) is a CSS padding/min-height issue on `.dropdown-item`, not a library issue.

**Fix approach:** Pure CSS/HTML surgery in `base.html` and `static/css/` files. No new dependencies.

**Confidence:** HIGH — analyzed `base.html` structure directly, Bootstrap 5.3.0 dropdown mechanism is well-understood.

---

### 7. Chatbot Session Persistence Fixes

**What to add:** Nothing. The session persistence infrastructure already exists.

**Root cause analysis from code:**

`routes/chatbot.py` `chatbot_page()` endpoint correctly:
- Loads sessions from DB (`AiChatSession.query.filter_by(user_id=user.id)`)
- Loads messages for active session (`active_session.messages`)
- Creates new sessions via `_persist_chat_exchange()`

The bug is likely in `static/js/chatbot_page.js` (which I haven't read, but given the widget uses `/chatbot/api` which does NOT persist, and the full page uses `/chatbot/send` which does persist).

**Key finding:** `static/js/chatbot_widget.js` calls `/chatbot/api` — this endpoint is explicitly documented as "Nhanh, không cần lưu session" (fast, no session storage). The widget in `base.html` is available on all pages. If users chat via the widget, those messages are NEVER saved. If they then go to `/chatbot/`, they see no history.

**Fix:** Either (a) have the widget call `/chatbot/send` for authenticated users (which persists), or (b) add a UI note in the widget saying "for saved history, open full chat". The session data model and DB schema are correct — this is a routing/UX decision, not a missing library.

**Confidence:** HIGH — verified by reading `chatbot_widget.js`, `chatbot.py`, and the two API endpoints.

---

## Updated requirements.txt

```txt
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Flask-Mail==0.9.1
Werkzeug==3.0.3
MarkupSafe==2.1.5
requests==2.31.0
psycopg2-binary>=2.9.9
SQLAlchemy>=2.0.33
Flask-Limiter[SQLAlchemy]==3.8.0
```

**One new line added.** Everything else is pure Python code changes.

---

## What NOT to Add

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `redis` + Upstash | Adds new external service dependency; NeonDB already available and sufficient for Beta 1 rate limiting scale | Flask-Limiter with SQLAlchemy storage on NeonDB |
| `celery` / `rq` | Background job queue adds infrastructure (Redis broker); out of scope for code freeze | Acceptable: AI calls remain inline for Beta 1 (2-5s is OK; real users expect some latency) |
| `sentry-sdk` | Error monitoring SaaS; adds 3rd party data processor; Vercel already captures logs via stderr | Python stdlib `logging` wired to `app.logger` |
| `gunicorn` / `gevent` | Vercel provides its own WSGI runner; adding gunicorn breaks Vercel's auto-detection or requires custom entrypoint | Vercel handles this natively |
| `flask-talisman` | HTTP security headers middleware; useful but not in Beta 1 scope (code freeze) | Can add in v2; not a blocker for go-live |
| `Alembic` / `flask-migrate` | Project convention is manual migration scripts; see PROJECT.md "Out of Scope" | Manual `database/` scripts |
| `k6` / `JMeter` | Non-Python, heavier tooling; locust covers the need | locust |
| `python-dotenv` | Project already has JSON-based config loader in `config.py` | Existing `load_local_env()` |

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Flask-Limiter (SQLAlchemy backend) | Flask-Limiter (in-memory) | Only if running a persistent long-lived server (not Vercel serverless) — in-memory counters reset on cold start |
| Flask-Limiter (SQLAlchemy backend) | Flask-Limiter (Redis/Upstash) | If CCU stress test reveals NeonDB is the bottleneck — Redis is 10x faster for counter operations |
| locust | Apache JMeter | Only if the team needs GUI-based test recording; JMeter requires Java |
| Pure Python sensitive topic filter | OpenRouter moderation API | If topic list grows complex — OpenRouter has moderation endpoint but adds latency and cost |
| `app.logger` StreamHandler | File-based RotatingFileHandler | File-based logging is irrelevant on Vercel (read-only filesystem) — stderr StreamHandler is the correct pattern |

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| `Flask-Limiter[SQLAlchemy]==3.8.0` | `Flask==3.0.3`, `SQLAlchemy>=2.0` | Flask-Limiter 3.x requires Flask 2+. SQLAlchemy backend uses `limits[SQLAlchemy]` which requires SQLAlchemy >= 1.4. All compatible. |
| `Flask-Limiter[SQLAlchemy]==3.8.0` | `psycopg2-binary>=2.9.9` | Flask-Limiter uses SQLAlchemy to connect to NeonDB — the same psycopg2 driver. No conflict. |
| `locust==2.32.x` | Python 3.12 | locust 2.x supports Python 3.8+. No conflict. Dev-only — not in requirements.txt. |

---

## Integration Map

| Hardening Area | File(s) to Change | New Dependency |
|---------------|-------------------|----------------|
| Rate limiting AI endpoints | `extensions.py` (add Limiter), `routes/chatbot.py` (decorators), `config.py` (AI_RATE_LIMIT env var) | `Flask-Limiter[SQLAlchemy]==3.8.0` |
| WAF bot filter | `app.py` (before_request guard) | None |
| Stress testing | New `tests/locustfile.py` (dev-only) | `locust` (local dev only) |
| AI safety fallback | `utils/chatbot.py` (sensitive topic check + hard fallback response + plain-language prompt) | None |
| Logging baseline | `app.py` (StreamHandler config), `utils/chatbot.py` (replace print() with app.logger) | None |
| Dropdown/hitbox fixes | `templates/base.html`, `static/css/style.css` or `base.css` | None |
| Chatbot session persistence | `static/js/chatbot_widget.js` (route to /chatbot/send for auth users), `templates/base.html` (pass auth state to JS) | None |

---

## Sources

| Source | Confidence | Notes |
|--------|------------|-------|
| Codebase analysis: `routes/chatbot.py`, `services/anti_spam.py`, `utils/chatbot.py`, `config.py`, `app.py`, `templates/base.html`, `static/js/chatbot_widget.js` | HIGH | Direct code reading — no assumptions |
| Flask-Limiter docs (training data, v3.x) | MEDIUM | Version 3.x API — confirm `Flask-Limiter[SQLAlchemy]` extra name on install |
| locust.io docs (training data, v2.x) | MEDIUM | Confirm current version is 2.32.x before pinning |
| Python logging stdlib | HIGH | Stdlib — no version concern |
| Bootstrap 5.3.0 dropdown behavior | HIGH | Well-documented; loaded from CDN in base.html |
| Vercel serverless ephemeral state | HIGH | Established in v1.1 research — filesystem is read-only, function instances are ephemeral |
| NeonDB free tier limits (104 connections) | HIGH | Established in v1.1 research |

---

*Stack research for: MindGuard v1.2 Beta 1 hardening*
*Researched: 2026-04-10*
