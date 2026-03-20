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

        if "anti_spam_events" not in inspector.get_table_names():
            with db.engine.connect() as conn:
                conn.execute(
                    text(
                        """
                        CREATE TABLE anti_spam_events (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            actor_key VARCHAR(128) NOT NULL,
                            actor_type VARCHAR(20) NOT NULL,
                            account_id VARCHAR(64),
                            reporter_hash VARCHAR(64),
                            ip_address VARCHAR(45),
                            risk_score INTEGER NOT NULL DEFAULT 0,
                            risk_level VARCHAR(10) NOT NULL DEFAULT 'low',
                            window_count INTEGER NOT NULL DEFAULT 1,
                            triggered_cooldown BOOLEAN NOT NULL DEFAULT 0,
                            cooldown_until DATETIME,
                            occurred_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                        );
                        """
                    )
                )
                conn.commit()

        inspector = db.inspect(db.engine)
        if "anti_spam_actor_states" not in inspector.get_table_names():
            with db.engine.connect() as conn:
                conn.execute(
                    text(
                        """
                        CREATE TABLE anti_spam_actor_states (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            actor_key VARCHAR(128) NOT NULL UNIQUE,
                            actor_type VARCHAR(20) NOT NULL,
                            account_id VARCHAR(64),
                            reporter_hash VARCHAR(64),
                            ip_address VARCHAR(45),
                            window_started_at DATETIME,
                            window_count INTEGER NOT NULL DEFAULT 0,
                            cooldown_until DATETIME,
                            last_risk_score INTEGER NOT NULL DEFAULT 0,
                            last_risk_level VARCHAR(10) NOT NULL DEFAULT 'low',
                            last_seen_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                        );
                        """
                    )
                )
                conn.commit()

        inspector = db.inspect(db.engine)
        indexes = [
            ("anti_spam_events", "idx_anti_spam_events_actor_occurred", "actor_key, occurred_at"),
            ("anti_spam_events", "idx_anti_spam_events_occurred_at", "occurred_at"),
            ("anti_spam_actor_states", "idx_anti_spam_actor_states_actor_key", "actor_key"),
            ("anti_spam_actor_states", "idx_anti_spam_actor_states_cooldown_until", "cooldown_until"),
        ]

        for table_name, index_name, columns_sql in indexes:
            if not _index_exists(inspector, table_name, index_name):
                with db.engine.connect() as conn:
                    conn.execute(
                        text(f"CREATE INDEX {index_name} ON {table_name} ({columns_sql});")
                    )
                    conn.commit()


if __name__ == "__main__":
    migrate()
