"""OTP email delivery service.

Phase 21 provider contract:
- Default provider: Resend API
- Credentials: environment-derived config only
- Behavior: bounded timeout + single retry + normalized result payload
"""
import math
from typing import Any, Dict, Optional

import requests


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


def otp_email_delivery_status(config: Any) -> Dict[str, Any]:
    """Validate provider and required credentials for OTP email delivery."""
    provider = str(_cfg_get(config, "EMAIL_PROVIDER", "resend_api") or "resend_api").strip().lower()
    if provider != "resend_api":
        return {
            "ok": False,
            "category": "unsupported_provider",
            "message": "Nhà cung cấp email OTP không được hỗ trợ.",
            "missing": ["EMAIL_PROVIDER(resend_api)"],
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
