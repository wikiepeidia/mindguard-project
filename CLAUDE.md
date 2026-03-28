# MindGuard — Claude Instructions

> Stack: Python 3.12.10 · Flask 3.0.3 · SQLite (SQLAlchemy) · Jinja2 + Bootstrap · localhost/ngrok
> Last updated: 2026-03-28

## Project Context

MindGuard is a community-driven fraud awareness platform for Vietnamese users. It provides interactive quizzes to educate about scam types, a scammer reporting system with community verification and leaderboard, and an AI chatbot for fraud prevention guidance. Inspired by Checkscam.vn.

**Tech stack summary**: Jinja2 + Bootstrap (Frontend) · Python/Flask (Backend) · SQLite via SQLAlchemy (Database) · localhost + ngrok (Hosting)

---

## Agents Available

**Mandatory delegation — this is not optional.** Every task that falls within a specialist's domain MUST be routed to that agent. Do not implement code, design schemas, write docs, or configure pipelines yourself — delegate. Only handle directly: project-level questions, routing decisions, and tasks explicitly outside all specialist domains.

| Agent | Role | Invoke when... |
|-------|------|----------------|
| `project-manager` | Backlog & coordination | "What's next?", sprint planning, breaking down features, reprioritizing |
| `systems-architect` | Architecture & ADRs | New feature design, tech decisions, system integration |
| `frontend-developer` | UI implementation | Components, pages, client-side state, styling |
| `backend-developer` | API & business logic | Endpoints, auth, background jobs, integrations |
| `ui-ux-designer` | UX & design system | User flows, wireframes, component specs, accessibility |
| `database-expert` | Schema & queries | Migrations, schema design, query optimization |
| `qa-engineer` | Testing (Playwright) | E2E tests, test strategy, coverage gaps |
| `documentation-writer` | Living docs | User guide updates, post-feature documentation |
| `cicd-engineer` | CI/CD & GitHub Actions | Pipelines, deployments, branch protection, release automation |
| `docker-expert` | Containerization | Dockerfiles, docker-compose, image optimization, container networking |
| `copywriter-seo` | Copy & SEO | Landing page copy, marketing content, meta tags, keyword strategy, structured data specs, brand voice |

---

## Critical Rules

These apply to all agents at all times. No exceptions without explicit human instruction.

1. **PRD.md is read-only.** Never modify it. Read it to understand requirements.
2. **TODO.md is the living backlog.** Agents may add items, mark items complete, and move items to "Completed". Preserve section order and existing item priority — do not reorder items within a section unless explicitly asked to reprioritize.
3. **All commits use Conventional Commits format** (see Git Conventions below).
4. **Update the relevant `docs/` file** after every significant change before marking a task complete.
5. **Run tests before marking any implementation task complete.**
6. **Never hardcode secrets, credentials, or environment-specific values** in source code.
7. **Consult `docs/technical/DECISIONS.md`** before proposing changes that may conflict with prior architectural decisions.
8. **Always delegate to the right specialist.** If a task touches frontend, backend, database, UX/design, QA, documentation, CI/CD, Docker, or copy/SEO — invoke the appropriate agent immediately. Do not implement it yourself. The delegation table above is binding, not advisory.

---

## Project Structure

```
routes/                 # Flask route blueprints (main, auth, quiz, scammer, chatbot, admin, library, api)
models/                 # SQLAlchemy models (models.py)
services/               # Business logic (anti_spam, leaderboard_integrity, sensitive_access_log)
utils/                  # Helpers (chatbot, ai_agent, encryption, quiz_data, helpers, privacy_policy)
templates/              # Jinja2 HTML templates
static/                 # CSS, JS, uploads
database/               # SQLite DB, migration scripts, seed scripts
tests/                  # Test suite
  test_quiz.py          # Quiz flow tests
  test_chatbot.py       # Chatbot tests
  test_antispam/        # Anti-spam test suite
  test_leaderboard/     # Leaderboard test suite
  ui/                   # UI contract tests
documents/              # Project documentation (SOP, changelog, guides)
packages/               # Custom installer for easy deployment
.env/                   # API keys config (JSON files)
docs/
  user/USER_GUIDE.md    # User-facing documentation
  technical/            # Architecture, API, DB, decisions
  content/              # Content strategy (owned by @copywriter-seo)
.claude/agents/         # Specialist agent definitions
.claude/templates/      # Blank doc templates (synced from upstream — do not edit)
.tasks/                 # Detailed task files — one per TODO item (owned by @project-manager)
```

---

## Git Conventions

### Commit Format
```
<type>(<scope>): <short description>

[optional body]
[optional footer: Closes #issue]
```

**Types**: `feat` · `fix` · `docs` · `style` · `refactor` · `test` · `chore` · `perf` · `ci`

Examples:
```
feat(auth): add OAuth2 login with Google
fix(api): handle null response from payment provider
docs(user-guide): update onboarding section after flow change
```

### Branch Naming
```
feature/<ticket-id>-short-description
fix/<ticket-id>-short-description
chore/<description>
docs/<description>
refactor/<description>
```

### PR Requirements
- PR title follows Conventional Commits format
- Fill out `.github/PULL_REQUEST_TEMPLATE.md` completely — do not delete sections
- Link to the related issue/ticket (`Closes #XXX`)
- At least one reviewer required before merge
- All CI checks must pass

---

## Code Style

- **Language**: Python 3.12.10
- **Formatter**: None (no formatter configured)
- **Linter**: None (no linter configured)
- **Import style**: Standard Python imports
- **No `print()` in production code** — use Flask's `app.logger`
- **No commented-out code committed** — delete it or track it in TODO.md

---

## Testing Conventions

- **Unit tests**: Basic tests in `tests/` directory, may use pytest or unittest
- **E2E tests**: Not yet configured
- **Run unit**: `python -m pytest`
- **Run E2E**: [TBD]
- **Coverage target**: [TBD]

---

## Environment & Commands

- **Python**: 3.12.10 (see requirements.txt)
- **Package manager**: pip (with custom Installer.py in `/packages` for easy deployment)
- `python app.py` — start dev server (runs on localhost:5000)
- `pip install -r requirements.txt` — install dependencies
- `python -m pytest` — run unit tests
- No build step (Flask serves directly)
- No lint command configured
- No typecheck command

---

## Key Documentation

@docs/technical/ARCHITECTURE.md
@docs/technical/DECISIONS.md
@docs/technical/API.md
@docs/technical/DATABASE.md
@docs/user/USER_GUIDE.md
