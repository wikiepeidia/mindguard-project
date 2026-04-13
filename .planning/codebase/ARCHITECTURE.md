# Architecture

> Mapped: 2026-04-13

## Pattern

Monolithic Flask app with blueprints-based routing, layered architecture (routes → services → models), NeonDB PostgreSQL + SQLAlchemy ORM, server-side Jinja2 rendering.

## Layers

### Routes (routes/)
8 Flask blueprints handling HTTP requests:
- `main.py` — Homepage, statistics, leaderboard
- `auth.py` — Login, register, password reset, OTP verification
- `quiz.py` — Quiz flow with dynamic AI questions
- `scammer.py` — Scammer reporting, profile viewing
- `chatbot.py` — AI chat endpoints (send, api, support, rename)
- `admin.py` — Admin dashboard, moderation, export, suspension
- `library.py` — Knowledge base articles
- `api.py` — Internal JSON API endpoints

### Services (services/)
Business logic encapsulation:
- `anti_spam.py` — Multi-signal rate limiting and risk scoring (IP + cookie + account)
- `leaderboard_integrity.py` — Reporter rankings with weighted integrity scoring
- `sensitive_access_log.py` — Audit trail for admin PII access
- `admin_guard.py` — Admin suspension logic

### Models (models/models.py)
13 SQLAlchemy models including: Registration, ScammerReport, AiChatSession, AiChatMessage, QuizResult, AntiSpamEvent, SensitiveAccessLog, etc.

### Utils (utils/)
Cross-cutting utilities:
- `ai_agent.py` — OpenRouter API client
- `chatbot.py` — Message handling, system prompt, sensitive topic blocking, fallback
- `encryption.py` — Data encryption/decryption
- `helpers.py` — Decorators, risk scoring, CAPTCHA verification, badge helpers
- `privacy_policy.py` — PII masking (phone, email, CCCD)
- `quiz_data.py` — Static question bank + quiz configuration
- `ngrok_tunnel.py` — Public tunneling for demos

### Config/Extensions
- `config.py` — Application settings, API key loading from `.env/` JSON files
- `extensions.py` — db, mail, limiter, csrf initialization

## Entry Points

- `app.py` — Main entry point. Creates Flask app, registers 8 blueprints, configures logging, runs `db.create_all()` on startup.
- `vercel.json` — Vercel serverless entry: routes all requests to `app.py`

## Data Flow

### Auth Flow
Browser → `routes/auth.py` → CAPTCHA verification (Cloudflare + math) → Werkzeug password hash → Flask session creation → role-based access

### Scammer Report Flow
Browser → `routes/scammer.py` → Anti-spam scoring (AntiSpamDecisionService) → Reporter anonymization (SHA-256 hash) → DB persistence → Admin moderation queue → Leaderboard update

### Quiz Flow
Browser → `routes/quiz.py` → Session-based state → 15 static + 1 AI question → POST-redirect-GET pattern → Score calculation → Certificate generation

### Chatbot Flow
Browser → `routes/chatbot.py` → Sensitive topic check → OpenRouter API (multi-model fallback) → `simple_bot_reply()` fallback → Persistent chat sessions per user

### Leaderboard Flow
Browser → `routes/main.py` → On-demand aggregation by `reporter_hash` → Weighted integrity scoring → Ranked display

## Key Abstractions

- **AntiSpamDecisionService** — Multi-signal cooldown with configurable thresholds per actor type
- **Reporter anonymization** — SHA-256 hash of reporter identity for privacy
- **Dynamic quiz questions** — AI-generated questions from real scammer reports via OpenRouter
- **Sensitive access audit** — Every admin view of unmasked PII logged to SensitiveAccessLog
- **PII masking** — Template filters mask phone, email, CCCD in public views
- **Rate limiting** — Flask-Limiter with SQLAlchemy storage backend for Vercel serverless
