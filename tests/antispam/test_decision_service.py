import unittest
from datetime import datetime, timedelta

from flask import Flask

from extensions import db


class TestAntiSpamDecisionService(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        db.init_app(self.app)

        with self.app.app_context():
            from models import AntiSpamActorState, AntiSpamEvent  # noqa: F401

            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_third_submission_in_10_minutes_triggers_15_minute_cooldown(self):
        from services.anti_spam import AntiSpamDecisionService

        service = AntiSpamDecisionService(
            window_minutes=10,
            threshold_count=3,
            cooldown_minutes=15,
        )

        start = datetime(2026, 3, 20, 10, 0, 0)

        with self.app.app_context():
            first = service.evaluate_submission(
                account_id="acc-01",
                reporter_hash="cookie-a",
                ip_address="10.0.0.1",
                submitted_at=start,
                signal_inputs={"account": 0, "cookie": 0, "ip": 0},
            )
            second = service.evaluate_submission(
                account_id="acc-01",
                reporter_hash="cookie-a",
                ip_address="10.0.0.1",
                submitted_at=start + timedelta(minutes=1),
                signal_inputs={"account": 0, "cookie": 0, "ip": 0},
            )
            third = service.evaluate_submission(
                account_id="acc-01",
                reporter_hash="cookie-a",
                ip_address="10.0.0.1",
                submitted_at=start + timedelta(minutes=2),
                signal_inputs={"account": 0, "cookie": 0, "ip": 0},
            )

        self.assertFalse(first.should_cooldown)
        self.assertFalse(second.should_cooldown)
        self.assertTrue(third.should_cooldown)
        self.assertEqual(third.actor_key, "acct:acc-01")
        self.assertEqual(third.window_count, 3)
        self.assertEqual(third.cooldown_until, start + timedelta(minutes=17))


if __name__ == "__main__":
    unittest.main()
