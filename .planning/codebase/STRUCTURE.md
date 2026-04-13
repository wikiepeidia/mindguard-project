# Structure

> Mapped: 2026-04-13

## Directory Layout

```
mindguard_flask_v2/
├── app.py                  # Entry point, blueprint registration, logging setup
├── config.py               # Config class, env vars, API key loading
├── extensions.py            # db, mail, limiter, csrf initialization
├── models/
│   └── models.py           # 13 SQLAlchemy models
├── routes/                 # 8 Flask blueprints
│   ├── main.py             # Homepage, stats, leaderboard
│   ├── auth.py             # Login, register, password reset, OTP
│   ├── quiz.py             # Quiz flow with dynamic questions
│   ├── scammer.py          # Report scammer, profiles
│   ├── chatbot.py          # AI chat endpoints
│   ├── admin.py            # Moderation dashboard
│   ├── library.py          # Knowledge base
│   └── api.py              # Internal JSON endpoints
├── services/               # Business logic
│   ├── anti_spam.py        # Rate limiting, risk scoring
│   ├── leaderboard_integrity.py  # Reporter rankings
│   ├── sensitive_access_log.py   # Audit trail
│   └── admin_guard.py      # Admin suspension logic
├── utils/                  # Shared utilities
│   ├── ai_agent.py         # OpenRouter client
│   ├── chatbot.py          # Message handling, AI safety
│   ├── encryption.py       # Data encryption
│   ├── helpers.py          # Decorators, scoring, CAPTCHA
│   ├── privacy_policy.py   # PII masking
│   ├── quiz_data.py        # Question bank
│   └── ngrok_tunnel.py     # Public tunneling
├── templates/              # 23+ Jinja2 templates
│   ├── base.html           # Master layout (all pages inherit)
│   ├── index.html          # Homepage with privacy banner
│   ├── login.html, register.html, verify_otp.html
│   ├── quiz.html, quiz_result.html, certificate.html
│   ├── report_scammer.html, scammer_profile.html
│   ├── chatbot.html, leaderboard.html, profile.html
│   ├── admin_dashboard.html, admin_login.html
│   ├── admin_scammer_reports.html, admin_sensitive_access_logs.html, admin_export.html
│   └── library.html, onboarding.html
├── static/
│   ├── css/                # 11 stylesheets (Bootstrap 5 + custom)
│   ├── js/                 # 13 vanilla JavaScript files
│   └── uploads/            # User-generated content
├── database/
│   ├── mindguard_v2.db     # SQLite file (legacy, NeonDB is primary)
│   ├── create_database.py, create_user.py
│   ├── seed_*.py           # Data seeding scripts
│   └── migrate_*.py        # Schema migration scripts
├── tests/                  # Test suite
│   ├── test_quiz.py, test_chatbot.py, test_ai_quiz.py
│   ├── antispam/, leaderboard/, quizflow/, privacy/, ui/
│   └── fixtures/
├── documents/              # Project documentation
├── logs/                   # access.log (auto-created)
├── .env/                   # Config JSON files (not in git)
└── .planning/              # GSD planning documents
```

## Naming Conventions

- **Files**: snake_case (`auth.py`, `quiz_data.py`)
- **Blueprints**: snake_case (`quiz_bp`, `auth_bp`, `scammer_bp`)
- **Functions**: snake_case (`generate_certificate_code`, `check_password_hash`)
- **Models**: PascalCase (`Registration`, `ScammerReport`, `AiChatSession`)
- **Routes**: kebab-case (`/report-scammer`, `/quiz/step/0`, `/chatbot/send`)
- **DB tables**: snake_case (`scam_reports`, `quiz_results`, `ai_chat_sessions`)

## Where to Add New Code

- **New route**: Add handler to appropriate blueprint in `routes/`
- **New model**: Add class to `models/models.py`
- **New business logic**: Create service in `services/` or extend existing
- **New utility**: Add to `utils/` (one concern per file)
- **New page**: Template in `templates/` + CSS in `static/css/` + JS in `static/js/`
- **New test**: Add to `tests/` in appropriate subdirectory
