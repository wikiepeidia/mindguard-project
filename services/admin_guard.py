"""
Admin Guard — tự động phát hiện và khóa admin có hành vi bất thường.

Ngưỡng cảnh báo theo action (trong 24h):
  export  → 3 lần  → khóa ngay
  update  → 15 lần → khóa ngay
  view    → 30 lần → cảnh báo (không khóa)
"""
from datetime import datetime, timedelta
from models import Registration, db
from services.sensitive_access_log import log_sensitive_access, query_sensitive_access_logs

# Ngưỡng → (lock=True/False)
ACTION_LIMITS = {
    "export": (3,  True),   # vượt 3 lần export → khóa
    "update": (15, True),   # vượt 15 lần update → khóa
    "view":   (30, False),  # vượt 30 lần view → chỉ cảnh báo, không khóa
}

WINDOW_HOURS = 24


def check_and_autolock(actor_email: str, actor_id: int | None = None) -> tuple[bool, str | None]:
    """
    Kiểm tra hành vi admin trong WINDOW_HOURS giờ qua.
    Nếu vượt ngưỡng của action có lock=True → khóa tài khoản.

    Returns:
        (should_block, reason_message)
    """
    window_start = datetime.utcnow() - timedelta(hours=WINDOW_HOURS)
    recent_logs, _ = query_sensitive_access_logs(
        actor_email=actor_email,
        start_time=window_start,
    )

    # Đếm theo action
    counts: dict[str, int] = {}
    for row in recent_logs:
        if row.action != "system_lock":  # không đếm chính log khóa
            counts[row.action] = counts.get(row.action, 0) + 1

    for action, (limit, should_lock) in ACTION_LIMITS.items():
        if counts.get(action, 0) >= limit and should_lock:
            reason = f"auto_lock: {action} x{counts[action]} trong {WINDOW_HOURS}h (ngưỡng: {limit})"
            _suspend_admin(actor_email, actor_id, reason)
            return True, reason

    return False, None


def _suspend_admin(actor_email: str, actor_id: int | None, reason: str) -> None:
    """Khóa tài khoản admin trong DB và ghi log."""
    user = Registration.query.filter_by(email=actor_email).first()
    if user and not user.is_suspended:
        user.is_suspended = True
        user.suspended_reason = reason
        db.session.commit()

    # Ghi log hệ thống
    log_sensitive_access(
        actor_id=None,
        actor_email="system",
        action="system_lock",
        object_type="admin_account",
        object_id=actor_email,
        reason=reason,
    )


def unsuspend_admin(email: str) -> bool:
    """Mở khóa admin — chỉ gọi từ route có secret key. Returns True nếu thành công."""
    user = Registration.query.filter_by(email=email).first()
    if not user:
        return False
    user.is_suspended = False
    user.suspended_reason = None
    db.session.commit()

    log_sensitive_access(
        actor_id=None,
        actor_email="system",
        action="system_unlock",
        object_type="admin_account",
        object_id=email,
        reason="manual_unsuspend",
    )
    return True


def is_admin_suspended(email: str) -> tuple[bool, str | None]:
    """Kiểm tra nhanh xem admin có đang bị khóa không."""
    user = Registration.query.filter_by(email=email).first()
    if user and user.is_suspended:
        return True, user.suspended_reason
    return False, None
