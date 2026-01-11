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
    age_group = db.Column(db.String(50))
    occupation = db.Column(db.String(100))
    city = db.Column(db.String(100))
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
    scammer_name = db.Column(db.String(200))  # Optional name
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
