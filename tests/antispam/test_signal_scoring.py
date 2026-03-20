import unittest

from services.anti_spam import AntiSpamDecisionService


class TestAntiSpamSignalScoring(unittest.TestCase):
    def setUp(self):
        self.service = AntiSpamDecisionService(
            account_weight=70,
            cookie_weight=20,
            ip_weight=10,
        )

    def test_account_signal_overrides_cookie_and_ip_for_actor_key(self):
        actor_key = self.service.canonicalize_actor(
            account_id="acc-123",
            reporter_hash="cookie-xyz",
            ip_address="192.168.1.9",
        )
        self.assertEqual(actor_key, "acct:acc-123")

    def test_score_tiers_map_to_low_medium_high(self):
        low = self.service.calculate_score(account_signal=0, cookie_signal=0, ip_signal=0)
        medium = self.service.calculate_score(account_signal=0, cookie_signal=1, ip_signal=1)
        high = self.service.calculate_score(account_signal=1, cookie_signal=1, ip_signal=1)

        self.assertEqual(low, 0)
        self.assertEqual(self.service.map_risk_level(low), "low")
        self.assertEqual(medium, 30)
        self.assertEqual(self.service.map_risk_level(medium), "medium")
        self.assertEqual(high, 100)
        self.assertEqual(self.service.map_risk_level(high), "high")


if __name__ == "__main__":
    unittest.main()
