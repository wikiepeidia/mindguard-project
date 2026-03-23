"""Tests for session resume stability: refresh and back-navigation.

These tests verify that:
  - Refreshing /quiz/finalize does NOT create a second QuizResult DB record.
  - Back-navigating to step 0 after step 1 keeps the same question order.
  - Previously submitted answers are preserved when revisiting an earlier step.

TDD note: these tests FAIL against the old /quiz route which has no step
or finalize routes and no session-backed attempt state.
"""

import unittest
from unittest.mock import patch

from tests.quizflow import QuizFlowTestBase
from models import QuizResult


class TestStateResume(QuizFlowTestBase):
    """Refresh / back-navigation stability contract."""

    # ------------------------------------------------------------------ #
    # Internal helper
    # ------------------------------------------------------------------ #

    def _answer_all_steps(self):
        """Submit answers for every step and follow last redirect to /quiz/finalize.

        Returns after the first GET /quiz/finalize has been executed (one
        QuizResult written, attempt marked finalized).
        """
        with self.client.session_transaction() as s:
            q_ids = list(s['quiz_attempt']['question_ids'])

        total = len(q_ids)
        for i, q_id in enumerate(q_ids):
            resp = self.client.post(
                f'/quiz/step/{i}',
                data={f'q{q_id}': '0'},
                follow_redirects=False,
            )
            if i == total - 1:
                # Last step must redirect to finalize
                self.assertEqual(resp.status_code, 302)
                self.assertIn('/quiz/finalize', resp.location)

        # Execute the finalize GET (writes one QuizResult)
        self.client.get('/quiz/finalize', follow_redirects=False)

    # ------------------------------------------------------------------ #
    # Duplicate-write guard
    # ------------------------------------------------------------------ #

    @patch('routes.quiz.generate_dynamic_question', return_value=None)
    def test_refresh_finalize_does_not_duplicate_db_write(self, _mock_ai):
        """Refreshing /quiz/finalize must not create a second QuizResult row."""
        self._login()
        self.client.get('/quiz', follow_redirects=False)
        self._answer_all_steps()

        count_after_first = QuizResult.query.count()
        self.assertEqual(count_after_first, 1,
                         "Exactly one QuizResult must be written after first finalize")

        # Second GET — should redirect immediately without writing
        self.client.get('/quiz/finalize', follow_redirects=False)
        count_after_refresh = QuizResult.query.count()

        self.assertEqual(count_after_refresh, count_after_first,
                         "Second GET /quiz/finalize must NOT create another QuizResult")

    # ------------------------------------------------------------------ #
    # Back-navigation order stability
    # ------------------------------------------------------------------ #

    @patch('routes.quiz.generate_dynamic_question', return_value=None)
    def test_back_navigation_preserves_question_order(self, _mock_ai):
        """Navigating back to step 0 must not randomise the question sequence."""
        self._login()
        self.client.get('/quiz', follow_redirects=False)

        with self.client.session_transaction() as s:
            original_ids = list(s['quiz_attempt']['question_ids'])
            q0_id = original_ids[0]

        # Submit step 0 then navigate back
        self.client.post('/quiz/step/0', data={f'q{q0_id}': '0'},
                         follow_redirects=False)
        resp = self.client.get('/quiz/step/0')

        self.assertEqual(resp.status_code, 200)

        with self.client.session_transaction() as s:
            current_ids = list(s['quiz_attempt']['question_ids'])

        self.assertEqual(original_ids, current_ids,
                         "Question IDs must remain in original order after back navigation")

    # ------------------------------------------------------------------ #
    # Back-navigation answer preservation
    # ------------------------------------------------------------------ #

    @patch('routes.quiz.generate_dynamic_question', return_value=None)
    def test_back_navigation_restores_selected_answer(self, _mock_ai):
        """Returning to a previously answered step must keep the stored answer."""
        self._login()
        self.client.get('/quiz', follow_redirects=False)

        with self.client.session_transaction() as s:
            q_id = s['quiz_attempt']['question_ids'][0]

        # Submit step 0 with option index 3
        self.client.post('/quiz/step/0', data={f'q{q_id}': '3'},
                         follow_redirects=False)

        # Navigate back to step 0 (GET)
        resp = self.client.get('/quiz/step/0')
        self.assertEqual(resp.status_code, 200)

        with self.client.session_transaction() as s:
            stored = s['quiz_attempt']['answers'].get(str(q_id))

        self.assertEqual(stored, 3,
                         "Answer submitted for step 0 must be preserved in session")


if __name__ == '__main__':
    unittest.main()
