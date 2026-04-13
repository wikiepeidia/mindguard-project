# External Integrations

**Analysis Date:** 2026-04-13

## APIs & External Services

**AI & Content Generation:**
- OpenRouter API - Provides AI chatbot replies and AI-generated quiz questions
  - SDK/Client: `urllib.request` (standard library HTTP client)
  - Auth: `OPENROUTER_API_KEY` (from env or `.env/chatbot.json`)
  - URL: `https://openrouter.ai/api/v1/chat/completions`
  - Models used (free tier): Liquid LFM 2.5, AllenAI Molmo 2, Google Gemini 2.0 Flash Lite
  - Implementation: `utils/chatbot.py::query_ai_model()` with automatic model fallback
  - Rate limiting: 20 requests/minute; 3 requests/second (configured in routes)
  - Fallback behavior: If API fails, returns simple rule-based bot response

**Bot Protection & CAPTCHA:**
- Cloudflare Turnstile - CAPTCHA verification on login/register/reporting forms
  - SDK/Client: JavaScript widget (client-side) + `requests` library (server-side verification)
  - Public Key: `CLOUDFLARE_SITE_KEY` (from env or `.env/cloudflare.json`)
  - Secret Key: `CLOUDFLARE_SECRET_KEY` (from env or `.env/cloudflare.json`)
  - Verification URL: `https://challenges.cloudflare.com/turnstile/v0/siteverify`
  - Fallback: Math CAPTCHA (simple arithmetic problem) when Turnstile unavailable
  - Implementation: `routes/auth.py::login()` and `routes/scammer.py` form handlers

**Public URL Tunneling:**
- ngrok - Exposes localhost:5000 publicly for demos and external access
  - SDK/Client: `pyngrok` library (Python wrapper)
  - Auth: `NGROK_AUTHTOKEN` (from env or `.env/ngrok.json`)
  - Usage: Starts tunnel on app startup in `app.py` (only in main process)
  - Implementation: `utils/ngrok_tunnel.py::start_ngrok()`
  - Output: Public URL printed to console (format: `https://xxxx-xx-xxx-xx-xx.ngrok.io`)

## Data Storage

**Databases:**
- SQLite 3 (file-based)
  - Connection: `sqlite:////[project_root]/database/mindguard_v2.db`
  - File path: `/database/mindguard_v2.db` (committed to git, 90KB)
  - Client: Flask-SQLAlchemy ORM via SQLAlchemy
  - Models: 13 tables (`Registration`, `QuizResult`, `ScammerReport`, `AiChatSession`, etc.)
  - Initialization: `db.create_all()` called on app startup in `app.py`
  - No external database server required (zero-config, file-based)

**File Storage:**
- Local filesystem only
  - User uploads: Not currently implemented
  - Static assets: `static/css/`, `static/js/` served by Flask directly
  - Database exports: Written to local disk (admin export feature)

**Caching:**
- None (in-memory session management via Flask sessions)
- Conversation history: Persisted to SQLite (not volatile cache)
- Rate limit state: In-memory (Flask-Limiter default)

## Authentication & Identity

**Auth Provider:**
- Custom (no external OAuth or SAML)
  - Implementation: Server-side sessions with Werkzeug password hashing
  - Session store: Flask server-side session (signed cookie-based)
  - Password hashing: PBKDF2-SHA256 via Werkzeug
  - Routes: `routes/auth.py` (login, register, password reset, OTP verification)
  - OTP email delivery: Via Flask-Mail (not yet fully configured in code)

**Supported Authentication Methods:**
- Email + Password (local registration and login)
- No OAuth/Google/Facebook login
- No 2FA beyond OTP-via-email (not fully implemented)

**Session Management:**
- Session lifetime: 7 days (`PERMANENT_SESSION_LIFETIME = 86400 * 7`)
- Session storage: Server-side (Flask manages via signed cookies)
- Roles: `user` (default) or `admin`
- Role-based access control: Routes check `user.role` before granting admin access

## Email Services

**Email Provider:**
- Flask-Mail 0.9.1 - Configured but not fully utilized
  - Purpose: OTP delivery for password reset (partially implemented)
  - Configuration: Reads from environment variables (e.g., `MAIL_SERVER`, `MAIL_USERNAME`, `MAIL_PASSWORD`)
  - No active SMTP server configured in code (auth routes reference mail but implementation incomplete)

## Monitoring & Observability

**Error Tracking:**
- None (no Sentry, Rollbar, or similar)
- Errors logged to Flask app.logger (standard logging module)

**Logs:**
- File-based logging to `logs/access.log`
  - Format: IP address, HTTP method, path, status code, user agent
  - Implementation: `app.py::log_request()` decorator
- Sensitive access audit: `SensitiveAccessLog` table in database
  - Purpose: Track admin operations on PII
  - Implementation: `services/sensitive_access_log.py`
- Anti-spam events: `AntiSpamEvent` table in database
  - Purpose: Track and analyze rate limit violations
  - Implementation: `services/anti_spam.py`

## CI/CD & Deployment

**Hosting:**
- Currently: localhost:5000 (development server)
- Public demo: ngrok tunnel (dynamic URL, regenerated on each startup)
- Production target: TBD (not deployed yet)

**CI Pipeline:**
- None configured (GitHub Actions planned for future)
- No automated testing on PRs
- Manual deployment via `python app.py`

**Deployment Process:**
- Manual: Clone repo → `pip install -r requirements.txt` → `python app.py`
- Custom installer available: `packages/Installer.py` (wrapper around pip)
- Production deployment: Use Gunicorn/uWSGI instead of Flask development server

## Environment Configuration

**Required Environment Variables:**
- `OPENROUTER_API_KEY` - AI chatbot and quiz generation (free tier)
- `CLOUDFLARE_SITE_KEY` - CAPTCHA public key
- `CLOUDFLARE_SECRET_KEY` - CAPTCHA verification secret
- `NGROK_AUTHTOKEN` - Public URL tunneling (optional, only for demo)
- `SECRET_KEY` - Flask session encryption (falls back to hardcoded value)
- `ADMIN_UNSUSPEND_SECRET` - Admin account unlock secret
- `ABUS_MODE` - Anti-spam mode ("monitor" or "enforce")
- `ABUS_WINDOW_MINUTES`, `ABUS_THRESHOLD_COUNT`, `ABUS_COOLDOWN_MINUTES` - Anti-spam tuning

**Optional Environment Variables:**
- `WERKZEUG_RUN_MAIN` - Used internally to prevent double startup of ngrok
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD` - Email configuration (not active)

**Secrets Location:**
- `.env/` directory (JSON files):
  - `.env/chatbot.json` - `OPENROUTER_API_KEY`
  - `.env/cloudflare.json` - `SITE_KEY`, `SECRET_KEY`
  - `.env/ngrok.json` - `NGROK_AUTHTOKEN`
  - `.env/postgresql_neondb.json` - Future PostgreSQL migration (not yet used)
- OR: Environment variables (take precedence over JSON files)
- Never hardcode secrets in source code (fallback values are placeholders only)

## Webhooks & Callbacks

**Incoming:**
- Cloudflare Turnstile callback: No webhook, verification is synchronous HTTP POST

**Outgoing:**
- None (no event-based callbacks to external systems)
- ngrok serves incoming traffic from internet to local app (not a webhook but public exposure)

## Data Flow Summary

**Quiz Generation Flow:**
1. User requests quiz via `routes/quiz.py`
2. System calls `utils/chatbot.py::query_ai_model()` with system prompt
3. OpenRouter API returns AI-generated question
4. Result stored in `AiQuizQuestion` table
5. Displayed to user in template

**Chatbot Flow:**
1. User sends message via `routes/chatbot.py::send_message()`
2. CSRF token validated (Flask-WTF)
3. Rate limiter checks (Flask-Limiter: 20/minute)
4. Message persisted to `AiChatMessage` table
5. OpenRouter API called via `utils/chatbot.py::query_ai_model()`
6. AI response persisted and returned as JSON
7. Client renders response in chat UI

**Scammer Report Flow:**
1. User submits report via `routes/scammer.py`
2. Cloudflare Turnstile verification via HTTPS POST
3. Fallback to math CAPTCHA if Turnstile unavailable
4. Anti-spam scoring by IP, account, cookie
5. Report encrypted and stored in `ScammerReport` table
6. Admin moderation via `routes/admin.py`

---

*Integration audit: 2026-04-13*
