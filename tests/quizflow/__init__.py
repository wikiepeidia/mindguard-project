"""Test helpers for quiz one-question flow tests.

Provides an isolated Flask test app with in-memory SQLite (StaticPool)
and a base TestCase class so each test method starts with a clean slate.
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask
from sqlalchemy.pool import StaticPool

from extensions import db
from config import Config


def create_test_app():
    """Create an isolated Flask test app with in-memory SQLite (StaticPool).

    Uses StaticPool so all connections share the same in-memory database,
    allowing DB writes inside request handlers to be visible when queried
    from the test body.
    """
    test_app = Flask(
        'mindguard_test',
        template_folder=os.path.join(PROJECT_ROOT, 'templates'),
        static_folder=os.path.join(PROJECT_ROOT, 'static'),
    )
    test_app.config.from_object(Config)
    test_app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key-quiz-flow',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'connect_args': {'check_same_thread': False},
            'poolclass': StaticPool,
        },
        'WTF_CSRF_ENABLED': False,
    })

    db.init_app(test_app)

    @test_app.template_filter('nl2br')
    def nl2br_filter(s):
        from markupsafe import Markup, escape
        return Markup(str(escape(s)).replace('\n', '<br>')) if s else ''

    # Register all blueprints so base.html url_for() calls resolve
    from routes.quiz import quiz_bp
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.scammer import scammer_bp
    from routes.chatbot import chatbot_bp

    test_app.register_blueprint(quiz_bp)
    test_app.register_blueprint(main_bp)
    test_app.register_blueprint(auth_bp)
    test_app.register_blueprint(admin_bp)
    test_app.register_blueprint(scammer_bp)
    test_app.register_blueprint(chatbot_bp)

    # Context processor mirrors app.py
    from datetime import datetime
    from utils.helpers import get_verification_badge

    @test_app.context_processor
    def inject_globals():
        return {
            'current_year': datetime.now().year,
            'get_verification_badge': get_verification_badge,
        }

    with test_app.app_context():
        db.create_all()

    return test_app


class QuizFlowTestBase(unittest.TestCase):
    """Base class for quiz flow tests.

    Each test method gets a fresh in-memory DB and an isolated Flask
    test client. The app context is pushed/popped around the test so
    that DB queries like `QuizResult.query.count()` work without extra
    context managers.
    """

    def setUp(self):
        self.app = create_test_app()
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def _login(self):
        """Inject a valid user session so @login_required passes."""
        with self.client.session_transaction() as s:
            s['registration_email'] = 'test@test.com'
            s['registration_name'] = 'Người dùng Test'
