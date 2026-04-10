---
gsd_state_version: 1.0
milestone: v1.2
milestone_name: — Beta 1 Go-Live (Code Freeze)
status: Defining requirements
last_updated: "2026-04-10T00:00:00.000Z"
progress:
  total_phases: 0
  completed_phases: 0
  total_plans: 0
  completed_plans: 0
---

# STATE - MindGuard v2

## Project Reference

- **Core Value**: Người dùng có thể học, kiểm tra nhận thức và gửi báo cáo lừa đảo một cách dễ dùng, an toàn, và đáng tin cậy.
- **Current Focus**: v1.2 Beta 1 Go-Live (Code Freeze) — sửa lỗi, gia cố, an toàn AI.

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-04-10 — Milestone v1.2 started

## Performance Metrics

- **v1.2 requirements total**: TBD
- **Mapped to phases**: TBD
- **Coverage**: TBD
- **Open blockers**: 0

## Accumulated Context

### Key Decisions (from v1.0)

- Tách privacy/masking + audit thành Phase 1 để giảm rủi ro lộ dữ liệu trước khi mở rộng feature.
- Đặt anti-spam monitor->soft-enforce thành Phase 2 để ưu tiên telemetry và giảm false-positive.
- Đặt light-mode token system trước quiz redesign để tránh UX drift và hồi quy giao diện.
- Session-backed one-question step flow with PRG pattern (04-01).
- Python-level aggregation over SQLAlchemy case() to avoid version-specific syntax differences (05-01).

### Key Decisions (v1.1)

- Migrate toàn bộ sang NeonDB PostgreSQL (không giữ SQLite cho local).
- Postgres trước, Vercel fix sau — DB ổn định là tiên quyết.
- NeonDB cho cả local và production — cùng connection string.
- Fresh seed only — không cần migrate user data từ SQLite.
- Dùng `-pooler` endpoint để tránh connection exhaustion trên serverless.

### Key Decisions (v1.2)

- CODE FREEZE — không thêm tính năng mới, chỉ sửa lỗi và gia cố.
- Ưu tiên: UI bugs > Infrastructure hardening > AI safety > Documentation.

### Open Todos

(None — defining requirements)

### Blockers

(None)

## Session Continuity

- **Last Updated**: 2026-04-10
- **Stopped at**: Milestone v1.2 initialized, defining requirements
- **Resume file**: .planning/ROADMAP.md
