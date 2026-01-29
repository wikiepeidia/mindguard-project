"""Configuration settings for MindGuard Flask application."""
import os
import json

def load_local_env(filename):
    """Utility to load keys from .env/filename.json"""
    try:
        path = os.path.join(os.path.dirname(__file__), '.env', filename)
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
    except:
        return {}
    return {}

cf_config = load_local_env('cloudflare.json')

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
    
    # Cloudflare Turnstile
    CLOUDFLARE_SITE_KEY = os.environ.get("CLOUDFLARE_SITE_KEY") or cf_config.get("SITE_KEY")
    CLOUDFLARE_SECRET_KEY = os.environ.get("CLOUDFLARE_SECRET_KEY") or cf_config.get("SECRET_KEY")

    # Cấu hình khác
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "mindguard2025"
    QUIZ_PASS_PERCENTAGE = 0.75
    REPORT_ENCRYPTION_KEY = "mindguard-secret-key-2025"