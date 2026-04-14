---
phase: 18-operational-sops
plan: 02
subsystem: documentation
tags: [sop, operations, admin, vercel, neondb]

requires:
  - phase: 17-system-documents
    provides: API.md, DATABASE.md, ARCHITECTURE.md for cross-referencing
provides:
  - SOP_VAN_HANH.md — complete system operations guide
  - SOP_QUAN_TRI.md — complete admin operations guide
affects: []

tech-stack:
  added: []
  patterns: []

key-files:
  created:
    - documents/SOP/SOP_VAN_HANH.md
    - documents/SOP/SOP_QUAN_TRI.md
  modified: []

key-decisions:
  - "SOP_VAN_HANH covers deploy, logs, rollback, troubleshooting, env vars"
  - "SOP_QUAN_TRI covers full admin workflow including unsuspend"
  - "Report moderation in SOP_QUAN_TRI is a summary — defers to SOP_BAO_CAO for details"

patterns-established:
  - "SOP format: numbered sections, tables for routes, cross-reference section at end"

requirements-completed:
  - SOP-02
  - SOP-03

duration: 8min
completed: 2026-04-14
---

# Plan 18-02: SOP_VAN_HANH.md + SOP_QUAN_TRI.md Summary

**Created two new SOPs: system operations guide (207 lines) and admin operations guide (223 lines).**

## What Was Built

### SOP_VAN_HANH.md (System Operations)

- System info table (Vercel, NeonDB, OpenRouter, Cloudflare)
- Deploy process: auto-deploy via `main` push, build logs, deployment check
- Logs: Vercel Dashboard + local access.log
- Rollback: Vercel promote-to-production + git revert
- Troubleshooting: 6 common issues (cold start, DB errors, rate limit, AI timeout, CSRF, filesystem)
- Environment variables reference table (9 vars with descriptions)

### SOP_QUAN_TRI.md (Admin Operations)

- Admin login: `/admin/login` with CAPTCHA, rate limit, session details
- Dashboard overview: user list, stats, management buttons
- User management: create admin, edit user, delete user with routes
- Report moderation summary (defers to SOP_BAO_CAO.md)
- Data export: two modes (summary + full with reason), CSV output
- Audit logs: sensitive_access_logs monitoring, anomaly detection
- Admin unsuspend: secret-key based recovery

### Cross-references

Both SOPs link to API.md, DATABASE.md, and each other.

## Deviations from Plan

None — plan executed exactly as written.

## Commits

| Hash | Description |
|------|-------------|
| 7e35fe7 | docs(18-02): create SOP_VAN_HANH.md system operations guide |
| 87b395d | docs(18-02): create SOP_QUAN_TRI.md admin operations guide |

## Self-Check: PASSED
