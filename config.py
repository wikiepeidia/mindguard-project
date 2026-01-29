"""Configuration settings for MindGuard Flask application."""
import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    # Thay đổi SECRET_KEY nếu cần bảo mật hơn
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-mindguard-2025-secure"
    PERMANENT_SESSION_LIFETIME = 86400 * 7 
    
    DB_PATH = os.path.join(BASE_DIR, 'database', 'mindguard_v2.db')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Cấu hình AI (OpenRouter)
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY") or "sk-or-v1-..." 
    OPENROUTER_MODELS = [
        "qwen/qwen-2.5-vl-7b-instruct:free",
        "google/gemini-2.0-flash-exp:free",
        "meta-llama/llama-3.3-70b-instruct:free",
    ]
    
    # Cấu hình khác
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "mindguard2025"
    QUIZ_PASS_PERCENTAGE = 0.75
    REPORT_ENCRYPTION_KEY = "mindguard-secret-key-2025"