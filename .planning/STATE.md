---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: — Core Platform
status: executing
last_updated: "2026-04-13T14:29:39.225Z"
last_activity: 2026-04-13
progress:
  total_phases: 10
  completed_phases: 10
  total_plans: 19
  completed_plans: 19
---

# STATE - MindGuard v2

## Project Reference

- **Core Value**: Người dùng có thể học, kiểm tra nhận thức và gửi báo cáo lừa đảo một cách dễ dùng, an toàn, và đáng tin cậy.
- **Current Focus**: v1.2 Beta 1 Go-Live (Code Freeze) — teammate đã hoàn thành phần lớn, còn 5 items.

## Current Position

Phase: 10
Plan: Not started
Status: Executing Phase 10
Last activity: 2026-04-13

```text
Progress: [████████████████    ] 12/17 requirements complete
          Phase 10 (2 left) → 11 ✓ → 12 (1 left) → 13 (1 left) → 14 (not started)
```

## Remaining Work (5 items)

| Phase | Requirement | Item | Effort |
|-------|-------------|------|--------|
| 10 | INFRA-01 | Xóa `db.create_all()` từ `app.py:69-70` | 1 dòng |
| 10 | INFRA-02 | Di chuyển `ADMIN_PASSWORD` & `REPORT_ENCRYPTION_KEY` sang env vars | ~5 dòng |
| 12 | AISF-01 | Giảm timeout 10s → 8s trong `utils/chatbot.py:66` | 1 dòng |
| 13 | TRUST-03 | Thêm nút "Báo cáo sai / Góp ý" nổi bật trong chatbot UI | UI nhỏ |
| 14 | INFRA-05 | Stress test với locust tìm ngưỡng CCU | Hoạt động riêng |

## Performance Metrics

- **v1.2 requirements total**: 17
- **Completed by teammate**: 12
- **Remaining**: 5
- **Coverage**: 100% mapped
- **Open blockers**: 0

## Accumulated Context

### Key Decisions (from v1.0)

- Tách privacy/masking + audit thành Phase 1 để giảm rủi ro lộ dữ liệu trước khi mở rộng feature.
- Đặt anti-spam monitor->soft-enforce thành Phase 2 để ưu tiên telemetry và giảm false-positive.
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
- Teammate đã hoàn thành: rate limiting, UI fixes, AI safety (trừ timeout), privacy banner, logging baseline.
- Còn lại: security hardening (credentials), AI timeout fix, feedback button, stress test.

### Pending Todos (5 new bugs from teammate code drop)

- Fix blurry red badge stats on homepage (UI)
- Fix dark theme on featured section homepage (UI)
- Investigate missing Cloudflare Turnstile CAPTCHA (auth)
- Fix toast notification hidden behind header (UI)
- Fix Vercel deployment issues (infra)

### Open Requirements

- Fix remaining 5 requirements (INFRA-01, INFRA-02, AISF-01, TRUST-03, INFRA-05)

### Blockers

(None)

## Session Continuity

- **Last Updated**: 2026-04-13
- **Stopped at**: Planning updated after teammate code drop — 5 items remaining
- **Resume with**: `/gsd:plan-phase 10` or execute remaining fixes directly
- **Resume file**: .planning/ROADMAP.md
