# Project Research Summary

**Project:** MindGuard v1.1 — PostgreSQL Migration & Vercel Deployment Fix
**Domain:** SQLite→NeonDB PostgreSQL migration + Vercel serverless deployment for Flask/SQLAlchemy app
**Researched:** 2026-04-03
**Confidence:** HIGH

---

## Executive Summary

MindGuard's Vercel deployment is broken (500 errors) because it relies on SQLite in Vercel's ephemeral `/tmp` filesystem. Every cold start creates a fresh database, seeds it (causing duplicates or timeouts), and loses all data when the function instance recycles. The fix is straightforward: replace SQLite with NeonDB PostgreSQL (already provisioned in `ap-southeast-1`), strip all ephemeral-storage workarounds from `app.py` and `config.py`, and deploy with proper environment variables. The entire migration requires only **2 new pip packages** (`psycopg2-binary`, explicit `SQLAlchemy>=2.0.33` pin) and changes to **4 source files** (`config.py`, `app.py`, `requirements.txt`, `.env/prosgressql_neondb.json`). No model changes, no route changes, no service changes — SQLAlchemy's ORM abstracts the dialect switch completely.

The primary risks are: (1) the malformed NeonDB config file silently falling back to SQLite without anyone noticing, (2) seed-on-cold-start duplicating data once PostgreSQL is connected, and (3) Vercel cold start timeouts if `db.create_all()` and NeonDB compute wake-up combine to exceed 10 seconds. All three are preventable with the configuration and startup changes detailed below. A secondary concern — file uploads crashing on Vercel's read-only filesystem — exists but is out of scope for this migration and should be a separate phase.

The recommended approach is a **3-phase execution**: (Phase 1) fix configuration and verify local PostgreSQL connectivity, (Phase 2) migrate schema and data to NeonDB, (Phase 3) clean `app.py` startup path, deploy to Vercel, and verify. This order ensures each phase builds on a verified foundation.

---

## Key Findings

### Recommended Stack Additions

Only **2 lines** added to `requirements.txt`. No new frameworks or major dependencies.

| Package | Version | Purpose |
|---------|---------|---------|
| `psycopg2-binary` | `>=2.9.9` | PostgreSQL driver for SQLAlchemy. Must use `-binary` variant — Vercel build lacks `libpq-dev` for source compilation. |
| `SQLAlchemy` | `>=2.0.33` | Explicit pin. Versions < 2.0.33 have a bug where idle connections fail after NeonDB auto-suspend (`SSL connection has been closed unexpectedly`). |

**Updated requirements.txt:**
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

**What NOT to add:**
- `asyncpg` — Flask is WSGI (sync). Zero benefit.
- `@neondatabase/serverless` — JS/TS driver, not Python.
- `psycopg2` (non-binary) — needs C compiler, fails on Vercel.
- `Alembic` / `Flask-Migrate` — project convention prohibits automated migration tools.

**NeonDB connection string format (pooled, for serverless):**
```
postgresql://USER:PASSWORD@ENDPOINT-pooler.REGION.aws.neon.tech/DBNAME?sslmode=require
```
The `-pooler` suffix is **mandatory** for Vercel — routes through PgBouncer to prevent "too many connections" (free tier limit: 104).

**Required SQLAlchemy engine options:**
```python
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,   # Detect stale connections after NeonDB suspend
    "pool_recycle": 300,      # Recycle every 5 min (matches Neon suspend timer)
    "pool_size": 5,           # Small pool for serverless
    "max_overflow": 10,       # Allow burst
}
```

### Feature Table Stakes (Migration-Specific)

From FEATURES_v1.1_migration.md — 10 table-stakes items, all required for a working deploy:

**Must have (broken without these):**
1. **Fix `.env/prosgressql_neondb.json`** — currently raw text, not valid JSON. Config loader silently returns `{}`.
2. **Add `psycopg2-binary`** — no PostgreSQL driver exists in requirements.
3. **Switch `SQLALCHEMY_DATABASE_URI` to PostgreSQL** — env var → JSON fallback pattern.
4. **SSL connection** (`sslmode=require`) — NeonDB enforces SSL on all connections.
5. **Remove seed-on-cold-start** — will duplicate all data on every Vercel function invocation.
6. **Run seed exactly once** against NeonDB via manual script.
7. **Set Vercel environment variables** — `DATABASE_URL`, `SECRET_KEY`, API keys.

**Should have (quality improvement):**
- NeonDB connection pooling via `-pooler` endpoint (D1)
- SQLAlchemy pool tuning for serverless (D2)
- Health check endpoint for debugging (D7)
- Cold start optimization — remove `db.create_all()` / legacy fix from import path (D10)

**Explicitly defer (anti-features for v1.1):**
- Alembic/Flask-Migrate (project convention: manual scripts only)
- Dual DB support (SQLite dev / PG prod) — PROJECT.md says NeonDB for all environments
- PG-specific features (JSONB, Array types) — keep models portable
- Async driver (asyncpg) — would require ASGI rewrite
- File upload cloud storage — separate concern, separate phase
- Multi-region NeonDB — single region for v1.1

### Architecture Changes

**Root cause of current 500 errors:**
```
app.py imports → db.create_all() in /tmp → run_seed() every cold start → SQLite ephemeral → data lost
```

**Target architecture:**
```
app.py imports (fast) → SQLAlchemy → TCP+SSL → NeonDB Pooler (PgBouncer) → PostgreSQL (persistent)
```

**Files that change:**

| File | Change | Effort |
|------|--------|--------|
| `config.py` | Remove `IS_VERCEL`/`DB_PATH`/SQLite logic. Add PostgreSQL URI from env/JSON. Add `SQLALCHEMY_ENGINE_OPTIONS`. | Medium |
| `app.py` | Remove `IS_VERCEL` seed block. Remove legacy data fix from import path. Keep `db.create_all()` (safe, idempotent) or move to script. | Medium |
| `requirements.txt` | Add 2 lines: `psycopg2-binary>=2.9.9`, `SQLAlchemy>=2.0.33`. | Minimal |
| `.env/prosgressql_neondb.json` | Rewrite as valid JSON with `DATABASE_URL` and `DATABASE_URL_DIRECT` keys. | Low |
| `vercel.json` | No change required (current config works). Optional: add function timeout config. | None |

**Files that DON'T change:**
- `models/models.py` — all 13 models use portable SQLAlchemy types
- `routes/*.py` — all use ORM, no raw SQL
- `services/*.py` — all use ORM
- `extensions.py` — unchanged (engine options come from config)
- `templates/` — unchanged
- `static/` — unchanged

### Critical Pitfalls (Top 7)

Ranked by deployment impact:

| # | Pitfall | Impact | Prevention | Phase |
|---|---------|--------|------------|-------|
| 1 | **Malformed NeonDB JSON config** — `json.load()` silently fails, falls back to SQLite | Silent wrong-database connection | Rewrite as valid JSON, add validation | Phase 1 |
| 2 | **No PostgreSQL driver** — `ModuleNotFoundError: psycopg2` | Immediate 500 on any DB operation | Add `psycopg2-binary>=2.9.9` to requirements | Phase 1 |
| 3 | **Seed-on-cold-start duplication** — `run_seed()` every Vercel invocation with persistent DB | Corrupted data, duplicate admin users | Remove `IS_VERCEL` seed block entirely | Phase 2 |
| 4 | **Cold start timeout** — `db.create_all()` + NeonDB wake-up exceeds 10s | 504 Gateway Timeout | Remove startup DB work from import path | Phase 3 |
| 5 | **Connection pool exhaustion** — N Vercel instances × M connections > 104 limit | Intermittent 500s under load | Use `-pooler` endpoint + `pool_size=5` | Phase 1 |
| 6 | **`LIKE` case sensitivity change** — SQLite case-insensitive, PostgreSQL case-sensitive | Broken search results | Audit all `.like()` → `.ilike()` | Phase 2 |
| 7 | **Read-only filesystem for uploads** — `static/uploads/evidence/` write fails | Report submission with evidence crashes | Defer to separate phase (cloud storage) | Future |

---

## Implications for Roadmap

### Phase 1: Configuration & Connection
**Rationale:** Everything else depends on a working PostgreSQL connection. Must be verified locally before touching deployment.
**Delivers:** Local Flask app connected to NeonDB PostgreSQL instead of SQLite.
**Addresses:** T1 (fix JSON), T2 (add driver), T3 (switch URI), T7 (SSL), D1 (pooler URL), D2 (pool tuning).
**Avoids:** Pitfalls 1 (malformed JSON), 2 (no driver), 5 (pool exhaustion), 7 (SSL).
**Work:**
- Rewrite `.env/prosgressql_neondb.json` as valid JSON
- Add `psycopg2-binary>=2.9.9` and pin `SQLAlchemy>=2.0.33` in requirements.txt
- Rewrite `config.py`: remove `IS_VERCEL`/SQLite branching, add PostgreSQL URI + engine options
- Verify local connection to NeonDB (SELECT 1)
- Check credential security (`.env/` in `.gitignore`, rotate if committed)

### Phase 2: Schema & Data Migration
**Rationale:** With connection working, create schema in PostgreSQL and migrate any existing data. Must happen before Vercel deploy to ensure tables exist.
**Delivers:** NeonDB has all 13 tables populated with seed data. Data integrity verified.
**Addresses:** T4 (create_all strategy), T5 (remove seed-on-cold-start), T6 (one-time seed), T10 (boolean compat), D4 (data migration).
**Avoids:** Pitfalls 3 (seed duplication), 6 (LIKE case sensitivity), 12 (boolean conversion), 14 (string length).
**Work:**
- Run `db.create_all()` once against NeonDB (via script, not app startup)
- Run `seed_all.py` once against NeonDB
- Audit `.like()` → `.ilike()` in all routes/services
- Verify `db.String(N)` lengths against existing data
- Mark old SQLite migration scripts as obsolete

### Phase 3: Vercel Deployment & Startup Optimization
**Rationale:** Database is ready. Now clean up `app.py` so Vercel cold starts are fast and reliable.
**Delivers:** Working Vercel deployment — no 500 errors, fast cold starts.
**Addresses:** T8 (WSGI routing), T9 (env vars), D6 (static files), D7 (health check), D10 (cold start).
**Avoids:** Pitfalls 4 (cold start timeout), 9 (SECRET_KEY), 13 (Vercel timeout), 16 (startup code).
**Work:**
- Remove `IS_VERCEL` seed block from `app.py`
- Move legacy data fix to one-time script
- Optionally move `db.create_all()` out of import path
- Set all environment variables on Vercel dashboard
- Add `/health` endpoint
- Deploy and verify
- Set `SECRET_KEY` as stable Vercel env var

### Phase 4 (Future): File Upload Storage
**Rationale:** Not part of DB migration but will break on Vercel. Separate concern.
**Delivers:** Evidence image uploads work on Vercel via cloud storage.
**Note:** Deferred per research — requires choosing storage provider (Vercel Blob, Cloudflare R2, S3).

### Phase Ordering Rationale

- **Phase 1 before 2:** Can't migrate data without a working connection.
- **Phase 2 before 3:** Vercel deploy needs tables to already exist in PostgreSQL — can't rely on cold-start `create_all`.
- **Phase 3 last:** Cleanup and deploy after DB is proven stable.
- **Phase 4 deferred:** File uploads are a separate feature, not blocking the core migration. Evidence URL storage works (text column), only the upload mechanism needs cloud storage.

### Research Flags

**Standard patterns (skip deep research during planning):**
- Phase 1 — well-documented: Neon official docs + SQLAlchemy docs cover everything.
- Phase 2 — straightforward: `db.create_all()` + seed script + LIKE audit is mechanical.
- Phase 3 — well-documented: Vercel Python runtime + Flask WSGI is stable.

**May need research during planning:**
- Phase 4 (file uploads) — needs storage provider comparison if not already decided.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | **HIGH** | Neon official docs, SQLAlchemy docs, Vercel Python runtime docs all cross-confirm. Only 2 packages needed. |
| Features (migration) | **HIGH** | Based on direct codebase inspection. All 10 table-stakes are concrete, file-level changes. |
| Features (v1.0 UX) | **MEDIUM** | FEATURES.md from prior milestone — UX guidance sound but not relevant to this migration. |
| Architecture | **HIGH** | Root cause diagnosed from code. Target architecture follows Neon's official serverless pattern. |
| Pitfalls | **HIGH** | All pitfalls derived from actual code inspection + known PostgreSQL/Vercel constraints. |

**Overall confidence:** **HIGH** — This is a well-documented migration path (Flask + SQLAlchemy + NeonDB + Vercel). No novel patterns required.

### Gaps to Address

| Gap | How to Handle |
|-----|---------------|
| **Real user data in SQLite?** | Need user input: is there production data in SQLite that must be migrated, or is seed data sufficient? This changes Phase 2 scope significantly. |
| **Vercel plan tier** | Hobby (10s timeout) vs Pro (60s). Affects whether AI chatbot routes will timeout. Need user input. |
| **File upload current state** | Are evidence images currently stored locally? If so, they're already lost on Vercel. May not need immediate action. |
| **NeonDB password rotation** | Credentials may be in git history (`.env/` file). Need to verify `.gitignore` and possibly rotate. |
| **FEATURES.md scope mismatch** | The v1.0 FEATURES.md covers UX/quiz/leaderboard — not this migration. FEATURES_v1.1_migration.md is the relevant file. Future milestones should reference the appropriate features file. |

### Open Questions Requiring User Input

1. **Is there real user data in the SQLite database that must be preserved?** If yes, Phase 2 needs a full data migration script (SQLite → PostgreSQL). If no, just seed fresh.
2. **What Vercel plan are you on?** Hobby has a 10-second function timeout. AI chatbot and scam analysis routes may exceed this.
3. **Should the NeonDB password be rotated?** If `.env/prosgressql_neondb.json` was ever committed to git, credentials are exposed.
4. **Is the filename typo (`prosgressql`) intentional?** The file is referenced as `prosgressql_neondb.json` in `config.py`. Renaming to `postgresql_neondb.json` would require updating the config loader call.

---

## Sources

### Primary (HIGH confidence)
- **Codebase analysis:** `config.py`, `app.py`, `models/models.py`, `extensions.py`, `vercel.json`, `requirements.txt`, `database/seed_all.py`, `.env/prosgressql_neondb.json`
- **NeonDB docs:** Connection pooling, SQLAlchemy integration, auto-suspend, SSL requirements
- **SQLAlchemy docs:** `pool_pre_ping`, `pool_recycle`, dialect portability, engine configuration
- **Vercel Python runtime docs:** `@vercel/python` WSGI detection, filesystem constraints, environment variables

### Secondary (MEDIUM confidence)
- **PROJECT.md constraints:** NeonDB for all environments, no Alembic, single region
- **copilot-instructions.md:** Manual migration scripts only, `.env/` JSON config pattern

### Tertiary (LOW confidence)
- **v1.0 FEATURES.md:** UX/quiz/leaderboard features — not directly applicable to migration but informs future milestones

---

*Research completed: 2026-04-03*
*Ready for roadmap: yes*
