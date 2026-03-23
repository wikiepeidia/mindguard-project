"""Regression tests for progress/status visibility in the one-question quiz view.

DOM contract that must be satisfied by quiz.html after Plan 04-02:
  - id="quiz-progress"   : progress container with aria-live and data attr
  - id="progress-current": span holding current 1-based step number
  - id="progress-total"  : span holding total question count
  - id="progress-bar-fill": fill element for the animated progress bar
  - EXACTLY one .quiz-question-card element per step (no multi-Q blocks)
  - NO legacy id patterns: q-block-*, question-block

TDD note: these tests FAIL against the old quiz.html which lacks these IDs.
They pass after Task 2 refactors the template.
"""

import re
import unittest
from unittest.mock import patch

from tests.quizflow import QuizFlowTestBase


class TestQuizProgressVisibility(QuizFlowTestBase):
    """Progress and status DOM contract for the one-question quiz step view."""

    # ------------------------------------------------------------------ #
    # Shared helper
    # ------------------------------------------------------------------ #

    def _start_and_get_step_0(self):
        """Login, initialise attempt via GET /quiz, return GET /quiz/step/0 response."""
        self._login()
        self.client.get('/quiz', follow_redirects=False)
        return self.client.get('/quiz/step/0')

    # ------------------------------------------------------------------ #
    # Test 1: Explicit current/total progress labels
    # ------------------------------------------------------------------ #

    @patch('routes.quiz.generate_dynamic_question', return_value=None)
    def test_progress_labels_show_current_and_total(self, _mock_ai):
        """Step page must include id=progress-current and id=progress-total
        labels that together render the 'Câu X / Y' pattern."""
        resp = self._start_and_get_step_0()
        self.assertEqual(resp.status_code, 200)
        body = resp.data.decode('utf-8')

        self.assertIn(
            'id="progress-current"', body,
            "Must have id='progress-current' element for current step number",
        )
        self.assertIn(
            'id="progress-total"', body,
            "Must have id='progress-total' element for total question count",
        )
        # Rendered text must match Vietnamese progress pattern "Câu 1 / <N>"
        self.assertRegex(
            body,
            r'Câu\s+1\s*/\s*\d+',
            "Rendered page must show 'Câu 1 / <N>' progress label",
        )

    # ------------------------------------------------------------------ #
    # Test 2: Progress bar container with aria/data attributes
    # ------------------------------------------------------------------ #

    @patch('routes.quiz.generate_dynamic_question', return_value=None)
    def test_progress_bar_container_exists_with_aria_and_data(self, _mock_ai):
        """Step page must include id=quiz-progress container with aria-live,
        data-answered, data-total attributes, and id=progress-bar-fill element."""
        resp = self._start_and_get_step_0()
        self.assertEqual(resp.status_code, 200)
        body = resp.data.decode('utf-8')

        self.assertIn(
            'id="quiz-progress"', body,
            "Progress wrapper must carry id='quiz-progress'",
        )
        self.assertIn(
            'id="progress-bar-fill"', body,
            "Progress bar fill must carry id='progress-bar-fill'",
        )
        self.assertIn(
            'data-answered', body,
            "Progress container must expose data-answered attribute for JS",
        )
        self.assertIn(
            'data-total', body,
            "Progress container must expose data-total attribute for JS",
        )
        self.assertIn(
            'aria-live', body,
            "Progress region must declare aria-live for screen readers",
        )

    # ------------------------------------------------------------------ #
    # Test 3: Single question card per step render
    # ------------------------------------------------------------------ #

    @patch('routes.quiz.generate_dynamic_question', return_value=None)
    def test_single_question_card_per_step(self, _mock_ai):
        """Step page must render EXACTLY one question card and must NOT
        contain any legacy multi-question block identifiers."""
        resp = self._start_and_get_step_0()
        self.assertEqual(resp.status_code, 200)
        body = resp.data.decode('utf-8')

        card_count = body.count('quiz-question-card')
        self.assertEqual(
            card_count, 1,
            f"Exactly one quiz-question-card must appear per step, got {card_count}",
        )
        self.assertNotIn(
            'q-block-', body,
            "Legacy q-block-N IDs must not appear in the template",
        )
        self.assertNotIn(
            'question-block', body,
            "Legacy question-block class must not appear in the template",
        )
