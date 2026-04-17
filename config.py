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
pg_config = load_local_env('postgresql_neondb.json')
resend_config = load_local_env('RESEND.json') or load_local_env('resend.json')

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    # Thay đổi SECRET_KEY nếu cần bảo mật hơn
    SECRET_KEY = os.environ.get("SECRET_KEY") or "579c3247894062d9c43f1a73d340fb55c6c25d3b9be6d8f74a20d9a2a9a0af06"
    PERMANENT_SESSION_LIFETIME = 86400 * 7 
    
    # Database: prefer PostgreSQL (env var or .env/postgresql_neondb.json), fallback to SQLite
    _DATABASE_URL = os.environ.get("DATABASE_URL") or pg_config.get("DATABASE_URL")
    if _DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = _DATABASE_URL
    else:
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
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
    QUIZ_PASS_PERCENTAGE = 0.75
    REPORT_ENCRYPTION_KEY = os.environ.get("REPORT_ENCRYPTION_KEY", "")

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

    # OTP security policy
    OTP_TTL_SECONDS = int(os.environ.get("OTP_TTL_SECONDS", 300))
    OTP_MAX_ATTEMPTS = int(os.environ.get("OTP_MAX_ATTEMPTS", 5))
    OTP_LOCKOUT_SECONDS = int(os.environ.get("OTP_LOCKOUT_SECONDS", 900))
    OTP_PEPPER = os.environ.get("OTP_PEPPER", "")
    OTP_PEPPER_VERSION = os.environ.get("OTP_PEPPER_VERSION", "v1")
    OTP_RESEND_COOLDOWN_SECONDS = int(os.environ.get("OTP_RESEND_COOLDOWN_SECONDS", 60))
    OTP_RESEND_WINDOW_SECONDS = int(os.environ.get("OTP_RESEND_WINDOW_SECONDS", 900))
    OTP_RESEND_MAX_PER_WINDOW = int(os.environ.get("OTP_RESEND_MAX_PER_WINDOW", 3))
    OTP_VERIFY_RATE_LIMIT = os.environ.get("OTP_VERIFY_RATE_LIMIT", "10/minute;3/second")
    OTP_RESEND_RATE_LIMIT = os.environ.get("OTP_RESEND_RATE_LIMIT", "5/minute;1/second")
    OTP_ABUSE_WINDOW_MINUTES = int(os.environ.get("OTP_ABUSE_WINDOW_MINUTES", 10))
    OTP_ABUSE_THRESHOLD_COUNT = int(os.environ.get("OTP_ABUSE_THRESHOLD_COUNT", 3))
    OTP_ABUSE_COOLDOWN_MINUTES = int(os.environ.get("OTP_ABUSE_COOLDOWN_MINUTES", 15))

    # OTP email delivery (Phase 21)
    EMAIL_PROVIDER = (os.environ.get("EMAIL_PROVIDER") or resend_config.get("EMAIL_PROVIDER") or "resend_api").strip().lower()
    RESEND_API_KEY = (os.environ.get("RESEND_API_KEY") or resend_config.get("RESEND_API_KEY") or resend_config.get("API_KEY") or "").strip()
    RESEND_FROM_EMAIL = (os.environ.get("RESEND_FROM_EMAIL") or resend_config.get("RESEND_FROM_EMAIL") or resend_config.get("FROM_EMAIL") or "").strip()
    OTP_EMAIL_TIMEOUT_SECONDS = int(os.environ.get("OTP_EMAIL_TIMEOUT_SECONDS", 5))
    OTP_EMAIL_RETRY_ATTEMPTS = int(os.environ.get("OTP_EMAIL_RETRY_ATTEMPTS", 1))

    @classmethod
    def otp_email_missing_config(cls):
        """Return missing config keys required for the selected OTP provider."""
        provider = (cls.EMAIL_PROVIDER or "").strip().lower()

        if provider != "resend_api":
            return ["EMAIL_PROVIDER(resend_api)"]

        missing = []
        if not cls.RESEND_API_KEY:
            missing.append("RESEND_API_KEY")
        if not cls.RESEND_FROM_EMAIL:
            missing.append("RESEND_FROM_EMAIL")
        return missing

    @classmethod
    def otp_email_config_ready(cls):
        """Whether OTP email delivery configuration is complete."""
        return len(cls.otp_email_missing_config()) == 0