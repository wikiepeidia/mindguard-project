import os
import sys

# Add the parent directory to sys.path to allow importing app
# This is necessary because this script is located in a subdirectory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db

def create_database():
    """
    Creates the SQLite database file and tables based on models.py.
    This script is designed to be run standalone to initialize the database.
    """
    print("🔄 Initializing Database Creation Process...")
    
    # Ensure the database directory exists (though app.py/config.py should handle pathing)
    db_folder = os.path.join(app.root_path, 'database')
    if not os.path.exists(db_folder):
        print(f"📂 Creating directory: {db_folder}")
        os.makedirs(db_folder, exist_ok=True)
    else:
        print(f"📂 Directory already exists: {db_folder}")

    # Log the database URI being used
    print(f"🔗 Target Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Create tables inside the application context
    with app.app_context():
        # Force import of models to ensure they are registered with SQLAlchemy
        import models
        print("🛠️  Creating database tables from models...")
        try:
            db.create_all()
            print("✅ Database tables created successfully!")
            print(f"✅ SQLite file should now exist at: {os.path.join(db_folder, 'mindguard.db')}")
        except Exception as e:
            print(f"❌ Error creating database: {e}")

if __name__ == "__main__":
    create_database()
