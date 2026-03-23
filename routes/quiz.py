"""Routes for quiz and certificate functionality.

Implements a server-driven one-question-per-step quiz flow:
  - GET  /quiz              — start or resume attempt, redirect to current step
  - GET  /quiz/step/<idx>   — render single question for step idx
  - POST /quiz/step/<idx>   — save answer, redirect to next step (PRG)
  - GET  /quiz/finalize     — compute score, write ONE QuizResult, redirect
  - GET  /quiz/result       — score summary (unchanged contract)
  - GET  /certificate       — certificate page (unchanged contract)

Session key: quiz_attempt = {
    question_ids: [int, ...],   # ordered IDs, frozen at attempt start
    ai_q: dict | None,          # full AI question dict (only 1, avoids cookie bloat)
    answers: {str(id): int},    # submitted option index per question
    current_index: int,
    total_questions: int,
    attempt_id: str,            # UUID, deduplicates concurrent attempts
    finalized: bool,            # guards against duplicate DB writes on refresh
}
"""

import random
import uuid
from datetime import datetime

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash,
)

from extensions import db
from models import QuizResult
from utils.quiz_data import quiz_questions
from utils.helpers import generate_certificate_code, login_required
from utils.ai_agent import generate_dynamic_question
from config import Config

quiz_bp = Blueprint('quiz', __name__)

# ------------------------------------------------------------------ #
# Internal helpers
# ------------------------------------------------------------------ #

_static_by_id = {q['id']: q for q in quiz_questions}


def _create_attempt():
    """Sample questions, freeze order, store compact attempt in session.

    Stores only question IDs (small ints) + one optional AI question dict
    to stay well within the Flask signed-cookie size limit (~4 KB).
    """
    ai_q = generate_dynamic_question()

    sample_size = 14 if ai_q else 15
    static_sample = random.sample(quiz_questions, min(len(quiz_questions), sample_size))

    question_ids = [q['id'] for q in static_sample]

    # AI question goes first; clean up answer key for serialisation
    ai_q_stored = None
    if ai_q:
        ai_q_stored = {
            'id': ai_q['id'],
            'question': ai_q['question'],
            'options': list(ai_q['options']),
            'answer': int(ai_q['answer']),
            'is_ai': True,
        }
        question_ids = [ai_q['id']] + question_ids

    session['quiz_attempt'] = {
        'question_ids': question_ids,
        'ai_q': ai_q_stored,
        'answers': {},
        'current_index': 0,
        'total_questions': len(question_ids),
        'attempt_id': str(uuid.uuid4()),
        'finalized': False,
    }
    session.modified = True
    return session['quiz_attempt']


def _get_question(attempt, idx):
    """Return the full question dict for the step at idx."""
    q_id = attempt['question_ids'][idx]
    ai_q = attempt.get('ai_q')
    if ai_q and ai_q['id'] == q_id:
        return ai_q
    q = _static_by_id.get(q_id)
    if q is None:
        return None
    return {**q, 'is_ai': False}


def _compute_score(attempt):
    """Calculate score over all answered questions in this attempt."""
    answers = attempt.get('answers', {})
    score = 0
    for idx, q_id in enumerate(attempt['question_ids']):
        q = _get_question(attempt, idx)
        if q is None:
            continue
        sel = answers.get(str(q_id))
        if sel is not None and int(sel) == q['answer']:
            score += 1
    return score


def _quiz_title_for_score(score, max_score):
    """Return gamification title based on previous best score."""
    if max_score <= 0:
        return 'Học viên an ninh mạng'
    pct = score / max_score * 100
    if pct >= 90:
        return 'Bậc thầy MindGuard'
    if pct >= 70:
        return 'Chuyên gia phòng chống lừa đảo'
    if pct >= 50:
        return 'Người dùng cảnh giác'
    return 'Học viên an ninh mạng'


# ------------------------------------------------------------------ #
# Entry point
# ------------------------------------------------------------------ #

@quiz_bp.route('/quiz')
@login_required
def quiz():
    """Start or resume a quiz attempt; redirect to current step."""
    force_retake = request.args.get('force')

    # If user already passed, redirect to result unless forcing a retake
    if not force_retake:
        email = session.get('registration_email')
        if email:
            passed = (
                QuizResult.query
                .filter_by(email=email)
                .filter(QuizResult.certificate_code.isnot(None))
                .order_by(QuizResult.created_at.desc())
                .first()
            )
            if passed:
                session['last_quiz_score'] = passed.score
                session['max_quiz_score'] = passed.max_score
                session['certificate_code'] = passed.certificate_code
                flash(
                    f'Bạn đã có chứng chỉ với kết quả {passed.score}/{passed.max_score} điểm.'
                    ' Bạn có muốn làm lại không?',
                    'info',
                )
                return redirect(url_for('quiz.quiz_result'))

    # Resume an in-progress attempt (unless force retake)
    existing = session.get('quiz_attempt')
    if existing and not existing.get('finalized') and not force_retake:
        return redirect(url_for('quiz.quiz_step', idx=existing.get('current_index', 0)))

    # Start fresh
    _create_attempt()
    return redirect(url_for('quiz.quiz_step', idx=0))


# ------------------------------------------------------------------ #
# Step view + submit (GET + POST, PRG pattern)
# ------------------------------------------------------------------ #

@quiz_bp.route('/quiz/step/<int:idx>', methods=['GET', 'POST'])
@login_required
def quiz_step(idx):
    """Render a single question (GET) or save answer and redirect (POST)."""
    attempt = session.get('quiz_attempt')
    if not attempt or not attempt.get('question_ids'):
        flash('Phiên làm bài không hợp lệ. Vui lòng bắt đầu lại.', 'warning')
        return redirect(url_for('quiz.quiz'))

    total = attempt['total_questions']

    # Clamp idx to valid range
    if idx < 0 or idx >= total:
        return redirect(url_for('quiz.quiz_step', idx=attempt.get('current_index', 0)))

    # --- POST: save answer, redirect to next step (POST-Redirect-GET) ---
    if request.method == 'POST':
        q = _get_question(attempt, idx)
        if q:
            raw = request.form.get(f"q{q['id']}")
            if raw is not None:
                try:
                    attempt['answers'][str(q['id'])] = int(raw)
                except (ValueError, TypeError):
                    pass

        next_idx = idx + 1
        attempt['current_index'] = next_idx if next_idx < total else idx
        session['quiz_attempt'] = attempt
        session.modified = True

        if next_idx >= total:
            return redirect(url_for('quiz.quiz_finalize'))
        return redirect(url_for('quiz.quiz_step', idx=next_idx))

    # --- GET: render single question ---
    # Move current_index forward only (back-navigation keeps the higher pointer)
    if idx > attempt.get('current_index', 0):
        attempt['current_index'] = idx
        session['quiz_attempt'] = attempt
        session.modified = True

    current_question = _get_question(attempt, idx)
    if current_question is None:
        flash('Câu hỏi không tồn tại. Vui lòng bắt đầu lại.', 'warning')
        return redirect(url_for('quiz.quiz'))

    answers = attempt.get('answers', {})
    selected_answer = answers.get(str(current_question['id']))
    answered_count = len(answers)

    quiz_title = _quiz_title_for_score(
        session.get('last_quiz_score', 0),
        session.get('max_quiz_score', 15),
    )

    return render_template(
        'quiz.html',
        current_question=current_question,
        current_index=idx,
        total_questions=total,
        answered_count=answered_count,
        selected_answer=selected_answer,
        quiz_title=quiz_title,
    )


# ------------------------------------------------------------------ #
# Finalize — compute score, write DB (once), redirect
# ------------------------------------------------------------------ #

@quiz_bp.route('/quiz/finalize')
@login_required
def quiz_finalize():
    """Compute final score and persist ONE QuizResult; idempotent on refresh."""
    attempt = session.get('quiz_attempt')
    if not attempt:
        return redirect(url_for('quiz.quiz'))

    # Guard: already finalised — do not write again
    if attempt.get('finalized'):
        return redirect(url_for('quiz.quiz_result'))

    max_score = attempt.get('total_questions', len(attempt.get('question_ids', [])))
    score = _compute_score(attempt)

    name = session.get('registration_name', 'Khách MindGuard')
    email = session.get('registration_email')

    result = QuizResult(name=name, email=email, score=score, max_score=max_score)
    db.session.add(result)
    db.session.commit()

    session['last_quiz_score'] = score
    session['max_quiz_score'] = max_score
    session['last_quiz_result_id'] = result.id

    # Mark attempt finalised to prevent duplicate writes on refresh
    attempt['finalized'] = True
    session['quiz_attempt'] = attempt
    session.modified = True

    if max_score > 0 and score >= int(max_score * Config.QUIZ_PASS_PERCENTAGE):
        code = generate_certificate_code()
        session['certificate_code'] = code
        result.certificate_code = code
        db.session.commit()

        title = _quiz_title_for_score(score, max_score)
        session['quiz_rank_title'] = title

        flash(
            f"🎉 Tuyệt vời! Bạn đạt danh hiệu '{title}' ({score}/{max_score} điểm).",
            'success',
        )
        return redirect(url_for('quiz.certificate'))

    flash(
        f'📊 Kết quả: {score}/{max_score}. Bạn chưa đạt mức an toàn.'
        ' Hãy thử lại để lấy chứng chỉ nhé!',
        'warning',
    )
    return redirect(url_for('quiz.quiz_result'))


# ------------------------------------------------------------------ #
# Result and certificate (unchanged downstream contracts)
# ------------------------------------------------------------------ #

@quiz_bp.route('/quiz/result')
@login_required
def quiz_result():
    """Quiz result page."""
    score = session.get('last_quiz_score', 0)
    max_score = session.get('max_quiz_score', 15)
    return render_template(
        'quiz_result.html',
        score=score,
        max_score=max_score,
        scam_types_avoided=score,
        scam_types_vulnerable=max_score - score,
    )


@quiz_bp.route('/certificate')
@login_required
def certificate():
    """Certificate page for successful quiz completion."""
    score = session.get('last_quiz_score')
    max_score = session.get('max_quiz_score')
    code = session.get('certificate_code')
    name = session.get('registration_name', 'Người học MindGuard')
    issue_date = datetime.now().strftime('%d/%m/%Y')

    if not code:
        flash('Bạn cần hoàn thành bài test với số điểm đạt yêu cầu để nhận chứng nhận.', 'info')
        return redirect(url_for('quiz.quiz'))

    return render_template(
        'certificate.html',
        score=score,
        max_score=max_score,
        code=code,
        name=name,
        issue_date=issue_date,
        scam_types_avoided=score,
    )
