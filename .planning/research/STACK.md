# Technology Stack: NeonDB PostgreSQL Migration & Vercel Deployment

**Project:** MindGuard v1.1
**Researched:** 2026-04-03
**Focus:** Stack additions/changes for NeonDB PostgreSQL + Vercel deployment ONLY

---

## Recommended Stack Additions

### PostgreSQL Driver

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| `psycopg2-binary` | `>=2.9.9` | PostgreSQL adapter for Python/SQLAlchemy | Pre-compiled binary — no `libpq-dev` or C compile toolchain needed. Vercel's build environment does not guarantee native compilation support, so `-binary` is mandatory. Neon's official docs recommend it explicitly. |

**Why NOT `psycopg2` (non-binary)?** Requires `libpq-dev` headers and a C compiler to build from source. Vercel's serverless build environment does not reliably provide these. Will fail at `pip install` during deployment. Use `psycopg2-binary` unconditionally.

**Why NOT `asyncpg`?** Flask is WSGI (synchronous). `asyncpg` is for `asyncio` frameworks (FastAPI, Starlette). Adding it adds complexity with zero benefit.

**Why NOT Neon's serverless driver (`@neondatabase/serverless`)?** That's a JavaScript/TypeScript WebSocket driver for edge runtimes. Not applicable to Python/Flask.

**Confidence:** HIGH — Neon official docs + SQLAlchemy docs + Vercel Python runtime docs all confirm.

### SQLAlchemy (Version Pin)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| `SQLAlchemy` | `>=2.0.33` | ORM engine (already used via Flask-SQLAlchemy) | Versions < 2.0.33 have a bug where idle connections are reused after Neon suspends the compute, causing `SSL connection has been closed unexpectedly` errors. Neon's official SQLAlchemy guide explicitly recommends >= 2.0.33. |

**Current state:** `Flask-SQLAlchemy==3.1.1` pulls in SQLAlchemy >= 2.0 but does NOT guarantee >= 2.0.33. Explicitly pin `SQLAlchemy>=2.0.33` in `requirements.txt`.

**Confidence:** HIGH — Neon docs + SQLAlchemy 2.0.33 changelog confirms the fix.

### No Other New Dependencies Needed

The existing stack handles everything else:
- `Flask-SQLAlchemy==3.1.1` — already provides the ORM layer; the PostgreSQL dialect activates automatically when the connection string uses `postgresql://`
- `Flask==3.0.3` — WSGI compatible with Vercel Python runtime
- `requests==2.31.0` — unchanged (OpenRouter API calls)
- `Flask-Mail==0.9.1` — unchanged
- `Werkzeug==3.0.3` — unchanged

---

## Updated requirements.txt

```txt
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Flask-Mail==0.9.1
Werkzeug==3.0.3
MarkupSafe==2.1.5
requests==2.31.0
psycopg2-binary>=2.9.9
SQLAlchemy>=2.0.33
```

**Only 2 lines added.** No other changes.

---

## NeonDB Connection Configuration

### Connection String Format

```
postgresql://USER:PASSWORD@ENDPOINT-pooler.REGION.aws.neon.tech/DBNAME?sslmode=require
```

For MindGuard (ap-southeast-1 region):
```
postgresql://neondb_owner:<password>@ep-lingering-violet-a1jiok7c-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
```

**Critical: Use the `-pooler` hostname.** Adding `-pooler` to the endpoint ID routes connections through Neon's PgBouncer. Without it, each Vercel cold start opens a direct Postgres connection, and you'll hit `max_connections` (104 on free tier 0.25 CU) fast.

### Pooled vs Direct Connection

| Use Case | Connection Type | When |
|----------|----------------|------|
| App runtime (Flask on Vercel) | **Pooled** (`-pooler` in hostname) | Always for the app — many short-lived connections from serverless |
| Schema migrations (manual scripts) | **Direct** (no `-pooler`) | `db.create_all()` and seed scripts — may use SET/DDL statements incompatible with transaction-mode pooling |

**Confidence:** HIGH — Neon connection pooling docs explicitly recommend pooled for serverless, direct for migrations.

### SSL Configuration

- `sslmode=require` in the connection string is sufficient
- No client certificate files needed
- No additional `connect_args` for SSL in SQLAlchemy
- Neon enforces SSL on all connections by default

### SQLAlchemy Engine Options (Critical for Neon)

These must be set in `config.py` or when initializing Flask-SQLAlchemy:

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,      # Test connection before use — handles Neon auto-suspend
    "pool_recycle": 300,         # Recycle connections every 5 min — prevents stale SSL
    "pool_size": 5,              # Keep pool small for serverless
    "max_overflow": 10,          # Allow burst connections
}
```

| Option | Value | Why |
|--------|-------|-----|
| `pool_pre_ping` | `True` | **Most important.** Neon suspends idle computes (free tier: after 5 min). When Flask reuses a pooled connection after suspend, the TCP socket is dead. `pool_pre_ping` issues a lightweight `SELECT 1` before each query to detect dead connections and replaces them. Without this, users get `SSL SYSCALL error: EOF detected`. |
| `pool_recycle` | `300` | Forces connections to be replaced every 5 minutes. Prevents long-lived connections from going stale when Neon cycles infrastructure. |
| `pool_size` | `5` | Vercel serverless functions are single-request (or Fluid Compute with limited concurrency). A large pool wastes Neon connections (free tier: 104 max). |
| `max_overflow` | `10` | Allows temporary burst past `pool_size` for concurrent requests. |

**Confidence:** HIGH — Neon SQLAlchemy docs explicitly recommend `pool_pre_ping=True` and `pool_recycle`.

---

## Vercel Deployment Configuration

### Current vercel.json Assessment

```json
{
  "version": 2,
  "builds": [{ "src": "app.py", "use": "@vercel/python" }],
  "routes": [
    { "src": "/static/(.*)", "dest": "/static/$1" },
    { "src": "/(.*)", "dest": "/app.py" }
  ]
}
```

**This is the legacy configuration format.** As of March 2026, Vercel's Python runtime auto-detects Flask from `requirements.txt` and doesn't require explicit `builds` or `routes`. The current config still works, but has redundancy.

### Recommended vercel.json

Keep the current format — it works and is explicit. The Flask auto-detection is newer and may not handle the `static/` directory routing as expected (Flask's `app.static_folder` is not recommended on Vercel — use explicit routes or `public/` directory).

### Vercel Python Runtime Facts

| Aspect | Detail |
|--------|--------|
| Python versions | 3.12 (default), 3.13, 3.14 |
| MindGuard target | 3.12 (matches current local dev) |
| Framework detection | Auto-detects Flask from `requirements.txt` |
| Entrypoint | `app.py` with `app = Flask(...)` — **already correct** |
| Deployment model | Single Vercel Function with Fluid Compute |
| Filesystem | **Read-only** — no SQLite, no writing to disk except `/tmp` |
| Max bundle | 500 MB uncompressed |
| Dependencies | Read from `requirements.txt` — **already used** |
| Static files | Should use `public/` dir or explicit routes (current routes config handles this) |

**Confidence:** HIGH — Vercel Python runtime docs (updated March 2026).

### Vercel Environment Variables

The NeonDB connection string must be set as a Vercel Environment Variable:

| Variable | Value | Set Where |
|----------|-------|-----------|
| `DATABASE_URL` | `postgresql://neondb_owner:<pw>@ep-...-pooler...neon.tech/neondb?sslmode=require` | Vercel Dashboard → Project Settings → Environment Variables |
| `SECRET_KEY` | (random secure string) | Vercel Dashboard |
| `OPENROUTER_API_KEY` | (existing key) | Vercel Dashboard |
| `CLOUDFLARE_SITE_KEY` | (existing key) | Vercel Dashboard |
| `CLOUDFLARE_SECRET_KEY` | (existing key) | Vercel Dashboard |

`config.py` should read `DATABASE_URL` from `os.environ` and fall back to the local JSON config:

```python
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or load_neondb_url()
```

**The `.env/prosgressql_neondb.json` file is currently malformed** — it contains raw text, not valid JSON. Must be restructured to:

```json
{
  "DATABASE_URL": "postgresql://neondb_owner:<password>@ep-lingering-violet-a1jiok7c-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
}
```

---

## Integration Points with Existing Code

### config.py Changes Required

| Current | Change To | Why |
|---------|-----------|-----|
| `SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"` | Read from `DATABASE_URL` env var / JSON config | Switch from SQLite to PostgreSQL |
| No `SQLALCHEMY_ENGINE_OPTIONS` | Add `pool_pre_ping`, `pool_recycle`, `pool_size` | Required for Neon auto-suspend resilience |
| `IS_VERCEL` conditional for `/tmp` SQLite path | Remove entirely | No longer needed — NeonDB is remote, same URI for local and Vercel |
| `load_local_env('prosgressql_neondb.json')` | Fix the JSON file to be valid JSON | Current file is not parseable JSON |

### app.py Changes Required

| Current | Change To | Why |
|---------|-----------|-----|
| `db.create_all()` runs on every import | Guard with check or use migration script | `db.create_all()` is safe with PostgreSQL but should use direct (non-pooled) connection for DDL |
| Vercel cold-start seed (`if Config.IS_VERCEL: run_seed()`) | Remove or replace with one-time seed check | PostgreSQL is persistent — seeding on every cold start would duplicate data or fail on unique constraints |

### models/models.py — No Changes Needed

All models use portable SQLAlchemy types:
- `db.Integer`, `db.String(N)`, `db.Text`, `db.Boolean`, `db.DateTime`, `db.ForeignKey`
- No SQLite-specific constructs (no `AUTOINCREMENT`, no `sqlite_` pragmas)
- PostgreSQL dialect handles these identically

**Confidence:** HIGH — Verified by reading all model definitions.

### Seed Data Strategy Change

| Current (SQLite/Vercel) | Required (PostgreSQL) |
|-------------------------|----------------------|
| Seed on every Vercel cold start (ephemeral /tmp DB) | Seed once, data persists in NeonDB |
| `seed_all.py` runs unconditionally | Must add idempotency checks (e.g., `INSERT ... ON CONFLICT DO NOTHING` or check if tables are populated) |

---

## What NOT to Add

| Don't Add | Why |
|-----------|-----|
| `psycopg2` (non-binary) | Won't compile on Vercel |
| `asyncpg` | Flask is synchronous WSGI |
| `@neondatabase/serverless` | JavaScript-only driver |
| `Alembic` / `flask-migrate` | Project convention: manual migration scripts in `database/` |
| `python-dotenv` | Project already has its own JSON-based config loader |
| `gunicorn` / `uvicorn` | Vercel provides its own WSGI server |
| `pg8000` | No advantage over psycopg2-binary; less ecosystem support |
| Client SSL certificates | Neon uses `sslmode=require` without client certs |
| `pgbouncer` (local) | Neon provides server-side PgBouncer — no local pooler needed |

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| PG Driver | `psycopg2-binary` | `psycopg[binary]` (psycopg3) | psycopg3 works but Flask-SQLAlchemy's default dialect is `psycopg2`. Switching to psycopg3 requires `postgresql+psycopg://` URI and is an unnecessary change for this migration. |
| PG Driver | `psycopg2-binary` | `pg8000` (pure Python) | Pure Python = slower. Less community support. No compile benefit over `-binary` which is already pre-compiled. |
| Connection pooling | Neon server-side (PgBouncer) | SQLAlchemy `QueuePool` + Neon direct | Neon PgBouncer already handles pooling at 10K connections. SQLAlchemy's default QueuePool works fine on top, but the `-pooler` endpoint is what actually matters for serverless. |
| Config format | `DATABASE_URL` env var | Keep `.env/*.json` only | Vercel env vars are the standard pattern. JSON fallback kept for local dev only. |

---

## Sources

| Source | Confidence | URL |
|--------|------------|-----|
| Neon: Connect Python app | HIGH | https://neon.tech/docs/guides/python |
| Neon: SQLAlchemy guide | HIGH | https://neon.tech/docs/guides/sqlalchemy |
| Neon: Connection pooling | HIGH | https://neon.tech/docs/connect/connection-pooling |
| Neon: Connect from any app | HIGH | https://neon.tech/docs/connect/connect-from-any-app |
| Vercel: Python runtime | HIGH | https://vercel.com/docs/functions/runtimes/python |
| Vercel: Flask on Vercel | HIGH | https://vercel.com/docs/frameworks/backend/flask |
| SQLAlchemy 2.0.33 changelog | HIGH | https://docs.sqlalchemy.org/en/20/changelog/changelog_20.html#change-2.0.33-postgresql |
| Existing codebase analysis | HIGH | Verified against config.py, models/models.py, requirements.txt, vercel.json, app.py |
