from flask import Flask, redirect, url_for
from datetime import datetime
from config import Config
from extensions import db, mail
from routes.main import main_bp
from routes.scammer import scammer_bp
from routes.chatbot import chatbot_bp
from routes.quiz import quiz_bp
from routes.auth import auth_bp
from routes.admin import admin_bp

app = Flask(__name__)
app.config.from_object(Config)

# Bộ lọc template (nl2br)
@app.template_filter('nl2br')
def nl2br_filter(s):
    from markupsafe import Markup, escape
    return Markup(str(escape(s)).replace('\n', '<br>')) if s else ""

# Khởi tạo DB & Mail
db.init_app(app)
mail.init_app(app)

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
    return {"current_year": datetime.now().year}

# --- ĐƯỜNG DẪN TẮT CHO ADMIN ---
@app.route('/admin')
def admin_redirect():
    return redirect(url_for('admin.admin_login'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # print("✅ Database tables checked/created.") # Silenced for clean output
    
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