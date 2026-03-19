# External Integrations

**Analysis Date:** 2026-03-19

## APIs & External Services

**AI Inference:**

- OpenRouter - LLM chat completions for chatbot and support assistant
  - SDK/Client: built-in `urllib.request` (no official SDK package), implemented in `utils/chatbot.py`
  - Auth: `OPENROUTER_API_KEY` from `config.py`
  - Endpoint: `https://openrouter.ai/api/v1/chat/completions`
  - Model fallback chain: configured in `Config.OPENROUTER_MODELS` in `config.py`

**Bot Protection / CAPTCHA:**

- Cloudflare Turnstile - anti-bot validation on login/register/report forms
  - SDK/Client: `requests` HTTP calls in `routes/auth.py` and `routes/scammer.py`
  - Auth: `CLOUDFLARE_SECRET_KEY` (server-side), `CLOUDFLARE_SITE_KEY` (template rendering)
  - Endpoint: `https://challenges.cloudflare.com/turnstile/v0/siteverify`
  - Frontend script loaded in `templates/login.html`, `templates/register.html`, `templates/report_scammer.html`

**Development Tunnel:**

- ngrok - optional public URL for local development
  - SDK/Client: `pyngrok` in `utils/ngrok_tunnel.py`
  - Auth: `NGROK_AUTHTOKEN` (env or `.env/ngrok.json`)
  - Invocation: app startup path in `app.py`

**Frontend CDN Services:**

- jsDelivr CDN - Bootstrap CSS/JS in `templates/base.html`
- Cloudflare CDNJS - Font Awesome CSS in `templates/base.html`
- unpkg CDN - AOS library in `templates/base.html`

## Data Storage

**Databases:**

- SQLite (local file DB)
  - Connection: `SQLALCHEMY_DATABASE_URI` built from local path in `config.py`
  - Client: Flask-SQLAlchemy (`extensions.py`, `models/models.py`)
  - Database file path target: `database/mindguard_v2.db`

**File Storage:**

- Local filesystem only
  - Uploaded evidence persisted under `static/uploads/evidence/` in `routes/scammer.py`
  - Additional upload directory exists at `uploads/evidence/` in repository root

**Caching:**

- None detected (no Redis/Memcached/cache library integration found)

## Authentication & Identity

**Auth Provider:**

- Custom session-based auth (Flask sessions)
  - Implementation: registration/login in `routes/auth.py`, decorator-based protection via `utils/helpers.py` (`login_required`), session keys checked in routes
  - Admin path: separate admin login flow in `routes/admin.py` and `/admin` redirect in `app.py`

## Monitoring & Observability

**Error Tracking:**

- None detected (no Sentry, Rollbar, Bugsnag, or equivalent integration found)

**Logs:**

- Basic stdout logging via `print(...)` and Flask dev output
  - Examples in `utils/chatbot.py`, `utils/ngrok_tunnel.py`, and startup banner in `app.py`

## CI/CD & Deployment

**Hosting:**

- Not explicitly defined in repository configuration
- Current run mode is direct Flask execution (`app.run(debug=True)` in `app.py`)

**CI Pipeline:**

- Not detected (no GitHub Actions workflow for test/build/deploy found in `.github/workflows/` during this tech scan)

## Environment Configuration

**Required env vars:**

- `SECRET_KEY` - Flask session secret (`config.py`)
- `OPENROUTER_API_KEY` - AI API access (`config.py`, `utils/chatbot.py`)
- `CLOUDFLARE_SITE_KEY` - Turnstile site widget key (`config.py`, templates)
- `CLOUDFLARE_SECRET_KEY` - Turnstile server verification key (`config.py`, `routes/auth.py`, `routes/scammer.py`)
- `NGROK_AUTHTOKEN` - optional local tunnel auth (`utils/ngrok_tunnel.py`)

**Secrets location:**

- Environment variables
- JSON fallback files under `.env/` loaded by `load_local_env` in `config.py`
- `.env` directory is present in workspace (contents intentionally not read)

## Webhooks & Callbacks

**Incoming:**

- None detected (no externally invoked webhook endpoints identified)

**Outgoing:**

- Outbound HTTP calls to:
  - OpenRouter completions API in `utils/chatbot.py`
  - Cloudflare Turnstile verify API in `routes/auth.py` and `routes/scammer.py`

---

*Integration audit: 2026-03-19*
