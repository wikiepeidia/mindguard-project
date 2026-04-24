from flask import Blueprint, render_template, request, session, jsonify, url_for, redirect
from models import Registration, AiChatSession, AiChatMessage, ChatFeedback
from extensions import db, limiter, csrf
from utils.chatbot import query_ai_model, simple_bot_reply, generate_support_reply
from utils.helpers import login_required
from datetime import datetime

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

# 1. Trang Chat Full (Load lịch sử từ DB)
@chatbot_bp.route("/", methods=["GET", "POST"])
@csrf.exempt
@login_required
def chatbot_page():
    user = Registration.query.filter_by(email=session.get("registration_email")).first()
    if not user:
        return redirect(url_for('auth.login'))

    if request.method == "POST":
        message = request.form.get("message", "").strip()
        session_id = request.form.get("session_id")
        if message:
            chat_session = None
            if session_id:
                chat_session = AiChatSession.query.filter_by(id=session_id, user_id=user.id).first()
            if not chat_session:
                chat_session = AiChatSession(user_id=user.id, title=message[:30])
                db.session.add(chat_session)
                db.session.commit()
            db.session.add(AiChatMessage(session_id=chat_session.id, sender='user', content=message))
            ai_reply = query_ai_model(message) or simple_bot_reply(message)
            db.session.add(AiChatMessage(session_id=chat_session.id, sender='bot', content=ai_reply))
            chat_session.updated_at = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('chatbot.chatbot_page', session_id=chat_session.id))
        return redirect(url_for('chatbot.chatbot_page'))

    # Lấy danh sách session cũ
    sessions = AiChatSession.query.filter_by(user_id=user.id).order_by(AiChatSession.updated_at.desc()).all()

    current_session_id = request.args.get('session_id')
    active_session = None
    messages = []

    if current_session_id:
        active_session = AiChatSession.query.filter_by(id=current_session_id, user_id=user.id).first()
        if active_session:
            messages = active_session.messages

    return render_template("chatbot.html", sessions=sessions, active_session=active_session, messages=messages, current_session_id=current_session_id)

@chatbot_bp.route("/new", methods=["GET"])
@login_required
def new_chat():
    return redirect(url_for('chatbot.chatbot_page'))

# 2. API Chat chính (Lưu DB - Dùng cho trang Chatbot Full)
@chatbot_bp.route("/send", methods=["POST"])
@csrf.exempt
@login_required
@limiter.limit("20/minute;3/second")
def send_message():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    session_id = data.get("session_id")
    
    if not user_message: return jsonify({"error": "Empty message"}), 400

    user = Registration.query.filter_by(email=session.get("registration_email")).first()
    
    chat_session = None
    if session_id:
        chat_session = AiChatSession.query.filter_by(id=session_id, user_id=user.id).first()
    
    if not chat_session:
        # Tạo session mới
        chat_session = AiChatSession(user_id=user.id, title=user_message[:30])
        db.session.add(chat_session)
        db.session.commit()

    # Lưu tin nhắn User
    db.session.add(AiChatMessage(session_id=chat_session.id, sender='user', content=user_message))
    
    # Gọi AI
    ai_reply = query_ai_model(user_message) or simple_bot_reply(user_message)
    
    # Lưu tin nhắn Bot
    db.session.add(AiChatMessage(session_id=chat_session.id, sender='bot', content=ai_reply))
    
    chat_session.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"reply": ai_reply, "session_id": chat_session.id})

# 3. API cho Widget (Nhanh, không cần lưu session)
# QUAN TRỌNG: Tên hàm phải là 'chatbot_api' để khớp với url_for('chatbot.chatbot_api') trong HTML
@chatbot_bp.route("/api", methods=["POST"])
@csrf.exempt
@limiter.limit("10/minute;2/second")
def chatbot_api():
    data = request.get_json() or {}
    message = data.get("message", "")

    if not message or not message.strip():
        return jsonify({"reply": "Bác/anh/chị vui lòng nhập nội dung câu hỏi."}), 400

    # Gọi AI trả lời ngay
    reply = query_ai_model(message) or simple_bot_reply(message)

    return jsonify({"reply": reply})

# 4. API Đổi tên session
@chatbot_bp.route("/rename", methods=["POST"])
@csrf.exempt
@login_required
def rename_session():
    data = request.get_json()
    session_id = data.get("session_id")
    title = data.get("title")
    
    user = Registration.query.filter_by(email=session.get("registration_email")).first()
    chat_session = AiChatSession.query.filter_by(id=session_id, user_id=user.id).first()
    
    if chat_session:
        chat_session.title = title
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

# 5. API Support Modal (Trang Report)
@chatbot_bp.route("/support", methods=["POST"])
@csrf.exempt
@limiter.limit("10/minute")
def support_chat():
    data = request.get_json()
    msg = data.get("message", "")
    reply = generate_support_reply(msg)
    return jsonify({"reply": reply})


# 6. API Góp ý / Báo cáo sai (TRUST-03)
@chatbot_bp.route("/feedback", methods=["POST"])
@csrf.exempt
@login_required
@limiter.limit("10/minute")
def submit_feedback():
    data = request.get_json() or {}
    feedback_type = data.get("feedback_type", "").strip()
    feedback_text = data.get("feedback_text", "").strip()
    message_id = data.get("message_id")
    session_id = data.get("session_id")

    valid_types = ("incorrect", "offensive", "unclear", "other")
    if feedback_type not in valid_types:
        return jsonify({"error": "Loại góp ý không hợp lệ"}), 400

    if not feedback_text:
        return jsonify({"error": "Vui lòng nhập nội dung góp ý"}), 400

    user = Registration.query.filter_by(email=session.get("registration_email")).first()

    fb = ChatFeedback(
        user_id=user.id if user else None,
        session_id=session_id,
        message_id=message_id,
        feedback_type=feedback_type,
        feedback_text=feedback_text,
    )
    db.session.add(fb)
    db.session.commit()

    return jsonify({"success": True, "message": "Cảm ơn bạn đã góp ý! Chúng tôi sẽ xem xét và cải thiện."})
