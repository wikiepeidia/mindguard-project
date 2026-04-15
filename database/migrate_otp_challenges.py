"""Migration script for otp_challenges table.

Idempotent: safe to run multiple times. Creates the table and indexes
only if they do not already exist.
"""
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
    """Check whether an index already exists on a table."""
    for index in inspector.get_indexes(table_name):
        if index.get("name") == index_name:
            return True
    return False


def migrate():
    """Create otp_challenges table and indexes if they do not exist."""
    with app.app_context():
        inspector = db.inspect(db.engine)

        if "otp_challenges" not in inspector.get_table_names():
            with db.engine.connect() as conn:
                conn.execute(
                    text(
                        """
                        CREATE TABLE otp_challenges (
                            id SERIAL PRIMARY KEY,
                            email VARCHAR(120) NOT NULL,
                            purpose VARCHAR(50) NOT NULL,
                            otp_hash VARCHAR(128) NOT NULL,
                            otp_salt VARCHAR(64) NOT NULL,
                            pepper_version VARCHAR(20) DEFAULT 'v1',
                            attempts_used INTEGER DEFAULT 0,
                            max_attempts INTEGER DEFAULT 5,
                            issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            expires_at TIMESTAMP NOT NULL,
                            locked_until TIMESTAMP,
                            used_at TIMESTAMP,
                            invalidated_at TIMESTAMP,
                            invalidation_reason VARCHAR(100),
                            status VARCHAR(30) DEFAULT 'active'
                        );
                        """
                    )
                )
                conn.commit()
            print("[migrate] Created table: otp_challenges")
        else:
            print("[migrate] Table otp_challenges already exists, skipping.")

        # Refresh inspector after potential table creation
        inspector = db.inspect(db.engine)

        indexes = [
            ("otp_challenges", "idx_otp_challenges_email", "email"),
            ("otp_challenges", "idx_otp_challenges_status", "status"),
            ("otp_challenges", "idx_otp_challenges_expires_at", "expires_at"),
            (
                "otp_challenges",
                "idx_otp_challenges_email_status",
                "email, status",
            ),
        ]

        for table_name, index_name, columns_sql in indexes:
            if not _index_exists(inspector, table_name, index_name):
                with db.engine.connect() as conn:
                    conn.execute(
                        text(
                            f"CREATE INDEX {index_name} ON {table_name} ({columns_sql});"
                        )
                    )
                    conn.commit()
                print(f"[migrate] Created index: {index_name}")
            else:
                print(f"[migrate] Index {index_name} already exists, skipping.")

    print("[migrate] otp_challenges migration complete.")


if __name__ == "__main__":
    migrate()
