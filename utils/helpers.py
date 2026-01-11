"""Helper functions for MindGuard application."""
import random
from datetime import datetime


def generate_certificate_code() -> str:
    """Generate unique certificate code."""
    return f"MG-{random.randint(100000, 999999)}"


def generate_session_id() -> str:
    """Generate session ID for chat."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_part = random.randint(1000, 9999)
    return f"CHAT-{timestamp}-{random_part}"


def calculate_danger_level(report_count: int) -> str:
    """Calculate danger level based on report count."""
    if report_count >= 20:
        return 'critical'
    elif report_count >= 10:
        return 'high'
    elif report_count >= 5:
        return 'medium'
    else:
        return 'low'


def auto_approve_report(report_count: int, evidence_count: int, threshold: int = 3) -> bool:
    """Determine if report should be auto-approved."""
    return evidence_count >= 1 and report_count >= threshold
