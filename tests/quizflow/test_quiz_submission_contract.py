"""Regression tests for final quiz submission contract.

Test 1: POST last step + GET /quiz/finalize creates exactly ONE QuizResult row.
Test 2: After finalize session has last_quiz_score, max_quiz_score;
        certificate_code present on pass path, absent on fail path.
Test 3: After finalize, client is redirected to /quiz/result (fail) or /certificate (pass).

Both pass (high / perfect score) and fail (zero score) branches are exercised.
"""

import unittest
from unittest.mock import patch

from tests.quizflow import QuizFlowTestBase
from models import QuizResult
from utils.quiz_data import quiz_questions


# Correct-answer lookup for static questions: id -> 0-based option index
_ANSWER_MAP = {q['id']: q['answer'] for q in quiz_questions}


def _wrong_answer(qid):
    """Return an option index that is definitively wrong for this question.

    Uses (correct + 1) % 4 so the selection is always different from the
    correct answer, regardless of whether the correct answer is index 0.
    """
    correct = _ANSWER_MAP.get(qid, 0)
    return (correct + 1) % 4


class TestQuizSubmissionContract(QuizFlowTestBase):
    """Submission contract: one DB row, correct session keys, correct redirects."""

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _start_quiz(self):
        """Login and create a new quiz attempt. Returns (q_ids list, total int)."""
        self._login()
        self.client.get('/quiz', follow_redirects=False)
        with self.client.session_transaction() as s:
            q_ids = list(s['quiz_attempt']['question_ids'])
            total = s['quiz_attempt']['total_questions']
        return q_ids, total

    def _submit_all_answers(self, q_ids, answer_fn):
        """POST an answer to every quiz step using answer_fn(q_id) -> option index."""
        for idx, q_id in enumerate(q_ids):
            self.client.post(
                f'/quiz/step/{idx}',
                data={f'q{q_id}': str(answer_fn(q_id))},
                follow_redirects=False,
            )

    def _complete_quiz(self, answer_fn):
        """Full walk: login, start attempt, answer all steps, GET /quiz/finalize.

        Returns the redirect response from /quiz/finalize (follow_redirects=False).
        """
        q_ids, _total = self._start_quiz()
        self._submit_all_answers(q_ids, answer_fn)
        return self.client.get('/quiz/finalize', follow_redirects=False)

    # ------------------------------------------------------------------ #
    # Test 1: Exactly one QuizResult row after finalize
    # ------------------------------------------------------------------ #

    @patch('routes.quiz.generate_dynamic_question', return_value=None)
    def test_finalize_creates_exactly_one_quiz_result(self, _mock_ai):
        """Completing a quiz must write exactly ONE QuizResult row to the DB."""
        self.assertEqual(QuizResult.query.count(), 0, "DB starts empty")

        self._complete_quiz(_wrong_answer)  # all wrong → fail path

        self.assertEqual(
            QuizResult.query.count(), 1,
            "Finalize must create exactly one QuizResult (not zero, not two)",
        )

    @patch('routes.quiz.generate_dynamic_question', return_value=None)
    def test_finalize_refresh_does_not_duplicate_db_row(self, _mock_ai):
        """Calling /quiz/finalize a second time (refresh) must NOT add a second row."""
        self._complete_quiz(_wrong_answer)

        # Simulate browser refresh on finalize URL
        self.client.get('/quiz/finalize', follow_redirects=False)

        self.assertEqual(
            QuizResult.query.count(), 1,
            "Refreshing /quiz/finalize must not create a duplicate QuizResult",
        )

    # ------------------------------------------------------------------ #
    # Test 2: Session keys after finalize
    # ------------------------------------------------------------------ #

    @patch('routes.quiz.generate_dynamic_question', return_value=None)
    def test_fail_path_sets_score_session_keys(self, _mock_ai):
        """Fail path (all wrong): last_quiz_score=0, max_quiz_score>0; no certificate_code."""
        self._complete_quiz(_wrong_answer)

        with self.client.session_transaction() as s:
            self.assertIn('last_quiz_score', s,
                          "last_quiz_score must be in session after fail finalize")
            self.assertIn('max_quiz_score', s,
                          "max_quiz_score must be in session after fail finalize")
            self.assertEqual(s['last_quiz_score'], 0,
                             "All-wrong answers must yield score=0")
            self.assertGreater(s['max_quiz_score'], 0,
                               "max_quiz_score must be a positive integer")
            self.assertNotIn('certificate_code', s,
                             "certificate_code must NOT be set in session on fail path")

    @patch('routes.quiz.generate_dynamic_question', return_value=None)
    def test_pass_path_sets_certificate_code_in_session(self, _mock_ai):
        """Pass path (all correct): certificate_code, last_quiz_score, max_quiz_score all set."""
        self._complete_quiz(lambda qid: _ANSWER_MAP.get(qid, 0))

        with self.client.session_transaction() as s:
            self.assertIn('last_quiz_score', s,
                          "last_quiz_score must be in session after pass finalize")
            self.assertIn('max_quiz_score', s,
                          "max_quiz_score must be in session after pass finalize")
            self.assertIn('certificate_code', s,
                          "certificate_code must be in session after passing quiz")
            self.assertTrue(s['certificate_code'],
                            "certificate_code must not be empty")
            self.assertEqual(
                s['last_quiz_score'], s['max_quiz_score'],
                "All-correct answers must yield score == max_score",
            )

    # ------------------------------------------------------------------ #
    # Test 3: Redirect targets after finalize
    # ------------------------------------------------------------------ #

    @patch('routes.quiz.generate_dynamic_question', return_value=None)
    def test_fail_path_redirects_to_quiz_result(self, _mock_ai):
        """Fail path must redirect to /quiz/result."""
        resp = self._complete_quiz(_wrong_answer)

        self.assertEqual(resp.status_code, 302,
                         "Finalize must return 302 on fail path")
        self.assertIn('/quiz/result', resp.location,
                      "Fail path must redirect to /quiz/result")

    @patch('routes.quiz.generate_dynamic_question', return_value=None)
    def test_pass_path_redirects_to_certificate(self, _mock_ai):
        """Pass path must redirect to /certificate."""
        resp = self._complete_quiz(lambda qid: _ANSWER_MAP.get(qid, 0))

        self.assertEqual(resp.status_code, 302,
                         "Finalize must return 302 on pass path")
        self.assertIn('/certificate', resp.location,
                      "Pass path must redirect to /certificate")


if __name__ == '__main__':
    unittest.main()
