"""Chatbot AI logic for analyzing scam scenarios."""


def simple_bot_reply(message: str) -> str:
    """Analyze message and provide scam risk assessment."""
    msg = (message or "").lower()

    # Simple rule-based AI/ML simulation
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
        ("cấp bách", 10, "tạo áp lực thời gian"),
        ("khẩn cấp", 10, "tạo áp lực khẩn cấp"),
    ]

    for kw, score, reason in risky_keywords:
        if kw in msg:
            risk_score += score
            reasons.append(reason)

    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        level = "Nguy cơ CAO"
        advice = (
            "⚠️ Tình huống có mức độ rủi ro rất cao. Tuyệt đối không cung cấp OTP/mật khẩu, "
            "không bấm vào link lạ và không chuyển bất kỳ khoản tiền nào. Hãy chủ động liên hệ "
            "kênh chính thức (ngân hàng, công ty, cơ quan nhà nước) để kiểm tra."
        )
    elif risk_score >= 40:
        level = "Nguy cơ TRUNG BÌNH"
        advice = (
            "⚠️ Tình huống có nhiều dấu hiệu cần cảnh giác. Bạn nên dừng lại, chụp màn hình làm bằng chứng, "
            "tự tìm số tổng đài/website chính thức để gọi hỏi lại, và không chia sẻ thông tin nhạy cảm."
        )
    else:
        level = "Nguy cơ THẤP (tạm thời)"
        advice = (
            "✓ Hiện chưa thấy nhiều từ khóa rủi ro, nhưng vẫn cần thận trọng. Đừng vội tin vào lời hứa lợi nhuận, "
            "hãy xác minh từ nhiều nguồn đáng tin cậy và tham khảo ý kiến người thân, chuyên gia."
        )

    # If empty message, provide general guidance
    if not message.strip():
        return (
            "👋 Xin chào! Hãy mô tả tình huống bạn gặp phải:\n"
            "• Ai đã liên hệ với bạn?\n"
            "• Qua kênh nào (SMS, Facebook, Zalo...)?\n"
            "• Họ yêu cầu bạn làm gì?\n\n"
            "💡 Nhớ che số tài khoản, CCCD, OTP khi chia sẻ. MindGuard sẽ giúp bạn phân tích mức độ rủi ro."
        )

    base_note = (
        "📊 Kết quả phân tích chỉ mang tính tham khảo, không thay thế tư vấn pháp lý hoặc hỗ trợ khẩn cấp.\n\n"
    )

    if reasons:
        reason_text = "\n• ".join(reasons)
        detail = f"**Đánh giá: {level}** (khoảng {risk_score}%)\n\n**Dấu hiệu nhận diện:**\n• {reason_text}\n\n**Khuyến nghị:**\n{advice}"
    else:
        detail = f"**Đánh giá: {level}**\n\n**Khuyến nghị:**\n{advice}"

    return base_note + detail


def generate_support_reply(message: str) -> str:
    """Generate support chatbot reply for reporting guidance."""
    msg = message.lower()
    
    if "bằng chứng" in msg or "chứng cứ" in msg or "evidence" in msg:
        return (
            "📸 **Bằng chứng cần thiết khi tố cáo:**\n\n"
            "1. Ảnh chụp màn hình cuộc trò chuyện\n"
            "2. Thông tin tài khoản/số điện thoại của scammer\n"
            "3. Ảnh chụp giao dịch (nếu có)\n"
            "4. Link trang web/nhóm lừa đảo\n"
            "5. Thông tin bổ sung khác\n\n"
            "✓ Cần ít nhất 1 bằng chứng rõ ràng để tố cáo được xét duyệt."
        )
    
    if "làm sao" in msg or "cách" in msg or "how to" in msg:
        return (
            "📝 **Hướng dẫn tố cáo scammer:**\n\n"
            "1. Điền đầy đủ thông tin về scammer\n"
            "2. Mô tả chi tiết hành vi lừa đảo\n"
            "3. Tải lên ít nhất 1 bằng chứng\n"
            "4. Hệ thống sẽ tự động xét duyệt\n"
            "5. Nếu đủ điều kiện, tố cáo sẽ được duyệt ngay\n\n"
            "🔒 Thông tin của bạn được mã hóa và bảo mật hoàn toàn!"
        )
    
    if "bảo mật" in msg or "an toàn" in msg or "privacy" in msg:
        return (
            "🔐 **Cam kết bảo mật:**\n\n"
            "✓ Danh tính người tố cáo được mã hóa\n"
            "✓ Không hiển thị thông tin cá nhân\n"
            "✓ Chỉ admin có thể xem dữ liệu gốc\n"
            "✓ Scammer không thể biết ai đã tố cáo\n\n"
            "Bạn có thể yên tâm tố cáo mà không lo bị trả thù!"
        )
    
    if "duyệt" in msg or "approved" in msg or "thẩm định" in msg:
        return (
            "✅ **Quy trình duyệt tố cáo:**\n\n"
            "• **Tự động duyệt:** Nếu có đủ bằng chứng và scammer đã bị tố cáo ≥ 3 lần\n"
            "• **Chờ xét duyệt:** Nếu là tố cáo mới hoặc bằng chứng chưa đủ\n"
            "• **Từ chối:** Nếu không có bằng chứng hoặc thông tin không rõ ràng\n\n"
            "Thời gian xét duyệt thủ công: 24-48 giờ"
        )
    
    return (
        "👋 Xin chào! Tôi là trợ lý ảo của MindGuard.\n\n"
        "Bạn có thể hỏi tôi về:\n"
        "• Cách tố cáo scammer\n"
        "• Bằng chứng cần thiết\n"
        "• Chính sách bảo mật\n"
        "• Quy trình duyệt tố cáo\n\n"
        "Hãy cho tôi biết bạn cần hỗ trợ gì!"
    )
