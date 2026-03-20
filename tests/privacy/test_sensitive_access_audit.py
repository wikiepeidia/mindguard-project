import unittest
from datetime import datetime, timedelta
from flask import Flask

from extensions import db


class TestSensitiveAccessAuditService(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        db.init_app(self.app)

        with self.app.app_context():
            from models import SensitiveAccessLog  # noqa: F401

            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_log_row_stores_required_metadata(self):
        from services.sensitive_access_log import log_sensitive_access
        from models import SensitiveAccessLog

        with self.app.app_context():
            with self.app.test_request_context(
                "/admin/export-dataset",
                headers={"User-Agent": "MindGuardTest/1.0"},
                environ_base={"REMOTE_ADDR": "127.0.0.1"},
            ):
                created = log_sensitive_access(
                    actor_id=1,
                    actor_email="admin@example.com",
                    action="export",
                    object_type="dataset",
                    object_id="approved-reports",
                    reason="for incident response",
                )

            row = SensitiveAccessLog.query.get(created.id)
            self.assertIsNotNone(row)
            self.assertEqual(row.actor_id, 1)
            self.assertEqual(row.actor_email, "admin@example.com")
            self.assertEqual(row.action, "export")
            self.assertEqual(row.object_type, "dataset")
            self.assertEqual(row.object_id, "approved-reports")
            self.assertEqual(row.reason, "for incident response")
            self.assertEqual(row.ip_address, "127.0.0.1")
            self.assertIn("MindGuardTest/1.0", row.user_agent)
            self.assertIsNotNone(row.created_at)

    def test_query_filters_by_actor_action_and_time_window(self):
        from models import SensitiveAccessLog
        from services.sensitive_access_log import query_sensitive_access_logs

        now = datetime.utcnow()

        with self.app.app_context():
            db.session.add_all(
                [
                    SensitiveAccessLog(
                        actor_email="admin1@example.com",
                        action="export",
                        object_type="dataset",
                        object_id="1",
                        reason="R1",
                        created_at=now - timedelta(hours=3),
                    ),
                    SensitiveAccessLog(
                        actor_email="admin1@example.com",
                        action="view",
                        object_type="report",
                        object_id="2",
                        created_at=now - timedelta(hours=2),
                    ),
                    SensitiveAccessLog(
                        actor_email="admin2@example.com",
                        action="export",
                        object_type="dataset",
                        object_id="3",
                        reason="R2",
                        created_at=now - timedelta(minutes=30),
                    ),
                ]
            )
            db.session.commit()

            logs = query_sensitive_access_logs(
                actor_email="admin1@example.com",
                action="export",
                start_time=now - timedelta(hours=4),
                end_time=now - timedelta(hours=1),
            )

            self.assertEqual(len(logs), 1)
            self.assertEqual(logs[0].actor_email, "admin1@example.com")
            self.assertEqual(logs[0].action, "export")

    def test_retention_cleanup_removes_logs_older_than_90_days(self):
        from models import SensitiveAccessLog
        from services.sensitive_access_log import cleanup_expired_sensitive_access_logs

        now = datetime.utcnow()

        with self.app.app_context():
            old_log = SensitiveAccessLog(
                actor_email="admin-old@example.com",
                action="view",
                object_type="report",
                object_id="old",
                created_at=now - timedelta(days=120),
            )
            new_log = SensitiveAccessLog(
                actor_email="admin-new@example.com",
                action="view",
                object_type="report",
                object_id="new",
                created_at=now - timedelta(days=10),
            )
            db.session.add_all([old_log, new_log])
            db.session.commit()

            deleted_count = cleanup_expired_sensitive_access_logs(retention_days=90)

            remaining_ids = {row.object_id for row in SensitiveAccessLog.query.all()}
            self.assertEqual(deleted_count, 1)
            self.assertEqual(remaining_ids, {"new"})


if __name__ == "__main__":
    unittest.main()
