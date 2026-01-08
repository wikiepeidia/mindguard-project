
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps
import random
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "change_this_in_production"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mindguard.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Đăng nhập admin demo
ADMIN_USERNAME = os.environ.get("MINDGUARD_ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get("MINDGUARD_ADMIN_PASS", "mindguard2025")

db = SQLAlchemy(app)


class ScamReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    channel = db.Column(db.String(100))
    description = db.Column(db.Text, nullable=False)
    protection_tip = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    age_group = db.Column(db.String(50))
    occupation = db.Column(db.String(100))
    city = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150))
    score = db.Column(db.Integer, nullable=False)
    max_score = db.Column(db.Integer, nullable=False)
    certificate_code = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()


def generate_certificate_code() -> str:
    return "MG-" + str(random.randint(100000, 999999))


def simple_bot_reply(message: str) -> str:
    msg = (message or "").lower()

    # Một số luật đơn giản giả lập AI/ML
    risk_score = 0
    reasons = []

    risky_keywords = [
        ("otp", 30, "yêu cầu cung cấp mã OTP"),
        ("mã xác thực", 25, "đòi mã xác thực"),
        ("chuyển khoản", 20, "ép chuyển khoản"),
        ("lãi suất", 15, "hứa lãi cao bất thường"),
        ("đầu tư", 15, "mời gọi đầu tư"),
        ("trúng thưởng", 20, "thông báo trúng thưởng"),
        ("link", 10, "gửi đường link lạ"),
        ("đăng nhập", 10, "yêu cầu đăng nhập vào link lạ"),
        ("khóa tài khoản", 20, "dọa khóa tài khoản"),
        ("nạp tiền", 15, "bắt nạp tiền trước"),
    ]

    for kw, score, reason in risky_keywords:
        if kw in msg:
            risk_score += score
            reasons.append(reason)

    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        level = "Nguy cơ CAO"
        advice = (
            "Tình huống có mức độ rủi ro rất cao. Tuyệt đối không cung cấp OTP/mật khẩu, "
            "không bấm vào link lạ và không chuyển bất kỳ khoản tiền nào. Hãy chủ động liên hệ "
            "kênh chính thức (ngân hàng, công ty, cơ quan nhà nước) để kiểm tra."
        )
    elif risk_score >= 40:
        level = "Nguy cơ TRUNG BÌNH"
        advice = (
            "Tình huống có nhiều dấu hiệu cần cảnh giác. Bạn nên dừng lại, chụp màn hình làm bằng chứng, "
            "tự tìm số tổng đài/website chính thức để gọi hỏi lại, và không chia sẻ thông tin nhạy cảm."
        )
    else:
        level = "Nguy cơ THẤP (tạm thời)"
        advice = (
            "Hiện chưa thấy nhiều từ khóa rủi ro, nhưng vẫn cần thận trọng. Đừng vội tin vào lời hứa lợi nhuận, "
            "hãy xác minh từ nhiều nguồn đáng tin cậy và tham khảo ý kiến người thân, chuyên gia."
        )

    # Nếu người dùng chỉ hỏi chung chung, trả lời chung
    if not message.strip():
        return (
            "Bạn hãy mô tả tình huống (ai liên hệ, kênh nào, họ yêu cầu gì). "
            "Nhớ che số tài khoản, CCCD, OTP… MindGuard sẽ giúp bạn phân tích mức độ rủi ro."
        )

    base_note = (
        "Kết quả phân tích chỉ mang tính tham khảo, không thay thế tư vấn pháp lý hoặc hỗ trợ khẩn cấp.\n\n"
    )

    if reasons:
        reason_text = " • ".join(reasons)
        detail = f"Đánh giá: {level} (khoảng {risk_score}%).\nDấu hiệu nhận diện: {reason_text}.\n\n{advice}"
    else:
        detail = (
            f"Đánh giá: {level}.\n"
            f"{advice}"
        )

    return base_note + detail


# Bộ câu hỏi MindGuard (15 câu)
quiz_questions = [
    {
        "id": 1,
        "question": "Một người tự xưng là nhân viên ngân hàng yêu cầu bạn cung cấp mã OTP để 'xác minh tài khoản'. Bạn nên làm gì?",
        "options": [
            "Cung cấp ngay mã OTP để tránh bị khóa tài khoản",
            "Từ chối và gọi lại số tổng đài chính thức của ngân hàng để kiểm tra",
            "Chụp màn hình rồi gửi cho bạn bè hỏi thử",
            "Nhắn lại hỏi thêm thông tin cá nhân của họ",
        ],
        "answer": 1,
    },
    {
        "id": 2,
        "question": "Bạn nhận được tin nhắn trúng thưởng với đường link lạ yêu cầu đăng nhập tài khoản mạng xã hội để nhận quà. Đây có thể là:",
        "options": [
            "Chương trình khuyến mãi hợp lệ",
            "Chiến dịch quảng cáo của nhà mạng",
            "Hình thức lừa đảo đánh cắp tài khoản (phishing)",
            "Cơ hội hiếm có, nên thử",
        ],
        "answer": 2,
    },
    {
        "id": 3,
        "question": "Dấu hiệu nào dưới đây thường gặp ở các tin nhắn lừa đảo?",
        "options": [
            "Ngôn ngữ rõ ràng, không sai chính tả, có địa chỉ liên hệ chính thức",
            "Thúc giục thao tác gấp, dọa khóa tài khoản, đường link lạ, sai chính tả",
            "Chỉ gửi vào giờ hành chính",
            "Luôn có chữ ký điện tử và con dấu đỏ",
        ],
        "answer": 1,
    },
    {
        "id": 4,
        "question": "Khi phát hiện người thân có dấu hiệu bị thao túng tâm lý bởi 'chuyên gia đầu tư' lạ trên mạng, bạn nên làm gì trước tiên?",
        "options": [
            "Mắng mỏ ngay vì cả tin",
            "Lén đăng nhập tài khoản của họ",
            "Trao đổi bình tĩnh, thu thập thêm thông tin và khuyên họ tạm dừng chuyển tiền",
            "Im lặng vì đó là chuyện riêng",
        ],
        "answer": 2,
    },
    {
        "id": 5,
        "question": "Một tài khoản Facebook lạ nhắn tin xưng là bạn bè của bạn, dùng hình ảnh đã có trên mạng. Họ nhờ bạn chuyển tiền gấp. Bạn nên:",
        "options": [
            "Chuyển ngay để 'cứu' bạn",
            "Hỏi số tài khoản rồi chuyển sau",
            "Gọi trực tiếp cho người bạn thật qua số điện thoại đã lưu để kiểm tra",
            "Nhắn lại xin thêm hình ảnh",
        ],
        "answer": 2,
    },
    {
        "id": 6,
        "question": "Trang web ngân hàng giả mạo thường có đặc điểm:",
        "options": [
            "Tên miền chính xác, có chứng chỉ bảo mật và được truy cập từ app chính thức",
            "Tên miền gần giống, khác 1–2 ký tự, giao diện giống nhưng đường link lạ",
            "Không cần nhập tài khoản, chỉ hiển thị thông tin chung",
            "Luôn xuất hiện logo của Bộ Công an",
        ],
        "answer": 1,
    },
    {
        "id": 7,
        "question": "Khi tham gia các nhóm 'đầu tư siêu lợi nhuận' trên mạng xã hội, nguyên tắc quan trọng nhất là:",
        "options": [
            "Chỉ đầu tư khi thấy nhiều người khoe lãi",
            "Tin vào các 'chuyên gia' livestream vì họ nói rất tự tin",
            "Không chuyển tiền cho cá nhân, chỉ giao dịch qua kênh đã được cơ quan quản lý cấp phép",
            "Rút tiền lãi liên tục để an toàn",
        ],
        "answer": 2,
    },
    {
        "id": 8,
        "question": "Một kẻ lừa đảo thường sử dụng cảm xúc nào để thao túng nạn nhân?",
        "options": [
            "Gây áp lực thời gian, đánh vào nỗi sợ và lòng tham",
            "Khuyến khích suy nghĩ chậm rãi, phân tích đa chiều",
            "Luôn cho bạn thời gian một tuần để suy nghĩ",
            "Chỉ dùng các lập luận logic, không gây áp lực",
        ],
        "answer": 0,
    },
    {
        "id": 9,
        "question": "Chiến lược nào giúp bạn giảm nguy cơ bị thao túng tâm lý trên mạng?",
        "options": [
            "Chỉ đọc một nguồn thông tin, không nghe ý kiến khác",
            "Hạn chế chia sẻ thông tin cá nhân, kiểm tra chéo thông tin từ nhiều nguồn đáng tin cậy",
            "Tin mọi thứ nếu được chia sẻ nhiều lần",
            "Luôn làm theo lời người có nhiều follower nhất",
        ],
        "answer": 1,
    },
    {
        "id": 10,
        "question": "Khi nhận cuộc gọi tự xưng là 'công an/viện kiểm sát' đe dọa liên quan tới án hình sự và yêu cầu chuyển tiền để 'kiểm tra', bạn nên:",
        "options": [
            "Làm theo ngay vì rất nghiêm trọng",
            "Giữ bình tĩnh, cúp máy và gọi tới số tổng đài chính thức của cơ quan đó hoặc 113 để xác minh",
            "Ghi âm rồi chuyển tiền để tránh rắc rối",
            "Chia sẻ lên Facebook để hỏi ý kiến rồi chuyển tiền sau",
        ],
        "answer": 1,
    },
    {
        "id": 11,
        "question": "Mật khẩu an toàn nên có đặc điểm:",
        "options": [
            "Ngắn, dễ nhớ như ngày sinh",
            "Giống nhau cho tất cả các tài khoản để khỏi quên",
            "Dài, có chữ hoa, chữ thường, số và ký tự đặc biệt, khác nhau giữa các tài khoản quan trọng",
            "Chỉ toàn số cho dễ nhập",
        ],
        "answer": 2,
    },
    {
        "id": 12,
        "question": "Khi con/em bạn bị dụ dỗ tham gia 'việc nhẹ lương cao' như like, share, nạp thẻ cào để nhận tiền, bạn nên:",
        "options": [
            "Động viên tham gia để kiếm thêm thu nhập",
            "Phớt lờ vì đó là việc riêng",
            "Ngồi cùng phân tích rủi ro, giải thích dấu hiệu lừa đảo và hướng dẫn cách từ chối",
            "Lấy điện thoại, tự mình làm giúp cho an toàn",
        ],
        "answer": 2,
    },
    {
        "id": 13,
        "question": "Hành vi nào dưới đây giúp bạn tự bảo vệ tốt hơn trước thao túng và tin giả?",
        "options": [
            "Chỉ đọc tiêu đề, không cần nội dung chi tiết",
            "Kiểm tra nguồn tin, tác giả, thời điểm đăng tải và mục đích thông điệp",
            "Tin những gì khiến mình cảm xúc mạnh nhất",
            "Tin mọi thông tin được bạn bè share lại",
        ],
        "answer": 1,
    },
    {
        "id": 14,
        "question": "Khi tham gia các nhóm chat cộng đồng, nguyên tắc an toàn quan trọng là:",
        "options": [
            "Gửi ảnh CCCD cho admin để được 'xác minh'",
            "Chia sẻ mọi thông tin cá nhân để làm quen",
            "Không gửi hình ảnh giấy tờ tùy thân, thông tin tài khoản, mã OTP lên nhóm",
            "Nhấn vào tất cả các file đính kèm để cập nhật thông tin",
        ],
        "answer": 2,
    },
    {
        "id": 15,
        "question": "Bạn nên làm gì nếu đã lỡ cung cấp thông tin nhạy cảm (mật khẩu, OTP, số thẻ) cho kẻ lừa đảo?",
        "options": [
            "Im lặng vì xấu hổ",
            "Đợi xem có chuyện gì xảy ra rồi mới xử lý",
            "Lập tức liên hệ ngân hàng/đơn vị cung cấp dịch vụ để khóa tài khoản, đổi mật khẩu và trình báo cơ quan chức năng",
            "Chỉ kể lại với bạn bè cho đỡ buồn",
        ],
        "answer": 2,
    },
]


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Bạn cần đăng nhập với vai trò Admin.", "warning")
            return redirect(url_for("admin_login", next=request.path))
        return view_func(*args, **kwargs)

    return wrapped


@app.context_processor
def inject_globals():
    return {"current_year": datetime.now().year}


@app.route("/")
def index():
    scam_count = ScamReport.query.count()
    registration_count = Registration.query.count()
    stats = {"scam_count": scam_count, "registration_count": registration_count}
    return render_template("index.html", stats=stats)


@app.route("/report", methods=["GET", "POST"])
def report_scam():
    if request.method == "POST":
        title = request.form.get("title")
        category = request.form.get("category")
        channel = request.form.get("channel")
        description = request.form.get("description")
        protection_tip = request.form.get("protection_tip")
        consent = request.form.get("consent") == "on"

        if not title or not description or not consent:
            flash(
                "Vui lòng điền đầy đủ thông tin bắt buộc và xác nhận chia sẻ kịch bản.",
                "danger",
            )
            return redirect(url_for("report_scam"))

        report = ScamReport(
            title=title,
            category=category,
            channel=channel,
            description=description,
            protection_tip=protection_tip,
        )
        db.session.add(report)
        db.session.commit()

        flash(
            "Cảm ơn bạn! Kịch bản lừa đảo của bạn đã được gửi cho MindGuard.",
            "success",
        )
        return redirect(url_for("report_scam"))

    recent_scams = (
        ScamReport.query.order_by(ScamReport.created_at.desc()).limit(5).all()
    )
    return render_template("report_scam.html", scams=recent_scams)


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
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

        # Tạm chưa có cert, sẽ cập nhật sau nếu đủ điểm
        result = QuizResult(
            name=name,
            email=email,
            score=score,
            max_score=max_score,
        )
        db.session.add(result)
        db.session.commit()
        session["last_quiz_result_id"] = result.id

        if score >= int(max_score * 0.75):
            code = generate_certificate_code()
            session["certificate_code"] = code
            result.certificate_code = code
            db.session.commit()
            flash(
                f"Chúc mừng! Bạn đạt {score}/{max_score} điểm. Bạn đủ điều kiện nhận chứng nhận MindGuard.",
                "success",
            )
            return redirect(url_for("certificate"))
        else:
            flash(
                f"Bạn đạt {score}/{max_score} điểm. Hãy xem lại phần nguyên tắc an toàn và thử lại để đạt chứng nhận nhé!",
                "warning",
            )
            return redirect(url_for("quiz_result"))

    return render_template("quiz.html", questions=quiz_questions)


@app.route("/quiz/result")
def quiz_result():
    score = session.get("last_quiz_score")
    max_score = session.get("max_quiz_score")
    return render_template("quiz_result.html", score=score, max_score=max_score)


@app.route("/certificate")
def certificate():
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
        return redirect(url_for("quiz"))

    return render_template(
        "certificate.html",
        score=score,
        max_score=max_score,
        code=code,
        name=name,
        issue_date=issue_date,
    )


@app.route("/chatbot", methods=["GET", "POST"])
def chatbot_page():
    """Trang chatbot full page (tuỳ chọn)."""
    history = session.get("chat_history", [])
    if request.method == "POST":
        user_message = request.form.get("message", "")
        if user_message.strip():
            bot_reply = simple_bot_reply(user_message)
            history.append({"sender": "Bạn", "text": user_message})
            history.append({"sender": "MindGuard Bot", "text": bot_reply})
            session["chat_history"] = history
    return render_template("chatbot.html", history=history)


@app.route("/api/chatbot", methods=["POST"])
def chatbot_api():
    """API cho widget chatbot ở góc màn hình."""
    data = request.get_json() or {}
    message = data.get("message", "")
    reply = simple_bot_reply(message)
    return jsonify({"reply": reply})


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        age_group = request.form.get("age_group")
        occupation = request.form.get("occupation")
        city = request.form.get("city")

        if not name or not email:
            flash("Vui lòng nhập đầy đủ Họ tên và Gmail.", "danger")
            return redirect(url_for("register"))

        if not email.lower().endswith("@gmail.com"):
            flash("Vui lòng sử dụng địa chỉ Gmail cá nhân (đuôi @gmail.com).", "warning")
            return redirect(url_for("register"))

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

        flash("Đăng ký thành công! Bạn có thể làm bài test MindGuard ngay bây giờ.", "success")
        return redirect(url_for("quiz"))

    return render_template("register.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["is_admin"] = True
            flash("Đăng nhập Admin thành công.", "success")
            next_url = request.args.get("next") or url_for("admin_dashboard")
            return redirect(next_url)
        else:
            flash("Tài khoản hoặc mật khẩu không đúng.", "danger")
            return redirect(url_for("admin_login"))
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    flash("Bạn đã đăng xuất Admin.", "info")
    return redirect(url_for("index"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    scam_count = ScamReport.query.count()
    registration_count = Registration.query.count()
    quiz_count = QuizResult.query.count()
    latest_scams = ScamReport.query.order_by(ScamReport.created_at.desc()).limit(10).all()
    latest_regs = Registration.query.order_by(Registration.created_at.desc()).limit(10).all()
    latest_results = QuizResult.query.order_by(QuizResult.created_at.desc()).limit(10).all()
    return render_template(
        "admin_dashboard.html",
        scam_count=scam_count,
        registration_count=registration_count,
        quiz_count=quiz_count,
        latest_scams=latest_scams,
        latest_regs=latest_regs,
        latest_results=latest_results,
    )


@app.route("/api/analyze_scam", methods=["POST"])
def api_analyze_scam():
    """API AI/ML giả lập để phân tích kịch bản lừa đảo."""
    data = request.get_json() or {}
    text = data.get("text", "")
    reply = simple_bot_reply(text)
    # Tách sơ bộ ra risk_score nếu có trong reply
    risk = 50
    if "Nguy cơ CAO" in reply:
        risk = 85
    elif "Nguy cơ TRUNG BÌNH" in reply:
        risk = 60
    elif "Nguy cơ THẤP" in reply:
        risk = 25
    return jsonify({"analysis": reply, "risk_score": risk})


if __name__ == "__main__":
    app.run(debug=True)
