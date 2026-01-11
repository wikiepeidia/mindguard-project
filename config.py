"""Configuration settings for MindGuard Flask application."""
import os
import secrets


class Config:
    """Base configuration."""
    
    # Define the base directory of the application
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    
    # Configure SQLite database to be located in the 'database' folder
    # We use an absolute path to ensure it works correctly regardless of where the app is run from
    DB_PATH = os.path.join(BASE_DIR, 'database', 'mindguard_v2.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", f"sqlite:///{DB_PATH}")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Admin credentials
    ADMIN_USERNAME = os.environ.get("MINDGUARD_ADMIN_USER", "admin")
    ADMIN_PASSWORD = os.environ.get("MINDGUARD_ADMIN_PASS", "mindguard2025")
    
    # Quiz settings
    QUIZ_PASS_PERCENTAGE = 0.75  # 75% to get certificate
    
    # Scammer report settings
    MIN_EVIDENCE_COUNT = 1  # Minimum evidence required
    AUTO_APPROVE_THRESHOLD = 3  # Auto-approve if report count >= this
    
    # Encryption settings
    REPORT_ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", "mindguard-secret-key-2025")
