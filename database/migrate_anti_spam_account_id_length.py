"""Widen anti-spam account_id columns to fit OTP actor identifiers.

Idempotent: safe to run multiple times. On PostgreSQL, widens both
anti_spam_events.account_id and anti_spam_actor_states.account_id to
VARCHAR(128) when they are narrower.
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


def _column_length(inspector, table_name, column_name):
    for column in inspector.get_columns(table_name):
        if column.get("name") != column_name:
            continue
        column_type = column.get("type")
        return getattr(column_type, "length", None)
    return None


def _ensure_column_width(table_name, column_name, target_length):
    inspector = db.inspect(db.engine)
    current_length = _column_length(inspector, table_name, column_name)
    if current_length is None:
        print(f"[migrate] Column missing: {table_name}.{column_name}, skipping.")
        return
    if current_length >= target_length:
        print(
            f"[migrate] Column {table_name}.{column_name} already width {current_length}, skipping."
        )
        return

    dialect = db.engine.dialect.name
    if dialect != "postgresql":
        print(
            f"[migrate] Unsupported dialect '{dialect}' for ALTER COLUMN on {table_name}.{column_name}; skipping."
        )
        return

    with db.engine.connect() as conn:
        conn.execute(
            text(
                f"ALTER TABLE {table_name} ALTER COLUMN {column_name} TYPE VARCHAR({target_length});"
            )
        )
        conn.commit()
    print(f"[migrate] Widened {table_name}.{column_name} to VARCHAR({target_length})")


def migrate():
    with app.app_context():
        _ensure_column_width("anti_spam_events", "account_id", 128)
        _ensure_column_width("anti_spam_actor_states", "account_id", 128)
    print("[migrate] anti_spam account_id width migration complete.")


if __name__ == "__main__":
    migrate()