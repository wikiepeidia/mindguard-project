"""Migration: Create chat_feedbacks table for TRUST-03 feedback button."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import ChatFeedback

with app.app_context():
    db.create_all()
    print("✅ chat_feedbacks table created (if not exists).")
