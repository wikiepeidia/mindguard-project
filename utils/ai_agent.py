"""
AI Agent module for MindGuard.
Simulates AI learning by analyzing user reports and generating new content.
"""
import random
import re
from models import ScammerReport
from sqlalchemy import func

def analyze_scam_trends():
    """
    Analyzes the database to find top scam types and common platforms.
    Returns a summary string.
    """
    try:
        # Top scam types
        top_types = (
            ScammerReport.query.with_entities(ScammerReport.scam_type, func.count(ScammerReport.id))
            .filter_by(status='approved')
            .group_by(ScammerReport.scam_type)
            .order_by(func.count(ScammerReport.id).desc())
            .limit(3)
            .all()
        )
        
        # Common platforms
        top_platforms = (
            ScammerReport.query.with_entities(ScammerReport.platform, func.count(ScammerReport.id))
            .filter_by(status='approved')
            .group_by(ScammerReport.platform)
            .order_by(func.count(ScammerReport.id).desc())
            .limit(3)
            .all()
        )

        summary = "AI Assistant Analysis:\n"
        if top_types:
            summary += "Top scam trends observed: " + ", ".join([f"{t[0]} ({t[1]} reports)" for t in top_types]) + ".\n"
        
        if top_platforms:
            summary += "Most dangerous platforms: " + ", ".join([f"{p[0]} ({p[1]} reports)" for p in top_platforms]) + "."
            
        return summary
    except Exception as e:
        return "Not enough data for AI analysis."

def generate_dynamic_question():
    """
    Generates a quiz question based on a real report from the database.
    ("AI learning from users")
    """
    try:
        # Get a random approved report
        # We fetch IDs first to be efficient
        report_ids = [ID[0] for ID in ScammerReport.query.filter_by(status='approved').with_entities(ScammerReport.id).all()]
        
        if not report_ids:
            return None
            
        random_id = random.choice(report_ids)
        report = ScammerReport.query.get(random_id)
        
        if not report:
            return None
            
        # Context sanitization
        # Truncate description to avoid too long text
        desc_snippet = report.description[:150] + "..." if len(report.description) > 150 else report.description
        
        # Scammer info masking (show partial)
        info = report.scammer_info_raw or "ẩn danh"
        if len(info) > 4:
            masked_info = info[:3] + "***" + info[-2:]
        else:
            masked_info = "***"
            
        scam_type = report.scam_type or "Lừa đảo"
        platform = report.platform or "Mạng xã hội"
        
        # Simple AI heuristic for prevention tip based on scam type/platform
        prevention_tip = "Tuyệt đối không tương tác và báo cáo ngay."
        st_lower = scam_type.lower()
        if "khoản" in st_lower or "bank" in st_lower:
            prevention_tip = "Tuyệt đối không chuyển tiền cho người lạ, dù lý do thuyết phục đến đâu."
        elif "việc" in st_lower or "tuyển" in st_lower:
            prevention_tip = "Không nạp tiền để 'giữ chỗ' hoặc 'làm nhiệm vụ'. Việc làm thật không thu phí này."
        elif "web" in st_lower or "link" in st_lower:
            prevention_tip = "Không nhấp vào link lạ. Kiểm tra kỹ tên miền (domain) chính chủ."

        # Construct question
        question_data = {
            "id": 9000 + report.id, # Dynamic ID range
            "question": (
                f"⚠️ TÌNH HUỐNG THỰC TẾ (AI Generated):\n"
                f"Một người dùng đã báo cáo kẻ gian sử dụng số/TK '{masked_info}' trên {platform} "
                f"với hành vi: \"{desc_snippet}\".\n"
                f"Bạn nên xử lý thế nào?"
            ),
            "options": [
                "Thử nhắn tin hội thoại để khai thác thêm thông tin.",
                "Tin tưởng vì họ có thông tin giao dịch cụ thể.",
                "Chặn liên lạc, không giao dịch và báo cáo MindGuard.", # Correct
                "Hỏi bạn bè trên Facebook xem có uy tín không."
            ],
            "answer": 2, # Index 2 matches the correct option
            "explanation": (
                f"Đây là dấu hiệu của {scam_type}. {prevention_tip} "
                "Hệ thống MindGuard đã ghi nhận trường hợp này."
            )
        }
        
        return question_data

    except Exception as e:
        print(f"Error generating AI question: {e}")
        return None
