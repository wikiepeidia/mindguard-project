"""Routes for quiz and certificate functionality."""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, QuizResult
from utils.quiz_data import quiz_questions
from utils.helpers import generate_certificate_code
from config import Config
from datetime import datetime

quiz_bp = Blueprint('quiz', __name__)


@quiz_bp.route("/quiz", methods=["GET", "POST"])
def quiz():
    """Quiz page for security awareness test."""
    if request.method == "POST":
        score = 0
        for q in quiz_questions:
            selected = request.form.get(f"q{q['id']}")
            if selected is not None and int(selected) == q["answer"]:
                score += 1

        max_score = len(quiz_questions)
        session["last_quiz_score"] = score
        session["max_quiz_score"] = max_score

        name = session.get("registration_name", "Khách MindGuard")
        email = session.get("registration_email")

        # Create quiz result
        result = QuizResult(
            name=name,
            email=email,
            score=score,
            max_score=max_score,
        )
        db.session.add(result)
        db.session.commit()
        session["last_quiz_result_id"] = result.id

        # Check if passed
        if score >= int(max_score * Config.QUIZ_PASS_PERCENTAGE):
            code = generate_certificate_code()
            session["certificate_code"] = code
            result.certificate_code = code
            db.session.commit()
            flash(
                f"🎉 Chúc mừng! Bạn đạt {score}/{max_score} điểm và có thể tránh được {score} loại lừa đảo!",
                "success",
            )
            return redirect(url_for("quiz.certificate"))
        else:
            scam_types_avoided = score
            scam_types_vulnerable = max_score - score
            flash(
                f"📊 Bạn đạt {score}/{max_score} điểm. Bạn có thể tránh được {scam_types_avoided} loại lừa đảo, "
                f"nhưng còn dễ bị lừa với {scam_types_vulnerable} loại khác. Hãy học thêm và thử lại!",
                "warning",
            )
            return redirect(url_for("quiz.quiz_result"))

    return render_template("quiz.html", questions=quiz_questions)


@quiz_bp.route("/quiz/result")
def quiz_result():
    """Quiz result page."""
    score = session.get("last_quiz_score", 0)
    max_score = session.get("max_quiz_score", 15)
    
    scam_types_avoided = score
    scam_types_vulnerable = max_score - score
    
    return render_template(
        "quiz_result.html",
        score=score,
        max_score=max_score,
        scam_types_avoided=scam_types_avoided,
        scam_types_vulnerable=scam_types_vulnerable
    )


@quiz_bp.route("/certificate")
def certificate():
    """Certificate page for successful quiz completion."""
    score = session.get("last_quiz_score")
    max_score = session.get("max_quiz_score")
    code = session.get("certificate_code")
    name = session.get("registration_name", "Người học MindGuard")
    issue_date = datetime.now().strftime("%d/%m/%Y")

    if not code:
        flash(
            "Bạn cần hoàn thành bài test với số điểm đạt yêu cầu để nhận chứng nhận.",
            "info",
        )
        return redirect(url_for("quiz.quiz"))

    scam_types_avoided = score

    return render_template(
        "certificate.html",
        score=score,
        max_score=max_score,
        code=code,
        name=name,
        issue_date=issue_date,
        scam_types_avoided=scam_types_avoided
    )
