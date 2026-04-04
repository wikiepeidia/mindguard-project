---
phase: 08-app-startup-cleanup-data-seeding
type: context
status: ready-to-plan
created: "2026-04-04"
---

# Phase 8: App Startup Cleanup & Data Seeding — Context

## Phase Goal

App startup sạch (không seed mỗi cold start) và NeonDB có đầy đủ tables + seed data từ script chạy 1 lần.

## Requirements Addressed

- **START-01**: Xóa seed logic khỏi app.py (không chạy mỗi cold start)
- **START-03**: Xác nhận db.create_all() tạo thành công tables trong NeonDB
- **SEED-01**: Seed data tồn tại trong NeonDB sau khi chạy script 1 lần

## Current State (Verified 2026-04-04)

From giggles check before planning:

| Item | Status |
|------|--------|
| app.py cold-start blocks removed | ✅ Done |
| NeonDB tables (13/13 tables) | ✅ Exist |
| Seed script idempotency guards | ✅ Done |
| Seed data in NeonDB | ❌ Not run yet (0 rows) |

Tables confirmed in NeonDB:
`ai_chat_messages`, `ai_chat_sessions`, `ai_quiz_questions`, `anti_spam_actor_states`,
`anti_spam_events`, `chat_support_messages`, `quiz_results`, `registrations`,
`scam_reports`, `scammer_leaderboard`, `scammer_reports`, `sensitive_access_logs`, `subscriptions`

## Decisions

### D-01: Remove IS_VERCEL seed block from app.py
**Decision**: Remove the `if Config.IS_VERCEL: run_seed()` block (was lines 36-39).
**Status**: ✅ Already done — app.py is clean.
**Rationale**: Seeding on every cold start causes duplicate data on Vercel's ephemeral containers.

### D-02: Remove db.create_all() from app.py
**Decision**: Remove `db.create_all()` from startup after confirming NeonDB tables exist.
**Status**: ✅ Already done — removed, comment added: `# Schema managed externally`.
**Rationale**: NeonDB tables confirmed via `information_schema.tables` (13 tables present). 200-500ms penalty avoided.

### D-03: Add idempotency guards to seed scripts
**Decision**: Add check-before-insert guards to all `seed_*` functions in `database/seed_all.py`.
**Status**: ✅ Already done — all 6 seed functions have guards:
- `seed_admin`: `filter_by(email=...).first()`
- `seed_users`: `filter_by(email=...).first()` per user
- `seed_scammers`: `filter_by(scammer_info_raw=...).first()` per entry
- `seed_leaderboard`: `filter_by(scammer_id=...).first()` per entry
- `seed_articles`: `filter_by(title=...).first()` per article
- `seed_quiz_results`: `QuizResult.query.count() >= 15` check

### D-04: Seed execution method — manual terminal command
**Decision**: Seed is run once via manual terminal command, NOT auto-detected at startup.
**Status**: ⏳ Not yet run — this is the remaining work for Phase 8.
**Command**: `python -m database.seed_all` (or `python database/seed_all.py`)
**Rationale**: One-time operation. Idempotency guards make it safe to re-run if needed.

## Deferred Ideas

- Auto-detect empty DB and prompt user to seed (deferred — adds startup complexity)
- Separate env-flag `SEED_ON_STARTUP=true` (deferred — unnecessary for NeonDB)
- Dark mode seeding UI (not applicable)

## Files In Scope

| File | Role |
|------|------|
| `app.py` | Cold-start blocks already removed |
| `database/seed_all.py` | Main seeder — `run_seed()` + all 6 functions, guards added |
| `database/seed_kb_articles.py` | KB articles seeder — separate, may also need guard check |
| `models/models.py` | 13 SQLAlchemy models being seeded |
| `config.py` | `IS_VERCEL` flag exists but no longer referenced in seed path |

## What Phase 8 Plans Must Do

1. Run `database/seed_all.py` against NeonDB
2. Verify row counts across key tables
3. Confirm app serves pages with real data (quiz, leaderboard, report)
4. Optionally check `database/seed_kb_articles.py` idempotency and run it

## References

- `.planning/phases/07-postgresql-configuration-connection/07-01-SUMMARY.md` — Phase 7 completion
- `.planning/research/PITFALLS.md` — Pitfall 6 (create_all latency), Pitfall 7 (seed duplication)
