"""Routes for scammer reporting system."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, ScamReport, ScammerReport, ScammerLeaderboard
from utils.encryption import hash_reporter_id, encrypt_scammer_info, validate_evidence, serialize_evidence, deserialize_evidence
from utils.helpers import calculate_danger_level, auto_approve_report
from config import Config
import uuid

scammer_bp = Blueprint('scammer', __name__, url_prefix='/scammer')


@scammer_bp.route("/report", methods=["GET", "POST"])
def report_scammer():
    """Report a scammer with anonymity and evidence."""
    if request.method == "POST":
        scammer_identifier = request.form.get("scammer_identifier")  # Phone, account, etc
        scammer_name = request.form.get("scammer_name", "")
        scam_type = request.form.get("scam_type")
        platform = request.form.get("platform")
        description = request.form.get("description")
        
        # Get evidence URLs (up to 5)
        evidence_list = []
        for i in range(1, 6):
            evidence = request.form.get(f"evidence_{i}", "").strip()
            if evidence:
                evidence_list.append(evidence)
        
        consent = request.form.get("consent") == "on"
        
        if not scammer_identifier or not scam_type or not description or not consent:
            flash("Vui lòng điền đầy đủ thông tin bắt buộc và xác nhận chia sẻ.", "danger")
            return redirect(url_for("scammer.report_scammer"))
        
        # Validate evidence
        if not validate_evidence(evidence_list):
            flash("Vui lòng cung cấp ít nhất 1 bằng chứng rõ ràng (ảnh, link, v.v.).", "warning")
            return redirect(url_for("scammer.report_scammer"))
        
        # Generate anonymous reporter hash
        if not session.get('reporter_id'):
            session['reporter_id'] = str(uuid.uuid4())
        
        reporter_hash = hash_reporter_id(session['reporter_id'])
        
        # Encrypt scammer identifier
        encrypted_id = encrypt_scammer_info(scammer_identifier, Config.REPORT_ENCRYPTION_KEY)
        
        # Check if this scammer already exists
        existing_scammer = ScammerReport.query.filter_by(
            scammer_identifier=encrypted_id,
            scam_type=scam_type
        ).first()
        
        if existing_scammer:
            # Increment report count
            existing_scammer.report_count += 1
            existing_scammer.description += f"\n\n---\n**Tố cáo #{existing_scammer.report_count}:**\n{description}"
            
            # Check auto-approval
            if auto_approve_report(existing_scammer.report_count, len(evidence_list), Config.AUTO_APPROVE_THRESHOLD):
                existing_scammer.status = 'approved'
                flash("Tố cáo của bạn đã được duyệt tự động vì scammer này đã bị tố cáo nhiều lần!", "success")
            else:
                flash("Tố cáo của bạn đã được ghi nhận và đang chờ xét duyệt.", "info")
            
            db.session.commit()
            
            # Update leaderboard
            leaderboard_entry = ScammerLeaderboard.query.filter_by(scammer_id=existing_scammer.id).first()
            if leaderboard_entry:
                leaderboard_entry.total_reports = existing_scammer.report_count
                leaderboard_entry.danger_level = calculate_danger_level(existing_scammer.report_count)
            elif existing_scammer.status == 'approved':
                leaderboard_entry = ScammerLeaderboard(
                    scammer_id=existing_scammer.id,
                    total_reports=existing_scammer.report_count,
                    danger_level=calculate_danger_level(existing_scammer.report_count)
                )
                db.session.add(leaderboard_entry)
            
            db.session.commit()
        else:
            # Create new scammer report
            new_report = ScammerReport(
                scammer_identifier=encrypted_id,
                scammer_name=scammer_name,
                scam_type=scam_type,
                platform=platform,
                description=description,
                evidence_urls=serialize_evidence(evidence_list),
                reporter_hash=reporter_hash,
                status='pending'
            )
            
            # Check auto-approval for first report
            if len(evidence_list) >= 2:  # Strong evidence
                new_report.status = 'approved'
                flash("Tố cáo của bạn đã được duyệt tự động nhờ có nhiều bằng chứng!", "success")
            else:
                flash("Tố cáo của bạn đã được ghi nhận và đang chờ xét duyệt.", "info")
            
            db.session.add(new_report)
            db.session.commit()
            
            # Add to leaderboard if approved
            if new_report.status == 'approved':
                leaderboard_entry = ScammerLeaderboard(
                    scammer_id=new_report.id,
                    total_reports=1,
                    danger_level='low'
                )
                db.session.add(leaderboard_entry)
                db.session.commit()
        
        return redirect(url_for("scammer.report_scammer"))
    
    # Get recent approved scammer reports
    recent_scammers = (
        ScammerReport.query
        .filter_by(status='approved')
        .order_by(ScammerReport.updated_at.desc())
        .limit(5)
        .all()
    )
    
    return render_template("report_scammer.html", scammers=recent_scammers)


@scammer_bp.route("/old-report", methods=["GET", "POST"])
def report_scam():
    """Old scam scenario reporting (keep for compatibility)."""
    if request.method == "POST":
        title = request.form.get("title")
        category = request.form.get("category")
        channel = request.form.get("channel")
        description = request.form.get("description")
        protection_tip = request.form.get("protection_tip")
        consent = request.form.get("consent") == "on"

        if not title or not description or not consent:
            flash(
                "Vui lòng điền đầy đủ thông tin bắt buộc và xác nhận chia sẻ kịch bản.",
                "danger",
            )
            return redirect(url_for("scammer.report_scam"))

        report = ScamReport(
            title=title,
            category=category,
            channel=channel,
            description=description,
            protection_tip=protection_tip,
        )
        db.session.add(report)
        db.session.commit()

        flash(
            "Cảm ơn bạn! Kịch bản lừa đảo của bạn đã được gửi cho MindGuard.",
            "success",
        )
        return redirect(url_for("scammer.report_scam"))

    recent_scams = (
        ScamReport.query.order_by(ScamReport.created_at.desc()).limit(5).all()
    )
    return render_template("report_scam.html", scams=recent_scams)
