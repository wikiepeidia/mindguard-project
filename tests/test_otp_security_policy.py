import os
import sys
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.otp_security import generate_otp_code, issue_otp_challenge, verify_otp_submission

class TestOtpSecurityPolicy(unittest.TestCase):
    """
    OTPSEC-01: Random six-digit generation
    OTPSEC-02: Hash storage without plaintext
    OTPSEC-03: Secure verification
    OTPPOL-01: Expiry rejection
    OTPPOL-02: Lockout after max attempts
    OTPPOL-03: Single-use and superseding invalidation
    """

    def setUp(self):
        from app import app
        self.app_context = app.app_context()
        self.app_context.push()

        self.mock_config = {
            "OTP_PEPPER": "test_pepper",
            "OTP_PEPPER_VERSION": "v1",
            "OTP_TTL_SECONDS": 300,
            "OTP_MAX_ATTEMPTS": 3,
            "OTP_LOCKOUT_SECONDS": 900
        }
        
        self.mock_session = MagicMock()

    def tearDown(self):
        self.app_context.pop()

    def test_otpsec_01_random_six_digit_generation(self):
        """OTPSEC-01: Ensure generated OTP is 6 digits and not static."""
        code1 = generate_otp_code()
        code2 = generate_otp_code()
        self.assertTrue(code1.isdigit() and len(code1) == 6)
        self.assertNotEqual(code1, "123456")
        
        # In a very rare case they might match, so we test a few
        codes = {generate_otp_code() for _ in range(10)}
        self.assertGreater(len(codes), 1, "OTP generation appears static")

    def test_otpsec_02_hash_storage_without_plaintext(self):
        """OTPSEC-02: Issue challenge does not persist plaintext OTP."""
        # Using a mock challenge class to capture what issue_otp_challenge does
        from models.models import OtpChallenge

        # Mock the query behavior to simulate no active challenges
        self.mock_session.add = MagicMock()
        self.mock_session.flush = MagicMock()
        
        # Mock OtpChallenge.query.filter_by(...).all() returning []
        # Actually it's easier to mock the OtpChallenge query object globally
        # But we can also just create a local patch
        with unittest.mock.patch('models.models.OtpChallenge.query') as mock_query:
            mock_query.filter_by.return_value.all.return_value = []
            
            challenge, plaintext = issue_otp_challenge(
                self.mock_session, "test@example.com", "register", self.mock_config
            )
            
            # The challenge should be added to the session
            self.mock_session.add.assert_called_once_with(challenge)
            
            # Verify plaintext is not stored on the challenge object
            self.assertFalse(hasattr(challenge, "plaintext_otp"))
            self.assertFalse(hasattr(challenge, "otp_code"))
            self.assertNotEqual(challenge.otp_hash, plaintext)
            self.assertNotIn(plaintext, challenge.otp_salt)
            self.assertIn(challenge.status, ["active"])
            self.assertIsNotNone(challenge.otp_hash)

    def test_otppol_01_expiry_rejection(self):
        """OTPPOL-01: Expired challenges are rejected."""
        with unittest.mock.patch('models.models.OtpChallenge.query') as mock_query:
            mock_query.filter_by.return_value.all.return_value = []
            challenge, plaintext = issue_otp_challenge(
                self.mock_session, "test@example.com", "register", self.mock_config
            )
            
            # Simulate time passing beyond expiration
            future_time = challenge.expires_at + timedelta(seconds=1)
            
            result = verify_otp_submission(challenge, plaintext, future_time, self.mock_config)
            self.assertEqual(result, "expired")
            self.assertEqual(challenge.status, "expired")

    def test_otppol_02_lockout_after_max_attempts(self):
        """OTPPOL-02: Challenge locks out after max attempts."""
        with unittest.mock.patch('models.models.OtpChallenge.query') as mock_query:
            mock_query.filter_by.return_value.all.return_value = []
            challenge, plaintext = issue_otp_challenge(
                self.mock_session, "test@example.com", "register", self.mock_config
            )
            
            now = challenge.issued_at + timedelta(seconds=1)
            
            # Max attempts is 3
            # Attempt 1
            res1 = verify_otp_submission(challenge, "000000", now, self.mock_config)
            self.assertEqual(res1, "invalid")
            self.assertEqual(challenge.attempts_used, 1)
            self.assertEqual(challenge.status, "active")
            
            # Attempt 2
            res2 = verify_otp_submission(challenge, "000000", now, self.mock_config)
            self.assertEqual(res2, "invalid")
            self.assertEqual(challenge.attempts_used, 2)
            
            # Attempt 3 (Triggers lockout)
            res3 = verify_otp_submission(challenge, "000000", now, self.mock_config)
            self.assertEqual(res3, "invalid") # Returns invalid on the attempt that locks it
            self.assertEqual(challenge.attempts_used, 3)
            self.assertEqual(challenge.status, "locked")
            self.assertIsNotNone(challenge.locked_until)
            self.assertEqual(challenge.invalidation_reason, "max_attempts")
            
            # Attempt 4 (Already locked)
            res4 = verify_otp_submission(challenge, plaintext, now, self.mock_config)
            self.assertEqual(res4, "locked") # Even with correct code, it's locked

    def test_otppol_03_single_use_verify(self):
        """OTPPOL-03: Challenge is single-use and invalidates on success."""
        with unittest.mock.patch('models.models.OtpChallenge.query') as mock_query:
            mock_query.filter_by.return_value.all.return_value = []
            challenge, plaintext = issue_otp_challenge(
                self.mock_session, "test@example.com", "register", self.mock_config
            )
            
            now = challenge.issued_at + timedelta(seconds=10)
            
            # Verify correct code
            result = verify_otp_submission(challenge, plaintext, now, self.mock_config)
            self.assertEqual(result, "valid")
            self.assertEqual(challenge.status, "used")
            self.assertEqual(challenge.used_at, now)
            
            # Second attempt should return already_used
            result2 = verify_otp_submission(challenge, plaintext, now + timedelta(seconds=1), self.mock_config)
            self.assertEqual(result2, "already_used")

    def test_otppol_superseding_invalidation(self):
        """OTPPOL: Re-issuing OTP challenge invalidates prior active ones."""
        # Create a mock active challenge
        active_challenge = MagicMock()
        active_challenge.status = "active"
        
        with unittest.mock.patch('models.models.OtpChallenge.query') as mock_query:
            # Return active challenge in query to simulate an existing one
            mock_query.filter_by.return_value.all.return_value = [active_challenge]
            
            new_challenge, _ = issue_otp_challenge(
                self.mock_session, "test@example.com", "register", self.mock_config
            )
            
            # Validate the previous challenge was invalidated
            self.assertEqual(active_challenge.status, "invalidated")
            self.assertEqual(active_challenge.invalidation_reason, "superseded")
            self.assertIsNotNone(active_challenge.invalidated_at)
            
            # Validate new challenge is active
            self.assertEqual(new_challenge.status, "active")

if __name__ == "__main__":
    unittest.main()
