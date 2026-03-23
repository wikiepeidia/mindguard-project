---
phase: 04-quiz-one-question-flow
plan: 01
status: complete
completed_at: "2026-03-23"
---

# SUMMARY — Plan 04-01: Session-Backed One-Question Quiz Flow

## What Was Built

Refactored `routes/quiz.py` from a single-page multi-question renderer into a server-driven step machine. The quiz now presents exactly one question per route render, with stable session state across steps.

### New Route Architecture

| Route | Method | Behavior |
|-------|--------|----------|
| `/quiz` | GET | Start or resume attempt → redirect to current step |
| `/quiz/step/<idx>` | GET | Render single question at step idx |
| `/quiz/step/<idx>` | POST | Save answer → redirect to next step (PRG) |
| `/quiz/finalize` | GET | Compute score, write one QuizResult, redirect |
| `/quiz/result` | GET | Score summary (contract unchanged) |
| `/certificate` | GET | Certificate page (contract unchanged) |

### Session Envelope (`quiz_attempt`)

```python
{
    "question_ids": [int, ...],   # frozen order at attempt start
    "ai_q": dict | None,          # optional AI question (one max)
    "answers": {str(id): int},    # submitted option per question
    "current_index": int,
    "total_questions": int,
    "attempt_id": str,            # UUID deduplicates concurrent attempts
    "finalized": bool,            # guards against duplicate DB writes
}
```

## Tests Created

- `tests/quizflow/__init__.py` — package init
- `tests/quizflow/test_quiz_step_flow.py` — 5 tests covering step navigation, PRG, answer persistence
- `tests/quizflow/test_state_resume.py` — 3 tests covering refresh idempotency, back-navigation stability

**Test results:** 8/8 PASSED in 0.275s

## Key Decisions

- Stored only question IDs (not full objects) in session to stay within Flask signed-cookie ~4KB limit
- `finalized` flag guards `/quiz/finalize` against duplicate `QuizResult` writes on refresh
- AI question is stored separately as one dict (`ai_q`) and prepended to question set
- Existing `/quiz/result` and `/certificate` routes and their session key contracts preserved unchanged

## Files Modified

- `routes/quiz.py` — full rewrite with step lifecycle
- `tests/quizflow/__init__.py` — created
- `tests/quizflow/test_quiz_step_flow.py` — created
- `tests/quizflow/test_state_resume.py` — created

## Commits

- `a50ec2f` — test(04-01): add failing TDD tests for one-question quiz flow and state resume
- `99af27c` — feat(04-01): refactor quiz route to session-backed one-question step lifecycle
