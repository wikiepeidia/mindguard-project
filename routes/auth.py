"""Routes for user registration."""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Registration

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration page."""
    if request.method == "POST":
        # Check if it's a login attempt
        if "login_email" in request.form:
            email = request.form.get("login_email")
            user = Registration.query.filter_by(email=email).first()
            if user:
                session["registration_name"] = user.name
                session["registration_email"] = user.email
                flash(f"Chào mừng trở lại, {user.name}!", "success")
                return redirect(url_for("quiz.quiz"))
            else:
                flash("Email chưa được đăng ký. Vui lòng đăng ký mới.", "warning")
                return redirect(url_for("auth.register"))

        name = request.form.get("name")
        email = request.form.get("email")
        age_group = request.form.get("age_group")
        occupation = request.form.get("occupation")
        city = request.form.get("city")

        if not name or not email:
            flash("Vui lòng nhập đầy đủ Họ tên và Gmail.", "danger")
            return redirect(url_for("auth.register"))

        if not email.lower().endswith("@gmail.com"):
            flash("Vui lòng sử dụng địa chỉ Gmail cá nhân (đuôi @gmail.com).", "warning")
            return redirect(url_for("auth.register"))

        reg = Registration(
            name=name,
            email=email,
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
