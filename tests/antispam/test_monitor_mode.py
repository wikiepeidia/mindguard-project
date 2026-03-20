import unittest

from flask import Flask

from extensions import db
from models import AntiSpamEvent, ScammerReport
from routes.scammer import scammer_bp


class TestMonitorModeReportRoute(unittest.TestCase):
    def setUp(self):
        project_root = __import__("pathlib").Path(__file__).resolve().parents[2]
        self.app = Flask(__name__, template_folder=str(project_root / "templates"))
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "test-secret"
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        self.app.config["ABUS_MODE"] = "monitor"
        self.app.config["ABUS_THRESHOLD_COUNT"] = 1
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

    def test_monitor_mode_allows_submit_even_when_cooldown_flagged_and_logs_event(self):
        with self.client.session_transaction() as sess:
            sess["math_captcha_answer_report"] = "7"
            sess["reporter_id"] = "reporter-monitor"

        response = self.client.post(
            "/scammer/report",
            data={
                "math_answer": "7",
                "term_truth": "on",
                "term_responsibility": "on",
                "report_type": "general",
                "identifier_person": "0987654321",
                "scam_type_person": "Lừa đảo khác",
                "description": "Bao cao monitor mode",
            },
            headers={"X-Forwarded-For": "203.0.113.10"},
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 302)
        response.close()

        with self.app.app_context():
            self.assertEqual(ScammerReport.query.count(), 1)
            event = AntiSpamEvent.query.order_by(AntiSpamEvent.id.desc()).first()
            self.assertIsNotNone(event)
            self.assertTrue(event.triggered_cooldown)


if __name__ == "__main__":
    unittest.main()