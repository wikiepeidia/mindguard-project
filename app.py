from flask import Flask, redirect, url_for, request
from datetime import datetime
import logging
import os
from config import Config
from extensions import db, mail, limiter, csrf
from routes.main import main_bp
from routes.scammer import scammer_bp
from routes.chatbot import chatbot_bp
from routes.quiz import quiz_bp
from routes.auth import auth_bp
from routes.admin import admin_bp
from utils.helpers import mask_sensitive_data, get_verification_badge

app = Flask(__name__)
app.config.from_object(Config)

# --- REQUEST LOGGING ---
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'access.log'),
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
access_logger = logging.getLogger('access')

# Bộ lọc template (nl2br)
@app.template_filter('nl2br')
def nl2br_filter(s):
    from markupsafe import Markup, escape
    return Markup(str(escape(s)).replace('\n', '<br>')) if s else ""

# Bộ lọc Masking (Ẩn thông tin nhạy cảm)
@app.template_filter('mask')
def mask_filter(s, data_type='auto'):
    return mask_sensitive_data(s, data_type)

@app.after_request
def apply_security_headers(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    # HSTS chỉ bật khi deploy HTTPS thực
    # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

@app.after_request
def log_request(response):
    access_logger.info(
        '%s %s %s %s %s',
        request.remote_addr,
        request.method,
        request.path,
        response.status_code,
        request.headers.get('User-Agent', '-')[:80]
    )
    return response

# Khởi tạo DB & Mail
db.init_app(app)
mail.init_app(app)
limiter.init_app(app)
csrf.init_app(app)

with app.app_context():
    db.create_all()

# Đăng ký Blueprints
app.register_blueprint(main_bp)
app.register_blueprint(scammer_bp)
app.register_blueprint(chatbot_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

# Biến toàn cục cho template
@app.context_processor
def inject_globals():
    return {
        "current_year": datetime.now().year,
        "get_verification_badge": get_verification_badge
    }

# --- ĐƯỜNG DẪN TẮT CHO ADMIN ---
@app.route('/admin')
def admin_redirect():
    return redirect(url_for('admin.admin_login'))

if __name__ == "__main__":
    # --- NGROK INTEGRATION ---
    # CHỈ CHẠY Ở PROCESS GỐC (Tránh khởi động 2 lần khi reload)
    import os
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        public_url_str = None
        try:
            from utils.ngrok_tunnel import start_ngrok
            # start_ngrok now returns URL silently
            public_url_str = start_ngrok(5000)
        except ImportError:
            pass 
        except Exception:
            pass 

        # Minimal Output as requested - ONLY in main process
        print("\n" + "="*50)
        print("🚀 MINDGUARD STARTED")
        print(f"🏠 Local: http://127.0.0.1:5000")
        print(f"👮 Admin: http://127.0.0.1:5000/admin")
        if public_url_str:
            print(f"🌍 Public: {public_url_str}")
        print("="*50 + "\n")
    
    app.run(debug=True)