# Requirements: MindGuard v2

**Defined:** 2026-03-19
**Core Value:** Nguoi dung co the hoc, kiem tra nhan thuc va gui bao cao lua dao mot cach de dung, an toan, va dang tin cay.

## v1.0 Requirements (Completed)

### UI/UX

- [x] **UI-01**: Nguoi dung thay light mode dong bo tren cac trang chinh (auth, quiz, report, profile, leaderboard).
- [x] **UI-02**: He thong su dung design tokens thong nhat (mau, font, spacing) cho cac trang uu tien.
- [x] **UI-03**: Trang quiz va report dam bao trai nghiem mobile-first o kich thuoc man hinh pho bien.

### Quiz

- [x] **QUIZ-01**: Nguoi dung lam bai quiz theo luong 1 cau hoi moi trang.
- [x] **QUIZ-02**: Nguoi dung thay thanh tien do va trang thai ro rang trong suot bai quiz.
- [x] **QUIZ-03**: Trang thai bai lam duoc giu on dinh khi refresh/back trong phien hop le.
- [x] **QUIZ-04**: He thong bo sung bo cau hoi theo chu de bao mat/lua dao de phu hop luong quiz moi.

### Privacy

- [x] **PRIV-01**: So dien thoai duoc che, chi hien 3 so cuoi o tat ca diem hien thi.
- [x] **PRIV-02**: Quy tac masking du lieu nhay cam duoc ap dung nhat quan trong toan he thong.
- [x] **PRIV-03**: Admin co nhat ky truy cap du lieu nhay cam de phuc vu kiem toan.

### Anti-Spam

- [x] **ABUS-01**: He thong ap dung rule tan suat gui to cao theo cua so thoi gian de chan spam.
- [x] **ABUS-02**: He thong danh gia rui ro dua tren da tin hieu (IP + cookie + account).
- [x] **ABUS-03**: Trien khai monitor mode truoc, sau do soft-enforce theo nguong duoc cau hinh.
- [x] **ABUS-04**: Nguoi dung nhan thong bao cooldown/chuyen trang thai voi ly do ro rang.

### Leaderboard

- [x] **LEAD-01**: Hien thi bang vinh danh nguoi to cao nhieu nhat.
- [x] **LEAD-02**: Ap dung integrity rule de giam gian lan tren leaderboard.

### Documentation & Operations

- [x] **DOC-01**: Admin co tai lieu SOP bang tieng Viet cho luong kiem duyet bao cao.
- [x] **DOC-02**: Nguoi dung co tai lieu huong dan bang tieng Viet de gui bao cao dung cach.

### ML Readiness

- [x] **ML-01**: Team co schema du lieu/gan nhan va quy tac an danh de thu thap du lieu moderation.
- [x] **ML-02**: Team co lo trinh offline-first cho baseline ML/DL va human-in-the-loop rollout.

## v1.1 Requirements

Requirements for PostgreSQL migration and Vercel deployment fix.

### Database Configuration

- [x] **DBCFG-01**: `.env/prosgressql_neondb.json` duoc cau truc lai thanh JSON hop le voi key `DATABASE_URL`
- [x] **DBCFG-02**: `config.py` chuyen `SQLALCHEMY_DATABASE_URI` tu SQLite sang NeonDB PostgreSQL
- [x] **DBCFG-03**: `psycopg2-binary` duoc them vao `requirements.txt`
- [x] **DBCFG-04**: SQLAlchemy engine duoc cau hinh `pool_pre_ping=True` va NeonDB pooler endpoint

### App Startup

- [x] **START-01**: Cold-start seeding bi xoa khoi `app.py` (khong chay `seed_all.py` moi Vercel invocation)
- [x] **START-02**: Logic `IS_VERCEL` SQLite `/tmp` path bi xoa khoi `config.py`
- [x] **START-03**: `db.create_all()` duoc xac nhan hoat dong voi NeonDB pooler connection

### Data Seeding

- [x] **SEED-01**: Seed scripts chay 1 lan duy nhat de tao du lieu ban dau tren NeonDB

### Vercel Deployment

- [x] **VDEP-01**: `DATABASE_URL` va cac secrets hien co duoc cau hinh trong Vercel environment variables
- [x] **VDEP-02**: Vercel deployment tra ve 200 (khong con 500 errors)

## v1.2 Requirements — Beta 1 Go-Live (Code Freeze)

Requirements cho gia cố hạ tầng, sửa lỗi UI, an toàn AI, và tin cậy trước Beta 1.

### Hạ tầng & Bảo mật

- [ ] **INFRA-01**: Xóa `db.create_all()` khỏi startup path — không tạo bảng mỗi cold start
- [ ] **INFRA-02**: Di chuyển `ADMIN_PASSWORD`, `REPORT_ENCRYPTION_KEY`, `SECRET_KEY` fallback từ `config.py` sang Vercel environment variables
- [x] **INFRA-03**: Bỏ hardcode admin credentials khỏi frontend để tránh user xâm nhập tài khoản admin *(đã hoàn thành bởi teammate)*
- [x] **INFRA-04**: Rate limiting DB-backed trên `/chatbot/api`, `/chatbot/support`, `/chatbot/send` để chống drain API budget *(đã hoàn thành bởi teammate — @limiter.limit trên cả 3 endpoints)*
- [ ] **INFRA-05**: Stress test với locust tìm ngưỡng CCU tối đa trước Beta 1

### Sửa lỗi UI

- [x] **UIFIX-01**: Sửa nút "Đăng xuất" trong dropdown menu để click được *(đã hoàn thành bởi teammate)*
- [x] **UIFIX-02**: Sửa hitbox quá nhỏ của mục "Hồ sơ" trong menu *(đã hoàn thành bởi teammate)*
- [x] **UIFIX-03**: Sửa chatbot bubble chat để lưu lịch sử trò chuyện giữa các phiên cho user đã đăng nhập *(đã hoàn thành bởi teammate — localStorage, 30 messages)*
- [x] **UIFIX-04**: Thiết kế và style huy hiệu "Certification Verify" đáng tin cậy và dễ nhìn *(đã hoàn thành bởi teammate)*
- [x] **UIFIX-05**: Rà soát và chỉnh sửa UI tổng thể cho gọn đẹp trước Beta *(đã hoàn thành bởi teammate — glassmorphism, modern CSS)*

### An toàn AI

- [ ] **AISF-01**: Giảm timeout OpenRouter từ 15s xuống 8s để không vượt 10s Vercel function kill limit *(hiện tại 10s, cần giảm xuống 8s)*
- [x] **AISF-02**: Hard-block trả lời cứng khi gặp chủ đề nhạy cảm (chính trị/tôn giáo/tự hại) + hotline Công an HN 113 *(đã hoàn thành bởi teammate)*
- [x] **AISF-03**: Điều chỉnh system prompt cho ngôn ngữ bình dân, tránh thuật ngữ kỹ thuật *(đã hoàn thành bởi teammate)*
- [x] **AISF-04**: Fallback an toàn khi AI không chắc chắn — cảnh báo OTP + hướng dẫn liên hệ cơ quan chức năng *(đã hoàn thành bởi teammate)*

### Tin cậy & Phản hồi

- [x] **TRUST-01**: Banner chính sách quyền riêng tư trên trang chủ: "MindGuard KHÔNG lưu trữ thông tin cá nhân, KHÔNG yêu cầu quyền truy cập danh bạ/tin nhắn" *(đã hoàn thành bởi teammate — section + modal)*
- [x] **TRUST-02**: Xác minh logging baseline (request, error, audit logs) hoạt động và lưu trữ an toàn trên Vercel *(đã hoàn thành bởi teammate — access logging trong app.py)*
- [ ] **TRUST-03**: Nút "Báo cáo sai / Góp ý" trên giao diện chatbot để thu thập dữ liệu tinh chỉnh cho Beta *(route /chatbot/support có, nhưng UI button chưa nổi bật)*

## v2 Requirements (Deferred)

### Anti-Fraud Nang Cao

- **ABUS-05**: Adaptive friction theo muc rui ro (step-up challenge linh hoat).
- **ABUS-06**: Co che machine-learning ho tro phat hien bat thuong sau khi co du telemetry.

### Leaderboard Nang Cao

- **LEAD-03**: Co che diem co trong so chat luong (khong chi dem so luong).
- **LEAD-04**: Giai thich minh bach ve cach tinh diem va dieu kien xep hang.

### Platform

- **ARCH-01**: Cloud storage cho file uploads (evidence images) thay cho local disk.
- **ARCH-02**: NeonDB branching cho Vercel preview deployments.

## Out of Scope

| Feature | Reason |
| ------- | ------ |
| File upload cloud storage | Deferred — evidence images khong critical cho deploy fix |
| NeonDB branching for preview deploys | Complexity khong can thiet cho initial deployment |
| Alembic/flask-migrate | Project dung manual migration scripts theo conventions |
| Auto-scaling/multi-region | v1.1 chi can 1 region on dinh |
| Dark mode | Uu tien infrastructure stability |
| SPA/microservices replatform | Rui ro hoi quy cao, khong can thiet |

## Traceability

| Requirement | Phase | Status |
| ----------- | ----- | ------ |
| UI-01 | Phase 3 | Complete |
| UI-02 | Phase 3 | Complete |
| UI-03 | Phase 3 | Complete |
| QUIZ-01 | Phase 4 | Complete |
| QUIZ-02 | Phase 4 | Complete |
| QUIZ-03 | Phase 4 | Complete |
| QUIZ-04 | Phase 4 | Complete |
| PRIV-01 | Phase 1 | Complete |
| PRIV-02 | Phase 1 | Complete |
| PRIV-03 | Phase 1 | Complete |
| ABUS-01 | Phase 2 | Complete |
| ABUS-02 | Phase 2 | Complete |
| ABUS-03 | Phase 2 | Complete |
| ABUS-04 | Phase 2 | Complete |
| LEAD-01 | Phase 5 | Complete |
| LEAD-02 | Phase 5 | Complete |
| DOC-01 | Phase 6 | Complete |
| DOC-02 | Phase 6 | Complete |
| ML-01 | Phase 6 | Complete |
| ML-02 | Phase 6 | Complete |
| DBCFG-01 | Phase 7 | Complete |
| DBCFG-02 | Phase 7 | Complete |
| DBCFG-03 | Phase 7 | Complete |
| DBCFG-04 | Phase 7 | Complete |
| START-01 | Phase 8 | Complete |
| START-02 | Phase 7 | Complete |
| START-03 | Phase 8 | Complete |
| SEED-01 | Phase 8 | Complete |
| VDEP-01 | Phase 9 | Complete |
| VDEP-02 | Phase 9 | Complete |
| INFRA-01 | Phase 10 | Pending |
| INFRA-02 | Phase 10 | Pending |
| INFRA-03 | Phase 10 | Complete (teammate) |
| UIFIX-01 | Phase 11 | Complete (teammate) |
| UIFIX-02 | Phase 11 | Complete (teammate) |
| UIFIX-03 | Phase 11 | Complete (teammate) |
| UIFIX-04 | Phase 11 | Complete (teammate) |
| UIFIX-05 | Phase 11 | Complete (teammate) |
| AISF-01 | Phase 12 | Pending |
| AISF-02 | Phase 12 | Complete (teammate) |
| AISF-03 | Phase 12 | Complete (teammate) |
| AISF-04 | Phase 12 | Complete (teammate) |
| INFRA-04 | Phase 13 | Complete (teammate) |
| TRUST-01 | Phase 13 | Complete (teammate) |
| TRUST-02 | Phase 13 | Complete (teammate) |
| TRUST-03 | Phase 13 | Pending |
| INFRA-05 | Phase 14 | Pending |

**Coverage:**

- v1.0 requirements: 20 total — all complete ✓
- v1.1 requirements: 10 total — all complete ✓
- v1.2 requirements: 17 total — 12 complete (teammate), 5 remaining
- Mapped to phases: 47/47 total requirements
- Unmapped: 0

---
*Requirements defined: 2026-03-19*
*Last updated: 2026-04-13 after teammate code drop verification*
