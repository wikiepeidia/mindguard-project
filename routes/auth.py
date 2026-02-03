"""Routes for user registration."""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Registration
from werkzeug.security import generate_password_hash, check_password_hash
import random

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """User login page."""
    # Redirect if already logged in
    if session.get("registration_email"):
        return redirect(url_for("main.index"))

    from models import QuizResult
    from config import Config
    import requests
    
    if request.method == "POST":
        # 1. Validate CAPTCHA (Hybrid: Turnstile + Math Fallback)
        cf_token = request.form.get('cf-turnstile-response')
        cf_secret = Config.CLOUDFLARE_SECRET_KEY
        
        captcha_success = False
        
        # A. Try Cloudflare (if keys exist and token provided)
        if cf_secret and cf_token:
            try:
                verify_url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
                validate_res = requests.post(verify_url, data={'secret': cf_secret, 'response': cf_token}, timeout=2)
                if validate_res.json().get('success'):
                    captcha_success = True
            except:
                pass # Failed to connect to CF, proceed to Math check if available
        
        # B. Check Math Captcha (if CF failed or no keys)
        if not captcha_success:
            user_math = request.form.get('math_answer')
            correct_math = session.get('math_captcha_answer')
            # If user answered math correctly
            if user_math and correct_math and user_math.strip() == correct_math:
                captcha_success = True
            # Handling "Fail Open" only if NO keys are configured AND no math answer provided? 
            # No, user wants Math fallback for localhost (no keys).
            # If no CF keys, we require math.
            elif not cf_secret and (not correct_math): 
                 # Edge case: First load didn't generate math? Should fail.
                 pass

        if not captcha_success:
             flash("Vui lòng hoàn thành xác thực (CAPTCHA/Toán).", "danger")
             # Regenerate for re-render
             from utils.helpers import generate_math_problem
             math_prob = generate_math_problem()
             session['math_captcha_answer'] = math_prob['answer']
             return render_template("login.html", site_key=Config.CLOUDFLARE_SITE_KEY, math_question=math_prob['question'], force_math=True)

        email = request.form.get("login_email")
        password = request.form.get("login_password")
        
        user = Registration.query.filter_by(email=email).first()
        
        if user:
            if user.password_hash and check_password_hash(user.password_hash, password):
                
                # Nếu là Admin thì đuổi sang trang Admin
                if user.role == 'admin':
                    flash("Đây là tài khoản Admin. Vui lòng đăng nhập tại trang Quản trị.", "warning")
                    return redirect(url_for("admin.admin_login"))

                # --- QUAN TRỌNG: XÓA SẠCH SESSION CŨ ---
                session.clear()
                # ---------------------------------------

                session.permanent = True
                session["registration_name"] = user.name
                session["registration_email"] = user.email
                flash(f"Chào mừng trở lại, {user.name}!", "success")
                
                if user.onboarding_completed:
                     return redirect(url_for("main.index"))
                
                if QuizResult.query.filter_by(email=email).first():
                        user.onboarding_completed = True
                        db.session.commit()
                        return redirect(url_for("scammer.report_scammer"))
                else:
                        return redirect(url_for("auth.onboarding"))
            else:
                flash("Mật khẩu không đúng.", "danger")
        else:
            flash("Email chưa được đăng ký.", "warning")
            
    from config import Config
    # Generate Math Captcha for potential fallback usage
    from utils.helpers import generate_math_problem
    math_prob = generate_math_problem()
    session['math_captcha_answer'] = math_prob['answer']
    
    return render_template("login.html", site_key=Config.CLOUDFLARE_SITE_KEY, math_question=math_prob['question'])


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration page."""
    if session.get("registration_email"):
        return redirect(url_for("main.index"))

    from config import Config
    import requests
    from utils.helpers import generate_math_problem

    # Generate Math Captcha for fallback on GET
    if request.method == "GET":
         math_prob = generate_math_problem()
         session['math_captcha_answer_register'] = math_prob['answer']
         return render_template("register.html", site_key=Config.CLOUDFLARE_SITE_KEY, math_question=math_prob['question'])

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
            except:
                pass 
        
        # Try Math Fallback
        if not captcha_success:
            user_math = request.form.get('math_answer')
            correct_math = session.get('math_captcha_answer_register')
            if user_math and correct_math and user_math.strip() == correct_math:
                captcha_success = True
            # Allow pure dev mode if no keys and no math (first load issue?) -> No, enforce math.
            elif not cf_secret and (not correct_math):
                pass 
        
        if not captcha_success:
            flash("Vui lòng hoàn thành xác thực (CAPTCHA/Toán).", "danger")
            math_prob = generate_math_problem()
            session['math_captcha_answer_register'] = math_prob['answer']
            return render_template("register.html", site_key=Config.CLOUDFLARE_SITE_KEY, math_question=math_prob['question'], force_math=True)

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        date_of_birth = request.form.get("date_of_birth")
        occupation = request.form.get("occupation")
        city = request.form.get("city")

        if not name or not email or not password:
            flash("Vui lòng nhập đầy đủ Họ tên, Gmail và Mật khẩu.", "danger")
            return redirect(url_for("auth.register"))

        if not email.lower().endswith("@gmail.com"):
            flash("Vui lòng sử dụng địa chỉ Gmail cá nhân (đuôi @gmail.com).", "warning")
            return redirect(url_for("auth.register"))
            
        if Registration.query.filter_by(email=email).first():
            flash("Email này đã được đăng ký. Vui lòng đăng nhập.", "warning")
            return redirect(url_for("auth.register"))

        session['pending_registration'] = {
            'name': name,
            'email': email,
            'password': password,
            'date_of_birth': date_of_birth,
            'occupation': occupation,
            'city': city
        }
        
        flash("Mã OTP đã được gửi đến email của bạn. (Demo: 123456)", "info")
        return redirect(url_for('auth.verify_otp'))

    return render_template("register.html", site_key=Config.CLOUDFLARE_SITE_KEY)


@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    """OTP Verification page."""
    if request.method == "POST":
        otp = request.form.get("otp")
        pending_data = session.get('pending_registration')
        
        if not pending_data:
            flash("Phiên đăng ký đã hết hạn. Vui lòng đăng ký lại.", "danger")
            return redirect(url_for("auth.register"))

        if otp == "123456":
            reg = Registration(
                name=pending_data['name'],
                email=pending_data['email'],
                password_hash=generate_password_hash(pending_data['password']),
                date_of_birth=pending_data.get('date_of_birth'),
                city=pending_data['city'],
                occupation=pending_data.get('occupation'),
                role='user'
            )
            db.session.add(reg)
            db.session.commit()

            session.permanent = True
            session["registration_name"] = pending_data['name']
            session["registration_email"] = pending_data['email']
            
            session.pop('pending_registration', None)
            session.pop('captcha_answer', None)

            flash("✅ Đăng ký thành công!", "success")
            return redirect(url_for("auth.onboarding"))
        else:
            flash("Mã OTP không đúng.", "danger")
    
    return render_template("verify_otp.html")


@auth_bp.route("/onboarding")
def onboarding():
    """Onboarding choice page."""
    return render_template("onboarding.html")


@auth_bp.route("/complete-onboarding")
def complete_onboarding():
    """Mark onboarding as complete."""
    email = session.get("registration_email")
    if email:
        user = Registration.query.filter_by(email=email).first()
        if user:
            user.onboarding_completed = True
            db.session.commit()
    return redirect(url_for("main.index"))


@auth_bp.route("/profile")
def profile():
    """User profile page."""
    from models import QuizResult
    email = session.get("registration_email")
    if not email:
        flash("Bạn cần đăng nhập để xem hồ sơ.", "warning")
        return redirect(url_for("auth.login"))

    user = Registration.query.filter_by(email=email).first()
    quiz_result = QuizResult.query.filter_by(email=email).order_by(QuizResult.created_at.desc()).first()

    return render_template("profile.html", user=user, quiz_result=quiz_result)


@auth_bp.route("/profile/edit", methods=["POST"])
def edit_profile():
    """Update user profile."""
    email = session.get("registration_email")
    if not email:
        return redirect(url_for("auth.login"))
        
    user = Registration.query.filter_by(email=email).first()
    if user:
        user.name = request.form.get("name")
        user.date_of_birth = request.form.get("date_of_birth")
        user.city = request.form.get("city")
        user.phone_number = request.form.get("phone_number")
        user.bio = request.form.get("bio")
        
        db.session.commit()
        flash("Cập nhật thông tin thành công!", "success")
        
    return redirect(url_for("auth.profile"))


@auth_bp.route("/logout")
def logout():
    """User logout."""
    session.clear() # Xóa sạch session
    flash("Đã đăng xuất thành công.", "success")
    return redirect(url_for("main.index"))