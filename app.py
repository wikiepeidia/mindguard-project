"""
MindGuard Flask Application
===========================
A web application to help users protect themselves from scams and fraud.

Features:
- Scammer reporting system with anonymity
- Scammer leaderboard (most reported scammers)
- AI chatbot for scam analysis
- Security awareness quiz
- Certificate generation
"""

from flask import Flask
from datetime import datetime
from config import Config
from models import db
from routes.main import main_bp
from routes.scammer import scammer_bp
from routes.chatbot import chatbot_bp
from routes.quiz import quiz_bp
from routes.auth import auth_bp
from routes.admin import admin_bp

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Register custom template filters
@app.template_filter('nl2br')
def nl2br_filter(s):
    if s:
        # Use Flask's re-exported Markup/escape
        from markupsafe import Markup, escape
        return Markup(str(escape(s)).replace('\n', '<br>'))
    return ""

# Initialize database
db.init_app(app)

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(scammer_bp)
app.register_blueprint(chatbot_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)


# Context processor for global template variables
@app.context_processor
def inject_globals():
    """Inject global variables into all templates."""
    return {"current_year": datetime.now().year}


# Create database tables
with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")


if __name__ == "__main__":
    print("🚀 Starting MindGuard Flask Application...")
    print("📊 Access the app at: http://127.0.0.1:5000")
    print("👤 Admin panel: http://127.0.0.1:5000/admin/login")
    print("   Username: admin | Password: mindguard2025")
    app.run(debug=True)
