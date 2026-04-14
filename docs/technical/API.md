<!--
DOCUMENT METADATA
Owner: @backend-developer
Update trigger: Thêm, sửa, hoặc xóa route/endpoint
Update scope: Toàn bộ tài liệu
Read by: Tất cả team members. Tra cứu route trước khi thêm hoặc sửa endpoint.
-->

# API & Route Reference

> **Production**: `https://mindguard-five.vercel.app`
> **Local**: `http://localhost:5000`
> **Authentication**: Flask *sessions* (cookie-based, signed) — không có Bearer token
> **Rate Limiting**: Mặc định 200 *request*/phút per IP (Flask-Limiter). *Per-route limits* ghi chú trong từng section.
> **CSRF**: Tất cả POST *requests* yêu cầu CSRF token (Flask-WTF) trừ các *endpoints* được đánh dấu `csrf.exempt`.
> **Last updated**: 2026-04-14

---

## Bảng tổng hợp (Summary)

| Blueprint | Prefix | Tổng routes | Auth mặc định | Ghi chú |
|-----------|--------|-------------|----------------|---------|
| `main` | — | 4 | Không | Trang chủ, *leaderboard*, tìm kiếm, *scammer profile* |
| `auth` | — | 8 | Không (trừ profile) | Đăng nhập, đăng ký, OTP, profile |
| `quiz` | — | 5 | `@login_required` | Luồng quiz, kết quả, chứng nhận |
| `scammer` | `/scammer` | 2 | Không | Báo cáo lừa đảo, theo dõi |
| `chatbot` | `/chatbot` | 7 | `@login_required` (phần lớn) | Chatbot AI, hỗ trợ |
| `admin` | `/admin` | 12 | `@admin_required` (trừ login) | Dashboard, kiểm duyệt |
| `library` | — | 2 | Không | Thư viện kiến thức |
| `api` | `/api/v1` | 2 | Không | JSON API public |

**Tổng cộng: 42 routes** (8 *blueprints*)

---

## main — Trang chủ & công cộng

*Blueprint*: `main_bp` — không có *prefix*

### Page Routes (HTML)

| Method | Path | Auth | Template | Mô tả |
|--------|------|------|----------|-------|
| GET | `/` | Không | `index.html` | Trang chủ — thống kê tổng quan và top bảng xếp hạng |
| GET | `/leaderboard` | Không | `leaderboard.html` | Bảng xếp hạng người báo cáo scammer nhiều nhất |
| GET | `/scammer/<int:scammer_id>` | Không | `scammer_profile.html` | Trang chi tiết *scammer* — số lần bị báo cáo, mức độ nguy hiểm |

### API Endpoints (JSON)

| Method | Path | Auth | Rate Limit | Mô tả | Response chính |
|--------|------|------|------------|-------|----------------|
| POST | `/api/search` | Không | Mặc định | Tìm kiếm *scammer* theo tên, SĐT, hoặc tài khoản ngân hàng | `{results: [...]}` |

---

## auth — Xác thực người dùng

*Blueprint*: `auth_bp` — không có *prefix*

### Page Routes (HTML)

| Method | Path | Auth | Rate Limit | Template | Mô tả |
|--------|------|------|------------|----------|-------|
| GET, POST | `/login` | Không | POST: 10/phút, 3/giây | `login.html` | Đăng nhập — Cloudflare Turnstile CAPTCHA |
| GET, POST | `/register` | Không | POST: 5/phút | `register.html` | Đăng ký tài khoản — email + mật khẩu + CAPTCHA |
| GET, POST | `/verify-otp` | Không | — | `verify_otp.html` | Nhập OTP gửi qua email để xác thực |
| GET | `/onboarding` | Không | — | `onboarding.html` | Hướng dẫn người dùng mới sau đăng ký |
| GET | `/complete-onboarding` | Không | — | *redirect* → `/` | Hoàn thành *onboarding*, chuyển về trang chủ |
| GET | `/profile` | `@login_required` | — | `profile.html` | Trang cá nhân — thông tin, quiz history |
| POST | `/profile/edit` | `@login_required` | — | *redirect* → `/profile` | Cập nhật tên hiển thị, thông tin cá nhân |
| GET | `/logout` | Không | — | *redirect* → `/` | Đăng xuất, xóa *session* |

---

## quiz — Hệ thống Quiz

*Blueprint*: `quiz_bp` — không có *prefix*

Tất cả *routes* yêu cầu `@login_required`.

### Page Routes (HTML)

| Method | Path | Auth | Template | Mô tả |
|--------|------|------|----------|-------|
| GET | `/quiz` | `@login_required` | `quiz.html` | Chọn danh mục quiz (loại lừa đảo) |
| GET, POST | `/quiz/step/<int:idx>` | `@login_required` | `quiz_start.html` | Trả lời câu hỏi quiz từng bước — GET hiển thị, POST submit đáp án |
| GET | `/quiz/finalize` | `@login_required` | *redirect* → `/quiz/result` | Tính điểm quiz, lưu kết quả vào database |
| GET | `/quiz/result` | `@login_required` | `quiz_result.html` | Hiển thị kết quả quiz — điểm, phân tích |
| GET | `/certificate` | `@login_required` | `certificate.html` | Chứng nhận hoàn thành quiz (≥75% đạt) |

---

## scammer — Báo cáo lừa đảo

*Blueprint*: `scammer_bp` — *prefix* `/scammer`

### Page Routes (HTML)

| Method | Path | Auth | Template | Mô tả |
|--------|------|------|----------|-------|
| GET, POST | `/scammer/report` | Không | `report_scammer.html` | Gửi báo cáo *scammer* — CAPTCHA + anti-spam check |

### API Endpoints (JSON)

| Method | Path | Auth | Mô tả | Response chính |
|--------|------|------|-------|----------------|
| POST | `/scammer/follow` | Không | Theo dõi / bỏ theo dõi *scammer* | `{success, followed}` |

---

## chatbot — Chatbot AI

*Blueprint*: `chatbot_bp` — *prefix* `/chatbot`

### Page Routes (HTML)

| Method | Path | Auth | Template | Mô tả |
|--------|------|------|----------|-------|
| GET | `/chatbot/` | `@login_required` | `chatbot.html` | Giao diện chatbot — danh sách *sessions* cũ, tạo mới |
| GET | `/chatbot/new` | `@login_required` | *redirect* → `/chatbot/` | Tạo phiên chat mới |

### API Endpoints (JSON)

Tất cả JSON *endpoints* đã được `csrf.exempt`.

| Method | Path | Auth | Rate Limit | Mô tả | Response chính |
|--------|------|------|------------|-------|----------------|
| POST | `/chatbot/send` | `@login_required` | 20/phút, 3/giây | Gửi tin nhắn cho chatbot AI, lưu lịch sử | `{reply, session_id, reply_source, reply_model}` |
| POST | `/chatbot/api` | Không | 10/phút, 2/giây | Quick AI chat cho floating widget — không lưu lịch sử | `{reply, reply_source, reply_model}` |
| POST | `/chatbot/rename` | `@login_required` | — | Đổi tên phiên chat | `{success}` |
| POST | `/chatbot/support` | Không | 10/phút | AI hỗ trợ cho trang báo cáo scammer | `{reply, reply_source, reply_model}` |
| POST | `/chatbot/feedback` | `@login_required` | 10/phút | Gửi đánh giá phản hồi AI (👍/👎) | `{success}` |

---

## admin — Quản trị hệ thống

*Blueprint*: `admin_bp` — *prefix* `/admin`

Tất cả *routes* (trừ login) yêu cầu `@admin_required` — kiểm tra `session['is_admin']`.

### Page Routes (HTML)

| Method | Path | Auth | Rate Limit | Template | Mô tả |
|--------|------|------|------------|----------|-------|
| GET, POST | `/admin/login` | Không | POST: 5/phút, 1/giây | `admin_login.html` | Đăng nhập admin |
| GET | `/admin/` | Admin | — | `admin_dashboard.html` | Dashboard — quản lý users, thống kê |
| GET | `/admin/logout` | Admin | — | *redirect* → `/admin/login` | Đăng xuất admin |
| GET | `/admin/scammer-reports` | Admin | — | `admin_scammer_reports.html` | Danh sách báo cáo chờ duyệt |
| GET, POST | `/admin/export-dataset` | Admin | — | `admin_export.html` / file download | Xuất dataset CSV cho ML training |
| GET | `/admin/sensitive-access-logs` | Admin | — | `admin_sensitive_access_logs.html` | Xem audit logs truy cập dữ liệu nhạy cảm |

### Action Endpoints (POST → redirect)

| Method | Path | Auth | Mô tả |
|--------|------|------|-------|
| POST | `/admin/unsuspend` | Không* | Mở khóa tài khoản admin bị suspend — yêu cầu `ADMIN_UNSUSPEND_SECRET` |
| POST | `/admin/create-admin` | Admin | Tạo tài khoản admin mới |
| POST | `/admin/delete-user/<int:user_id>` | Admin | Xóa người dùng |
| POST | `/admin/edit-user/<int:user_id>` | Admin | Cập nhật thông tin người dùng |
| POST | `/admin/approve-report/<int:report_id>` | Admin | Duyệt báo cáo scammer |
| POST | `/admin/reject-report/<int:report_id>` | Admin | Từ chối báo cáo scammer |

> \* `/admin/unsuspend` được `csrf.exempt` và không yêu cầu admin session — sử dụng secret key để mở khóa.

---

## library — Thư viện kiến thức

*Blueprint*: `library_bp` — không có *prefix*

### Page Routes (HTML)

| Method | Path | Auth | Template | Mô tả |
|--------|------|------|----------|-------|
| GET | `/library` | Không | `library.html` | Danh sách bài viết kiến thức phòng chống lừa đảo |
| GET | `/library/<int:article_id>` | Không | `library_detail.html` | Chi tiết bài viết |

---

## api — Public JSON API

*Blueprint*: `api_bp` — *prefix* `/api/v1`

### API Endpoints (JSON)

| Method | Path | Auth | Rate Limit | Mô tả | Response chính |
|--------|------|------|------------|-------|----------------|
| GET | `/api/v1/check` | Không | 30/phút, 5/giây | Kiểm tra scammer — query param `?q=` (SĐT, tên, bank) | `{found, scammer_data}` |
| GET | `/api/v1/stats` | Không | 60/phút | Thống kê hệ thống tổng quan | `{total_reports, total_scammers, total_users}` |

---

## Ghi chú bổ sung

### Models liên quan

Các *routes* tương tác với 14 SQLAlchemy *models* — xem [DATABASE.md](DATABASE.md) để tra cứu chi tiết schema, kiểu dữ liệu, và quan hệ giữa các bảng.

### Xác thực (Authentication patterns)

- **User**: `session['registration_email']` — đặt sau đăng nhập/OTP thành công
- **Admin**: `session['is_admin']` — đặt sau đăng nhập admin
- **Decorators**: `@login_required` (kiểm tra user session), `@admin_required` (kiểm tra admin session)

### Rate Limiting

- **Global**: 200 *request*/phút per IP (Flask-Limiter, cấu hình trong `extensions.py`)
- **Per-route**: Ghi chú trong bảng từng section — xem [ADR-005](DECISIONS.md) cho quyết định thiết kế

---

## Xem thêm (See Also)

- [ARCHITECTURE.md](ARCHITECTURE.md) — Kiến trúc tổng thể hệ thống
- [DATABASE.md](DATABASE.md) — Schema database chi tiết (14 bảng, ER diagram)
- [DECISIONS.md](DECISIONS.md) — Architecture Decision Records (5 ADRs)
- [CONVENTIONS.md](CONVENTIONS.md) — Quy ước viết tài liệu
