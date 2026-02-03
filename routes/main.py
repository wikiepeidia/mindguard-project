"""Main routes for MindGuard application."""
import json
from flask import Blueprint, render_template, request, jsonify, session
from sqlalchemy import func, or_
from models import ScamReport, Registration, ScammerLeaderboard, ScammerReport, Subscription, db
from utils.helpers import mask_sensitive_data, calculate_risk_score, get_verification_badge, get_risk_level_info
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    """Homepage with stats and live feed."""
    
    # 1. Đếm số liệu
    approved_scammers_count = ScammerReport.query.filter_by(status='approved').count()
    articles_count = ScamReport.query.count() 
    total_cases = articles_count + approved_scammers_count
    registration_count = Registration.query.filter_by(role='user').count()

    stats = {
        "scam_count": total_cases,
        "registration_count": registration_count,
        "scammer_reports_count": approved_scammers_count, 
    }
    
    # 2. Lấy danh sách từ DB
    raw_scammers = (
        ScammerLeaderboard.query
        .join(ScammerReport)
        .filter(ScammerReport.status == 'approved')
        .order_by(ScammerLeaderboard.last_reported.desc()) 
        .limit(20)
        .all()
    )

    # --- [KHẮC PHỤC LỖI ẢNH] ---
    # Chuyển đổi sang list Dictionary để dữ liệu cố định, không bị DB reset
    top_scammers = []
    for entry in raw_scammers:
        # Xử lý ảnh
        img_url = ""
        if entry.scammer.evidence_urls:
            try:
                imgs = json.loads(entry.scammer.evidence_urls)
                if imgs and len(imgs) > 0:
                    img_url = imgs[0]
            except:
                img_url = ""
        
        # Đóng gói dữ liệu
        item = {
            "id": entry.scammer.id,  # Thêm ID
            "identifier": entry.scammer.scammer_info_raw,
            "name": entry.scammer.scammer_name or 'Chưa rõ danh tính',
            "type": entry.scammer.scam_type,
            "platform": entry.scammer.platform,
            "description": entry.scammer.description,
            "total_reports": entry.total_reports,
            "updated_at": entry.scammer.updated_at.strftime('%H:%M %d/%m/%Y'),
            "report_type": entry.scammer.report_type,
            "image": img_url,  # Link ảnh chuẩn
            # Thêm các trường mới
            "verification_status": entry.scammer.verification_status or 'unverified',
            "risk_score": entry.scammer.risk_score or 0,
            "confirmed_by_count": entry.scammer.confirmed_by_count or 0
        }
        top_scammers.append(item)
    # ---------------------------

    return render_template("index.html", stats=stats, top_scammers=top_scammers)

# ... (Các hàm leaderboard và search giữ nguyên) ...
# Bạn chỉ cần copy đè hàm index() ở trên, hoặc copy cả file nếu muốn chắc chắn.
# Dưới đây là phần còn lại của file để bạn tiện copy full nếu cần:

@main_bp.route("/leaderboard")
def leaderboard():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    base_query = ScammerLeaderboard.query.join(ScammerReport).filter(ScammerReport.status == 'approved').order_by(ScammerLeaderboard.total_reports.desc())
    top_3 = base_query.limit(3).all() if page == 1 else []
    pagination = base_query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template("leaderboard.html", top_3=top_3, pagination=pagination, scammers=pagination.items)

@main_bp.route("/api/search", methods=["POST"])
def search_scammer():
    data = request.get_json()
    query = data.get("query", "").strip().lower()
    if not query or len(query) < 3: return jsonify({"status": "error", "message": "Nhập ít nhất 3 ký tự."})
    clean_query = query.replace("https://", "").replace("http://", "").replace("www.", "").strip("/")
    results = ScammerReport.query.filter(ScammerReport.status == 'approved', or_(ScammerReport.scammer_info_raw.contains(query), ScammerReport.scammer_info_raw.contains(clean_query), ScammerReport.scammer_name.contains(query))).all()
    if results:
        total = sum(r.report_count for r in results)
        lst = [{"identifier": r.scammer_info_raw, "type": r.scam_type, "reports": r.report_count, "platform": r.platform, "report_type": r.report_type} for r in results]
        return jsonify({"status": "danger", "total_reports": total, "data": lst})
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

    # Mask sensitive data by default
    data_type = 'phone' if scammer.report_type == 'general' else 'account'
    masked_identifier = mask_sensitive_data(scammer.scammer_info_raw, data_type)
    
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
        is_following=is_following
    )