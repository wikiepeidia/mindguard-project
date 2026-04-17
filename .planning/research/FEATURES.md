# Feature Research — v1.5 SMTP Pivot

## Table stakes

- Generic SMTP OTP sending on Vercel.
- Gmail App Password support.
- Fail-closed behavior on delivery errors.
- Clear operator config contract.
- Regression coverage for register/resend SMTP paths.

## Differentiators

- Provider-neutral SMTP config instead of Gmail-only special cases.
- Readiness diagnostics that separate misconfiguration from transient send errors.
- Production smoke evidence captured as part of milestone closeout.

## Anti-features for this milestone

- Resend domain verification work.
- Backup-provider orchestration.
- Broader email platform work outside OTP.# Feature Landscape

**Domain:** v1.4 OTP Email Reliability & QA
**Researched:** 2026-04-14
**Confidence:** HIGH (đối chiếu trực tiếp từ PROJECT scope, auth routes/templates, static JS, và test hiện có)

## Table Stakes (must-have in v1.4)

| Feature | User behavior expectation | Complexity | Dependency hints | Suggested REQ-ID category labels |
| --- | --- | --- | --- | --- |
| OTP ngẫu nhiên + verify an toàn (không còn hardcode) | "Mỗi lần đăng ký tôi nhận OTP mới; mã cũ không tái dùng; hệ thống không chấp nhận mã mặc định/demo." | M | `routes/auth.py`: bỏ `session.get('otp_code', '123456')`; tạo helper sinh OTP; so khớp an toàn; xóa OTP sau verify thành công. | `OTPSEC` (ví dụ: `OTPSEC-01..`) |
| Gửi OTP email thật trên production | "Sau khi bấm đăng ký tôi nhận email OTP thật trong thời gian ngắn, không còn thông báo demo." | M | `config.py`: bổ sung `MAIL_SERVER/PORT/USE_TLS/USERNAME/PASSWORD/DEFAULT_SENDER`; dùng `mail` từ `extensions.py`; tạo service gửi mail OTP; map secrets trong Vercel env. | `OTPMAIL` |
| Chính sách OTP đầy đủ: expiry + max attempts + single-use | "OTP hết hạn rõ ràng; nhập sai nhiều lần thì bị chặn tạm; OTP dùng xong không dùng lại được." | M | `routes/auth.py`: thêm metadata OTP (`issued_at`, `expires_at`, `attempts`); rule lockout; flash message tiếng Việt rõ ràng; cleanup session đúng lúc. | `OTPPOL` |
| Resend OTP với cooldown + rate-limit | "Nút gửi lại có đếm ngược, chỉ cho gửi lại khi đủ thời gian, không bị spam." | M | Thêm route resend (vd `/resend-otp`) + `@limiter.limit`; cập nhật `templates/verify_otp.html`; thêm JS timer riêng (hiện `static/js/**` chưa có OTP script). | `OTPRES` |
| Session contract ổn định giữa register -> verify | "Trang verify luôn hiển thị đúng email và không lỗi khi refresh/tab mới; session hết hạn thì quay lại đăng ký." | S | Đồng bộ key session (hiện template dùng `pending_verification_email` nhưng route set `pending_registration`); chuẩn hóa 1 nguồn dữ liệu email pending. | `OTPSES` |
| OTP UI reliability (không lộ demo, validate input 6 chữ số, feedback rõ) | "Tôi nhập OTP dễ dàng, lỗi dễ hiểu, không thấy text demo `123456`, và thông báo tự ẩn hợp lý." | S | `templates/verify_otp.html` + `templates/register.html`: bỏ demo text; chuẩn hóa input pattern; tận dụng auto-dismiss trong `static/js/base.js`; xử lý TODO OTP dismiss còn mở. | `OTPUI` |
| Bộ test tự động bao phủ OTP flow (unit + route + integration mock email) | "Các lỗi resend/expiry/session không tái phát sau deploy." | M | `tests/test_csrf_and_routes.py` đang hardcode `123456`; cần refactor test để mock OTP generator/mail sender; bổ sung case expiry, resend cooldown, lockout, session timeout. | `OTPQA` |

## Differentiators (nice-to-have, ưu tiên v1.5+)

| Feature | User behavior expectation | Complexity | Dependency hints | Suggested REQ-ID category labels |
| --- | --- | --- | --- | --- |
| Provider failover (SMTP chính + fallback provider API) | "Ngay cả khi provider chính lỗi, OTP vẫn được gửi ổn định." | L | Cần abstraction mail provider + retry policy + health checks; chưa cần cho v1.4 nếu provider đơn ổn định. | `OTPREL` |
| OTP observability dashboard (delivery latency, fail rate, resend abuse) | "Đội vận hành phát hiện sớm OTP lỗi trước khi người dùng phản ánh." | M | Cần structured logs/events + dashboard admin hoặc query page; phụ thuộc logging chuẩn hóa. | `OTPOBS` |
| Tách OTP thành service dùng chung cho đăng ký + quên mật khẩu | "Trải nghiệm OTP thống nhất trên mọi luồng tài khoản." | M | Liên quan PRD FR-003 (password reset OTP); nên làm sau khi v1.4 ổn định để tránh mở rộng scope sớm. | `OTPSVC` |
| UX nâng cao OTP input (6 ô tách, paste full-code, tự focus) | "Nhập OTP nhanh hơn trên mobile và desktop." | S | Cần JS riêng cho OTP input + accessibility pass; không bắt buộc để đạt reliability. | `OTPUX+` |

## Anti-features (tránh làm trong v1.4)

| Feature to avoid now | User behavior expectation | Complexity | Dependency hints | Suggested REQ-ID category labels |
| --- | --- | --- | --- | --- |
| Mở rộng MFA ngoài email OTP (SMS/TOTP/Auth app) | Người dùng hiện chỉ cần email OTP chạy ổn định; thêm MFA lúc này dễ rối UX. | L | Thêm provider, recovery flow, migration account, test matrix lớn; trái out-of-scope trong PROJECT.md. | `OTP2FA` (defer) |
| Refactor toàn bộ auth system không liên quan OTP | Người dùng cần fix luồng hiện tại, không cần đổi toàn bộ kiến trúc auth. | L | Chạm nhiều route/session/model, tăng risk regression; đi ngược mục tiêu milestone sửa đúng OTP flow. | `AUTHREF` (defer) |
| Thêm Celery/Redis queue chỉ để gửi OTP ở v1.4 | Người dùng cần OTP ổn định, không cần hạ tầng phức tạp mới. | L | Vercel serverless không thuận persistent worker; tăng vận hành và secret footprint. | `OTPINFRA` (avoid-now) |
| Lưu/hiển thị OTP dạng plaintext (UI, log, flash, test fixture production-like) | Người dùng kỳ vọng OTP là bí mật tuyệt đối. | S (làm sai thì dễ) | Hiện còn demo text trong route/template; phải loại bỏ hoàn toàn khỏi UI/log và kiểm soát test data. | `OTPSEC` (must-enforce) |
| E2E test phụ thuộc inbox thật trong CI | Người dùng kỳ vọng release ổn định; test flakey làm giảm độ tin cậy release. | M | Dễ fail do quota/network/provider; nên dùng mocked mail backend + deterministic integration tests trước. | `OTPQA` (guardrail) |

## Dependency sequencing hints (đề xuất)

1. `OTPSEC` + `OTPMAIL`: tạo OTP thật và gửi email thật trước.
2. `OTPPOL` + `OTPSES`: đóng rule expiry/attempt/session contract.
3. `OTPRES` + `OTPUI`: hoàn thiện resend UX và thông báo rõ ràng.
4. `OTPQA`: chốt test tự động sau khi behavior ổn định.

## v1.4 feature shortlist

1. `OTPSEC`: bỏ hardcode OTP, sinh OTP ngẫu nhiên, verify an toàn, single-use.
2. `OTPMAIL`: gửi OTP email thật trên production + xử lý lỗi gửi rõ ràng.
3. `OTPPOL`: expiry, attempt limit, lockout ngắn hạn để chống brute force.
4. `OTPRES`: resend OTP có cooldown/rate-limit và countdown UX.
5. `OTPSES`: thống nhất session keys, fix hiển thị email pending và timeout redirect.
6. `OTPUI`: bỏ toàn bộ demo OTP text, chuẩn hóa nhập OTP và thông báo.
7. `OTPQA`: bổ sung unit/route/integration tests (mock email) cho toàn flow register -> receive -> verify -> session.
