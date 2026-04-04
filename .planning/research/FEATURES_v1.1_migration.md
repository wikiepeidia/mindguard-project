# Feature Landscape: PostgreSQL Migration & Vercel Deployment

**Domain:** SQLite→PostgreSQL migration + Vercel serverless deployment for Flask/SQLAlchemy app
**Researched:** 2026-04-03
**Confidence:** HIGH (based on codebase analysis + known Flask/PostgreSQL/Vercel patterns)

---

## Table Stakes

Features that are **required** for a working migration. Missing any = broken production.

| # | Feature | Why Expected | Complexity | Notes |
|---|---------|--------------|------------|-------|
| T1 | **Fix `.env/prosgressql_neondb.json` to valid JSON** | Current file is raw text with comments — not parseable. Config loader (`load_local_env`) expects JSON. | Low | Must have `{"DATABASE_URL": "postgresql://..."}` format. Also fix typo in filename (prosgressql→postgresql). |
| T2 | **Add `psycopg2-binary` to requirements.txt** | SQLAlchemy needs a PostgreSQL driver. Currently only Flask/SQLAlchemy/Werkzeug present — no PG driver. | Low | Use `psycopg2-binary` (not `psycopg2`) to avoid C compiler requirement on Vercel build. |
| T3 | **Switch `SQLALCHEMY_DATABASE_URI` to PostgreSQL** | Config currently hardcoded to `sqlite:///`. Must read NeonDB connection string from env/JSON. | Low | Pattern: `os.environ.get("DATABASE_URL") or load_local_env('postgresql_neondb.json').get("DATABASE_URL")`. Remove SQLite `/tmp` fallback. |
| T4 | **Run `db.create_all()` once, not every cold start** | Current `app.py` calls `db.create_all()` at import time. With PostgreSQL, tables persist — no need to recreate. This adds ~200-500ms to every cold start. | Medium | Move to a one-time migration script in `database/`. Keep a lightweight check (e.g., flag env var `TABLES_CREATED=1`) or just let `create_all()` no-op on existing tables (SQLAlchemy checks before CREATE). |
| T5 | **Remove ephemeral seed-on-cold-start** | `app.py` line 38-40: seeds on every Vercel cold start because SQLite `/tmp` is wiped. With persistent PostgreSQL, this would duplicate data on every function invocation. | High (critical) | Must remove the `if Config.IS_VERCEL: run_seed()` block. Seed once via manual script. |
| T6 | **One-time seed script for PostgreSQL** | Data must be seeded exactly once into NeonDB. Current `seed_all.py` uses `filter_by().first()` guards (idempotent) — this is good but still shouldn't run on every request. | Medium | Run `seed_all.py` locally against NeonDB connection string once. The existing idempotency guards (`if existing: skip`) make it safe to re-run. |
| T7 | **SSL connection to NeonDB** | NeonDB requires `sslmode=require`. SQLAlchemy/psycopg2 needs SSL config. | Low | Pass `?sslmode=require` in the connection URL (already present in the NeonDB string). May also need `connect_args={"sslmode": "require"}` in engine config if URL parsing strips it. |
| T8 | **Vercel `vercel.json` WSGI routing** | Current config routes `/(.*) → /app.py` via `@vercel/python`. This works because `@vercel/python` auto-detects Flask WSGI `app` object. Must verify the `app` variable is importable at module level. | Low | Already works — `app = Flask(__name__)` is at module level in `app.py`. No changes needed unless import errors occur. |
| T9 | **Environment variables on Vercel** | Database URL, API keys, and secrets must be set as Vercel env vars (not rely on `.env/` JSON files which are in `.gitignore`). | Low | Set `DATABASE_URL`, `OPENROUTER_API_KEY`, `CLOUDFLARE_SITE_KEY`, `CLOUDFLARE_SECRET_KEY`, `SECRET_KEY` in Vercel project settings. Config.py already reads `os.environ.get()` first — this pattern is correct. |
| T10 | **Boolean column compatibility** | SQLite stores booleans as 0/1 integers. PostgreSQL has native `BOOLEAN`. SQLAlchemy handles this transparently, but existing data must be migrated correctly. | Low | SQLAlchemy `db.Boolean` maps to native PG `BOOLEAN`. No model changes needed. Data migration script should cast 0→false, 1→true if doing raw SQL export/import. |

---

## Differentiators

Features that **improve quality** of the migration/deployment but aren't strictly required for it to work.

| # | Feature | Value Proposition | Complexity | Notes |
|---|---------|-------------------|------------|-------|
| D1 | **NeonDB connection pooling (pooler URL)** | NeonDB offers a PgBouncer-based connection pooler at port 5432 (pooled) vs 5433 (direct). Vercel serverless creates new connections per invocation — pooler prevents "too many connections" errors under load. | Low | Use the `-pooler` suffix URL from NeonDB dashboard. The neon-workflow.yml already references `db_url_with_pooler`. |
| D2 | **SQLAlchemy connection pool tuning** | Vercel functions are short-lived. Default SQLAlchemy pool (5 connections, 10 overflow) is wasteful for serverless. | Low | Set `SQLALCHEMY_ENGINE_OPTIONS = {"pool_size": 1, "max_overflow": 2, "pool_pre_ping": True, "pool_recycle": 300}`. `pool_pre_ping=True` is critical — it validates connections before use (NeonDB suspends idle compute after 5 min). |
| D3 | **NeonDB serverless auto-suspend awareness** | NeonDB free tier suspends compute after 5 minutes of inactivity. First query after suspend adds ~0.5-2s latency ("cold start"). | Low | Use `pool_pre_ping=True` (handles stale connections). Inform users about first-request latency. No code change needed beyond pool config. |
| D4 | **Proper data migration script (SQLite → PostgreSQL)** | Export existing SQLite data and import into PostgreSQL preserving relationships, timestamps, and encoding. | Medium | Write `database/migrate_sqlite_to_pg.py` that: (1) connects to SQLite, (2) reads all rows per table, (3) inserts into PostgreSQL via SQLAlchemy. The existing seed script serves as a template for fresh data, but real migration preserves user-generated data. |
| D5 | **Vercel function timeout configuration** | Vercel Hobby plan: 10s max execution. Flask routes that call OpenRouter AI can take 5-15s. | Medium | Set `"functions": {"app.py": {"maxDuration": 30}}` in `vercel.json` (requires Pro plan for >10s). On Hobby: add client-side timeout handling and streaming responses for chatbot. |
| D6 | **Static file serving via Vercel CDN** | Current `vercel.json` routes `/static/(.*)` → `/static/$1`. Vercel serves these from the build output, not through Flask. This is correct and faster than Flask serving static files. | Low | Already configured. Add `Cache-Control` headers via `vercel.json` headers config for CSS/JS/images to leverage CDN caching. |
| D7 | **Health check endpoint** | A `/health` or `/api/health` endpoint that tests DB connectivity. Useful for monitoring and debugging Vercel deployment issues. | Low | Simple route that does `db.session.execute(text("SELECT 1"))` and returns 200/500. Helps distinguish "app broken" vs "DB broken" when debugging 500 errors. |
| D8 | **NeonDB branching for PR previews** | The `neon-workflow.yml` already creates NeonDB branches per pull request. Wire it into Vercel preview deployments so each PR gets its own database branch. | Medium | Set `DATABASE_URL` in Vercel preview env from GitHub Action output. Requires Vercel GitHub integration + environment variable API. |
| D9 | **Schema diff on PRs** | NeonDB's `schema-diff-action` (already referenced but commented out in workflow) posts schema changes as PR comments. | Low | Uncomment the schema-diff-action block in `neon-workflow.yml`. Add `permissions: contents: read, pull-requests: write` to the job. |
| D10 | **Graceful cold start initialization** | Current `app.py` does heavy work at import time (db.create_all, legacy data fix, seed). Refactor to lazy initialization to reduce cold start time on Vercel. | Medium | Move `db.create_all()` behind a "first request" hook or remove entirely (tables exist in PostgreSQL). Remove the legacy data fix block or make it a one-time migration script. |

---

## Anti-Features

Features to explicitly **NOT** build during this migration.

| # | Anti-Feature | Why Avoid | What to Do Instead |
|---|--------------|-----------|-------------------|
| A1 | **Alembic/Flask-Migrate** | Project convention explicitly prohibits automated migration tools (see copilot-instructions.md: "Do NOT use flask db upgrade/migrate"). Manual scripts in `database/` are the convention. | Continue using manual migration scripts. `db.create_all()` for initial schema, manual `ALTER TABLE` scripts for future changes. |
| A2 | **Dual database support (SQLite for dev, PG for prod)** | PROJECT.md explicitly states "NeonDB dung cho ca local dev va production — khong phan tach env". Maintaining two DB dialects causes subtle bugs. | Use NeonDB for everything. Local dev connects to the same NeonDB instance (or a dev branch). |
| A3 | **ORM-level PostgreSQL-specific features (JSONB, Array, etc.)** | Current models use only portable types (String, Integer, Text, Boolean, DateTime). Introducing PG-specific types during migration adds unnecessary risk. | Keep models using standard SQLAlchemy types. Add PG-specific features (full-text search, JSONB) in a future milestone when needed. |
| A4 | **Async driver (asyncpg)** | Flask is synchronous WSGI. Async PG driver would require switching to ASGI (Quart/FastAPI) — a complete rewrite. | Use `psycopg2-binary` (sync). If async is needed later, that's a separate milestone. |
| A5 | **Database seeding in application startup** | Root cause of current Vercel issues. Never seed in `app.py` or on cold start. | Seed via explicit manual script run once. Add a `SEED_COMPLETE` check if paranoia needed. |
| A6 | **Multi-region NeonDB deployment** | PROJECT.md: "v1.1 chi can 1 region on dinh". Multi-region adds complexity and cost. | Use single region (ap-southeast-1 — already configured). Add multi-region in a future scale milestone. |
| A7 | **Custom WSGI server on Vercel** | Vercel `@vercel/python` handles WSGI automatically. Adding gunicorn/uwsgi config for Vercel is unnecessary and may conflict. | Let `@vercel/python` manage WSGI. Gunicorn is only needed for non-Vercel deployments (VPS, Docker). |
| A8 | **File upload migration to cloud storage** | Evidence uploads (`evidence_urls` in ScammerReport) are stored as text URLs. File system storage doesn't work on Vercel (read-only). But this is a separate feature, not part of DB migration. | If uploads are currently local files, move to Vercel Blob or S3 in a separate phase. For now, ensure `evidence_urls` stores external URLs only. |

---

## Feature Dependencies

```
T2 (psycopg2-binary) ──→ T3 (switch DATABASE_URI) ──→ T7 (SSL config)
                                    │
                                    ▼
T1 (fix JSON config) ──────→ T3 (switch DATABASE_URI)
                                    │
                                    ▼
                        T4 (create_all strategy) ──→ T5 (remove ephemeral seed)
                                    │                        │
                                    ▼                        ▼
                        T6 (one-time seed script)    T10 (boolean compat)
                                    │
                                    ▼
                        D4 (data migration script) ──→ D1 (connection pooling)
                                                             │
                                                             ▼
                                                      D2 (pool tuning)
                                                             │
                                                             ▼
T9 (Vercel env vars) ──→ T8 (verify WSGI routing) ──→ D7 (health check)
                                                             │
                                                             ▼
                                                      D10 (cold start optimization)
```

**Critical path:** T1 → T2 → T3 → T7 → T5 → T6 → T9 → T8 (minimum viable deployment)

---

## MVP Recommendation

**Phase 1 — Database Migration (do first, verify locally):**

1. T1: Fix NeonDB JSON config file
2. T2: Add `psycopg2-binary` to requirements
3. T3: Switch `SQLALCHEMY_DATABASE_URI` to PostgreSQL
4. T7: Verify SSL connection
5. D2: Add connection pool tuning for serverless
6. T4: Make `db.create_all()` safe (keep but won't hurt — SQLAlchemy no-ops on existing tables)
7. T6: Run seed script once against NeonDB
8. D4: Migrate existing SQLite data if any real user data exists

**Phase 2 — Vercel Deployment Fix (do after DB is stable):**

1. T5: Remove ephemeral seed-on-cold-start from `app.py`
2. T10: Verify boolean/datetime column compatibility
3. T9: Set all env vars on Vercel dashboard
4. T8: Verify WSGI routing (likely already works)
5. D6: Verify static file serving
6. D7: Add health check endpoint
7. D10: Optimize cold start (remove legacy data fix block)

**Defer to future milestone:**

- D5: Function timeout (requires Pro plan)
- D8: NeonDB branching for PR previews (nice-to-have)
- D9: Schema diff (nice-to-have)
- A8: File upload cloud storage (separate concern)

---

## Codebase-Specific Observations

### Current SQLite-Specific Patterns Found

| Pattern | Location | Migration Impact |
|---------|----------|-----------------|
| `/tmp/mindguard_v2.db` fallback | `config.py` line 31-34 | Remove entire `IS_VERCEL` SQLite block |
| `db.create_all()` at module level | `app.py` line 33-34 | Keep (harmless with PG) but flag for cold start optimization |
| Seed on cold start | `app.py` line 37-40 | **Must remove** — will corrupt PG data |
| Legacy data fix at startup | `app.py` line 42-52 | Move to one-time migration script |
| `datetime.utcnow` as default | All models | Compatible with PostgreSQL — no change needed |
| `db.String(N)` column types | All models | Maps to `VARCHAR(N)` in PG — compatible |
| `db.Text` columns | All models | Maps to `TEXT` in PG — compatible |
| No raw SQL queries found | Throughout | Good — SQLAlchemy handles dialect differences |

### NeonDB Config File Issue

The file `.env/prosgressql_neondb.json` is currently:

```
postgresql: //neondb_owner:npg_NlUTW9nsARq4@ep-...neon.tech/neondb?sslmode=require
ep-lingering-violet-a1jiok7c
// napi_ubicdknkb... api neon
// please fix this file because IDK what is the api key for database
```

This is **not valid JSON**. Must become:

```json
{
  "DATABASE_URL": "postgresql://neondb_owner:<password>@ep-lingering-violet-a1jiok7c-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
}
```

Note: Use the `-pooler` endpoint for serverless (D1).

### Requirements Gap

Current `requirements.txt` is missing:

- `psycopg2-binary` — PostgreSQL driver (required)

No other dependency changes needed. Flask-SQLAlchemy handles PostgreSQL via the driver.

---

## Sources

- Codebase analysis: `models/models.py`, `config.py`, `app.py`, `vercel.json`, `extensions.py`, `database/seed_all.py`, `.env/prosgressql_neondb.json`, `.github/workflows/neon-workflow.yml`
- PROJECT.md constraints and decisions
- copilot-instructions.md conventions (no Alembic, manual scripts, NeonDB for all envs)
- NeonDB documentation patterns (connection pooling, auto-suspend, SSL) — HIGH confidence
- Vercel Python runtime behavior (`@vercel/python` WSGI auto-detection) — HIGH confidence
- SQLAlchemy dialect portability (SQLite→PostgreSQL type mapping) — HIGH confidence
