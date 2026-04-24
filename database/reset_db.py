import sys
import os

# Add parent directory to path to import app and models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import db

def reset_database():
    with app.app_context():
        print("Dropping all tables...")
        try:
            db.drop_all()
            print("All tables dropped.")
            db.create_all()
            print("All tables recreated with new schema.")
        except Exception as e:
            print(f"Error resetting database: {e}")

if __name__ == "__main__":
    reset_database()
