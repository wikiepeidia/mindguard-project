---
phase: 04
slug: quiz-one-question-flow
status: ready
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-20
---

# Phase 04 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python unittest |
| **Config file** | none |
| **Quick run command** | `python -m unittest tests/quizflow/test_quiz_step_flow.py -v` |
| **Full suite command** | `python -m unittest discover -s tests/quizflow -p "test_*.py" -v` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m unittest tests/quizflow/test_quiz_step_flow.py -v`
- **After every plan wave:** Run `python -m unittest discover -s tests/quizflow -p "test_*.py" -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | QUIZ-01, QUIZ-02 | unit/integration | `python -m unittest tests/quizflow/test_quiz_step_flow.py -v` | ✅ | ⬜ pending |
| 04-01-02 | 01 | 1 | QUIZ-03 | integration | `python -m unittest tests/quizflow/test_state_resume.py -v` | ✅ | ⬜ pending |
| 04-02-01 | 02 | 2 | QUIZ-04 | integration | `python -m unittest tests/quizflow/test_question_set_stability.py -v` | ✅ | ⬜ pending |
| 04-02-02 | 02 | 2 | QUIZ-01..03 | integration | `python -m unittest tests/quizflow/test_quiz_submission_contract.py -v` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/quizflow/test_quiz_step_flow.py` — one-question-per-page navigation + progress checks
- [ ] `tests/quizflow/test_state_resume.py` — refresh/back resume behavior
- [ ] `tests/quizflow/test_question_set_stability.py` — question set freeze by attempt
- [ ] `tests/quizflow/test_quiz_submission_contract.py` — result/certificate compatibility assertions

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Stepper clarity and cognitive load | QUIZ-01, QUIZ-02 | UX readability and pacing are subjective | Run quiz end-to-end on desktop/mobile and confirm one-question rhythm is clear |
| Back/refresh continuity perception | QUIZ-03 | Real browser behavior should be validated with user interactions | Navigate forward/back, refresh mid-attempt, verify user understands restored state |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-03-20
