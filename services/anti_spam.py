from dataclasses import dataclass
from datetime import datetime, timedelta

from flask import current_app

from extensions import db
from models import AntiSpamActorState, AntiSpamEvent


@dataclass
class AntiSpamDecision:
    actor_key: str
    actor_type: str
    risk_score: int
    risk_level: str
    window_count: int
    should_cooldown: bool
    cooldown_until: datetime | None


class AntiSpamDecisionService:
    def __init__(
        self,
        window_minutes=None,
        threshold_count=None,
        cooldown_minutes=None,
        account_weight=None,
        cookie_weight=None,
        ip_weight=None,
    ):
        self.window_minutes = int(window_minutes or self._cfg("ABUS_WINDOW_MINUTES", 10))
        self.threshold_count = int(threshold_count or self._cfg("ABUS_THRESHOLD_COUNT", 3))
        self.cooldown_minutes = int(cooldown_minutes or self._cfg("ABUS_COOLDOWN_MINUTES", 15))
        self.account_weight = int(account_weight or self._cfg("ABUS_ACCOUNT_WEIGHT", 70))
        self.cookie_weight = int(cookie_weight or self._cfg("ABUS_COOKIE_WEIGHT", 20))
        self.ip_weight = int(ip_weight or self._cfg("ABUS_IP_WEIGHT", 10))

    def _cfg(self, key, default):
        try:
            return current_app.config.get(key, default)
        except RuntimeError:
            return default

    def canonicalize_actor(self, account_id=None, reporter_hash=None, ip_address=None):
        if account_id:
            return f"acct:{account_id}"
        if reporter_hash:
            return f"cookie:{reporter_hash}"
        if ip_address:
            return f"ip:{self._normalize_ip(ip_address)}"
        return "ip:unknown"

    def _actor_type(self, actor_key):
        if actor_key.startswith("acct:"):
            return "account"
        if actor_key.startswith("cookie:"):
            return "cookie"
        return "ip"

    def _normalize_ip(self, ip_address):
        return (ip_address or "unknown").split(",")[0].strip()

    def calculate_score(self, account_signal=0, cookie_signal=0, ip_signal=0):
        score = (
            int(bool(account_signal)) * self.account_weight
            + int(bool(cookie_signal)) * self.cookie_weight
            + int(bool(ip_signal)) * self.ip_weight
        )
        return max(0, min(100, score))

    def map_risk_level(self, score):
        if score >= 70:
            return "high"
        if score >= 20:
            return "medium"
        return "low"

    def evaluate_submission(
        self,
        account_id=None,
        reporter_hash=None,
        ip_address=None,
        submitted_at=None,
        signal_inputs=None,
    ):
        now = submitted_at or datetime.utcnow()
        signals = signal_inputs or {"account": 0, "cookie": 0, "ip": 0}

        actor_key = self.canonicalize_actor(
            account_id=account_id,
            reporter_hash=reporter_hash,
            ip_address=ip_address,
        )
        actor_type = self._actor_type(actor_key)

        score = self.calculate_score(
            account_signal=signals.get("account", 0),
            cookie_signal=signals.get("cookie", 0),
            ip_signal=signals.get("ip", 0),
        )
        risk_level = self.map_risk_level(score)

        window_start = now - timedelta(minutes=self.window_minutes)
        recent_count = (
            AntiSpamEvent.query.filter(
                AntiSpamEvent.actor_key == actor_key,
                AntiSpamEvent.occurred_at >= window_start,
            ).count()
        )
        window_count = recent_count + 1

        state = AntiSpamActorState.query.filter_by(actor_key=actor_key).first()
        if not state:
            state = AntiSpamActorState(
                actor_key=actor_key,
                actor_type=actor_type,
            )
            db.session.add(state)

        active_cooldown = bool(state.cooldown_until and state.cooldown_until > now)
        reached_threshold = window_count >= self.threshold_count
        should_cooldown = active_cooldown or reached_threshold

        cooldown_until = state.cooldown_until if active_cooldown else None
        if reached_threshold:
            next_cooldown = now + timedelta(minutes=self.cooldown_minutes)
            if cooldown_until:
                cooldown_until = max(cooldown_until, next_cooldown)
            else:
                cooldown_until = next_cooldown

        state.actor_type = actor_type
        state.account_id = str(account_id) if account_id else None
        state.reporter_hash = reporter_hash
        state.ip_address = self._normalize_ip(ip_address)
        state.window_started_at = window_start
        state.window_count = window_count
        state.cooldown_until = cooldown_until
        state.last_risk_score = score
        state.last_risk_level = risk_level
        state.last_seen_at = now

        event = AntiSpamEvent(
            actor_key=actor_key,
            actor_type=actor_type,
            account_id=str(account_id) if account_id else None,
            reporter_hash=reporter_hash,
            ip_address=self._normalize_ip(ip_address),
            risk_score=score,
            risk_level=risk_level,
            window_count=window_count,
            triggered_cooldown=should_cooldown,
            cooldown_until=cooldown_until,
            occurred_at=now,
        )
        db.session.add(event)
        db.session.commit()

        return AntiSpamDecision(
            actor_key=actor_key,
            actor_type=actor_type,
            risk_score=score,
            risk_level=risk_level,
            window_count=window_count,
            should_cooldown=should_cooldown,
            cooldown_until=cooldown_until,
        )
