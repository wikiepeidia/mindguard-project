"""DOM contract tests for reporter honor roll section.

Verifies that /leaderboard HTML contains required identifiers for the
reporter honor roll UI: section wrapper, table, rank column, score column,
and trust tier badge.

Tests follow RED-GREEN TDD pattern:
  RED  (Task 1): Template lacks reporter section → 5 tests fail.
  GREEN (Task 4): Reporter section added → 5 tests pass.
"""

import unittest
from tests.leaderboard import LeaderboardTestBase


class TestReporterUiContract(LeaderboardTestBase):
    """DOM contract: reporter honor roll section must exist on /leaderboard."""

    def _get_leaderboard_html(self) -> str:
        """Fetch /leaderboard and return decoded HTML body."""
        response = self.client.get('/leaderboard')
        self.assertEqual(
            response.status_code, 200,
            "GET /leaderboard must return HTTP 200",
        )
        return response.data.decode('utf-8')

    def test_reporter_section_exists(self):
        """Leaderboard page must contain a section with id='reporter-leaderboard'."""
        html = self._get_leaderboard_html()
        self.assertIn(
            'id="reporter-leaderboard"', html,
            "Expected id='reporter-leaderboard' wrapper div in leaderboard page",
        )

    def test_reporter_table_headers(self):
        """Leaderboard page must contain a table with id='reporter-table'."""
        html = self._get_leaderboard_html()
        self.assertIn(
            'id="reporter-table"', html,
            "Expected id='reporter-table' element in leaderboard page",
        )

    def test_reporter_rank_column(self):
        """Reporter table must use 'reporter-rank' CSS class on rank cells."""
        html = self._get_leaderboard_html()
        self.assertIn(
            'reporter-rank', html,
            "Expected 'reporter-rank' class marker in leaderboard page HTML",
        )

    def test_reporter_score_column(self):
        """Reporter table must use 'reporter-score' CSS class on score cells."""
        html = self._get_leaderboard_html()
        self.assertIn(
            'reporter-score', html,
            "Expected 'reporter-score' class marker in leaderboard page HTML",
        )

    def test_integrity_badge_exists(self):
        """Reporter table must use 'reporter-integrity-badge' CSS class for trust tier."""
        html = self._get_leaderboard_html()
        self.assertIn(
            'reporter-integrity-badge', html,
            "Expected 'reporter-integrity-badge' class in leaderboard page HTML",
        )


if __name__ == '__main__':
    unittest.main()
