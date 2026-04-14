# MindGuard v2

## What This Is

MindGuard v2 là nền tảng giáo dục an toàn mạng và phòng chống lừa đảo xây dựng bằng Flask. Hệ thống cung cấp quiz nhận thức, chatbot hỗ trợ, báo cáo đối tượng lừa đảo, và dashboard quản trị để theo dõi dữ liệu. Ứng dụng chạy trên NeonDB PostgreSQL và deploy lên Vercel.

## Core Value

Người dùng có thể học, kiểm tra nhận thức và gửi báo cáo lừa đảo một cách dễ dùng, an toàn, và đáng tin cậy.

## Current Milestone: v1.4 OTP Email Reliability & QA

**Goal:** Triển khai OTP email thật cho luồng xác thực tài khoản, sửa toàn bộ lỗi OTP hiện có, và tăng độ tin cậy bằng test tự động.

**Target features:**

- Tích hợp provider gửi mail OTP chạy ổn định trên Vercel (Google SMTP/App Password hoặc provider API tương thích).
- Thay OTP hardcode `123456` bằng OTP sinh ngẫu nhiên, có expiry và kiểm soát số lần thử.
- Hoàn thiện resend OTP với cooldown và rate-limit phù hợp.
- Sửa lỗi verify/session/UI liên quan OTP trong auth flow.
- Bổ sung test unit + route + integration (mock email) cho luồng tạo tài khoản -> nhận OTP -> xác thực.

## Requirements

### Validated

- ✓ Đăng ký/đăng nhập người dùng qua email và session.
- ✓ Làm quiz và xem kết quả/chứng nhận.
- ✓ Gửi báo cáo lừa đảo kèm bằng chứng.
- ✓ Chatbot hỗ trợ hỏi đáp có fallback an toàn.
- ✓ Dashboard admin cho quản trị báo cáo.
- ✓ Anti-spam đa tín hiệu (IP + cookie + account).
- ✓ Leaderboard có integrity rules.
- ✓ Migration sang NeonDB PostgreSQL + deploy Vercel ổn định.
- ✓ AI safety baseline + trust signals cho Beta.
- ✓ Bộ tài liệu kỹ thuật/SOP v1.3 hoàn chỉnh và đã verify.

### Active

- [ ] OTP được tạo ngẫu nhiên và không còn hardcode trong bất kỳ luồng xác thực nào.
- [ ] Người dùng nhận OTP qua email thật khi đăng ký/xác minh tài khoản trên môi trường production.
- [ ] Luồng resend/verify OTP hoạt động ổn định với expiry, cooldown và rate-limit rõ ràng.
- [ ] Các bug OTP liên quan gửi mail, validate, session và UI được sửa triệt để.
- [ ] Có bộ test tự động bao phủ end-to-end logic OTP từ tạo account đến xác thực.

### Out of Scope

- MFA ngoài email OTP (SMS OTP, authenticator app) — chưa thuộc phạm vi v1.4.
- Refactor toàn bộ hệ thống auth không liên quan OTP — ưu tiên sửa đúng luồng OTP hiện tại.
- Tính năng mới không liên quan OTP (notifications/social/gamification) — để milestone sau.
- Thay đổi deployment platform hoặc DB stack — tiếp tục dùng Vercel + NeonDB hiện tại.

## Context

Dự án đã hoàn thành v1.0 (core platform), v1.1 (PostgreSQL + Vercel), v1.2 (Beta hardening), và v1.3 (tài liệu kỹ thuật/SOP). App đang live trên Vercel với NeonDB PostgreSQL. Luồng OTP hiện tại còn hardcode `123456`, chưa đáp ứng production security và reliability; milestone v1.4 tập trung xử lý OTP email thật, sửa lỗi OTP và bổ sung test để tránh regression.

## Constraints

- **Tech stack**: Flask + NeonDB PostgreSQL + SQLAlchemy + Jinja — không thay đổi stack.
- **Database**: NeonDB PostgreSQL cho cả local và production — không phân tách env.
- **Deployment**: Vercel serverless — cần tối ưu timeout và tránh phụ thuộc filesystem cục bộ.
- **OTP Security**: OTP phải ngẫu nhiên, có expiry, không hardcode/plaintext trong codebase.
- **Email Delivery**: Secrets gửi mail phải lấy từ environment variables, không commit credentials.
- **Testing**: Milestone v1.4 bắt buộc có unit + route tests cho OTP flow để giảm rủi ro hồi quy.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Giữ kiến trúc Flask brownfield, nâng cấp theo từng phase | Giảm rủi ro hồi quy và tận dụng hệ thống đang chạy | ✓ Good |
| Migrate toàn bộ sang NeonDB PostgreSQL + Vercel | Phù hợp serverless production và vận hành thực tế | ✓ Good |
| Ưu tiên hardening trước mở rộng tính năng | Ổn định hệ thống trước khi tăng scope | ✓ Good |
| Docs-only milestone v1.3 | Hoàn thiện nền tảng tài liệu trước handoff/mở rộng | ✓ Good |
| Chuẩn hóa OTP email production trong v1.4 | OTP hardcode không an toàn và không dùng được thực tế | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? -> Move to Out of Scope with reason
2. Requirements validated? -> Move to Validated with phase reference
3. New requirements emerged? -> Add to Active
4. Decisions to log? -> Add to Key Decisions
5. "What This Is" still accurate? -> Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check -> still the right priority?
3. Audit Out of Scope -> reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-14 after milestone v1.4 started (OTP email reliability, OTP bug fixes, and test hardening scope confirmed).* 
