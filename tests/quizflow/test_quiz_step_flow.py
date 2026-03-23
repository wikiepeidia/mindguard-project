"""Tests for one-question-per-step quiz flow and PRG navigation.

These tests verify the new server-driven step behavior:
  - GET /quiz redirects to first step (not renders all questions).
  - GET /quiz/step/0 renders exactly ONE question in context.
  - POST /quiz/step/0 saves the answer in session and redirects to next step (PRG).
  - Reloading the step page keeps the same question order.

TDD note: these tests are written BEFORE the implementation so they
intentionally FAIL against the old /quiz route that renders all questions
at once and has no /quiz/step/* routes.
"""

import unittest
from unittest.mock import patch

from tests.quizflow import QuizFlowTestBase


class TestQuizStepFlow(QuizFlowTestBase):
    """One-question-per-step rendering and PRG navigation contract."""

    # ------------------------------------------------------------------ #
    # GET /quiz — entry point
    # ------------------------------------------------------------------ #

    @patch('routes.quiz.generate_dynamic_question', return_value=None)
    def test_get_quiz_redirects_to_first_step(self, _mock_ai):
        """GET /quiz must redirect to /quiz/step/0 (not render all questions)."""
        self._login()
        resp = self.client.get('/quiz', follow_redirects=False)

        self.assertEqual(resp.status_code, 302,
                         "GET /quiz must return 302 redirect to step 0")
        self.assertIn('/quiz/step/0', resp.location,
                      "Redirect target must be /quiz/step/0")

    # ------------------------------------------------------------------ #
    # GET /quiz/step/0 — view single question
    # ------------------------------------------------------------------ #

    @patch('routes.quiz.generate_dynamic_question', return_value=None)
    def test_step_0_renders_single_question(self, _mock_ai):
        """GET /quiz/step/0 renders the first question (one at a time)."""
        self._login()
        # Initialise attempt via entry point
        self.client.get('/quiz', follow_redirects=False)

        resp = self.client.get('/quiz/step/0')
        self.assertEqual(resp.status_code, 200,
                         "GET /quiz/step/0 must return 200")
        data = resp.data.decode('utf-8')
        self.assertIn('Câu 1', data,
                      "Step 0 response must contain 'Câu 1' (question number label)")

    # ------------------------------------------------------------------ #
    # POST /quiz/step/0 — submit answer
    # ------------------------------------------------------------------ #

    @patch('routes.quiz.generate_dynamic_question', return_value=None)
    def test_post_step_redirects_to_next_step(self, _mock_ai):
        """POST /quiz/step/0 must redirect to /quiz/step/1 (PRG pattern)."""
        self._login()
        self.client.get('/quiz', follow_redirects=False)

        with self.client.session_transaction() as s:
            q_id = s['quiz_attempt']['question_ids'][0]

        resp = self.client.post(
            '/quiz/step/0',
            data={f'q{q_id}': '0'},
            follow_redirects=False,
        )
        self.assertEqual(resp.status_code, 302,
                         "POST /quiz/step/0 must return 302 redirect")
        self.assertIn('/quiz/step/1', resp.location,
                      "POST step 0 must redirect to step 1")

    @patch('routes.quiz.generate_dynamic_question', return_value=None)
    def test_post_step_saves_answer_in_session(self, _mock_ai):
        """POST step answer must update session answers map with correct value."""
        self._login()
        self.client.get('/quiz', follow_redirects=False)

        with self.client.session_transaction() as s:
            q_id = s['quiz_attempt']['question_ids'][0]

        self.client.post(
            '/quiz/step/0',
            data={f'q{q_id}': '2'},
            follow_redirects=False,
        )

        with self.client.session_transaction() as s:
            answers = s['quiz_attempt']['answers']

        self.assertIn(str(q_id), answers,
                      "Session answers must contain submitted question ID")
        self.assertEqual(answers[str(q_id)], 2,
                         "Session must store the submitted option index (2)")

    # ------------------------------------------------------------------ #
    # Reload stability
    # ------------------------------------------------------------------ #

    @patch('routes.quiz.generate_dynamic_question', return_value=None)
    def test_reload_step_keeps_question_order(self, _mock_ai):
        """Two consecutive GET /quiz/step/0 calls must yield the same ordered IDs."""
        self._login()
        self.client.get('/quiz', follow_redirects=False)

        with self.client.session_transaction() as s:
            first_ids = list(s['quiz_attempt']['question_ids'])

        self.client.get('/quiz/step/0')  # reload

        with self.client.session_transaction() as s:
            second_ids = list(s['quiz_attempt']['question_ids'])

        self.assertEqual(first_ids, second_ids,
                         "Question order must not change between step reloads")


if __name__ == '__main__':
    unittest.main()
