---
id: "005"
title: "Implement UI fixes from audit findings"
status: "todo"
area: "frontend"
agent: "@frontend-developer"
priority: "high"
created_at: "2026-03-28"
due_date: null
started_at: null
completed_at: null
prd_refs: []
blocks: []
blocked_by: ["004"]
---

## Description

Implement the UI/UX fixes identified in the audit (task #004). This task is blocked until the audit is complete and findings are documented. The scope will be defined by the audit results.

## Acceptance Criteria

- [ ] All major and minor issues from #004 audit are resolved
- [ ] Cosmetic issues addressed where feasible
- [ ] Pages render correctly at mobile (375px), tablet (768px), and desktop (1024px+) breakpoints
- [ ] No visual regressions introduced
- [ ] Light-mode semantic tokens used consistently

## Technical Notes

- Scope depends on #004 audit findings
- Edit templates in `templates/` and styles in `static/css/`
- Test across breakpoints after each change

## History

| Date | Agent / Human | Event |
|------|--------------|-------|
| 2026-03-28 | human | Task created during onboarding |
