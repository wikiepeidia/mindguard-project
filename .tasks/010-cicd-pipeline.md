---
id: "010"
title: "Set up CI/CD pipeline with GitHub Actions"
status: "todo"
area: "infra"
agent: "@cicd-engineer"
priority: "normal"
created_at: "2026-03-28"
due_date: null
started_at: null
completed_at: null
prd_refs: []
blocks: []
blocked_by: []
---

## Description

Set up a GitHub Actions CI pipeline that runs on every push and pull request. At minimum: install dependencies, run tests, and check for basic issues. This establishes code quality gates before merging.

## Acceptance Criteria

- [ ] GitHub Actions workflow file created in `.github/workflows/`
- [ ] Pipeline runs `pip install -r requirements.txt`
- [ ] Pipeline runs `python -m pytest`
- [ ] Pipeline triggers on push to `main` and on pull requests
- [ ] Pipeline status badge added to README.md

## Technical Notes

- Python 3.12.10 target
- Tests are in `tests/` directory
- No linter yet (task #011), but pipeline can be extended later
- Keep it simple — no deployment step until production target is decided

## History

| Date | Agent / Human | Event |
|------|--------------|-------|
| 2026-03-28 | human | Task created during onboarding |
