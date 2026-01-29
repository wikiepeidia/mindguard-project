# MindGuard - Project TODO & Status Update
*(Cập nhật ngày 11/01/2026)*

## 1. Tính năng Đã Hoàn Thành (Completed Features)

### A. Hệ thống Tố cáo & Giao diện (Scammer Reporting)
- [x] **Giao diện chuẩn Checkscam.vn**:
    - Chia làm 2 Tab rõ ràng: **Tố cáo STK Ngân hàng** và **Tố cáo Website/Link độc hại**.
    - Form nhập liệu chi tiết: Số tài khoản, Tên chủ, Ngân hàng, Link Facebook, Website giả mạo...
- [x] **Hệ thống Upload Bằng chứng**:
    - Hỗ trợ tải ảnh trực tiếp từ thiết bị (tối đa 10 ảnh).
    - Hỗ trợ dán link Google Drive/Imgur.
    - **Bảo mật file**: 
        - Kiểm tra đuôi file (chỉ allow png, jpg, gif).
        - **Advanced check**: Kiểm tra Magic Bytes (Header) của file để chặn file giả mạo đuôi ảnh (chặn shell/malware).
- [x] **Cam kết pháp lý**:
    - Bắt buộc tick chọn "Tôi cam kết đúng sự thật".
    - Bắt buộc tick chọn "Tôi là nạn nhân & Chịu trách nhiệm trước pháp luật" mới được gửi.
- [x] **Bảo mật danh tính**:
    - Mã hóa ID người tố cáo, không hiển thị trực tiếp thông tin người tố cáo.

### B. Hệ thống Chatbot & AI Agent
- [x] **Chatbot Thông minh (Database Integration)**:
    - Chatbot tự động quét tin nhắn người dùng.
    - **Cảnh báo đỏ (Red Alert)**: Nếu phát hiện SĐT/STK/Website đã có trong "Sổ đen" (Database ScammerReport), chatbot cảnh báo ngay lập tức kèm số lần bị tố cáo.
    - Phân tích rủi ro dựa trên từ khóa (OTP, chuyển tiền, việc nhẹ lương cao...) và đưa ra % rủi ro.
- [x] **AI Agent (Học từ dữ liệu)**:
    - Module `utils/ai_agent.py` tự động lấy dữ liệu từ các đơn tố cáo thật đã được duyệt.
    - Tạo ra **câu hỏi trắc nghiệm động (Dynamic Question)** dựa trên tình huống lừa đảo có thật để đưa vào bài kiểm tra nhận thức.

### C. Bài kiểm tra nhận thức & Chứng chỉ (Quiz & Certificate)
- [x] **Logic bài test**:
    - Random 15 câu hỏi mỗi lượt thi.
    - Trong đó: 14 câu hỏi tĩnh (cơ bản) + **1 câu hỏi AI tạo ra từ tình huống lừa đảo mới nhất**.
- [x] **Chứng chỉ**:
    - Người dùng đạt >75% điểm sẽ được cấp "Chứng nhận nhận thức an toàn không gian mạng" (Certificate).
- [x] **Quy trình**: Đăng ký -> Làm Quiz -> Có chứng chỉ -> Mới được phép tham gia hoạt động sâu hơn (tùy chọn).

### D. Hệ thống Tài khoản & Bảo mật (Auth & Security)
- [x] **Phân quyền truy cập (Access Control)**:
    - **Khách**: Chỉ xem Trang chủ, Bảng vàng (Leaderboard).
    - **Thành viên (Đã đăng nhập)**: Mới được sử dụng Bot chat, Làm Quiz, Gửi tố cáo.
    - Sử dụng decorator `@login_required` để bảo vệ các route quan trọng (`/scammer/report`, `/quiz`, `/chatbot`).
- [x] **Quản lý phiên (Session)**:
    - Fix lỗi tự đăng xuất. Cấu hình `PERMANENT_SESSION_LIFETIME` 7 ngày.

### E. Cấu trúc Dự án
- [x] Tách file module hóa:
    - `routes/`: Chứa các file xử lý luồng (`scammer.py`, `chatbot.py`, `quiz.py`...).
    - `utils/`: Chứa logic phụ trợ (`ai_agent.py`, `encryption.py`, `helpers.py`).
    - `models.py`: Cấu trúc Database (SQLite).
    - `templates/`: Giao diện HTML (Jinja2).

---

## 2. Phần đang phát triển / Cần làm thêm (Pending / Improvements)

### UI/UX
- [ ] **Làm đẹp Trang chủ**: Hiện tại đã ổn nhưng có thể thêm biểu đồ thống kê trực quan hơn.
- [ ] **Leaderboard**: Thêm bộ lọc (theo ngân hàng, theo tháng).

### Chức năng nâng cao (Future)
- [ ] **Admin Dashboard**: Hoàn thiện trang quản trị để Duyệt/Từ chối đơn tố cáo (Hiện tại đang duyệt tự động hoặc chờ).
- [ ] **Email Verify**: Xác thực email khi đăng ký (Gửi OTP như yêu cầu cũ - *Note: Cần cấu hình SMTP Server*).
- [ ] **API Public**: Cho phép các bên thứ 3 check scam qua API của MindGuard.

---

## 3. Ghi chú Kỹ thuật
- **Database**: SQLite (File `instance/mindguard.db`).
- **Uploads**: Lưu tại `static/uploads/evidence/`.
- **Run**: Chạy file `app.py`. 

