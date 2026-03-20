from flask import Blueprint, jsonify, request
from models import ScammerReport, ScamReport, ScammerLeaderboard
from sqlalchemy import or_
from utils.privacy_policy import MASKED_DATA_NOTICE, to_display_identifier

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


def serialize_public_check_result(raw_result: dict, is_admin: bool = False) -> dict:
    """Serialize check endpoint payload using shared privacy policy."""
    risk_score = raw_result.get("risk_score", 0) or 0
    return {
        "identifier": to_display_identifier(
            raw_result.get("identifier", ""),
            raw_result.get("report_type", "general"),
            is_admin=is_admin,
        ),
        "risk_score": risk_score,
        "reports_count": raw_result.get("reports_count", 0),
        "type": raw_result.get("type"),
        "verification_status": raw_result.get("verification_status") or "unverified",
        "danger_level": "High" if risk_score > 70 else "Medium" if risk_score > 40 else "Low",
    }

@api_bp.route('/check', methods=['GET'])
def check_scammer():
    """
    Public API to check for scammer info.
    Query Params: q (identifier to check)
    Returns: JSON with risk score and status
    """
    query = request.args.get('q', '').strip()
    if not query or len(query) < 3:
        return jsonify({
            "status": "error",
            "message": "Query too short (min 3 chars)"
        }), 400

    clean_query = query.replace("https://", "").replace("http://", "").replace("www.", "").strip("/")
    
    # Simple logic similar to main search
    results = ScammerReport.query.filter(
        ScammerReport.status == 'approved', 
        or_(
            ScammerReport.scammer_info_raw.contains(query), 
            ScammerReport.scammer_info_raw.contains(clean_query),
            ScammerReport.scammer_name.contains(query)
        )
    ).all()

    if results:
        top_match = results[0]
        payload = serialize_public_check_result(
            {
                "identifier": top_match.scammer_info_raw,
                "report_type": top_match.report_type,
                "risk_score": top_match.risk_score,
                "reports_count": top_match.report_count,
                "type": top_match.scam_type,
                "verification_status": top_match.verification_status,
            },
            is_admin=False,
        )
        return jsonify({
            "found": True,
            "data": payload,
            "privacy_note": MASKED_DATA_NOTICE,
        })
    else:
        return jsonify({
            "found": False,
            "message": "No reports found for this identifier"
        })

@api_bp.route('/stats', methods=['GET'])
def stats():
    """Public stats API"""
    total_scammers = ScammerReport.query.filter_by(status='approved').count()
    total_articles = ScamReport.query.count()
    return jsonify({
        "total_reports": total_scammers,
        "knowledge_articles": total_articles
    })
