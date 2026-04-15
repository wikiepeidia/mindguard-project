"""Unit tests for OTP email delivery service (Phase 21)."""

import os
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
            'EMAIL_PROVIDER': 'smtp',
            'TESTING': False,
        }
        status = otp_email_delivery_status(cfg)
        self.assertFalse(status['ok'])
        self.assertEqual(status['category'], 'unsupported_provider')


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


if __name__ == '__main__':
    unittest.main()
