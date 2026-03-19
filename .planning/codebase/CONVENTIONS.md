# Coding Conventions

**Analysis Date:** 2026-03-19

## Naming Patterns

**Files:**
- Python modules use `snake_case.py` for routes and utilities, e.g. `routes/scammer.py`, `utils/ngrok_tunnel.py`.
- Blueprint modules are grouped by feature under `routes/` (`admin.py`, `auth.py`, `chatbot.py`, `main.py`, `quiz.py`, `scammer.py`).
- Model definitions are centralized in `models/models.py` and re-exported via `models/__init__.py`.

**Functions:**
- Function names are `snake_case`, including route handlers and helpers (`report_scammer`, `generate_math_problem`, `calculate_risk_score`).
- Flask route handlers commonly use verb/action names (`login`, `register`, `send_message`, `follow_scammer`).
- Decorators follow role-based naming (`login_required`, `admin_required`) in `utils/helpers.py`.

**Variables:**
- Local variables are `snake_case` (`captcha_success`, `scammer_identifier`, `pending_data`).
- Session keys are lower-case strings with underscores (`registration_email`, `math_captcha_answer_report`).
- Constants are `UPPER_SNAKE_CASE` in config (`OPENROUTER_MODELS`, `CLOUDFLARE_SECRET_KEY`) and scripts (`IGNORE_DIRS`, `IGNORE_FILES`).

**Types:**
- SQLAlchemy model classes use `PascalCase` (`ScammerReport`, `AiChatMessage`).
- DB table names are lowercase plural/snake style via `__tablename__` (`scammer_reports`, `ai_chat_sessions`).
- Type hints are used selectively in helper functions (`generate_certificate_code() -> str`) but are not consistently applied project-wide.

## Code Style

**Formatting:**
- No auto-formatter config detected (`pyproject.toml`, `setup.cfg`, `tox.ini`, `ruff.toml` not detected at workspace root).
- Style is maintained manually; most files use 4-space indentation and line lengths near 120 chars.
- One script (`packages/installer.py`) uses tabs, showing style drift between utility scripts and app modules.

**Linting:**
- Linting config exists at `.github/.pylintrc`.
- Project-level rules in `.github/.pylintrc` disable several strict checks:
  - `C0114`, `C0115`, `C0116` (docstrings)
  - `C0103` (invalid-name)
  - `R0913`, `R0903` (complexity/shape limits)
  - `W0511` (TODO/FIXME)
- Maximum line length is set to 120 in `.github/.pylintrc`.

## Import Organization

**Order:**
1. Standard library imports (`os`, `json`, `datetime`, `random`, `uuid`).
2. Third-party imports (`flask`, `sqlalchemy`, `requests`, `werkzeug`).
3. Local project imports (`models`, `extensions`, `utils.*`, `config`).

**Path Aliases:**
- Not detected. Imports use root-level absolute module paths such as `from models import ...`, `from utils.helpers import ...`, and `from extensions import db`.
- Several files perform local-in-function imports to avoid circular imports or reduce startup dependencies (e.g. `routes/auth.py`, `app.py`).

## Error Handling

**Patterns:**
- Route and utility code prefer `try/except` around external calls and JSON parsing.
- Broad exception catches are common (`except:` and `except Exception`) in:
  - `routes/auth.py`
  - `routes/main.py`
  - `routes/scammer.py`
  - `utils/ai_agent.py`
  - `utils/chatbot.py`
  - `config.py`
- User-facing failures in routes are usually handled with Flask `flash(...)` messages and redirects/renders.
- Utility/script failures are often handled by returning fallback values (`None`, static strings) or printing diagnostics.

## Logging

**Framework:** `print`-based logging and Flask flash messaging

**Patterns:**
- No centralized `logging` module configuration detected.
- Runtime diagnostics are printed directly in app startup and scripts (`app.py`, `tests/*.py`, `database/*.py`).
- User-visible status/errors rely on UI flash categories (`success`, `warning`, `danger`, `info`) in route handlers.

## Comments

**When to Comment:**
- Comments are used heavily to describe control-flow intent, especially in route handlers (`routes/auth.py`, `routes/scammer.py`, `routes/main.py`).
- Inline comments frequently annotate behavior changes and fallback decisions.

**JSDoc/TSDoc:**
- Not applicable (Python codebase).
- Python docstrings are present in many modules/functions but are not enforced by linting rules.

## Function Design

**Size:**
- Route handlers can be large and multi-responsibility, especially:
  - `routes/auth.py::login`
  - `routes/auth.py::register`
  - `routes/scammer.py::report_scammer`
  - `routes/main.py::index`
- Helper functions in `utils/helpers.py` are generally smaller and single-purpose.

**Parameters:**
- Route handlers rely on `request.form`, `request.get_json()`, and `session` instead of explicit parameter objects.
- Helpers use primitive inputs (`str`, `int`, `bool`) and return primitives or small dicts.

**Return Values:**
- Flask route handlers return `render_template`, `redirect`, or JSON responses (`jsonify`).
- Utility functions return nullable values on failure (`None` or fallback text/object) instead of raising custom exceptions.

## Module Design

**Exports:**
- `models/__init__.py` acts as a re-export module for SQLAlchemy models and `db`.
- Route modules export one `Blueprint` each (`*_bp`) and route functions.
- Utility modules export free functions rather than classes.

**Barrel Files:**
- Present for `models` and `routes` packages (`models/__init__.py`, `routes/__init__.py`).
- No broader barrel/export-index pattern detected beyond package init files.

## Prescriptive Guidance For New Code

- Add new web handlers as a dedicated module in `routes/` with a `Blueprint` named `<feature>_bp`.
- Keep module and function names in `snake_case`; keep model classes in `PascalCase`.
- Use root absolute imports (`from models import ...`, `from extensions import db`) to match existing project layout.
- For user-facing errors in routes, use `flash(..., <category>)` and redirect/render instead of uncaught exceptions.
- For external API calls, wrap requests in `try/except` and provide deterministic fallback behavior.
- Follow `.github/.pylintrc` constraints (120-char lines, relaxed docstring/name rules) unless lint policy is tightened later.

---

*Convention analysis: 2026-03-19*