---
phase: 18-operational-sops
plan: 01
subsystem: documentation
tags: [sop, reporting, admin-routes]

requires:
  - phase: 17-system-documents
    provides: API.md and DATABASE.md for cross-referencing
provides:
  - Updated SOP_BAO_CAO.md with correct /admin/ route prefixes
  - Cross-references to API.md, DATABASE.md, SOP_QUAN_TRI.md
affects: []

tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified:
    - documents/SOP/SOP_BAO_CAO.md

key-decisions:
  - "Selective update: only routes and cross-refs, no content changes"
  - "Added Section 11 (Tài liệu liên quan) with relative links"

patterns-established:
  - "SOP cross-reference pattern: relative links to docs/technical/"

requirements-completed:
  - SOP-01

duration: 3min
completed: 2026-04-14
---

# Plan 18-01: SOP_BAO_CAO.md Update Summary

**Fixed 3 admin route prefixes and added cross-reference section to reporting SOP.**

## What Changed

1. Section 4 routes corrected:
   - `POST /approve-report/<report_id>` → `POST /admin/approve-report/<report_id>`
   - `POST /reject-report/<report_id>` → `POST /admin/reject-report/<report_id>`
   - `GET /export-dataset` → `GET/POST /admin/export-dataset`

2. Added Section 11 "Tài liệu liên quan" with links to API.md, DATABASE.md, SOP_QUAN_TRI.md.

3. Confirmed no SQLite references present.

## Deviations from Plan

None — plan executed exactly as written.

## Commits

| Hash | Description |
|------|-------------|
| 2461e32 | docs(18-01): update SOP_BAO_CAO routes with /admin/ prefix and add cross-references |

## Self-Check: PASSED
