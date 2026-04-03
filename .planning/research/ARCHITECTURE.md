# Architecture Patterns

**Domain:** SQLite → NeonDB PostgreSQL migration + Vercel deployment fix for Flask app
**Researched:** 2026-04-03
**Confidence:** HIGH (verified via Neon official docs, SQLAlchemy docs, codebase analysis)

---

## Current Architecture (Broken)

```
Browser → Vercel Edge → @vercel/python (app.py)
                              │
                              ├─ db.create_all()         ← creates tables in /tmp
                              ├─ run_seed()               ← seeds on EVERY cold start
                              ├─ SQLite at /tmp/mindguard_v2.db  ← ephemeral, lost on cold restart
                              └─ 500 errors               ← likely: /tmp race, slow cold start, seed failures
```

**Root cause of 500 errors (diagnosis):**
1. Vercel's `/tmp` is ephemeral — data lost between function invocations
2. `db.create_all()` + `run_seed()` run on every cold start → slow, may timeout
3. SQLite on `/tmp` is not shared across function instances → each instance has different data
4. Concurrent function instances may race on SQLite file creation

---

## Target Architecture (NeonDB PostgreSQL)

```
Browser → Vercel Edge → @vercel/python (app.py)
                              │
                              ├─ SQLAlchemy (psycopg2-binary)
                              │       │
                              │       └─ TCP + SSL → NeonDB Pooler (PgBouncer)
                              │                          │
                              │                          └─ NeonDB PostgreSQL
                              │                             (ap-southeast-1)
                              │                             Persistent storage
                              │                             Shared across ALL instances
                              └─ No cold-start seed
                                 No /tmp dependency
                                 No IS_VERCEL branching
```

**Key properties:**
- All Vercel function instances connect to the **same** NeonDB PostgreSQL database
- Data persists across cold starts — no re-seeding needed
- Connection pooling via NeonDB's built-in PgBouncer (add `-pooler` to hostname)
- `pool_pre_ping=True` handles Neon's scale-to-zero (compute may suspend after idle)

---

## Component Boundaries

| Component | Current Responsibility | Change Required | Effort |
|-----------|----------------------|-----------------|--------|
| `config.py` | SQLite URI, IS_VERCEL branching, .env JSON loading | **MODIFY** — PostgreSQL URI, remove IS_VERCEL/DB_PATH, fix JSON config | Medium |
| `extensions.py` | Bare `SQLAlchemy()` init | **MODIFY** — No change to file, but engine_options set via config | Minimal |
| `app.py` | `db.create_all()`, cold-start seed, legacy fix | **MODIFY** — Remove IS_VERCEL seed block, keep create_all (safe for Postgres) | Medium |
| `models/models.py` | 13 SQLAlchemy models | **NO CHANGE** — All types are PostgreSQL-compatible | None |
| `models/__init__.py` | Re-export `from .models import *` | **NO CHANGE** | None |
| `vercel.json` | @vercel/python build config | **MODIFY** — Add env var config, possibly adjust build | Low |
| `requirements.txt` | Flask + SQLAlchemy deps | **MODIFY** — Add `psycopg2-binary` | Minimal |
| `.env/prosgressql_neondb.json` | Malformed — raw connection string, not valid JSON | **REWRITE** — Proper JSON structure | Low |
| `database/seed_all.py` | Seeds data (called on cold start for Vercel) | **MODIFY** — Run once via CLI, not on cold start | Low |
| `database/migrate_*.py` | Raw SQL with SQLite syntax (AUTOINCREMENT) | **OBSOLETE** — Not needed; `db.create_all()` creates Postgres schema | None |
| `routes/*.py` | Blueprint handlers | **NO CHANGE** — Use ORM, no raw SQLite SQL | None |
| `services/*.py` | Business logic (anti_spam, leaderboard) | **NO CHANGE** — Use ORM | None |
| `tests/**/*.py` | Unit tests using `sqlite:///:memory:` | **OPTIONAL** — Can keep SQLite for fast unit tests, or switch to Postgres test DB | Low |

---

## Data Flow: Serverless PostgreSQL Connection

### Connection Lifecycle (per Vercel function invocation)

```
1. Cold Start (first request to a new function instance):
   ┌─────────────────────────────────────────────────┐
   │ Vercel spawns Python process                     │
   │ → Flask app initializes                          │
   │ → SQLAlchemy creates engine with pool            │
   │ → First request triggers TCP connection          │
   │   to NeonDB Pooler (PgBouncer)                  │
   │ → PgBouncer routes to Postgres compute           │
   │   (may wake from scale-to-zero: ~200-500ms)     │
   │ → Connection established, query executes         │
   └─────────────────────────────────────────────────┘

2. Warm Request (reuses existing function instance):
   ┌─────────────────────────────────────────────────┐
   │ SQLAlchemy reuses pooled connection              │
   │ → pool_pre_ping checks connection is alive       │
   │ → If stale (Neon suspended), reconnects          │
   │ → Query executes on existing PgBouncer pool      │
   └─────────────────────────────────────────────────┘

3. Function Idle → Vercel Freezes Instance:
   ┌─────────────────────────────────────────────────┐
   │ SQLAlchemy pool connections go idle              │
   │ → NeonDB PgBouncer returns them to pool          │
   │ → After ~5min idle, NeonDB compute suspends      │
   │ → Next request: pool_pre_ping detects stale      │
   │   connection, SQLAlchemy reconnects transparently │
   └─────────────────────────────────────────────────┘
```

### Connection String Format

**Pooled (for Vercel serverless — REQUIRED):**
```
postgresql://{user}:{password}@{endpoint}-pooler.{region}.aws.neon.tech/{database}?sslmode=require
```
Note the `-pooler` suffix on the endpoint hostname. This routes through NeonDB's PgBouncer.

**Direct (for migrations, seed scripts, pg_dump — optional):**
```
postgresql://{user}:{password}@{endpoint}.{region}.aws.neon.tech/{database}?sslmode=require
```

---

## Detailed Modification Plans

### 1. `.env/prosgressql_neondb.json` — REWRITE

**Current (malformed):**
```
postgresql: //neondb_owner:...@ep-lingering-violet-a1jiok7c.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
```

**Target (valid JSON):**
```json
{
  "DATABASE_URL": "postgresql://neondb_owner:<password>@ep-lingering-violet-a1jiok7c-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require",
  "DATABASE_URL_DIRECT": "postgresql://neondb_owner:<password>@ep-lingering-violet-a1jiok7c.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
}
```

Key changes:
- Valid JSON structure
- `-pooler` suffix on endpoint for the primary DATABASE_URL
- Separate `DATABASE_URL_DIRECT` for seed/migration scripts
- Password stored in JSON (local dev), Vercel env vars for production

### 2. `config.py` — MODIFY

**Remove:**
- `IS_VERCEL` flag
- `DB_PATH` / SQLite path logic
- `sqlite:///` URI construction

**Add:**
- Load from `.env/prosgressql_neondb.json`
- `SQLALCHEMY_DATABASE_URI` = PostgreSQL connection string (pooled)
- `SQLALCHEMY_ENGINE_OPTIONS` with:
  - `pool_pre_ping=True` — detect stale connections after Neon scale-to-zero
  - `pool_recycle=300` — recycle connections every 5 min (matches Neon default suspend)
  - `pool_size=5` — small pool for serverless (each function instance)
  - `max_overflow=10` — allow burst connections

**Pattern:**
```python
neon_config = load_local_env('prosgressql_neondb.json')

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or neon_config.get("DATABASE_URL")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 5,
        "max_overflow": 10,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

**Env var priority:** `DATABASE_URL` env var (Vercel) → `.env/prosgressql_neondb.json` (local dev)

### 3. `app.py` — MODIFY

**Remove:**
- `if Config.IS_VERCEL: from database.seed_all import run_seed; run_seed()` block
- The entire cold-start seed pattern

**Keep:**
- `db.create_all()` — safe for PostgreSQL, creates tables if they don't exist (idempotent)
- Legacy data fix block (updates verification_status) — ORM-based, works on Postgres

**Result:** App startup becomes ~instant on Vercel (no seed overhead).

### 4. `requirements.txt` — MODIFY

**Add:**
```
psycopg2-binary==2.9.9
```

This is the PostgreSQL adapter that SQLAlchemy uses under the hood when given a `postgresql://` URI. The `-binary` variant includes pre-compiled C extensions (no build tools needed on Vercel).

### 5. `vercel.json` — MODIFY

**Current config is minimal but functional for @vercel/python.** Main changes:
- Ensure `DATABASE_URL` env var is set in Vercel project settings (not in vercel.json)
- Consider adding `maxMemory` if cold starts are slow:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python",
      "config": { "maxMemory": 512 }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/app.py"
    }
  ]
}
```

**Critical:** Set `DATABASE_URL` in Vercel project settings (Settings → Environment Variables), pointing to the pooled NeonDB connection string. Do NOT put the connection string in `vercel.json`.

### 6. `database/seed_all.py` — MODIFY (usage pattern change)

**No code changes needed** — `run_seed()` uses SQLAlchemy ORM, which is Postgres-compatible. The seed functions already check for existing records before inserting (idempotent).

**Usage change:**
- **Before:** Called automatically on every Vercel cold start
- **After:** Run manually once: `python database/seed_all.py` (from local machine or CI)
- Data persists in NeonDB — no need to re-seed

### 7. Tests — OPTIONAL

Tests currently use `sqlite:///:memory:` for isolation. Two strategies:

| Strategy | Pros | Cons |
|----------|------|------|
| **Keep SQLite for tests** | Fast, no external dependency, works offline | May miss Postgres-specific behavior |
| **Use Neon branch for tests** | Tests against real Postgres dialect | Slower, needs network, needs cleanup |

**Recommendation:** Keep `sqlite:///:memory:` for unit tests (speed), add a separate integration test config that uses Neon branch if needed later.

---

## Model Compatibility Audit

All 13 models in `models/models.py` use standard SQLAlchemy types:

| SQLAlchemy Type | SQLite Mapping | PostgreSQL Mapping | Compatible? |
|----------------|---------------|-------------------|-------------|
| `db.Integer` | INTEGER | INTEGER | Yes |
| `db.String(N)` | VARCHAR(N) | VARCHAR(N) | Yes |
| `db.Text` | TEXT | TEXT | Yes |
| `db.Boolean` | INTEGER (0/1) | BOOLEAN | Yes |
| `db.DateTime` | TEXT/REAL | TIMESTAMP | Yes |
| `db.ForeignKey` | Supported | Supported | Yes |

**No SQLite-specific code in models.** The `AUTOINCREMENT` keyword only appears in raw SQL migration scripts (`database/migrate_*.py`), which are obsolete — `db.create_all()` handles Postgres schema creation with `SERIAL` primary keys automatically.

**One consideration:** `default=datetime.utcnow` works identically on both. No changes needed.

---

## Patterns to Follow

### Pattern 1: Environment-Aware Config with Single DB
**What:** Use PostgreSQL for both local dev and production (same NeonDB instance).
**When:** Always — simplifies config, eliminates SQLite/Postgres incompatibility risk.
**Example:**
```python
# config.py
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or neon_config.get("DATABASE_URL")
```

### Pattern 2: Pooled Connections for Serverless
**What:** Use NeonDB's PgBouncer pooler endpoint for all application connections.
**When:** Always for Vercel serverless functions — prevents connection exhaustion.
**Why:** Each Vercel function instance creates its own connection pool. Without PgBouncer, 10 concurrent instances x 5 pool_size = 50 direct Postgres connections. With PgBouncer, these are multiplexed through a shared pool.

### Pattern 3: pool_pre_ping for Scale-to-Zero Resilience
**What:** SQLAlchemy checks if a connection is alive before using it.
**When:** Required for NeonDB — compute may suspend after idle, killing TCP connections.
**Source:** Neon SQLAlchemy docs — "Set the SQLAlchemy pool_pre_ping parameter to true"

### Pattern 4: Idempotent Seed Scripts
**What:** Seed scripts check for existing records before inserting.
**When:** Running seeds against persistent database — prevents duplicates.
**Status:** Already implemented in `seed_all.py` (checks `Registration.query.filter_by(email=...).first()` etc.)

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Cold-Start Seeding
**What:** Running `run_seed()` on every Vercel cold start
**Why bad:** Slow startup (seed_all.py creates ~50+ records), wastes DB connections, risks timeouts on Vercel (10s default)
**Instead:** Seed once via CLI, remove from app.py startup

### Anti-Pattern 2: IS_VERCEL Environment Branching for DB
**What:** Different database paths for Vercel vs local
**Why bad:** Testing divergence — local uses SQLite, production uses (broken) SQLite on /tmp
**Instead:** Single PostgreSQL connection string for all environments

### Anti-Pattern 3: Direct (Non-Pooled) Connections from Serverless
**What:** Using NeonDB endpoint without `-pooler` suffix
**Why bad:** Each serverless function instance opens direct Postgres connections, quickly exhausting `max_connections` (104 on free tier 0.25 CU)
**Instead:** Always use `-pooler` endpoint for application connections

### Anti-Pattern 4: Storing Connection Strings in vercel.json
**What:** Putting DATABASE_URL in vercel.json (committed to git)
**Why bad:** Credentials exposed in source control
**Instead:** Set via Vercel project settings (Settings → Environment Variables)

---

## New Components Needed

| Component | Purpose | Priority |
|-----------|---------|----------|
| None | No new files needed — all changes are modifications to existing files | — |

**Explanation:** The migration is purely a config/dependency change. SQLAlchemy abstracts the DB engine, so switching from SQLite to PostgreSQL requires only:
1. New dependency (`psycopg2-binary`)
2. New connection string (PostgreSQL URI)
3. Engine options (pool_pre_ping, pool_recycle)
4. Removing SQLite-specific workarounds (IS_VERCEL, /tmp, cold-start seed)

No new abstraction layers, no new files, no new patterns.

---

## Build Order (Dependency-Aware)

```
Phase 1: Config Foundation (no app changes yet)
  1a. Fix .env/prosgressql_neondb.json → valid JSON with pooled + direct URLs
  1b. Add psycopg2-binary to requirements.txt
  1c. Modify config.py → PostgreSQL URI + engine options, remove IS_VERCEL/DB_PATH

Phase 2: App Startup Cleanup (depends on Phase 1)
  2a. Modify app.py → remove IS_VERCEL seed block
  2b. Keep db.create_all() (creates tables on Postgres if not exist)

Phase 3: Seed and Verify Locally (depends on Phase 1+2)
  3a. Run app locally → verify db.create_all() creates tables on NeonDB
  3b. Run seed_all.py once → populate NeonDB with demo data
  3c. Verify all routes work (quiz, scammer, chatbot, admin, auth)

Phase 4: Vercel Deployment Fix (depends on Phase 1+2+3)
  4a. Set DATABASE_URL env var in Vercel project settings
  4b. Update vercel.json if needed (maxMemory, build config)
  4c. Deploy and verify → no more 500 errors
  4d. Verify all routes on production URL

Phase 5: Cleanup (depends on all above)
  5a. Remove database/mindguard_v2.db from git (no longer needed)
  5b. Update .gitignore for *.db files
  5c. Update documentation (README, docs/)
```

**Why this order:**
- Phase 1 must come first: config is the foundation everything depends on
- Phase 2 depends on Phase 1: app.py imports Config
- Phase 3 validates locally before touching Vercel: cheaper to debug
- Phase 4 is the deployment itself: only after local validation passes
- Phase 5 is cleanup: non-blocking, can happen anytime after Phase 4

---

## Scalability Considerations

| Concern | Free Tier (0.25 CU) | If Traffic Grows |
|---------|---------------------|------------------|
| Max Connections | 104 (97 usable) | Upgrade compute CU |
| Pooler Limit | 10,000 client connections via PgBouncer | More than enough |
| Storage | 0.5 GB (free tier) | Upgrade plan |
| Compute Suspend | 5 min idle → cold start ~200-500ms | Disable suspend (paid) |
| Concurrent Vercel Functions | ~10 instances x 5 pool = 50 connections | Within 97 limit |

**Current free tier is sufficient** for MindGuard's expected traffic (educational platform, not high-concurrency).

---

## Sources

- [Neon SQLAlchemy Connection Guide](https://neon.com/docs/guides/sqlalchemy.md) — HIGH confidence
- [Neon Connection Pooling](https://neon.com/docs/connect/connection-pooling.md) — HIGH confidence
- [Neon Connection Methods Decision Tree](https://neon.com/docs/ai/skills/neon-postgres/references/connection-methods.md) — HIGH confidence
- [Neon Scale to Zero](https://neon.com/docs/introduction/scale-to-zero.md) — HIGH confidence
- Codebase analysis: config.py, app.py, extensions.py, models/models.py, vercel.json, seed_all.py — PRIMARY source
