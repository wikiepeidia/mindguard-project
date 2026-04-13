import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from functools import wraps
from sqlalchemy import func
from models import Registration, QuizResult, ScammerReport, ScammerLeaderboard, AntiSpamEvent, db
from werkzeug.security import check_password_hash
from config import Config
from utils.helpers import calculate_danger_level
from utils.privacy_policy import to_display_identifier
from services.sensitive_access_log import log_sensitive_access, query_sensitive_access_logs
from services.admin_guard import check_and_autolock, unsuspend_admin, is_admin_suspended
from extensions import limiter, csrf
import os
import csv
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def _get_admin_actor():
    actor_id = session.get("admin_id")
    actor_email = session.get("admin_email") or session.get("admin_name") or "unknown-admin"
    return actor_id, actor_email

def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin.admin_login"))

        admin_email = session.get("admin_email", "")
        admin_id = session.get("admin_id")

        # Kiểm tra tài khoản có đang bị khóa không
        suspended, reason = is_admin_suspended(admin_email)
        if suspended:
            session.clear()
            flash(f"Tài khoản admin đã bị tạm khóa do hành vi bất thường. Lý do: {reason}", "danger")
            return redirect(url_for("admin.admin_login"))

        # Kiểm tra hành vi trong 24h qua, tự động khóa nếu vượt ngưỡng
        blocked, block_reason = check_and_autolock(admin_email, admin_id)
        if blocked:
            session.clear()
            flash(f"Phiên làm việc bị chấm dứt do phát hiện hành vi bất thường: {block_reason}", "danger")
            return redirect(url_for("admin.admin_login"))

        return f(*args, **kwargs)
    return wrapped

@admin_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5/minute;1/second", methods=["POST"])
def admin_login():
    if session.get("is_admin"): return redirect(url_for("admin.admin_dashboard"))
    if request.method == "POST":
        user = Registration.query.filter_by(email=request.form.get("username")).first()
        if user and (user.role == 'admin' or user.is_admin) and check_password_hash(user.password_hash, request.form.get("password")):
            session.clear()
            session.permanent = True
            session["is_admin"] = True
            session["admin_name"] = user.name
            session["admin_email"] = user.email
            session["admin_id"] = user.id
            return redirect(url_for("admin.admin_dashboard"))
        flash("Đăng nhập thất bại.", "danger")
    return render_template("admin_login.html")

@admin_bp.route("/")
@admin_required
def admin_dashboard():
    # Stats
    scammer_report_count = ScammerReport.query.filter_by(status='approved').count()
    pending_reports = ScammerReport.query.filter_by(status='pending').count() 
    registration_count = Registration.query.filter_by(role='user').count()
    quiz_count = QuizResult.query.count()
    
    latest_scammer_reports = ScammerReport.query.order_by(ScammerReport.created_at.desc()).limit(5).all()
    all_users = Registration.query.order_by(Registration.role.asc(), Registration.created_at.desc()).limit(50).all()

    # Chart Data
    trend_data = db.session.query(func.strftime('%Y-%m-%d', ScammerReport.created_at).label('d'), func.count(ScammerReport.id)).group_by('d').order_by('d').limit(7).all()
    trend_labels = [d[0] for d in trend_data]
    trend_values = [d[1] for d in trend_data]

    type_data = db.session.query(ScammerReport.scam_type, func.count(ScammerReport.id)).group_by(ScammerReport.scam_type).all()
    type_labels = [t[0] for t in type_data]
    type_values = [t[1] for t in type_data]

    return render_template("admin_dashboard.html",
        scammer_report_count=scammer_report_count, pending_reports=pending_reports,
        registration_count=registration_count, quiz_count=quiz_count,
        latest_scammer_reports=latest_scammer_reports, all_users=all_users,
        trend_labels=json.dumps(trend_labels), trend_data=json.dumps(trend_values),
        type_labels=json.dumps(type_labels), type_data=json.dumps(type_values)
    )

# ... (Các route delete-user, edit-user, scammer-reports, approve, reject, export, logout giữ nguyên như phiên bản trước) ...
# (Nếu bạn cần full file này, hãy dùng nội dung tôi đã gửi ở câu trả lời trước đó cho file routes/admin.py, chỉ cần đảm bảo hàm admin_dashboard giống như trên là được)
@admin_bp.route("/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("main.index"))


@admin_bp.route("/unsuspend", methods=["POST"])
@csrf.exempt
def unsuspend_admin_account():
    """
    Mở khóa tài khoản admin bị suspend.
    Yêu cầu secret key từ Config — không cần đăng nhập.
    POST body: { secret: "...", email: "admin@..." }
    """
    secret = request.form.get("secret") or request.json.get("secret", "") if request.is_json else request.form.get("secret", "")
    email = request.form.get("email") or (request.json.get("email", "") if request.is_json else "")

    if secret != Config.ADMIN_UNSUSPEND_SECRET:
        return {"status": "error", "message": "Sai secret key."}, 403

    if unsuspend_admin(email):
        return {"status": "ok", "message": f"Đã mở khóa {email}."}, 200
    return {"status": "error", "message": "Không tìm thấy tài khoản."}, 404

@admin_bp.route("/create-admin", methods=["POST"])
@admin_required
def create_admin_account():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not name or not email or len(password) < 8:
        flash("Vui lòng điền đầy đủ thông tin, mật khẩu tối thiểu 8 ký tự.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    existing = Registration.query.filter_by(email=email).first()
    if existing:
        flash(f"Email {email} đã tồn tại trong hệ thống.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    from werkzeug.security import generate_password_hash
    new_admin = Registration(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        role="admin",
        onboarding_completed=True,
    )
    db.session.add(new_admin)
    db.session.commit()

    actor_id, actor_email = _get_admin_actor()
    log_sensitive_access(
        actor_id=actor_id,
        actor_email=actor_email,
        action="update",
        object_type="admin_account",
        object_id=email,
        reason="create_admin",
    )

    flash(f"Đã tạo tài khoản admin cho {email}.", "success")
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/delete-user/<int:user_id>", methods=["POST"])
@admin_required
def delete_user(user_id):
    user = Registration.query.get_or_404(user_id)
    if user.role != 'admin' and not user.is_admin:
        actor_id, actor_email = _get_admin_actor()
        log_sensitive_access(
            actor_id=actor_id,
            actor_email=actor_email,
            action="update",
            object_type="user",
            object_id=str(user_id),
            reason=f"delete_user:{user.email}",
        )
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route("/edit-user/<int:user_id>", methods=["POST"])
@admin_required
def edit_user(user_id):
    user = Registration.query.get_or_404(user_id)
    if user.role != 'admin' and not user.is_admin:
        actor_id, actor_email = _get_admin_actor()
        log_sensitive_access(
            actor_id=actor_id,
            actor_email=actor_email,
            action="update",
            object_type="user",
            object_id=str(user_id),
            reason=f"edit_user:{user.email}",
        )
        user.name = request.form.get("name")
        user.phone_number = request.form.get("phone_number")
        db.session.commit()
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route("/scammer-reports")
@admin_required
def scammer_reports():
    status = request.args.get('status', 'all')
    search = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 15

    query = ScammerReport.query
    if status != 'all':
        query = query.filter_by(status=status)
    if search:
        query = query.filter(ScammerReport.scammer_info_raw.ilike(f'%{search}%'))

    pagination = query.order_by(ScammerReport.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    reports = pagination.items

    for r in reports:
        if r.evidence_urls:
            try: r.evidence_list = json.loads(r.evidence_urls)
            except: r.evidence_list = []
        else: r.evidence_list = []

    actor_id, actor_email = _get_admin_actor()
    log_sensitive_access(
        actor_id=actor_id,
        actor_email=actor_email,
        action="view",
        object_type="scammer_reports",
        object_id=f"status:{status};page:{page};q:{search}",
        reason="admin_full_view",
    )

    return render_template("admin_scammer_reports.html",
        reports=reports, status_filter=status,
        pagination=pagination, search=search)

@admin_bp.route("/approve-report/<int:report_id>", methods=["POST"])
@admin_required
def approve_report(report_id):
    report = ScammerReport.query.get_or_404(report_id)
    report.status = 'approved'
    lb = ScammerLeaderboard.query.filter_by(scammer_id=report.id).first()
    if lb:
        lb.total_reports = report.report_count
        lb.danger_level = calculate_danger_level(report.report_count)
        lb.last_reported = datetime.utcnow()
    else:
        db.session.add(ScammerLeaderboard(scammer_id=report.id, total_reports=report.report_count, danger_level=calculate_danger_level(report.report_count)))
    db.session.commit()

    actor_id, actor_email = _get_admin_actor()
    log_sensitive_access(
        actor_id=actor_id,
        actor_email=actor_email,
        action="update",
        object_type="scammer_report",
        object_id=str(report.id),
        reason="approve_report",
    )

    flash("Đã duyệt.", "success")
    return redirect(request.referrer)

@admin_bp.route("/reject-report/<int:report_id>", methods=["POST"])
@admin_required
def reject_report(report_id):
    report = ScammerReport.query.get_or_404(report_id)
    report.status = 'rejected'
    db.session.commit()

    actor_id, actor_email = _get_admin_actor()
    log_sensitive_access(
        actor_id=actor_id,
        actor_email=actor_email,
        action="update",
        object_type="scammer_report",
        object_id=str(report.id),
        reason="reject_report",
    )

    flash("Đã từ chối.", "warning")
    return redirect(request.referrer)

@admin_bp.route("/export-dataset", methods=["GET", "POST"])
@admin_required
def export_dataset():
    approved_count = ScammerReport.query.filter_by(status='approved').count()

    if request.method == "GET":
        return render_template("admin_export.html", approved_count=approved_count)

    full_data_requested = request.form.get("full_data", "0") == "1"
    reason = request.form.get("reason", "").strip()

    if full_data_requested and not reason:
        flash("Vui lòng nhập lý do khi xuất dữ liệu đầy đủ.", "danger")
        return render_template("admin_export.html", approved_count=approved_count)

    dataset_dir = os.path.join(Config.BASE_DIR, 'datasets')
    if not os.path.exists(dataset_dir): os.makedirs(dataset_dir)
    filename = "scam_dataset_export.csv"
    filepath = os.path.join(dataset_dir, filename)
    reports = ScammerReport.query.filter_by(status='approved').all()
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['id', 'identifier', 'scam_type', 'platform', 'description', 'report_count', 'date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for report in reports:
            if full_data_requested:
                identifier_value = report.scammer_info_raw or 'Hidden'
            else:
                identifier_value = to_display_identifier(report.scammer_info_raw, report.report_type, is_admin=False)
            writer.writerow({
                'id': report.id,
                'identifier': identifier_value,
                'scam_type': report.scam_type,
                'platform': report.platform,
                'description': report.description,
                'report_count': report.report_count,
                'date': report.created_at.strftime('%Y-%m-%d')
            })

    actor_id, actor_email = _get_admin_actor()
    log_sensitive_access(
        actor_id=actor_id,
        actor_email=actor_email,
        action="export",
        object_type="dataset",
        object_id=f"approved_scam_reports;full={full_data_requested}",
        reason=reason or "standard_export",
    )

    return send_file(filepath, as_attachment=True, download_name=filename)


@admin_bp.route("/sensitive-access-logs")
@admin_required
def sensitive_access_logs():
    actor = (request.args.get("actor") or "").strip()
    action = (request.args.get("action") or "").strip().lower()
    start_raw = (request.args.get("start") or "").strip()
    end_raw = (request.args.get("end") or "").strip()

    start_time = None
    end_time = None
    if start_raw:
        try:
            start_time = datetime.fromisoformat(start_raw)
        except ValueError:
            start_time = None
    if end_raw:
        try:
            end_time = datetime.fromisoformat(end_raw)
        except ValueError:
            end_time = None

    page = request.args.get('page', 1, type=int)
    per_page = 20

    logs, log_pagination = query_sensitive_access_logs(
        actor_email=actor or None,
        action=action or None,
        start_time=start_time,
        end_time=end_time,
        page=page,
        per_page=per_page,
    )

    default_threshold = getattr(Config, "SENSITIVE_ACCESS_ALERT_THRESHOLD", 10)
    threshold = int(request.args.get("threshold") or default_threshold)

    # Ngưỡng riêng theo từng loại action — export nguy hiểm hơn view
    ACTION_THRESHOLDS = {"export": 3, "update": 5, "view": threshold}

    recent_window_start = datetime.utcnow() - timedelta(hours=24)
    recent_logs, _ = query_sensitive_access_logs(start_time=recent_window_start)

    # Đếm theo (actor, action) và (ip, action)
    actor_action_counts = {}
    ip_action_counts = {}
    for row in recent_logs:
        key = (row.actor_email, row.action)
        actor_action_counts[key] = actor_action_counts.get(key, 0) + 1
        if row.ip_address:
            ikey = (row.ip_address, row.action)
            ip_action_counts[ikey] = ip_action_counts.get(ikey, 0) + 1

    high_frequency_actors = list({
        actor for (actor, action), count in actor_action_counts.items()
        if count >= ACTION_THRESHOLDS.get(action, threshold)
    })
    high_frequency_ips = list({
        ip for (ip, action), count in ip_action_counts.items()
        if count >= ACTION_THRESHOLDS.get(action, threshold)
    })

    anti_spam_window_start = datetime.utcnow() - timedelta(hours=24)
    anti_spam_total_events = (
        AntiSpamEvent.query.filter(AntiSpamEvent.occurred_at >= anti_spam_window_start).count()
    )
    anti_spam_cooldown_events = (
        AntiSpamEvent.query.filter(
            AntiSpamEvent.occurred_at >= anti_spam_window_start,
            AntiSpamEvent.triggered_cooldown.is_(True),
        ).count()
    )
    risk_breakdown_rows = (
        db.session.query(AntiSpamEvent.risk_level, func.count(AntiSpamEvent.id))
        .filter(AntiSpamEvent.occurred_at >= anti_spam_window_start)
        .group_by(AntiSpamEvent.risk_level)
        .all()
    )
    actor_breakdown_rows = (
        db.session.query(AntiSpamEvent.actor_type, func.count(AntiSpamEvent.id))
        .filter(AntiSpamEvent.occurred_at >= anti_spam_window_start)
        .group_by(AntiSpamEvent.actor_type)
        .all()
    )

    anti_spam_summary = {
        "window_hours": 24,
        "total_events": anti_spam_total_events,
        "cooldown_events": anti_spam_cooldown_events,
        "risk_breakdown": {row[0] or "unknown": row[1] for row in risk_breakdown_rows},
        "actor_breakdown": {row[0] or "unknown": row[1] for row in actor_breakdown_rows},
    }

    return render_template(
        "admin_sensitive_access_logs.html",
        logs=logs,
        log_pagination=log_pagination,
        filters={"actor": actor, "action": action, "start": start_raw, "end": end_raw},
        threshold=threshold,
        high_frequency_actors=high_frequency_actors,
        high_frequency_ips=high_frequency_ips,
        anti_spam_summary=anti_spam_summary,
    )