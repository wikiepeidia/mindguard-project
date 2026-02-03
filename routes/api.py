from flask import Blueprint, jsonify, request
from models import ScammerReport, ScamReport, ScammerLeaderboard
from sqlalchemy import or_

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

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
        return jsonify({
            "found": True,
            "data": {
                "identifier": top_match.scammer_info_raw,
                "risk_score": top_match.risk_score or 0,
                "reports_count": top_match.report_count,
                "type": top_match.scam_type,
                "verification_status": top_match.verification_status or "unverified",
                "danger_level": "High" if (top_match.risk_score or 0) > 70 else "Medium" if (top_match.risk_score or 0) > 40 else "Low"
            }
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
