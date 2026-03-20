import os, uuid, requests
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
from models import db, AntiSpamEvent, ScammerReport, ScammerLeaderboard, Subscription, Registration
from services.anti_spam import AntiSpamDecisionService
from utils.encryption import hash_reporter_id, encrypt_scammer_info, validate_evidence, serialize_evidence
from utils.helpers import calculate_danger_level, login_required
from config import Config

scammer_bp = Blueprint('scammer', __name__, url_prefix='/scammer')


def _remaining_cooldown_minutes(cooldown_until, now=None):
    if not cooldown_until:
        return 0
    now = now or datetime.utcnow()
    delta = cooldown_until - now
    seconds = int(delta.total_seconds())
    if seconds <= 0:
        return 0
    return max(1, (seconds + 59) // 60)


def _anti_spam_reason_code(decision, threshold_count, now=None):
    now = now or datetime.utcnow()
    if decision.cooldown_until and decision.cooldown_until > now and decision.window_count < threshold_count:
        return "active_cooldown"
    if decision.actor_type == "account":
        return "acct_threshold"
    if decision.actor_type == "cookie":
        return "cookie_threshold"
    return "ip_threshold"


def anti_spam_reason_message(reason_code, remaining_minutes=0):
    remaining_text = ""
    if remaining_minutes > 0:
        remaining_text = f" Thoi gian con lai: {remaining_minutes} phut."

    message_map = {
        "active_cooldown": (
            "He thong dang tam cooldown vi ban da gui bao cao lien tuc."
            " Ly do: cooldown van con hieu luc."
            f"{remaining_text}"
            " Vui long thu lai sau de dam bao chat luong du lieu."
        ),
        "acct_threshold": (
            "He thong tam gioi han gui bao cao."
            " Ly do: tai khoan vuot nguong tan suat trong cua so kiem tra."
            f"{remaining_text}"
            " Vui long cho va gui lai khi het cooldown."
        ),
        "cookie_threshold": (
            "He thong tam gioi han gui bao cao."
            " Ly do: thiet bi/phien dang co tan suat gui cao bat thuong."
            f"{remaining_text}"
            " Vui long doi trong it phut roi thu lai."
        ),
        "ip_threshold": (
            "He thong tam gioi han gui bao cao."
            " Ly do: mang ket noi hien tai co tan suat gui cao bat thuong."
            f"{remaining_text}"
            " Vui long doi trong it phut roi gui lai."
        ),
        "monitor_observe": (
            "He thong dang giam sat anti-spam o che do monitor."
            " Bao cao cua ban van duoc ghi nhan, khong chan du lieu."
            " Neu tiep tuc gui lien tuc, he thong co the bat cooldown o che do enforce."
        ),
    }

    return message_map.get(
        reason_code,
        (
            "He thong anti-spam da kich hoat de bao ve du lieu."
            " Ly do: tan suat gui dang cao hon muc thong thuong."
            f"{remaining_text}"
            " Vui long thu lai sau."
        ),
    )

@scammer_bp.route("/report", methods=["GET", "POST"])
# @login_required  <-- Removed to allow anonymous reporting
def report_scammer():
    from utils.helpers import generate_math_problem
    
    if request.method == "POST":
        # 1. Validate CAPTCHA (Hybrid)
        cf_token = request.form.get('cf-turnstile-response')
        cf_secret = Config.CLOUDFLARE_SECRET_KEY
        
        captcha_success = False
        
        # Try Cloudflare
        if cf_secret and cf_token:
            try:
                verify_url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
                validate_res = requests.post(verify_url, data={'secret': cf_secret, 'response': cf_token}, timeout=2)
                if validate_res.json().get('success'):
                    captcha_success = True
            except Exception as e:
                print(f"CAPTCHA Error: {e}")
                pass 
        
        # Try Math
        if not captcha_success:
            user_math = request.form.get('math_answer')
            correct_math = session.get('math_captcha_answer_report')
            if user_math and correct_math and user_math.strip() == correct_math:
                captcha_success = True
                
        if not captcha_success:
            flash("Vui lòng hoàn thành xác thực (CAPTCHA hoặc Toán).", "danger")
            math_prob = generate_math_problem()
            session['math_captcha_answer_report'] = math_prob['answer']
            return render_template("report_scammer.html", site_key=Config.CLOUDFLARE_SITE_KEY, math_question=math_prob['question'], force_math=True)

        # 2. Validate Terms
        term_truth = request.form.get("term_truth")
        term_responsibility = request.form.get("term_responsibility")
        if not term_truth or not term_responsibility:
             flash("Vui lòng đồng ý các điều khoản.", "danger")
             # Regenerate math because redirect clears render context, although session persists.
             # Better to render template again to keep form data if possible, but redirect is safer for reset.
             # Sticking to redirect here as validation failure logic? 
             # No, let's keep consistent UX. If terms fail, we should probably stick to page.
             # But for minimal changes let's redirect.
             return redirect(url_for("scammer.report_scammer"))

        report_type = request.form.get("report_type", "general")
        
        # Khởi tạo biến
        scammer_identifier = ""
        scammer_name = ""
        scam_type = ""
        bank_name = None
        platform = ""
        description = request.form.get("description")

        # 2. Lấy dữ liệu TÙY THEO LOẠI
        if report_type == 'website':
            # Lấy từ input Website
            scammer_identifier = request.form.get("identifier_website")
            scam_type = request.form.get("scam_type_website")
            platform = request.form.get("platform_website") or "Website/Internet"
        else:
            # Lấy từ input Person
            scammer_identifier = request.form.get("identifier_person")
            scammer_name = request.form.get("scammer_name")
            scam_type = request.form.get("scam_type_person")
            
            # Xử lý nền tảng cho Person
            if report_type == 'bank':
                bank_name = request.form.get("bank_name")
                platform = "Ngân hàng"
            else:
                platform = "Mạng xã hội / Điện thoại"

        # Fallback
        if not scam_type: scam_type = "Lừa đảo khác"

        # 3. Xử lý ảnh
        evidence_list = []
        if 'evidence_files' in request.files:
            files = request.files.getlist('evidence_files')
            for file in files:
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    upload_folder = os.path.join(current_app.static_folder, 'uploads', 'evidence')
                    if not os.path.exists(upload_folder): os.makedirs(upload_folder)
                    file.save(os.path.join(upload_folder, unique_filename))
                    evidence_list.append(url_for('static', filename=f'uploads/evidence/{unique_filename}', _external=True))

        if not scammer_identifier or not description:
            flash("Thiếu thông tin bắt buộc.", "danger")
            return redirect(url_for("scammer.report_scammer"))

        if not session.get('reporter_id'): session['reporter_id'] = str(uuid.uuid4())
        reporter_hash = hash_reporter_id(session['reporter_id'])
        client_ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()

        account_id = None
        registration_email = session.get("registration_email")
        if registration_email:
            user = Registration.query.filter_by(email=registration_email).first()
            if user:
                account_id = user.id

        window_minutes = int(current_app.config.get("ABUS_WINDOW_MINUTES", Config.ABUS_WINDOW_MINUTES))
        threshold_count = int(current_app.config.get("ABUS_THRESHOLD_COUNT", Config.ABUS_THRESHOLD_COUNT))
        window_start = datetime.utcnow() - timedelta(minutes=window_minutes)

        account_signal = 0
        cookie_signal = 0
        ip_signal = 0

        if account_id:
            account_signal = int(
                AntiSpamEvent.query.filter(
                    AntiSpamEvent.actor_key == f"acct:{account_id}",
                    AntiSpamEvent.occurred_at >= window_start,
                ).count()
                >= threshold_count
            )
        if reporter_hash:
            cookie_signal = int(
                AntiSpamEvent.query.filter(
                    AntiSpamEvent.actor_key == f"cookie:{reporter_hash}",
                    AntiSpamEvent.occurred_at >= window_start,
                ).count()
                >= threshold_count
            )
        if client_ip:
            ip_signal = int(
                AntiSpamEvent.query.filter(
                    AntiSpamEvent.actor_key == f"ip:{client_ip}",
                    AntiSpamEvent.occurred_at >= window_start,
                ).count()
                >= threshold_count
            )

        anti_spam_service = AntiSpamDecisionService()
        anti_spam_decision = anti_spam_service.evaluate_submission(
            account_id=account_id,
            reporter_hash=reporter_hash,
            ip_address=client_ip,
            signal_inputs={
                "account": account_signal,
                "cookie": cookie_signal,
                "ip": ip_signal,
            },
        )

        abus_mode = str(current_app.config.get("ABUS_MODE", Config.ABUS_MODE)).lower()
        threshold_count_cfg = int(current_app.config.get("ABUS_THRESHOLD_COUNT", Config.ABUS_THRESHOLD_COUNT))
        reason_code = _anti_spam_reason_code(
            anti_spam_decision,
            threshold_count=threshold_count_cfg,
            now=datetime.utcnow(),
        )
        remaining_minutes = _remaining_cooldown_minutes(anti_spam_decision.cooldown_until)

        if abus_mode == "soft_enforce" and anti_spam_decision.should_cooldown:
            flash(anti_spam_reason_message(reason_code, remaining_minutes), "warning")
            return redirect(url_for("scammer.report_scammer"))

        if abus_mode == "monitor" and anti_spam_decision.should_cooldown:
            flash(anti_spam_reason_message("monitor_observe", remaining_minutes), "info")

        encrypted_id = encrypt_scammer_info(scammer_identifier, Config.REPORT_ENCRYPTION_KEY)
        
        # 4. Lưu DB
        existing_scammer = ScammerReport.query.filter_by(
            scammer_identifier=encrypted_id, 
            scam_type=scam_type
        ).first()

        if existing_scammer:
            existing_scammer.report_count += 1
            existing_scammer.description += f"\n\n---\n**Tố cáo #{existing_scammer.report_count}:**\n{description}"
            existing_scammer.updated_at = db.func.now()
            if not existing_scammer.scammer_name and scammer_name:
                existing_scammer.scammer_name = scammer_name
            db.session.commit()
            
            if existing_scammer.status == 'approved':
                lb = ScammerLeaderboard.query.filter_by(scammer_id=existing_scammer.id).first()
                if lb:
                    lb.total_reports = existing_scammer.report_count
                    lb.danger_level = calculate_danger_level(existing_scammer.report_count)
                    lb.last_reported = db.func.now()
                    db.session.commit()
            flash("Đã cập nhật hồ sơ Scammer có sẵn.", "info")
        else:
            new_report = ScammerReport(
                scammer_identifier=encrypted_id, 
                scammer_info_raw=scammer_identifier,
                scammer_name=scammer_name, 
                scam_type=scam_type, 
                platform=platform,
                description=description, 
                evidence_urls=serialize_evidence(evidence_list),
                reporter_hash=reporter_hash, 
                status='pending', 
                report_type=report_type, 
                bank_name=bank_name
            )
            db.session.add(new_report)
            db.session.commit()
            flash("Tố cáo website/kẻ gian đã gửi thành công.", "success")
        
        return redirect(url_for("scammer.report_scammer"))
    
    # GET: Generate math
    from utils.helpers import generate_math_problem
    math_prob = generate_math_problem()
    session['math_captcha_answer_report'] = math_prob['answer']
    
    return render_template("report_scammer.html", site_key=Config.CLOUDFLARE_SITE_KEY, math_question=math_prob['question'])

@scammer_bp.route("/follow", methods=["POST"])
@login_required
def follow_scammer():
    identifier = request.form.get("identifier")
    if not identifier:
        return {"status": "error", "message": "Missing identifier"}, 400
    
    email = session.get("registration_email")
    user = Registration.query.filter_by(email=email).first()
    if not user:
        return {"status": "error", "message": "User not found"}, 404
        
    sub = Subscription.query.filter_by(user_id=user.id, target_identifier=identifier).first()
    if sub:
        db.session.delete(sub)
        db.session.commit()
        return {"status": "unfollowed", "message": "Đã hủy theo dõi"}
    else:
        new_sub = Subscription(user_id=user.id, target_identifier=identifier)
        db.session.add(new_sub)
        db.session.commit()
        return {"status": "followed", "message": "Đã theo dõi"}
