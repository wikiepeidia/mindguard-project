import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import db, ScamReport
from app import app

def create_kb_articles():
    with app.app_context():
        # Clean existing articles
        # ScamReport.query.delete() 

        articles = [
            {
                "title": "Nhận diện lừa đảo 'Tuyển dụng việc nhẹ lương cao'",
                "category": "Tuyển dụng",
                "channel": "Telegram, Zalo",
                "description": "Các đối tượng thường đăng bài tuyển cộng tác viên chốt đơn, like dạo, xem video TikTok kiếm tiền. Yêu cầu nạp tiền để làm nhiệm vụ hoặc nâng cấp tài khoản VIP.",
                "protection_tip": "Không bao giờ nạp tiền để được làm việc. Các công ty chân chính không yêu cầu đặt cọc. Kiểm tra mã số thuế và địa chỉ công ty."
            },
            {
                "title": "Cảnh báo thủ đoạn giả danh công an, viện kiểm sát",
                "category": "Giả danh",
                "channel": "Điện thoại (VoIP)",
                "description": "Gọi điện thông báo bạn có liên quan đến vụ án ma túy, rửa tiền. Yêu cầu chuyển tiền vào 'tài khoản tạm giữ' để phục vụ điều tra hoặc cài ứng dụng lạ để lấy cắp OTP.",
                "protection_tip": "Cơ quan công an KHÔNG làm việc qua điện thoại. KHÔNG chuyển tiền, KHÔNG cài app qua link lại (.apk)."
            },
            {
                "title": "Lừa đảo tình cảm (Romance Scam)",
                "category": "Tình cảm",
                "channel": "Tinder, Facebook Dating",
                "description": "Kết bạn, tán tỉnh qua mạng thời gian dài. Sau đó nhờ nhận hộ quà từ nước ngoài (phải đóng thuế hải quan) hoặc rủ rê đầu tư tiền ảo lãi suất cao.",
                "protection_tip": "Cảnh giác với người yêu trên mạng chưa từng gặp mặt nhưng đòi tiền. Không nhận quà, không chuyển khoản cho 'nhân viên hải quan' giả mạo."
            },
             {
                "title": "Giả mạo nhân viên ngân hàng nâng hạn mức thẻ tín dụng",
                "category": "Tài chính",
                "channel": "SMS Brandname Fake, Zalo",
                "description": "Gửi tin nhắn SMS có tên thương hiệu (Brandname) giả mạo, chứa link lừa đảo yêu cầu đăng nhập và cung cấp OTP để nâng hạn mức hoặc hủy phí thường niên.",
                "protection_tip": "Không click vào link trong tin nhắn SMS. Gọi trực tiếp lên tổng đài ngân hàng để xác minh."
            }
        ]

        for art in articles:
            # Check exist
            exists = ScamReport.query.filter_by(title=art['title']).first()
            if not exists:
                new_art = ScamReport(
                    title=art['title'],
                    category=art['category'],
                    channel=art['channel'],
                    description=art['description'],
                    protection_tip=art['protection_tip']
                )
                db.session.add(new_art)
                print(f"Added: {art['title']}")
            else:
                print(f"Skipped: {art['title']}")
        
        db.session.commit()

if __name__ == "__main__":
    create_kb_articles()
