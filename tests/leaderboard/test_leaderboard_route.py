"""Tests for /leaderboard route passing reporter_rankings template context.

Verifies that:
  1. GET /leaderboard returns HTTP 200 and the template context contains
     the 'reporter_rankings' key.
  2. reporter_rankings in context is a list.
"""

import unittest
from contextlib import contextmanager
from flask import template_rendered

from tests.leaderboard import LeaderboardTestBase


@contextmanager
def captured_templates(app):
    """Capture (template, context) pairs emitted during a request."""
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


class TestLeaderboardRoute(LeaderboardTestBase):
    """Leaderboard route template context contract."""

    def test_leaderboard_route_passes_reporter_rankings(self):
        """GET /leaderboard must return 200 and context must contain reporter_rankings."""
        with captured_templates(self.app) as templates:
            response = self.client.get('/leaderboard')

        self.assertEqual(response.status_code, 200,
                         "GET /leaderboard must return HTTP 200")
        self.assertTrue(len(templates) > 0,
                        "At least one template must be rendered")
        # Find leaderboard.html context
        context = templates[-1][1]
        self.assertIn('reporter_rankings', context,
                      "Template context must include 'reporter_rankings' key")

    def test_reporter_rankings_is_list(self):
        """reporter_rankings in leaderboard context must be a list."""
        with captured_templates(self.app) as templates:
            self.client.get('/leaderboard')

        context = templates[-1][1]
        self.assertIsInstance(context.get('reporter_rankings'), list,
                              "reporter_rankings must be a list instance")


if __name__ == '__main__':
    unittest.main()
