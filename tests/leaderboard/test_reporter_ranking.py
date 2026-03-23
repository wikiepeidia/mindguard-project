"""Tests for reporter ranking query and integrity scoring service.

TDD RED phase: These tests are written BEFORE services/leaderboard_integrity.py
exists, so they fail with ImportError on the first run.

Test cases:
  1. Empty DB returns empty list.
  2. Reporter with more approved reports ranks higher.
  3. Reporter in cooldown is excluded from rankings.
  4. Verified reports contribute more integrity_score than unverified.
"""

import unittest
from datetime import datetime, timedelta

from tests.leaderboard import LeaderboardTestBase
from extensions import db
from models import ScammerReport, AntiSpamActorState
from services.leaderboard_integrity import get_reporter_rankings


class TestReporterRanking(LeaderboardTestBase):
    """Reporter ranking query and integrity score contract."""

    # ------------------------------------------------------------------ #
    # Helper
    # ------------------------------------------------------------------ #

    def _make_report(self, reporter_hash, status='approved', verification_status='unverified'):
        """Create and persist a ScammerReport fixture."""
        r = ScammerReport(
            scammer_identifier='test-scammer-001',
            scam_type='lua_dao',
            description='Mo ta lua dao',
            reporter_hash=reporter_hash,
            status=status,
            verification_status=verification_status,
        )
        db.session.add(r)
        db.session.commit()
        return r

    def _make_cooldown_state(self, reporter_hash, hours_ahead=1):
        """Create an AntiSpamActorState that puts reporter_hash in cooldown."""
        state = AntiSpamActorState(
            actor_key=f'cookie:{reporter_hash}',
            actor_type='cookie',
            reporter_hash=reporter_hash,
            cooldown_until=datetime.utcnow() + timedelta(hours=hours_ahead),
            window_count=5,
            last_seen_at=datetime.utcnow(),
        )
        db.session.add(state)
        db.session.commit()
        return state

    # ------------------------------------------------------------------ #
    # Test 1: Empty DB
    # ------------------------------------------------------------------ #

    def test_reporter_ranking_empty_db(self):
        """Empty database returns an empty reporter rankings list."""
        result = get_reporter_rankings()
        self.assertIsInstance(result, list,
                              "get_reporter_rankings() must return a list")
        self.assertEqual(len(result), 0,
                         "Empty DB must produce empty rankings list")

    # ------------------------------------------------------------------ #
    # Test 2: Approved count determines rank order
    # ------------------------------------------------------------------ #

    def test_reporter_ranking_ordered_by_approved(self):
        """Reporter with more approved reports ranks higher."""
        # Reporter A: 3 approved reports
        for _ in range(3):
            self._make_report('aaaaaaaabbbbbbbbccccccccdddddddd', status='approved')

        # Reporter B: 1 approved report
        self._make_report('zzzzzzzz11111111yyyyyyyyxxxxxxxx', status='approved')

        result = get_reporter_rankings()

        self.assertGreaterEqual(len(result), 2,
                                "Must have at least 2 reporters in rankings")
        scores = [r['integrity_score'] for r in result]
        # Scores must be in descending order
        self.assertEqual(scores, sorted(scores, reverse=True),
                         "Rankings must be ordered by integrity_score descending")
        # Top reporter should be hash_a (3 approved > 1 approved)
        self.assertEqual(result[0]['reporter_hash_display'],
                         'aaaaaaaabbbbbbbbccccccccdddddddd'[:8],
                         "Reporter with 3 approved reports should be ranked first")

    # ------------------------------------------------------------------ #
    # Test 3: Cooldown exclusion
    # ------------------------------------------------------------------ #

    def test_reporter_ranking_excludes_cooldown_actor(self):
        """Reporter currently in cooldown must be excluded from rankings."""
        # Normal reporter — 2 approved reports
        normal_hash = 'normalreporter0000000000000000ab'
        for _ in range(2):
            self._make_report(normal_hash, status='approved')

        # Flagged reporter — 5 approved reports but in cooldown
        flagged_hash = 'flaggedreporter000000000000000cd'
        for _ in range(5):
            self._make_report(flagged_hash, status='approved')
        self._make_cooldown_state(flagged_hash)

        result = get_reporter_rankings()

        displayed_hashes = [r['reporter_hash_display'] for r in result]
        self.assertNotIn(
            flagged_hash[:8], displayed_hashes,
            "Reporter in cooldown must not appear in rankings"
        )
        self.assertIn(
            normal_hash[:8], displayed_hashes,
            "Normal reporter must appear in rankings"
        )

    # ------------------------------------------------------------------ #
    # Test 4: Verified reports add bonus to integrity_score
    # ------------------------------------------------------------------ #

    def test_reporter_ranking_weights_verified_higher(self):
        """Verified reports contribute more to integrity_score than unverified."""
        # Reporter D: 2 approved, unverified reports
        hash_d = 'dddddddddddddddddddddddddddddddd'
        for _ in range(2):
            self._make_report(hash_d, status='approved', verification_status='unverified')

        # Reporter E: 2 approved, verified reports (same count but verified bonus)
        hash_e = 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
        for _ in range(2):
            self._make_report(hash_e, status='approved', verification_status='verified')

        result = get_reporter_rankings()

        self.assertGreaterEqual(len(result), 2,
                                "Must have at least 2 reporters in results")

        score_d = next(r['integrity_score'] for r in result
                       if r['reporter_hash_display'] == hash_d[:8])
        score_e = next(r['integrity_score'] for r in result
                       if r['reporter_hash_display'] == hash_e[:8])

        self.assertGreater(score_e, score_d,
                           "Verified reporter (E) must have higher integrity_score than "
                           "unverified reporter (D) with same approved count")


if __name__ == '__main__':
    unittest.main()
