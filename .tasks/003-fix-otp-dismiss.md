---
id: "003"
title: "Fix OTP notification auto-dismiss timing"
status: "todo"
area: "frontend"
agent: "@frontend-developer"
priority: "high"
created_at: "2026-03-28"
due_date: null
started_at: null
completed_at: null
prd_refs: ["FR-003"]
blocks: []
blocked_by: []
---

## Description

The OTP notification message "Mã OTP đã được gửi đến email của bạn. (Demo: 123456)" does not auto-dismiss after 2 seconds as intended. The notification stays visible indefinitely. This is a minor but noticeable UX issue on the auth flow.

## Acceptance Criteria

- [ ] OTP success notification auto-dismisses after 2 seconds
- [ ] Other flash/notification messages also auto-dismiss appropriately
- [ ] Dismiss animation is smooth (fade out, not abrupt removal)
- [ ] Manual dismiss (click to close) still works

## Technical Notes

- Check the auth templates (`templates/register.html`, `templates/login.html`) for notification/flash message display
- Look for JavaScript `setTimeout` or similar auto-dismiss logic — it may be missing or broken
- Check `static/js/` for any notification utility scripts
- The notification may be using Bootstrap alerts — ensure the dismiss JS is loaded

## History

| Date | Agent / Human | Event |
|------|--------------|-------|
| 2026-03-28 | human | Task created during onboarding |
