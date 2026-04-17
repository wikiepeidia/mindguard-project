import hashlib
from datetime import datetime, timedelta

from models import AntiSpamActorState, AntiSpamEvent
from services.anti_spam import AntiSpamDecisionService


def _cfg_get(config, key, default=None):
    if isinstance(config, dict):
        value = config.get(key)
        if value is not None:
            return value
    value = getattr(config, key, None)
    if value is not None:
        return value
    return default


def build_otp_actor_id(email):
    normalized_email = (email or "").strip().lower()
    email_digest = hashlib.sha256(normalized_email.encode("utf-8")).hexdigest()
    return f"otp:{email_digest}"


def _otp_actor_key(email):
    return f"acct:{build_otp_actor_id(email)}"


def _otp_abuse_service(config):
    return AntiSpamDecisionService(
        window_minutes=int(_cfg_get(config, "OTP_ABUSE_WINDOW_MINUTES", 10) or 10),
        threshold_count=int(_cfg_get(config, "OTP_ABUSE_THRESHOLD_COUNT", 3) or 3),
        cooldown_minutes=int(_cfg_get(config, "OTP_ABUSE_COOLDOWN_MINUTES", 15) or 15),
        account_weight=100,
        cookie_weight=0,
        ip_weight=0,
    )


def get_active_otp_cooldown(email, now=None):
    current_time = now or datetime.utcnow()
    state = AntiSpamActorState.query.filter_by(actor_key=_otp_actor_key(email)).first()
    if not state or not state.cooldown_until or state.cooldown_until <= current_time:
        return None
    return state.cooldown_until


def record_otp_abuse_event(email, ip_address, config, submitted_at=None):
    current_time = submitted_at or datetime.utcnow()
    service = _otp_abuse_service(config)
    threshold_count = service.threshold_count
    actor_key = _otp_actor_key(email)
    window_start = current_time - timedelta(minutes=service.window_minutes)

    recent_count = AntiSpamEvent.query.filter(
        AntiSpamEvent.actor_key == actor_key,
        AntiSpamEvent.occurred_at >= window_start,
    ).count()
    account_signal = int(recent_count >= threshold_count)

    return service.evaluate_submission(
        account_id=build_otp_actor_id(email),
        ip_address=ip_address,
        submitted_at=current_time,
        signal_inputs={"account": account_signal, "cookie": 0, "ip": 0},
    )


def sync_otp_challenge_cooldown(challenge, cooldown_until):
    if not challenge or not cooldown_until:
        return None

    if challenge.locked_until is None or challenge.locked_until < cooldown_until:
        challenge.locked_until = cooldown_until

    if challenge.status == "active":
        challenge.status = "locked"

    return challenge.locked_until


def merge_resend_guardrail(email, resend_policy, now=None):
    current_time = now or datetime.utcnow()
    cooldown_until = get_active_otp_cooldown(email, now=current_time)
    if not cooldown_until:
        return resend_policy

    wait_seconds = int(max(1, (cooldown_until - current_time).total_seconds()))
    if resend_policy.get("ok") or wait_seconds > int(resend_policy.get("wait_seconds", 0) or 0):
        merged_policy = dict(resend_policy)
        merged_policy.update({
            "ok": False,
            "reason": "cooldown",
            "wait_seconds": wait_seconds,
            "source": "anti_spam",
        })
        return merged_policy

    return resend_policy