# Lộ Trình Phát Triển Tối Ưu cho MindGuard (Best Approach Strategy)
>
> Main lanugage for the project should be vietnamese-consistent with existing documentation.
Dựa trên phân tích mã nguồn hiện tại (Flask Skeleton) và tài liệu mô tả dự án, dưới đây là lộ trình đề xuất để chuyển đổi MindGuard từ bản demo (MVP) sang một sản phẩm thực tế hoàn chỉnh.

## I. Đánh Giá Hiện Trạng

* **Điểm mạnh:**
  * Cấu trúc dự án MVC rõ ràng (Templates/Static/App logic).
  * Giao diện Frontend đã hoàn thiện tốt với Bootstrap.
  * Các luồng chính (Quiz, Report, Chat) đã chạy được.
* **Điểm yếu (Cần khắc phục ngay):**
  * **Dữ liệu tạm thời:** Mọi báo cáo lừa đảo và kết quả quiz đang lưu trong RAM (biến global). Reset server là mất hết.
  * **Chatbot sơ khai:** Logic `if-else` bắt từ khóa quá đơn giản, chưa thực sự là "AI".
  * **Dashboard tĩnh:** Trang Admin chưa kết nối dữ liệu thực.

---

## II. Kế Hoạch Triển Khai (Action Plan)

Chúng ta không nên làm tất cả cùng lúc. Hãy chia làm 3 giai đoạn ưu tiên:

### Giai đoạn 1: "Bộ nhớ" (Database Implementation) - Ưu tiên cao nhất

Mục tiêu: Dữ liệu (Báo cáo lừa đảo, Người dùng đăng ký) phải được lưu trữ vĩnh viễn.

1. **Cài đặt `Flask-SQLAlchemy`**:
    * Đây là ORM tiêu chuẩn cho Flask, giúp thao tác DB bằng Python object thay vì SQL thuần.
    * Sử dụng **SQLite** cho môi trường phát triển (dễ dàng, không cần cài server DB riêng).
2. **Thiết kế Database Schema (`models.py`)**:
    * `User`: Lưu thông tin người làm Quiz (Họ tên, Email, Điểm số, Mã chứng nhận).
    * `ScamReport`: Lưu các báo cáo lừa đảo (Tiêu đề, Loại lừa đảo, Mô tả, Kênh tiếp cận).
3. **Refactor `app.py`**:
    * Thay thế các list tạm `reports = []` bằng các câu lệnh truy vấn DB (`ScamReport.query.all()`).

### Giai đoạn 2: "Bộ não" quản trị (Dashboard & Admin)

Mục tiêu: Tận dụng file `admin_dashboard.html` đã có.

1. **Xây dựng Route Admin**:
    * Tạo route `/admin` có bảo mật (cần đăng nhập, dù đơn giản là hardcode user/pass lúc đầu).
2. **Hiển thị dữ liệu thực**:
    * Query tất cả `ScamReport` từ DB và đẩy sang template Admin.
    * Thêm chức năng **Xóa** (Delete) các báo cáo spam/sai lệch.
3. **Thống kê cơ bản**:
    * Đếm số lượng Report theo loại (Ngân hàng, Tình cảm, v.v.) để vẽ biểu đồ.

### Giai đoạn 3: "Trí tuệ" (AI Integration) - Điểm nhấn dự án

Mục tiêu: Biến Chatbot thành trợ lý thực thụ.

1. **Nâng cấp Chatbot**:
    * Thay logic `rule-based` bằng API của một LLM (như **DEEPSEEK api?** - đang miễn phí, hoặc DeếéekDee).
    * Tạo **System Prompt** cho AI: *"Bạn là chuyên gia an ninh mạng MindGuard. Hãy tư vấn ngắn gọn, tập trung vào cách phòng tránh lừa đảo..."*
2. **Gợi ý tự động**:
    * Khi người dùng gõ mô tả lừa đảo, dùng AI để gợi ý "Loại lừa đảo" tự động.

---

## III. Đề xuất Cấu trúc Database (Models) , database Progressql /sqlite

Dưới đây là thiết kế kiến nghị cho file `models.py` sắp tới:

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    score = db.Column(db.Integer)
    certificate_code = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ScamReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    scam_type = db.Column(db.String(50)) # Ngân hàng, Đầu tư, v.v.
    description = db.Column(db.Text, nullable=False)
    contact_method = db.Column(db.String(50)) # SMS, Zalo, v.v.
    is_verified = db.Column(db.Boolean, default=False) # Cho admin duyệt
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

## IV. Kết luận

Hãy bắt đầu ngay với **Giai đoạn 1 (Database)**. Đây là nền móng quan trọng nhất. Sau khi cài xong DB, việc làm Admin Dashboard hay AI sẽ dễ dàng hơn rất nhiều.
