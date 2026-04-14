<!--
DOCUMENT METADATA
Owner: @backend-developer
Last updated: 2026-04-14
Source files: routes/admin.py, models/models.py, services/sensitive_access_log.py
Update trigger: Thay đổi chức năng admin dashboard, thêm/sửa admin route
Update scope: Cập nhật các bước thao tác, đường dẫn, và bảng thông tin
-->

# SOP QUẢN TRỊ VIÊN MINDGUARD

> Phiên bản: 1.0 · Cập nhật: 2026-04-14 · Owner: Admin Team

## 1. Mục đích

Hướng dẫn quản trị viên thực hiện các thao tác quản lý trên hệ thống MindGuard: đăng nhập, quản lý người dùng, kiểm duyệt báo cáo, xuất dữ liệu và xem audit logs.

## 2. Phạm vi áp dụng

- Đăng nhập và quản lý phiên admin.
- Dashboard tổng quan.
- Quản lý người dùng (tạo admin, sửa, xóa).
- Kiểm duyệt báo cáo lừa đảo (tóm tắt — chi tiết xem `SOP_BAO_CAO.md`).
- Xuất dữ liệu.
- Xem audit logs.
- Mở khóa admin bị suspend.

## 3. Vai trò tham gia

- **Quản trị viên (Admin)**: Thực hiện tất cả thao tác quản lý qua giao diện `/admin/`.
- **Developer**: Hỗ trợ kỹ thuật khi cần tạo admin ban đầu hoặc xử lý sự cố.

## 4. Đăng nhập Admin

### 4.1 Thông tin đăng nhập

| Thông tin | Chi tiết |
|-----------|----------|
| URL | `/admin/login` |
| Username | `admin` (mặc định) |
| Password | Env var `ADMIN_PASSWORD` |
| Rate limit | 5 lần/phút cho POST (chống brute-force) |

### 4.2 Các bước thực hiện

1. Truy cập `/admin/login`.
2. Nhập username và password.
3. Hoàn thành Cloudflare Turnstile CAPTCHA.
4. Nhấn **Đăng nhập**.

### 4.3 Sau khi đăng nhập

- Session được thiết lập: `session['is_admin'] = True`.
- Chuyển hướng tự động đến Dashboard (`/admin/`).
- Session hết hạn khi đóng trình duyệt hoặc logout.

### 4.4 Đăng xuất

- Truy cập `/admin/logout` hoặc click nút đăng xuất.
- Session admin bị xóa.

## 5. Dashboard (`/admin/`)

### 5.1 Tổng quan

Dashboard hiển thị:

- Danh sách người dùng đã đăng ký (bảng `registrations`).
- Thống kê nhanh: tổng số users, số báo cáo chờ duyệt.
- Các nút thao tác: tạo admin, sửa user, xóa user.

### 5.2 Các thao tác chính từ Dashboard

| Thao tác | Đường dẫn | Phương thức |
|----------|-----------|-------------|
| Xem dashboard | `/admin/` | GET |
| Tạo admin mới | `/admin/create-admin` | POST |
| Sửa user | `/admin/edit-user/<id>` | POST |
| Xóa user | `/admin/delete-user/<id>` | POST |

## 6. Quản lý người dùng

### 6.1 Tạo admin mới

**Yêu cầu**: Đã đăng nhập với quyền admin.

**Đường dẫn**: `POST /admin/create-admin`

**Các bước**:

1. Trên Dashboard, tìm form tạo admin.
2. Nhập thông tin: username, email, password.
3. Nhấn **Tạo Admin**.
4. Hệ thống tạo tài khoản admin mới trong bảng `registrations` với `is_admin = True`.

### 6.2 Sửa thông tin người dùng

**Đường dẫn**: `POST /admin/edit-user/<id>`

**Các bước**:

1. Trên Dashboard, tìm user cần sửa.
2. Click nút **Sửa**.
3. Cập nhật thông tin cần thiết.
4. Nhấn **Lưu**.

**Lưu ý**: Thay đổi được ghi vào bảng `registrations` (xem `DATABASE.md`).

### 6.3 Xóa người dùng

**Đường dẫn**: `POST /admin/delete-user/<id>`

**Các bước**:

1. Trên Dashboard, tìm user cần xóa.
2. Click nút **Xóa**.
3. Xác nhận tại hộp thoại hiện ra.
4. User bị xóa khỏi bảng `registrations`.

**Cảnh báo**: Thao tác này **không thể hoàn tác**. Cân nhắc kỹ trước khi xóa.

## 7. Kiểm duyệt báo cáo lừa đảo (tóm tắt)

> **Chi tiết đầy đủ**: Xem [SOP_BAO_CAO.md](SOP_BAO_CAO.md)

### 7.1 Các đường dẫn

| Thao tác | Đường dẫn | Phương thức |
|----------|-----------|-------------|
| Xem danh sách báo cáo | `/admin/scammer-reports` | GET |
| Phê duyệt | `/admin/approve-report/<id>` | POST |
| Từ chối | `/admin/reject-report/<id>` | POST |

### 7.2 Quy trình tóm tắt

1. Truy cập `/admin/scammer-reports`.
2. Lọc báo cáo theo trạng thái: Tất cả / Chờ duyệt / Đã duyệt / Đã từ chối.
3. Rà soát thông tin đối tượng và bằng chứng.
4. Chọn **Phê duyệt** hoặc **Từ chối**.
5. Xem quy trình chi tiết tại `SOP_BAO_CAO.md`.

**Models liên quan**: bảng `scam_reports`, `scammer_reports` (xem `DATABASE.md`).

## 8. Xuất dữ liệu (Export)

### 8.1 Thông tin chung

| Thông tin | Chi tiết |
|-----------|----------|
| URL | `/admin/export-dataset` |
| Phương thức | GET (xem form) / POST (thực hiện export) |
| Output | File CSV |
| Models | Bảng `scam_reports` (xem `DATABASE.md`) |

### 8.2 Hai chế độ export

1. **Tóm tắt (mặc định)**: Xuất dữ liệu đã redact thông tin nhạy cảm. Không yêu cầu lý do.
2. **Đầy đủ**: Xuất toàn bộ dữ liệu bao gồm thông tin nhạy cảm. **Yêu cầu nhập lý do** trước khi export.

### 8.3 Các bước thực hiện

1. Truy cập `/admin/export-dataset`.
2. Xem số lượng báo cáo đã duyệt.
3. Chọn chế độ export:
   - Bản tóm tắt: click **Xuất dữ liệu**.
   - Bản đầy đủ: nhập lý do → click **Xuất dữ liệu đầy đủ**.
4. Tải file CSV.
5. Lưu file tại thư mục nội bộ được kiểm soát truy cập.

### 8.4 Lưu ý bảo mật

- Export đầy đủ được ghi nhận vào **audit logs** (xem Section 9).
- Không chia sẻ file CSV qua kênh công khai.
- Tham chiếu quy tắc bảo mật tại Section 8.3 của `SOP_BAO_CAO.md`.

## 9. Audit Logs

### 9.1 Thông tin chung

| Thông tin | Chi tiết |
|-----------|----------|
| URL | `/admin/sensitive-access-logs` |
| Phương thức | GET |
| Models | Bảng `sensitive_access_logs` (xem `DATABASE.md`) |

### 9.2 Nội dung ghi nhận

Hệ thống tự động ghi nhận:

- **Ai**: Admin nào thực hiện thao tác.
- **Làm gì**: Loại action (view, export, update).
- **Khi nào**: Timestamp.
- **Chi tiết**: Resource được truy cập, lý do (nếu có).

### 9.3 Cảnh báo bất thường

Hệ thống tự động phát hiện access patterns bất thường:

- Export nhiều lần trong thời gian ngắn (ngưỡng: 3 lần).
- View/update vượt ngưỡng bình thường.
- Cảnh báo hiển thị trực tiếp trên trang audit logs.

### 9.4 Sử dụng

1. Truy cập `/admin/sensitive-access-logs`.
2. Xem danh sách logs theo thời gian.
3. Filter theo action type nếu cần.
4. Kiểm tra các cảnh báo bất thường (nếu có).

## 10. Mở khóa admin bị suspend

### 10.1 Khi nào admin bị suspend

Admin có thể bị hệ thống tự động suspend khi phát hiện hành vi bất thường (ví dụ: đăng nhập sai quá nhiều lần liên tiếp).

### 10.2 Thông tin

| Thông tin | Chi tiết |
|-----------|----------|
| URL | `POST /admin/unsuspend` |
| Yêu cầu | Env var `ADMIN_UNSUSPEND_SECRET` |
| Quyền | Không cần admin session — dùng secret key |

### 10.3 Các bước thực hiện

1. Gửi POST request đến `/admin/unsuspend` với `secret` = giá trị của `ADMIN_UNSUSPEND_SECRET`.
2. Nếu secret đúng, hệ thống unsuspend tài khoản admin.
3. Đăng nhập lại bình thường.

**Lưu ý**: Chỉ người có quyền truy cập env var `ADMIN_UNSUSPEND_SECRET` mới có thể thực hiện thao tác này. Secret này được set trên Vercel Dashboard.

## 11. Tài liệu liên quan

- [docs/technical/API.md](../../docs/technical/API.md) — Chi tiết tất cả endpoints admin (section "admin Blueprint")
- [docs/technical/DATABASE.md](../../docs/technical/DATABASE.md) — Schema database: bảng `registrations`, `scam_reports`, `sensitive_access_logs`
- [documents/SOP/SOP_BAO_CAO.md](SOP_BAO_CAO.md) — Quy trình kiểm duyệt báo cáo lừa đảo chi tiết
- [documents/SOP/SOP_VAN_HANH.md](SOP_VAN_HANH.md) — Quy trình vận hành hệ thống (deploy, logs, rollback)
