---
phase: 05-leaderboard-integrity
verified: 2026-03-23T00:00:00Z
status: passed
score: 3/3 must-haves verified
re_verification: false
---

# Phase 05: Leaderboard Integrity — Verification Report

**Phase Goal:** Người dùng thấy bảng vinh danh có ý nghĩa và hạn chế được hành vi gian lận để leo hạng.
**Verified:** 2026-03-23
**Status:** ✅ PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Người dùng có thể xem bảng vinh danh người tố cáo nhiều nhất trên giao diện | ✓ VERIFIED | `id="reporter-leaderboard"` section with `id="reporter-table"` exists in `templates/leaderboard.html`; trust tier badges rendered via `reporter-integrity-badge`; DOM contract tests pass (`test_reporter_section_exists`, `test_reporter_table_headers`) |
| 2 | Bảng xếp hạng không chỉ dựa vào đếm thô, mà có luật integrity để giảm thao túng/gian lận | ✓ VERIFIED | `_compute_integrity_score()` implements `base = approved*1.0 + verified*0.5`, `penalty = min(window_count*0.2, base*0.5)`, `score = max(base-penalty, 0.0)`; `_get_flagged_hashes()` excludes cooldown actors entirely; tests `test_reporter_ranking_excludes_cooldown_actor` and `test_reporter_ranking_weights_verified_higher` verify both rules |
| 3 | Kết quả xếp hạng được cập nhật ở mức chấp nhận được và phản ánh đúng luật đã công bố | ✓ VERIFIED | Rankings computed live from DB on each request, sorted by `integrity_score` descending; route uses `try/except` fallback (`reporter_rankings=[]`) ensuring no 500s; `test_leaderboard_route_passes_reporter_rankings` confirms live injection |

**Score:** 3/3 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `services/leaderboard_integrity.py` | Integrity scoring service | ✓ VERIFIED | 120 lines; `get_reporter_rankings()`, `_compute_integrity_score()`, `_get_flagged_hashes()` all implemented and substantive |
| `templates/leaderboard.html` — reporter section | `id="reporter-leaderboard"` section with table | ✓ VERIFIED | Section at line ~165; 6-column table with trust tier badges, masked hash display, empty state fallback |
| `static/css/leaderboard.css` | Reporter section styles with `--mg-*` tokens | ✓ VERIFIED | `.leaderboard-reporter-shell`, `.reporter-rank`, `.reporter-id`, `.reporter-score`, `.reporter-integrity-badge` classes defined |
| `routes/main.py` | `reporter_rankings` passed to template | ✓ VERIFIED | Import at line 9; `get_reporter_rankings(limit=10)` called with try/except at line 171–173; passed as template context at line 181 |
| `tests/leaderboard/test_reporter_ranking.py` | 4 unit tests for ranking logic | ✓ VERIFIED | 4 tests all pass |
| `tests/leaderboard/test_leaderboard_route.py` | 2 route context tests | ✓ VERIFIED | 2 tests all pass |
| `tests/leaderboard/test_reporter_ui_contract.py` | 5 DOM contract tests | ✓ VERIFIED | 5 tests all pass |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `routes/main.py` | `services/leaderboard_integrity.py` | `from services.leaderboard_integrity import get_reporter_rankings` (line 9) | ✓ WIRED | Import + call at line 171; result passed to `render_template` at line 181 |
| `routes/main.py` | `templates/leaderboard.html` | `render_template("leaderboard.html", ..., reporter_rankings=reporter_rankings)` | ✓ WIRED | Context key matches Jinja2 loop variable `{% for reporter in reporter_rankings %}` |
| `leaderboard.html` | `.leaderboard-reporter-shell` CSS | `leaderboard.css` loaded via `url_for` at bottom of template | ✓ WIRED | `<link rel="stylesheet" href="{{ url_for('static', filename='css/leaderboard.css') }}">` |
| `_get_flagged_hashes()` | `get_reporter_rankings()` | Result consumed in exclusion check `if reporter_hash in flagged: continue` | ✓ WIRED | Cooldown exclusion active in live ranking pipeline |

---

### Requirements Coverage

| Requirement | Description | Status | Evidence |
|-------------|-------------|--------|----------|
| LEAD-01 | Reporter leaderboard displayed on /leaderboard page | ✓ SATISFIED | `id="reporter-leaderboard"` DOM section confirmed in template; route injects `reporter_rankings` context; `test_reporter_section_exists` and `test_reporter_table_headers` pass |
| LEAD-02 | Integrity rules applied (weighted score formula, cooldown exclusion) | ✓ SATISFIED | `_compute_integrity_score()` implements full weighted formula; cooldown exclusion verified by `test_reporter_ranking_excludes_cooldown_actor`; formula weights verified by `test_reporter_ranking_weights_verified_higher` |

---

### Anti-Patterns Found

| File | Pattern | Severity | Impact |
|------|---------|----------|--------|
| `services/leaderboard_integrity.py` line 109 | `datetime.utcnow()` deprecated in Python 3.12+ | ℹ️ Info | DeprecationWarning only; no functional impact; tests pass cleanly |
| `tests/leaderboard/test_reporter_ranking.py` lines 49, 51 | `datetime.utcnow()` in test fixtures | ℹ️ Info | Same deprecation warning; no functional impact |

No blocker or warning-level anti-patterns found.

---

### Test Results

```
Ran 11 tests in 0.420s

OK
```

All 11 tests passed:

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

---

### Human Verification Required

#### 1. Trust tier badge visual rendering

**Test:** Open `/leaderboard` in a browser with seeded reporter data having `integrity_score >= 10`, `>= 5`, and `< 5`.
**Expected:** Badges display "Tin cậy cao" (green), "Đang đóng góp" (yellow), "Mới tham gia" (grey) respectively.
**Why human:** Badge color class logic verified by DOM contract test but visual rendering requires browser.

#### 2. Reporter identity masking in production

**Test:** Submit a real report, then check the leaderboard — confirm only 8-char hash prefix appears, never email or full hash.
**Expected:** Reporter ID shown as `...XXXXXXXX` (8 chars only).
**Why human:** Programmatic tests use fixture data; production data flow requires a real submission.

---

### Summary

Phase 05 fully achieves its goal. All three success criteria are verified:

1. The reporter honor roll section (`id="reporter-leaderboard"`) is live on the `/leaderboard` page with a complete 6-column table, trust tier badges, and masked identity display.
2. The integrity scoring pipeline is substantive — weighted formula (`approved*1.0 + verified*0.5`) with spam penalty capped at 50% of base, plus full cooldown actor exclusion. These are not cosmetic; they are TDD-verified behaviors.
3. Rankings are computed live per request from the database, sorted correctly, and protected by a try/except fallback ensuring resilience.

LEAD-01 and LEAD-02 are both fully satisfied. No blocker anti-patterns exist. Two minor DeprecationWarnings for `datetime.utcnow()` are the only noted issues and do not affect functionality.

---

_Verified: 2026-03-23_
_Verifier: Claude (gsd-verifier)_
