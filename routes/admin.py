"""Admin routes and dashboard."""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from models import ScamReport, Registration, QuizResult, ScammerReport, ScammerLeaderboard, db
from config import Config

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(view_func):
    """Decorator to require admin login."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Bạn cần đăng nhập với vai trò Admin.", "warning")
            return redirect(url_for("admin.admin_login", next=request.path))
        return view_func(*args, **kwargs)
    return wrapped


@admin_bp.route("/login", methods=["GET", "POST"])
def admin_login():
    """Admin login page."""
    if session.get("is_admin"):
        return redirect(url_for("admin.admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            session["is_admin"] = True
            flash("Đăng nhập Admin thành công.", "success")
            next_url = request.args.get("next") or url_for("admin.admin_dashboard")
            return redirect(next_url)
        else:
            flash("Tài khoản hoặc mật khẩu không đúng.", "danger")
            return redirect(url_for("admin.admin_login"))
    return render_template("admin_login.html")


@admin_bp.route("/logout")
def admin_logout():
    """Admin logout."""
    session.pop("is_admin", None)
    flash("Bạn đã đăng xuất Admin.", "info")
    return redirect(url_for("main.index"))


@admin_bp.route("/")
@admin_required
def admin_dashboard():
    """Admin dashboard with statistics."""
    scam_count = ScamReport.query.count()
    registration_count = Registration.query.count()
    quiz_count = QuizResult.query.count()
    scammer_report_count = ScammerReport.query.count()
    pending_reports = ScammerReport.query.filter_by(status='pending').count()
    
    latest_scams = ScamReport.query.order_by(ScamReport.created_at.desc()).limit(10).all()
    latest_regs = Registration.query.order_by(Registration.created_at.desc()).limit(10).all()
    latest_results = QuizResult.query.order_by(QuizResult.created_at.desc()).limit(10).all()
    latest_scammer_reports = ScammerReport.query.order_by(ScammerReport.created_at.desc()).limit(10).all()
    
    return render_template(
        "admin_dashboard.html",
        scam_count=scam_count,
        registration_count=registration_count,
        quiz_count=quiz_count,
        scammer_report_count=scammer_report_count,
        pending_reports=pending_reports,
        latest_scams=latest_scams,
        latest_regs=latest_regs,
        latest_results=latest_results,
        latest_scammer_reports=latest_scammer_reports,
    )


@admin_bp.route("/scammer-reports")
@admin_required
def scammer_reports():
    """View all scammer reports."""
    status_filter = request.args.get('status', 'all')
    
    query = ScammerReport.query
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    reports = query.order_by(ScammerReport.created_at.desc()).all()
    
    return render_template("admin_scammer_reports.html", reports=reports, status_filter=status_filter)


@admin_bp.route("/approve-report/<int:report_id>", methods=["POST"])
@admin_required
def approve_report(report_id):
    """Approve a scammer report."""
    report = ScammerReport.query.get_or_404(report_id)
    report.status = 'approved'
    db.session.commit()
    
    # Add/update leaderboard
    leaderboard_entry = ScammerLeaderboard.query.filter_by(scammer_id=report.id).first()
    if not leaderboard_entry:
        from utils.helpers import calculate_danger_level
        leaderboard_entry = ScammerLeaderboard(
            scammer_id=report.id,
            total_reports=report.report_count,
            danger_level=calculate_danger_level(report.report_count)
        )
        db.session.add(leaderboard_entry)
        db.session.commit()
    
    flash(f"Tố cáo #{report_id} đã được duyệt.", "success")
    return redirect(url_for("admin.scammer_reports"))


@admin_bp.route("/reject-report/<int:report_id>", methods=["POST"])
@admin_required
def reject_report(report_id):
    """Reject a scammer report."""
    report = ScammerReport.query.get_or_404(report_id)
    report.status = 'rejected'
    db.session.commit()
    
    flash(f"Tố cáo #{report_id} đã bị từ chối.", "warning")
    return redirect(url_for("admin.scammer_reports"))
