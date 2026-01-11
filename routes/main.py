"""Main routes for MindGuard application."""
from flask import Blueprint, render_template, session
from models import ScamReport, Registration, QuizResult, ScammerLeaderboard, ScammerReport
from utils.helpers import calculate_danger_level

main_bp = Blueprint('main', __name__)


@main_bp.route("/")
def index():
    """Homepage with stats."""
    scam_count = ScamReport.query.count()
    registration_count = Registration.query.count()
    scammer_reports_count = ScammerReport.query.filter_by(status='approved').count()
    
    # Get top 5 scammers for display
    top_scammers = (
        ScammerLeaderboard.query
        .join(ScammerReport)
        .filter(ScammerReport.status == 'approved')
        .order_by(ScammerLeaderboard.total_reports.desc())
        .limit(5)
        .all()
    )
    
    stats = {
        "scam_count": scam_count,
        "registration_count": registration_count,
        "scammer_reports_count": scammer_reports_count,
    }
    
    return render_template("index.html", stats=stats, top_scammers=top_scammers)


@main_bp.route("/leaderboard")
def leaderboard():
    """Scammer leaderboard page - Top reported scammers."""
    top_scammers = (
        ScammerLeaderboard.query
        .join(ScammerReport)
        .filter(ScammerReport.status == 'approved')
        .order_by(ScammerLeaderboard.total_reports.desc())
        .limit(50)
        .all()
    )
    
    return render_template("leaderboard.html", top_scammers=top_scammers)
