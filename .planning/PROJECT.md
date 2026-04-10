# MindGuard v2

## What This Is

MindGuard v2 la nen tang giao duc an toan mang va phong chong lua dao duoc xay dung bang Flask. He thong cung cap bai quiz nhan thuc, chatbot huong dan, bao cao doi tuong lua dao, va dashboard quan tri de theo doi du lieu. Ung dung su dung NeonDB PostgreSQL va deploy len Vercel de san sang production.

## Core Value

Nguoi dung co the hoc, kiem tra nhan thuc va gui bao cao lua dao mot cach de dung, an toan, va dang tin cay.

## Current Milestone: v1.2 Beta 1 Go-Live (Code Freeze)

**Goal:** Sửa lỗi UI nghiêm trọng, gia cố hạ tầng chống quá tải, đảm bảo an toàn AI, và hoàn thiện tài liệu trước khi ra mắt Beta 1 cho người dân Hà Nội (~10 triệu người dùng tiềm năng).

**Target features:**

- Sửa lỗi UI nghiêm trọng (dropdown "Đăng xuất", hitbox "Hồ sơ", chatbot lưu lịch sử, huy hiệu Certification)
- Rate limiting + WAF rules cho AI chatbot endpoints (chống drain API budget)
- Xác minh logging baseline và stress test tìm ngưỡng CCU
- Banner chính sách quyền riêng tư trên trang chủ
- Điều chỉnh AI prompt bình dân hóa + fallback cứng cho chủ đề nhạy cảm
- Nút "Báo cáo sai / Góp ý" cho Beta

## Requirements

### Validated

- ✓ Dang ky/dang nhap nguoi dung qua email va session — v1.0
- ✓ Lam quiz va xem ket qua/chung nhan — v1.0
- ✓ Gui bao cao lua dao kem bang chung — v1.0
- ✓ Chatbot ho tro hoi dap co fallback — v1.0
- ✓ Quan tri vien co dashboard rieng de quan ly — v1.0
- ✓ Light mode dong bo tren cac trang chinh — v1.0
- ✓ Design tokens thong nhat (mau, font, spacing) — v1.0
- ✓ Quiz 1 cau hoi/trang voi tien do ro rang — v1.0
- ✓ Anti-spam da tin hieu (IP + cookie + account) — v1.0
- ✓ Bang vinh danh voi integrity rules — v1.0
- ✓ SOP bao cao va ML readiness — v1.0

### Active

- [ ] Sửa nút "Đăng xuất" bị chết trong dropdown menu
- [ ] Sửa hitbox quá nhỏ của mục "Hồ sơ" trong menu
- [ ] Sửa chatbot bubble chat không lưu lịch sử giữa các phiên
- [ ] Thiết kế và triển khai huy hiệu "Certification Verify" đúng cách
- [ ] Rate limiting + WAF rules trên endpoint AI chatbot
- [ ] Xác minh logging baseline (request, error, audit logs) hoạt động và lưu trữ an toàn
- [ ] Stress test tìm ngưỡng CCU tối đa cho Beta 1
- [ ] Banner chính sách quyền riêng tư trên trang chủ
- [ ] Điều chỉnh system prompt AI cho ngôn ngữ bình dân
- [ ] Cơ chế fallback cứng cho AI khi gặp chủ đề nhạy cảm (OTP + Hotline Công an Hà Nội)
- [ ] Nút "Báo cáo sai / Góp ý" cho Beta

### Out of Scope

- Dark mode trong v1.2 — ưu tiên sửa lỗi và gia cố, không thêm tính năng
- Tính năng mới (notifications, social, gamification) — CODE FREEZE cho Beta 1
- Auto-scaling/multi-region — v1.2 chỉ cần 1 region ổn định
- Migration tool tự động (Alembic/flask-migrate) — dùng manual scripts theo conventions
- OAuth/2FA — không nằm trong scope Beta 1

## Context

Dự án đã hoàn thành v1.0 (6 phases: Privacy, Anti-Spam, Light Mode, Quiz Flow, Leaderboard, Docs/ML) và v1.1 (3 phases: PostgreSQL migration, seeding, Vercel deployment). App đang live tại mindguard-five.vercel.app trên NeonDB PostgreSQL. Hiện tại đang trong giai đoạn CODE FREEZE chuẩn bị Beta 1 Go-Live trước ngày lễ quốc gia. MindGuard được định vị là ứng dụng AI chatbot phát hiện lừa đảo tài chính công cộng cho người dân Hà Nội (~10 triệu người dùng tiềm năng). Chỉ sửa lỗi, gia cố hạ tầng, và đảm bảo an toàn AI.

## Constraints

- **Tech stack**: Flask + NeonDB PostgreSQL + SQLAlchemy + Jinja — không thay đổi stack
- **Database**: NeonDB PostgreSQL cho cả local và production — không phân tách env
- **Deployment**: Vercel serverless — read-only filesystem, ephemeral function instances
- **Code Freeze**: KHÔNG thêm tính năng mới — chỉ sửa lỗi, gia cố, và an toàn AI
- **Security**: Connection string và credentials phải được bảo vệ trong .env/ — không commit secrets
- **Quy mô**: Phải sẵn sàng cho ~10 triệu người dùng tiềm năng (Beta 1 Hà Nội)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Uu tien light mode va UX quiz lam trung tam v1 | Nhu cau uu tien cao nhat tu nguoi dung la UI/UX | ✓ Good |
| Giu kien truc Flask brownfield, nang cap theo tung pha | Giam rui ro hoi quy va tan dung he thong dang chay | ✓ Good |
| Dua anti-spam (rule tan suat + IP/cookie tracking) vao v1 | Bao ve chat luong du lieu bao cao va han che gian lan | ✓ Good |
| Migrate toàn bộ sang NeonDB PostgreSQL cho v1.1 | SQLite không phù hợp Vercel serverless (ephemeral /tmp), NeonDB đã có sẵn | ✓ Good |
| NeonDB cho cả local và production | Đơn giản hóa config, tránh sqlite/postgres incompatibility | ✓ Good |
| Postgres trước, Vercel fix sau | DB ổn định là tiên quyết để debug deployment | ✓ Good |
| Code Freeze cho v1.2 Beta 1 | Ổn định trước go-live, không thêm tính năng mới | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):

1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):

1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-10 after milestone v1.2 initialization*
