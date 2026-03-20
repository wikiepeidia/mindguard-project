import os
import sys

from flask import Flask
from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import Config
from extensions import db


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


def _index_exists(inspector, table_name, index_name):
    for index in inspector.get_indexes(table_name):
        if index.get("name") == index_name:
            return True
    return False


def migrate():
    with app.app_context():
        inspector = db.inspect(db.engine)

        if "sensitive_access_logs" not in inspector.get_table_names():
            with db.engine.connect() as conn:
                conn.execute(
                    text(
                        """
                        CREATE TABLE sensitive_access_logs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            actor_id INTEGER,
                            actor_email VARCHAR(150) NOT NULL,
                            action VARCHAR(20) NOT NULL,
                            object_type VARCHAR(100) NOT NULL,
                            object_id VARCHAR(100) NOT NULL,
                            reason TEXT,
                            ip_address VARCHAR(45),
                            user_agent VARCHAR(512),
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                            FOREIGN KEY(actor_id) REFERENCES registrations(id)
                        );
                        """
                    )
                )
                conn.commit()

        inspector = db.inspect(db.engine)
        indexes = [
            ("idx_sensitive_access_logs_created_at", "created_at"),
            ("idx_sensitive_access_logs_actor_email_created_at", "actor_email, created_at"),
            ("idx_sensitive_access_logs_action_created_at", "action, created_at"),
        ]

        for index_name, columns_sql in indexes:
            if not _index_exists(inspector, "sensitive_access_logs", index_name):
                with db.engine.connect() as conn:
                    conn.execute(
                        text(
                            f"CREATE INDEX {index_name} ON sensitive_access_logs ({columns_sql});"
                        )
                    )
                    conn.commit()


if __name__ == "__main__":
    migrate()
