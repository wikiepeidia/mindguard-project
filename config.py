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
ai_config = load_local_env('chatbot.json')

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    # Thay đổi SECRET_KEY nếu cần bảo mật hơn
    SECRET_KEY = os.environ.get("SECRET_KEY") or "579c3247894062d9c43f1a73d340fb55c6c25d3b9be6d8f74a20d9a2a9a0af06"
    PERMANENT_SESSION_LIFETIME = 86400 * 7 
    
    DB_PATH = os.path.join(BASE_DIR, 'database', 'mindguard_v2.db')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Cấu hình AI (OpenRouter)
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY") or ai_config.get("OPENROUTER_API_KEY") or "sk-or-v1-..." 
    OPENROUTER_MODELS = [
        "liquid/lfm-2.5-1.2b-instruct:free",
        "liquid/lfm-2.5-1.2b-thinking:free",
        "allenai/molmo-2-8b:free",
        "google/gemini-2.0-flash-lite-preview-02-05:free"
    ]
    
    # Cloudflare Turnstile
    CLOUDFLARE_SITE_KEY = os.environ.get("CLOUDFLARE_SITE_KEY") or cf_config.get("SITE_KEY")
    CLOUDFLARE_SECRET_KEY = os.environ.get("CLOUDFLARE_SECRET_KEY") or cf_config.get("SECRET_KEY")

    # Cấu hình khác
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "mindguard2025"
    QUIZ_PASS_PERCENTAGE = 0.75
    REPORT_ENCRYPTION_KEY = "mindguard-secret-key-2025"

    # Admin guard — secret key để mở khóa tài khoản admin bị suspend
    ADMIN_UNSUSPEND_SECRET = os.environ.get("ADMIN_UNSUSPEND_SECRET") or "0f27bbb5d2fd0bf9e76a5f0f08fcb4d614a7bc1130950832892faa4640420932"

    # Anti-spam monitor/soft-enforce configuration
    ABUS_MODE = os.environ.get("ABUS_MODE", "monitor")
    ABUS_WINDOW_MINUTES = int(os.environ.get("ABUS_WINDOW_MINUTES", 10))
    ABUS_THRESHOLD_COUNT = int(os.environ.get("ABUS_THRESHOLD_COUNT", 3))
    ABUS_COOLDOWN_MINUTES = int(os.environ.get("ABUS_COOLDOWN_MINUTES", 15))
    ABUS_ACCOUNT_WEIGHT = int(os.environ.get("ABUS_ACCOUNT_WEIGHT", 70))
    ABUS_COOKIE_WEIGHT = int(os.environ.get("ABUS_COOKIE_WEIGHT", 20))
    ABUS_IP_WEIGHT = int(os.environ.get("ABUS_IP_WEIGHT", 10))