<!--
DOCUMENT METADATA
Owner: DevOps / Developer
Last updated: 2026-04-14
Source files: app.py, config.py, vercel.json, requirements.txt
Update trigger: Thay đổi cách deploy, thêm env var mới, thay đổi infrastructure
Update scope: Cập nhật toàn bộ — quy trình deploy, env vars, troubleshooting
-->

# SOP VẬN HÀNH HỆ THỐNG MINDGUARD

> Phiên bản: 1.0 · Cập nhật: 2026-04-14 · Owner: DevOps / Developer

## 1. Mục đích

Hướng dẫn vận hành hệ thống MindGuard trên môi trường production (Vercel + NeonDB). Tài liệu này giúp team member thực hiện deploy, theo dõi logs, rollback và xử lý sự cố mà không cần hỏi developer gốc.

## 2. Phạm vi áp dụng

- Deploy ứng dụng lên production.
- Theo dõi logs và monitoring.
- Rollback khi deployment gặp sự cố.
- Xử lý các lỗi thường gặp trong vận hành.
- Không bao gồm quy trình quản trị nội dung (xem `SOP_QUAN_TRI.md`).

## 3. Vai trò tham gia

- **Developer / DevOps**: Thực hiện deploy, rollback, xử lý sự cố kỹ thuật.
- **Admin**: Theo dõi trạng thái hệ thống, báo cáo sự cố.

## 4. Thông tin hệ thống

| Thành phần | Chi tiết |
|------------|----------|
| Production URL | `https://mindguard-five.vercel.app` |
| Hosting | Vercel (Serverless Functions) |
| Database | NeonDB PostgreSQL 15 (serverless) |
| AI API | OpenRouter (DeepSeek, Gemini, Llama) |
| CAPTCHA | Cloudflare Turnstile |
| Source Code | GitHub repository |

### Dashboards quản lý

- **Vercel Dashboard**: Quản lý deployments, logs, env vars.
- **NeonDB Dashboard**: Quản lý database, connection strings, branches.
- **OpenRouter Dashboard**: Theo dõi API usage, credits.

## 5. Quy trình Deploy

### 5.1 Deploy tự động (khuyến nghị)

1. Push code lên branch `main` trên GitHub.
2. Vercel tự động detect thay đổi và bắt đầu build.
3. Thời gian build trung bình: **1-2 phút**.
4. Sau khi build thành công, deployment tự động go-live.

### 5.2 Kiểm tra deployment

1. Truy cập **Vercel Dashboard > Project > Deployments**.
2. Xác nhận deployment mới nhất có trạng thái **Ready**.
3. Kiểm tra production URL hoạt động bình thường.

### 5.3 Xem build logs

1. **Vercel Dashboard > Deployments > chọn deployment > Build Logs**.
2. Kiểm tra không có error trong quá trình build.
3. Lưu ý: warnings thường không ảnh hưởng đến hoạt động.

### 5.4 Lưu ý quan trọng

- Vercel filesystem là **read-only** — chỉ thư mục `/tmp` có thể ghi.
- Mỗi request chạy trong một serverless function riêng biệt.
- Cold start có thể mất 1-3 giây cho request đầu tiên.

## 6. Xem Logs

### 6.1 Logs trên Vercel

1. **Vercel Dashboard > Project > Logs**.
2. Filter theo:
   - Thời gian (last hour, last day, custom range).
   - Route / path cụ thể.
   - Status code (200, 4xx, 5xx).
   - Level (info, warning, error).
3. Realtime logs: bật nút **Live** để xem logs theo thời gian thực.

### 6.2 Logs local (khi chạy dev server)

- File `logs/access.log` ghi nhận các request.
- Chạy dev server: `python app.py` (localhost:5000).

## 7. Rollback Deployment

### 7.1 Rollback qua Vercel Dashboard (nhanh nhất)

1. Truy cập **Vercel Dashboard > Project > Deployments**.
2. Tìm deployment trước đó hoạt động tốt.
3. Click **⋮ (menu)** > **Promote to Production**.
4. Xác nhận — deployment cũ sẽ thay thế deployment hiện tại ngay lập tức.

### 7.2 Rollback qua Git

1. `git revert HEAD` — tạo commit đảo ngược thay đổi gần nhất.
2. `git push origin main` — Vercel auto-deploy bản đã revert.
3. Phương pháp này tạo lịch sử rõ ràng hơn.

### 7.3 Khi nào cần rollback

- Trang production trả về lỗi 500 sau deploy.
- Tính năng quan trọng bị hỏng (login, quiz, báo cáo).
- Database connection lỗi do config sai.

## 8. Xử lý sự cố thường gặp

### 8.1 Cold start chậm (1-3 giây)

**Triệu chứng**: Request đầu tiên sau khoảng idle mất 1-3 giây.

**Nguyên nhân**: Đặc trưng của Vercel Serverless Functions — function instance bị cold khi không có traffic.

**Xử lý**: Đây là hành vi bình thường, không cần can thiệp. Các request tiếp theo sẽ nhanh hơn.

### 8.2 Database connection error

**Triệu chứng**: Lỗi `OperationalError`, `Connection refused`, hoặc timeout khi truy vấn database.

**Xử lý**:

1. Kiểm tra **NeonDB Dashboard** — xác nhận database đang hoạt động.
2. Kiểm tra env var `DATABASE_URL` trên Vercel Dashboard đúng format.
3. NeonDB serverless auto-suspend sau khoảng idle — request đầu có thể chậm hơn.
4. Kiểm tra connection limit (NeonDB free tier giới hạn concurrent connections).

### 8.3 Rate limit 429 (Too Many Requests)

**Triệu chứng**: Response trả về status `429`.

**Nguyên nhân**: Flask-Limiter giới hạn requests — mặc định 200/phút.

**Xử lý**:

1. Đợi hết cooldown period (thường 1 phút).
2. Kiểm tra có đang bị spam/abuse không.
3. Xem chi tiết rate limiting tại ADR-005 trong `docs/technical/DECISIONS.md`.

### 8.4 AI chatbot timeout

**Triệu chứng**: Chatbot không phản hồi hoặc trả về lỗi timeout.

**Nguyên nhân**: OpenRouter API timeout (8 giây — xem ADR-004).

**Xử lý**:

1. Hệ thống tự động fallback sang model khác.
2. Kiểm tra **OpenRouter Dashboard** — xem API status và credits.
3. Kiểm tra env var `OPENROUTER_API_KEY` hợp lệ.
4. Nếu tất cả models đều fail → chatbot trả về response mặc định.

### 8.5 CSRF error (400 Bad Request)

**Triệu chứng**: Form submit trả về lỗi 400, message liên quan đến CSRF.

**Nguyên nhân**: Template thiếu CSRF token hoặc session hết hạn.

**Xử lý**:

1. Kiểm tra template có `{{ csrf_token() }}` trong form.
2. Yêu cầu user refresh trang để lấy session mới.
3. Kiểm tra `SECRET_KEY` env var đã được set.

### 8.6 Filesystem error (Read-only)

**Triệu chứng**: Lỗi `OSError: Read-only file system` khi ghi file.

**Nguyên nhân**: Vercel serverless filesystem là read-only.

**Xử lý**:

1. Chỉ ghi file vào thư mục `/tmp` (ephemeral — bị xóa sau mỗi request).
2. Dùng database hoặc external storage cho dữ liệu persistent.
3. Upload files hiện sử dụng thư mục `static/uploads/` — chỉ hoạt động khi chạy local.

## 9. Environment Variables

### 9.1 Danh sách env vars cần thiết

Tham chiếu đầy đủ tại file `.env.example` trong source code.

| Env Var | Mô tả | Bắt buộc |
|---------|--------|----------|
| `SECRET_KEY` | Flask secret key cho sessions và CSRF | Có |
| `DATABASE_URL` | NeonDB PostgreSQL connection string | Có |
| `OPENROUTER_API_KEY` | API key cho AI chatbot | Có |
| `CLOUDFLARE_SITE_KEY` | Cloudflare Turnstile site key | Có |
| `CLOUDFLARE_SECRET_KEY` | Cloudflare Turnstile secret key | Có |
| `ADMIN_PASSWORD` | Mật khẩu đăng nhập admin | Có |
| `REPORT_ENCRYPTION_KEY` | Key mã hóa dữ liệu báo cáo | Có |
| `ADMIN_UNSUSPEND_SECRET` | Secret key mở khóa admin bị suspend | Có |
| `ABUS_MODE` | Chế độ anti-spam (`monitor` / `enforce`) | Không (mặc định: `monitor`) |

### 9.2 Cập nhật env vars trên Vercel

1. **Vercel Dashboard > Project > Settings > Environment Variables**.
2. Thêm hoặc sửa giá trị env var.
3. Chọn environment: Production / Preview / Development.
4. **Quan trọng**: Sau khi thay đổi env var, cần **Redeploy** để áp dụng.

### 9.3 Lưu ý bảo mật

- Không commit secrets vào source code.
- Không chia sẻ env vars qua kênh không được mã hóa.
- Rotate keys định kỳ, đặc biệt khi có sự thay đổi nhân sự.

## 10. Tài liệu liên quan

- [docs/technical/ARCHITECTURE.md](../../docs/technical/ARCHITECTURE.md) — Kiến trúc hệ thống tổng thể
- [docs/technical/API.md](../../docs/technical/API.md) — Danh sách routes và endpoints
- [docs/technical/DATABASE.md](../../docs/technical/DATABASE.md) — Schema database
- [docs/technical/DECISIONS.md](../../docs/technical/DECISIONS.md) — ADRs: deployment (ADR-001), AI safety (ADR-004), rate limiting (ADR-005)
- [documents/SOP/SOP_QUAN_TRI.md](SOP_QUAN_TRI.md) — SOP quản trị viên
- [documents/SOP/SOP_BAO_CAO.md](SOP_BAO_CAO.md) — Quy trình kiểm duyệt báo cáo lừa đảo
