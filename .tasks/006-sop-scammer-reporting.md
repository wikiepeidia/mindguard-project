---
id: "006"
title: "Write SOP documentation for scammer reporting"
status: "todo"
area: "docs"
agent: "@documentation-writer"
priority: "normal"
created_at: "2026-03-28"
due_date: null
started_at: null
completed_at: null
prd_refs: ["FR-020", "FR-021", "FR-022", "FR-024"]
blocks: []
blocked_by: []
---

## Description

Write Standard Operating Procedure (SOP) documentation for the scammer reporting flow. This should cover the full lifecycle: how a user submits a report, how reports are moderated by admins, how verification status progresses, and how the leaderboard is updated. Include placeholder images where screenshots are needed — the user will add real screenshots later.

Existing SOP docs are in `documents/SOP/`.

## Acceptance Criteria

- [ ] SOP document covers: report submission, admin moderation, verification progression, leaderboard ranking
- [ ] Step-by-step instructions for each role (user and admin)
- [ ] Placeholder images marked clearly for user to replace
- [ ] Document placed in `documents/SOP/`
- [ ] Written in Vietnamese (primary audience language)

## Technical Notes

- Reference existing SOP files in `documents/SOP/` for format consistency
- The reporting flow is in `routes/scammer.py` and `templates/report_scammer.html`
- Admin moderation is in `routes/admin.py` and `templates/admin_scammer_reports.html`
- Privacy policy (reporter anonymization) is in `utils/privacy_policy.py`

## History

| Date | Agent / Human | Event |
|------|--------------|-------|
| 2026-03-28 | human | Task created during onboarding |
