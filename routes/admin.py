import json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from functools import wraps
from sqlalchemy import func
from models import Registration, QuizResult, ScammerReport, ScammerLeaderboard, db
from werkzeug.security import check_password_hash
from config import Config
from utils.helpers import calculate_danger_level

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"): return redirect(url_for("admin.admin_login"))
        return f(*args, **kwargs)
    return wrapped

@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    if session.get("is_admin"): return redirect(url_for("admin.admin_dashboard"))
    if request.method == "POST":
        user = Registration.query.filter_by(email=request.form.get("username")).first()
        if user and (user.role == 'admin' or user.is_admin) and check_password_hash(user.password_hash, request.form.get("password")):
            session.clear()
            session.permanent = True
            session["is_admin"] = True
            session["admin_name"] = user.name
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

@admin_bp.route("/delete-user/<int:user_id>", methods=["POST"])
@admin_required
def delete_user(user_id):
    user = Registration.query.get_or_404(user_id)
    if user.role != 'admin' and not user.is_admin:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route("/edit-user/<int:user_id>", methods=["POST"])
@admin_required
def edit_user(user_id):
    user = Registration.query.get_or_404(user_id)
    if user.role != 'admin' and not user.is_admin:
        user.name = request.form.get("name")
        user.phone_number = request.form.get("phone_number")
        db.session.commit()
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route("/scammer-reports")
@admin_required
def scammer_reports():
    status = request.args.get('status', 'all')
    query = ScammerReport.query
    if status != 'all': query = query.filter_by(status=status)
    reports = query.order_by(ScammerReport.created_at.desc()).all()
    # Handle evidence JSON
    for r in reports:
        if r.evidence_urls:
            try: r.evidence_list = json.loads(r.evidence_urls)
            except: r.evidence_list = []
        else: r.evidence_list = []
    return render_template("admin_scammer_reports.html", reports=reports, status_filter=status)

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
    flash("Đã duyệt.", "success")
    return redirect(request.referrer)

@admin_bp.route("/reject-report/<int:report_id>", methods=["POST"])
@admin_required
def reject_report(report_id):
    report = ScammerReport.query.get_or_404(report_id)
    report.status = 'rejected'
    db.session.commit()
    flash("Đã từ chối.", "warning")
    return redirect(request.referrer)

@admin_bp.route("/export-dataset")
@admin_required
def export_dataset():
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
            writer.writerow({
                'id': report.id,
                'identifier': report.scammer_info_raw or 'Hidden',
                'scam_type': report.scam_type,
                'platform': report.platform,
                'description': report.description,
                'report_count': report.report_count,
                'date': report.created_at.strftime('%Y-%m-%d')
            })
    return send_file(filepath, as_attachment=True, download_name=filename)