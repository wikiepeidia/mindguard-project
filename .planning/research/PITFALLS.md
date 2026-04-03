# Domain Pitfalls — SQLite→NeonDB PostgreSQL Migration + Vercel Deployment

**Project:** MindGuard v1.1
**Researched:** 2026-04-03
**Scope:** Adding NeonDB PostgreSQL and fixing Vercel deployment to existing Flask platform
**Confidence:** HIGH — pitfalls derived from direct codebase inspection + well-documented PostgreSQL/Vercel constraints

---

## Critical Pitfalls

Mistakes that cause 500 errors, data loss, or deployment failure.

---

### Pitfall 1: NeonDB Config File Is Not Valid JSON

**What goes wrong:** `config.py` uses `load_local_env('prosgressql_neondb.json')` which calls `json.load(f)`. The current file `.env/prosgressql_neondb.json` contains a raw connection string with inline comments — not JSON. `json.load()` silently fails (bare `except: return {}`) and returns an empty dict, so the connection string is never loaded.

**Actual file content (sanitized):**
```
postgresql: //user:pass@host/db?sslmode=require
ep-lingering-violet-...
// comments about API keys
```

**Why it happens:** The file was created as a quick dump of NeonDB dashboard info, not structured as JSON.

**Consequences:** `SQLALCHEMY_DATABASE_URI` falls back to SQLite. App appears to work locally but never connects to PostgreSQL. On Vercel, falls back to `/tmp/mindguard_v2.db` (ephemeral — data lost on every cold start).

**Prevention:**
1. Restructure file as valid JSON:
   ```json
   {
     "DATABASE_URL": "postgresql://user:pass@host/neondb?sslmode=require"
   }
   ```
2. Update `config.py` to load from this JSON and set `SQLALCHEMY_DATABASE_URI`.
3. On Vercel, set `DATABASE_URL` as an environment variable (never rely on `.env/` files in serverless).
4. Add validation: if the loaded URL doesn't start with `postgresql://`, raise an error at startup instead of silently falling back.

**Detection:** App works locally with SQLite but 500s on Vercel, or data disappears between deploys.

**Phase target:** Phase 1 (Config & Connection) — must be the very first fix.

---

### Pitfall 2: No PostgreSQL Driver in requirements.txt

**What goes wrong:** `requirements.txt` contains only `Flask`, `Flask-SQLAlchemy`, `Flask-Mail`, `Werkzeug`, `MarkupSafe`, `requests`. There is no `psycopg2-binary`, `psycopg`, or any PostgreSQL adapter. SQLAlchemy cannot connect to PostgreSQL without a driver.

**Why it happens:** The project was built on SQLite (which uses Python's built-in `sqlite3` module — no pip install needed).

**Consequences:** `sqlalchemy.exc.OperationalError` or `ModuleNotFoundError: No module named 'psycopg2'` on first connection attempt. On Vercel, this manifests as a 500 error with no helpful message in user-facing logs.

**Prevention:**
1. Add `psycopg2-binary>=2.9` to `requirements.txt` (binary wheel — no C compiler needed, critical for Vercel).
2. Do NOT use `psycopg2` (source package) — Vercel's build environment may not have `libpq-dev` and the compile will fail.
3. Alternatively, use `psycopg[binary]>=3.1` (psycopg3) which is newer and also ships binary wheels.
4. Test locally with PostgreSQL connection before deploying.

**Detection:** Immediate `ModuleNotFoundError` on app startup.

**Phase target:** Phase 1 (Config & Connection).

---

### Pitfall 3: Raw SQL Migration Scripts Use SQLite-Specific Syntax

**What goes wrong:** `database/migrate_anti_spam_phase2.py` (and `migrate_sensitive_access_log.py`) contain raw `CREATE TABLE` statements with `INTEGER PRIMARY KEY AUTOINCREMENT` — this is SQLite-only syntax. PostgreSQL uses `SERIAL` or `GENERATED ALWAYS AS IDENTITY`.

**Actual code (`migrate_anti_spam_phase2.py` line 35):**
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT,
...
triggered_cooldown BOOLEAN NOT NULL DEFAULT 0,
```

**Two issues:**
1. `AUTOINCREMENT` → PostgreSQL syntax is `SERIAL PRIMARY KEY` or `INTEGER GENERATED ALWAYS AS IDENTITY`.
2. `DEFAULT 0` for BOOLEAN → PostgreSQL expects `DEFAULT FALSE`. While `0` may work, it's dialect-incorrect.

**Consequences:** Migration scripts fail with `syntax error at or near "AUTOINCREMENT"` on PostgreSQL.

**Prevention:**
1. With NeonDB, these migration scripts are no longer needed — `db.create_all()` will create tables using SQLAlchemy's PostgreSQL dialect which handles `SERIAL` and proper `BOOLEAN` automatically.
2. If migration scripts must be kept for data migration, rewrite them using SQLAlchemy's `text()` with dialect-agnostic SQL, or use SQLAlchemy DDL operations instead of raw SQL.
3. Mark all `database/migrate_*.py` scripts as "SQLite-only — do not run against PostgreSQL" in their docstrings.

**Detection:** `ProgrammingError` when running migration scripts against PostgreSQL.

**Phase target:** Phase 2 (Schema Migration) — audit all files in `database/` directory.

---

### Pitfall 4: File Uploads Crash on Vercel's Read-Only Filesystem

**What goes wrong:** `routes/scammer.py` (lines 169-173) saves evidence images to `static/uploads/evidence/` on the local filesystem:

```python
upload_folder = os.path.join(current_app.static_folder, 'uploads', 'evidence')
if not os.path.exists(upload_folder): os.makedirs(upload_folder)
file.save(os.path.join(upload_folder, unique_filename))
```

Vercel's serverless runtime has a **read-only filesystem** except `/tmp` (which is ephemeral per invocation).

**Consequences:** File upload raises `OSError: [Errno 30] Read-only file system` or `PermissionError`. Every scammer report with evidence images fails. If saved to `/tmp`, files disappear after the function returns.

**Prevention:**
1. **Use external object storage** — Cloudflare R2, AWS S3, or Vercel Blob. Upload directly from the browser (presigned URL) or stream from the serverless function.
2. As a quick interim fix: save file to `/tmp`, upload to external storage, then store the external URL in `evidence_urls`.
3. Update `evidence_urls` column to store external URLs (it already stores URLs via `serialize_evidence()`, so the schema change is minimal).
4. Add `IS_VERCEL` check: if on Vercel, reject local file save path and use the external storage path.

**Detection:** Any report submission with attached evidence images returns 500 on Vercel.

**Phase target:** Phase 3 or separate phase — requires choosing a storage provider and updating the upload flow.

---

### Pitfall 5: Seed Data Runs on Every Vercel Cold Start (Data Duplication)

**What goes wrong:** `app.py` (lines 36-39) runs `run_seed()` on every cold start when `IS_VERCEL` is true:

```python
if Config.IS_VERCEL:
    from database.seed_all import run_seed
    run_seed()
```

With SQLite in `/tmp`, this was necessary because the DB was empty on each cold start. With PostgreSQL (persistent), seeding on every cold start will **duplicate all data** — duplicate admin users, duplicate scam reports, duplicate quiz results.

**Consequences:** Duplicate rows accumulate over time. Admin user creation may fail on unique constraint (email). Reports and leaderboard data become corrupted with ghost duplicates.

**Prevention:**
1. Remove the `IS_VERCEL` seed block entirely once PostgreSQL is connected.
2. Run `seed_all.py` exactly once as a standalone script against NeonDB.
3. Add idempotency guards to `run_seed()`: check if data exists before inserting (e.g., `if Registration.query.filter_by(email='admin@...').first() is None:`).
4. Consider a `seed_status` table or flag to track whether seeding has been done.

**Detection:** Duplicate admin accounts, exponentially growing row counts after multiple cold starts.

**Phase target:** Phase 2 (Schema Migration) — must be addressed before first deploy with PostgreSQL.

---

### Pitfall 6: `db.create_all()` at Module Top Level on Every Cold Start

**What goes wrong:** `app.py` line 34 runs `db.create_all()` unconditionally at import time:

```python
with app.app_context():
    db.create_all()
```

On Vercel, `app.py` is imported on every cold start. `db.create_all()` issues `CREATE TABLE IF NOT EXISTS` for every model — this hits NeonDB on every cold start, adding ~200-500ms latency.

**Why it matters for NeonDB:** NeonDB computes scale to zero after 5 minutes of inactivity. The first cold start must: (1) wake NeonDB compute, (2) establish TLS connection, (3) run `CREATE TABLE IF NOT EXISTS` for 13+ tables. This can push cold start time to 3-8 seconds.

**Consequences:** Slow cold starts. Unnecessary database round-trips. Potential connection timeout if NeonDB compute is waking up simultaneously.

**Prevention:**
1. Run `db.create_all()` only in a standalone setup script, not on every app import.
2. On Vercel, trust that tables already exist (they persist in PostgreSQL).
3. If defensive checks are needed, use a lightweight health check query (`SELECT 1`) instead of `CREATE TABLE IF NOT EXISTS` for all tables.
4. Consider setting NeonDB's auto-suspend timeout to a longer value (e.g., 5 minutes → 15 minutes) during initial testing.

**Detection:** Cold start times > 5 seconds. Vercel function timeout errors (default 10s for hobby plan).

**Phase target:** Phase 1 (Config & Connection) — remove from startup path.

---

### Pitfall 7: Missing SSL Configuration for NeonDB Connection

**What goes wrong:** NeonDB requires SSL (`sslmode=require`). The connection string in the `.env` file includes `?sslmode=require`, but SQLAlchemy's default engine creation for PostgreSQL may not pass SSL parameters correctly on all platforms.

**Consequences:** `psycopg2.OperationalError: connection to server failed: SSL required` or intermittent connection drops.

**Prevention:**
1. Ensure connection string includes `?sslmode=require` (already present in the NeonDB string).
2. For `psycopg2`, this is usually sufficient. But if using connection pooling (see Pitfall 9), SSL must be configured at the pool level too.
3. Add `SQLALCHEMY_ENGINE_OPTIONS` in config:
   ```python
   SQLALCHEMY_ENGINE_OPTIONS = {
       "connect_args": {"sslmode": "require"}
   }
   ```
4. Test connection from local dev machine to NeonDB before deploying.

**Detection:** `OperationalError` with SSL-related message on first query.

**Phase target:** Phase 1 (Config & Connection).

---

## Moderate Pitfalls

Issues that cause bugs or degraded performance but aren't deployment-breaking.

---

### Pitfall 8: Connection Pool Exhaustion in Serverless

**What goes wrong:** SQLAlchemy's default connection pool (`QueuePool`) keeps connections open. In serverless, each cold start creates a new pool, but NeonDB has a connection limit (e.g., 100 for free tier). Multiple concurrent Vercel function instances can exhaust the pool.

**Why it happens:** Vercel spins up multiple function instances under load. Each instance creates its own SQLAlchemy engine with its own pool. Unlike a traditional server with one pool, serverless can have N pools × M connections.

**Consequences:** `psycopg2.OperationalError: too many connections for role "neondb_owner"`. Some requests fail while others succeed depending on which instance they hit.

**Prevention:**
1. Use `NullPool` for serverless (no persistent connections — connect per request):
   ```python
   from sqlalchemy.pool import NullPool
   SQLALCHEMY_ENGINE_OPTIONS = {
       "poolclass": NullPool,
       "connect_args": {"sslmode": "require"}
   }
   ```
2. Alternatively, use NeonDB's built-in connection pooler (pooler endpoint instead of direct endpoint). NeonDB provides a `-pooler` hostname specifically for serverless.
3. Set `pool_size=1, max_overflow=0` if using `QueuePool` as a compromise.
4. Monitor connection count via NeonDB dashboard during load testing.

**Detection:** Intermittent 500 errors under concurrent load. NeonDB dashboard shows connection count at limit.

**Phase target:** Phase 1 (Config & Connection) — must configure pool strategy before deploy.

---

### Pitfall 9: Flask Session Cookie SECRET_KEY Not Stable Across Deploys

**What goes wrong:** Flask's default session is a signed cookie (client-side), which works fine across serverless instances. However, the `SECRET_KEY` has a hardcoded fallback: `"dev-secret-key-mindguard-2025-secure"`. If `SECRET_KEY` isn't set as a Vercel environment variable, the fallback is used — but if it ever changes between deploys, all existing sessions are invalidated.

**Consequences:** Users get logged out on every deploy. CAPTCHA verification fails (session math answer doesn't match). Reporter IDs change, breaking anti-spam tracking.

**Prevention:**
1. Set `SECRET_KEY` as a Vercel environment variable with a strong, stable value.
2. Never change the secret key between deploys unless intentionally invalidating sessions.
3. The cookie-based session approach is actually serverless-friendly — no changes needed to session storage mechanism.

**Detection:** Users report being logged out after every Vercel deploy. CAPTCHA always fails.

**Phase target:** Phase 1 (Config & Connection) — set env var before first deploy.

---

### Pitfall 10: `LIKE` Case Sensitivity Difference

**What goes wrong:** SQLite's `LIKE` operator is case-insensitive by default for ASCII characters. PostgreSQL's `LIKE` is case-sensitive. Any search or filter using `.like()` or `.contains()` in SQLAlchemy will behave differently.

**Risk areas in MindGuard:**
- Scammer report search by `scammer_identifier`, `scammer_name`, `description`
- Admin dashboard filters
- Any query using `Model.column.like('%term%')`

**Consequences:** Searches that worked on SQLite return no results on PostgreSQL because of case mismatch. Users can't find scammer reports they previously could.

**Prevention:**
1. Use `Model.column.ilike('%term%')` (case-insensitive LIKE) instead of `.like()`.
2. Or use `func.lower(Model.column).like(func.lower(term))`.
3. Audit all `.like()`, `.contains()`, and `.startswith()` calls in routes and services.
4. PostgreSQL also supports `ILIKE` natively — SQLAlchemy's `.ilike()` maps to it.

**Detection:** Search features return fewer results on PostgreSQL than they did on SQLite.

**Phase target:** Phase 2 (Schema Migration) — audit during model migration.

---

### Pitfall 11: `datetime.utcnow` and `db.func.now()` Timezone Behavior

**What goes wrong:** All models use `default=datetime.utcnow` (without parentheses — correctly passing the function, not the result). `db.func.now()` is used in `scammer.py` lines 263, 273 for update timestamps. The PostgreSQL behavior difference: PostgreSQL's `NOW()` is timezone-aware if the column is `TIMESTAMP WITH TIME ZONE`, while `datetime.utcnow()` returns a naive (no timezone) datetime.

**All model columns use `db.DateTime` (no timezone):**
```python
created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

SQLAlchemy maps `DateTime` to `TIMESTAMP WITHOUT TIME ZONE` on PostgreSQL. `db.func.now()` works on both SQLite and PostgreSQL.

**Prevention:**
1. Keep `db.DateTime` (no timezone) — consistent with current behavior.
2. Ensure `datetime.utcnow()` is used consistently (not `datetime.now()` which uses local time).
3. `db.func.now()` works on both dialects — no change needed.
4. If timezone support is needed later, migrate to `db.DateTime(timezone=True)` and use `datetime.now(timezone.utc)`.

**Detection:** Timestamp comparison bugs. Reports showing wrong times.

**Phase target:** Phase 2 — low risk, verify during testing.

---

### Pitfall 12: Boolean Storage Differences in Data Migration

**What goes wrong:** SQLite stores `db.Boolean` as `0`/`1` integers. PostgreSQL stores them as native `TRUE`/`FALSE`. When migrating data from SQLite to PostgreSQL, boolean columns need explicit type casting.

**Affected columns (4 total):**
- `Registration.is_admin` (Boolean, default=False)
- `Registration.onboarding_completed` (Boolean, default=False)
- `AiQuizQuestion.is_verified` (Boolean, default=True)
- `AntiSpamEvent.triggered_cooldown` (Boolean, default=False)

**Consequences:** If data is migrated via raw SQL dump/restore, PostgreSQL may reject `0`/`1` values for boolean columns.

**Prevention:**
1. Use SQLAlchemy ORM for data migration (read from SQLite, write to PostgreSQL) — the ORM handles type conversion automatically.
2. If using raw SQL, cast explicitly: `CASE WHEN old_value = 1 THEN TRUE ELSE FALSE END`.
3. Don't use `pg_dump`/`sqlite3 .dump` for cross-database migration.

**Detection:** `DataError: invalid input syntax for type boolean: "0"` during data import.

**Phase target:** Phase 2 (Schema Migration) — data migration script must handle this.

---

### Pitfall 13: Vercel Python Runtime Timeout on Cold Start

**What goes wrong:** Vercel's `@vercel/python` runtime has specific constraints:
- **Max execution time:** 10 seconds (Hobby) / 60 seconds (Pro).
- **No persistent process:** Each request may hit a new or reused function instance.
- **Entry point:** Vercel expects a WSGI app object at module level in the file specified by `vercel.json`.

**Current `app.py` runs at import time:** `db.create_all()` + conditional seed + legacy data fix query. Combined with NeonDB cold start (compute wake-up), this can exceed 10 seconds.

**Consequences:** Function timeout on cold start. 500 errors if initialization takes too long.

**Prevention:**
1. Move ALL startup logic out of module-level code in `app.py`.
2. Ensure `app.py` exports the WSGI app as fast as possible.
3. Use lazy initialization for database connections.
4. Remove seed and legacy-fix code from the import path entirely.
5. Test cold start time end-to-end with a fresh Vercel deployment.

**Detection:** Vercel deploys succeed but first request after idle returns 504 Gateway Timeout.

**Phase target:** Phase 3 (Vercel Deployment) — restructure app initialization.

---

## Minor Pitfalls

Issues that are easy to fix but easy to forget.

---

### Pitfall 14: `db.String` Length Enforcement Difference

**What goes wrong:** SQLite ignores `String(200)` length limits entirely — you can store any length string. PostgreSQL enforces `VARCHAR(200)` strictly and will raise `DataError: value too long for type character varying(200)`.

**Risk areas:** `scammer_identifier` (200), `scammer_name` (200), `social_link` (200), `user_agent` (512). If existing SQLite data has values exceeding declared lengths, migration will fail.

**Prevention:**
1. Before migrating data, query max lengths in SQLite: `SELECT MAX(LENGTH(column)) FROM table`.
2. Increase column sizes in models if needed (e.g., `user_agent` to `String(1024)` or `Text`).
3. Consider using `db.Text` for unbounded strings (like `description`, which already uses `Text`).

**Detection:** `DataError: value too long` during data migration.

**Phase target:** Phase 2 — check before data migration.

---

### Pitfall 15: Credentials Potentially Committed to Git

**What goes wrong:** The `.env/prosgressql_neondb.json` file contains the NeonDB connection string with username and password in plaintext. If `.env/` is not properly gitignored, these credentials are in the repository history.

**Consequences:** Anyone with repository access can connect to the production database. Credential leak if repo is ever made public.

**Prevention:**
1. Verify `.env/` is in `.gitignore`.
2. **Rotate the NeonDB password immediately** if credentials were ever committed.
3. On Vercel, use environment variables (`DATABASE_URL`) instead of file-based config.
4. Check with `git log --all -- .env/` for any commits touching the directory.

**Detection:** `git log --all -- .env/` returns results.

**Phase target:** Phase 1 — security prerequisite.

---

### Pitfall 16: Vercel WSGI Entry Point Startup Code

**What goes wrong:** Vercel's Python runtime imports `app.py` and looks for the `app` WSGI variable. The `if __name__ == "__main__":` block (ngrok, debug server) won't run on Vercel — that's correct. But everything outside that guard (create_all, seed, legacy fix) runs on every cold start.

**Prevention:**
1. Ensure the WSGI export path is clean: `app = Flask(...)`, `app.config.from_object(Config)`, blueprint registration — nothing else at module level.
2. Move `db.create_all()`, seed logic, and legacy fixes into a separate `init_db.py` script or behind a CLI command.

**Detection:** Already covered by Pitfalls 5, 6, and 13.

**Phase target:** Phase 3 (Vercel Deployment).

---

### Pitfall 17: PostgreSQL Integer Sequence vs SQLite rowid

**What goes wrong:** SQLite auto-assigns rowids and `AUTOINCREMENT` ensures monotonically increasing IDs (never reuses deleted IDs). PostgreSQL `SERIAL` uses sequences which also don't reuse, but the sequence value can have gaps after failed transactions. If any code relies on contiguous IDs (e.g., counting reports by ID range), behavior changes.

**Prevention:** Don't rely on contiguous IDs. Use `COUNT(*)` instead of `MAX(id) - MIN(id) + 1`. This is unlikely to be an issue in MindGuard but worth noting.

**Detection:** Report count discrepancies if counting by ID gaps.

**Phase target:** No action needed — informational.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Config & Connection (Phase 1) | Pitfalls 1, 2, 7, 8, 9, 15 | Fix JSON config, add driver, configure SSL + NullPool, set SECRET_KEY, rotate credentials |
| Schema Migration (Phase 2) | Pitfalls 3, 5, 6, 10, 11, 12, 14 | Rewrite migration scripts, remove ephemeral seed, audit LIKE/Boolean/String lengths |
| Vercel Deployment (Phase 3) | Pitfalls 4, 6, 13, 16 | External file storage, clean startup path, respect runtime limits |
| Data Migration (Phase 2.5) | Pitfalls 3, 12, 14 | Use ORM-based migration, validate boolean casting, check string lengths |

## Integration Pitfalls (Multiple Systems Interacting)

| Systems | Pitfall | Prevention |
|---------|---------|------------|
| NeonDB + Vercel cold start | NeonDB compute wakes from sleep (1-3s) + Vercel function cold start (1-2s) = 3-5s before first query. Add `db.create_all()` = potential timeout. | Remove `create_all()` from startup. Use NeonDB pooler endpoint. Consider keeping NeonDB awake during initial testing. |
| File uploads + Vercel filesystem | Evidence images can't be saved to disk. Current code crashes on read-only FS. | Switch to external storage (Cloudflare R2 recommended — project already uses Cloudflare for CAPTCHA). |
| Anti-spam + Serverless instances | Each Vercel instance has its own memory. If `AntiSpamDecisionService` caches anything in-memory, it won't share across instances. | Verify anti-spam service is fully database-backed (it appears to be via `AntiSpamEvent` and `AntiSpamActorState` models — likely OK). |
| Session cookies + Deploy | `SECRET_KEY` fallback means different deploy = potentially different key = all sessions invalidated. | Set stable `SECRET_KEY` in Vercel env vars. |

---

## Sources

- **NeonDB connection pooling:** NeonDB official docs — connection pooling for serverless (HIGH confidence)
- **Vercel Python runtime:** Vercel docs — `@vercel/python` limitations (HIGH confidence)
- **SQLite→PostgreSQL differences:** SQLAlchemy docs — dialect-specific behavior (HIGH confidence)
- **psycopg2-binary for serverless:** psycopg2 docs — binary vs source package (HIGH confidence)
- **Boolean/AUTOINCREMENT syntax:** PostgreSQL docs — DDL syntax differences from SQLite (HIGH confidence)
- **Direct codebase inspection:** All pitfalls verified against actual code in `config.py`, `app.py`, `models/models.py`, `routes/scammer.py`, `database/migrate_anti_spam_phase2.py`, `vercel.json`, and `.env/prosgressql_neondb.json` (HIGH confidence)
