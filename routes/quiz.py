"""Routes for quiz and certificate functionality."""

import random
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, QuizResult
from utils.quiz_data import quiz_questions
from utils.helpers import generate_certificate_code, login_required
from utils.ai_agent import generate_dynamic_question
from config import Config
from datetime import datetime

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    """Quiz page for security awareness test."""
    
    # --- 1. KIỂM TRA THAM SỐ LÀM LẠI ---
    # Nếu URL có đuôi ?force=true (do bấm nút làm lại), ta bỏ qua kiểm tra lịch sử
    force_retake = request.args.get('force')

    # --- 2. KIỂM TRA LỊCH SỬ (Nếu không phải đang Force làm lại) ---
    if not force_retake:
        email = session.get("registration_email")
        if email:
            # Tìm kết quả đậu gần nhất
            passed_result = QuizResult.query.filter_by(email=email).filter(QuizResult.certificate_code != None).order_by(QuizResult.created_at.desc()).first()
            
            if passed_result:
                # Cập nhật Session để trang kết quả hiển thị đúng điểm cũ
                session["last_quiz_score"] = passed_result.score
                session["max_quiz_score"] = passed_result.max_score
                session["certificate_code"] = passed_result.certificate_code
                
                # Thông báo và chuyển hướng
                flash(f"Bạn đã có chứng chỉ với kết quả {passed_result.score}/{passed_result.max_score} điểm. Bạn có muốn làm lại không?", "info")
                return redirect(url_for("quiz.quiz_result"))

    # --- 3. XỬ LÝ NỘP BÀI (POST) HOẶC HIỂN THỊ CÂU HỎI (GET) ---
    
    # Tạo câu hỏi AI (giữ nguyên logic cũ)
    ai_question = generate_dynamic_question()
    
    if request.method == "POST":
        score = 0
        # Chấm điểm câu hỏi thường
        for q in quiz_questions:
            selected = request.form.get(f"q{q['id']}")
            if selected is not None and int(selected) == q["answer"]:
                score += 1
        
        # Chấm điểm câu hỏi AI
        ai_q_id = request.form.get("ai_q_id")
        if ai_q_id:
             ai_selected = request.form.get(f"q{ai_q_id}")
             ai_correct = request.form.get(f"ai_correct_{ai_q_id}")
             if ai_selected and ai_correct and ai_selected == ai_correct:
                 score += 1
                 
        max_score = 15 # Tổng điểm
        
        # Lưu điểm vào session
        session["last_quiz_score"] = score
        session["max_quiz_score"] = max_score

        name = session.get("registration_name", "Khách MindGuard")
        email = session.get("registration_email")

        # Lưu kết quả mới vào DB
        result = QuizResult(
            name=name,
            email=email,
            score=score,
            max_score=max_score,
        )
        db.session.add(result)
        db.session.commit()
        session["last_quiz_result_id"] = result.id

        # Kiểm tra đậu/trượt
        if score >= int(max_score * Config.QUIZ_PASS_PERCENTAGE):
            code = generate_certificate_code()
            session["certificate_code"] = code
            result.certificate_code = code
            db.session.commit()
            flash(
                f"🎉 Tuyệt vời! Bạn đạt {score}/{max_score} điểm. Chứng chỉ đã được cập nhật!",
                "success",
            )
            return redirect(url_for("quiz.certificate"))
        else:
            flash(
                f"📊 Kết quả: {score}/{max_score}. Bạn chưa đạt mức an toàn. Hãy thử lại để lấy chứng chỉ nhé!",
                "warning",
            )
            return redirect(url_for("quiz.quiz_result"))

    # Logic chọn câu hỏi ngẫu nhiên để hiển thị
    sample_size = 14 if ai_question else 15
    display_questions = random.sample(quiz_questions, min(len(quiz_questions), sample_size))
    
    if ai_question:
        display_questions.insert(0, ai_question)

    return render_template("quiz.html", questions=display_questions, ai_question=ai_question)


@quiz_bp.route("/quiz/result")
@login_required
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
@login_required
def certificate():
    """Certificate page for successful quiz completion."""
    score = session.get("last_quiz_score")
    max_score = session.get("max_quiz_score")
    code = session.get("certificate_code")
    name = session.get("registration_name", "Người học MindGuard")
    issue_date = datetime.now().strftime("%d/%m/%Y")

    if not code:
        flash("Bạn cần hoàn thành bài test với số điểm đạt yêu cầu để nhận chứng nhận.", "info")
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
