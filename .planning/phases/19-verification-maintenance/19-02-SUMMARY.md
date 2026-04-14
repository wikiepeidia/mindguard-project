---
phase: 19-verification-maintenance
plan: 02
subsystem: docs
tags: [metadata, conventions, maintenance-rules]

requires:
  - phase: 19-verification-maintenance
    provides: Cross-check verification (Plan 01) confirming all docs are accurate

provides:
  - Metadata headers on all 3 SOP files (HTML comment DOCUMENT METADATA format)
  - Merge checklist in CONVENTIONS.md for docs update review

affects: [all-future-phases]

tech-stack:
  added: []
  patterns: [document-metadata-header, merge-checklist]

key-files:
  created: []
  modified:
    - documents/SOP/SOP_BAO_CAO.md
    - documents/SOP/SOP_VAN_HANH.md
    - documents/SOP/SOP_QUAN_TRI.md
    - docs/technical/CONVENTIONS.md

key-decisions:
  - "Used HTML comment DOCUMENT METADATA format matching existing tech docs (DATABASE.md, API.md, etc.)"
  - "CONVENTIONS.md already had Section 4 with trigger matrix — added merge checklist subsection"

patterns-established:
  - "All docs use HTML comment METADATA block with Owner, Last updated, Source files, Update trigger"

requirements-completed: [CONV-01, SOP-01, SOP-02, SOP-03]

duration: 5min
completed: 2026-04-14
---

# Phase 19 Plan 02: Metadata headers + docs maintenance rules

**All 8 v1.3 docs now have metadata headers; CONVENTIONS.md has merge checklist for docs review.**

## What Was Done

### Task 1: Metadata headers on SOP files
Added HTML comment `DOCUMENT METADATA` blocks to:
- **SOP_BAO_CAO.md**: Owner @backend-developer, source: routes/admin.py, routes/scammer.py, models/models.py
- **SOP_VAN_HANH.md**: Owner DevOps/Developer, source: app.py, config.py, vercel.json
- **SOP_QUAN_TRI.md**: Owner @backend-developer, source: routes/admin.py, models/models.py, services/sensitive_access_log.py

Tech docs already had metadata: CONVENTIONS.md (YAML), DATABASE.md, DECISIONS.md, ARCHITECTURE.md, API.md (HTML comments).

### Task 2: Merge checklist in CONVENTIONS.md
Added "Checklist review trước khi merge" subsection with 6 checkboxes covering:
- model → DATABASE.md
- route → API.md
- config key → .env.example + SOP_VAN_HANH.md
- admin workflow → SOP_QUAN_TRI.md
- report flow → SOP_BAO_CAO.md
- metadata `last_updated` field

## Self-Check

- [x] All 8 docs have metadata headers
- [x] CONVENTIONS.md has trigger matrix (already existed)
- [x] CONVENTIONS.md has merge checklist (added)
- [x] Review process documented (already existed)
