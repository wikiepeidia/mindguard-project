# BÁO CÁO TIẾN ĐỘ VÀ CẬP NHẬT TÍNH NĂNG - DỰ ÁN MINDGUARD

**Kính gửi:** Giảng viên hướng dẫn / Cố vấn dự án

Dưới đây là báo cáo tổng hợp về tiến độ phát triển của dự án **MindGuard** (Nền tảng giáo dục và phòng chống lừa đảo trực tuyến). Báo cáo này tóm tắt các chức năng cốt lõi đã hoàn thiện, đồng thời chi tiết hóa các hạng mục nâng cấp mới nhất về hệ thống và chuẩn hóa mã nguồn.

---

## PHẦN 1: CÁC CHỨC NĂNG CỐT LÕI ĐÃ HOÀN THIỆN

1. **Quản lý Tài khoản (Auth & Profile):** Hoàn thiện quy trình đăng ký và đăng nhập bảo mật với xác thực hai yếu tố (OTP) qua email. Cung cấp giao diện quản lý và cập nhật thông tin cá nhân.
2. **Hệ thống Trắc nghiệm (Quiz & Leaderboard):** Nền tảng đánh giá kiến thức an toàn thông tin của người dùng. Tích hợp Bảng xếp hạng (Leaderboard) theo thành tích và tự động cấp "Chứng chỉ" hoàn thành.
3. **Hệ thống Cảnh báo (Report Scammer):** Chức năng cốt lõi cho phép cộng đồng báo cáo các số điện thoại, đường dẫn URL, hoặc Số tài khoản chiếm đoạt tài sản. Hệ thống cung cấp cơ sở dữ liệu để tra cứu và nhận diện các đối tượng khả nghi.
4. **Trợ lý Ảo AI (Chatbot):** Tích hợp Trí tuệ Nhân tạo thông qua API của OpenRouter. Hỗ trợ người dùng phân tích văn bản, tư vấn trực tiếp và tự động nhận diện các dấu hiệu lừa đảo.
5. **Thư viện Kiến thức (Library):** Kho lưu trữ các tài liệu, bài giảng và tình huống phòng chống an ninh mạng thực tế.
6. **Hệ thống Quản trị (Admin Dashboard):** Phân hệ dành riêng cho Ban quản trị viên nhằm theo dõi, xét duyệt nội dung báo cáo và quản lý dữ liệu người dùng.

---

## PHẦN 2: CÁC TÍNH NĂNG NÂNG CẤP MỚI ĐƯỢC TÍCH HỢP

*(Tất cả tính năng đã được kiểm thử và tích hợp thành công vào mã nguồn thực tế)*

**Hệ thống Báo cáo (Report Scammer) đã được nâng cấp chuyên sâu với hơn 15 tính năng mới, bao gồm:**

- **Trạng thái Xác minh (Verification Status):** Phân loại cảnh báo theo 3 cấp độ (Đã xác minh / Chờ xử lý / Chưa xác minh).
- **Hệ thống Đánh giá Rủi ro (Risk Scoring):** Thuật toán tự động tính điểm rủi ro từ 0 đến 100 dựa trên số lượng báo cáo, mức độ chính xác của bằng chứng và thời gian.
- **Bảo mật Dữ liệu (Data Masking):** Cơ chế mã hóa tự động (ví dụ: `091***5678`) nhằm bảo vệ thông tin cá nhân của các bên liên quan.
- **Bộ lọc Trực tiếp (Live Feed Filter):** Hỗ trợ tra cứu dữ liệu cập nhật theo mức độ cảnh báo chuyên dụng.
- **Thẻ Gợi ý (Search Chips) & Tiêu bản (Placeholder):** Tối ưu hóa UI/UX, hỗ trợ người dùng nhập liệu trực quan.
- **Trang Hồ sơ Đối tượng (Entity Profile Page):** Trang tổng hợp báo cáo chi tiết về từng đối tượng hình sự lừa đảo chuyên biệt.
- **Biểu đồ Dòng thời gian (Timeline) & Lượt xác nhận (Confirmed Count):** Minh bạch quá trình cập nhật báo cáo, cấp độ nguy hiểm và số liệu xác nhận chéo.
- **Tính năng Hiện/Ẩn dữ liệu (Toggle Mask/Unmask):** Trao quyền tự chủ kiểm soát thông tin ẩn danh cho người sử dụng.
- **Phân loại Ngành (Categories):** Tích hợp hệ thống Dropdown phân loại chi tiết với hơn 40 loại hình lừa đảo, được tổ chức thành 5 nhóm cơ bản.
- **Khuyến cáo (Disclaimers):** Bổ sung chính sách bảo vệ dữ liệu người báo cáo, kết hợp hướng dẫn chi tiết quy trình hoạt động (How it works).

---

## PHẦN 3: CẤU TRÚC KỸ THUẬT VÀ TỔ CHỨC MÃ NGUỒN

Tổng quan về sự nâng cấp kiến trúc phần mềm, cơ sở dữ liệu và logic xử lý (Backend/Frontend):

### 1. Cơ Sở Dữ Liệu & Models (`models/models.py`)
- Khởi tạo thêm 3 cấu trúc dữ liệu mới thuộc thực thể `ScammerReport`: `verification_status`, `risk_score` và `confirmed_by_count`.

### 2. Hàm Tiện ích / Utility Functions (`utils/helpers.py`)
- `mask_sensitive_data`: Phương thức thay thế (Masking) và bảo mật thông tin (SĐT, STK).
- `calculate_risk_score`: Thuật toán máy tính giúp tính toán rủi ro trên 4 hệ số tham chiếu.
- `get_verification_badge` & `get_risk_level_info`: Hệ quy chiếu đánh giá và truy xuất định dạng UI cho các trạng thái đối tượng lừa đảo.

### 3. Điều phối / Routes (`routes/main.py`)
- Tái cấu trúc hàm `index()`: Phân phối 3 tham số tham chiếu mới lên bảng tương tác chính.
- Khởi tạo route `scammer_profile`: Cung cấp điểm điều hướng URL độc lập cho từng hồ sơ phạm tội.

### 4. Giao diện Người dùng / Templates (`templates/`)
- **`index.html`**: Cập nhật bộ Search Chips, nút điều hướng bộ lọc, nhãn mức độ rủi ro, và minh họa quy trình báo cáo.
- **`report_scammer.html`**: Nâng cấp biểu mẫu (Form) bằng Dropdown Select với danh mục 40 nhóm hành vi, đính kèm xác nhận bảo mật.
- **`scammer_profile.html` (Khởi tạo mới)**: Khung HTML chuyên biệt tích hợp Thanh biểu đồ rủi ro (Progress bar), Hình ảnh thu thập (Evidence) và Biến động lịch sử (Timeline lịch trình).

### 5. Cập nhật Cơ sở Dữ liệu & Tài liệu 
- **Migration Scripts**: Xây dựng mã nguồn `database/migrate_add_verification.py` và `add_columns.py` chạy trên ngữ cảnh ứng dụng (Context) để thay đổi cấu trúc bảng SQLite hiện hành một cách an toàn.
- **Tài liệu Hệ thống**: Bổ sung `documents/IMPROVEMENTS_REPORT.md` và `QUICK_START.md` với văn bản kỹ thuật quy chuẩn hỗ trợ quá trình bàn giao và bảo trì.

---

**Kết luận:** Tính đến thời điểm hiện tại, dự án đã đồng bộ hóa toàn diện từ logic nghiệp vụ (Backend bằng Python/Flask) tới hệ thống biểu diễn (Frontend HTML/JS/CSS). Yêu cầu kỹ thuật nâng cấp mới đã thi công thành công và tương thích hoàn toàn trên kho lưu trữ mã nguồn dự án.
