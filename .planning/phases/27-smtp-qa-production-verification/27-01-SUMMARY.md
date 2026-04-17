---
phase: 27-smtp-qa-production-verification
plan: 01
subsystem: otp-production-schema
tags: [otp, smtp, production, neon, anti-spam]

requires:
  - phase: 26-auth-flow-smtp-cutover
    provides: SMTP-ready auth routes and route-level diagnostics
provides:
  - Production-safe OTP schema repair for `otp_challenges`
  - Production-safe anti-spam `account_id` width repair for OTP abuse guard
  - Regression coverage that locks the width contract into the repo
affects: [27-02]

tech-stack:
  added: []
  patterns: [Idempotent production migrations, log-driven production diagnosis, schema-contract regression testing]

key-files:
  created: [database/migrate_anti_spam_account_id_length.py]
  modified: [models/models.py, database/migrate_anti_spam_phase2.py, tests/antispam/test_otp_guardrails.py]

key-decisions:
  - "Production resend was fixed by widening schema width instead of truncating OTP actor IDs."
  - "Existing `database/migrate_otp_challenges.py` stayed the repair path for the missing OTP table; a new migration was added only for the anti-spam width drift."

patterns-established:
  - "When protected production smoke fails, use `vercel logs` first and treat manual migration scripts as the source of truth for live schema repair."
  - "Schema-width assumptions that only fail on Postgres should be locked with explicit contract tests, not left implicit in SQLite coverage."

requirements-completed: [SMTPQ-03]

duration: 45min
completed: 2026-04-17
---

# Phase 27 Plan 01 Summary

Diagnosed and repaired the production schema blockers that live SMTP smoke exposed.

## Accomplishments

- Pulled the live `POST /register` stack trace and confirmed Production Neon was missing `otp_challenges`.
- Ran the existing OTP migration against the Production database sourced from Vercel Production envs.
- Pulled the subsequent `POST /verify-otp/resend` stack trace and traced it to `anti_spam_* .account_id` being too narrow for `otp:<sha256>` actor IDs.
- Widened the anti-spam `account_id` contract in the SQLAlchemy models and base anti-spam bootstrap migration.
- Added `database/migrate_anti_spam_account_id_length.py` so existing Postgres/Neon databases can be repaired idempotently.
- Added a regression check proving OTP actor IDs fit both anti-spam `account_id` columns.

## Task Commits

Pending final closeout commit.

## Verification

- `python -m pytest tests/antispam/test_otp_guardrails.py tests/test_otp_auth_integration.py -q`
- `vercel logs dpl_8FYykxiS598gBJLou1HJBzMUxThh --no-follow --status-code 500 --since 30m --expand`
- `vercel env pull <tmp> --environment=production --yes` + `python database/migrate_otp_challenges.py`
- `vercel env pull <tmp> --environment=production --yes` + `python database/migrate_anti_spam_account_id_length.py`

## Self-Check: PASSED
