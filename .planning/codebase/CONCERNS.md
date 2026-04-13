# Concerns

> Mapped: 2026-04-13

## Security

### CRITICAL: Hardcoded Credentials
- `config.py:44` — `ADMIN_PASSWORD = "mindguard2025"` hardcoded, no env var
- `config.py:46` — `REPORT_ENCRYPTION_KEY = "mindguard-secret-key-2025"` hardcoded
- `config.py:22` — `SECRET_KEY` has env var but falls back to hardcoded string
- **Risk**: Anyone reading source code gets admin access
- **Fix**: Move all three to Vercel environment variables, remove fallbacks

### Admin Authentication
- Admin uses simple password comparison, not user-based auth
- No session timeout for admin sessions
- No brute-force protection on admin login (rate limiting added but basic)

### CSRF
- CSRF protection initialized in `extensions.py` but enforcement coverage unclear
- Some AJAX endpoints may bypass CSRF checks

## Performance

### Cold Start
- `app.py:69-70` — `db.create_all()` runs on every cold start
- With NeonDB auto-suspend, cold start can take 5-8 seconds
- Vercel Hobby kills functions at 10 seconds — dangerously close
- **Fix**: Remove `db.create_all()` — tables already exist in NeonDB

### AI Timeout
- `utils/chatbot.py:66` — `timeout=10` on OpenRouter calls
- Matches Vercel's 10s limit exactly — no safety margin
- If OpenRouter is slow, function gets killed before fallback runs
- **Fix**: Reduce to 8s

### NeonDB Connection Limits
- Using `NullPool` — each request opens/closes a connection
- NeonDB free tier ~100 connections
- Under concurrent load, connection exhaustion is the first bottleneck
- Expected ceiling: ~30-50 concurrent chatbot users

## Technical Debt

### Bare Except Blocks
- Several `except:` or `except Exception:` blocks that swallow errors silently
- Makes debugging production issues difficult
- Should catch specific exceptions

### Print Statements
- Some `print()` calls remain in production code (`utils/chatbot.py`)
- Should use `app.logger` for structured logging

### Mixed Database State
- `database/mindguard_v2.db` (SQLite) still exists locally
- NeonDB is the primary database
- Config still references SQLite in some paths
- Migration scripts reference both databases

### No Database Migrations
- No Alembic or flask-migrate
- Schema changes done via manual scripts in `database/`
- Risk of schema drift between environments

## Fragile Areas

### `templates/base.html`
- Master template inherited by ALL pages
- Changes here affect every page
- Contains navbar, footer, chatbot widget, JavaScript
- High blast radius for any modification

### `utils/chatbot.py`
- Handles AI safety, system prompt, fallback, message formatting
- Multiple responsibilities in one file
- Changes to safety logic affect all 3 chatbot endpoints

### `routes/admin.py`
- Largest route file (200+ lines changed in latest update)
- Handles dashboard, moderation, export, suspension, sensitive logs
- Admin guard logic split between `admin.py` and `services/admin_guard.py`

## Missing Features (for Beta readiness)

- No stress test infrastructure (locust/k6)
- No prominent feedback/report button in chatbot UI
- `ADMIN_PASSWORD` and `REPORT_ENCRYPTION_KEY` not in env vars
- `db.create_all()` still runs on cold start
- AI timeout too close to Vercel limit (10s vs 10s)

## Test Coverage Gaps

- No tests for chatbot rate limiting behavior
- No tests for sensitive topic blocking (`_is_sensitive()`)
- No tests for admin suspension flow (`admin_guard.py`)
- No E2E tests
- No load/stress tests
