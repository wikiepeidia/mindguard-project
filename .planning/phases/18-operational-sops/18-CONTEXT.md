# Phase 18 — Smart Discuss Context

**Phase:** 18-operational-sops
**Date:** 2025-07-15
**Mode:** Autonomous (recommended answers accepted)

---

## Grey Areas Identified

### GA-1: SOP_BAO_CAO.md — Mức độ cập nhật

SOP hiện tại (212 dòng) chất lượng tốt. Cần cập nhật routes cho đúng prefix (`/admin/approve-report/`, `/admin/export-dataset`) và references cho NeonDB thay SQLite.

**Decision:** Cập nhật có chọn lọc (routes, database references), giữ nguyên nội dung quy trình vì vẫn chính xác.

### GA-2: SOP Vận hành — Nơi đặt file

**Decision:** Tạo file mới `documents/SOP/SOP_VAN_HANH.md` — cùng thư mục với SOP_BAO_CAO.md.

### GA-3: SOP Quản trị viên — Nơi đặt file

**Decision:** Tạo file mới `documents/SOP/SOP_QUAN_TRI.md` — cùng thư mục với SOP_BAO_CAO.md.

### GA-4: SOP Vận hành — Scope nội dung

**Decision:** Bao gồm: deploy Vercel (qua git push, Vercel Dashboard), xem logs (Vercel Functions Logs), rollback deployment (Vercel Dashboard), xử lý sự cố thường gặp (cold start, DB connection, rate limit). Cross-ref đến API.md và DATABASE.md.

### GA-5: SOP Quản trị viên — Scope nội dung

**Decision:** Bao gồm: đăng nhập admin (`/admin/login`), dashboard overview, duyệt/từ chối báo cáo, quản lý users (create, edit, delete), export data, xem audit logs. Không lặp lại chi tiết quy trình báo cáo đã có trong SOP_BAO_CAO.md — chỉ tham chiếu.

---

## Decisions

### D-01: Cập nhật có chọn lọc SOP_BAO_CAO.md
**Decision:** Chỉ sửa routes (prefix `/admin/`), database references (PostgreSQL thay SQLite), thêm cross-references đến API.md và DATABASE.md. Giữ nguyên nội dung quy trình.
**Rationale:** Quy trình xử lý báo cáo vẫn chính xác, chỉ có technical references cần cập nhật.

### D-02: SOP_VAN_HANH.md — Hướng dẫn vận hành hệ thống
**Decision:** Document: (1) Deploy qua git push + Vercel auto-deploy, (2) Xem logs Vercel Dashboard, (3) Rollback deployment, (4) Troubleshooting thường gặp.
**Rationale:** Team member mới cần biết cách deploy, xem logs, và xử lý sự cố cơ bản.

### D-03: SOP_QUAN_TRI.md — Hướng dẫn quản trị viên
**Decision:** Document: (1) Đăng nhập admin, (2) Dashboard overview, (3) Quản lý users, (4) Export data, (5) Audit logs. Tham chiếu SOP_BAO_CAO.md cho quy trình kiểm duyệt.
**Rationale:** Tách biệt với SOP báo cáo, tập trung vào admin operations.

### D-04: Cross-references trong 3 SOPs
**Decision:** Mỗi SOP có section "Tài liệu liên quan" cuối file linking đến API.md, DATABASE.md và các SOP khác.
**Rationale:** Success criteria #4 yêu cầu cross-references đúng.

### D-05: Prose tiếng Việt theo CONVENTIONS.md
**Decision:** Tuân thủ doc conventions: prose tiếng Việt, thuật ngữ kỹ thuật giữ tiếng Anh.
**Rationale:** Nhất quán với toàn bộ tài liệu đã viết.

---

## Deferred Ideas

- Video tutorials cho admin workflow — quá phức tạp
- Automated health checks — không trong scope docs-only milestone

---

## Agent's Discretion

- Chi tiết các bước troubleshooting
- Format sections trong SOP mới
- Mức độ chi tiết screenshots placeholder
