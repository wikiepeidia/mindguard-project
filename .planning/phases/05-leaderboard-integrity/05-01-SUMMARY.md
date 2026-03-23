---
phase: "05"
plan: "01"
subsystem: "leaderboard-integrity"
tags: ["leaderboard", "reporter-ranking", "anti-spam", "integrity-score", "tdd"]
dependency_graph:
  requires: ["services/anti_spam.py", "models/models.py (ScammerReport, AntiSpamActorState)"]
  provides: ["services/leaderboard_integrity.py", "reporter_rankings template context"]
  affects: ["routes/main.py leaderboard route", "leaderboard.html template"]
tech_stack:
  added: []
  patterns: ["TDD RED-GREEN", "Python aggregation over SQLAlchemy ORM", "Flask template_rendered signal for context testing", "StaticPool in-memory SQLite for isolated tests"]
key_files:
  created:
    - services/leaderboard_integrity.py
    - tests/leaderboard/__init__.py
    - tests/leaderboard/test_reporter_ranking.py
    - tests/leaderboard/test_leaderboard_route.py
  modified:
    - routes/main.py
    - .gitignore
key_decisions:
  - "Python-level aggregation over SQLAlchemy case() to avoid version-specific syntax differences"
  - "Exclude cooldown reporters entirely (not threshold-filtered) for predictable test behavior"
  - "reporter_hash_display is always first 8 chars — never full hash or email exposed"
  - "Added tests/leaderboard/ gitignore exception (same pattern as tests/quizflow/)"
metrics:
  duration: "~10 minutes"
  completed: "2026-03-23"
  tasks: 5
  files: 6
---

# Phase 05 Plan 01: Reporter Leaderboard Data Layer & Integrity Service Summary

## One-liner

Privacy-safe reporter integrity ranking with cooldown exclusion, verified-report bonus weighting, and TDD-verified route context injection.

## What Was Built

A complete backend data layer for the reporter leaderboard:

- **`services/leaderboard_integrity.py`**: Three functions implementing the full integrity scoring pipeline:
  - `get_reporter_rankings(limit)` — queries ScammerReport grouped by reporter_hash, excludes flagged actors, computes integrity score, returns ranked list with `reporter_hash_display` (8-char prefix only)
  - `_compute_integrity_score(approved, verified, window_count)` — `base = approved*1.0 + verified*0.5`, penalty capped at 50% of base
  - `_get_flagged_hashes()` — queries AntiSpamActorState for cookie-actor cooldowns active right now

- **`routes/main.py`**: Import added, `reporter_rankings=get_reporter_rankings(limit=10)` passed to `leaderboard.html`

- **`tests/leaderboard/`**: Full TDD test suite (4 ranking tests + 2 route tests)

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | TDD RED — failing ranking tests | 80e8922 | tests/leaderboard/__init__.py, test_reporter_ranking.py, .gitignore |
| 2 | Implement integrity service (GREEN) | a15731e | services/leaderboard_integrity.py |
| 3 | Update leaderboard route | 9a2822d | routes/main.py |
| 4 | TDD route context tests | 15491e5 | tests/leaderboard/test_leaderboard_route.py |
| 5 | Verification — all 6 tests pass | (no new commit) | — |

## Test Results

```
Ran 6 tests in 0.241s

OK
```

All tests pass:
- `test_reporter_ranking_empty_db` ✓
- `test_reporter_ranking_ordered_by_approved` ✓
- `test_reporter_ranking_excludes_cooldown_actor` ✓
- `test_reporter_ranking_weights_verified_higher` ✓
- `test_leaderboard_route_passes_reporter_rankings` ✓
- `test_reporter_rankings_is_list` ✓

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] .gitignore blocked tests/leaderboard/ from being committed**
- **Found during:** Task 1 commit attempt
- **Issue:** `.gitignore` had `tests/*` with only `tests/quizflow/` and `tests/privacy/` exceptions
- **Fix:** Added `!tests/leaderboard/`, `!tests/leaderboard/__init__.py`, `!tests/leaderboard/test_*.py` to `.gitignore`
- **Files modified:** `.gitignore`
- **Commit:** 80e8922

**2. [Plan clarification] Task 4 tests were not "failing" — route already updated in Task 3**
- The plan described Task 4 as "failing tests" but since Task 3 had already updated the route, all tests passed immediately. This is a plan sequencing inconsistency. Both route tests pass correctly.

## Self-Check

- [x] `services/leaderboard_integrity.py` exists — FOUND
- [x] `tests/leaderboard/__init__.py` exists — FOUND
- [x] `tests/leaderboard/test_reporter_ranking.py` exists — FOUND
- [x] `tests/leaderboard/test_leaderboard_route.py` exists — FOUND
- [x] All 6 tests pass
- [x] Commits 80e8922, a15731e, 9a2822d, 15491e5 — FOUND

## Self-Check: PASSED
