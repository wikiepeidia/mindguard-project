# Codebase Structure

**Analysis Date:** 2026-03-19

## Directory Layout

```text
mindguard_flask_v2/
├── app.py                     # Flask runtime entrypoint and blueprint wiring
├── config.py                  # Central configuration and local JSON env loading
├── extensions.py              # SQLAlchemy and Mail extension singletons
├── models/                    # ORM model definitions
├── routes/                    # Blueprint-based HTTP modules
├── utils/                     # Shared business and integration helpers
├── templates/                 # Jinja2 server-rendered pages
├── static/                    # Frontend assets (CSS/JS/uploads)
├── database/                  # Manual migration/seed scripts and DB utilities
├── tests/                     # Script-style test and debug files
├── browser_extension/         # Browser extension client package
├── datasets/                  # Exported CSV and dataset artifacts
├── documents/                 # Project documentation and reports
├── packages/                  # Installer and packaging helpers
├── updates/                   # Update artifacts/scripts
├── backup/                    # Backup project materials
└── .planning/codebase/        # Generated architecture/quality/codebase mapping docs
```

## Directory Purposes

**models/:**

- Purpose: Define persistence schema for domain entities.
- Contains: `db.Model` classes and table relationships.
- Key files: `models/models.py`, `models/__init__.py`

**routes/:**

- Purpose: Expose web/API endpoints by feature module.
- Contains: Blueprint declarations and request handlers.
- Key files: `routes/main.py`, `routes/auth.py`, `routes/scammer.py`, `routes/quiz.py`, `routes/chatbot.py`, `routes/admin.py`, `routes/api.py`, `routes/library.py`

**utils/:**

- Purpose: Cross-cutting helper logic and external integration wrappers.
- Contains: Auth decorators, risk/masking utilities, AI integrations, encryption, quiz data.
- Key files: `utils/helpers.py`, `utils/chatbot.py`, `utils/ai_agent.py`, `utils/encryption.py`, `utils/quiz_data.py`

**templates/:**

- Purpose: Server-side rendered HTML views.
- Contains: Public pages, auth pages, admin pages, quiz/chat/report pages.
- Key files: `templates/base.html`, `templates/index.html`, `templates/login.html`, `templates/report_scammer.html`, `templates/admin_dashboard.html`

**static/:**

- Purpose: Frontend resources served by Flask static handler.
- Contains: CSS, JavaScript, uploaded evidence files.
- Key files: `static/css/base.css`, `static/js/base.js`, `static/uploads/evidence/`

**database/:**

- Purpose: Manual schema evolution and seed operations.
- Contains: Migration scripts, seed scripts, DB setup/reset tools.
- Key files: `database/migrate_subscription.py`, `database/seed_data.py`, `database/seed_scam_data.py`

**tests/:**

- Purpose: Development-time validation scripts for AI, stats, and diagnostics.
- Contains: Script-style tests and output fixtures.
- Key files: `tests/test_ai_quiz.py`, `tests/test_stats.py`, `tests/test_openrouter_limits.py`

## Key File Locations

**Entry Points:**

- `app.py`: Main Flask app bootstrap and registration point.

**Configuration:**

- `config.py`: Runtime settings and local JSON env loading fallback.
- `extensions.py`: Shared initialized extension objects.
- `requirements.txt`: Python dependency baseline.

**Core Logic:**

- `routes/main.py`: Homepage, leaderboard, search, scammer profile details.
- `routes/auth.py`: Login, registration, OTP flow, profile management.
- `routes/scammer.py`: Scammer reporting intake, evidence uploads, follow/unfollow.
- `routes/quiz.py`: Quiz flow, scoring, certificate creation.
- `routes/chatbot.py`: Chat session UI and JSON chatbot APIs.
- `routes/admin.py`: Admin authentication, moderation, dashboard analytics/export.

**Testing:**

- `tests/`: Test and debug scripts.
- `database/test/`: DB inspection and migration helper scripts.

## Naming Conventions

**Files:**

- Python modules use snake_case (example: `routes/scammer.py`, `utils/ai_agent.py`).
- HTML templates use snake_case (example: `templates/report_scammer.html`).
- Static assets use snake_case and feature names (example: `static/js/chatbot_page.js`, `static/css/report_scammer.css`).

**Directories:**

- Feature or concern-oriented top-level directories (example: `routes/`, `models/`, `utils/`, `database/`).

## Where to Add New Code

**New Feature:**

- Primary code: Add new blueprint module under `routes/` and register in `app.py`.
- Tests: Add script or test module under `tests/` (or DB-specific checks under `database/test/`).

**New Component/Module:**

- Implementation: Add shared logic to `utils/` and call it from the owning route module.

**Utilities:**

- Shared helpers: Add to `utils/helpers.py` if generic; create a dedicated `utils/<feature>.py` for feature-specific logic.

## Module Boundaries

**Boundary: App Assembly vs Feature Routes**

- Composition root: `app.py`
- Feature modules: `routes/*.py`
- Rule: Keep route registration in `app.py`; avoid blueprint registration side effects inside feature modules.

**Boundary: Route Handlers vs ORM Schema**

- Request orchestration: `routes/*.py`
- Data schema: `models/models.py`
- Rule: Add/modify table fields in models plus manual migration scripts under `database/`.

**Boundary: Route Handlers vs Reusable Utilities**

- Route-specific flow: `routes/*.py`
- Reusable functions: `utils/*.py`
- Rule: Move shared calculations, decorators, external API wrappers, and crypto transforms into `utils/`.

**Boundary: Runtime-Active vs Currently Unwired Modules**

- Active blueprints registered in runtime: `routes/main.py`, `routes/scammer.py`, `routes/chatbot.py`, `routes/quiz.py`, `routes/auth.py`, `routes/admin.py` (registered in `app.py`).
- Present but not registered by default: `routes/api.py`, `routes/library.py`.

## Special Directories

**.planning/codebase/:**

- Purpose: Generated architecture/quality/stack mapping docs used by GSD planning workflow.
- Generated: Yes.
- Committed: Yes.

**instance/:**

- Purpose: Flask instance-specific runtime data.
- Generated: Yes.
- Committed: Yes (directory present).

****pycache** directories:**

- Purpose: Python bytecode caches.
- Generated: Yes.
- Committed: No (should be ignored).

**.env/:**

- Purpose: Local environment JSON configuration files.
- Generated: Manual/local.
- Committed: No (sensitive configuration area).

---

*Structure analysis: 2026-03-19*
