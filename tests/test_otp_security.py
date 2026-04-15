"""Tests for OTP security foundation: generation, hashing, challenge lifecycle."""
import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestGenerateOtpCode(unittest.TestCase):
    """OTP code generation must be 6-digit and cryptographically random."""

    def test_returns_six_digit_string(self):
        from utils.otp_security import generate_otp_code
        code = generate_otp_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())

    def test_range_bounds(self):
        from utils.otp_security import generate_otp_code
        for _ in range(200):
            code = generate_otp_code()
            self.assertGreaterEqual(int(code), 100000)
            self.assertLessEqual(int(code), 999999)

    def test_uses_secrets_module(self):
        """Ensure cryptographic randomness, not stdlib random."""
        import utils.otp_security as mod
        import inspect
        source = inspect.getsource(mod.generate_otp_code)
        self.assertIn("secrets", source)
        self.assertNotIn("random.rand", source)


class TestHashOtp(unittest.TestCase):
    """OTP hashing must use PBKDF2 with salt and pepper."""

    def test_hash_deterministic_with_same_inputs(self):
        from utils.otp_security import hash_otp
        h1 = hash_otp("123456", "salt1", "pepper1")
        h2 = hash_otp("123456", "salt1", "pepper1")
        self.assertEqual(h1, h2)

    def test_hash_differs_with_different_salt(self):
        from utils.otp_security import hash_otp
        h1 = hash_otp("123456", "salt_a", "pepper1")
        h2 = hash_otp("123456", "salt_b", "pepper1")
        self.assertNotEqual(h1, h2)

    def test_hash_differs_with_different_pepper(self):
        from utils.otp_security import hash_otp
        h1 = hash_otp("123456", "salt1", "pepper_a")
        h2 = hash_otp("123456", "salt1", "pepper_b")
        self.assertNotEqual(h1, h2)

    def test_hash_is_hex_string(self):
        from utils.otp_security import hash_otp
        h = hash_otp("654321", "salt", "pepper")
        # Should be valid hex
        int(h, 16)


class TestVerifyOtpSubmission(unittest.TestCase):
    """OTP verification must use constant-time comparison and enforce lifecycle."""

    def test_correct_otp_returns_valid(self):
        from utils.otp_security import hash_otp, verify_otp_submission
        salt = "test_salt"
        pepper = "test_pepper"
        code = "123456"
        otp_hash = hash_otp(code, salt, pepper)

        challenge = MagicMock()
        challenge.otp_hash = otp_hash
        challenge.otp_salt = salt
        challenge.pepper_version = "v1"
        challenge.attempts_used = 0
        challenge.max_attempts = 5
        challenge.expires_at = datetime.utcnow() + timedelta(minutes=5)
        challenge.locked_until = None
        challenge.status = "active"

        config = MagicMock()
        config.OTP_PEPPER = pepper
        config.OTP_LOCKOUT_SECONDS = 900

        result = verify_otp_submission(challenge, code, datetime.utcnow(), config)
        self.assertEqual(result, "valid")

    def test_wrong_otp_returns_invalid(self):
        from utils.otp_security import hash_otp, verify_otp_submission
        salt = "test_salt"
        pepper = "test_pepper"
        otp_hash = hash_otp("123456", salt, pepper)

        challenge = MagicMock()
        challenge.otp_hash = otp_hash
        challenge.otp_salt = salt
        challenge.pepper_version = "v1"
        challenge.attempts_used = 0
        challenge.max_attempts = 5
        challenge.expires_at = datetime.utcnow() + timedelta(minutes=5)
        challenge.locked_until = None
        challenge.status = "active"

        config = MagicMock()
        config.OTP_PEPPER = pepper
        config.OTP_LOCKOUT_SECONDS = 900

        result = verify_otp_submission(challenge, "999999", datetime.utcnow(), config)
        self.assertEqual(result, "invalid")

    def test_expired_challenge_returns_expired(self):
        from utils.otp_security import hash_otp, verify_otp_submission
        salt = "test_salt"
        pepper = "test_pepper"
        otp_hash = hash_otp("123456", salt, pepper)

        challenge = MagicMock()
        challenge.otp_hash = otp_hash
        challenge.otp_salt = salt
        challenge.pepper_version = "v1"
        challenge.attempts_used = 0
        challenge.max_attempts = 5
        challenge.expires_at = datetime.utcnow() - timedelta(minutes=1)
        challenge.locked_until = None
        challenge.status = "active"

        config = MagicMock()
        config.OTP_PEPPER = pepper
        config.OTP_LOCKOUT_SECONDS = 900

        result = verify_otp_submission(challenge, "123456", datetime.utcnow(), config)
        self.assertEqual(result, "expired")

    def test_locked_challenge_returns_locked(self):
        from utils.otp_security import hash_otp, verify_otp_submission
        salt = "test_salt"
        pepper = "test_pepper"
        otp_hash = hash_otp("123456", salt, pepper)

        challenge = MagicMock()
        challenge.otp_hash = otp_hash
        challenge.otp_salt = salt
        challenge.pepper_version = "v1"
        challenge.attempts_used = 5
        challenge.max_attempts = 5
        challenge.expires_at = datetime.utcnow() + timedelta(minutes=5)
        challenge.locked_until = datetime.utcnow() + timedelta(minutes=15)
        challenge.status = "locked"

        config = MagicMock()
        config.OTP_PEPPER = pepper
        config.OTP_LOCKOUT_SECONDS = 900

        result = verify_otp_submission(challenge, "123456", datetime.utcnow(), config)
        self.assertEqual(result, "locked")

    def test_uses_hmac_compare_digest(self):
        """Ensure constant-time comparison is used."""
        import utils.otp_security as mod
        import inspect
        source = inspect.getsource(mod.verify_otp_submission)
        self.assertIn("hmac.compare_digest", source)


class TestConfigKeys(unittest.TestCase):
    """Config must expose OTP policy keys."""

    def test_otp_ttl_seconds_exists(self):
        from config import Config
        self.assertTrue(hasattr(Config, "OTP_TTL_SECONDS"))
        self.assertEqual(Config.OTP_TTL_SECONDS, 300)

    def test_otp_max_attempts_exists(self):
        from config import Config
        self.assertTrue(hasattr(Config, "OTP_MAX_ATTEMPTS"))
        self.assertEqual(Config.OTP_MAX_ATTEMPTS, 5)

    def test_otp_lockout_seconds_exists(self):
        from config import Config
        self.assertTrue(hasattr(Config, "OTP_LOCKOUT_SECONDS"))
        self.assertEqual(Config.OTP_LOCKOUT_SECONDS, 900)

    def test_otp_pepper_from_env(self):
        from config import Config
        self.assertTrue(hasattr(Config, "OTP_PEPPER"))

    def test_otp_pepper_version_exists(self):
        from config import Config
        self.assertTrue(hasattr(Config, "OTP_PEPPER_VERSION"))
        self.assertEqual(Config.OTP_PEPPER_VERSION, "v1")


class TestOtpChallengeModel(unittest.TestCase):
    """OtpChallenge model must have all required fields."""

    def test_model_exists(self):
        from models.models import OtpChallenge
        self.assertEqual(OtpChallenge.__tablename__, "otp_challenges")

    def test_required_fields(self):
        from models.models import OtpChallenge
        required = [
            "id", "email", "purpose", "otp_hash", "otp_salt",
            "pepper_version", "attempts_used", "max_attempts",
            "issued_at", "expires_at", "locked_until", "used_at",
            "invalidated_at", "invalidation_reason", "status",
        ]
        for field in required:
            self.assertTrue(
                hasattr(OtpChallenge, field),
                f"OtpChallenge missing field: {field}",
            )


if __name__ == "__main__":
    unittest.main()
