# MindGuard - AI Coding Agent Instructions

You are an expert developer working on **MindGuard**, a Flask-based cybersecurity education platform. This project combines a web application (Quiz, Reporting, Dashboard) with AI integrations (Chatbot, Scam Analysis).

## 🏗 Global Architecture

- **Framework**: Flask (Python) with `Flask-SQLAlchemy`.
- **Primary Language**: 
  - **User-facing**: **Vietnamese** (Required for all HTML, messages, and documentation).
  - **Code**: **English** (Comments, variable names).
- **Pattern**: Modular Blueprints. Logic is split into `routes/`, `models/`, `utils/`, and `services`.
- **Database**: SQLite (`database/mindguard_v2.db`).
  - **Migration Strategy**: **Manual scripts only** in `database/`. Do NOT use `flask db upgrade/migrate`.

## 📂 Project Structure & Key Files

- **Entry Point**: `app.py` (Registers blueprints: `admin`, `auth`, `chatbot`, `main`, `quiz`, `scammer`).
- **Configuration**: `config.py` 
  - **Critical**: Loads secrets from `.env/*.json` (e.g., `cloudflare.json`, `chatbot.json`) if env vars are missing.
- **Extensions**: `extensions.py` (Holds `db`, `mail` instances).
- **AI Engine**: `utils/ai_agent.py`. Integrates OpenRouter (DeepSeek, Gemini, Llama) for chatbot and dynamic content generation.
- **Frontend**:
  - `templates/`: Jinja2/HTML. `base.html` defines the layout.
  - `static/`: **Strict separation**. CSS in `static/css/`, JS in `static/js/`. Avoid inline styles/scripts.

## 🚀 Critical Workflows

### 1. Database Management
- **Schema Changes**: Create a standalone script in `database/` (e.g., `migrate_add_column.py`) using `app.app_context()`.
- **Seeding**: Use `database/seed_data.py` or `database/seed_scam_data.py`.

### 2. External Integrations
- **AI (OpenRouter)**:
  - Logic in `utils/ai_agent.py`.
  - Models: `google/gemini-2.0-flash-lite-preview-02-05:free`, `meta-llama/llama-3-8b-instruct:free`, `liquid/lfm-2.5-1.2b-thinking:free`.
  - **Pattern**: Fallback gracefully (try/except) if API fails; return static/cached content.
- **Security (Cloudflare)**:
  - Turnstile CAPTCHA is implemented on Login, Signup, and Report forms.
  - Config keys: `CLOUDFLARE_SITE_KEY`, `CLOUDFLARE_SECRET_KEY`.

## 🧩 Coding Conventions

### Imports & Dependencies
- **Absolute Imports**: `from models import User` (Root-level imports).
- **Extensions**: Import `db` from `extensions.py`, NOT `app.py` (Circular dependency risk).

### Authentication & Sessions
- **Admin**: Check `session.get('is_admin')`.
- **User**: Check `session.get('registration_email')`.
- **Decorator**: Use `@login_required` from `utils.helpers`.

### Frontend Guidelines
- **HTML**: All visible text must be **Vietnamese**.
- **Styles**: Use Bootstrap 5 utility classes where possible. Custom styles go in `static/css/*.css`. 
- **Js**: Use Bootstrap 5 utility classes where possible. Custom JS go in `static/js/*.js`. 
- **Assets**: Use `url_for('static', filename='...')`. NEver put any CSS/JS into  html files directly.

## 🛠 Troubleshooting
- **Cloudflare Issues**: Check `config.py` JSON loaders if keys aren't picking up from environment.
- **Database Locks**: SQLite may lock if multiple scripts access it. Ensure connections are closed.

