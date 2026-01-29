from flask import Blueprint, render_template, request, session, jsonify, url_for, redirect
from models import Registration, AiChatSession, AiChatMessage
from extensions import db
from utils.chatbot import query_ai_model, simple_bot_reply, generate_support_reply
from utils.helpers import login_required
from datetime import datetime

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

# 1. Trang Chat Full (Load lịch sử từ DB)
@chatbot_bp.route("/", methods=["GET"])
@login_required
def chatbot_page():
    user = Registration.query.filter_by(email=session.get("registration_email")).first()
    if not user:
        return redirect(url_for('auth.login'))
        
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
@login_required
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
def chatbot_api():
    data = request.get_json() or {}
    message = data.get("message", "")
    
    # Gọi AI trả lời ngay
    reply = query_ai_model(message) or simple_bot_reply(message)
    
    return jsonify({"reply": reply})

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
    reply = generate_support_reply(msg)
    return jsonify({"reply": reply})
