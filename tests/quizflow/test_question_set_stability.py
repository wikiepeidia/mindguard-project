"""Regression tests for question-set stability and schema completeness.

TDD RED: test_all_questions_have_required_fields fails before topic is added.

Test 1: Attempt question IDs stay unchanged across refresh/back within one attempt.
Test 2: Every served question has all required fields: id, question, options, answer, topic.
Test 3: Questions have at least 4 options each.
"""

import unittest
from unittest.mock import patch

from tests.quizflow import QuizFlowTestBase
from utils.quiz_data import quiz_questions


class TestQuestionSetStability(QuizFlowTestBase):
    """Question-set freeze, schema completeness, and option count checks."""

    # ------------------------------------------------------------------ #
    # Test 1: Question IDs frozen within one attempt (refresh / back safe)
    # ------------------------------------------------------------------ #

    @patch('routes.quiz.generate_dynamic_question', return_value=None)
    def test_question_ids_frozen_across_refresh(self, _mock_ai):
        """Question IDs must remain identical across repeated GET /quiz/step/0 calls."""
        self._login()
        self.client.get('/quiz', follow_redirects=False)

        with self.client.session_transaction() as s:
            ids_before = list(s['quiz_attempt']['question_ids'])

        # Simulate back-navigation and page refresh
        self.client.get('/quiz/step/0')
        self.client.get('/quiz/step/0')

        with self.client.session_transaction() as s:
            ids_after = list(s['quiz_attempt']['question_ids'])

        self.assertEqual(
            ids_before, ids_after,
            "question_ids must not change between step views within one attempt",
        )

    # ------------------------------------------------------------------ #
    # Test 2: Every question in quiz_questions has all required fields
    # ------------------------------------------------------------------ #

    def test_all_questions_have_required_fields(self):
        """Each question dict must contain: id, question, options, answer, topic.

        This test FAILS before topic metadata is added to quiz_data.py (TDD RED).
        """
        required = {'id', 'question', 'options', 'answer', 'topic'}
        for q in quiz_questions:
            missing = required - set(q.keys())
            self.assertFalse(
                missing,
                f"Question id={q.get('id', '?')} is missing fields: {missing}",
            )

    # ------------------------------------------------------------------ #
    # Test 3: Every question has at least 4 answer options
    # ------------------------------------------------------------------ #

    def test_questions_have_at_least_four_options(self):
        """Each question must have at least 4 answer options."""
        for q in quiz_questions:
            count = len(q.get('options', []))
            self.assertGreaterEqual(
                count, 4,
                f"Question id={q.get('id', '?')} has only {count} options",
            )

    # ------------------------------------------------------------------ #
    # Test 4: Quiz bank has at least 25 questions
    # ------------------------------------------------------------------ #

    def test_question_bank_has_at_least_25_questions(self):
        """quiz_questions must contain at least 25 questions after expansion."""
        self.assertGreaterEqual(
            len(quiz_questions), 25,
            f"Expected at least 25 questions, got {len(quiz_questions)}",
        )

    # ------------------------------------------------------------------ #
    # Test 5: All question IDs are unique
    # ------------------------------------------------------------------ #

    def test_question_ids_are_unique(self):
        """Every question must have a unique numeric ID."""
        ids = [q.get('id') for q in quiz_questions]
        self.assertEqual(len(ids), len(set(ids)),
                         "Duplicate question IDs detected in quiz_questions")


if __name__ == '__main__':
    unittest.main()
