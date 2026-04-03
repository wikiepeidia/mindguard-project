# Phase 7: PostgreSQL Configuration & Connection - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-04
**Phase:** 07-postgresql-configuration-connection
**Areas discussed:** Config URI Strategy, Connection Pool Type, JSON File Naming, IS_VERCEL Scope

---

## Config URI Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Env var first, JSON fallback | `os.environ.get('DATABASE_URL')` or load from `.env/postgresql_neondb.json` — works both on Vercel (env var) and local (.env/JSON file) | ✓ |
| JSON only for local | Local devs must have `.env/postgresql_neondb.json`. Vercel uses env var. Two separate code paths. | |
| Env var only everywhere | Remove JSON loading. All devs must set `DATABASE_URL` as system env var. Simpler code, harder dev setup. | |

**User's choice:** Env var first, JSON fallback
**Notes:** User emphasized that both Vercel and local dev must work simultaneously — friends in development need to be able to clone and run.

---

## Connection Pool Type

| Option | Description | Selected |
|--------|-------------|----------|
| NullPool (recommended for serverless) | No local pool — each request gets a fresh connection from NeonDB's pgbouncer. Best for Vercel serverless where processes are ephemeral. | ✓ |
| QueuePool with small limits | Local pool + NeonDB pgbouncer. `pool_size=2, max_overflow=3`. Fine for local dev, but on Vercel each process has its own pool that may hold stale connections. | |
| NullPool on Vercel, QueuePool locally | More code, but optimal for each env. | |

**User's choice:** NullPool (recommended for serverless)
**Notes:** None — straightforward selection.

---

## JSON File Naming

| Option | Description | Selected |
|--------|-------------|----------|
| Rename to postgresql_neondb.json | Fix the typo. No code currently loads this file by name — safe to rename. Cleaner for dev friends. | ✓ |
| Keep prosgressql_neondb.json | Leave as is. Devs just need to know the filename. | |

**User's choice:** Rename to postgresql_neondb.json
**Notes:** None.

---

## IS_VERCEL Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Remove SQLite path only (recommended) | Remove SQLite path logic (lines 30-33 in config.py). Keep IS_VERCEL flag itself — Phase 8 needs it. | |
| Remove IS_VERCEL entirely | Remove all IS_VERCEL references now. Cleans up both config.py and app.py in one shot. | |
| Keep everything, add PostgreSQL alongside | Leave IS_VERCEL and SQLite path. Just add PostgreSQL URI alongside. | |

**User's choice:** Custom — "delete the temp shit path we dont use sqlite for vercel. For dev, we use postgres but if neondb is fucked, fallback sqlite emergency"
**Notes:** User wants `/tmp` SQLite path removed entirely. SQLite fallback only for local dev when `DATABASE_URL` is not set at all. Follow-up question clarified: fallback triggers when `DATABASE_URL` env var is missing, not on connection failure.

### Fallback Clarification

| Option | Description | Selected |
|--------|-------------|----------|
| SQLite fallback for local only | If `DATABASE_URL` is missing/empty → fall back to `sqlite:///database/mindguard_v2.db`. Only useful locally. On Vercel, `DATABASE_URL` must be set (no fallback). | ✓ |
| Connection-test fallback | Try to connect to NeonDB. If connection fails at startup, switch to SQLite automatically. More complex but auto-recovers. | |

**User's choice:** SQLite fallback for local only

---

## Agent's Discretion

- Exact `SQLALCHEMY_ENGINE_OPTIONS` dict structure
- Whether to add a startup log line for active DB backend
- Order of operations in config.py restructuring

## Deferred Ideas

- Cold-start seeding removal (Phase 8)
- db.create_all() optimization (Phase 8)
- Vercel env var configuration (Phase 9)
- Legacy AUTOINCREMENT migration scripts (future cleanup)
