"""OTP email delivery service.

Phase 21 + 25 provider contract:
- Default provider: Resend API
- Additional provider: generic SMTP over Flask-Mail
- Credentials: environment-derived config only
- Behavior: normalized result payload with fail-closed provider handling
"""
import math
import smtplib
import socket
from typing import Any, Dict, Optional

import requests
from flask_mail import Message

from extensions import mail


RESEND_SEND_ENDPOINT = "https://api.resend.com/emails"


def _cfg_get(config: Any, key: str, default: Any = None) -> Any:
    """Read a config value from Flask dict-like config or class attributes."""
    if hasattr(config, "get") and callable(config.get):
        val = config.get(key)
        if val is not None:
            return val
    val = getattr(config, key, None)
    if val is not None:
        return val
    return default


def _cfg_bool(config: Any, key: str, default: bool = False) -> bool:
    value = _cfg_get(config, key, default)
    if isinstance(value, bool):
        return value
    text = str(value or "").strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return default


def _smtp_cfg_get(config: Any, smtp_key: str, mail_key: str, default: Any = None) -> Any:
    value = _cfg_get(config, smtp_key)
    if value is None or (isinstance(value, str) and not value.strip()):
        return _cfg_get(config, mail_key, default)
    return value


def _email_provider(config: Any) -> str:
    return str(_cfg_get(config, "EMAIL_PROVIDER", "resend_api") or "resend_api").strip().lower()


def _smtp_status(config: Any) -> Dict[str, Any]:
    missing = []
    host = str(_smtp_cfg_get(config, "SMTP_HOST", "MAIL_SERVER", "") or "").strip()
    username = str(_smtp_cfg_get(config, "SMTP_USERNAME", "MAIL_USERNAME", "") or "").strip()
    password = str(_smtp_cfg_get(config, "SMTP_PASSWORD", "MAIL_PASSWORD", "") or "").strip()
    from_email = str(_smtp_cfg_get(config, "SMTP_FROM_EMAIL", "MAIL_DEFAULT_SENDER", "") or "").strip()

    try:
        port = int(_smtp_cfg_get(config, "SMTP_PORT", "MAIL_PORT", 587) or 0)
    except (TypeError, ValueError):
        port = 0

    use_tls = _cfg_bool(config, "SMTP_USE_TLS", _cfg_bool(config, "MAIL_USE_TLS", False))
    use_ssl = _cfg_bool(config, "SMTP_USE_SSL", _cfg_bool(config, "MAIL_USE_SSL", False))

    if not host:
        missing.append("SMTP_HOST")
    if port <= 0 or port > 65535:
        missing.append("SMTP_PORT")
    if not username:
        missing.append("SMTP_USERNAME")
    if not password:
        missing.append("SMTP_PASSWORD")
    if not from_email:
        missing.append("SMTP_FROM_EMAIL")
    if use_tls and use_ssl:
        missing.append("SMTP_USE_TLS/SMTP_USE_SSL(conflict)")

    if missing:
        return {
            "ok": False,
            "category": "misconfigured",
            "message": "Thiếu cấu hình gửi email OTP trên máy chủ.",
            "missing": missing,
        }

    return {
        "ok": True,
        "category": "ready",
        "message": "Cấu hình gửi email OTP đã sẵn sàng.",
        "missing": [],
    }


def otp_email_delivery_status(config: Any) -> Dict[str, Any]:
    """Validate provider and required credentials for OTP email delivery."""
    provider = _email_provider(config)

    if provider == "smtp":
        return _smtp_status(config)

    if provider != "resend_api":
        return {
            "ok": False,
            "category": "unsupported_provider",
            "message": "Nhà cung cấp email OTP không được hỗ trợ.",
            "missing": ["EMAIL_PROVIDER(resend_api|smtp)"],
        }

    missing = []
    if not str(_cfg_get(config, "RESEND_API_KEY", "") or "").strip():
        missing.append("RESEND_API_KEY")
    if not str(_cfg_get(config, "RESEND_FROM_EMAIL", "") or "").strip():
        missing.append("RESEND_FROM_EMAIL")

    if missing:
        return {
            "ok": False,
            "category": "misconfigured",
            "message": "Thiếu cấu hình gửi email OTP trên máy chủ.",
            "missing": missing,
        }

    return {
        "ok": True,
        "category": "ready",
        "message": "Cấu hình gửi email OTP đã sẵn sàng.",
        "missing": [],
    }


def _send_resend_otp_email(
    email: str,
    otp_code: str,
    config: Any,
    transport=None,
) -> Dict[str, Any]:
    api_key = str(_cfg_get(config, "RESEND_API_KEY", "") or "").strip()
    from_email = str(_cfg_get(config, "RESEND_FROM_EMAIL", "") or "").strip()
    ttl_seconds = int(_cfg_get(config, "OTP_TTL_SECONDS", 300) or 300)
    timeout_seconds = int(_cfg_get(config, "OTP_EMAIL_TIMEOUT_SECONDS", 5) or 5)
    retry_attempts = int(_cfg_get(config, "OTP_EMAIL_RETRY_ATTEMPTS", 1) or 1)

    req_post = transport or requests.post
    payload = {
        "from": from_email,
        "to": [email],
        "subject": "Ma OTP xac thuc tai khoan MindGuard",
        "text": _build_otp_email_body(otp_code, ttl_seconds),
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    total_attempts = max(1, retry_attempts + 1)
    last_category = "network_error"

    for attempt in range(total_attempts):
        try:
            response = req_post(
                RESEND_SEND_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=timeout_seconds,
            )
        except requests.Timeout:
            last_category = "timeout"
            if attempt < total_attempts - 1:
                continue
            break
        except requests.RequestException:
            last_category = "network_error"
            if attempt < total_attempts - 1:
                continue
            break

        if 200 <= response.status_code < 300:
            provider_message_id = None
            try:
                provider_message_id = response.json().get("id")
            except Exception:
                provider_message_id = None
            return {
                "ok": True,
                "category": "sent",
                "message": "Mã OTP đã được gửi đến email của bạn.",
                "provider_message_id": provider_message_id,
            }

        if response.status_code in (429, 500, 502, 503, 504):
            last_category = "transient_error"
            if attempt < total_attempts - 1:
                continue
            break

        return {
            "ok": False,
            "category": "provider_rejected",
            "message": "Không thể gửi mã OTP lúc này. Vui lòng thử lại sau vài phút.",
            "provider_message_id": None,
        }

    return {
        "ok": False,
        "category": last_category,
        "message": "Không thể gửi mã OTP lúc này. Vui lòng thử lại sau vài phút.",
        "provider_message_id": None,
    }


def _smtp_transport_callable(transport):
    if transport is None:
        return mail.send
    if hasattr(transport, "send") and callable(transport.send):
        return transport.send
    return transport


def _send_smtp_otp_email(
    email: str,
    otp_code: str,
    config: Any,
    transport=None,
) -> Dict[str, Any]:
    ttl_seconds = int(_cfg_get(config, "OTP_TTL_SECONDS", 300) or 300)
    from_email = str(_smtp_cfg_get(config, "SMTP_FROM_EMAIL", "MAIL_DEFAULT_SENDER", "") or "").strip()
    send_mail = _smtp_transport_callable(transport)
    message = Message(
        subject="Ma OTP xac thuc tai khoan MindGuard",
        recipients=[email],
        body=_build_otp_email_body(otp_code, ttl_seconds),
        sender=from_email,
    )

    try:
        send_mail(message)
    except (socket.timeout, TimeoutError):
        return {
            "ok": False,
            "category": "timeout",
            "message": "Không thể gửi mã OTP lúc này. Vui lòng thử lại sau vài phút.",
            "provider_message_id": None,
        }
    except smtplib.SMTPServerDisconnected as exc:
        category = "timeout" if "timed out" in str(exc).lower() else "network_error"
        return {
            "ok": False,
            "category": category,
            "message": "Không thể gửi mã OTP lúc này. Vui lòng thử lại sau vài phút.",
            "provider_message_id": None,
        }
    except (smtplib.SMTPAuthenticationError, smtplib.SMTPSenderRefused,
            smtplib.SMTPRecipientsRefused, smtplib.SMTPDataError,
            smtplib.SMTPResponseException, smtplib.SMTPException):
        return {
            "ok": False,
            "category": "provider_rejected",
            "message": "Không thể gửi mã OTP lúc này. Vui lòng thử lại sau vài phút.",
            "provider_message_id": None,
        }
    except OSError:
        return {
            "ok": False,
            "category": "network_error",
            "message": "Không thể gửi mã OTP lúc này. Vui lòng thử lại sau vài phút.",
            "provider_message_id": None,
        }

    return {
        "ok": True,
        "category": "sent",
        "message": "Mã OTP đã được gửi đến email của bạn.",
        "provider_message_id": None,
    }


def _build_otp_email_body(otp_code: str, ttl_seconds: int) -> str:
    ttl_minutes = max(1, int(math.ceil(float(ttl_seconds) / 60.0)))
    return (
        "Xin chào,\n\n"
        "Bạn vừa yêu cầu xác thực tài khoản MindGuard.\n"
        f"Mã OTP của bạn là: {otp_code}\n"
        f"Mã có hiệu lực trong khoảng {ttl_minutes} phút.\n\n"
        "Lưu ý an toàn: Tuyệt đối không chia sẻ mã OTP cho bất kỳ ai.\n"
        "Nếu bạn không thực hiện yêu cầu này, vui lòng bỏ qua email này.\n\n"
        "MindGuard"
    )


def send_otp_email(
    email: str,
    otp_code: str,
    context: Optional[Dict[str, Any]] = None,
    config: Any = None,
    transport=None,
) -> Dict[str, Any]:
    """Send OTP email through configured provider and return normalized status.

    Return contract:
    - ok: bool
    - category: sent | timeout | transient_error | provider_rejected | network_error |
                misconfigured | unsupported_provider
    - message: user-safe guidance message (Vietnamese)
    - provider_message_id: optional provider message identifier
    """
    if config is None:
        from flask import current_app

        config = current_app.config

    # Deterministic test mode -- avoids external network dependency in unit/route tests.
    if bool(_cfg_get(config, "TESTING", False)):
        if bool(_cfg_get(config, "OTP_EMAIL_TEST_FORCE_FAIL", False)):
            return {
                "ok": False,
                "category": "test_failure",
                "message": "Không thể gửi mã OTP lúc này. Vui lòng thử lại sau vài phút.",
                "provider_message_id": None,
            }
        return {
            "ok": True,
            "category": "sent",
            "message": "Mã OTP đã được gửi đến email của bạn.",
            "provider_message_id": "test-delivery-id",
        }

    status = otp_email_delivery_status(config)
    if not status["ok"]:
        return {
            "ok": False,
            "category": status["category"],
            "message": "Hệ thống chưa sẵn sàng để gửi mã OTP. Vui lòng thử lại sau.",
            "provider_message_id": None,
        }

    provider = _email_provider(config)
    if provider == "smtp":
        return _send_smtp_otp_email(email, otp_code, config, transport=transport)

    return _send_resend_otp_email(email, otp_code, config, transport=transport)
