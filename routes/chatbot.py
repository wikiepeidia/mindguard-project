"""Routes for chatbot functionality."""
from flask import Blueprint, render_template, request, session, jsonify
from models import db, ChatSupportMessage
from utils.chatbot import simple_bot_reply, generate_support_reply
from utils.helpers import generate_session_id

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')


@chatbot_bp.route("/", methods=["GET", "POST"])
def chatbot_page():
    """Full page chatbot for scam analysis."""
    history = session.get("chat_history", [])
    
    if request.method == "POST":
        user_message = request.form.get("message", "")
        if user_message.strip():
            bot_reply = simple_bot_reply(user_message)
            history.append({"sender": "Bạn", "text": user_message})
            history.append({"sender": "MindGuard Bot", "text": bot_reply})
            session["chat_history"] = history
    
    return render_template("chatbot.html", history=history)


@chatbot_bp.route("/api", methods=["POST"])
def chatbot_api():
    """API for chatbot widget."""
    data = request.get_json() or {}
    message = data.get("message", "")
    reply = simple_bot_reply(message)
    return jsonify({"reply": reply})


@chatbot_bp.route("/support", methods=["POST"])
def support_chat():
    """Support chatbot for reporting guidance."""
    data = request.get_json() or {}
    message = data.get("message", "")
    
    # Get or create session ID
    if not session.get('support_chat_session'):
        session['support_chat_session'] = generate_session_id()
    
    session_id = session['support_chat_session']
    
    # Generate reply
    reply = generate_support_reply(message)
    
    # Save to database
    chat_message = ChatSupportMessage(
        session_id=session_id,
        user_message=message,
        bot_reply=reply
    )
    db.session.add(chat_message)
    db.session.commit()
    
    return jsonify({"reply": reply, "session_id": session_id})


@chatbot_bp.route("/clear", methods=["POST"])
def clear_history():
    """Clear chat history."""
    session.pop("chat_history", None)
    return jsonify({"status": "success"})
