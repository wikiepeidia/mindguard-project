# Technology Stack

**Analysis Date:** 2026-04-13

## Languages

**Primary:**
- Python 3.12.10 - Backend application logic, all server-side code
- Jinja2 (templating language) - Server-side HTML rendering
- JavaScript - Client-side interactivity (chatbot, quiz, form validation)
- HTML5 / CSS3 - Markup and styling

**Secondary:**
- JSON - Configuration files (`.env/` directory for credentials and API keys)

## Runtime

**Environment:**
- CPython 3.12.10 - Standard Python runtime

**Package Manager:**
- pip - Python package management
- Lockfile: Present (`requirements.txt` and `packages/requirements.txt` identical)

## Frameworks

**Core:**
- Flask 3.0.3 - Web framework, request routing, session management, error handling
- Flask-SQLAlchemy 3.1.1 - ORM layer for database abstraction
- Werkzeug 3.0.3 - WSGI utilities, password hashing (Werkzeug.security)

**Utilities & Extensions:**
- Flask-Mail 0.9.1 - SMTP email integration (OTP delivery, notifications)
- Flask-Limiter 3.5.0 - Rate limiting and anti-spam on routes
- Flask-WTF 1.2.2 - CSRF protection via CSRFProtect
- pyngrok 7.1.5 - ngrok tunnel management for public URL exposure during development
- requests 2.31.0 - HTTP client library for external API calls
- MarkupSafe 2.1.5 - Safe HTML escaping in Jinja2 templates

**Testing:**
- pytest (referenced in documentation, may be installed separately)
- unittest (Python standard library)

## Key Dependencies

**Critical:**
- Flask 3.0.3 - Application framework; all routes, blueprints, and request handling depend on this
- Flask-SQLAlchemy 3.1.1 - Provides ORM and database session management; all database queries use SQLAlchemy
- Werkzeug 3.0.3 - Password hashing via `generate_password_hash()` and `check_password_hash()` in auth flows

**Infrastructure:**
- pyngrok 7.1.5 - Exposes local development server publicly; required for ngrok tunneling feature
- requests 2.31.0 - Calls OpenRouter API for AI chatbot and quiz generation; calls Cloudflare Turnstile verification
- Flask-Limiter 3.5.0 - Multi-signal rate limiting (account, cookie, IP-based); prevents spam abuse

**Security:**
- Flask-WTF 1.2.2 - Prevents CSRF attacks on POST/PUT/DELETE endpoints

## Configuration

**Environment:**
- Configuration loaded from `config.py` which reads environment variables and JSON files from `.env/` directory
- Environment variables override JSON defaults:
  - `SECRET_KEY` - Flask session encryption key (stored in config.py or env var)
  - `OPENROUTER_API_KEY` - AI service authentication (from env or `.env/chatbot.json`)
  - `CLOUDFLARE_SITE_KEY` - Public CAPTCHA key (from env or `.env/cloudflare.json`)
  - `CLOUDFLARE_SECRET_KEY` - CAPTCHA secret key (from env or `.env/cloudflare.json`)
  - `NGROK_AUTHTOKEN` - Ngrok tunnel auth (from env or `.env/ngrok.json`)
  - `ADMIN_UNSUSPEND_SECRET` - Admin unlock secret (from env or hardcoded)
  - `ABUS_MODE` - Anti-spam mode: "monitor" or "enforce" (env var, default "monitor")
  - `ABUS_WINDOW_MINUTES`, `ABUS_THRESHOLD_COUNT`, `ABUS_COOLDOWN_MINUTES` - Anti-spam parameters

**Build:**
- No build configuration (Flask serves directly from source)
- `static/` directory contains unprocessed CSS and JavaScript
- `templates/` directory contains Jinja2 HTML files
- No minification, bundling, or transpilation step

**Database Configuration:**
```
SQLALCHEMY_DATABASE_URI = "sqlite:////[project_root]/database/mindguard_v2.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
```

## Platform Requirements

**Development:**
- Windows 11 IoT Enterprise or Linux/macOS with Python 3.12.10
- pip package manager
- Text editor or IDE (VSCode, PyCharm, etc.)
- Optionally: ngrok CLI (tunneling) or use pyngrok instead
- Optional: Cloudflare Turnstile account for CAPTCHA (fallback: math CAPTCHA available)

**Production:**
- Target: Cloud deployment platform (AWS, Heroku, Railway, Vercel, etc.)
- Currently runs on localhost:5000 with Flask development server
- For production: Gunicorn, uWSGI, or similar WSGI server required
- Database: SQLite (file-based, no external DB server needed; upgrade to PostgreSQL when scaling)
- HTTP Tunneling: ngrok public URL or traditional domain + SSL

**Deployment Notes:**
- Flask development server (used via `python app.py`) is single-threaded and not suitable for production traffic
- No Docker configuration present (manual deployment only)
- No CI/CD pipeline configured (GitHub Actions planned)
- Environment variables must be set before running in production

---

*Stack analysis: 2026-04-13*
