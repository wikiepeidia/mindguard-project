# Phase 16: Foundation Documents — Context

**Gathered:** 2026-04-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Các quyết định kiến trúc được ghi nhận chính thức và schema database được document đầy đủ để làm nền tảng tham chiếu cho mọi tài liệu sau. Cập nhật DECISIONS.md (thêm ADR-002 đến ADR-005) và viết lại DATABASE.md từ models.py thực tế.

</domain>

<decisions>
## Implementation Decisions

### DATABASE.md Organization

- D-01: Nhóm bảng theo domain (Auth, Quiz, Scammer, Chatbot, Anti-Spam) — phản ánh đúng mental model của codebase
- D-02: Chỉ document schema hiện tại, không ghi migration history (migration scripts nằm riêng trong database/)
- D-03: Dùng một Mermaid erDiagram duy nhất cho tất cả 14 bảng — GitHub render được
- D-04: Không ghi seed data notes — DATABASE.md tập trung vào schema

### ADR Content & Format

- D-05: Theo format ADR-001 đã có (Context / Options Considered / Decision / Consequences) để nhất quán
- D-06: Thêm note vào ADR-001: "Partially superseded by ADR-002" cho quyết định SQLite→PostgreSQL
- D-07: ADR body viết bằng tiếng Anh — theo tiền lệ ADR-001 và bản chất tài liệu kỹ thuật tham chiếu
- D-08: Minimal code references trong ADR — chỉ reference file paths, không copy code blocks

### The Agent's Discretion

- Thứ tự cột trong bảng schema (id → foreign keys → data → metadata → timestamps)
- Mô tả constraints và indexes khi có trong models.py

</decisions>

<code_context>

## Existing Code Insights

### Reusable Assets

- `models/models.py`: 14 SQLAlchemy models — source of truth cho DATABASE.md
- `docs/technical/DECISIONS.md`: ADR-001 đã có, template cho ADRs mới ở cuối file
- `docs/technical/DATABASE.md`: File template placeholder, cần viết lại hoàn toàn
- `docs/technical/CONVENTIONS.md`: Quy ước ngôn ngữ từ Phase 15

### Established Patterns

- ADR format: Michael Nygard style (Context, Options Considered, Decision, Consequences)
- DECISIONS.md có Decision Index table ở đầu
- Metadata comment block ở đầu mỗi file docs/technical/

### Integration Points

- DATABASE.md được tham chiếu bởi ARCHITECTURE.md (Phase 17)
- ADRs được tham chiếu bởi tất cả tài liệu kỹ thuật sau

</code_context>

<specifics>
## Specific Ideas

- Mermaid ER diagram phải render được trên GitHub (dùng ```mermaid code fence)
- ADR-002 cần giải thích rõ tại sao chuyển từ SQLite sang PostgreSQL (Vercel ephemeral filesystem)
- ADR-005 cần giải thích tại sao DB-backed thay vì in-memory counter (serverless stateless)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>
