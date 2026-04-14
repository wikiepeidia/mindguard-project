# Plan 17-01 Summary — ARCHITECTURE.md Rewrite

**Status:** ✅ Complete
**Commit:** 3a17516

## What Was Done

Rewrite hoàn toàn ARCHITECTURE.md (280 dòng cũ → ~200 dòng mới) phản ánh đúng stack hiện tại:

- Cập nhật Tech Stack: SQLite → NeonDB PostgreSQL 15 (serverless), localhost+ngrok → Vercel
- Thêm CSRF protection (Flask-WTF), Flask-Limiter vào stack table
- Thêm 2 Mermaid diagrams: System Overview (flowchart) + Request Lifecycle (sequenceDiagram)
- Viết đầy đủ 4 Data Flow (Auth, Quiz, Scammer Report, AI Chatbot)
- Thay Design System placeholders bằng ghi chú thực tế
- Cập nhật Security Architecture: thêm CSRF, sửa session (cookie-based vs server-side)
- Cập nhật Performance: NeonDB latency, Vercel cold starts, CDN
- Cập nhật Known Constraints: Vercel read-only filesystem, cold starts, connection limits
- Thêm "Xem thêm" section với links đến DATABASE.md, API.md, DECISIONS.md, CONVENTIONS.md

## Artifacts

| File | Action |
|------|--------|
| `docs/technical/ARCHITECTURE.md` | Rewritten |

## Verification

8/8 automated checks passed: NeonDB mentioned, Vercel mentioned, 2 Mermaid diagrams, 3 cross-references, no secrets leaked.
