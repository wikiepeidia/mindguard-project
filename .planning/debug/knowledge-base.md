# GSD Debug Knowledge Base

Resolved debug sessions. Used by `gsd-debugger` to surface known-pattern hypotheses at the start of new investigations.

---

## missing-scammer-reports-table-homepage — Homepage GET / crashed with missing scammer_reports table
- **Date:** 2026-03-20
- **Error patterns:** HTTP 500, GET /, sqlalchemy.exc.OperationalError, no such table, scammer_reports, homepage crash
- **Root cause:** `db.create_all()` was only executed in the `__main__` block, so import-based startup paths (including `flask run`) skipped schema initialization and homepage query to `scammer_reports` crashed.
- **Fix:** Run `db.create_all()` during app initialization (not only in `__main__`) so both `flask run` and `python app.py` have required tables.
- **Files changed:** app.py
---
