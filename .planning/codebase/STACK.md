# Technology Stack

**Analysis Date:** 2026-03-19

## Languages

**Primary:**
- Python 3.x - Backend application, routing, business logic, and data layer in `app.py`, `routes/*.py`, `utils/*.py`, `models/models.py`
- HTML (Jinja2 templates) - Server-rendered UI in `templates/*.html`

**Secondary:**
- JavaScript (ES6+) - Frontend behavior and API calls in `static/js/*.js`
- CSS - UI styling in `static/css/*.css`
- SQL (via ORM) - Database access through SQLAlchemy models and query APIs in `models/models.py` and route handlers

## Runtime

**Environment:**
- Python runtime - required by Flask app startup in `app.py`
- Browser runtime - required for client-side scripts and browser extension in `static/js/*.js` and `browser_extension/*.js`

**Package Manager:**
- pip - dependencies pinned in `requirements.txt` and `packages/requirements.txt`
- Lockfile: missing (no `poetry.lock`, `Pipfile.lock`, or `requirements.lock` detected)

## Frameworks

**Core:**
- Flask 3.0.3 - HTTP app and blueprint routing in `app.py`, `routes/*.py`
- Flask-SQLAlchemy 3.1.1 - ORM and database sessions in `extensions.py`, `models/models.py`
- Flask-Mail 0.9.1 - Mail extension initialized in `extensions.py` and `app.py` (no active send workflow detected)

**Testing:**
- Not detected as a formal test framework dependency (no pytest/unittest runner config found in manifests)
- Script-style test utilities are present in `tests/*.py` and `database/test/*.py`

**Build/Dev:**
- Werkzeug 3.0.3 - Flask dev server/runtime support via Flask stack (`requirements.txt`)
- pyngrok 7.1.5 - local tunnel for development exposure in `utils/ngrok_tunnel.py` and startup path in `app.py`

## Key Dependencies

**Critical:**
- `Flask==3.0.3` - web framework and request lifecycle (`app.py`, `routes/*.py`)
- `Flask-SQLAlchemy==3.1.1` - persistence layer (`extensions.py`, `models/models.py`)
- `Werkzeug==3.0.3` - request handling and utility helpers used by Flask (`routes/scammer.py` uses `secure_filename`)
- `requests==2.31.0` - Cloudflare Turnstile verification HTTP calls in `routes/auth.py` and `routes/scammer.py`

**Infrastructure:**
- `Flask-Mail==0.9.1` - extension registration in `extensions.py`; integration surface exists for transactional email but not wired to SMTP config in `config.py`
- `pyngrok==7.1.5` - optional public tunnel in dev mode (`utils/ngrok_tunnel.py`)
- `MarkupSafe==2.1.5` - template-safe rendering in `app.py` (`nl2br` filter)

## Configuration

**Environment:**
- Main app config uses class-based settings in `config.py`
- Secret/config fallback pattern: read env vars first, then JSON files in `.env/` directory (`load_local_env` in `config.py`)
- External/service settings used by code:
  - `SECRET_KEY`
  - `OPENROUTER_API_KEY`
  - `CLOUDFLARE_SITE_KEY`
  - `CLOUDFLARE_SECRET_KEY`
  - `NGROK_AUTHTOKEN` (via env or `.env/ngrok.json` in `utils/ngrok_tunnel.py`)

**Build:**
- No separate build system (Flask server run directly in `app.py`)
- Static assets served by Flask from `static/`
- Browser extension packaged separately in `browser_extension/manifest.json` (Chrome Extension Manifest V3)

## Platform Requirements

**Development:**
- Python environment with pip-installable dependencies from `requirements.txt`
- Local writable filesystem for SQLite DB at `database/mindguard_v2.db` (configured in `config.py`)
- Optional `.env/*.json` config files for Cloudflare/OpenRouter/ngrok fallback

**Production:**
- WSGI-compatible Python host for Flask app
- Persistent filesystem for SQLite and uploaded evidence files (`static/uploads/evidence/` created in `routes/scammer.py`)
- Network egress to:
  - OpenRouter API (`https://openrouter.ai/api/v1/chat/completions` in `utils/chatbot.py`)
  - Cloudflare Turnstile verify endpoint (`https://challenges.cloudflare.com/turnstile/v0/siteverify`)
  - Optional ngrok service when enabled in `utils/ngrok_tunnel.py`

---

*Stack analysis: 2026-03-19*
