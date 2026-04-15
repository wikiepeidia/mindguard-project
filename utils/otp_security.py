"""OTP security helpers: generation, hashing, and challenge lifecycle verification.

All OTP codes are generated using cryptographically secure randomness.
OTP persistence stores hash metadata only -- no plaintext OTP is persisted.
Verification uses constant-time comparison via hmac.compare_digest.
"""
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta


def generate_otp_code():
    """Generate a cryptographically secure 6-digit OTP code.

    Returns:
        str: A zero-padded 6-digit string (100000-999999).
    """
    code = secrets.randbelow(900000) + 100000
    return str(code)


def hash_otp(code, salt, pepper):
    """Hash an OTP code using PBKDF2-HMAC-SHA256 with salt and pepper.

    Args:
        code: The plaintext OTP code string.
        salt: A unique salt for this challenge.
        pepper: Application-level secret pepper from config.

    Returns:
        str: Hex-encoded hash digest.
    """
    # Combine code with pepper before hashing
    key_material = f"{code}{pepper}".encode("utf-8")
    salt_bytes = salt.encode("utf-8")
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        key_material,
        salt_bytes,
        iterations=100_000,
    )
    return digest.hex()


def _cfg_get(config, key, default=None):
    """Read a config value from either a class (getattr) or dict-like (Flask config).

    Flask's app.config is a dict subclass -- getattr won't find dynamic keys.
    This helper tries dict-style first, then falls back to getattr.
    """
    # Dict-like access (Flask config, plain dict)
    if hasattr(config, "get") and callable(config.get):
        val = config.get(key)
        if val is not None:
            return val
    # Class attribute access (Config class)
    val = getattr(config, key, None)
    if val is not None:
        return val
    return default


def issue_otp_challenge(session, email, purpose, config):
    """Create a new OTP challenge and persist it to the database.

    Invalidates any existing active challenges for the same email+purpose
    before creating a new one.

    Args:
        session: SQLAlchemy database session (db.session).
        email: User email address.
        purpose: Challenge purpose (e.g., 'register', 'login').
        config: Application config object or Flask config dict with OTP_* keys.

    Returns:
        tuple: (OtpChallenge instance, plaintext_otp_code)
            The plaintext code is returned for sending via email
            but must NEVER be persisted.
    """
    from models.models import OtpChallenge

    now = datetime.utcnow()

    # Invalidate existing active challenges for this email+purpose
    active_challenges = OtpChallenge.query.filter_by(
        email=email,
        purpose=purpose,
        status="active",
    ).all()
    for ch in active_challenges:
        ch.status = "invalidated"
        ch.invalidated_at = now
        ch.invalidation_reason = "superseded"

    # Generate new OTP
    plaintext_code = generate_otp_code()
    salt = secrets.token_hex(32)
    pepper = _cfg_get(config, "OTP_PEPPER", "")
    pepper_version = _cfg_get(config, "OTP_PEPPER_VERSION", "v1")
    otp_hash = hash_otp(plaintext_code, salt, pepper)

    ttl = _cfg_get(config, "OTP_TTL_SECONDS", 300)
    max_attempts = _cfg_get(config, "OTP_MAX_ATTEMPTS", 5)

    challenge = OtpChallenge(
        email=email,
        purpose=purpose,
        otp_hash=otp_hash,
        otp_salt=salt,
        pepper_version=pepper_version,
        attempts_used=0,
        max_attempts=max_attempts,
        issued_at=now,
        expires_at=now + timedelta(seconds=ttl),
        status="active",
    )
    session.add(challenge)
    session.flush()  # Get id assigned without full commit

    return challenge, plaintext_code


def verify_otp_submission(challenge, submitted_code, now, config):
    """Verify a submitted OTP code against a challenge.

    Performs lifecycle checks (expiry, lockout, status) before
    constant-time hash comparison.

    Args:
        challenge: OtpChallenge ORM instance.
        submitted_code: The OTP code string submitted by the user.
        now: Current UTC datetime for expiry/lockout checks.
        config: Application config object with OTP_PEPPER, OTP_LOCKOUT_SECONDS.

    Returns:
        str: One of 'valid', 'invalid', 'expired', 'locked', 'already_used',
             'invalidated'.
    """
    # Check status-based rejections first
    if challenge.status == "used":
        return "already_used"

    if challenge.status == "invalidated":
        return "invalidated"

    if challenge.status == "locked":
        # Check if lockout has expired
        if challenge.locked_until and now < challenge.locked_until:
            return "locked"
        # Lockout expired -- but challenge may still be expired by TTL
        # Fall through to expiry check

    # Check expiry
    if now > challenge.expires_at:
        challenge.status = "expired"
        return "expired"

    # Check active lockout (even if status wasn't set to locked yet)
    if challenge.locked_until and now < challenge.locked_until:
        return "locked"

    # Perform constant-time hash comparison
    pepper = _cfg_get(config, "OTP_PEPPER", "")
    submitted_hash = hash_otp(submitted_code, challenge.otp_salt, pepper)

    is_match = hmac.compare_digest(
        submitted_hash.encode("utf-8"),
        challenge.otp_hash.encode("utf-8"),
    )

    if is_match:
        challenge.status = "used"
        challenge.used_at = now
        return "valid"

    # Wrong code -- increment attempts
    challenge.attempts_used += 1

    if challenge.attempts_used >= challenge.max_attempts:
        lockout_seconds = _cfg_get(config, "OTP_LOCKOUT_SECONDS", 900)
        challenge.status = "locked"
        challenge.locked_until = now + timedelta(seconds=lockout_seconds)
        challenge.invalidation_reason = "max_attempts"

    return "invalid"
