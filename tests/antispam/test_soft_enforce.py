import unittest
from datetime import datetime

from flask import Flask

from extensions import db
from models import AntiSpamEvent, Registration, ScammerReport
from routes.scammer import scammer_bp
from utils.encryption import hash_reporter_id


class TestSoftEnforceReportRoute(unittest.TestCase):
    def setUp(self):
        project_root = __import__("pathlib").Path(__file__).resolve().parents[2]
        self.app = Flask(__name__, template_folder=str(project_root / "templates"))
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "test-secret"
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config["ABUS_MODE"] = "soft_enforce"
        self.app.config["ABUS_THRESHOLD_COUNT"] = 2
        self.app.config["ABUS_WINDOW_MINUTES"] = 10
        self.app.config["ABUS_COOLDOWN_MINUTES"] = 15
        self.app.config["ABUS_ACCOUNT_WEIGHT"] = 70
        self.app.config["ABUS_COOKIE_WEIGHT"] = 20
        self.app.config["ABUS_IP_WEIGHT"] = 10
        self.app.config["CLOUDFLARE_SECRET_KEY"] = None
        self.app.config["CLOUDFLARE_SITE_KEY"] = ""
        self.app.config["REPORT_ENCRYPTION_KEY"] = "test-key"

        db.init_app(self.app)
        self.app.register_blueprint(scammer_bp)

        with self.app.app_context():
            db.create_all()

        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _base_payload(self, description):
        return {
            "math_answer": "7",
            "term_truth": "on",
            "term_responsibility": "on",
            "report_type": "general",
            "identifier_person": "0911222333",
            "scam_type_person": "Lừa đảo khác",
            "description": description,
        }

    def test_soft_enforce_blocks_submit_when_cooldown_active_and_prevents_new_report_write(self):
        with self.client.session_transaction() as sess:
            sess["math_captcha_answer_report"] = "7"
            sess["reporter_id"] = "reporter-soft"

        first = self.client.post(
            "/scammer/report",
            data=self._base_payload("First submit"),
            headers={"X-Forwarded-For": "203.0.113.11"},
            follow_redirects=False,
        )
        self.assertEqual(first.status_code, 302)
        first.close()

        with self.client.session_transaction() as sess:
            sess["math_captcha_answer_report"] = "7"

        second = self.client.post(
            "/scammer/report",
            data=self._base_payload("Second submit should be blocked"),
            headers={"X-Forwarded-For": "203.0.113.11"},
            follow_redirects=False,
        )
        self.assertEqual(second.status_code, 302)
        second.close()

        with self.app.app_context():
            self.assertEqual(ScammerReport.query.count(), 1)
            self.assertEqual(AntiSpamEvent.query.count(), 2)
            latest_event = AntiSpamEvent.query.order_by(AntiSpamEvent.id.desc()).first()
            self.assertIsNotNone(latest_event)
            self.assertTrue(latest_event.triggered_cooldown)

    def test_soft_enforce_does_not_block_clean_account_when_only_cookie_ip_are_medium_risk(self):
        hashed_cookie = hash_reporter_id("cookie-bad")
        with self.app.app_context():
            user = Registration(name="User", email="clean@example.com", password_hash="x")
            db.session.add(user)
            db.session.flush()

            now = datetime.utcnow()
            db.session.add_all(
                [
                    AntiSpamEvent(
                        actor_key=f"cookie:{hashed_cookie}",
                        actor_type="cookie",
                        reporter_hash=hashed_cookie,
                        ip_address="198.51.100.2",
                        risk_score=30,
                        risk_level="medium",
                        window_count=2,
                        triggered_cooldown=False,
                        occurred_at=now,
                    ),
                    AntiSpamEvent(
                        actor_key=f"cookie:{hashed_cookie}",
                        actor_type="cookie",
                        reporter_hash=hashed_cookie,
                        ip_address="198.51.100.2",
                        risk_score=30,
                        risk_level="medium",
                        window_count=3,
                        triggered_cooldown=False,
                        occurred_at=now,
                    ),
                    AntiSpamEvent(
                        actor_key="ip:198.51.100.2",
                        actor_type="ip",
                        reporter_hash=hashed_cookie,
                        ip_address="198.51.100.2",
                        risk_score=30,
                        risk_level="medium",
                        window_count=2,
                        triggered_cooldown=False,
                        occurred_at=now,
                    ),
                    AntiSpamEvent(
                        actor_key="ip:198.51.100.2",
                        actor_type="ip",
                        reporter_hash=hashed_cookie,
                        ip_address="198.51.100.2",
                        risk_score=30,
                        risk_level="medium",
                        window_count=3,
                        triggered_cooldown=False,
                        occurred_at=now,
                    ),
                ]
            )
            db.session.commit()

        with self.client.session_transaction() as sess:
            sess["math_captcha_answer_report"] = "7"
            sess["reporter_id"] = "cookie-bad"
            sess["registration_email"] = "clean@example.com"

        response = self.client.post(
            "/scammer/report",
            data=self._base_payload("Clean account submit"),
            headers={"X-Forwarded-For": "198.51.100.2"},
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        response.close()

        with self.app.app_context():
            self.assertEqual(ScammerReport.query.count(), 1)
            latest_event = AntiSpamEvent.query.order_by(AntiSpamEvent.id.desc()).first()
            self.assertIsNotNone(latest_event)
            self.assertEqual(latest_event.actor_key, "acct:1")
            self.assertEqual(latest_event.risk_level, "medium")
            self.assertFalse(latest_event.triggered_cooldown)


if __name__ == "__main__":
    unittest.main()