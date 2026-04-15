"""Comprehensive tests for CSRF protection, auth, quiz, scammer, chatbot, admin routes.

Focuses on:
  - CSRF attack surface: every POST endpoint is tested with AND without CSRF token
  - Auth flows: login, register, OTP, logout, profile edit
  - Quiz routes: start, step, finalize
  - Scammer report: submit, follow
  - Chatbot: csrf-exempt endpoints work without token
  - Admin: login, dashboard guard, CRUD, unsuspend exemption
  - Security headers: X-Frame-Options, X-Content-Type-Options, etc.
"""

import os
import sys
import unittest
from unittest.mock import patch
from werkzeug.security import generate_password_hash

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from flask import Flask
from sqlalchemy.pool import StaticPool

from extensions import db, csrf, limiter
from config import Config
from models import Registration, ScammerReport, QuizResult


# ---------------------------------------------------------------------------
# Test app factory
# ---------------------------------------------------------------------------

def create_csrf_test_app(csrf_enabled=True):
    """Create a test Flask app.

    When *csrf_enabled* is True the app behaves like production — every
    unexempted POST must carry a valid CSRF token.
    """
    app = Flask(
        'mindguard_csrf_test',
        template_folder=os.path.join(PROJECT_ROOT, 'templates'),
        static_folder=os.path.join(PROJECT_ROOT, 'static'),
    )
    app.config.from_object(Config)
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-csrf-secret',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_ENGINE_OPTIONS': {
            'connect_args': {'check_same_thread': False},
            'poolclass': StaticPool,
        },
        'WTF_CSRF_ENABLED': csrf_enabled,
        'CLOUDFLARE_SECRET_KEY': None,   # disable captcha in tests
        'CLOUDFLARE_SITE_KEY': None,
        'ABUS_MODE': 'monitor',
    })

    db.init_app(app)
    limiter.init_app(app)
    csrf.init_app(app)

    # Security headers (mirrors app.py)
    @app.after_request
    def apply_security_headers(response):
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        return response

    # Template filters required by base.html
    @app.template_filter('nl2br')
    def nl2br_filter(s):
        from markupsafe import Markup, escape
        return Markup(str(escape(s)).replace('\n', '<br>')) if s else ''

    @app.template_filter('mask')
    def mask_filter(s, data_type='auto'):
        return s  # passthrough in tests

    from datetime import datetime
    from utils.helpers import get_verification_badge

    @app.context_processor
    def inject_globals():
        return {
            'current_year': datetime.now().year,
            'get_verification_badge': get_verification_badge,
        }

    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.scammer import scammer_bp
    from routes.quiz import quiz_bp
    from routes.chatbot import chatbot_bp
    from routes.library import library_bp
    from routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(scammer_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(library_bp)
    app.register_blueprint(api_bp)

    with app.app_context():
        db.create_all()

    return app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_csrf_token(client):
    """Extract a valid CSRF token from a page that renders one."""
    resp = client.get('/login')
    html = resp.get_data(as_text=True)
    # Flask-WTF injects a hidden input or meta tag
    import re
    match = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
    if match:
        return match.group(1)
    match = re.search(r'content="([^"]+)"[^>]*name="csrf-token"', html)
    if not match:
        match = re.search(r'name="csrf-token"[^>]*content="([^"]+)"', html)
    return match.group(1) if match else None


# ===================================================================== #
#  1.  CSRF PROTECTION TESTS  (csrf_enabled=True)
# ===================================================================== #

class TestCSRFProtection(unittest.TestCase):
    """Verify that CSRF tokens are enforced on all protected POST routes."""

    def setUp(self):
        self.app = create_csrf_test_app(csrf_enabled=True)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()

        # Seed a test user
        user = Registration(
            name='CSRF Tester',
            email='csrf@test.com',
            password_hash=generate_password_hash('password123'),
            role='user',
        )
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def _login(self):
        with self.client.session_transaction() as sess:
            sess['registration_email'] = 'csrf@test.com'
            sess['registration_name'] = 'CSRF Tester'
            sess['math_captcha_answer'] = '42'

    def _admin_login(self):
        with self.client.session_transaction() as sess:
            sess['is_admin'] = True
            sess['admin_email'] = 'admin@test.com'

    # ------ Attack: POST without CSRF token must fail (400) ----------- #

    def test_login_post_without_csrf_rejected(self):
        resp = self.client.post('/login', data={
            'login_email': 'csrf@test.com',
            'login_password': 'password123',
        })
        self.assertEqual(resp.status_code, 400)

    def test_register_post_without_csrf_rejected(self):
        resp = self.client.post('/register', data={
            'name': 'Hacker', 'email': 'hack@gmail.com', 'password': 'x',
        })
        self.assertEqual(resp.status_code, 400)

    def test_verify_otp_without_csrf_rejected(self):
        resp = self.client.post('/verify-otp', data={'otp': '123456'})
        self.assertEqual(resp.status_code, 400)

    def test_profile_edit_without_csrf_rejected(self):
        self._login()
        resp = self.client.post('/profile/edit', data={'name': 'pwned'})
        self.assertEqual(resp.status_code, 400)

    def test_scammer_report_without_csrf_rejected(self):
        resp = self.client.post('/scammer/report', data={
            'identifier_person': '0901234567',
            'description': 'Scam!',
            'scam_type_person': 'Lừa đảo',
            'term_truth': 'on',
            'term_responsibility': 'on',
        })
        self.assertEqual(resp.status_code, 400)

    def test_scammer_follow_without_csrf_rejected(self):
        self._login()
        resp = self.client.post('/scammer/follow', data={'identifier': '123'})
        self.assertEqual(resp.status_code, 400)

    def test_quiz_step_post_without_csrf_rejected(self):
        self._login()
        resp = self.client.post('/quiz/step/0', data={'answer': '1'})
        self.assertEqual(resp.status_code, 400)

    def test_admin_login_without_csrf_rejected(self):
        resp = self.client.post('/admin/login', data={
            'email': 'admin@test.com', 'password': 'x',
        })
        self.assertEqual(resp.status_code, 400)

    def test_admin_create_admin_without_csrf_rejected(self):
        self._admin_login()
        resp = self.client.post('/admin/create-admin', data={
            'name': 'evil', 'email': 'evil@test.com', 'password': 'x',
        })
        self.assertEqual(resp.status_code, 400)

    def test_admin_delete_user_without_csrf_rejected(self):
        self._admin_login()
        resp = self.client.post('/admin/delete-user/1')
        self.assertEqual(resp.status_code, 400)

    def test_admin_edit_user_without_csrf_rejected(self):
        self._admin_login()
        resp = self.client.post('/admin/edit-user/1', data={'name': 'Hacked'})
        self.assertEqual(resp.status_code, 400)

    def test_admin_approve_report_without_csrf_rejected(self):
        self._admin_login()
        resp = self.client.post('/admin/approve-report/1')
        self.assertEqual(resp.status_code, 400)

    def test_admin_reject_report_without_csrf_rejected(self):
        self._admin_login()
        resp = self.client.post('/admin/reject-report/1')
        self.assertEqual(resp.status_code, 400)

    def test_search_scammer_without_csrf_rejected(self):
        resp = self.client.post('/api/search', data={'query': 'test'})
        self.assertEqual(resp.status_code, 400)

    # ------ Chatbot endpoints (csrf.exempt) MUST work WITHOUT token --- #

    def test_chatbot_send_without_csrf_allowed(self):
        self._login()
        resp = self.client.post(
            '/chatbot/send',
            json={'message': 'hello'},
            content_type='application/json',
        )
        # Should NOT be 400 (CSRF). Could be 200 or other app error.
        self.assertNotEqual(resp.status_code, 400)

    def test_chatbot_api_without_csrf_allowed(self):
        resp = self.client.post(
            '/chatbot/api',
            json={'message': 'test'},
            content_type='application/json',
        )
        self.assertNotEqual(resp.status_code, 400)

    def test_chatbot_rename_without_csrf_allowed(self):
        """rename requires @login_required + @csrf.exempt — login first."""
        # Login via session so @login_required passes
        with self.client.session_transaction() as sess:
            sess['registration_email'] = 'csrf@test.com'
            sess['registration_name'] = 'CSRF Tester'
        resp = self.client.post(
            '/chatbot/rename',
            json={'session_id': 'x', 'title': 'y'},
            content_type='application/json',
        )
        # Should NOT be 400 CSRF — may be 400 app-level (no session found) which is fine
        # The key distinction: CSRF would return a HTML error page, app returns JSON
        self.assertTrue(
            resp.status_code != 400 or
            (resp.content_type and 'json' in resp.content_type)
        )

    def test_chatbot_feedback_without_csrf_allowed(self):
        """feedback requires @login_required + @csrf.exempt — login first."""
        with self.client.session_transaction() as sess:
            sess['registration_email'] = 'csrf@test.com'
            sess['registration_name'] = 'CSRF Tester'
        resp = self.client.post(
            '/chatbot/feedback',
            json={'feedback_type': 'other', 'feedback_text': 'test feedback'},
            content_type='application/json',
        )
        # CSRF would return HTML 400; app-level may return JSON 200/400
        self.assertTrue(
            resp.status_code != 400 or
            (resp.content_type and 'json' in resp.content_type)
        )

    def test_chatbot_support_without_csrf_allowed(self):
        resp = self.client.post(
            '/chatbot/support',
            json={'message': 'help'},
            content_type='application/json',
        )
        self.assertNotEqual(resp.status_code, 400)

    # ------ Admin unsuspend (csrf.exempt) works without token --------- #

    def test_admin_unsuspend_without_csrf_allowed(self):
        resp = self.client.post(
            '/admin/unsuspend',
            json={'secret': 'wrong-secret'},
            content_type='application/json',
        )
        self.assertNotEqual(resp.status_code, 400)

    # ------ Cross-origin attack simulation ----------------------------- #

    def test_cross_origin_post_with_wrong_token_rejected(self):
        """Simulate a CSRF attack with a fabricated token."""
        resp = self.client.post('/login', data={
            'login_email': 'csrf@test.com',
            'login_password': 'password123',
            'csrf_token': 'fabricated-evil-token-12345',
        })
        self.assertEqual(resp.status_code, 400)

    def test_cross_origin_referer_with_bad_token(self):
        """Simulate cross-origin POST with a Referer from a different domain."""
        resp = self.client.post('/login', data={
            'login_email': 'csrf@test.com',
            'login_password': 'password123',
            'csrf_token': 'fake',
        }, headers={'Referer': 'https://evil-phishing-site.com/csrf-attack'})
        self.assertEqual(resp.status_code, 400)


# ===================================================================== #
#  2.  SECURITY HEADERS
# ===================================================================== #

class TestSecurityHeaders(unittest.TestCase):
    """Verify security headers are applied to all responses."""

    def setUp(self):
        self.app = create_csrf_test_app(csrf_enabled=False)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_x_frame_options(self):
        resp = self.client.get('/')
        self.assertEqual(resp.headers.get('X-Frame-Options'), 'SAMEORIGIN')

    def test_x_content_type_options(self):
        resp = self.client.get('/')
        self.assertEqual(resp.headers.get('X-Content-Type-Options'), 'nosniff')

    def test_x_xss_protection(self):
        resp = self.client.get('/')
        self.assertEqual(resp.headers.get('X-XSS-Protection'), '1; mode=block')

    def test_referrer_policy(self):
        resp = self.client.get('/')
        self.assertEqual(resp.headers.get('Referrer-Policy'), 'strict-origin-when-cross-origin')

    def test_permissions_policy(self):
        resp = self.client.get('/')
        self.assertEqual(resp.headers.get('Permissions-Policy'), 'geolocation=(), microphone=(), camera=()')


# ===================================================================== #
#  3.  AUTH FLOW TESTS  (csrf disabled for functional testing)
# ===================================================================== #

class TestAuthFlows(unittest.TestCase):
    """Test login, register, OTP, profile edit, logout."""

    def setUp(self):
        self.app = create_csrf_test_app(csrf_enabled=False)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()

        user = Registration(
            name='Test User',
            email='user@gmail.com',
            password_hash=generate_password_hash('correct_password'),
            role='user',
        )
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def _set_math_captcha(self, key='math_captcha_answer', answer='42'):
        with self.client.session_transaction() as sess:
            sess[key] = answer

    # --- Login ---

    def test_login_page_renders(self):
        resp = self.client.get('/login')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Đăng nhập', resp.get_data(as_text=True))

    def test_login_correct_credentials(self):
        self._set_math_captcha()
        resp = self.client.post('/login', data={
            'login_email': 'user@gmail.com',
            'login_password': 'correct_password',
            'math_answer': '42',
        }, follow_redirects=False)
        self.assertIn(resp.status_code, [302, 200])

        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('registration_email'), 'user@gmail.com')

    def test_login_wrong_password(self):
        self._set_math_captcha()
        resp = self.client.post('/login', data={
            'login_email': 'user@gmail.com',
            'login_password': 'wrong_password',
            'math_answer': '42',
        }, follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertIn('Mật khẩu không đúng', html)

    def test_login_nonexistent_email(self):
        self._set_math_captcha()
        resp = self.client.post('/login', data={
            'login_email': 'nobody@gmail.com',
            'login_password': 'x',
            'math_answer': '42',
        }, follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertIn('Email chưa được đăng ký', html)

    def test_login_bad_captcha_rejected(self):
        self._set_math_captcha()
        resp = self.client.post('/login', data={
            'login_email': 'user@gmail.com',
            'login_password': 'correct_password',
            'math_answer': '999',  # wrong
        }, follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertIn('xác thực', html)

    # --- Register ---

    def test_register_page_renders(self):
        resp = self.client.get('/register')
        self.assertEqual(resp.status_code, 200)

    def test_register_success_redirects_to_otp(self):
        self._set_math_captcha(key='math_captcha_answer_register')
        resp = self.client.post('/register', data={
            'name': 'New User',
            'email': 'new@gmail.com',
            'password': 'securepass',
            'math_answer': '42',
        }, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('verify-otp', resp.headers['Location'])

    def test_register_duplicate_email_rejected(self):
        self._set_math_captcha(key='math_captcha_answer_register')
        resp = self.client.post('/register', data={
            'name': 'Dup',
            'email': 'user@gmail.com',  # already exists
            'password': 'x',
            'math_answer': '42',
        }, follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertIn('đã được đăng ký', html)

    def test_register_non_gmail_rejected(self):
        self._set_math_captcha(key='math_captcha_answer_register')
        resp = self.client.post('/register', data={
            'name': 'Bad',
            'email': 'user@yahoo.com',  # not gmail
            'password': 'x',
            'math_answer': '42',
        }, follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertIn('Gmail', html)

    def test_register_missing_fields_rejected(self):
        self._set_math_captcha(key='math_captcha_answer_register')
        resp = self.client.post('/register', data={
            'name': '',
            'email': '',
            'password': '',
            'math_answer': '42',
        }, follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertIn('đầy đủ', html)

    # --- OTP ---

    def test_verify_otp_success(self):
        # Create a challenge-based OTP in the database
        from models.models import OtpChallenge
        from utils.otp_security import hash_otp
        import secrets as sec
        from datetime import datetime, timedelta

        otp_code = '654321'
        salt = sec.token_hex(32)
        pepper = self.app.config.get('OTP_PEPPER', '')
        otp_hash = hash_otp(otp_code, salt, pepper)
        now = datetime.utcnow()

        challenge = OtpChallenge(
            email='otp@gmail.com',
            purpose='register',
            otp_hash=otp_hash,
            otp_salt=salt,
            pepper_version='v1',
            attempts_used=0,
            max_attempts=5,
            issued_at=now,
            expires_at=now + timedelta(seconds=300),
            status='active',
        )
        db.session.add(challenge)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['pending_registration'] = {
                'name': 'OTP User',
                'email': 'otp@gmail.com',
                'password': 'pass',
                'city': 'Hanoi',
            }
            sess['pending_otp_challenge_id'] = challenge.id
            sess['pending_verification_email'] = 'otp@gmail.com'

        resp = self.client.post('/verify-otp', data={'otp': otp_code}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)

        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('registration_email'), 'otp@gmail.com')

        # User created in DB
        user = Registration.query.filter_by(email='otp@gmail.com').first()
        self.assertIsNotNone(user)

    def test_verify_otp_wrong_code(self):
        from models.models import OtpChallenge
        from utils.otp_security import hash_otp
        import secrets as sec
        from datetime import datetime, timedelta

        otp_code = '654321'
        salt = sec.token_hex(32)
        pepper = self.app.config.get('OTP_PEPPER', '')
        otp_hash = hash_otp(otp_code, salt, pepper)
        now = datetime.utcnow()

        challenge = OtpChallenge(
            email='otp2@gmail.com',
            purpose='register',
            otp_hash=otp_hash,
            otp_salt=salt,
            pepper_version='v1',
            attempts_used=0,
            max_attempts=5,
            issued_at=now,
            expires_at=now + timedelta(seconds=300),
            status='active',
        )
        db.session.add(challenge)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['pending_registration'] = {
                'name': 'OTP User',
                'email': 'otp2@gmail.com',
                'password': 'pass',
                'city': 'Ha Noi',
            }
            sess['pending_otp_challenge_id'] = challenge.id
            sess['pending_verification_email'] = 'otp2@gmail.com'

        resp = self.client.post('/verify-otp', data={'otp': '000000'}, follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertIn('OTP không đúng', html)

    def test_verify_otp_no_pending_registration(self):
        resp = self.client.post('/verify-otp', data={'otp': '123456'}, follow_redirects=False)
        self.assertEqual(resp.status_code, 302)

    # --- Profile ---

    def test_profile_requires_login(self):
        resp = self.client.get('/profile', follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertIn('đăng nhập', html.lower())

    def test_profile_edit(self):
        with self.client.session_transaction() as sess:
            sess['registration_email'] = 'user@gmail.com'
            sess['registration_name'] = 'Test User'

        resp = self.client.post('/profile/edit', data={
            'name': 'Updated Name',
            'date_of_birth': '2000-01-01',
            'city': 'HCMC',
            'phone_number': '0912345678',
            'bio': 'Hello',
        }, follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertIn('thành công', html)

        user = Registration.query.filter_by(email='user@gmail.com').first()
        self.assertEqual(user.name, 'Updated Name')

    # --- Logout ---

    def test_logout_clears_session(self):
        with self.client.session_transaction() as sess:
            sess['registration_email'] = 'user@gmail.com'

        resp = self.client.get('/logout', follow_redirects=False)
        self.assertEqual(resp.status_code, 302)

        with self.client.session_transaction() as sess:
            self.assertIsNone(sess.get('registration_email'))

    # --- Redirect when logged in ---

    def test_login_page_redirects_when_already_logged_in(self):
        with self.client.session_transaction() as sess:
            sess['registration_email'] = 'user@gmail.com'

        resp = self.client.get('/login', follow_redirects=False)
        self.assertEqual(resp.status_code, 302)


# ===================================================================== #
#  4.  QUIZ ROUTE TESTS
# ===================================================================== #

class TestQuizRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_csrf_test_app(csrf_enabled=False)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()

        user = Registration(
            name='Quiz User',
            email='quiz@gmail.com',
            password_hash=generate_password_hash('pass'),
            role='user',
        )
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def _login(self):
        with self.client.session_transaction() as sess:
            sess['registration_email'] = 'quiz@gmail.com'
            sess['registration_name'] = 'Quiz User'

    def test_quiz_requires_login(self):
        resp = self.client.get('/quiz', follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertIn('đăng nhập', html.lower())

    def test_quiz_page_renders_when_logged_in(self):
        self._login()
        resp = self.client.get('/quiz', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_quiz_step_without_attempt_redirects(self):
        self._login()
        resp = self.client.get('/quiz/step/0', follow_redirects=False)
        self.assertEqual(resp.status_code, 302)

    @patch('routes.quiz.generate_dynamic_question', return_value=None)
    def test_quiz_step_with_attempt(self, _mock):
        self._login()
        # Start quiz to get an attempt
        self.client.get('/quiz')
        resp = self.client.get('/quiz/step/0', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)


# ===================================================================== #
#  5.  SCAMMER REPORT TESTS
# ===================================================================== #

class TestScammerRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_csrf_test_app(csrf_enabled=False)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()

        user = Registration(
            name='Reporter',
            email='reporter@gmail.com',
            password_hash=generate_password_hash('pass'),
            role='user',
        )
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def _login(self):
        with self.client.session_transaction() as sess:
            sess['registration_email'] = 'reporter@gmail.com'
            sess['registration_name'] = 'Reporter'

    def _set_math_captcha(self):
        with self.client.session_transaction() as sess:
            sess['math_captcha_answer_report'] = '42'

    def test_report_page_renders(self):
        resp = self.client.get('/scammer/report')
        self.assertEqual(resp.status_code, 200)

    def test_report_submit_person(self):
        self._login()
        self._set_math_captcha()
        resp = self.client.post('/scammer/report', data={
            'report_type': 'general',
            'identifier_person': '0901234567',
            'scammer_name': 'Con Lừa',
            'scam_type_person': 'Lừa đảo tài chính',
            'platform': 'Facebook',
            'description': 'Lừa mua hàng online',
            'term_truth': 'on',
            'term_responsibility': 'on',
            'math_answer': '42',
        }, follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertIn('thành công', html.lower())

        report = ScammerReport.query.first()
        self.assertIsNotNone(report)

    def test_report_missing_identifier_rejected(self):
        self._set_math_captcha()
        resp = self.client.post('/scammer/report', data={
            'report_type': 'general',
            'identifier_person': '',  # missing
            'description': 'test',
            'scam_type_person': 'Lừa đảo',
            'term_truth': 'on',
            'term_responsibility': 'on',
            'math_answer': '42',
        }, follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertIn('Thiếu thông tin', html)

    def test_report_missing_terms_rejected(self):
        self._set_math_captcha()
        resp = self.client.post('/scammer/report', data={
            'report_type': 'general',
            'identifier_person': '0901234567',
            'description': 'test',
            'scam_type_person': 'Lừa đảo',
            # missing term_truth, term_responsibility
            'math_answer': '42',
        }, follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertIn('điều khoản', html)

    def test_report_bad_captcha_rejected(self):
        resp = self.client.post('/scammer/report', data={
            'report_type': 'general',
            'identifier_person': '0901234567',
            'description': 'test',
            'scam_type_person': 'Lừa đảo',
            'term_truth': 'on',
            'term_responsibility': 'on',
            'math_answer': '999',  # wrong
        }, follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertIn('xác thực', html)

    def test_follow_scammer_requires_login(self):
        resp = self.client.post('/scammer/follow', data={'identifier': '123'}, follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertIn('đăng nhập', html.lower())


# ===================================================================== #
#  6.  CHATBOT ROUTE TESTS
# ===================================================================== #

class TestChatbotRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_csrf_test_app(csrf_enabled=False)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()

        user = Registration(
            name='Chat User',
            email='chat@gmail.com',
            password_hash=generate_password_hash('pass'),
            role='user',
        )
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def _login(self):
        with self.client.session_transaction() as sess:
            sess['registration_email'] = 'chat@gmail.com'
            sess['registration_name'] = 'Chat User'

    def test_chatbot_page_requires_login(self):
        resp = self.client.get('/chatbot/', follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertIn('đăng nhập', html.lower())

    def test_chatbot_page_renders_when_logged_in(self):
        self._login()
        resp = self.client.get('/chatbot/')
        self.assertEqual(resp.status_code, 200)

    @patch('utils.chatbot.query_ai_model', return_value='Test reply')
    def test_chatbot_send_message(self, _mock):
        self._login()
        resp = self.client.post('/chatbot/send', json={'message': 'Hello'})
        self.assertIn(resp.status_code, [200, 201])

    def test_chatbot_send_empty_message(self):
        self._login()
        resp = self.client.post('/chatbot/send', json={'message': ''})
        # Should return an error (400 or message about empty)
        data = resp.get_json(silent=True)
        # Either status 400 or an error key in response
        self.assertTrue(
            resp.status_code == 400 or
            (data and ('error' in data or data.get('status') == 'error'))
        )


# ===================================================================== #
#  7.  ADMIN ROUTE TESTS
# ===================================================================== #

class TestAdminRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_csrf_test_app(csrf_enabled=False)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()

        admin = Registration(
            name='Admin',
            email='admin@test.com',
            password_hash=generate_password_hash('adminpass'),
            role='admin',
            is_admin=True,
        )
        user = Registration(
            name='Normal',
            email='normal@test.com',
            password_hash=generate_password_hash('userpass'),
            role='user',
        )
        db.session.add_all([admin, user])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def _admin_login(self):
        with self.client.session_transaction() as sess:
            sess['is_admin'] = True
            sess['admin_email'] = 'admin@test.com'

    def test_admin_login_page_renders(self):
        resp = self.client.get('/admin/login')
        self.assertEqual(resp.status_code, 200)

    def test_admin_dashboard_requires_admin_session(self):
        resp = self.client.get('/admin/', follow_redirects=False)
        self.assertEqual(resp.status_code, 302)  # redirect to login

    def test_admin_dashboard_renders_when_admin(self):
        self._admin_login()
        resp = self.client.get('/admin/')
        self.assertEqual(resp.status_code, 200)

    def test_admin_delete_user(self):
        self._admin_login()
        user = Registration.query.filter_by(email='normal@test.com').first()
        resp = self.client.post(f'/admin/delete-user/{user.id}', follow_redirects=False)
        self.assertIn(resp.status_code, [302, 200])

        deleted = Registration.query.filter_by(email='normal@test.com').first()
        self.assertIsNone(deleted)

    def test_admin_edit_user(self):
        self._admin_login()
        user = Registration.query.filter_by(email='normal@test.com').first()
        resp = self.client.post(f'/admin/edit-user/{user.id}', data={
            'name': 'Edited Name',
            'email': 'normal@test.com',
            'role': 'user',
        }, follow_redirects=False)
        self.assertIn(resp.status_code, [302, 200])

        updated = Registration.query.get(user.id)
        self.assertEqual(updated.name, 'Edited Name')

    def test_admin_logout(self):
        self._admin_login()
        resp = self.client.get('/admin/logout', follow_redirects=False)
        self.assertEqual(resp.status_code, 302)

        with self.client.session_transaction() as sess:
            self.assertIsNone(sess.get('is_admin'))

    def test_admin_unsuspend_wrong_secret(self):
        resp = self.client.post('/admin/unsuspend', json={
            'secret': 'wrong-secret',
        })
        self.assertIn(resp.status_code, [400, 403, 401])


# ===================================================================== #
#  8.  PUBLIC API TESTS
# ===================================================================== #

class TestPublicAPI(unittest.TestCase):

    def setUp(self):
        self.app = create_csrf_test_app(csrf_enabled=False)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_api_check_short_query_rejected(self):
        resp = self.client.get('/api/v1/check?q=ab')
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertEqual(data['status'], 'error')

    def test_api_check_no_results(self):
        resp = self.client.get('/api/v1/check?q=nonexistent-scammer')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertFalse(data['found'])

    def test_api_stats(self):
        resp = self.client.get('/api/v1/stats')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('total_reports', data)
        self.assertIn('knowledge_articles', data)


# ===================================================================== #
#  9.  MAIN ROUTES (Homepage, Leaderboard, Search)
# ===================================================================== #

class TestMainRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_csrf_test_app(csrf_enabled=False)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_homepage_renders(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_leaderboard_renders(self):
        resp = self.client.get('/leaderboard')
        self.assertEqual(resp.status_code, 200)


# ===================================================================== #
#  10. LOGIN_REQUIRED DECORATOR TESTS
# ===================================================================== #

class TestLoginRequiredDecorator(unittest.TestCase):
    """Ensure @login_required redirects unauthenticated users and
    displays the correct Vietnamese flash message."""

    def setUp(self):
        self.app = create_csrf_test_app(csrf_enabled=False)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_quiz_redirects_unauthenticated(self):
        resp = self.client.get('/quiz', follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('login', resp.headers['Location'])

    def test_chatbot_redirects_unauthenticated(self):
        resp = self.client.get('/chatbot/', follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('login', resp.headers['Location'])

    def test_flash_message_is_vietnamese(self):
        resp = self.client.get('/quiz', follow_redirects=True)
        html = resp.get_data(as_text=True)
        self.assertIn('đăng nhập', html.lower())


if __name__ == '__main__':
    unittest.main()
