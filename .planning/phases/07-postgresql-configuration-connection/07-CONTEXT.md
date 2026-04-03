# Phase 7: PostgreSQL Configuration & Connection - Context

**Gathered:** 2026-04-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Flask app connects to NeonDB PostgreSQL instead of SQLite. Config is restructured, driver is added, and connection is verified locally. Both Vercel and local dev environments work with the same NeonDB instance. SQLite remains as emergency local-only fallback when DATABASE_URL is not set.

</domain>

<decisions>
## Implementation Decisions

### Config URI Loading (D-01)
- **D-01:** `SQLALCHEMY_DATABASE_URI` resolved via: `os.environ.get('DATABASE_URL')` first → `.env/postgresql_neondb.json` fallback → local SQLite emergency fallback (`database/mindguard_v2.db`). On Vercel, `DATABASE_URL` env var is required (no fallback — fail fast).
- The existing `load_local_env()` pattern in `config.py` is reused for JSON loading. Same pattern as `cloudflare.json` and `chatbot.json`.

### Connection Pool Strategy (D-02)
- **D-02:** Use `NullPool` everywhere (both local and Vercel). NeonDB's `-pooler` endpoint already provides pgbouncer — local SQLAlchemy pooling on top creates pool-on-pool issues.
- **D-02a:** `pool_pre_ping=True` for connection liveness validation.
- **D-02b:** `sslmode=require` in the connection URI (already present in NeonDB connection string).
- Engine options set via `SQLALCHEMY_ENGINE_OPTIONS` in `Config` class.

### JSON File Naming (D-03)
- **D-03:** Rename `.env/prosgressql_neondb.json` → `.env/postgresql_neondb.json` (fix typo).
- **D-03a:** Restructure content from raw text into valid JSON: `{"DATABASE_URL": "postgresql://...pooler..."}`.
- No existing code references the old filename — safe to rename.

### IS_VERCEL Cleanup (D-04)
- **D-04:** Remove the SQLite `/tmp` path logic from `config.py` (lines 30-33). No more `IS_VERCEL` SQLite branch.
- **D-04a:** Keep the `IS_VERCEL` flag itself — Phase 8 needs it to remove cold-start seeding from `app.py`.
- **D-04b:** SQLite fallback triggers only when `DATABASE_URL` is completely absent (not set in env, not in JSON). This is for local emergency dev only.

### Agent's Discretion
- Exact `SQLALCHEMY_ENGINE_OPTIONS` dict structure (NullPool import, pool_pre_ping, connect_args for SSL if needed beyond URI param).
- Whether to add a startup log line confirming which DB backend is active (PostgreSQL vs SQLite fallback).
- Order of operations in `config.py` restructuring (cleanup SQLite first vs add PostgreSQL first).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Configuration
- `config.py` — Central config class. Lines 7-33 contain `load_local_env()`, `IS_VERCEL`, SQLite path logic, and `SQLALCHEMY_DATABASE_URI`.
- `.env/prosgressql_neondb.json` — Malformed NeonDB config (to be renamed and restructured).
- `.env/cloudflare.json` — Reference for correct `.env/*.json` pattern.
- `.env/chatbot.json` — Reference for correct `.env/*.json` pattern.

### Database
- `extensions.py` — SQLAlchemy instance (`db = SQLAlchemy()`). No engine options currently set.
- `models/models.py` — All 13 SQLAlchemy models. All use portable types (String, Integer, Text, DateTime, Boolean, ForeignKey). Zero changes needed for PostgreSQL.

### App Lifecycle
- `app.py` — Lines 35-41: `db.init_app(app)`, `db.create_all()`, `IS_VERCEL` seed logic. Phase 7 does NOT touch seeding (Phase 8).

### Research
- `.planning/research/PITFALLS.md` — 17 pitfalls identified. Pitfall 1 (malformed JSON), Pitfall 7 (db.create_all cold start), Pitfall 2 (pooler endpoint) directly relevant.
- `.planning/research/STACK.md` — Package requirements: `psycopg2-binary>=2.9.9`.
- `.planning/research/ARCHITECTURE.md` — NeonDB connection architecture and serverless constraints.

### Deployment
- `vercel.json` — Vercel build config. Not modified in Phase 7.
- `requirements.txt` — Current deps (no psycopg2). Must add `psycopg2-binary`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `load_local_env(filename)` in `config.py`: Already handles JSON loading from `.env/` with silent failure. Reuse for `postgresql_neondb.json`.
- `Config` class pattern: All config is centralized. Just needs URI and engine options added.

### Established Patterns
- **Env var → JSON fallback**: Used for `CLOUDFLARE_SITE_KEY`, `OPENROUTER_API_KEY`. Same pattern applies to `DATABASE_URL`.
- **Single Config class**: No env-specific subclasses. All branching is inline with `os.environ.get()`.

### Integration Points
- `extensions.py` → `db = SQLAlchemy()` initialized without engine options. `SQLALCHEMY_ENGINE_OPTIONS` in Config class will be picked up by `db.init_app(app)`.
- `app.py` → `app.config.from_object(Config)` loads all config including new URI and engine options.
- `requirements.txt` → `psycopg2-binary` must be added for PostgreSQL driver.

</code_context>

<specifics>
## Specific Ideas

- User explicitly wants both Vercel and local dev to work simultaneously with the same NeonDB. Friends working locally should just clone, have the JSON file, and connect.
- The `-pooler` hostname must be used in the connection string (from research: `ep-lingering-violet-a1jiok7c-pooler.ap-southeast-1.aws.neon.tech`).
- Connection string: `postgresql://neondb_owner:npg_NlUTW9nsARq4@ep-lingering-violet-a1jiok7c-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require`

</specifics>

<deferred>
## Deferred Ideas

- **Cold-start seeding removal** — Phase 8 scope (START-01). IS_VERCEL flag preserved for this.
- **db.create_all() optimization** — Phase 8 scope (START-03). May need conditional or one-time execution.
- **Vercel env var configuration** — Phase 9 scope (VDEP-01).
- **Legacy migration scripts using AUTOINCREMENT** — Not blocking Phase 7 (models use SQLAlchemy ORM, not raw SQL). Mark for cleanup in future phase.

</deferred>

---

*Phase: 07-postgresql-configuration-connection*
*Context gathered: 2026-04-04*
