---
owner: MindGuard Team
last_updated: 2026-04-14
source_files:
  - config.py
  - .planning/codebase/CONVENTIONS.md
---

# Quy ước viết tài liệu MindGuard (Documentation Conventions)

Tài liệu này quy định cách viết, thuật ngữ, và bảo vệ thông tin nhạy cảm cho toàn bộ tài liệu kỹ thuật MindGuard v2.

> **Phạm vi áp dụng:** Tất cả file trong `docs/`, `documents/SOP/`, và README.md.
> **Quy ước code** (naming, import, patterns): xem `.planning/codebase/CONVENTIONS.md`.

---

## 1. Quy ước ngôn ngữ (Language Conventions)

### Nguyên tắc chung

- **Prose (văn mô tả):** Viết bằng **tiếng Việt**.
- **Thuật ngữ kỹ thuật:** Giữ nguyên **tiếng Anh**, in nghiêng hoặc đặt trong `code`. Ví dụ: *blueprint*, `endpoint`, *serverless*.
- **Code blocks, file paths, command lines:** Giữ nguyên tiếng Anh.
- **Tên riêng:** Giữ nguyên — MindGuard, Flask, NeonDB, Vercel, OpenRouter, Cloudflare, Bootstrap.
- **Tiêu đề:** Có thể song ngữ để dễ tìm kiếm. Ví dụ: "Kiến trúc hệ thống (Architecture)".

### Ví dụ đúng / sai

| Đúng ✓ | Sai ✗ |
|---------|-------|
| Hệ thống sử dụng *blueprint* `auth` để xử lý xác thực. | Hệ thống sử dụng bản thiết kế xác thực để xử lý chứng thực. |
| *Route* `/quiz/start` trả về trang bắt đầu quiz. | Đường dẫn /quiz/start trả về trang bắt đầu câu đố. |
| Deploy lên *Vercel* bằng lệnh `vercel --prod`. | Triển khai lên Vơ-xen bằng lệnh triển khai sản xuất. |
| Chạy `python -m pytest` để kiểm thử. | Chạy trăn trừ em pi thử để kiểm thử. |

### Quy tắc cụ thể

1. **Không dịch** thuật ngữ có trong bảng thuật ngữ bên dưới.
2. **Viết hoa** tên model/class đúng cách: `Registration`, `ScammerReport` (PascalCase).
3. **Dùng backtick** (`` ` ``) cho tên file, lệnh, biến, route: `config.py`, `SECRET_KEY`, `/api/chatbot/send`.
4. **Dấu tiếng Việt đầy đủ:** Không viết tắt dấu (vd: "khong" thay vì "không").

---

## 2. Bảng thuật ngữ (Glossary)

Các thuật ngữ dưới đây **KHÔNG được dịch** sang tiếng Việt trong tài liệu.

| Thuật ngữ (English) | Giải thích (Vietnamese) | Ghi chú |
|---------------------|------------------------|---------|
| blueprint | Mô-đun route trong Flask, nhóm các endpoint liên quan | MindGuard có 8 blueprints |
| route | Đường dẫn URL được xử lý bởi server | Ví dụ: `/quiz/start` |
| endpoint | Điểm truy cập API hoặc trang web | Route + method = endpoint |
| middleware | Lớp xử lý trung gian giữa request và response | Flask không gọi đúng "middleware" nhưng decorator tương tự |
| decorator | Hàm bao bọc (wrapper) dùng `@` syntax trong Python | `@login_required`, `@limiter.limit` |
| template | File HTML Jinja2 dùng để render giao diện | Nằm trong `templates/` |
| static files | File tĩnh (CSS, JS, hình ảnh) serve trực tiếp | Nằm trong `static/` |
| model | Lớp Python đại diện cho bảng trong database | SQLAlchemy model |
| migration | Script thay đổi cấu trúc database | Nằm trong `database/` |
| schema | Cấu trúc (bảng, cột, quan hệ) của database | Định nghĩa trong `models/models.py` |
| query | Câu truy vấn database | SQLAlchemy query hoặc raw SQL |
| relationship | Quan hệ giữa các bảng (1-N, N-N) | `db.relationship()` |
| foreign key | Khóa ngoại liên kết giữa hai bảng | `db.ForeignKey()` |
| ORM | Object-Relational Mapping — ánh xạ class ↔ bảng DB | Flask-SQLAlchemy |
| serverless | Mô hình chạy code không quản lý server | Vercel Functions |
| cold start | Lần khởi động đầu tiên của serverless function | Thường chậm hơn các lần sau |
| environment variable | Biến môi trường cấu hình ứng dụng | Xem `.env.example` |
| secret | Giá trị bí mật (API key, password, encryption key) | KHÔNG BAO GIỜ đưa vào tài liệu |
| deployment | Quá trình đưa code lên server production | `vercel --prod` |
| rollback | Quay lại phiên bản deployment trước | Vercel Dashboard > Deployments |
| rate limiting | Giới hạn số request trong khoảng thời gian | Flask-Limiter, `@limiter.limit` |
| CAPTCHA | Kiểm tra người dùng là người thật | Cloudflare Turnstile |
| CSRF | Cross-Site Request Forgery — tấn công giả mạo request | Flask-WTF CSRFProtect |
| session | Phiên làm việc server-side lưu trạng thái user | Flask session (cookie-based) |
| authentication | Xác thực danh tính người dùng | Login/register flow |
| encryption | Mã hóa dữ liệu nhạy cảm | `REPORT_ENCRYPTION_KEY` |
| chatbot | Trợ lý AI trò chuyện tự động | OpenRouter API |
| prompt | Câu lệnh/hướng dẫn gửi cho AI model | System prompt + user message |
| fallback | Phương án dự phòng khi AI/API gặp lỗi | `simple_bot_reply()` |
| hard-block | Chặn cứng — từ chối trả lời chủ đề nhạy cảm | Chính trị, tôn giáo, tự hại |
| timeout | Thời gian chờ tối đa trước khi hủy request | OpenRouter: 8 giây |

---

## 3. Quy tắc bảo vệ thông tin (Redaction Rules)

### Nguyên tắc tối cao

**KHÔNG BAO GIỜ** copy giá trị thật từ `config.py`, `.env/`, hoặc Vercel Dashboard vào tài liệu.

### Format placeholder

Khi cần ví dụ về secret/credential trong tài liệu, sử dụng:

| Loại | Format | Ví dụ |
|------|--------|-------|
| API key | `your-xxx-key-here` | `OPENROUTER_API_KEY=your-openrouter-key-here` |
| Password | `your-xxx-here` | `ADMIN_PASSWORD=your-admin-password-here` |
| Connection string | Generic URL | `DATABASE_URL=postgresql://user:password@host/dbname` |
| Hex secret | `your-xxx-here` | `SECRET_KEY=your-flask-secret-key-here` |

### Patterns nguy hiểm — kiểm tra trước khi commit

Trước khi commit bất kỳ file tài liệu nào, **grep toàn bộ file** cho các pattern sau:

| Pattern | Mô tả | Lệnh kiểm tra |
|---------|--------|----------------|
| `sk-or-v1-` theo sau bởi chuỗi hex dài | OpenRouter API key | `grep -r "sk-or-v1-[a-f0-9]" docs/` |
| Chuỗi hex > 32 ký tự | SECRET_KEY, ADMIN_UNSUSPEND_SECRET | `grep -rE "[a-f0-9]{32,}" docs/` |
| `postgresql://` kèm password thật | Database connection string | `grep -r "postgresql://[^u]" docs/` |
| Cloudflare key dạng `0x...` | Turnstile site/secret key | `grep -r "0x[A-Za-z0-9]" docs/` |

### Quy trình xử lý khi phát hiện secret

1. **Xóa ngay** secret khỏi file tài liệu.
2. Thay bằng placeholder format ở trên.
3. Nếu đã commit: `git reset HEAD~1` rồi commit lại (nếu chưa push).
4. Nếu đã push: yêu cầu admin force-push để xóa khỏi git history.

---

## 4. Quy tắc cập nhật tài liệu (Document Maintenance)

### Khi nào cần cập nhật tài liệu

| Khi thay đổi... | Cập nhật file... |
|-----------------|------------------|
| `routes/*.py` (thêm/sửa/xóa route) | `docs/technical/API.md` |
| `models/models.py` (thêm/sửa bảng, cột) | `docs/technical/DATABASE.md` |
| `config.py` (thêm env var mới) | `.env.example` + `docs/technical/ARCHITECTURE.md` |
| Deploy config (`vercel.json`, env vars) | `documents/SOP/SOP_VAN_HANH.md` |
| Admin workflow (dashboard, moderation) | `documents/SOP/SOP_QUAN_TRI.md` |
| Scammer report flow | `documents/SOP/SOP_BAO_CAO.md` |
| Kiến trúc tổng thể (stack, infrastructure) | `docs/technical/ARCHITECTURE.md` + `docs/technical/DECISIONS.md` |

### Metadata header bắt buộc

Mỗi file tài liệu kỹ thuật **phải** có YAML frontmatter:

```yaml
---
owner: [Tên người/nhóm chịu trách nhiệm]
last_updated: [YYYY-MM-DD]
source_files:
  - [file1.py]
  - [file2.py]
---
```

- `owner`: Người/nhóm maintain file này.
- `last_updated`: Ngày cập nhật cuối cùng.
- `source_files`: Các file code mà tài liệu tham chiếu — khi file code thay đổi, tài liệu cần review.

### Quy trình review tài liệu

1. Khi PR thay đổi code thuộc bảng mapping ở trên → **reviewer kiểm tra** tài liệu tương ứng đã được update chưa.
2. Nếu chưa update → yêu cầu bổ sung trong cùng PR hoặc tạo issue theo dõi.
3. Định kỳ (mỗi milestone): chạy cross-check giữa code và tài liệu — xem Phase 19 (Verification).

### Checklist review trước khi merge

- [ ] Code thay đổi model → `DATABASE.md` updated?
- [ ] Code thay đổi route → `API.md` updated?
- [ ] Config key mới → `.env.example` + `SOP_VAN_HANH.md` updated?
- [ ] Thay đổi admin workflow → `SOP_QUAN_TRI.md` updated?
- [ ] Thay đổi report flow → `SOP_BAO_CAO.md` updated?
- [ ] Metadata header `last_updated` cập nhật trong file đã sửa?
