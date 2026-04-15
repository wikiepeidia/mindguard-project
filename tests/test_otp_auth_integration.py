"""Tests for OTP auth route integration (Phase 20, Plan 02).

Validates that:
  - Register issues OTP challenge (no hardcoded fallback)
  - Verify enforces TTL, attempts, lockout, single-use
  - Template does not disclose OTP values
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask
from sqlalchemy.pool import StaticPool

from extensions import db, csrf, limiter
from config import Config
from models import Registration
from models.models import OtpChallenge


# ---------------------------------------------------------------------------
# Test app factory
# ---------------------------------------------------------------------------

def create_test_app():
    """Create a test Flask app with in-memory SQLite."""
    app = Flask(
        'mindguard_otp_auth_test',
        template_folder=os.path.join(PROJECT_ROOT, 'templates'),
        static_folder=os.path.join(PROJECT_ROOT, 'static'),
    )
    app.config.from_object(Config)
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-otp-auth-secret',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'connect_args': {'check_same_thread': False},
            'poolclass': StaticPool,
        },
        'WTF_CSRF_ENABLED': False,
        'CLOUDFLARE_SECRET_KEY': None,
        'CLOUDFLARE_SITE_KEY': None,
        'ABUS_MODE': 'monitor',
        'RATELIMIT_ENABLED': False,
        'OTP_TTL_SECONDS': 300,
        'OTP_MAX_ATTEMPTS': 3,
        'OTP_LOCKOUT_SECONDS': 900,
        'OTP_PEPPER': 'test-pepper',
        'OTP_PEPPER_VERSION': 'v1',
    })

    db.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)

    @app.template_filter('nl2br')
    def nl2br_filter(s):
        from markupsafe import Markup, escape
        return Markup(str(escape(s)).replace('\n', '<br>')) if s else ''

    @app.template_filter('mask')
    def mask_filter(s, data_type='auto'):
        return s

    from datetime import datetime as dt
    from utils.helpers import get_verification_badge

    @app.context_processor
    def inject_globals():
        return {
            'current_year': dt.now().year,
            'get_verification_badge': get_verification_badge,
        }

    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.scammer import scammer_bp
    from routes.quiz import quiz_bp
    from routes.chatbot import chatbot_bp
    from routes.admin import admin_bp
    from routes.library import library_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(scammer_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(library_bp)

    with app.app_context():
        db.create_all()

    return app


class OtpAuthRegisterTests(unittest.TestCase):
    """Task 1: Register route creates OTP challenge instead of hardcoded OTP."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_test_app()

    def setUp(self):
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        # Set math captcha
        with self.client.session_transaction() as sess:
            sess['math_captcha_answer_register'] = '42'

    def tearDown(self):
        db.session.rollback()
        self.ctx.pop()

    def test_register_creates_otp_challenge_in_db(self):
        """After register, an OtpChallenge row should exist for the email."""
        resp = self.client.post('/register', data={
            'name': 'Test User',
            'email': 'challenge@gmail.com',
            'password': 'securepass',
            'math_answer': '42',
        }, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)

        challenge = OtpChallenge.query.filter_by(
            email='challenge@gmail.com', purpose='register'
        ).first()
        self.assertIsNotNone(challenge, "OtpChallenge should be created on register")
        self.assertEqual(challenge.status, 'active')

    def test_register_sets_pending_otp_challenge_id_in_session(self):
        """Session should contain pending_otp_challenge_id after register."""
        resp = self.client.post('/register', data={
            'name': 'Test User',
            'email': 'sessionid@gmail.com',
            'password': 'securepass',
            'math_answer': '42',
        }, follow_redirects=False)

        with self.client.session_transaction() as sess:
            self.assertIn('pending_otp_challenge_id', sess)
            self.assertIsNotNone(sess['pending_otp_challenge_id'])

    def test_register_sets_pending_verification_email_in_session(self):
        """Session should contain pending_verification_email after register."""
        resp = self.client.post('/register', data={
            'name': 'Test User',
            'email': 'veremail@gmail.com',
            'password': 'securepass',
            'math_answer': '42',
        }, follow_redirects=False)

        with self.client.session_transaction() as sess:
            self.assertIn('pending_verification_email', sess)
            self.assertEqual(sess['pending_verification_email'], 'veremail@gmail.com')

    def test_register_no_otp_code_in_session(self):
        """Session must NOT contain otp_code (legacy key)."""
        resp = self.client.post('/register', data={
            'name': 'Test User',
            'email': 'nootp@gmail.com',
            'password': 'securepass',
            'math_answer': '42',
        }, follow_redirects=False)

        with self.client.session_transaction() as sess:
            self.assertNotIn('otp_code', sess)

    def test_register_no_hardcoded_123456_in_flash(self):
        """Flash messages must not contain the demo OTP '123456'."""
        resp = self.client.post('/register', data={
            'name': 'Test User',
            'email': 'nohard@gmail.com',
            'password': 'securepass',
            'math_answer': '42',
        }, follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertNotIn('123456', html)

    def test_register_supersedes_prior_active_challenge(self):
        """Re-registering same email should invalidate prior active challenge."""
        # First register
        with self.client.session_transaction() as sess:
            sess['math_captcha_answer_register'] = '42'
        self.client.post('/register', data={
            'name': 'Test User',
            'email': 'supersede@gmail.com',
            'password': 'pass1',
            'math_answer': '42',
        })

        first_challenge = OtpChallenge.query.filter_by(
            email='supersede@gmail.com', purpose='register'
        ).first()
        first_id = first_challenge.id

        # Reset session to allow re-register (clear pending_registration)
        with self.client.session_transaction() as sess:
            sess.pop('pending_registration', None)
            sess.pop('pending_otp_challenge_id', None)
            sess.pop('pending_verification_email', None)
            sess.pop('registration_email', None)
            sess['math_captcha_answer_register'] = '42'

        # Second register for same email
        self.client.post('/register', data={
            'name': 'Test User',
            'email': 'supersede@gmail.com',
            'password': 'pass2',
            'math_answer': '42',
        })

        # First challenge should be invalidated
        first_challenge = db.session.get(OtpChallenge, first_id)
        self.assertEqual(first_challenge.status, 'invalidated')
        self.assertIsNotNone(first_challenge.invalidated_at)


class OtpAuthVerifyTests(unittest.TestCase):
    """Task 2: Verify route enforces TTL, attempts, lockout, single-use."""

    @classmethod
    def setUpClass(cls):
        cls.app = create_test_app()

    def setUp(self):
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        db.session.rollback()
        self.ctx.pop()

    def _create_challenge(self, email='test@gmail.com', status='active',
                          otp_code='654321', expires_delta=300,
                          attempts_used=0, max_attempts=3):
        """Helper: create an OtpChallenge and return (challenge, plaintext_code)."""
        from utils.otp_security import hash_otp
        import secrets as sec

        salt = sec.token_hex(32)
        pepper = self.app.config.get('OTP_PEPPER', '')
        otp_hash = hash_otp(otp_code, salt, pepper)
        now = datetime.utcnow()

        challenge = OtpChallenge(
            email=email,
            purpose='register',
            otp_hash=otp_hash,
            otp_salt=salt,
            pepper_version='v1',
            attempts_used=attempts_used,
            max_attempts=max_attempts,
            issued_at=now,
            expires_at=now + timedelta(seconds=expires_delta),
            status=status,
        )
        db.session.add(challenge)
        db.session.commit()
        return challenge, otp_code

    def test_verify_correct_otp_creates_user(self):
        """Correct OTP should create the Registration and mark challenge used."""
        challenge, code = self._create_challenge(email='correct@gmail.com')

        with self.client.session_transaction() as sess:
            sess['pending_registration'] = {
                'name': 'Correct User',
                'email': 'correct@gmail.com',
                'password': 'pass',
                'city': 'HN',
            }
            sess['pending_otp_challenge_id'] = challenge.id
            sess['pending_verification_email'] = 'correct@gmail.com'

        resp = self.client.post('/verify-otp', data={'otp': code}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)

        user = Registration.query.filter_by(email='correct@gmail.com').first()
        self.assertIsNotNone(user)

        db.session.refresh(challenge)
        self.assertEqual(challenge.status, 'used')
        self.assertIsNotNone(challenge.used_at)

    def test_verify_wrong_otp_increments_attempts(self):
        """Wrong OTP should increment attempts_used."""
        challenge, _ = self._create_challenge(email='wrong@gmail.com')

        with self.client.session_transaction() as sess:
            sess['pending_registration'] = {
                'name': 'Wrong User',
                'email': 'wrong@gmail.com',
                'password': 'pass',
                'city': 'HN',
            }
            sess['pending_otp_challenge_id'] = challenge.id
            sess['pending_verification_email'] = 'wrong@gmail.com'

        self.client.post('/verify-otp', data={'otp': '000000'}, follow_redirects=True)

        db.session.refresh(challenge)
        self.assertGreater(challenge.attempts_used, 0)

    def test_verify_expired_challenge_rejected(self):
        """Expired challenge should be rejected."""
        challenge, code = self._create_challenge(
            email='expired@gmail.com', expires_delta=-60  # already expired
        )

        with self.client.session_transaction() as sess:
            sess['pending_registration'] = {
                'name': 'Expired User',
                'email': 'expired@gmail.com',
                'password': 'pass',
                'city': 'HN',
            }
            sess['pending_otp_challenge_id'] = challenge.id
            sess['pending_verification_email'] = 'expired@gmail.com'

        resp = self.client.post('/verify-otp', data={'otp': code}, follow_redirects=True)
        html = resp.get_data(as_text=True)

        user = Registration.query.filter_by(email='expired@gmail.com').first()
        self.assertIsNone(user, "User should not be created for expired challenge")

    def test_verify_lockout_after_max_attempts(self):
        """After max_attempts wrong tries, challenge should be locked."""
        challenge, code = self._create_challenge(
            email='lockout@gmail.com', attempts_used=2, max_attempts=3
        )

        with self.client.session_transaction() as sess:
            sess['pending_registration'] = {
                'name': 'Lockout User',
                'email': 'lockout@gmail.com',
                'password': 'pass',
                'city': 'HN',
            }
            sess['pending_otp_challenge_id'] = challenge.id
            sess['pending_verification_email'] = 'lockout@gmail.com'

        # This wrong attempt (3rd) should trigger lockout
        self.client.post('/verify-otp', data={'otp': '000000'}, follow_redirects=True)

        db.session.refresh(challenge)
        self.assertEqual(challenge.status, 'locked')
        self.assertIsNotNone(challenge.locked_until)

    def test_verify_used_challenge_rejected(self):
        """Already-used challenge should not allow replay."""
        challenge, code = self._create_challenge(
            email='replay@gmail.com', status='used'
        )
        challenge.used_at = datetime.utcnow()
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['pending_registration'] = {
                'name': 'Replay User',
                'email': 'replay@gmail.com',
                'password': 'pass',
                'city': 'HN',
            }
            sess['pending_otp_challenge_id'] = challenge.id
            sess['pending_verification_email'] = 'replay@gmail.com'

        resp = self.client.post('/verify-otp', data={'otp': code}, follow_redirects=True)
        user = Registration.query.filter_by(email='replay@gmail.com').first()
        self.assertIsNone(user, "User should not be created from replayed challenge")

    def test_verify_no_pending_registration_redirects(self):
        """Without pending_registration, should redirect to register."""
        resp = self.client.post('/verify-otp', data={'otp': '123456'}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)


if __name__ == '__main__':
    unittest.main()
