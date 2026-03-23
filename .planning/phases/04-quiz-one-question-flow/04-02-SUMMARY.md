---
phase: 04-quiz-one-question-flow
plan: 02
status: complete
completed_at: "2026-03-23"
subsystem: quiz-ui
tags: [quiz, tdd, frontend, progress, accessibility]
dependency_graph:
  requires: [04-01]
  provides: [quiz-progress-dom-contract, quiz-step-ui]
  affects: [templates/quiz.html, static/css/quiz.css, static/js/quiz.js]
tech_stack:
  added: []
  patterns: [tdd-red-green, data-attribute-driven-animation, server-driven-navigation]
key_files:
  created:
    - tests/quizflow/test_quiz_progress_visibility.py
  modified:
    - templates/quiz.html
    - static/css/quiz.css
    - static/js/quiz.js
decisions:
  - "Progress bar width driven by JS reading data-pct on #progress-bar-fill instead of Jinja inline style"
  - "Removed all multi-question navigation JS (goToQuestion, timer, exit modal) — server handles all routing"
  - "Kept submit guard warning for empty selection (no option selected)"
  - "Added keyboard accessibility (tabindex + Enter/Space) on option labels"
metrics:
  duration: "~20 minutes"
  completed_date: "2026-03-23"
  tasks_completed: 2
  files_changed: 4
---

# Phase 04 Plan 02: Progress Visibility & One-Question UX Summary

## One-liner

Quiz template/CSS/JS refactored with explicit progress IDs, data-attribute-driven bar animation, and stale multi-question JS removed — all behind TDD progress visibility tests.

## What Was Built

### DOM Contract (quiz.html)

The quiz step template now exposes a fully-specified progress block:

```html
<div id="quiz-progress"
     data-answered="{{ answered_count }}"
     data-total="{{ total_questions }}"
     role="status" aria-live="polite" aria-atomic="false">
  <span>Câu <span id="progress-current">N</span> / <span id="progress-total">T</span></span>
  <div id="progress-bar-fill" role="progressbar"
       data-pct="…" aria-valuenow="…" aria-valuemin="0" aria-valuemax="…">
  </div>
</div>
```

Previously this section had no IDs — JS could not reliably target it and tests had nothing to assert against.

### CSS Change (quiz.css)

Added `.quiz-progress-track { height: 8px; }` to replace the `style="height: 8px;"` inline style that was on the Bootstrap `.progress` wrapper.

### JS Rewrite (quiz.js)

**Removed (~230 lines):**
- Multi-question nav: `goToQuestion()`, `changeQuestion()`, `updateNavState()`, `getTotalQuestions()`, `markAnswered()`, `markAnsweredInNav()`
- Timer: 15-min countdown, `updateTimer()`, `submitQuiz()`
- Exit modal: Bootstrap modal init, `#exitModal` / `#confirmExitBtn` listeners
- `window.onbeforeunload` warning
- `sessionStorage` start-time management

**Kept / Added (~65 lines):**
- Progress bar fill: reads `data-pct` → sets `fill.style.width` via `requestAnimationFrame`
- Option keyboard nav: `tabindex=0` + Enter/Space → `label.click()`
- Submit guard: warns if no radio selected; restores button label after 1.8s

## Tests Created

| File | Tests | Result |
|------|-------|--------|
| `tests/quizflow/test_quiz_progress_visibility.py` | 3 | 3/3 PASS |

- **Test 1**: `id="progress-current"` and `id="progress-total"` are present; spans hold correct values
- **Test 2**: `id="quiz-progress"` exists with `data-answered`, `data-total`, `aria-live`; `id="progress-bar-fill"` present
- **Test 3**: exactly one `.quiz-question-card` per step; no `q-block-` or `question-block` legacy patterns

Combined with Plan 04-01 tests: **11/11 PASS** in 0.42s

## Decisions Made

1. **JS sets width, not Jinja** — `style="width: …%"` in the template was replaced with `data-pct` + `fill.style.width` in `DOMContentLoaded`. This keeps the template clean and makes the bar animatable.
2. **No timer in the new flow** — step-by-step routing removes the need for a JS-driven countdown; each step is a full page load.
3. **Back button stays an anchor** — `<a href>` to the previous step URL. No JS needed; server handles state.
4. **Regex test adjusted for HTML spans** — progress text is now wrapped in `<span id="progress-current">1</span>` so the test matches against `id="progress-current"[^>]*>\s*1\s*</span>` instead of a raw text pattern.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Test regex did not account for HTML tags around progress numbers**
- **Found during:** Task 2 GREEN verification
- **Issue:** Test regex `r'Câu\s+1\s*/\s*\d+'` failed because the current step number is wrapped in `<span id="progress-current">` in the rendered HTML
- **Fix:** Updated regex pattern to match `id="progress-current"[^>]*>\s*1\s*</span>` — verifies both the ID contract and the value
- **Files modified:** `tests/quizflow/test_quiz_progress_visibility.py`
- **Commit:** `4b6d0e5`

## Self-Check: PASSED

- [x] `tests/quizflow/test_quiz_progress_visibility.py` exists
- [x] `templates/quiz.html` has `id="quiz-progress"`, `id="progress-current"`, `id="progress-total"`, `id="progress-bar-fill"`
- [x] `static/css/quiz.css` has `.quiz-progress-track`
- [x] `static/js/quiz.js` has no multi-Q stale logic; 65 lines total
- [x] 11/11 tests pass: `python -m unittest tests.quizflow.test_quiz_progress_visibility tests.quizflow.test_state_resume`

## Commits

- `e829d46` — test(04-02): add failing progress visibility tests for one-question quiz view
- `4b6d0e5` — feat(04-02): refactor quiz template/CSS/JS for one-question-per-step UI
