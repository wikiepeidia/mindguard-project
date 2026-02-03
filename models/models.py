"""Database models."""
from datetime import datetime
from extensions import db  # <--- QUAN TRỌNG: Import từ extensions

class ScamReport(db.Model):
    __tablename__ = 'scam_reports'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    channel = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=False)
    protection_tip = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Registration(db.Model):
    __tablename__ = 'registrations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default='user')
    is_admin = db.Column(db.Boolean, default=False)
    date_of_birth = db.Column(db.String(20))
    cccd = db.Column(db.String(20))
    occupation = db.Column(db.String(100))
    city = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    bio = db.Column(db.Text)
    onboarding_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class QuizResult(db.Model):
    __tablename__ = 'quiz_results'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150))
    score = db.Column(db.Integer, nullable=False)
    max_score = db.Column(db.Integer, nullable=False)
    certificate_code = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ScammerReport(db.Model):
    __tablename__ = 'scammer_reports'
    id = db.Column(db.Integer, primary_key=True)
    scammer_identifier = db.Column(db.String(200), nullable=False)
    scammer_info_raw = db.Column(db.String(200))
    scammer_name = db.Column(db.String(200))
    report_type = db.Column(db.String(50), default='general')
    bank_name = db.Column(db.String(100))
    scammer_email = db.Column(db.String(100))
    social_link = db.Column(db.String(200))
    scam_type = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=False)
    evidence_urls = db.Column(db.Text)
    reporter_hash = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(20), default='pending')
    verification_status = db.Column(db.String(20), default='unverified')  # unverified, pending, verified
    risk_score = db.Column(db.Integer, default=0)  # 0-100
    confirmed_by_count = db.Column(db.Integer, default=0)  # Số người xác nhận
    report_count = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ScammerLeaderboard(db.Model):
    __tablename__ = 'scammer_leaderboard'
    id = db.Column(db.Integer, primary_key=True)
    scammer_id = db.Column(db.Integer, db.ForeignKey('scammer_reports.id'), nullable=False)
    total_reports = db.Column(db.Integer, default=0)
    danger_level = db.Column(db.String(20), default='low')
    last_reported = db.Column(db.DateTime, default=datetime.utcnow)
    scammer = db.relationship('ScammerReport', backref='leaderboard_entry')

class AiQuizQuestion(db.Model):
    __tablename__ = 'ai_quiz_questions'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Integer, nullable=False)
    source_type = db.Column(db.String(50), default='scam_report')
    is_verified = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        import json
        try: opts = json.loads(self.options)
        except: opts = []
        return {"id": self.id, "question": self.question, "options": opts, "answer": self.answer, "is_dynamic": True}

class AiChatSession(db.Model):
    __tablename__ = 'ai_chat_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('registrations.id'), nullable=False)
    title = db.Column(db.String(100), default="Cuộc trò chuyện mới")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    messages = db.relationship('AiChatMessage', backref='session', lazy=True, cascade="all, delete-orphan")

class AiChatMessage(db.Model):
    __tablename__ = 'ai_chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('ai_chat_sessions.id'), nullable=False)
    sender = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatSupportMessage(db.Model):
    __tablename__ = 'chat_support_messages'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    bot_reply = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('registrations.id'), nullable=False)
    target_identifier = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

