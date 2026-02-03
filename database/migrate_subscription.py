import sys
import os

# Add parent directory to path so we can import extensions
# Use insert(0) to prioritize local modules over system packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from extensions import db
from config import Config
from sqlalchemy import text

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def migrate():
    with app.app_context():
        # Check if table exists
        inspector = db.inspect(db.engine)
        if 'subscriptions' not in inspector.get_table_names():
            print("Creating subscriptions table...")
            with db.engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE subscriptions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        target_identifier VARCHAR(200) NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES registrations(id)
                    );
                """))
                print("Table created.")
        else:
            print("Table subscriptions already exists.")

if __name__ == "__main__":
    migrate()
