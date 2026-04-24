import sys
import os

# Add parent directory to path to import app and models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import db, ScammerReport, ScammerLeaderboard, ScamReport
from utils.encryption import encrypt_scammer_info, hash_reporter_id, serialize_evidence
from utils.helpers import calculate_danger_level
from config import Config
from datetime import datetime, timedelta
import random

def seed_data():
    with app.app_context():
        print("🌱 Seeding database with mock data...")

        # 1. Seed Scammer Reports (and Leaderboard)
        # We need raw info to encrypt
        mock_scammers = [
            {
                "identifier": "0912345678",
                "name": "Nguyễn Văn Hùng",
                "type": "Lừa đảo tuyển cộng tác viên",
                "platform": "Zalo",
                "desc": "Tự xưng là nhân viên Tiki/Shopee tuyển cộng tác viên chốt đơn. Yêu cầu nạp tiền để nhận hoa hồng 20%. Sau khi nạp 5 triệu thì chặn liên lạc.",
                "reports": 15,
                "evidence": ["https://i.imgur.com/example1.jpg"]
            },
            {
                "identifier": "0987654321",
                "name": "Trần Thị Mai (Techcombank)",
                "type": "Giả mạo ngân hàng",
                "platform": "Điện thoại",
                "desc": "Gọi điện thông báo tài khoản bị khóa, yêu cầu cung cấp OTP để mở khóa. Giọng miền Nam, rất hung hăng.",
                "reports": 8,
                "evidence": []
            },
            {
                "identifier": "02473001234",
                "name": "Cán bộ Viện Kiểm Sát",
                "type": "Giả danh cơ quan nhà nước",
                "platform": "Điện thoại",
                "desc": "Gọi điện dọa nạt có liên quan đến đường dây rửa tiền. Yêu cầu chuyển toàn bộ tiền vào 'tài khoản tạm giữ' của VKS để điều tra.",
                "reports": 25,
                "evidence": ["https://drive.google.com/file/d/example"]
            },
             {
                "identifier": "support.facebook.check-verify.com",
                "name": "Hỗ trợ Facebook",
                "type": "Đánh cắp tài khoản (Phishing)",
                "platform": "Website",
                "desc": "Gửi tin nhắn cảnh báo vi phạm tiêu chuẩn cộng đồng, kèm link giả mạo để chiếm quyền kiểm soát fanpage.",
                "reports": 42,
                "evidence": ["https://i.imgur.com/phishing.png"]
            },
             {
                "identifier": "0865342112",
                "name": "Sàn Forex LionGroup",
                "type": "Đầu tư tài chính lừa đảo",
                "platform": "Telegram",
                "desc": "Mời gọi vào nhóm Telegram đọc lệnh. Cam kết lợi nhuận 30%/tháng. Sàn sập không rút được tiền.",
                "reports": 12,
                "evidence": []
            },
            {
                "identifier": "0334567890",
                "name": "Tuấn Forex",
                "type": "Đầu tư tiền ảo",
                "platform": "Telegram",
                "desc": "Kêu gọi đầu tư tiền ảo lãi suất cao, sau đó biến mất.",
                "reports": 5,
                "evidence": []
            },
            {
                 "identifier": "0909090909",
                 "name": "Shop Mẹ và Bé (Giả)",
                 "type": "Lừa đảo mua bán hàng",
                 "platform": "Facebook",
                 "desc": "Bán sữa giá rẻ, yêu cầu chuyển khoản trước rồi không giao hàng.",
                 "reports": 3,
                 "evidence": []
            },
             {
                 "identifier": "0911223344",
                 "name": "Vay nhanh lãi thấp",
                 "type": "Tín dụng đen",
                 "platform": "App",
                 "desc": "Vay 2 triệu nhưng bắt trả 5 triệu sau 1 tuần. Khủng bố điện thoại người thân.",
                 "reports": 18,
                 "evidence": []
            },
            {
                 "identifier": "0966778899",
                 "name": "Vé máy bay giá rẻ",
                 "type": "Lừa đảo du lịch",
                 "platform": "Facebook",
                 "desc": "Bán combo du lịch giá rẻ bất ngờ, yêu cầu cọc 50%. Nhận tiền xong chặn số.",
                 "reports": 6,
                 "evidence": []
            },
            {
                 "identifier": "0888999111",
                 "name": "Mỹ Phẩm Xách Tay Auth",
                 "type": "Hàng giả/Nhái",
                 "platform": "Shopee/Facebook",
                 "desc": "Bán nước hoa giả, son giả nhưng cam kết chính hãng. Không cho kiểm hàng.",
                 "reports": 4,
                 "evidence": []
            }
        ]

        # Reporters (anonymous hashes)
        reporter_hashes = [hash_reporter_id(f"user{i}") for i in range(10)]

        for item in mock_scammers:
            encrypted_id = encrypt_scammer_info(item['identifier'], Config.REPORT_ENCRYPTION_KEY)
            
            # Check if exists
            existing = ScammerReport.query.filter_by(scammer_identifier=encrypted_id).first()
            
            if not existing:
                # Create Report
                report = ScammerReport(
                    scammer_identifier=encrypted_id,
                    scammer_info_raw=item['identifier'], # Add raw info
                    scammer_name=item['name'],
                    scam_type=item['type'],
                    platform=item['platform'],
                    description=item['desc'],
                    evidence_urls=serialize_evidence(item['evidence']),
                    reporter_hash=random.choice(reporter_hashes),
                    status='approved', # Auto approve for seed data
                    report_count=item['reports'],
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
                )
                db.session.add(report)
                db.session.commit() # Commit to get ID
                
                # Create Leaderboard entry
                leaderboard = ScammerLeaderboard(
                    scammer_id=report.id,
                    total_reports=item['reports'],
                    danger_level=calculate_danger_level(item['reports']),
                    last_reported=datetime.utcnow()
                )
                db.session.add(leaderboard)
                print(f"   [+] Added scammer: {item['name']} with {item['reports']} reports")
        
        # 2. Seed Educational Articles (ScamReport)
        articles = [
            {
                "title": "Cảnh giác chiêu trò 'Việc nhẹ lương cao'",
                "category": "Lừa đảo tuyển dụng",
                "channel": "Mạng xã hội",
                "desc": "Các đối tượng thường mạo danh các sàn TMĐT như Shopee, Tiki, Lazada tuyển cộng tác viên xử lý đơn hàng. Ban đầu chúng sẽ trả lại tiền gốc và lãi nhỏ để dụ dỗ. Khi số tiền nạp vào lớn (hàng chục triệu), chúng sẽ viện cớ lỗi hệ thống, sai cú pháp... để chiếm đoạt.",
                "tip": "Không bao giờ nạp tiền để được làm việc. Kiểm tra kỹ thông tin tuyển dụng từ các kênh chính thức của doanh nghiệp."
            },
             {
                "title": "Nhận diện cuộc gọi giả danh Công an, Viện kiểm sát",
                "category": "Giả danh cơ quan chức năng",
                "channel": "Điện thoại",
                "desc": "Kẻ lừa đảo sử dụng công nghệ VoIP để giả mạo số điện thoại cơ quan chức năng. Chúng thông báo nạn nhân liên quan đến vụ án ma túy, rửa tiền... và yêu cầu chuyển tiền vào 'tài khoản an toàn' để phục vụ điều tra.",
                "tip": "Cơ quan công an KHÔNG BAO GIỜ làm việc qua điện thoại về các vụ án, không yêu cầu chuyển tiền. Nếu nhận cuộc gọi này, hãy tắt máy và báo cơ quan công an gần nhất."
            },
            {
                "title": "Lừa đảo chiếm đoạt sim điện thoại (Upgrade SIM 4G)",
                "category": "Công nghệ cao",
                "channel": "SMS/Điện thoại",
                "desc": "Kẻ gian giả danh nhà mạng gọi điện hỗ trợ nâng cấp SIM 4G/5G miễn phí. Chúng hướng dẫn cú pháp tin nhắn nhằm chiếm quyền kiểm soát SIM, từ đó lấy mã OTP ngân hàng, ví điện tử của nạn nhân.",
                "tip": "Chỉ thực hiện đổi SIM tại các điểm giao dịch chính thức của nhà mạng. Không gửi các mã số lạ theo hướng dẫn của người gọi đến."
            }
        ]
        
        for art in articles:
             # Check distinct
             if not ScamReport.query.filter_by(title=art['title']).first():
                 new_art = ScamReport(
                     title=art['title'],
                     category=art['category'],
                     channel=art['channel'],
                     description=art['desc'],
                     protection_tip=art['tip']
                 )
                 db.session.add(new_art)
                 print(f"   [+] Added article: {art['title']}")

        db.session.commit()
        print("✅ Database seeding completed!")

if __name__ == "__main__":
    seed_data()
