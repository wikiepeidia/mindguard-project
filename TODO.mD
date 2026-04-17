# TODO - SMTP miễn phí cho Phase 26

## Mục tiêu hiện tại

- Chạy OTP bằng SMTP miễn phí, không mua domain, không trả tiền cho provider mới.
- Dùng Gmail App Password làm đường SMTP chính cho cutover Phase 26.
- Sau khi set env đúng, app phải chạy với `EMAIL_PROVIDER=smtp` trên Vercel.

## Cách setup SMTP miễn phí nhanh nhất

### Option dùng ngay: Gmail App Password

- Miễn phí.
- Không cần custom domain.
- Hợp với app hiện tại vì form đăng ký đã giới hạn email nhận là `@gmail.com`.
- Nên tạo riêng một Gmail cho MindGuard, ví dụ `mindguard.smtp@gmail.com`, đừng dùng email cá nhân chính.

## Bước 1: Tạo Gmail App Password

1. Tạo hoặc đăng nhập Gmail sẽ dùng làm email gửi OTP.
2. Bật 2-Step Verification trong tài khoản Google.
3. Vào Google Account > Security > App passwords.
4. Tạo app password mới cho `Mail`.
5. Google sẽ trả về chuỗi 16 ký tự.
6. Lưu chuỗi đó, đây là giá trị cho `SMTP_PASSWORD`.

## Bước 2: Set env vars trên Vercel

Set các biến sau trong project Vercel:

```text
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=your-16-char-app-password
SMTP_USE_TLS=true
SMTP_USE_SSL=false
SMTP_FROM_EMAIL
```

Ghi chú:

- Port `587` + `SMTP_USE_TLS=true` là config nên dùng trước.
- Không bật cả `SMTP_USE_TLS=true` và `SMTP_USE_SSL=true` cùng lúc.
- `SMTP_FROM_EMAIL` nên trùng với `SMTP_USERNAME` cho Gmail để tránh bị reject.

## Bước 3: Local fallback nếu muốn test local trước

Tạo file `.env/SMTP.json` với nội dung:

```json
{
 "EMAIL_PROVIDER": "smtp",
 "SMTP_HOST": "smtp.gmail.com",
 "SMTP_PORT": 587,
 "SMTP_USERNAME": "mail@gmail.com",
 "SMTP_PASSWORD": "your-16-char-app-password",
 "SMTP_USE_TLS": true,
 "SMTP_USE_SSL": false,
 "SMTP_FROM_EMAIL": "mail@gmail.com"
}
```

Prod vẫn phải ưu tiên Vercel env vars. JSON này chỉ để test local nhanh.

## Readiness / lỗi cần hiểu

App hiện đã phân loại lỗi SMTP theo các category dưới đây:

- `misconfigured`: thiếu env hoặc config mâu thuẫn.
  - Cần kiểm tra `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`.
  - Cũng sẽ dính nếu bật cả TLS và SSL cùng lúc.
- `provider_rejected`: Gmail từ chối đăng nhập hoặc từ chối người gửi.
  - Thường là app password sai, 2FA chưa bật, hoặc `SMTP_FROM_EMAIL` không khớp account gửi.
- `timeout`: Gmail SMTP phản hồi quá chậm hoặc network bị nghẽn tạm thời.
  - Thử lại sau trước khi đổi config.
- `network_error`: lỗi mạng/outbound từ runtime.
  - Kiểm tra lại deploy, network, hoặc provider có đang chặn kết nối không.

## Checklist cutover Phase 26

- [ ] Có Gmail riêng cho MindGuard.
- [ ] Đã bật 2FA.
- [ ] Đã tạo App Password mới.
- [ ] Đã set đủ env vars SMTP trên Vercel.
- [ ] `EMAIL_PROVIDER=smtp` đã được set trên Vercel.
- [ ] Redeploy sau khi set env.
- [ ] Test đăng ký bằng 1 Gmail nhận OTP thật.
- [ ] Test resend OTP trên `/verify-otp`.

## Nếu Gmail chặn hoặc không muốn dùng Gmail chính

- Tạo 1 Gmail mới chỉ để gửi OTP.
- Không dùng mật khẩu thường, chỉ dùng App Password.
- Không gửi volume lớn bằng account này. Với scope hiện tại của MindGuard, Gmail free là đủ để unblock.

## Ghi nhớ cho Phase 27

- Cần smoke test thật trên Vercel sau khi set env xong.
- Cần chụp evidence: register thành công, nhận mail, resend thành công.
- Nếu log báo `misconfigured`, sửa env trước khi test lại.
