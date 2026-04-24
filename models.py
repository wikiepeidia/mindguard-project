"""Database models for MindGuard application."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ScamReport(db.Model):
    """Model for user-submitted scam reports."""
    __tablename__ = 'scam_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    channel = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=False)
    protection_tip = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Registration(db.Model):
    """Model for user registrations."""
    __tablename__ = 'registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(256))  # Added password hash
    # age_group = db.Column(db.String(50)) # Deprecated
    date_of_birth = db.Column(db.String(20)) # Storing as String YYYY-MM-DD for simplicity
    cccd = db.Column(db.String(20))
    occupation = db.Column(db.String(100))
    city = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    bio = db.Column(db.Text)
    onboarding_completed = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class QuizResult(db.Model):
    """Model for storing quiz results."""
    __tablename__ = 'quiz_results'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150))
    score = db.Column(db.Integer, nullable=False)
    max_score = db.Column(db.Integer, nullable=False)
    certificate_code = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ScammerReport(db.Model):
    """Model for tracking reported scammers with anonymity."""
    __tablename__ = 'scammer_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    scammer_identifier = db.Column(db.String(200), nullable=False)  # Phone, account, etc (encrypted)
    scammer_info_raw = db.Column(db.String(200))  # Visible info (Phone, Bank Acc) - Added for display 
    scammer_name = db.Column(db.String(200))  # Optional name
    
    # New columns for specialized reports
    report_type = db.Column(db.String(50), default='general') # 'bank' or 'website'
    bank_name = db.Column(db.String(100))
    scammer_email = db.Column(db.String(100))
    social_link = db.Column(db.String(200))

    scam_type = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(100))  # Facebook, Zalo, SMS, etc
    description = db.Column(db.Text, nullable=False)
    evidence_urls = db.Column(db.Text)  # JSON array of evidence links
    reporter_hash = db.Column(db.String(64), nullable=False)  # Hashed reporter ID for anonymity
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    report_count = db.Column(db.Integer, default=1)  # How many times this scammer was reported
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ScammerReport {self.scammer_identifier}>'


class ScammerLeaderboard(db.Model):
    """Model for scammer leaderboard (most reported scammers)."""
    __tablename__ = 'scammer_leaderboard'
    
    id = db.Column(db.Integer, primary_key=True)
    scammer_id = db.Column(db.Integer, db.ForeignKey('scammer_reports.id'), nullable=False)
    total_reports = db.Column(db.Integer, default=0)
    danger_level = db.Column(db.String(20), default='low')  # low, medium, high, critical
    last_reported = db.Column(db.DateTime, default=datetime.utcnow)
    
    scammer = db.relationship('ScammerReport', backref='leaderboard_entry')
    
    def __repr__(self):
        return f'<ScammerLeaderboard {self.scammer_id}: {self.total_reports} reports>'



class AiQuizQuestion(db.Model):
    """Model for AI-generated quiz questions."""
    __tablename__ = 'ai_quiz_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=False) # stored as JSON string
    answer = db.Column(db.Integer, nullable=False)
    source_type = db.Column(db.String(50), default='scam_report')
    is_verified = db.Column(db.Boolean, default=True) # Assume trusted for now
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        try:
            opts = json.loads(self.options)
        except:
            opts = []
        return {
            "id": self.id,
            "question": self.question,
            "options": opts,
            "answer": self.answer,
            "is_dynamic": True
        }

class AiChatSession(db.Model):
    """Model for AI Chat sessions (Chat history)."""
    __tablename__ = 'ai_chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('registrations.id'), nullable=False)
    title = db.Column(db.String(100), default="New Chat")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = db.relationship('AiChatMessage', backref='session', lazy=True, cascade="all, delete-orphan")


class AiChatMessage(db.Model):
    """Model for individual messages in an AI chat session."""
    __tablename__ = 'ai_chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('ai_chat_sessions.id'), nullable=False)
    sender = db.Column(db.String(20), nullable=False) # 'user' or 'bot'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ChatSupportMessage(db.Model):
    """Model for chat support messages."""
    __tablename__ = 'chat_support_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    bot_reply = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChatMessage {self.session_id}>'
