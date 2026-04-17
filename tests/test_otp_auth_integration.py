"""Tests for OTP auth route integration (Phase 20, Plan 02).

Validates that:
  - Register issues OTP challenge (no hardcoded fallback)
  - Verify enforces TTL, attempts, lockout, single-use
  - Template does not disclose OTP values
"""

import os
import socket
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
from models.models import AntiSpamActorState, OtpChallenge


# ---------------------------------------------------------------------------
# Test app factory
# ---------------------------------------------------------------------------

def create_test_app(overrides=None):
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
        'OTP_RESEND_COOLDOWN_SECONDS': 60,
        'OTP_RESEND_WINDOW_SECONDS': 900,
        'OTP_RESEND_MAX_PER_WINDOW': 3,
        'OTP_VERIFY_RATE_LIMIT': '10/minute;3/second',
        'OTP_RESEND_RATE_LIMIT': '5/minute;1/second',
        'OTP_ABUSE_WINDOW_MINUTES': 10,
        'OTP_ABUSE_THRESHOLD_COUNT': 3,
        'OTP_ABUSE_COOLDOWN_MINUTES': 15,
    })

    if overrides:
        app.config.update(overrides)

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

    @patch('routes.auth.send_otp_email')
    def test_register_send_success_redirects_verify(self, mock_send_otp_email):
        """When delivery succeeds, flow should redirect to verify page."""
        mock_send_otp_email.return_value = {
            'ok': True,
            'category': 'sent',
            'message': 'sent',
            'provider_message_id': 'msg-1',
        }

        resp = self.client.post('/register', data={
            'name': 'Send Success',
            'email': 'sendsuccess@gmail.com',
            'password': 'securepass',
            'math_answer': '42',
        }, follow_redirects=False)

        self.assertEqual(resp.status_code, 302)
        self.assertIn('/verify-otp', resp.location)

    @patch('routes.auth.send_otp_email')
    def test_register_send_failure_fails_closed_and_cleans_state(self, mock_send_otp_email):
        """When delivery fails, account activation must not proceed and pending state is cleared."""
        mock_send_otp_email.return_value = {
            'ok': False,
            'category': 'timeout',
            'message': 'timeout',
            'provider_message_id': None,
        }

        resp = self.client.post('/register', data={
            'name': 'Send Failure',
            'email': 'sendfail@gmail.com',
            'password': 'securepass',
            'math_answer': '42',
        }, follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn('Không thể gửi mã OTP lúc này', html)

        user = Registration.query.filter_by(email='sendfail@gmail.com').first()
        self.assertIsNone(user, 'User must not be created when OTP send fails')

        challenge = OtpChallenge.query.filter_by(email='sendfail@gmail.com', purpose='register').first()
        self.assertIsNotNone(challenge)
        self.assertEqual(challenge.status, 'invalidated')

        with self.client.session_transaction() as sess:
            self.assertNotIn('pending_registration', sess)
            self.assertNotIn('pending_otp_challenge_id', sess)
            self.assertNotIn('pending_verification_email', sess)


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

    def _set_pending_session(self, challenge, name='Pending User', password='pass', city='HN', client=None):
        target_client = client or self.client
        with target_client.session_transaction() as sess:
            sess['pending_registration'] = {
                'name': name,
                'email': challenge.email,
                'password': password,
                'city': city,
            }
            sess['pending_otp_challenge_id'] = challenge.id
            sess['pending_verification_email'] = challenge.email

    def _create_challenge(self, email='test@gmail.com', status='active',
                          otp_code='654321', expires_delta=300,
                          attempts_used=0, max_attempts=3, issued_at=None):
        """Helper: create an OtpChallenge and return (challenge, plaintext_code)."""
        from utils.otp_security import hash_otp
        import secrets as sec

        salt = sec.token_hex(32)
        pepper = self.app.config.get('OTP_PEPPER', '')
        otp_hash = hash_otp(otp_code, salt, pepper)
        now = issued_at or datetime.utcnow()

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

    def test_verify_get_renders_when_pending_state_is_valid(self):
        """GET /verify-otp should keep the flow stable when pending state is valid."""
        challenge, _ = self._create_challenge(
            email='refreshsafe@gmail.com',
            issued_at=datetime.utcnow() - timedelta(seconds=120),
        )
        self._set_pending_session(challenge, name='Refresh User')

        resp = self.client.get('/verify-otp')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('refreshsafe@gmail.com', html)
        self.assertIn('Gửi lại mã OTP', html)

    def test_verify_get_shows_cooldown_notice_and_disables_resend(self):
        """GET /verify-otp should show resend wait-state while cooldown is active."""
        challenge, _ = self._create_challenge(email='cooldownnotice@gmail.com')
        self._set_pending_session(challenge, name='Cooldown Notice User')

        resp = self.client.get('/verify-otp')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Bạn có thể gửi lại mã sau', html)
        self.assertIn('disabled aria-disabled="true"', html)

    def test_verify_get_without_pending_session_redirects_register(self):
        """GET /verify-otp should redirect safely when pending state is missing."""
        resp = self.client.get('/verify-otp', follow_redirects=False)

        self.assertEqual(resp.status_code, 302)
        self.assertIn('/register', resp.location)

    def test_verify_get_expired_challenge_redirects_and_clears_session(self):
        """Expired pending challenge on GET should clear pending state and redirect."""
        challenge, _ = self._create_challenge(
            email='expiredget@gmail.com',
            issued_at=datetime.utcnow() - timedelta(seconds=600),
            expires_delta=300,
        )
        self._set_pending_session(challenge, name='Expired Get User')

        resp = self.client.get('/verify-otp', follow_redirects=False)

        self.assertEqual(resp.status_code, 302)
        self.assertIn('/register', resp.location)
        with self.client.session_transaction() as sess:
            self.assertNotIn('pending_registration', sess)
            self.assertNotIn('pending_otp_challenge_id', sess)
            self.assertNotIn('pending_verification_email', sess)

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

    @patch('routes.auth.send_otp_email')
    def test_resend_without_pending_session_redirects_register(self, mock_send_otp_email):
        """Resend must deny when the pending verify session state is missing."""
        resp = self.client.post('/verify-otp/resend', follow_redirects=False)

        self.assertEqual(resp.status_code, 302)
        self.assertIn('/register', resp.location)
        mock_send_otp_email.assert_not_called()


class OtpAuthAbuseGuardrailTests(unittest.TestCase):
    def setUp(self):
        self.app = create_test_app({
            'RATELIMIT_ENABLED': True,
            'OTP_VERIFY_RATE_LIMIT': '2/minute',
            'OTP_RESEND_RATE_LIMIT': '2/minute',
            'OTP_RESEND_COOLDOWN_SECONDS': 60,
            'OTP_RESEND_MAX_PER_WINDOW': 3,
            'OTP_MAX_ATTEMPTS': 10,
            'OTP_ABUSE_THRESHOLD_COUNT': 2,
        })
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        db.session.rollback()
        db.drop_all()
        self.ctx.pop()

    def _set_pending_session(self, challenge, name='Guardrail User', password='pass', city='HN', client=None):
        target_client = client or self.client
        with target_client.session_transaction() as sess:
            sess['pending_registration'] = {
                'name': name,
                'email': challenge.email,
                'password': password,
                'city': city,
            }
            sess['pending_otp_challenge_id'] = challenge.id
            sess['pending_verification_email'] = challenge.email

    def _create_challenge(self, email='guardrail@gmail.com', status='active', otp_code='654321', issued_at=None):
        from utils.otp_security import hash_otp
        import secrets as sec

        salt = sec.token_hex(32)
        otp_hash = hash_otp(otp_code, salt, self.app.config.get('OTP_PEPPER', ''))
        now = issued_at or datetime.utcnow()

        challenge = OtpChallenge(
            email=email,
            purpose='register',
            otp_hash=otp_hash,
            otp_salt=salt,
            pepper_version='v1',
            attempts_used=0,
            max_attempts=self.app.config.get('OTP_MAX_ATTEMPTS', 10),
            issued_at=now,
            expires_at=now + timedelta(seconds=300),
            status=status,
        )
        db.session.add(challenge)
        db.session.commit()
        return challenge, otp_code

    def test_verify_invalid_attempts_sync_anti_spam_cooldown_to_challenge(self):
        from services.otp_abuse_guard import build_otp_actor_id

        challenge, _ = self._create_challenge(email='abuseverify@gmail.com')
        self._set_pending_session(challenge, name='Abuse Verify User')

        first = self.client.post('/verify-otp', data={'otp': '000000'}, follow_redirects=False)
        second = self.client.post('/verify-otp', data={'otp': '000000'}, follow_redirects=False)

        actor_state = AntiSpamActorState.query.filter_by(
            actor_key=f"acct:{build_otp_actor_id('abuseverify@gmail.com')}"
        ).first()

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 302)
        self.assertIsNotNone(actor_state)

        db.session.refresh(challenge)
        self.assertEqual(challenge.status, 'locked')
        self.assertIsNotNone(challenge.locked_until)
        self.assertEqual(challenge.locked_until, actor_state.cooldown_until)

    def test_verify_get_uses_anti_spam_cooldown_to_disable_resend(self):
        from services.otp_abuse_guard import build_otp_actor_id

        challenge, _ = self._create_challenge(email='cooldownrender@gmail.com')
        self._set_pending_session(challenge, name='Cooldown Render User')

        actor_state = AntiSpamActorState(
            actor_key=f"acct:{build_otp_actor_id('cooldownrender@gmail.com')}",
            actor_type='account',
            cooldown_until=datetime.utcnow() + timedelta(minutes=5),
            window_count=2,
            last_risk_score=100,
            last_risk_level='high',
        )
        db.session.add(actor_state)
        db.session.commit()

        resp = self.client.get('/verify-otp')
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Bạn có thể gửi lại mã sau', html)
        self.assertIn('disabled aria-disabled="true"', html)

    def test_verify_normal_success_still_passes_under_guardrails(self):
        challenge, code = self._create_challenge(email='guardrailsuccess@gmail.com')
        self._set_pending_session(challenge, name='Guardrail Success User')

        resp = self.client.post('/verify-otp', data={'otp': code}, follow_redirects=False)

        self.assertEqual(resp.status_code, 302)
        user = Registration.query.filter_by(email='guardrailsuccess@gmail.com').first()
        self.assertIsNotNone(user)

    def test_verify_post_rate_limit_returns_429(self):
        challenge, _ = self._create_challenge(email='verifylimit@gmail.com')
        self._set_pending_session(challenge, name='Verify Limit User')

        first = self.client.post('/verify-otp', data={'otp': '000000'}, follow_redirects=False)
        second = self.client.post('/verify-otp', data={'otp': '000000'}, follow_redirects=False)
        third = self.client.post('/verify-otp', data={'otp': '000000'}, follow_redirects=False)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(third.status_code, 429)

    @patch('routes.auth.send_otp_email')
    def test_resend_post_rate_limit_returns_429(self, mock_send_otp_email):
        mock_send_otp_email.return_value = {
            'ok': True,
            'category': 'sent',
            'message': 'sent',
            'provider_message_id': 'msg-rate',
        }
        first_challenge, _ = self._create_challenge(
            email='resendlimit1@gmail.com',
            issued_at=datetime.utcnow() - timedelta(seconds=120),
        )
        self._set_pending_session(first_challenge, name='Resend Limit User 1')
        first = self.client.post('/verify-otp/resend', follow_redirects=False)

        second_challenge, _ = self._create_challenge(
            email='resendlimit2@gmail.com',
            issued_at=datetime.utcnow() - timedelta(seconds=120),
        )
        self._set_pending_session(second_challenge, name='Resend Limit User 2')
        second = self.client.post('/verify-otp/resend', follow_redirects=False)

        third_challenge, _ = self._create_challenge(
            email='resendlimit3@gmail.com',
            issued_at=datetime.utcnow() - timedelta(seconds=120),
        )
        self._set_pending_session(third_challenge, name='Resend Limit User 3')
        third = self.client.post('/verify-otp/resend', follow_redirects=False)

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(third.status_code, 429)
        self.assertEqual(mock_send_otp_email.call_count, 2)

    @patch('routes.auth.send_otp_email')
    def test_resend_success_replaces_challenge_and_updates_session(self, mock_send_otp_email):
        """Successful resend should activate a replacement challenge and update session state."""
        mock_send_otp_email.return_value = {
            'ok': True,
            'category': 'sent',
            'message': 'sent',
            'provider_message_id': 'msg-2',
        }
        current_challenge, _ = self._create_challenge(
            email='resendsuccess@gmail.com',
            issued_at=datetime.utcnow() - timedelta(seconds=120),
        )
        self._set_pending_session(current_challenge, name='Resend Success User')

        resp = self.client.post('/verify-otp/resend', follow_redirects=False)

        self.assertEqual(resp.status_code, 302)
        self.assertIn('/verify-otp', resp.location)
        challenges = OtpChallenge.query.filter_by(
            email='resendsuccess@gmail.com', purpose='register'
        ).order_by(OtpChallenge.issued_at.asc(), OtpChallenge.id.asc()).all()
        self.assertEqual(len(challenges), 2)

        original_challenge, replacement_challenge = challenges
        db.session.refresh(original_challenge)
        db.session.refresh(replacement_challenge)
        self.assertEqual(original_challenge.status, 'invalidated')
        self.assertEqual(replacement_challenge.status, 'active')

        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('pending_otp_challenge_id'), replacement_challenge.id)
            self.assertEqual(sess.get('pending_verification_email'), 'resendsuccess@gmail.com')

        mock_send_otp_email.assert_called_once()

    @patch('routes.auth.send_otp_email')
    def test_resend_send_failure_rolls_back_and_keeps_current_challenge(self, mock_send_otp_email):
        """Delivery failure during resend must keep the existing challenge/session intact."""
        mock_send_otp_email.return_value = {
            'ok': False,
            'category': 'timeout',
            'message': 'timeout',
            'provider_message_id': None,
        }
        current_challenge, _ = self._create_challenge(
            email='resendfail@gmail.com',
            issued_at=datetime.utcnow() - timedelta(seconds=120),
        )
        self._set_pending_session(current_challenge, name='Resend Failure User')

        resp = self.client.post('/verify-otp/resend', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('Không thể gửi lại mã OTP lúc này', html)

        challenges = OtpChallenge.query.filter_by(
            email='resendfail@gmail.com',
            purpose='register',
        ).order_by(OtpChallenge.issued_at.asc(), OtpChallenge.id.asc()).all()
        self.assertEqual(len(challenges), 1)
        db.session.refresh(current_challenge)
        self.assertEqual(current_challenge.status, 'active')

        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('pending_otp_challenge_id'), current_challenge.id)
            self.assertEqual(sess.get('pending_verification_email'), 'resendfail@gmail.com')

        mock_send_otp_email.assert_called_once()

    @patch('routes.auth.send_otp_email')
    def test_resend_during_cooldown_keeps_current_challenge(self, mock_send_otp_email):
        """Cooldown denial must not replace the current pending challenge."""
        current_challenge, _ = self._create_challenge(email='cooldown@gmail.com')
        self._set_pending_session(current_challenge, name='Cooldown User')

        resp = self.client.post('/verify-otp/resend', follow_redirects=False)

        self.assertEqual(resp.status_code, 302)
        self.assertIn('/verify-otp', resp.location)
        self.assertEqual(
            OtpChallenge.query.filter_by(email='cooldown@gmail.com', purpose='register').count(),
            1,
        )
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('pending_otp_challenge_id'), current_challenge.id)

        mock_send_otp_email.assert_not_called()

    @patch('routes.auth.send_otp_email')
    def test_resend_cap_denial_keeps_current_challenge(self, mock_send_otp_email):
        """Window cap denial must not create a replacement challenge."""
        base_time = datetime.utcnow() - timedelta(seconds=360)
        first_challenge, _ = self._create_challenge(
            email='caplimit@gmail.com',
            issued_at=base_time,
        )
        second_challenge, _ = self._create_challenge(
            email='caplimit@gmail.com',
            issued_at=base_time + timedelta(seconds=80),
        )
        third_challenge, _ = self._create_challenge(
            email='caplimit@gmail.com',
            issued_at=base_time + timedelta(seconds=160),
        )
        current_challenge, _ = self._create_challenge(
            email='caplimit@gmail.com',
            issued_at=base_time + timedelta(seconds=240),
        )
        first_challenge.status = 'invalidated'
        second_challenge.status = 'invalidated'
        third_challenge.status = 'invalidated'
        db.session.commit()

        self._set_pending_session(current_challenge, name='Cap User')

        resp = self.client.post('/verify-otp/resend', follow_redirects=True)
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('gửi lại mã quá nhiều lần', html)
        self.assertEqual(
            OtpChallenge.query.filter_by(email='caplimit@gmail.com', purpose='register').count(),
            4,
        )
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('pending_otp_challenge_id'), current_challenge.id)

        mock_send_otp_email.assert_not_called()

    def test_concurrent_verify_allows_only_one_successful_use(self):
        """Two clients using the same pending challenge should yield only one successful verification."""
        challenge, code = self._create_challenge(email='concurrent@gmail.com')

        first_client = self.app.test_client()
        second_client = self.app.test_client()
        self._set_pending_session(challenge, name='Concurrent User', client=first_client)
        self._set_pending_session(challenge, name='Concurrent User', client=second_client)

        first = first_client.post('/verify-otp', data={'otp': code}, follow_redirects=False)
        second = second_client.post('/verify-otp', data={'otp': code}, follow_redirects=False)

        self.assertEqual(first.status_code, 302)
        self.assertIn('/onboarding', first.location)
        self.assertEqual(second.status_code, 302)
        self.assertIn('/register', second.location)
        self.assertEqual(Registration.query.filter_by(email='concurrent@gmail.com').count(), 1)

        db.session.refresh(challenge)
        self.assertEqual(challenge.status, 'used')

        with second_client.session_transaction() as sess:
            self.assertNotIn('pending_registration', sess)
            self.assertNotIn('pending_otp_challenge_id', sess)
            self.assertNotIn('pending_verification_email', sess)


class OtpAuthSmtpCutoverTests(unittest.TestCase):
    def setUp(self):
        self.app = create_test_app({
            'TESTING': False,
            'EMAIL_PROVIDER': 'smtp',
            'SMTP_HOST': 'smtp.gmail.com',
            'SMTP_PORT': 587,
            'SMTP_USERNAME': 'mindguard.smtp@gmail.com',
            'SMTP_PASSWORD': 'app-password-1234',
            'SMTP_USE_TLS': True,
            'SMTP_USE_SSL': False,
            'SMTP_FROM_EMAIL': 'mindguard.smtp@gmail.com',
            'MAIL_SERVER': 'smtp.gmail.com',
            'MAIL_PORT': 587,
            'MAIL_USERNAME': 'mindguard.smtp@gmail.com',
            'MAIL_PASSWORD': 'app-password-1234',
            'MAIL_USE_TLS': True,
            'MAIL_USE_SSL': False,
            'MAIL_DEFAULT_SENDER': 'mindguard.smtp@gmail.com',
        })
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        with self.client.session_transaction() as sess:
            sess['math_captcha_answer_register'] = '42'

    def tearDown(self):
        db.session.rollback()
        db.drop_all()
        self.ctx.pop()

    def _set_pending_session(self, challenge, name='SMTP User', password='pass', city='HN', client=None):
        target_client = client or self.client
        with target_client.session_transaction() as sess:
            sess['pending_registration'] = {
                'name': name,
                'email': challenge.email,
                'password': password,
                'city': city,
            }
            sess['pending_otp_challenge_id'] = challenge.id
            sess['pending_verification_email'] = challenge.email

    def _create_challenge(self, email='smtpuser@gmail.com', status='active', otp_code='654321', issued_at=None):
        from utils.otp_security import hash_otp
        import secrets as sec

        salt = sec.token_hex(32)
        otp_hash = hash_otp(otp_code, salt, self.app.config.get('OTP_PEPPER', ''))
        now = issued_at or datetime.utcnow()

        challenge = OtpChallenge(
            email=email,
            purpose='register',
            otp_hash=otp_hash,
            otp_salt=salt,
            pepper_version='v1',
            attempts_used=0,
            max_attempts=self.app.config.get('OTP_MAX_ATTEMPTS', 3),
            issued_at=now,
            expires_at=now + timedelta(seconds=300),
            status=status,
        )
        db.session.add(challenge)
        db.session.commit()
        return challenge, otp_code

    @patch('services.otp_email_delivery.mail.send')
    def test_register_smtp_success_redirects_verify_and_uses_mail_transport(self, mock_mail_send):
        resp = self.client.post('/register', data={
            'name': 'SMTP Success',
            'email': 'smtpregistersuccess@gmail.com',
            'password': 'securepass',
            'math_answer': '42',
        }, follow_redirects=False)

        self.assertEqual(resp.status_code, 302)
        self.assertIn('/verify-otp', resp.location)
        mock_mail_send.assert_called_once()
        message = mock_mail_send.call_args.args[0]
        self.assertEqual(message.sender, 'mindguard.smtp@gmail.com')
        self.assertEqual(message.recipients, ['smtpregistersuccess@gmail.com'])

        challenge = OtpChallenge.query.filter_by(
            email='smtpregistersuccess@gmail.com',
            purpose='register',
        ).first()
        self.assertIsNotNone(challenge)
        self.assertEqual(challenge.status, 'active')

    def test_register_smtp_misconfigured_fails_closed_and_logs_diagnostic(self):
        self.app.config.update({
            'SMTP_HOST': '',
            'MAIL_SERVER': '',
        })

        with self.assertLogs(self.app.logger.name, level='WARNING') as captured:
            resp = self.client.post('/register', data={
                'name': 'SMTP Broken',
                'email': 'smtpmisconfigured@gmail.com',
                'password': 'securepass',
                'math_answer': '42',
            }, follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn('Không thể gửi mã OTP lúc này', html)
        self.assertIn('category=misconfigured', '\n'.join(captured.output))
        self.assertIn('missing=SMTP_HOST', '\n'.join(captured.output))

        challenge = OtpChallenge.query.filter_by(
            email='smtpmisconfigured@gmail.com',
            purpose='register',
        ).first()
        self.assertIsNotNone(challenge)
        self.assertEqual(challenge.status, 'invalidated')

    @patch('services.otp_email_delivery.mail.send')
    def test_resend_smtp_success_replaces_challenge_and_updates_session(self, mock_mail_send):
        current_challenge, _ = self._create_challenge(
            email='smtpresendsuccess@gmail.com',
            issued_at=datetime.utcnow() - timedelta(seconds=120),
        )
        self._set_pending_session(current_challenge, name='SMTP Resend Success')

        resp = self.client.post('/verify-otp/resend', follow_redirects=False)

        self.assertEqual(resp.status_code, 302)
        self.assertIn('/verify-otp', resp.location)
        mock_mail_send.assert_called_once()
        message = mock_mail_send.call_args.args[0]
        self.assertEqual(message.sender, 'mindguard.smtp@gmail.com')
        self.assertEqual(message.recipients, ['smtpresendsuccess@gmail.com'])

        challenges = OtpChallenge.query.filter_by(
            email='smtpresendsuccess@gmail.com', purpose='register'
        ).order_by(OtpChallenge.issued_at.asc(), OtpChallenge.id.asc()).all()
        self.assertEqual(len(challenges), 2)
        original_challenge, replacement_challenge = challenges
        self.assertEqual(original_challenge.status, 'invalidated')
        self.assertEqual(replacement_challenge.status, 'active')

        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('pending_otp_challenge_id'), replacement_challenge.id)

    @patch('services.otp_email_delivery.mail.send', side_effect=socket.timeout('timed out'))
    def test_resend_smtp_timeout_keeps_current_challenge_and_logs_diagnostic(self, mock_mail_send):
        current_challenge, _ = self._create_challenge(
            email='smtpresendtimeout@gmail.com',
            issued_at=datetime.utcnow() - timedelta(seconds=120),
        )
        self._set_pending_session(current_challenge, name='SMTP Resend Timeout')

        with self.assertLogs(self.app.logger.name, level='WARNING') as captured:
            resp = self.client.post('/verify-otp/resend', follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        html = resp.get_data(as_text=True)
        self.assertIn('Không thể gửi lại mã OTP lúc này', html)
        self.assertIn('provider=smtp', '\n'.join(captured.output))
        self.assertIn('provider_hint=gmail_app_password', '\n'.join(captured.output))
        self.assertIn('category=timeout', '\n'.join(captured.output))

        challenges = OtpChallenge.query.filter_by(
            email='smtpresendtimeout@gmail.com',
            purpose='register',
        ).order_by(OtpChallenge.issued_at.asc(), OtpChallenge.id.asc()).all()
        self.assertEqual(len(challenges), 1)
        db.session.refresh(current_challenge)
        self.assertEqual(current_challenge.status, 'active')

        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('pending_otp_challenge_id'), current_challenge.id)

        mock_mail_send.assert_called_once()


if __name__ == '__main__':
    unittest.main()
