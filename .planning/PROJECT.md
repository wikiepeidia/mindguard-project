# MindGuard v2

## What This Is

MindGuard v2 la nen tang giao duc an toan mang va phong chong lua dao duoc xay dung bang Flask. He thong cung cap bai quiz nhan thuc, chatbot huong dan, bao cao doi tuong lua dao, va dashboard quan tri de theo doi du lieu. Ung dung su dung NeonDB PostgreSQL va deploy len Vercel de san sang production.

## Core Value

Nguoi dung co the hoc, kiem tra nhan thuc va gui bao cao lua dao mot cach de dung, an toan, va dang tin cay.

## Current Milestone: v1.3 Hoàn thiện Tài liệu Kỹ thuật & SOP v1

**Goal:** Cập nhật toàn bộ SOP và tài liệu kỹ thuật dựa trên codebase hiện tại để phục vụ handoff và onboarding team members.

**Target features:**

- Cập nhật SOP_BAO_CAO.md cho đầy đủ theo codebase mới
- Viết SOP vận hành hệ thống (deploy Vercel, monitoring, incident response)
- Viết SOP quản trị viên (admin dashboard, moderation workflow)
- Cập nhật ARCHITECTURE.md cho NeonDB PostgreSQL + Vercel serverless
- Document tất cả API endpoints trong API.md
- Document database schema thực tế trong DATABASE.md
- Bổ sung ADR cho NeonDB migration, Vercel deployment, AI safety decisions

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
- ✓ .env.example với placeholder values, không chứa secrets — v1.3 Phase 15
- ✓ Quy tắc viết tài liệu (ngôn ngữ, glossary, redaction) — v1.3 Phase 15
- ✓ Document database schema thực tế trong DATABASE.md — v1.3 Phase 16
- ✓ Bổ sung ADR cho NeonDB migration — v1.3 Phase 16
- ✓ Bổ sung ADR cho Vercel deployment — v1.3 Phase 16
- ✓ Bổ sung ADR cho AI safety decisions — v1.3 Phase 16
- ✓ Bổ sung ADR cho rate limiting — v1.3 Phase 16

### Active

- [ ] Cập nhật SOP_BAO_CAO.md cho đầy đủ theo codebase mới
- [ ] Viết SOP vận hành hệ thống (deploy Vercel, monitoring, incident response)
- [ ] Viết SOP quản trị viên (admin dashboard, moderation workflow)
- [ ] Cập nhật ARCHITECTURE.md cho NeonDB PostgreSQL + Vercel serverless
- [ ] Document tất cả API endpoints trong API.md

### Out of Scope

- Dark mode — ưu tiên tài liệu, không thêm tính năng mới
- Tính năng mới (notifications, social, gamification) — milestone tài liệu, không code
- Auto-scaling/multi-region — không nằm trong scope v1.3
- Migration tool tự động (Alembic/flask-migrate) — dùng manual scripts theo conventions
- Tài liệu tiếng Anh — v1.3 chỉ viết tiếng Việt, song ngữ về sau

## Context

Dự án đã hoàn thành v1.0 (6 phases: Privacy, Anti-Spam, Light Mode, Quiz Flow, Leaderboard, Docs/ML), v1.1 (3 phases: PostgreSQL migration, seeding, Vercel deployment), và v1.2 (5 phases: Infrastructure hardening, UI fixes, AI safety, Trust signals, Stress test — Beta 1 approved). App đang live tại mindguard-five.vercel.app trên NeonDB PostgreSQL. Hiện tại cần hoàn thiện tài liệu kỹ thuật và SOP dựa trên codebase hiện tại để phục vụ handoff và onboarding cho team members.

## Constraints

- **Tech stack**: Flask + NeonDB PostgreSQL + SQLAlchemy + Jinja — không thay đổi stack
- **Database**: NeonDB PostgreSQL cho cả local và production — không phân tách env
- **Deployment**: Vercel serverless — read-only filesystem, ephemeral function instances
- **Docs Only**: Milestone này chỉ viết/cập nhật tài liệu — không thay đổi code
- **Security**: Connection string và credentials phải được bảo vệ trong .env/ — không commit secrets
- **Ngôn ngữ**: Tất cả tài liệu viết bằng tiếng Việt

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Uu tien light mode va UX quiz lam trung tam v1 | Nhu cau uu tien cao nhat tu nguoi dung la UI/UX | ✓ Good |
| Giu kien truc Flask brownfield, nang cap theo tung pha | Giam rui ro hoi quy va tan dung he thong dang chay | ✓ Good |
| Dua anti-spam (rule tan suat + IP/cookie tracking) vao v1 | Bao ve chat luong du lieu bao cao va han che gian lan | ✓ Good |
| Migrate toàn bộ sang NeonDB PostgreSQL cho v1.1 | SQLite không phù hợp Vercel serverless (ephemeral /tmp), NeonDB đã có sẵn | ✓ Good |
| NeonDB cho cả local và production | Đơn giản hóa config, tránh sqlite/postgres incompatibility | ✓ Good |
| Postgres trước, Vercel fix sau | DB ổn định là tiên quyết để debug deployment | ✓ Good |
| Code Freeze cho v1.2 Beta 1 | Ổn định trước go-live, không thêm tính năng mới | ✓ Good |
| Docs-only milestone v1.3 | Hoàn thiện tài liệu trước khi mở rộng tính năng | — Pending |

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
*Last updated: 2026-04-14 after Phase 16 complete (Foundation Documents — DATABASE.md + ADRs)*
