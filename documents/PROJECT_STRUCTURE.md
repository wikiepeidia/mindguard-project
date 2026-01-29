# 📂 Project Structure Guide

## Overview
```
mindguard_flask_v2/
│
├── 📄 app.py                    # Main application entry point
├── 📄 config.py                 # Configuration settings
├── 📄 models.py                 # Database models
│
├── 📁 routes/                   # Blueprint routes (modular)
│   ├── __init__.py
│   ├── main.py                 # Homepage, leaderboard
│   ├── scammer.py              # Scammer reporting
│   ├── chatbot.py              # Chatbot functionality
│   ├── quiz.py                 # Quiz & certificates
│   ├── auth.py                 # User registration
│   └── admin.py                # Admin dashboard
│
├── 📁 utils/                    # Utility functions
│   ├── __init__.py
│   ├── encryption.py           # Encryption & hashing
│   ├── helpers.py              # General helpers
│   ├── chatbot.py              # Chatbot AI logic
│   └── quiz_data.py            # Quiz questions
│
├── 📁 templates/                # HTML templates
│   ├── base.html               # Base template
│   ├── index.html              # Homepage
│   ├── report_scammer.html     # NEW: Scammer reporting
│   ├── leaderboard.html        # NEW: Scammer leaderboard
│   ├── admin_scammer_reports.html  # NEW: Admin reports
│   ├── chatbot.html            # Chatbot page
│   ├── quiz.html               # Quiz page
│   ├── quiz_result.html        # Quiz results
│   ├── certificate.html        # Certificate
│   ├── register.html           # Registration
│   ├── report_scam.html        # Old scam report
│   ├── admin_login.html        # Admin login
│   └── admin_dashboard.html    # Admin dashboard
│
├── 📁 static/                   # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
│
├── 📁 instance/                 # Database files
│   └── mindguard.db
│
├── 📁 packages/                 # Package management
│   ├── requirements.txt
│   └── installer.py
│
├── 📁 .venv/                    # Virtual environment
│
├── 📄 CHANGELOG.md             # NEW: Detailed changelog
├── 📄 SUMMARY.md               # NEW: Quick summary
└── 📄 README.md                # Project documentation
```

## 🔍 File Descriptions

### Core Files

#### `app.py`
- Main Flask application
- Registers all blueprints
- Initializes database
- Entry point for running the app

#### `config.py`
- All configuration settings
- Admin credentials
- Database URI
- Encryption keys
- App settings

#### `models.py`
- All database models:
  - `ScamReport` - Old scam reports
  - `Registration` - User registrations
  - `QuizResult` - Quiz results
  - `ScammerReport` - **NEW** Scammer reports
  - `ScammerLeaderboard` - **NEW** Leaderboard
  - `ChatSupportMessage` - **NEW** Support chats

### Routes (Blueprints)

#### `routes/main.py`
- `/` - Homepage
- `/leaderboard` - Scammer leaderboard

#### `routes/scammer.py`
- `/scammer/report` - Report scammer (NEW)
- `/scammer/old-report` - Old report form

#### `routes/chatbot.py`
- `/chatbot/` - Chatbot page
- `/chatbot/api` - Scam analysis API
- `/chatbot/support` - Support chat API (NEW)

#### `routes/quiz.py`
- `/quiz` - Quiz page
- `/quiz/result` - Results page
- `/certificate` - Certificate page

#### `routes/auth.py`
- `/register` - User registration

#### `routes/admin.py`
- `/admin/login` - Admin login
- `/admin/logout` - Admin logout
- `/admin/` - Admin dashboard
- `/admin/scammer-reports` - **NEW** Scammer reports
- `/admin/approve-report/<id>` - **NEW** Approve report
- `/admin/reject-report/<id>` - **NEW** Reject report

### Utilities

#### `utils/encryption.py`
- `hash_reporter_id()` - Hash reporter identity
- `encrypt_scammer_info()` - Encrypt scammer data
- `validate_evidence()` - Validate evidence
- `serialize_evidence()` - Convert to JSON
- `deserialize_evidence()` - Parse JSON

#### `utils/helpers.py`
- `generate_certificate_code()` - Generate cert codes
- `generate_session_id()` - Generate session IDs
- `calculate_danger_level()` - Calculate danger level
- `auto_approve_report()` - Auto-approval logic

#### `utils/chatbot.py`
- `simple_bot_reply()` - Main chatbot AI
- `generate_support_reply()` - Support chatbot

#### `utils/quiz_data.py`
- `quiz_questions` - All 15 quiz questions

## 🎨 Template Hierarchy

```
base.html (extends nothing)
├── index.html
├── report_scammer.html (NEW)
├── leaderboard.html (NEW)
├── chatbot.html
├── quiz.html
├── quiz_result.html
├── certificate.html
├── register.html
├── report_scam.html
├── admin_login.html
├── admin_dashboard.html
└── admin_scammer_reports.html (NEW)
```

## 📊 Database Schema

### ScammerReport
```sql
id                  INTEGER PRIMARY KEY
scammer_identifier  TEXT (encrypted)
scammer_name        TEXT
scam_type          TEXT
platform           TEXT
description        TEXT
evidence_urls      TEXT (JSON)
reporter_hash      TEXT (hashed)
status             TEXT (pending/approved/rejected)
report_count       INTEGER
created_at         DATETIME
updated_at         DATETIME
```

### ScammerLeaderboard
```sql
id              INTEGER PRIMARY KEY
scammer_id      INTEGER (FK → ScammerReport)
total_reports   INTEGER
danger_level    TEXT (low/medium/high/critical)
last_reported   DATETIME
```

### ChatSupportMessage
```sql
id            INTEGER PRIMARY KEY
session_id    TEXT
user_message  TEXT
bot_reply     TEXT
created_at    DATETIME
```

## 🔄 Data Flow

### Scammer Reporting Flow
```
User Input → Validation → Encryption → Database
                ↓
        Auto-Approval Check
                ↓
    Approved/Pending/Rejected
                ↓
        Update Leaderboard
                ↓
        Notify User
```

### Chat Support Flow
```
User Message → Support Bot → AI Logic
                                ↓
                          Generate Reply
                                ↓
                          Save to DB
                                ↓
                          Return Response
```

## 🔧 How to Modify

### Add a new route:
1. Create file in `routes/` (e.g., `routes/new_feature.py`)
2. Define blueprint and routes
3. Register in `app.py`

### Add a new model:
1. Add class to `models.py`
2. Run app to create table automatically

### Add a new utility:
1. Create file in `utils/` (e.g., `utils/new_helper.py`)
2. Import in route file
3. Use in your routes

### Add a new template:
1. Create HTML in `templates/`
2. Extend `base.html`
3. Use in route with `render_template()`

## 🎯 Key Features Location

| Feature | File(s) |
|---------|---------|
| Scammer Reporting | `routes/scammer.py`, `templates/report_scammer.html` |
| Leaderboard | `routes/main.py`, `templates/leaderboard.html` |
| Encryption | `utils/encryption.py` |
| Auto-Approval | `utils/helpers.py` → `auto_approve_report()` |
| Support Chat | `routes/chatbot.py` → `/chatbot/support` |
| Danger Levels | `utils/helpers.py` → `calculate_danger_level()` |
| Admin Reports | `routes/admin.py`, `templates/admin_scammer_reports.html` |

## 📝 Notes

- All routes use **blueprints** for modularity
- Database is **SQLite** (easy to switch to PostgreSQL)
- Encryption uses **SHA-256** (upgrade to Fernet for production)
- **Auto-approval** reduces admin workload
- **Session-based** reporter tracking
- **AJAX** for support chat
- **Bootstrap 5** for styling

---

This structure makes the app:
✅ **Easy to understand**
✅ **Easy to maintain**
✅ **Easy to extend**
✅ **Production-ready**
