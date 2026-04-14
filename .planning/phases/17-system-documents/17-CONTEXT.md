# Phase 17 — Smart Discuss Context

**Phase:** 17-system-documents (ARCHITECTURE.md + API.md)
**Date:** 2025-07-15
**Mode:** Autonomous (recommended answers accepted)

---

## Grey Areas Identified

### GA-1: ARCHITECTURE.md — Mức độ rewrite

Hiện tại ARCHITECTURE.md (280 dòng) viết cho stack cũ (SQLite, localhost, ngrok). Cần cập nhật cho NeonDB PostgreSQL + Vercel serverless.

**Question:** Rewrite toàn bộ hay chỉ cập nhật các section lỗi thời?

### GA-2: ARCHITECTURE.md — Mermaid diagrams

Success criteria yêu cầu ít nhất 2 Mermaid diagrams (system overview, request flow).

**Question:** Dùng diagram types nào cho mỗi? Thêm diagram thứ 3 (deployment) hay chỉ đủ 2?

### GA-3: API.md — Format route listing

Success criteria yêu cầu phân loại rõ HTML page routes vs JSON API endpoints.

**Question:** Liệt kê theo blueprint (mỗi blueprint 1 section) hay theo loại (HTML section + JSON section)?

### GA-4: API.md — Mức chi tiết response

**Question:** Mô tả response chi tiết (schema JSON đầy đủ) hay chỉ tóm tắt (status code + mô tả ngắn)?

---

## Decisions

### D-01: Rewrite ARCHITECTURE.md cho stack hiện tại
**Decision:** Rewrite toàn bộ các section liên quan (Tech Stack, Infrastructure, Data Flow, Known Constraints, Performance) để phản ánh đúng NeonDB + Vercel. Giữ lại cấu trúc section và các phần vẫn đúng (Frontend Architecture, Security Architecture phần lớn vẫn đúng). Xóa placeholder sections (Design System tokens chưa điền).
**Rationale:** Tài liệu cũ có thông tin sai (SQLite, localhost only, ngrok) — sửa từng dòng tốn nhiều hơn rewrite có chọn lọc.

### D-02: 2 Mermaid diagrams — flowchart + sequence
**Decision:** (1) System Overview — `flowchart TD` thể hiện Browser → Vercel → Flask → Services/DB/External. (2) Request Flow — `sequenceDiagram` thể hiện lifecycle 1 request từ browser qua Vercel Function → Flask → DB → response. Không thêm diagram thứ 3.
**Rationale:** 2 diagrams đủ cho success criteria. Flowchart cho big picture, sequence cho chi tiết runtime.

### D-03: API.md liệt kê theo blueprint, phân loại HTML vs JSON trong mỗi section
**Decision:** Tổ chức API.md theo 8 blueprints (giống cấu trúc code). Mỗi blueprint section có 2 sub-groups: "Page Routes (HTML)" và "API Endpoints (JSON)" nếu có cả hai loại. Đầu tài liệu có bảng tổng hợp (summary table) liệt kê tất cả routes.
**Rationale:** Theo blueprint giữ trực quan 1-1 với codebase. Sub-groups giải quyết success criteria phân loại HTML vs JSON.

### D-04: Response mô tả ngắn gọn, không full schema
**Decision:** Mỗi route/endpoint listing gồm: Method, Path, Auth requirement, Response type (HTML/JSON), Mô tả ngắn 1 dòng tiếng Việt. Cho JSON endpoints: thêm key fields trong response (không full schema). Cho HTML page routes: thêm template name.
**Rationale:** MindGuard không có public API — routes chủ yếu nội bộ. Full schema quá chi tiết cho docs-only milestone, dễ lỗi thời.

### D-05: Cross-references giữa 3 tài liệu
**Decision:** ARCHITECTURE.md link sang DATABASE.md và API.md ở các section liên quan. API.md link sang DATABASE.md khi nói về models. Dùng relative Markdown links (`[DATABASE.md](DATABASE.md)`). Cuối mỗi tài liệu có section "Xem thêm" (See Also) liệt kê các file liên quan.
**Rationale:** Success criteria #4 yêu cầu cross-references nhất quán.

### D-06: Prose viết tiếng Việt theo CONVENTIONS.md
**Decision:** Tuân thủ doc conventions (Phase 15): prose tiếng Việt, thuật ngữ kỹ thuật giữ tiếng Anh, dùng glossary terms, redaction rules cho credentials.
**Rationale:** Nhất quán với DATABASE.md và DECISIONS.md đã viết ở Phase 16.

---

## Deferred Ideas

- Swagger/OpenAPI spec generation — quá phức tạp cho docs-only milestone
- Interactive API playground — không trong scope
- Sequence diagrams cho mỗi major flow (auth, quiz, report, chatbot) — chỉ cần 1 generic request flow

---

## Agent's Discretion

- Chọn chi tiết Mermaid diagram nodes/labels cụ thể
- Quyết định thứ tự sections trong ARCHITECTURE.md (có thể sắp xếp lại)
- Quyết định format bảng route listing trong API.md (Markdown table vs list)
