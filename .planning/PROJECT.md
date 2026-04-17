# MindGuard v2

## What This Is

MindGuard v2 là nền tảng giáo dục an toàn mạng và phòng chống lừa đảo xây dựng bằng Flask. Hệ thống cung cấp quiz nhận thức, chatbot hỗ trợ, báo cáo đối tượng lừa đảo, và dashboard quản trị để theo dõi dữ liệu. Ứng dụng chạy trên NeonDB PostgreSQL và deploy lên Vercel.

## Core Value

Người dùng có thể học, kiểm tra nhận thức và gửi báo cáo lừa đảo một cách dễ dùng, an toàn, và đáng tin cậy.

## Current Milestone: v1.5 Vercel-Compatible OTP Mail Pivot

**Goal:** Loại bỏ phụ thuộc Resend yêu cầu custom domain và chuyển OTP sang đường gửi mail generic SMTP/Gmail App Password chạy được trên Vercel.

**Target features:**

- Chuyển provider OTP production sang generic SMTP không yêu cầu custom sending domain.
- Hỗ trợ Gmail App Password và generic SMTP thông qua environment variables trên Vercel.
- Giữ nguyên luồng register -> verify -> resend, session, cooldown, và abuse guardrails khi thay backend gửi mail.
- Bổ sung regression test và production smoke checklist cho cutover SMTP.

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
- ✓ OTP được tạo ngẫu nhiên và không còn hardcode trong bất kỳ luồng xác thực nào.
- ✓ Luồng OTP email production đã có adapter gửi mail thật và fail-closed khi provider/runtime hợp lệ.
- ✓ Luồng resend/verify OTP hoạt động ổn định với expiry, cooldown và rate-limit rõ ràng.
- ✓ Các bug OTP liên quan gửi mail, validate, session và UI đã được khóa bằng regression test và hành vi ổn định.
- ✓ Có bộ test tự động bao phủ helper, route và integration cho các nhánh OTP quan trọng.
- ✓ Generic SMTP provider core cho OTP đã được thêm qua Flask-Mail mà không phụ thuộc custom sending domain.
- ✓ OTP mail giờ phân biệt rõ `misconfigured`, `provider_rejected`, `timeout`, và `network_error` cho nhánh SMTP.
- ✓ Register/resend auth flow giờ chạy đúng qua `EMAIL_PROVIDER=smtp` mà không làm đổi UX, session contract, hay guardrails OTP.
- ✓ Repo đã có runbook Gmail App Password / generic SMTP miễn phí trong `TODO.mD` cho operator.
- ✓ Route/integration test giờ khóa các nhánh SMTP success/failure cho register và resend.

### Active

- [ ] Thu thập production smoke evidence trên Vercel với mailbox thật để hoàn tất go-live SMTP.

### Out of Scope

- Mua/verify custom domain cho Resend — milestone này chọn hướng không phụ thuộc domain gửi mail riêng.
- Failover đa provider, retry queue nền, hoặc manual admin assist path — ưu tiên cắt sang một provider chạy được trước.
- Mở rộng email khác ngoài OTP (newsletter, notifications, password reset redesign) — chưa thuộc scope v1.5.
- Refactor toàn bộ hệ thống auth không liên quan mail provider — giữ nguyên luồng OTP hiện tại.

## Context

Dự án đã hoàn thành v1.0 (core platform), v1.1 (PostgreSQL + Vercel), v1.2 (Beta hardening), v1.3 (tài liệu kỹ thuật/SOP), và v1.4 (OTP reliability + QA). App đang live trên Vercel với NeonDB PostgreSQL. Sau khi kiểm tra production, team xác nhận Resend yêu cầu custom sending domain và `*.vercel.app` không đủ để verify domain gửi mail, nên milestone v1.5 tập trung pivot OTP delivery sang generic SMTP/Gmail App Password để tiếp tục dùng Vercel mà không cần mua domain mới trước mắt.

## Constraints

- **Tech stack**: Flask + NeonDB PostgreSQL + SQLAlchemy + Jinja — không đổi stack, ưu tiên tái sử dụng `Flask-Mail` đã có.
- **Deployment**: Vercel serverless — provider mail phải chạy qua environment variables và outbound network mặc định của Vercel.
- **Mail provider**: Không giả định có custom sending domain; giải pháp phải chạy được khi team chỉ có mailbox account và `*.vercel.app`.
- **Secrets**: SMTP username/password/app password chỉ lấy từ environment variables, không commit credentials.
- **OTP Security**: OTP lifecycle, resend policy, cooldown, và guardrails hiện tại không được suy giảm khi đổi provider.
- **Testing**: Cutover SMTP phải có unit + route + integration coverage và evidence production smoke.

## Key Decisions

| Decision | Rationale | Outcome |
| -------- | --------- | ------- |
| Giữ kiến trúc Flask brownfield, nâng cấp theo từng phase | Giảm rủi ro hồi quy và tận dụng hệ thống đang chạy | ✓ Good |
| Migrate toàn bộ sang NeonDB PostgreSQL + Vercel | Phù hợp serverless production và vận hành thực tế | ✓ Good |
| Ưu tiên hardening trước mở rộng tính năng | Ổn định hệ thống trước khi tăng scope | ✓ Good |
| Docs-only milestone v1.3 | Hoàn thiện nền tảng tài liệu trước handoff/mở rộng | ✓ Good |
| Chuẩn hóa OTP email production trong v1.4 | OTP hardcode không an toàn và không dùng được thực tế | ✓ Good |
| Pivot OTP khỏi Resend sang generic SMTP/Gmail ở v1.5 | Team không có custom sending domain; `vercel.app` không verify được với Resend | ✓ Good |

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
*Last updated: 2026-04-17 after Phase 26 completed the SMTP auth-flow cutover, route diagnostics, and operator runbook for the v1.5 pivot.*
