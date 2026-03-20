import unittest

from flask import Flask

from extensions import db
from models import Registration, ScammerReport
from routes.scammer import scammer_bp


class TestAntiSpamUserFeedback(unittest.TestCase):
    def setUp(self):
        project_root = __import__("pathlib").Path(__file__).resolve().parents[2]
        self.app = Flask(__name__, template_folder=str(project_root / "templates"))
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "test-secret"
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config["ABUS_WINDOW_MINUTES"] = 10
        self.app.config["ABUS_THRESHOLD_COUNT"] = 1
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

    def _get_flash_messages(self):
        with self.client.session_transaction() as sess:
            flashes = sess.get("_flashes", [])
        return [message for _category, message in flashes]

    def test_soft_enforce_feedback_contains_reason_and_remaining_minutes(self):
        self.app.config["ABUS_MODE"] = "soft_enforce"

        with self.app.app_context():
            db.session.add(Registration(name="A", email="a@example.com", password_hash="x"))
            db.session.commit()

        with self.client.session_transaction() as sess:
            sess["math_captcha_answer_report"] = "7"
            sess["reporter_id"] = "reporter-feedback-soft"
            sess["registration_email"] = "a@example.com"

        response = self.client.post(
            "/scammer/report",
            data=self._base_payload("Soft enforce should explain cooldown"),
            headers={"X-Forwarded-For": "203.0.113.9"},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        response.close()

        with self.app.app_context():
            self.assertEqual(ScammerReport.query.count(), 0)

        messages = self._get_flash_messages()
        combined = " ".join(messages).lower()
        self.assertIn("ly do", combined)
        self.assertIn("15 phut", combined)

    def test_monitor_mode_feedback_is_informational_and_submission_is_preserved(self):
        self.app.config["ABUS_MODE"] = "monitor"

        with self.client.session_transaction() as sess:
            sess["math_captcha_answer_report"] = "7"
            sess["reporter_id"] = "reporter-feedback-monitor"

        payload = self._base_payload("Monitor mode still stores this report")
        response = self.client.post(
            "/scammer/report",
            data=payload,
            headers={"X-Forwarded-For": "203.0.113.10"},
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        response.close()

        with self.app.app_context():
            stored = ScammerReport.query.first()
            self.assertIsNotNone(stored)
            self.assertEqual(stored.description, payload["description"])

        messages = self._get_flash_messages()
        combined = " ".join(messages).lower()
        self.assertIn("giam sat", combined)
        self.assertIn("khong chan", combined)

    def test_reason_code_mapping_returns_clear_vietnamese_messages(self):
        from routes.scammer import anti_spam_reason_message

        account_msg = anti_spam_reason_message("acct_threshold", 8)
        cookie_msg = anti_spam_reason_message("cookie_threshold", 8)
        ip_msg = anti_spam_reason_message("ip_threshold", 8)
        cooldown_msg = anti_spam_reason_message("active_cooldown", 4)
        monitor_msg = anti_spam_reason_message("monitor_observe", 0)
        fallback_msg = anti_spam_reason_message("unknown", 5)

        self.assertIn("tai khoan", account_msg.lower())
        self.assertIn("thiet bi", cookie_msg.lower())
        self.assertIn("mang", ip_msg.lower())
        self.assertIn("con lai", cooldown_msg.lower())
        self.assertIn("giam sat", monitor_msg.lower())
        self.assertIn("ly do", fallback_msg.lower())


if __name__ == "__main__":
    unittest.main()
