from datetime import datetime, timedelta

from flask import request

from extensions import db
from models import SensitiveAccessLog


def log_sensitive_access(
    actor_email,
    action,
    object_type,
    object_id,
    reason=None,
    actor_id=None,
):
    """Persist one sensitive access event with request metadata."""
    user_agent = None
    ip_address = None

    try:
        if request:
            ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
            user_agent = request.headers.get("User-Agent")
            if not user_agent and request.user_agent:
                user_agent = request.user_agent.string
    except RuntimeError:
        # Allows service usage in jobs/tests without an active request context.
        pass

    row = SensitiveAccessLog(
        actor_id=actor_id,
        actor_email=(actor_email or "unknown").strip() or "unknown",
        action=(action or "view").strip().lower(),
        object_type=(object_type or "unknown").strip(),
        object_id=str(object_id),
        reason=(reason or None),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.session.add(row)
    db.session.commit()
    return row


def query_sensitive_access_logs(actor_email=None, action=None, start_time=None, end_time=None, page=None, per_page=20):
    """Query logs with optional filters. Returns (list, pagination) if page given, else (list, None)."""
    query = SensitiveAccessLog.query

    if actor_email:
        query = query.filter(SensitiveAccessLog.actor_email == actor_email)
    if action:
        query = query.filter(SensitiveAccessLog.action == action)
    if start_time:
        query = query.filter(SensitiveAccessLog.created_at >= start_time)
    if end_time:
        query = query.filter(SensitiveAccessLog.created_at <= end_time)

    query = query.order_by(SensitiveAccessLog.created_at.desc())

    if page is not None:
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return pagination.items, pagination

    return query.all(), None


def cleanup_expired_sensitive_access_logs(retention_days=90, now=None):
    """Delete old logs according to retention policy. Returns deleted row count."""
    reference = now or datetime.utcnow()
    cutoff = reference - timedelta(days=retention_days)

    deleted_count = (
        SensitiveAccessLog.query.filter(SensitiveAccessLog.created_at < cutoff)
        .delete(synchronize_session=False)
    )
    db.session.commit()
    return deleted_count
