import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from flask import Flask

from config import Config
from extensions import db
from models import ScammerReport, SensitiveAccessLog
from routes.admin import admin_bp


class TestAdminExportPolicy(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_base_dir = Config.BASE_DIR
        Config.BASE_DIR = self.temp_dir.name

        project_root = Path(__file__).resolve().parents[2]
        self.app = Flask(__name__, template_folder=str(project_root / "templates"))
        self.app.config["TESTING"] = True
        self.app.config["PROPAGATE_EXCEPTIONS"] = False
        self.app.config["SECRET_KEY"] = "test-secret"
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        db.init_app(self.app)
        self.app.register_blueprint(admin_bp)

        with self.app.app_context():
            db.create_all()
            db.session.add(
                ScammerReport(
                    scammer_identifier="0912345678",
                    scammer_info_raw="0912345678",
                    report_type="general",
                    scam_type="phone-scam",
                    description="Test description",
                    reporter_hash="abc",
                    status="approved",
                    report_count=2,
                    created_at=datetime.utcnow(),
                )
            )
            db.session.commit()

        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        Config.BASE_DIR = self.original_base_dir
        self.temp_dir.cleanup()

    def _login_admin_session(self):
        with self.client.session_transaction() as sess:
            sess["is_admin"] = True
            sess["admin_id"] = 1
            sess["admin_email"] = "admin@example.com"

    def test_export_masked_by_default(self):
        self._login_admin_session()

        response = self.client.get("/admin/export-dataset")

        self.assertEqual(response.status_code, 200)
        csv_content = response.data.decode("utf-8-sig")
        response.close()
        self.assertIn("*******678", csv_content)
        self.assertNotIn("0912345678", csv_content)

    def test_export_full_data_requires_reason(self):
        self._login_admin_session()

        response = self.client.get("/admin/export-dataset?full_data=1")

        self.assertEqual(response.status_code, 400)
        self.assertIn("Ly do bat buoc", response.data.decode("utf-8"))

    def test_export_full_data_with_reason_creates_audit_log(self):
        self._login_admin_session()

        response = self.client.get("/admin/export-dataset?full_data=1&reason=incident")

        self.assertEqual(response.status_code, 200)
        csv_content = response.data.decode("utf-8-sig")
        response.close()
        self.assertIn("0912345678", csv_content)

        with self.app.app_context():
            row = SensitiveAccessLog.query.filter_by(action="export").first()
            self.assertIsNotNone(row)
            self.assertEqual(row.actor_email, "admin@example.com")
            self.assertEqual(row.reason, "incident")

    def test_scammer_reports_view_creates_audit_log(self):
        self._login_admin_session()

        response = self.client.get("/admin/scammer-reports")

        self.assertEqual(response.status_code, 500)
        with self.app.app_context():
            row = SensitiveAccessLog.query.filter_by(action="view", object_type="scammer_reports").first()
            self.assertIsNotNone(row)
            self.assertEqual(row.actor_email, "admin@example.com")

    def test_approve_report_creates_update_audit_log(self):
        self._login_admin_session()

        response = self.client.post("/admin/approve-report/1", headers={"Referer": "/admin/scammer-reports"})

        self.assertEqual(response.status_code, 302)
        with self.app.app_context():
            row = SensitiveAccessLog.query.filter_by(action="update", object_type="scammer_report", object_id="1").first()
            self.assertIsNotNone(row)
            self.assertEqual(row.reason, "approve_report")


if __name__ == "__main__":
    unittest.main()
