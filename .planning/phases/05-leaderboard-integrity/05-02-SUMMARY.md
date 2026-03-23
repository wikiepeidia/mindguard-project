---
phase: "05"
plan: "02"
subsystem: "leaderboard-integrity"
tags: ["leaderboard", "reporter-ui", "tdd", "dom-contract", "css-tokens"]
dependency_graph:
  requires: ["services/leaderboard_integrity.py", "reporter_rankings template context (05-01)"]
  provides: ["id=reporter-leaderboard DOM section", "reporter honor roll UI", "DOM contract tests"]
  affects: ["templates/leaderboard.html", "static/css/leaderboard.css", "services/leaderboard_integrity.py", "routes/main.py"]
tech_stack:
  added: []
  patterns: ["TDD RED-GREEN DOM contract", "Bootstrap 5 trust tier badges", "CSS design tokens (--mg-*)"]
key_files:
  created:
    - tests/leaderboard/test_reporter_ui_contract.py
  modified:
    - templates/leaderboard.html
    - static/css/leaderboard.css
    - services/leaderboard_integrity.py
    - routes/main.py
key_decisions:
  - "Seeded ScammerReport fixture in test setUp to force tbody loop rendering — empty DB always shows else-branch only"
  - "OperationalError guard in _get_flagged_hashes() protects against missing anti_spam_actor_states table"
  - "Route try/except fallback ensures reporter_rankings=[] on any service exception"
metrics:
  duration: "~5 minutes"
  completed: "2026-03-23"
  tasks: 5
  files: 5
---

# Phase 05 Plan 02: Reporter Honor Roll UI & Integrity Display Summary

## One-liner

TDD-validated reporter honor roll section with trust tier badges, masked identity display, and --mg-* design tokens — 11/11 tests passing.

## What Was Built

- **`templates/leaderboard.html`**: New `id="reporter-leaderboard"` section inserted after `.leaderboard-table-shell`, inside the main container. Contains `id="reporter-table"` with 6 columns: Hạng, Người tố cáo, Báo cáo được duyệt, Đã xác minh, Điểm uy tín, Cấp độ. Trust tier badges (`reporter-integrity-badge`) render via `{% if %}` logic: bg-success ("Tin cậy cao" ≥10), bg-warning text-dark ("Đang đóng góp" ≥5), bg-secondary ("Mới tham gia" else). Empty state: colspan=6 "Chưa có dữ liệu." Reporter identity masked to 8-char hash prefix only.

- **`static/css/leaderboard.css`**: Added reporter section block using `--mg-*` design tokens — `.leaderboard-reporter-shell` (border, shadow, radius), `.reporter-rank` (accent color, bold), `.reporter-id` (monospace), `.reporter-score` (bold), `.reporter-integrity-badge` (pill, no-wrap). No hardcoded colors.

- **`tests/leaderboard/test_reporter_ui_contract.py`**: 5 DOM contract tests via Flask test client. Includes `setUp` that seeds a `ScammerReport` with `status='approved'` so the tbody loop renders and class markers appear.

- **`services/leaderboard_integrity.py`**: Added `OperationalError` import and try/except guard in `_get_flagged_hashes()` — returns empty set if `anti_spam_actor_states` table missing.

- **`routes/main.py`**: Wrapped `get_reporter_rankings()` in try/except — passes `reporter_rankings=[]` as fallback on any service exception.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | TDD RED — failing DOM contract tests | 9d278d8 | tests/leaderboard/test_reporter_ui_contract.py |
| 2-5 | Template, CSS, GREEN, regression verify | 97bbbd1 | leaderboard.html, leaderboard.css, test_reporter_ui_contract.py, leaderboard_integrity.py, main.py |

## Test Results

```
Ran 11 tests in 0.429s

OK
```

All tests pass:

- `test_leaderboard_route_passes_reporter_rankings` ✓
- `test_reporter_rankings_is_list` ✓
- `test_reporter_ranking_empty_db` ✓
- `test_reporter_ranking_excludes_cooldown_actor` ✓
- `test_reporter_ranking_ordered_by_approved` ✓
- `test_reporter_ranking_weights_verified_higher` ✓
- `test_reporter_section_exists` ✓
- `test_reporter_table_headers` ✓
- `test_reporter_rank_column` ✓
- `test_reporter_score_column` ✓
- `test_integrity_badge_exists` ✓

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing error handling] OperationalError guard missing in _get_flagged_hashes()**

- **Found during:** Task 2 (noted in project context)
- **Issue:** `_get_flagged_hashes()` would raise `OperationalError` if `anti_spam_actor_states` table missing (e.g. fresh DB before migration)
- **Fix:** Added `try/except OperationalError: return set()` around the query
- **Files modified:** `services/leaderboard_integrity.py`
- **Commit:** 97bbbd1

**2. [Rule 2 - Missing error handling] No fallback in leaderboard route for get_reporter_rankings() exception**

- **Found during:** Task 2 (noted in project context)
- **Issue:** Route would 500 if any service exception occurred
- **Fix:** Wrapped call in try/except, passes `reporter_rankings=[]` as fallback
- **Files modified:** `routes/main.py`
- **Commit:** 97bbbd1

**3. [Rule 1 - Bug] DOM contract tests used wrong ScammerReport field**

- **Found during:** Task 4 (first GREEN run)
- **Issue:** Used `scammer_info_raw` instead of required NOT NULL `scammer_identifier`; caused IntegrityError on all 5 tests
- **Fix:** Corrected field name to `scammer_identifier='test-scammer-ui'`, removed non-existent kwargs
- **Files modified:** `tests/leaderboard/test_reporter_ui_contract.py`
- **Commit:** 97bbbd1

**4. [Rule 1 - Bug] DOM contract tests failed with empty DB (tbody loop never rendered)**

- **Found during:** Task 4 (initial run showed 3/5 FAIL)
- **Issue:** `reporter-rank`, `reporter-score`, `reporter-integrity-badge` classes only in loop body; empty DB → `{% else %}` branch → no class markers in HTML
- **Fix:** Added `setUp` that seeds one `ScammerReport(status='approved')` so loop renders
- **Files modified:** `tests/leaderboard/test_reporter_ui_contract.py`
- **Commit:** 97bbbd1

## Self-Check

- [x] `templates/leaderboard.html` has `id="reporter-leaderboard"` — FOUND
- [x] `static/css/leaderboard.css` has `.reporter-integrity-badge` rules — FOUND
- [x] `tests/leaderboard/test_reporter_ui_contract.py` has 5 test methods — FOUND
- [x] 11/11 tests pass — VERIFIED
- [x] Commits 9d278d8, 97bbbd1 — FOUND

## Self-Check: PASSED
