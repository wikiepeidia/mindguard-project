"""Unit tests for OTP email delivery service (Phase 21)."""

import os
import smtplib
import socket
import sys
import unittest

import requests

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from services.otp_email_delivery import otp_email_delivery_status, send_otp_email


class _FakeResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload


class OtpEmailDeliveryStatusTests(unittest.TestCase):
    def test_missing_config_returns_fail_closed(self):
        cfg = {
            'EMAIL_PROVIDER': 'resend_api',
            'RESEND_API_KEY': '',
            'RESEND_FROM_EMAIL': '',
            'TESTING': False,
        }
        status = otp_email_delivery_status(cfg)
        self.assertFalse(status['ok'])
        self.assertEqual(status['category'], 'misconfigured')
        self.assertIn('RESEND_API_KEY', status['missing'])
        self.assertIn('RESEND_FROM_EMAIL', status['missing'])

    def test_unsupported_provider_rejected(self):
        cfg = {
            'EMAIL_PROVIDER': 'ses_api',
            'TESTING': False,
        }
        status = otp_email_delivery_status(cfg)
        self.assertFalse(status['ok'])
        self.assertEqual(status['category'], 'unsupported_provider')

    def test_smtp_ready_status(self):
        cfg = {
            'EMAIL_PROVIDER': 'smtp',
            'SMTP_HOST': 'smtp.gmail.com',
            'SMTP_PORT': 587,
            'SMTP_USERNAME': 'mindguard@gmail.com',
            'SMTP_PASSWORD': 'app-password',
            'SMTP_USE_TLS': True,
            'SMTP_USE_SSL': False,
            'SMTP_FROM_EMAIL': 'mindguard@gmail.com',
            'TESTING': False,
        }
        status = otp_email_delivery_status(cfg)
        self.assertTrue(status['ok'])
        self.assertEqual(status['category'], 'ready')

    def test_smtp_missing_config_returns_fail_closed(self):
        cfg = {
            'EMAIL_PROVIDER': 'smtp',
            'SMTP_HOST': '',
            'SMTP_PORT': 587,
            'SMTP_USERNAME': '',
            'SMTP_PASSWORD': '',
            'SMTP_USE_TLS': True,
            'SMTP_USE_SSL': False,
            'SMTP_FROM_EMAIL': '',
            'TESTING': False,
        }
        status = otp_email_delivery_status(cfg)
        self.assertFalse(status['ok'])
        self.assertEqual(status['category'], 'misconfigured')
        self.assertIn('SMTP_HOST', status['missing'])
        self.assertIn('SMTP_USERNAME', status['missing'])
        self.assertIn('SMTP_PASSWORD', status['missing'])
        self.assertIn('SMTP_FROM_EMAIL', status['missing'])

    def test_smtp_rejects_conflicting_tls_and_ssl(self):
        cfg = {
            'EMAIL_PROVIDER': 'smtp',
            'SMTP_HOST': 'smtp.gmail.com',
            'SMTP_PORT': 465,
            'SMTP_USERNAME': 'mindguard@gmail.com',
            'SMTP_PASSWORD': 'app-password',
            'SMTP_USE_TLS': True,
            'SMTP_USE_SSL': True,
            'SMTP_FROM_EMAIL': 'mindguard@gmail.com',
            'TESTING': False,
        }
        status = otp_email_delivery_status(cfg)
        self.assertFalse(status['ok'])
        self.assertEqual(status['category'], 'misconfigured')
        self.assertIn('SMTP_USE_TLS/SMTP_USE_SSL(conflict)', status['missing'])


class OtpEmailDeliverySendTests(unittest.TestCase):
    def _base_cfg(self):
        return {
            'EMAIL_PROVIDER': 'resend_api',
            'RESEND_API_KEY': 're_test_key',
            'RESEND_FROM_EMAIL': 'otp@mindguard.local',
            'OTP_TTL_SECONDS': 300,
            'OTP_EMAIL_TIMEOUT_SECONDS': 2,
            'OTP_EMAIL_RETRY_ATTEMPTS': 1,
            'TESTING': False,
        }

    def test_send_success(self):
        cfg = self._base_cfg()

        def transport(*args, **kwargs):
            return _FakeResponse(200, {'id': 'msg_123'})

        result = send_otp_email(
            email='user@example.com',
            otp_code='123456',
            context={'purpose': 'register'},
            config=cfg,
            transport=transport,
        )

        self.assertTrue(result['ok'])
        self.assertEqual(result['category'], 'sent')
        self.assertEqual(result['provider_message_id'], 'msg_123')

    def test_send_timeout_retry_exhausted(self):
        cfg = self._base_cfg()
        calls = {'count': 0}

        def transport(*args, **kwargs):
            calls['count'] += 1
            raise requests.Timeout('timeout')

        result = send_otp_email(
            email='user@example.com',
            otp_code='123456',
            context={'purpose': 'register'},
            config=cfg,
            transport=transport,
        )

        self.assertFalse(result['ok'])
        self.assertEqual(result['category'], 'timeout')
        self.assertEqual(calls['count'], 2)  # first call + 1 retry

    def test_send_non_2xx_provider_rejected(self):
        cfg = self._base_cfg()

        def transport(*args, **kwargs):
            return _FakeResponse(400, {'message': 'invalid request'})

        result = send_otp_email(
            email='user@example.com',
            otp_code='123456',
            context={'purpose': 'register'},
            config=cfg,
            transport=transport,
        )

        self.assertFalse(result['ok'])
        self.assertEqual(result['category'], 'provider_rejected')

    def test_test_mode_can_force_failure(self):
        cfg = self._base_cfg()
        cfg['TESTING'] = True
        cfg['OTP_EMAIL_TEST_FORCE_FAIL'] = True

        result = send_otp_email(
            email='user@example.com',
            otp_code='123456',
            context={'purpose': 'register'},
            config=cfg,
        )

        self.assertFalse(result['ok'])
        self.assertEqual(result['category'], 'test_failure')

    def _smtp_cfg(self):
        return {
            'EMAIL_PROVIDER': 'smtp',
            'SMTP_HOST': 'smtp.gmail.com',
            'SMTP_PORT': 587,
            'SMTP_USERNAME': 'mindguard@gmail.com',
            'SMTP_PASSWORD': 'app-password',
            'SMTP_USE_TLS': True,
            'SMTP_USE_SSL': False,
            'SMTP_FROM_EMAIL': 'mindguard@gmail.com',
            'OTP_TTL_SECONDS': 300,
            'TESTING': False,
        }

    def test_smtp_send_success(self):
        cfg = self._smtp_cfg()
        captured = {}

        def transport(message):
            captured['message'] = message

        result = send_otp_email(
            email='user@example.com',
            otp_code='654321',
            context={'purpose': 'register'},
            config=cfg,
            transport=transport,
        )

        self.assertTrue(result['ok'])
        self.assertEqual(result['category'], 'sent')
        self.assertIsNone(result['provider_message_id'])
        self.assertEqual(captured['message'].sender, 'mindguard@gmail.com')
        self.assertEqual(captured['message'].recipients, ['user@example.com'])
        self.assertIn('654321', captured['message'].body)

    def test_smtp_send_provider_rejected(self):
        cfg = self._smtp_cfg()

        def transport(message):
            raise smtplib.SMTPAuthenticationError(535, b'5.7.8 Authentication failed')

        result = send_otp_email(
            email='user@example.com',
            otp_code='654321',
            context={'purpose': 'register'},
            config=cfg,
            transport=transport,
        )

        self.assertFalse(result['ok'])
        self.assertEqual(result['category'], 'provider_rejected')

    def test_smtp_send_timeout(self):
        cfg = self._smtp_cfg()

        def transport(message):
            raise socket.timeout('timed out')

        result = send_otp_email(
            email='user@example.com',
            otp_code='654321',
            context={'purpose': 'register'},
            config=cfg,
            transport=transport,
        )

        self.assertFalse(result['ok'])
        self.assertEqual(result['category'], 'timeout')

    def test_smtp_send_network_error(self):
        cfg = self._smtp_cfg()

        def transport(message):
            raise OSError('network unreachable')

        result = send_otp_email(
            email='user@example.com',
            otp_code='654321',
            context={'purpose': 'register'},
            config=cfg,
            transport=transport,
        )

        self.assertFalse(result['ok'])
        self.assertEqual(result['category'], 'network_error')


if __name__ == '__main__':
    unittest.main()
