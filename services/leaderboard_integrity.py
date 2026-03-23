"""Leaderboard integrity service.

Provides reporter ranking computation with integrity scoring:
- Groups ScammerReport rows by reporter_hash
- Weights approved + verified reports per formula
- Excludes reporters currently in anti-spam cooldown
"""

from datetime import datetime

from sqlalchemy.exc import OperationalError

from extensions import db
from models import ScammerReport, AntiSpamActorState


def get_reporter_rankings(limit: int = 20) -> list:
    """Return top reporters ranked by integrity_score.

    Each entry contains:
        rank (int)
        reporter_hash_display (str) — first 8 chars of hash only
        total_reports (int)
        approved_reports (int)
        verified_reports (int)
        integrity_score (float)
        is_flagged (bool) — True if reporter was in cooldown (always excluded)

    Reporters currently in anti-spam cooldown are excluded entirely.
    """
    flagged = _get_flagged_hashes()

    all_reports = (
        ScammerReport.query
        .filter(ScammerReport.reporter_hash.isnot(None))
        .all()
    )

    # Aggregate per reporter_hash in Python (avoids SQLAlchemy version quirks)
    stats: dict[str, dict] = {}
    for report in all_reports:
        h = report.reporter_hash
        if h not in stats:
            stats[h] = {'total': 0, 'approved': 0, 'verified': 0}
        stats[h]['total'] += 1
        if report.status == 'approved':
            stats[h]['approved'] += 1
        if report.verification_status == 'verified':
            stats[h]['verified'] += 1

    # Build ranked list, excluding cooldown actors
    results = []
    for reporter_hash, counts in stats.items():
        if reporter_hash in flagged:
            continue  # excluded: currently in cooldown

        state = AntiSpamActorState.query.filter_by(
            reporter_hash=reporter_hash,
            actor_type='cookie',
        ).first()
        window_count = state.window_count if state else 0

        approved = counts['approved']
        verified = counts['verified']
        score = _compute_integrity_score(approved, verified, window_count)

        results.append({
            'rank': 0,
            'reporter_hash_display': reporter_hash[:8],
            'total_reports': counts['total'],
            'approved_reports': approved,
            'verified_reports': verified,
            'integrity_score': score,
            'is_flagged': False,
        })

    results.sort(key=lambda x: x['integrity_score'], reverse=True)
    results = results[:limit]

    for i, entry in enumerate(results, 1):
        entry['rank'] = i

    return results


def _compute_integrity_score(approved: int, verified: int, window_count: int) -> float:
    """Compute weighted integrity score for a reporter.

    Formula:
        base    = approved * 1.0 + verified * 0.5
        penalty = min(window_count * 0.2, base * 0.5)   # capped at 50% of base
        score   = max(base - penalty, 0.0)
    """
    base = approved * 1.0 + verified * 0.5
    penalty = min(window_count * 0.2, base * 0.5)
    return max(base - penalty, 0.0)


def _get_flagged_hashes() -> set:
    """Return set of reporter_hash values currently in anti-spam cooldown.

    Queries AntiSpamActorState for cookie-type actors whose cooldown_until
    is in the future. Privacy-safe: only hashes are returned, never emails.

    Returns empty set if the AntiSpamActorState table does not yet exist
    (e.g. during test runs with a fresh in-memory DB that pre-dates migration).
    """
    try:
        now = datetime.utcnow()
        states = (
            AntiSpamActorState.query
            .filter(
                AntiSpamActorState.actor_type == 'cookie',
                AntiSpamActorState.cooldown_until > now,
            )
            .all()
        )
        return {s.reporter_hash for s in states if s.reporter_hash}
    except OperationalError:
        return set()
