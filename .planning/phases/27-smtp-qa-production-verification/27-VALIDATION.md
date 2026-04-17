---
status: passed
phase: 27-smtp-qa-production-verification
validated: 2026-04-17
---

# Phase 27: SMTP QA & Production Verification - Validation

## Commands Executed

```text
node "$HOME/.copilot/get-shit-done/bin/gsd-tools.cjs" frontmatter validate .planning/phases/27-smtp-qa-production-verification/27-01-PLAN.md --schema plan
node "$HOME/.copilot/get-shit-done/bin/gsd-tools.cjs" verify plan-structure .planning/phases/27-smtp-qa-production-verification/27-01-PLAN.md
node "$HOME/.copilot/get-shit-done/bin/gsd-tools.cjs" frontmatter validate .planning/phases/27-smtp-qa-production-verification/27-02-PLAN.md --schema plan
node "$HOME/.copilot/get-shit-done/bin/gsd-tools.cjs" verify plan-structure .planning/phases/27-smtp-qa-production-verification/27-02-PLAN.md
python -m pytest tests/antispam/test_otp_guardrails.py tests/test_otp_auth_integration.py -q
vercel logs dpl_8FYykxiS598gBJLou1HJBzMUxThh --no-follow --status-code 500 --since 30m --expand
vercel env pull <tmp> --environment=production --yes && python database/migrate_otp_challenges.py
vercel env pull <tmp> --environment=production --yes && python database/migrate_anti_spam_account_id_length.py
protected production smoke via `vercel curl` stepwise GET/POST flow with cookie jar reuse and CSRF parsing
```

## Results

- `python -m pytest tests/antispam/test_otp_guardrails.py tests/test_otp_auth_integration.py -q`
  - Result: `37 passed, 113 warnings in 3.40s`
- Initial production `POST /register` log trace
  - Result: failed with `psycopg2.errors.UndefinedTable: relation "otp_challenges" does not exist`
- `python database/migrate_otp_challenges.py` against Production envs
  - Result: created `otp_challenges` plus required indexes in Neon
- Second production `POST /verify-otp/resend` log trace
  - Result: failed with `psycopg2.errors.StringDataRightTruncation: value too long for type character varying(64)` on `anti_spam_actor_states.account_id`
- `python database/migrate_anti_spam_account_id_length.py` against Production envs
  - Result: widened `anti_spam_events.account_id` and `anti_spam_actor_states.account_id` to `VARCHAR(128)`
- Final protected production smoke on `mindguard-five.vercel.app`
  - Result: `POST /register` returned `302` to `/verify-otp`
  - Result: verify page rendered for a unique Gmail plus-alias using the configured mailbox sender path
  - Result: immediate resend returned `302` to `/verify-otp` with the expected cooldown warning
  - Result: resend became enabled after cooldown and a later `POST /verify-otp/resend` returned `302` to `/verify-otp` with the success notice `Mã OTP mới đã được gửi đến email của bạn.`

## Coverage Added In This Phase

- `models/models.py`
  - Widens anti-spam `account_id` columns so OTP abuse actor IDs fit the persisted schema contract.
- `database/migrate_anti_spam_phase2.py`
  - Ensures fresh anti-spam table creation uses the widened `account_id` width.
- `database/migrate_anti_spam_account_id_length.py`
  - Provides an idempotent repair path for existing Postgres/Neon databases.
- `tests/antispam/test_otp_guardrails.py`
  - Locks the OTP actor ID width contract so the schema mismatch cannot silently regress.

## Residual Notes

- OTP/auth tests still emit existing `datetime.utcnow()` deprecation warnings from application code and fixtures.
- Flask-Limiter still emits the expected in-memory backend warning in the test harness.
- The Vercel production deployment remains protected, so future smoke checks should continue using authenticated `vercel curl` flows rather than anonymous HTTP requests.
