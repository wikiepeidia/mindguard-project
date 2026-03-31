from flask import Blueprint, render_template, request, session, jsonify, url_for, redirect
from models import Registration, AiChatSession, AiChatMessage
from extensions import db
from utils.chatbot import generate_chatbot_reply, generate_support_reply
from utils.helpers import login_required
from datetime import datetime

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')


def _get_current_user():
    return Registration.query.filter_by(email=session.get("registration_email")).first()


def _serialize_chat_session(chat_session):
    return {
        "id": chat_session.id,
        "title": chat_session.title or "Cuộc trò chuyện",
        "updated_at": chat_session.updated_at.strftime('%d/%m/%Y') if chat_session.updated_at else "Không rõ thời gian",
        "url": url_for('chatbot.chatbot_page', session_id=chat_session.id),
    }


def _persist_chat_exchange(user, user_message, session_id=None):
    chat_session = None
    if session_id:
        chat_session = AiChatSession.query.filter_by(id=session_id, user_id=user.id).first()

    is_new_session = chat_session is None

    if not chat_session:
        chat_session = AiChatSession(user_id=user.id, title=user_message[:30])
        db.session.add(chat_session)
        db.session.flush()

    db.session.add(AiChatMessage(session_id=chat_session.id, sender='user', content=user_message))

    ai_reply, reply_meta = generate_chatbot_reply(user_message)

    db.session.add(AiChatMessage(session_id=chat_session.id, sender='bot', content=ai_reply))

    chat_session.updated_at = datetime.utcnow()
    db.session.commit()

    return chat_session, ai_reply, reply_meta, is_new_session

# 1. Trang Chat Full (Load lịch sử từ DB)
@chatbot_bp.route("/", methods=["GET", "POST"])
@login_required
def chatbot_page():
    user = _get_current_user()
    if not user:
        return redirect(url_for('auth.login'))

    if request.method == "POST":
        user_message = request.form.get("message", "").strip()
        session_id = request.form.get("session_id")
        if user_message:
            chat_session, _ai_reply, _reply_meta, _is_new_session = _persist_chat_exchange(user, user_message, session_id=session_id)
            return redirect(url_for('chatbot.chatbot_page', session_id=chat_session.id))

    # Lấy danh sách session cũ
    sessions = AiChatSession.query.filter_by(user_id=user.id).order_by(AiChatSession.updated_at.desc()).all()
    
    current_session_id = request.args.get('session_id', type=int)
    active_session = None
    messages = []
    
    if current_session_id:
        active_session = AiChatSession.query.filter_by(id=current_session_id, user_id=user.id).first()
        if active_session:
            messages = active_session.messages
            
    return render_template("chatbot.html", sessions=sessions, active_session=active_session, messages=messages, current_session_id=current_session_id, history=[])

@chatbot_bp.route("/new", methods=["GET"])
@login_required
def new_chat():
    return redirect(url_for('chatbot.chatbot_page'))

# 2. API Chat chính (Lưu DB - Dùng cho trang Chatbot Full)
@chatbot_bp.route("/send", methods=["GET", "POST"])
@login_required
def send_message():
    # GET requests redirect to the chatbot page (prevents 405 on direct navigation
    # or post-login redirect chains)
    if request.method == "GET":
        return redirect(url_for('chatbot.chatbot_page'))

    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    session_id = data.get("session_id")

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    user = _get_current_user()
    if not user:
        return jsonify({"error": "Phiên đăng nhập không hợp lệ.", "code": "UNAUTHENTICATED"}), 401

    chat_session, ai_reply, reply_meta, is_new_session = _persist_chat_exchange(user, user_message, session_id=session_id)

    return jsonify({
        "reply": ai_reply,
        "session_id": chat_session.id,
        "reply_source": reply_meta.get("source"),
        "reply_model": reply_meta.get("model"),
        "is_new_session": is_new_session,
        "session": _serialize_chat_session(chat_session),
    })

# 3. API cho Widget (Nhanh, không cần lưu session)
# QUAN TRỌNG: Tên hàm phải là 'chatbot_api' để khớp với url_for('chatbot.chatbot_api') trong HTML
@chatbot_bp.route("/api", methods=["GET", "POST"])
def chatbot_api():
    # GET requests return usage instructions (prevents 405 on direct navigation)
    if request.method == "GET":
        return jsonify({
            "error": "Gửi tin nhắn bằng phương thức POST với JSON body: {\"message\": \"...\"}",
            "code": "METHOD_HINT",
        }), 200

    data = request.get_json() or {}
    message = data.get("message", "")
    
    # Gọi AI trả lời ngay
    reply, reply_meta = generate_chatbot_reply(message)
    
    return jsonify({
        "reply": reply,
        "reply_source": reply_meta.get("source"),
        "reply_model": reply_meta.get("model"),
    })

# 4. API Đổi tên session
@chatbot_bp.route("/rename", methods=["POST"])
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
def support_chat():
    data = request.get_json()
    msg = data.get("message", "")
    reply, reply_meta = generate_support_reply(msg)
    return jsonify({
        "reply": reply,
        "reply_source": reply_meta.get("source"),
        "reply_model": reply_meta.get("model"),
    })
