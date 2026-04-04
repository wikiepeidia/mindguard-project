---
phase: 07-postgresql-configuration-connection
plan: 01
subsystem: database
tags: [postgresql, neondb, psycopg2, sqlalchemy, nullpool]

requires:
  - phase: none
    provides: first phase of v1.1 milestone

provides:
  - NeonDB PostgreSQL connection via config.py
  - Valid .env/postgresql_neondb.json with pooler endpoint
  - psycopg2-binary driver in requirements.txt
  - SQLALCHEMY_ENGINE_OPTIONS with NullPool + pool_pre_ping

affects: [phase-08-app-startup, phase-09-vercel-deployment]

tech-stack:
  added: [psycopg2-binary>=2.9.9, SQLAlchemy>=2.0.33]
  patterns: [env-var-then-json-fallback-then-sqlite, nullpool-for-pgbouncer, pool-pre-ping-for-auto-suspend]

key-files:
  created: [.env/postgresql_neondb.json]
  modified: [config.py, requirements.txt]

key-decisions:
  - "DATABASE_URL resolution: env var -> JSON fallback -> SQLite emergency (per D-01)"
  - "NullPool everywhere — NeonDB pooler provides pgbouncer (per D-02)"
  - "Conditional engine options: NullPool only for postgresql:// URIs, empty dict for SQLite fallback"
  - "IS_VERCEL flag kept for Phase 8 seed removal (per D-04a)"
  - "Cloudflare Turnstile config untouched — confirmed working with env var -> JSON fallback pattern"

patterns-established:
  - "db_config loading: load_local_env('postgresql_neondb.json') alongside cf_config and ai_config"
  - "Conditional SQLALCHEMY_ENGINE_OPTIONS based on URI scheme"

requirements-completed: [DBCFG-01, DBCFG-02, DBCFG-03, DBCFG-04, START-02]

duration: 8min
completed: 2026-04-04
---

# Phase 7 Plan 01: PostgreSQL Configuration & Connection Summary

**NeonDB PostgreSQL connection configured with NullPool + pool_pre_ping, replacing broken SQLite-on-Vercel setup. SELECT 1 verified through Flask app context.**

## Performance

- **Duration:** 8 min
- **Tasks:** 3 completed
- **Files modified:** 3

## Accomplishments

- Created valid `.env/postgresql_neondb.json` with NeonDB pooler endpoint (replaces malformed `prosgressql_neondb.json`)
- Rewrote `config.py` database section: env var → JSON → SQLite fallback chain with NullPool + pool_pre_ping
- Verified live NeonDB connection: `SELECT 1` returns 1 through both raw SQLAlchemy and Flask app context
- Confirmed Cloudflare Turnstile config preserved (None locally as expected, will activate via Vercel env vars)
- Added `psycopg2-binary>=2.9.9` and `SQLAlchemy>=2.0.33` to requirements.txt

## Task Commits

1. **Task 1: Fix NeonDB JSON config and add PostgreSQL driver** - `131b0e5` (chore)
2. **Task 2: Rewrite config.py database section for NeonDB PostgreSQL** - `3d7b8b8` (feat)
3. **Task 3: Verify NeonDB connection end-to-end** - verification only, no code changes

## Files Created/Modified

- `.env/postgresql_neondb.json` - Valid JSON with DATABASE_URL (pooler endpoint) and NEON_API_KEY
- `config.py` - PostgreSQL URI with env→JSON→SQLite fallback, NullPool engine options, IS_VERCEL /tmp path removed
- `requirements.txt` - Added psycopg2-binary>=2.9.9 and SQLAlchemy>=2.0.33

## Decisions Made

- Conditional `SQLALCHEMY_ENGINE_OPTIONS`: NullPool + pool_pre_ping only for postgresql:// URIs. SQLite fallback gets empty dict (NullPool is incompatible with SQLite).
- `sslmode=require` stays in the URI string itself — no separate `connect_args` needed.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Phase 8 (App Startup Cleanup): `IS_VERCEL` flag preserved for seed removal. `db.create_all()` ready to test against NeonDB.
- Phase 9 (Vercel Deployment): `DATABASE_URL` env var pattern ready — just needs Vercel dashboard configuration. Cloudflare Turnstile will activate when `CLOUDFLARE_SITE_KEY` and `CLOUDFLARE_SECRET_KEY` env vars are set on Vercel.

---
*Phase: 07-postgresql-configuration-connection*
*Completed: 2026-04-04*
