# Architecture

**Analysis Date:** 2026-03-19

## Pattern Overview

**Overall:** Modular Flask monolith using Blueprint-based feature modules.

**Key Characteristics:**
- Application bootstraps in a single entrypoint (`app.py`) and registers feature blueprints as route boundaries.
- Data access is mostly route-driven through SQLAlchemy models imported from `models/models.py` and `extensions.py`.
- Utility modules in `utils/` provide cross-cutting logic (auth decorators, masking, risk scoring, AI calls, encryption) consumed by routes.

## Layers

**Application Bootstrap Layer:**
- Purpose: Create Flask app, load config, initialize extensions, register runtime routes and template globals.
- Location: `app.py`, `config.py`, `extensions.py`
- Contains: Flask app creation, `Config` loading, `db`/`mail` initialization, `app.register_blueprint(...)`, template filters, startup logic.
- Depends on: `routes/*`, `utils/helpers.py`, `extensions.py`, `config.py`
- Used by: All HTTP requests entering the process.

**HTTP Interface Layer (Blueprints):**
- Purpose: Handle request parsing, session checks, validation, render templates or JSON, and orchestrate database updates.
- Location: `routes/main.py`, `routes/auth.py`, `routes/quiz.py`, `routes/scammer.py`, `routes/chatbot.py`, `routes/admin.py`
- Contains: Web pages, JSON endpoints, redirects, flash messages, upload handling.
- Depends on: `models/`, `utils/`, `config.py`, Flask session/request APIs.
- Used by: Browser clients and frontend JavaScript.

**Data Access Layer (ORM Models):**
- Purpose: Define database schema and relationships for domain entities.
- Location: `models/models.py`, re-exported in `models/__init__.py`
- Contains: `Registration`, `ScamReport`, `ScammerReport`, `ScammerLeaderboard`, `QuizResult`, AI chat/session entities, `Subscription`.
- Depends on: `extensions.py` (`db` instance), SQLAlchemy metadata.
- Used by: All blueprint modules and utility logic that queries persistence.

**Domain Utility Layer:**
- Purpose: Shared business utilities reused across route modules.
- Location: `utils/helpers.py`, `utils/encryption.py`, `utils/ai_agent.py`, `utils/chatbot.py`, `utils/quiz_data.py`, `utils/ngrok_tunnel.py`
- Contains: Auth decorators, score/risk calculators, masking, CAPTCHA math fallback, identifier hashing, AI prompt/query wrappers.
- Depends on: Flask context/session (helpers), SQLAlchemy models (`ai_agent.py`), external HTTP (`utils/chatbot.py`).
- Used by: Feature blueprints in `routes/` and app bootstrap in `app.py`.

**Presentation Layer:**
- Purpose: Render server-side UI with static assets.
- Location: `templates/*.html`, `static/css/*`, `static/js/*`
- Contains: Jinja templates, page styles/scripts, dashboard/chatbot/quiz/report views.
- Depends on: Route context variables, `url_for` static routing.
- Used by: End users in browser.

## Data Flow

**Flow Name: Authenticated Web Request (Template Page)**

1. Client requests route (for example `/quiz`) mapped in `routes/quiz.py`.
2. `@login_required` from `utils/helpers.py` validates `session['registration_email']` and redirects if absent.
3. Route reads/writes models in `models/models.py` via `db.session` (`extensions.py`).
4. Route renders Jinja template from `templates/` with computed view model.
5. Browser loads matching assets from `static/css/` and `static/js/`.

**Flow Name: Scammer Report Submission**

1. User submits `POST /scammer/report` handled by `routes/scammer.py`.
2. CAPTCHA is validated (Cloudflare token first, then math fallback from `utils/helpers.py`).
3. Input is normalized by report type; uploaded files are stored under `static/uploads/evidence/` and serialized.
4. Identifier is transformed using `hash_reporter_id(...)` and `encrypt_scammer_info(...)` in `utils/encryption.py`.
5. Existing `ScammerReport` row is updated or a new row is inserted; leaderboard sync logic updates `ScammerLeaderboard`.
6. Client is redirected back with flash status.

**Flow Name: Chatbot Interaction**

1. Logged-in user sends message to `POST /chatbot/send` in `routes/chatbot.py`.
2. Route resolves user from session email in `Registration`.
3. Route creates/loads `AiChatSession`, stores user message in `AiChatMessage`.
4. AI response is generated via `query_ai_model(...)` in `utils/chatbot.py` with fallback `simple_bot_reply(...)`.
5. Bot reply is persisted as `AiChatMessage` and returned as JSON.

**State Management:**
- Request-level state: Flask request context.
- User/auth state: Cookie-based Flask session (`registration_email`, `is_admin`, quiz values).
- Persistent state: SQLite (`database/mindguard_v2.db`) accessed through SQLAlchemy models.

## Key Abstractions

**Blueprint-as-Module Boundary:**
- Purpose: Encapsulate route namespaces by feature.
- Examples: `routes/main.py`, `routes/scammer.py`, `routes/chatbot.py`, `routes/admin.py`, `routes/auth.py`, `routes/quiz.py`
- Pattern: One blueprint per module; app-level assembly in `app.py`.

**Session-backed Identity Context:**
- Purpose: Lightweight identity and role checks without Flask-Login.
- Examples: `utils/helpers.py` (`login_required`), `routes/admin.py` (`session.get('is_admin')`), `routes/auth.py`.
- Pattern: Session keys gate route access and personalization.

**Active Record-like ORM Usage:**
- Purpose: Route handlers execute queries directly on model classes.
- Examples: `models/models.py` entities used in `routes/main.py`, `routes/scammer.py`, `routes/admin.py`.
- Pattern: Query and mutation logic lives close to route handlers, with minimal repository/service layer.

## Entry Points

**Flask Runtime Entry:**
- Location: `app.py`
- Triggers: `python app.py` or WSGI startup.
- Responsibilities: Construct app, initialize extensions, register blueprints, set filters/context processor, run server.

**Web Entry (Public):**
- Location: `routes/main.py` (`/`), `routes/auth.py` (`/login`, `/register`), `routes/scammer.py` (`/scammer/report`)
- Triggers: Browser navigation/forms.
- Responsibilities: Public pages, auth, report intake, search/profile pages.

**Web Entry (Authenticated):**
- Location: `routes/quiz.py`, `routes/chatbot.py`, `routes/auth.py` (`/profile`)
- Triggers: Logged-in user actions.
- Responsibilities: Quiz lifecycle, certificate issuance, chat session history.

**Web Entry (Admin):**
- Location: `routes/admin.py` (prefix `/admin`)
- Triggers: Admin login/session.
- Responsibilities: Dashboard, moderation, user management, dataset export.

## Error Handling

**Strategy:** Localized defensive handling in route/util functions, usually with graceful fallback and user-facing flash messages.

**Patterns:**
- Broad `try/except` around external calls and JSON parsing (for example `utils/chatbot.py`, `routes/scammer.py`, `routes/main.py`).
- Redirect and flash on validation failures rather than central exception middleware.
- AI and CAPTCHA paths prefer fallback behavior over hard failure.

## Cross-Cutting Concerns

**Logging:** Minimal print-based logging in exception branches (`utils/chatbot.py`, `routes/scammer.py`, startup output in `app.py`).
**Validation:** Inline request validation in blueprint handlers plus helper-based utilities (math CAPTCHA generation in `utils/helpers.py`).
**Authentication:** Session-key checks through decorators and per-route guards (`utils/helpers.py`, `routes/admin.py`).

---

*Architecture analysis: 2026-03-19*