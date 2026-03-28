<!--
DOCUMENT METADATA
Owner: @systems-architect (all sections except Design System)
Update trigger: System architecture changes, new integrations, component additions, design system updates
Update scope:
  @systems-architect: All sections except "Design System"
  @ui-ux-designer: "Design System" section only
  @frontend-developer: May append to "Frontend Architecture" (never overwrite)
  @backend-developer: May append to "Backend Architecture" (never overwrite)
Read by: All agents. Always read before making implementation decisions.
-->

# System Architecture

> Last updated: 2026-03-28
> Version: 1.0.0

---

## Overview

MindGuard is a fraud awareness platform that educates users about online scams through interactive quizzes, AI-powered conversations, and a community-driven scammer reporting system. It serves everyday internet users who want to learn how to recognize and avoid fraud, as well as administrators who moderate reported scammer profiles.

The application is a monolithic Flask web application using server-side rendering with Jinja2 templates. It follows a blueprints-based architecture with separate modules for routing, models, services, and utilities. SQLite provides persistence, while external integrations (OpenRouter for AI, Cloudflare Turnstile for bot protection, Flask-Mail for OTP delivery) extend the core functionality. The architectural posture is deliberately simple: a modular monolith that can be deployed as a single process, with clear internal boundaries that allow future extraction if scale demands it.

```
  [Browser]
     |
     v
[Flask App (app.py)]
     |
     +-- [Blueprints / Routes]
     |     +-- main.py (homepage, stats, leaderboard)
     |     +-- auth.py (login, register, password reset)
     |     +-- quiz.py (quiz flow, AI questions)
     |     +-- scammer.py (reporting, profiles)
     |     +-- chatbot.py (AI chat interface)
     |     +-- admin.py (dashboard, moderation)
     |     +-- library.py (knowledge base)
     |     +-- api.py (internal API endpoints)
     |
     +-- [Services Layer]
     |     +-- anti_spam.py (rate limiting, risk scoring)
     |     +-- leaderboard_integrity.py (rankings, verification)
     |     +-- sensitive_access_log.py (audit trail)
     |
     +-- [Models (SQLAlchemy)]
     |     +-- models.py (13 models)
     |
     +-- [Utils]
     |     +-- ai_agent.py (OpenRouter API)
     |     +-- chatbot.py (message handling)
     |     +-- encryption.py (data encryption)
     |     +-- helpers.py (risk scoring, badges)
     |     +-- privacy_policy.py (data masking)
     |     +-- quiz_data.py (question bank)
     |
     +-- [External Services]
           +-- OpenRouter API (AI chatbot + quiz generation)
           +-- Cloudflare Turnstile (CAPTCHA)
           +-- Flask-Mail (OTP emails)
           +-- ngrok (public tunneling for demos)
```

---

## Tech Stack

| Layer | Technology | Version | Why Chosen |
|-------|-----------|---------|------------|
| Frontend | Jinja2 + Bootstrap 5 | Flask 3.0.3 built-in | Server-side rendering, simple deployment, no build step |
| Styling | Bootstrap 5 + Custom CSS | 5.x | Rapid UI development, responsive out of the box |
| Backend | Python + Flask | 3.12.10 / 3.0.3 | Lightweight, easy to learn, large ecosystem |
| Database | SQLite | 3 | Zero-config, file-based, sufficient for initial scale |
| ORM | Flask-SQLAlchemy | 3.1.1 | Pythonic ORM, tight Flask integration |
| Auth | Flask sessions + Werkzeug | 3.0.3 | Built-in password hashing, session management |
| AI | OpenRouter API | Latest | Access to free LLM models (Mistral, Qwen, Llama) |
| Anti-Bot | Cloudflare Turnstile | Latest | Free, privacy-respecting CAPTCHA alternative |
| Email | Flask-Mail | 0.9.1 | OTP delivery, notifications |
| Hosting | localhost + ngrok | Latest | Development: local; tunneled for demo access |

---

## System Components

### Frontend Architecture

The frontend uses server-side rendered Jinja2 templates with Bootstrap 5 for styling. All HTML is generated on the server; there is no frontend build step, no SPA framework, and no client-side routing.

**Routing**: Flask blueprints define all routes server-side. Each blueprint corresponds to a feature area (auth, quiz, chatbot, etc.). URLs map directly to blueprint handler functions.

**Template hierarchy**: All page templates inherit from `templates/base.html`, which provides the common HTML shell, navigation, and footer. Feature-specific templates live alongside their blueprint (e.g., `templates/quiz/`, `templates/chatbot/`).

**Client-side JavaScript**: Used sparingly for interactive features that require dynamic behavior without a full page reload:
- Quiz flow (timed questions, answer submission)
- Chatbot interface (message sending/receiving)
- Leaderboard animations
- Form validation and CAPTCHA integration

**Styling**: Bootstrap 5 utility classes supplemented by custom CSS. Light-mode semantic tokens are used. No CSS preprocessor or build pipeline.

---

### Backend Architecture

The backend is a Flask application organized around blueprints, with a services layer for business logic and a utils layer for cross-cutting concerns.

**API style**: Primarily server-rendered HTML responses. The `api.py` blueprint provides a small set of internal JSON endpoints consumed by client-side JavaScript (e.g., chatbot messages, quiz answer submission).

**Blueprint organization** (route layer):
```
routes/
  main.py        # Homepage, statistics, leaderboard
  auth.py        # Login, register, password reset, OTP verification
  quiz.py        # Quiz flow, AI-generated questions
  scammer.py     # Scammer reporting, profile viewing
  chatbot.py     # AI chatbot interface
  admin.py       # Admin dashboard, moderation tools
  library.py     # Knowledge base articles
  api.py         # Internal JSON API endpoints
```

**Middleware / request pipeline**:
1. Flask session management -- authenticates user via session cookie
2. Role-based authorization -- route decorators check `user.role` for admin-only endpoints
3. Cloudflare Turnstile verification -- validated server-side on form submissions
4. Anti-spam checks -- rate limiting by account, cookie, and IP with configurable weights

**Services layer** (`services/`): Encapsulates business logic that spans multiple routes or requires complex orchestration:
- `anti_spam.py` -- multi-signal rate limiting and risk scoring
- `leaderboard_integrity.py` -- ranking calculations and verification
- `sensitive_access_log.py` -- audit trail for admin operations

**Utils layer** (`utils/`): Cross-cutting utilities shared across blueprints:
- `ai_agent.py` -- OpenRouter API client for AI interactions
- `chatbot.py` -- message formatting and conversation management
- `encryption.py` -- data encryption/decryption helpers
- `helpers.py` -- risk scoring algorithms, badge calculation
- `privacy_policy.py` -- PII masking (phone, email, CCCD)
- `quiz_data.py` -- static question bank and quiz configuration

**Configuration**: `config.py` holds application settings. Extensions (SQLAlchemy, Mail) are initialized in `extensions.py` and registered with the app in `app.py`.

---

### Infrastructure

**Environments**:
| Environment | URL | Branch | Notes |
|-------------|-----|--------|-------|
| Production | TBD | `main` | Deployment target not yet decided |
| Local | `localhost:5000` | any | `python app.py` |
| Public Demo | ngrok tunnel URL | any | Generated dynamically on startup |

**CI/CD**: Not yet configured. Manual deployment via `python app.py`. GitHub Actions pipeline is planned (see Known Constraints below).

---

## Data Flow

> To be documented as implementation stabilizes. The following flows should be captured:

### User Authentication Flow

```
[To be filled: login/register -> OTP verification -> session creation -> role-based access]
```

### Quiz Flow

```
[To be filled: quiz start -> AI question generation via OpenRouter -> answer submission -> scoring -> leaderboard update]
```

### Scammer Report Flow

```
[To be filled: report submission -> Turnstile verification -> anti-spam check -> reporter anonymization -> admin moderation queue]
```

### AI Chatbot Flow

```
[To be filled: user message -> message formatting -> OpenRouter API call -> response rendering -> conversation history]
```

---

## Design System

<!--
This section is owned by @ui-ux-designer.
Other agents: read-only. Do not modify.
-->

### Color Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `color-primary-500` | [#XXXXXX] | Primary actions, links |
| `color-primary-600` | [#XXXXXX] | Primary hover states |
| `color-neutral-100` | [#XXXXXX] | Background surfaces |
| `color-neutral-900` | [#XXXXXX] | Body text |
| `color-error-500` | [#XXXXXX] | Error states |
| `color-success-500` | [#XXXXXX] | Success states |

### Typography Scale

| Token | Size | Weight | Usage |
|-------|------|--------|-------|
| `text-heading-1` | [32px] | [700] | Page headings |
| `text-heading-2` | [24px] | [600] | Section headings |
| `text-body` | [16px] | [400] | Body copy |
| `text-small` | [14px] | [400] | Labels, captions |

### Spacing System

[e.g., 4px base unit — all spacing is multiples of 4: 4, 8, 12, 16, 24, 32, 48, 64]

### Component Inventory

| Component | Location | Status | Notes |
|-----------|----------|--------|-------|
| Button | `src/components/ui/Button` | [Stable] | Primary, secondary, ghost variants |
| Input | `src/components/ui/Input` | [Stable] | |
| Modal | `src/components/ui/Modal` | [Stable] | |
| [Component] | | [Draft/Stable/Deprecated] | |

### Interaction Patterns

- **Loading states**: [e.g., skeleton screens for content, spinner for actions]
- **Error states**: [e.g., inline error messages below form fields, toast for async errors]
- **Empty states**: [e.g., illustrated empty state with CTA for first-use scenarios]
- **Confirmation dialogs**: [e.g., required for destructive actions, not for saves]

---

## Security Architecture

**Authentication model**: Flask server-side sessions with Werkzeug password hashing. Users authenticate via username/password; sessions are stored server-side and tracked via a session cookie. OTP verification via Flask-Mail for password reset flows.

**Authorization**: Role-based access control with two roles: `user` and `admin`. Route decorators check the current user's role before granting access to admin-only endpoints (dashboard, moderation, sensitive data viewing).

**Data protection**:
- Passwords hashed using Werkzeug's `generate_password_hash` (PBKDF2-SHA256 by default)
- Sensitive PII (phone numbers, email addresses, CCCD/national ID) masked in public-facing views via `privacy_policy.py`
- Encryption utilities in `encryption.py` for data-at-rest protection of sensitive fields
- Reporter anonymization: scammer report submissions use hashed identifiers to protect reporter identity

**Anti-spam and bot protection**:
- Multi-signal rate limiting (`anti_spam.py`): scores requests based on account activity, cookie fingerprint, and IP address with configurable weights and cooldown periods
- Cloudflare Turnstile CAPTCHA integrated on public-facing forms (registration, reporting, contact)

**Audit trail**: `sensitive_access_log.py` records admin operations on sensitive data (viewing masked PII, moderation actions) for accountability.

**Key security decisions**: See `docs/technical/DECISIONS.md` for rationale behind auth and data protection choices.

---

## Performance Considerations

- **Database**: SQLite runs in-process with zero network overhead. Single-writer limitation is acceptable at current scale but will become the first bottleneck under concurrent write load.
- **AI calls**: OpenRouter API calls (quiz generation, chatbot responses) run inline in the request cycle. P95 latency for these endpoints is dominated by external API response time (typically 2-5 seconds). No caching layer exists for AI responses yet.
- **Server-side rendering**: All pages are rendered server-side via Jinja2. No client-side hydration cost. Page load times are fast for static content but depend on database query performance for dynamic pages (leaderboard, scammer profiles).
- **Static assets**: CSS, JavaScript, and images served directly by Flask's static file handler. No CDN configured. For production, a reverse proxy (nginx) or CDN should serve static assets.
- **Anti-spam scoring**: Risk scoring runs on every form submission but is lightweight (in-memory lookups against recent activity). No measurable impact on request latency.

---

## Known Constraints and Technical Debt

| Item | Impact | Plan |
|------|--------|------|
| SQLite single-writer limitation | Cannot handle high concurrent writes; risks `database is locked` errors under load | Migrate to PostgreSQL when scale requires (deliberate/strategic debt) |
| No background job queue | AI quiz generation and chatbot calls run inline, blocking the request thread for 2-5s | Consider Celery or RQ for v2 to offload AI calls |
| Hardcoded admin credentials in config | Security risk if config file is exposed in production | Move to environment variables before any production deployment |
| No CI/CD pipeline | Manual deployment, no automated testing on PRs | Set up GitHub Actions for lint, test, and deploy |
| No linter or formatter configured | Inconsistent code style across contributors | Add Ruff or Black; enforce in CI |
| No CDN or reverse proxy | Static assets served by Flask directly, inefficient under load | Add nginx or Cloudflare CDN for production |
| Flask development server used in production | Not suitable for production traffic (single-threaded, no graceful shutdown) | Deploy behind Gunicorn or uWSGI for production |
