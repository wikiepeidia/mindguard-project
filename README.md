# MindGuard

> A community-driven fraud awareness platform that educates Vietnamese users about scams through quizzes, enables scammer reporting with community verification, and provides AI chatbot guidance.

---

## Overview

MindGuard is a web-based platform designed to protect Vietnamese citizens of all ages from online fraud and scams. Inspired by Checkscam.vn, it combines education (interactive quizzes about scam types), community action (scammer reporting with verification badges and a public leaderboard), and AI assistance (chatbot powered by OpenRouter for fraud prevention guidance). It also includes a curated knowledge base of articles about specific scam types and prevention tips, managed by administrators.

The platform serves three user types: learners (taking quizzes, reading articles), reporters (submitting and verifying scammer reports), and administrators (managing content and moderating reports). By gamifying fraud awareness and leveraging community intelligence, MindGuard makes fraud prevention accessible and engaging.

---

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Frontend | Jinja2 Templates + Bootstrap 5 | Server-side rendered HTML |
| Styling | Bootstrap 5 + Custom CSS | Light-mode semantic tokens |
| Backend | Python 3.12.10 + Flask 3.0.3 | Blueprints-based routing |
| Database | SQLite 3 | Via SQLAlchemy ORM |
| ORM | Flask-SQLAlchemy 3.1.1 | |
| Auth | Flask sessions + Werkzeug | Password hashing, OTP email verification |
| AI Integration | OpenRouter API | Free models: Mistral, Qwen, Llama |
| Anti-Bot | Cloudflare Turnstile | CAPTCHA for forms |
| Hosting | localhost + ngrok | Production target TBD |

---

## Getting Started

### Prerequisites

- Python 3.12.10+
- pip (package manager)
- No external database needed (SQLite file-based)

### Installation

```bash
git clone <repo-url>
cd mindguard_flask_v2
pip install -r requirements.txt
# Or use the custom installer:
python packages/Installer.py
```

### Database Setup

```bash
cd database/
python create_database.py      # Initialize schema
python seed_kb_articles.py     # Load sample articles
python create_admin.py         # Create admin user
cd ..
```

### Running Locally

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

Admin panel: [http://localhost:5000/admin](http://localhost:5000/admin) (dev credentials: `admin` / `mindguard2025`)

### Running Tests

```bash
python -m pytest
```

---

## Project Structure

```
mindguard_flask_v2/
├── app.py                  # Flask application entry point
├── config.py               # Configuration settings
├── extensions.py           # SQLAlchemy & Flask-Mail init
├── requirements.txt        # Python dependencies
├── routes/                 # Flask blueprints (auth, quiz, scammer, chatbot, admin, etc.)
├── models/                 # SQLAlchemy database models
├── services/               # Business logic (anti-spam, leaderboard integrity)
├── utils/                  # Helpers (AI agent, encryption, privacy, quiz data)
├── templates/              # Jinja2 HTML templates
├── static/                 # CSS, JS, uploaded files
├── database/               # SQLite DB, migrations, seed scripts
├── tests/                  # Test suite
├── documents/              # SOP docs, changelog, guides
├── packages/               # Custom installer for deployment
├── docs/                   # Technical & user documentation
├── PRD.md                  # Product requirements (source of truth)
├── TODO.md                 # Project backlog
└── CLAUDE.md               # Claude AI instructions
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `.env/chatbot.json` → `api_key` | Yes | OpenRouter API key for AI chatbot |
| `.env/cloudflare.json` → `site_key`, `secret_key` | Yes | Cloudflare Turnstile CAPTCHA keys |
| `.env/ngrok.json` → `auth_token` | No | Ngrok auth token for public tunneling |
| `config.py` → `SECRET_KEY` | Yes | Flask secret key (change in production!) |

---

## Deployment

Currently runs locally with optional ngrok tunneling for public access. Production deployment target is TBD.

---

## License

Not yet specified.
