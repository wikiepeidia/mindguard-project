# Phase 19: Verification & Maintenance Setup - Context

**Gathered:** 2026-04-14
**Status:** Ready for planning
**Mode:** Auto-generated (infrastructure/verification phase)

<domain>
## Phase Boundary

Xác minh tất cả tài liệu v1.3 chính xác với codebase hiện tại và thiết lập cơ chế ngăn docs drift trong tương lai.

Phạm vi:
1. Cross-check facts trong tất cả docs (tên bảng, route paths, config keys, model names) với codebase thực tế.
2. Xử lý PLACEHOLDER còn sót lại trong tài liệu.
3. Đảm bảo mỗi tài liệu có metadata header (owner, last updated, source files).
4. Thêm quy tắc cập nhật tài liệu vào CONVENTIONS.md.

</domain>

<decisions>
## Implementation Decisions

### D-01: Phương pháp cross-check
- Dùng automated script (Python/grep) để kiểm tra tất cả facts trong docs vs codebase.
- Kiểm tra: tên bảng (vs models.py), route paths (vs routes/*.py), config keys (vs config.py), model names.
- Output: danh sách mismatches cần sửa.

### D-02: Metadata header format
- Mỗi tài liệu thêm/cập nhật header ghi: Owner, Last updated, Source files tham chiếu.
- Giữ format đơn giản: blockquote hoặc YAML-style tại đầu file.

### D-03: Docs maintenance rules
- Thêm section "Quy tắc Cập nhật Tài liệu" vào CONVENTIONS.md.
- Nội dung: khi nào cần update docs, file nào cần update khi code thay đổi, checklist review.

### D-04: PLACEHOLDER handling
- Grep tất cả files docs/ và documents/ cho PLACEHOLDER.
- Xóa hoặc thay thế bằng nội dung thực tế.
- SOP_BAO_CAO.md có PLACEHOLDER_HINH_* — giữ nguyên vì là placeholder cho hình ảnh chưa chụp (chấp nhận được).

### Claude's Discretion
- Cách tổ chức script verification (inline Python vs standalone file)
- Cụ thể format metadata header

</decisions>

<code_context>
## Existing Code Insights

### Docs đã viết trong v1.3
- `docs/technical/CONVENTIONS.md` — Glossary + redaction rules (Phase 15)
- `docs/technical/DATABASE.md` — 14 tables, ER diagram (Phase 16)
- `docs/technical/DECISIONS.md` — 5 ADRs (Phase 16)
- `docs/technical/ARCHITECTURE.md` — Full rewrite for NeonDB+Vercel (Phase 17)
- `docs/technical/API.md` — 42 routes across 8 blueprints (Phase 17)
- `documents/SOP/SOP_BAO_CAO.md` — Updated routes + cross-refs (Phase 18)
- `documents/SOP/SOP_VAN_HANH.md` — New system operations SOP (Phase 18)
- `documents/SOP/SOP_QUAN_TRI.md` — New admin operations SOP (Phase 18)

### Source files for cross-checking
- `models/models.py` — All SQLAlchemy model definitions (table names)
- `routes/*.py` — All route definitions (8 blueprint files)
- `config.py` — All config keys and env vars
- `app.py` — Blueprint registration

</code_context>

<specifics>
## Specific Ideas

- Image PLACEHOLDERs in SOP_BAO_CAO.md (PLACEHOLDER_HINH_*) are acceptable — they mark where screenshots will go later.
- Verification should be automated where possible to be reproducible.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>
