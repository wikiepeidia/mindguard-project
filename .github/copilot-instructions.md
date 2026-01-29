# MindGuard - AI Coding Agent Instructions

You are an expert developer working on **MindGuard**, a Flask-based cybersecurity education platform. This project combines a web application (Quiz, Reporting, Dashboard) with AI integrations (Chatbot, Scam Analysis).

## 🏗 Global Architecture

- **Framework**: Flask (Python) with `Flask-SQLAlchemy`.
- **Primary Language**: **Vietnamese** for user-facing content (HTML, messages) and documentation. **English** for code comments and variable names.
- **Pattern**: Modular Blueprints. Logic is split into `routes/`, `models/`, `utils/`, and `services`.
- **Database**: SQLite (Development). 
  - **Migration Strategy**: Manual scripts in `database/` folder (NO Flask-Migrate).
- **AI Integration**: OpenRouter API (DeepSeek, Gemini, Llama) handled in `utils/ai_agent.py`.

## 📂 Project Structure & Key Files

- **Entry Point**: `app.py` (Registers blueprints, initializes DB triggers).
- **Configuration**: `config.py` (Loads environment variables, defines defaults).
- **Extensions**: `extensions.py` (Holds `db`, `mail` instances to prevent circular imports).
- **Routes**: `routes/` folder. Each file is a Blueprint (e.g., `admin_bp`, `chatbot_bp`).
- **Models**: `models/` folder. All SQLAlchemy models.
- **Database Scripts**: `database/` folder containing standalone scripts for schema updates and seeding.
- **Unit Tests**: `tests/` folder containing standalone python scripts to valid logic.

## 🚀 Critical Workflows

### 1. Database Management (CRITICAL)
**Do NOT use `flask db upgrade`.**
- **Changes**: To modify schema, check `database/` for existing migration scripts or create a new `migrate_*.py` script.
- **Execution**: Run scripts directly: `python database/migrate_add_verification.py`.
- **Context**: Always wrap DB operations in `with app.app_context():` if writing standalone scripts.

### 2. Running & Testing
- **Run App**: `python app.py` (Debug mode enabled by default).
- **Run Tests**: Execute specific test scripts: `python tests/test_ai_quiz.py`.
- **Context**: Tests usually construct their own minimal app context.

## 🧩 Coding Conventions

### Imports & Dependencies
- Use **absolute imports**: `from models import User` instead of `from ..models import User`.
- Import `db` from `extensions.py`, NOT `app.py`.

### Authentication
- **Mechanism**: Session-based (`session['registration_email']`).
- **Protection**: Use `@login_required` decorator from `utils.helpers`.

### AI Integration
- **Location**: AI logic resides in `utils/ai_agent.py`.
- **Pattern**: Functions return raw text/JSON. Route handlers process this output.
- **Fail-safe**: Always wrap external API calls in `try/except` blocks to fallback gracefully if API fails.

### Styles & Templates
- **Frontend**: Bootstrap 5 + Custom CSS (`static/css/`).
- **Templates**: Jinja2 with `base.html` layout.
- **Language**: Ensure ALL user-visible text in `templates/` is in **Vietnamese**.

## 🛑 Common Pitfalls
- **Circular Imports**: Never import `app` inside `routes/`. Use `current_app` or `extensions.py`.
- **Paths**: Use `os.path.join(Config.BASE_DIR, ...)` for file paths (e.g., database, uploads).
- **Secrets**: Provide fallback values in `config.py` for local dev convenience (`os.environ.get(...) or "default"`).
