"""Main routes for MindGuard application."""
import json
from flask import Blueprint, render_template, request, jsonify, session
from sqlalchemy import func, or_
from models import ScamReport, Registration, ScammerLeaderboard, ScammerReport, Subscription, db
from utils.helpers import calculate_risk_score, get_verification_badge, get_risk_level_info
from utils.privacy_policy import MASKED_DATA_NOTICE, to_display_identifier
from datetime import datetime
from services.leaderboard_integrity import get_reporter_rankings

main_bp = Blueprint('main', __name__)


def serialize_public_search_result(raw_result: dict, is_admin: bool = False) -> dict:
    """Serialize search response with role-safe identifier masking."""
    identifier = to_display_identifier(
        raw_result.get("identifier", ""),
        raw_result.get("report_type", "general"),
        is_admin=is_admin,
    )
    return {
        "identifier": identifier,
        "type": raw_result.get("type"),
        "reports": raw_result.get("reports", 0),
        "platform": raw_result.get("platform"),
        "report_type": raw_result.get("report_type", "general"),
    }

@main_bp.route("/")
def index():
    """Homepage with stats and live feed."""
    
    # 1. Đếm số liệu
    approved_scammers_count = ScammerReport.query.filter_by(status='approved').count()
    total_scammer_reports_count = ScammerReport.query.count()
    articles_count = ScamReport.query.count()
    visible_scammer_count = approved_scammers_count or total_scammer_reports_count
    total_cases = articles_count + visible_scammer_count
    registration_count = Registration.query.filter_by(role='user').count()

    stats = {
        "scam_count": total_cases,
        "registration_count": registration_count,
        "scammer_reports_count": visible_scammer_count,
    }

    # 2. Lấy danh sách từ DB
    raw_leaderboard_entries = (
        ScammerLeaderboard.query
        .join(ScammerReport)
        .filter(ScammerReport.status == 'approved')
        .order_by(ScammerLeaderboard.last_reported.desc())
        .limit(20)
        .all()
    )

    # Fallback: nếu leaderboard chưa đồng bộ nhưng có dữ liệu đã duyệt,
    # vẫn hiển thị từ bảng scammer_reports để tránh trang chủ bị trống.
    approved_report_fallback = []
    if not raw_leaderboard_entries:
        approved_report_fallback = (
            ScammerReport.query
            .filter_by(status='approved')
            .order_by(ScammerReport.updated_at.desc())
            .limit(20)
            .all()
        )

    is_admin = bool(session.get('is_admin'))

    top_scammers = []
    use_leaderboard_source = bool(raw_leaderboard_entries)
    data_source = raw_leaderboard_entries if use_leaderboard_source else approved_report_fallback

    for entry in data_source:
        scammer = entry.scammer if use_leaderboard_source else entry
        total_reports = entry.total_reports if use_leaderboard_source else int(scammer.report_count or 0)

        # Xử lý ảnh
        img_url = ""
        if scammer.evidence_urls:
            try:
                imgs = json.loads(scammer.evidence_urls)
                if imgs and len(imgs) > 0:
                    img_url = imgs[0]
            except:
                img_url = ""

        updated_at_display = datetime.utcnow().strftime('%H:%M %d/%m/%Y')
        if scammer.updated_at:
            updated_at_display = scammer.updated_at.strftime('%H:%M %d/%m/%Y')

        # Đóng gói dữ liệu
        item = {
            "id": scammer.id,
            "identifier": to_display_identifier(
                scammer.scammer_info_raw,
                scammer.report_type,
                is_admin=is_admin,
            ),
            "name": scammer.scammer_name or 'Chưa rõ danh tính',
            "type": scammer.scam_type,
            "platform": scammer.platform,
            "description": scammer.description,
            "total_reports": total_reports,
            "updated_at": updated_at_display,
            "report_type": scammer.report_type,
            "image": img_url,
            "verification_status": scammer.verification_status or 'unverified',
            "risk_score": scammer.risk_score or 0,
            "confirmed_by_count": scammer.confirmed_by_count or 0
        }
        top_scammers.append(item)

    return render_template(
        "index.html",
        stats=stats,
        top_scammers=top_scammers,
        privacy_note=MASKED_DATA_NOTICE,
    )

# ... (Các hàm leaderboard và search giữ nguyên) ...
# Bạn chỉ cần copy đè hàm index() ở trên, hoặc copy cả file nếu muốn chắc chắn.
# Dưới đây là phần còn lại của file để bạn tiện copy full nếu cần:

@main_bp.route("/leaderboard")
def leaderboard():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    base_query = ScammerLeaderboard.query.join(ScammerReport).filter(ScammerReport.status == 'approved').order_by(ScammerLeaderboard.total_reports.desc())
    is_admin = bool(session.get('is_admin'))

    top_3 = base_query.limit(3).all() if page == 1 else []
    pagination = base_query.paginate(page=page, per_page=per_page, error_out=False)

    top_3_payload = []
    for entry in top_3:
        top_3_payload.append({
            "id": entry.scammer.id,
            "identifier": to_display_identifier(entry.scammer.scammer_info_raw, entry.scammer.report_type, is_admin=is_admin),
            "name": entry.scammer.scammer_name,
            "type": entry.scammer.scam_type,
            "platform": entry.scammer.platform,
            "description": entry.scammer.description,
            "total_reports": entry.total_reports,
            "updated_at": entry.scammer.updated_at.strftime('%H:%M %d/%m/%Y'),
            "updated_date": entry.scammer.updated_at.strftime('%d/%m/%Y'),
            "report_type": entry.scammer.report_type,
            "verification_status": entry.scammer.verification_status or 'unverified',
            "evidence_urls": entry.scammer.evidence_urls,
        })

    scammers_payload = []
    for entry in pagination.items:
        scammers_payload.append({
            "id": entry.scammer.id,
            "identifier": to_display_identifier(entry.scammer.scammer_info_raw, entry.scammer.report_type, is_admin=is_admin),
            "name": entry.scammer.scammer_name,
            "type": entry.scammer.scam_type,
            "platform": entry.scammer.platform,
            "description": entry.scammer.description,
            "total_reports": entry.total_reports,
            "updated_at": entry.scammer.updated_at.strftime('%H:%M %d/%m/%Y'),
            "updated_date": entry.scammer.updated_at.strftime('%d/%m/%Y'),
            "report_type": entry.scammer.report_type,
            "verification_status": entry.scammer.verification_status or 'unverified',
            "evidence_urls": entry.scammer.evidence_urls,
        })

    reporter_rankings = get_reporter_rankings(limit=10)

    return render_template(
        "leaderboard.html",
        top_3=top_3_payload,
        pagination=pagination,
        scammers=scammers_payload,
        privacy_note=MASKED_DATA_NOTICE,
        reporter_rankings=reporter_rankings,
    )

@main_bp.route("/api/search", methods=["POST"])
def search_scammer():
    data = request.get_json()
    query = data.get("query", "").strip().lower()
    if not query or len(query) < 3: return jsonify({"status": "error", "message": "Nhập ít nhất 3 ký tự."})
    clean_query = query.replace("https://", "").replace("http://", "").replace("www.", "").strip("/")
    results = ScammerReport.query.filter(ScammerReport.status == 'approved', or_(ScammerReport.scammer_info_raw.contains(query), ScammerReport.scammer_info_raw.contains(clean_query), ScammerReport.scammer_name.contains(query))).all()
    if results:
        is_admin = bool(session.get('is_admin'))
        total = sum(r.report_count for r in results)
        lst = [
            serialize_public_search_result(
                {
                    "identifier": r.scammer_info_raw,
                    "type": r.scam_type,
                    "reports": r.report_count,
                    "platform": r.platform,
                    "report_type": r.report_type,
                },
                is_admin=is_admin,
            )
            for r in results
        ]
        return jsonify({"status": "danger", "total_reports": total, "data": lst, "privacy_note": MASKED_DATA_NOTICE})
    return jsonify({"status": "safe"})

@main_bp.route("/scammer/<int:scammer_id>")
def scammer_profile(scammer_id):
    """Display detailed scammer profile."""
    scammer = ScammerReport.query.get_or_404(scammer_id)
    
    # Check follow status
    is_following = False
    if session.get('registration_email'):
        user = Registration.query.filter_by(email=session['registration_email']).first()
        if user:
            sub = Subscription.query.filter_by(user_id=user.id, target_identifier=scammer.scammer_info_raw).first()
            if sub:
                is_following = True

    is_admin = bool(session.get('is_admin'))
    masked_identifier = to_display_identifier(
        scammer.scammer_info_raw,
        scammer.report_type,
        is_admin=is_admin,
    )
    
    # Calculate risk score if not set
    if not scammer.risk_score:
        days_since = (datetime.utcnow() - scammer.created_at).days
        has_evidence = bool(scammer.evidence_urls)
        scammer.risk_score = calculate_risk_score(
            int(scammer.report_count),
            int(scammer.confirmed_by_count or 0),
            has_evidence,
            days_since
        )
        db.session.commit()
    
    # Get verification badge
    verification_badge = get_verification_badge(scammer.verification_status or 'unverified')
    
    # Get risk level info
    risk_info = get_risk_level_info(scammer.risk_score or 0)
    
    # Parse evidence images
    evidence_images = []
    if scammer.evidence_urls:
        try:
            evidence_images = json.loads(scammer.evidence_urls)
        except:
            pass
    
    return render_template(
        "scammer_profile.html",
        scammer=scammer,
        masked_identifier=masked_identifier,
        verification_badge=verification_badge,
        risk_info=risk_info,
        evidence_images=evidence_images,
        is_following=is_following,
        privacy_note=MASKED_DATA_NOTICE,
        can_view_full_sensitive=is_admin,
    )