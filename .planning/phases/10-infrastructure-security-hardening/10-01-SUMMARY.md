---
phase: 10-infrastructure-security-hardening
plan: 01
status: complete
started: 2026-04-13T14:30:00.000Z
completed: 2026-04-13T14:32:00.000Z
---

## One-liner

Removed `db.create_all()` from cold start and moved hardcoded credentials to environment variables.

## What Changed

### Task 1: Remove db.create_all() (INFRA-01)
- Removed `with app.app_context(): db.create_all()` block from `app.py:69-70`
- Tables already exist in NeonDB — this call wasted 500ms-2s on every cold start
- Reduces risk of hitting Vercel's 10s function timeout

### Task 2: Move credentials to env vars (INFRA-02)
- `ADMIN_PASSWORD = "mindguard2025"` → `os.environ.get("ADMIN_PASSWORD", "")`
- `REPORT_ENCRYPTION_KEY = "mindguard-secret-key-2025"` → `os.environ.get("REPORT_ENCRYPTION_KEY", "")`
- Empty string fallback is intentional — admin login fails safely when env var is absent

### INFRA-03 (pre-completed by teammate)
- No frontend admin credentials exposed — verified during code drop analysis

## Key Files

- `app.py` — removed db.create_all() block
- `config.py` — credentials now from env vars

## Self-Check: PASSED

- [x] `app.py` does not contain `db.create_all`
- [x] `config.py` does not contain `mindguard2025`
- [x] `config.py` does not contain `mindguard-secret-key-2025`
- [x] `config.py` contains `os.environ.get("ADMIN_PASSWORD"`
- [x] `config.py` contains `os.environ.get("REPORT_ENCRYPTION_KEY"`

## Deviations

None.

## Action Required

Set environment variables in Vercel Dashboard:
- `ADMIN_PASSWORD` = (your admin password)
- `REPORT_ENCRYPTION_KEY` = (your encryption key)
