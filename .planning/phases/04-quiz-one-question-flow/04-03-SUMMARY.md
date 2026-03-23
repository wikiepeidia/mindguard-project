---
phase: 04-quiz-one-question-flow
plan: "03"
subsystem: quiz
tags: [quiz, data, tdd, regression-tests, topic-metadata]
dependency_graph:
  requires: [04-01, 04-02]
  provides: [expanded-quiz-bank, topic-schema, submission-contract-tests]
  affects: [utils/quiz_data.py, routes/quiz.py, tests/quizflow]
tech_stack:
  added: []
  patterns: [TDD red-green, topic normalization, session contract testing]
key_files:
  created:
    - tests/quizflow/test_question_set_stability.py
    - tests/quizflow/test_quiz_submission_contract.py
  modified:
    - utils/quiz_data.py
    - routes/quiz.py
decisions:
  - "_wrong_answer helper uses (correct+1)%4 to avoid Q8 answer=0 false-positive in fail-path test"
  - "Topic normalization applied in both _create_attempt (ai_q payload) and _get_question (static fallback)"
  - "5 new questions cover network_security (VPN, public WiFi), password_security (2FA, password manager), data_privacy (social media oversharing)"
metrics:
  duration: "~20 minutes"
  completed_date: "2026-03-23"
  tasks_completed: 2
  files_changed: 4
requirements: [QUIZ-04, QUIZ-01, QUIZ-02, QUIZ-03]
---

# Phase 04 Plan 03: Quiz Bank Expansion & Submission Contract — Summary

**One-liner:** Topic-tagged 25-question bank with TDD regression suite covering schema contract and finalize idempotency.

## What Was Built

### Task 1 — TDD Regression Tests (RED → committed, then GREEN after Task 2)

**`tests/quizflow/test_question_set_stability.py`** (5 tests):
- `test_question_ids_frozen_across_refresh` — verifies session question_ids are unchanged across GET /quiz/step/0 calls
- `test_all_questions_have_required_fields` — asserts every question has `id, question, options, answer, topic` (TDD RED driver)
- `test_questions_have_at_least_four_options` — asserts ≥ 4 options per question
- `test_question_bank_has_at_least_25_questions` — asserts quiz_questions ≥ 25 entries (TDD RED driver)
- `test_question_ids_are_unique` — asserts no duplicate IDs

**`tests/quizflow/test_quiz_submission_contract.py`** (6 tests):
- `test_finalize_creates_exactly_one_quiz_result` — DB row count = 1 after full walk
- `test_finalize_refresh_does_not_duplicate_db_row` — second GET /quiz/finalize does not add second row
- `test_fail_path_sets_score_session_keys` — score=0, max_score>0, no certificate_code in session
- `test_pass_path_sets_certificate_code_in_session` — all correct → certificate_code + matching max score
- `test_fail_path_redirects_to_quiz_result` — fail redirect → /quiz/result
- `test_pass_path_redirects_to_certificate` — pass redirect → /certificate

### Task 2 — Quiz Bank Expansion + Route Normalization (GREEN)

**`utils/quiz_data.py`:**
- Added `"topic"` field to all 20 existing questions
- Topics assigned: `phishing` (Q2, Q6, Q16, Q19), `scam_awareness` (Q1, Q3, Q7, Q10, Q12, Q15, Q18, Q20), `social_engineering` (Q4, Q5, Q8, Q17), `data_privacy` (Q9, Q13, Q14), `password_security` (Q11)
- Added 5 new questions (IDs 21-25):
  - Q21 `network_security` — Public Wi-Fi login risks
  - Q22 `password_security` — Two-factor authentication (2FA)
  - Q23 `network_security` — VPN benefits
  - Q24 `data_privacy` — Social media oversharing
  - Q25 `password_security` — Password manager benefits
- **Total: 25 questions**, all normalized with required fields

**`routes/quiz.py`:**
- `_create_attempt()`: AI question payload now stores `'topic': ai_q.get('topic', 'general')`
- `_get_question()`: static question return includes `'topic': q.get('topic', 'general')` as safety net

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fail-path test `answer_fn` triggered false correct answer on Q8**
- **Found during:** Task 1 test authoring
- **Issue:** `lambda qid: 0` submitted option index 0, but Q8 has `"answer": 0`, scoring 1 point on the "all wrong" pass. This made `test_fail_path_sets_score_session_keys` fail for the wrong reason.
- **Fix:** Introduced `_wrong_answer(qid)` helper using `(correct + 1) % 4`, guaranteeing a wrong answer regardless of which index is correct.
- **Files modified:** `tests/quizflow/test_quiz_submission_contract.py`
- **Committed inline** before Task 1 test commit.

## Test Results

```
Ran 22 tests in 0.558s
OK
```

Full quizflow suite: **22/22 passing** — all pre-existing tests (04-01, 04-02) remain green.

## Commits

| Hash    | Type | Description                                               |
|---------|------|-----------------------------------------------------------|
| f5f8b2a | test | Task 1: Add failing stability + submission-contract tests |
| b2099ee | feat | Task 2: Expand quiz bank to 25Q + normalize topic field   |

## Self-Check

- [x] `tests/quizflow/test_question_set_stability.py` exists and passes
- [x] `tests/quizflow/test_quiz_submission_contract.py` exists and passes
- [x] `utils/quiz_data.py` has 25 questions with topic on all
- [x] `routes/quiz.py` normalizes topic in `_create_attempt` and `_get_question`
- [x] `python -m unittest discover -s tests/quizflow -p "test_*.py" -v` → 22 tests OK
- [x] Commits f5f8b2a and b2099ee exist

## Self-Check: PASSED
