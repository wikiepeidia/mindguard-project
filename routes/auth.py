"""Routes for user registration."""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Registration
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration page."""
    if request.method == "POST":
        # Check if it's a login attempt
        if "login_email" in request.form:
            email = request.form.get("login_email")
            password = request.form.get("login_password")
            
            user = Registration.query.filter_by(email=email).first()
            
            # Check password
            if user:
                if user.password_hash:
                    if check_password_hash(user.password_hash, password):
                        session["registration_name"] = user.name
                        session["registration_email"] = user.email
                        flash(f"Chào mừng trở lại, {user.name}!", "success")
                        return redirect(url_for("quiz.quiz"))
                    else:
                        flash("Mật khẩu không đúng.", "danger")
                        return redirect(url_for("auth.register"))
                else:
                    # Legacy users without password (only if you want to support them, otherwise blocking is safer)
                    # For this request, we strictly want passwords.
                    flash("Tài khoản này chưa được thiết lập mật khẩu. Vui lòng đăng ký mới.", "warning")
                    return redirect(url_for("auth.register"))
            else:
                flash("Email chưa được đăng ký. Vui lòng đăng ký mới.", "warning")
                return redirect(url_for("auth.register"))

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        age_group = request.form.get("age_group")
        occupation = request.form.get("occupation")
        city = request.form.get("city")

        if not name or not email or not password:
            flash("Vui lòng nhập đầy đủ Họ tên, Gmail và Mật khẩu.", "danger")
            return redirect(url_for("auth.register"))

        if not email.lower().endswith("@gmail.com"):
            flash("Vui lòng sử dụng địa chỉ Gmail cá nhân (đuôi @gmail.com).", "warning")
            return redirect(url_for("auth.register"))
            
        # Check existing user
        if Registration.query.filter_by(email=email).first():
            flash("Email này đã được đăng ký. Vui lòng đăng nhập.", "warning")
            return redirect(url_for("auth.register"))

        reg = Registration(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            age_group=age_group,
            occupation=occupation,
            city=city,
        )
        db.session.add(reg)
        db.session.commit()

        session["registration_name"] = name
        session["registration_email"] = email

        flash("✅ Đăng ký thành công! Bạn có thể làm bài test MindGuard ngay bây giờ.", "success")
        return redirect(url_for("quiz.quiz"))

    return render_template("register.html")

@auth_bp.route("/logout")
def logout():
    """User logout."""
    session.pop("registration_name", None)
    session.pop("registration_email", None)
    flash("Đã đăng xuất thành công.", "success")
    return redirect(url_for("main.index"))
