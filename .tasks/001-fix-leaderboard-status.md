---
id: "001"
title: "Fix leaderboard verification status showing all as Chưa xác minh"
status: "todo"
area: "backend"
agent: "@backend-developer"
priority: "high"
created_at: "2026-03-28"
due_date: null
started_at: null
completed_at: null
prd_refs: ["FR-023", "FR-024"]
blocks: []
blocked_by: []
---

## Description

On the leaderboard page (`/leaderboard`), all scammers display "Chưa xác minh" (Unverified) regardless of their actual verification status in the database. This is a data display bug — either the verification status is not being read correctly from the database, the status update logic is not running, or the template is not rendering the correct status value.

This is a user-reported bug from the original TODO notes. The leaderboard is a core feature (FR-023) and verification status progression (FR-024) is essential for platform credibility.

## Acceptance Criteria

- [ ] Scammer verification status on `/leaderboard` reflects actual database values
- [ ] Verification badges (Unverified → Verified → Confirmed) display correctly based on report count and admin review
- [ ] Status is consistent between leaderboard view and individual scammer profile pages
- [ ] Relevant tests written and passing

## Technical Notes

- Check `routes/main.py` for the leaderboard route and how it queries `ScammerLeaderboard` model
- Check `models/models.py` for the `ScammerLeaderboard` and `ScammerReport` models — verify the status field values
- Check `utils/helpers.py` for verification badge logic
- Check `services/leaderboard_integrity.py` for the integrity/ranking logic
- The template `templates/leaderboard.html` renders the status — verify it reads the correct model field

## History

| Date | Agent / Human | Event |
|------|--------------|-------|
| 2026-03-28 | human | Task created during onboarding |
