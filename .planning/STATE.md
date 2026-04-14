---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: — Core Platform
status: complete
last_updated: "2026-04-14"
last_activity: 2026-04-14
progress:
  total_phases: 14
  completed_phases: 14
  total_plans: 20
  completed_plans: 20
---

# STATE - MindGuard v2

## Project Reference

- **Core Value**: Người dùng có thể học, kiểm tra nhận thức và gửi báo cáo lừa đảo một cách dễ dùng, an toàn, và đáng tin cậy.
- **Current Focus**: v1.2 Beta 1 Go-Live — 17/17 reqs COMPLETE. Beta 1 APPROVED.

## Current Position

Phase: 14
Plan: Complete
Status: All phases complete — Beta 1 approved
Last activity: 2026-04-14

```text
Progress: [████████████████████] 17/17 requirements complete
           Phase 10 ✓ → 11 ✓ → 12 ✓ → 13 ✓ → 14 ✓ (DONE)
```

## Remaining Work

None — all v1.2 requirements complete. Beta 1 signed off.

## Performance Metrics

- **v1.2 requirements total**: 17
- **Completed**: 17
- **Remaining**: 0
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

- ~~Fix blurry red badge stats on homepage (UI)~~ ✅ Fixed — font-smoothing + translateZ(0)
- ~~Fix dark theme on featured section homepage (UI)~~ ✅ Fixed — lighter gradient
- ~~Investigate missing Cloudflare Turnstile CAPTCHA (auth)~~ ✅ Not a bug — CAPTCHA renders correctly
- ~~Fix toast notification hidden behind header (UI)~~ ✅ Fixed — z-index 10700 > navbar 10500
- ~~Fix Vercel deployment issues (infra)~~ ✅ Fixed — PostgreSQL config, missing blueprints, logs dir, schema sync

### Open Requirements

None — all requirements complete.

### Blockers

(None)

## Session Continuity

- **Last Updated**: 2026-04-14
- **Stopped at**: Phase 14 complete. Stress test executed (50+200 CCU). Beta 1 signed off.
- **Resume with**: Beta 1 launch / v2 planning
- **Resume file**: .planning/phases/14-stress-test-beta-signoff/BETA-SIGNOFF.md
