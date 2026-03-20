---
status: resolved
trigger: "Investigate issue: missing-scammer-reports-table-homepage. GET / returns HTTP 500 due to sqlite OperationalError no such table: scammer_reports."
created: 2026-03-20T00:00:00Z
updated: 2026-03-20T02:42:10Z
---

## Current Focus

hypothesis: Root cause and fix are confirmed end-to-end.
test: User confirmed real workflow behavior after checkpoint.
expecting: Session can be archived and recorded in debug knowledge base.
next_action: archive debug session and append knowledge base entry

## Symptoms

expected: Home page GET / returns HTTP 200 and renders normally.
actual: GET / crashes with HTTP 500.
errors: sqlalchemy.exc.OperationalError: no such table: scammer_reports (query from routes/main.py index count on ScammerReport).
reproduction: Start Flask dev server and open http://127.0.0.1:5000/.
started: Observed now after recent project changes; exact first bad commit unknown.

## Eliminated

## Evidence

- timestamp: 2026-03-20T02:39:39Z
	checked: .planning/debug/knowledge-base.md
	found: No knowledge base file exists yet.
	implication: No prior known-pattern shortcut is available; continue standard hypothesis testing.

- timestamp: 2026-03-20T02:39:39Z
	checked: routes/main.py index route
	found: Homepage executes `ScammerReport.query.filter_by(status='approved').count()` before rendering.
	implication: Missing `scammer_reports` table will cause HTTP 500 immediately on GET /.

- timestamp: 2026-03-20T02:39:39Z
	checked: models/models.py ScammerReport model
	found: `ScammerReport` is mapped to `__tablename__ = 'scammer_reports'`.
	implication: Runtime query requires SQLite table `scammer_reports` to exist.

- timestamp: 2026-03-20T02:39:39Z
	checked: config.py database URI
	found: SQLAlchemy points to `database/mindguard_v2.db`.
	implication: Schema verification must target `database/mindguard_v2.db`.

- timestamp: 2026-03-20T02:40:22Z
	checked: sqlite schema for database/mindguard_v2.db
	found: `SELECT name FROM sqlite_master WHERE type='table'` returned only `sqlite_sequence`; `scammer_reports` is absent.
	implication: The active database schema is uninitialized for application models.

- timestamp: 2026-03-20T02:40:22Z
	checked: app.py startup flow and Flask test client reproduction
	found: `db.create_all()` runs only inside `if __name__ == "__main__"`; importing `app` then GET / returns 500 with `no such table: scammer_reports`.
	implication: Launch paths that import `app` (including `flask run`) skip table creation and trigger the crash.

- timestamp: 2026-03-20T02:40:58Z
	checked: Post-fix Flask test client GET /
	found: Response status is 200 after importing `app`.
	implication: The original crash path is resolved in import-based startup mode.

- timestamp: 2026-03-20T02:40:58Z
	checked: SQLite schema after app import
	found: sqlite_master now includes table `scammer_reports`.
	implication: Startup table initialization now prevents missing-table OperationalError.

- timestamp: 2026-03-20T02:42:10Z
	checked: Human checkpoint response
	found: User confirmed fixed in real workflow (`flask run` import-based GET / is 200 and `scammer_reports` exists in `database/mindguard_v2.db`).
	implication: Verification is complete; session can be marked resolved.

## Resolution

root_cause: `db.create_all()` was only executed in the `__main__` block, so when running the app through import-based entrypoints (e.g. `flask run`), tables were never initialized and homepage queries against `scammer_reports` failed.
fix: Moved `db.create_all()` execution out of `__main__` block so it runs during app initialization for both `flask run` and `python app.py`.
verification: Import-based reproduction now returns HTTP 200 for GET /, sqlite schema includes `scammer_reports`, and user confirmed fix in real workflow.
files_changed: ["app.py"]
